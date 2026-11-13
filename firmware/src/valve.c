// VAT valves (USB 272b:0010, composite: vendor HID on interface 0 + CD-ROM, the CD-ROM is not used).
//
// Packet format (cpa4showcase docs/analysis/legacy-analysis.md 9.1.3, protocol-verification.md):
//   HID reports are 64 bytes without report ID, every output report is padded to 64 bytes.
//   Header (8 bytes): unique ID (LE16), message length = 8 + payload (LE16), message code,
//   timestamp (LE16), reserved. Text commands use code 0x15, payload = ASCII text + CR LF.
//   Reply: same unique ID and code (0x80 = error, payload byte 0 = error code). A reply longer
//   than one report continues in reports with code 0x7A: sequence (LE16), length 0x0040, 0x7A,
//   tick (LE16), reserved, payload count (LE16), up to 54 payload bytes.
//   Strict ping-pong, 1000 ms timeout, no retry.
//
// Only read commands are passed on (allow-list as in cpa4showcase src/valve-commands.md):
//   p:<read service><ID 8 hex><index 2 hex>, g:1E17/18/19 and g:1E20/21[<ID>] (+ "START"),
//   exactly the two W1 writes that set the number format to hex, the W2 write
//   "deliver bitmap strings" (0x06102000 = 0 or 1) and the acknowledge of the three change
//   counters 0x06100100/0200/0300 (index 0) - the same writes the cpa4showcase gate allows.
//
// Three request kinds (prefix of the TCP reply):
//   'V'  v<addr> <cmd>  -> "#V<addr> <reply>"                   (text, as before)
//   'T'  t<addr> <cmd>  -> "#T<addr> <tick 4 hex> <reply>"      (text + valve tick of the reply)
//   'C'  c<addr>        -> "#C<addr> <tick 4 hex> <type 4 hex>" (controller type, message 0x16)
// Errors are always "#<kind><addr> ERR <reason>".
#include <ctype.h>
#include <stdio.h>
#include <string.h>
#include "pico/stdlib.h"
#include "tusb.h"
#include "app.h"

#define VALVE_VID       0x272B
#define VALVE_PID       0x0010
#define VALVE_MAX       8
#define REPORT_LEN      64
#define HEADER_LEN      8
#define CODE_TEXT       0x15
#define CODE_CTYPE      0x16
#define CODE_ERROR      0x80
#define CODE_CONT       0x7A
#define FIRST_PAYLOAD   (REPORT_LEN - HEADER_LEN)       // 56
#define CONT_HEADER     10
#define REPLY_MAX       4096
#define TIMEOUT_MS      1000

typedef struct {
    uint8_t dev_addr;                   // 0 = free
    uint8_t idx;                        // TinyUSB HID instance
} valve_t;

static valve_t valves[VALVE_MAX];

// one request at a time (over all valves)
static struct {
    bool busy;
    char kind;                          // 'V', 'T' or 'C', see the header
    uint8_t want_code;                  // CODE_TEXT or CODE_CTYPE
    uint16_t tick;                      // timestamp of the first reply report
    uint8_t dev_addr;
    uint16_t uid;
    uint32_t t_start;
    bool got_first;
    uint8_t code;
    size_t expected;                    // payload bytes of the whole reply
    size_t received;
    uint32_t t_sent;                    // for the debug log
    unsigned reports;
} req;

static uint8_t reply[REPLY_MAX];
static uint16_t next_uid = 1;

static uint32_t now_ms(void) {
    return to_ms_since_boot(get_absolute_time());
}

static valve_t *find(uint8_t dev_addr) {
    for (int i = 0; i < VALVE_MAX; i++)
        if (valves[i].dev_addr == dev_addr)
            return &valves[i];
    return NULL;
}

// ---------------------------------------------------------------- allow-list

static bool all_hex(const char *s, size_t n) {
    for (size_t i = 0; i < n; i++)
        if (!isxdigit((unsigned char)s[i]))
            return false;
    return true;
}

static bool allowed(const char *cmd) {
    size_t n = strlen(cmd);

    // the only writes: W1, number formats integer and float to hex
    if (strcmp(cmd, "p:01060201010003") == 0 || strcmp(cmd, "p:01060201020002") == 0)
        return true;

    // W2 and the change counter acknowledges: p:01 + ID (8) + index 00 + value (1..16 hex)
    if (strncmp(cmd, "p:01", 4) == 0 && n > 14 && n <= 30 && all_hex(cmd + 4, n - 4)) {
        if (strncmp(cmd + 12, "00", 2) != 0)
            return false;
        if (strncasecmp(cmd + 4, "06100100", 8) == 0 || strncasecmp(cmd + 4, "06100200", 8) == 0 ||
            strncasecmp(cmd + 4, "06100300", 8) == 0)
            return true;
        if (strncasecmp(cmd + 4, "06102000", 8) == 0) {
            for (size_t i = 14; i < n - 1; i++)     // value 0 or 1, leading zeros allowed
                if (cmd[i] != '0')
                    return false;
            return cmd[n - 1] == '0' || cmd[n - 1] == '1';
        }
        return false;
    }

    if (strncmp(cmd, "p:", 2) == 0) {
        // p: + service (2) + parameter ID (8) + index (2), nothing else
        static const char *const read_services[] = {
            "0B", "0E", "0F", "10", "12", "15", "17", "1A", "1B", "29" };
        if (n != 14 || !all_hex(cmd + 2, 12))
            return false;
        for (size_t i = 0; i < sizeof read_services / sizeof read_services[0]; i++)
            if (strncasecmp(cmd + 2, read_services[i], 2) == 0)
                return true;
        return false;
    }

    if (strncasecmp(cmd, "g:1E", 4) == 0 && n >= 6) {
        const char *sub = cmd + 4;
        const char *arg = cmd + 6;
        size_t arg_len = n - 6;
        if (arg_len >= 5 && strcmp(cmd + n - 5, "START") == 0)
            arg_len -= 5;
        if (!all_hex(arg, arg_len) || arg_len > 8)
            return false;
        if (strncmp(sub, "17", 2) == 0 || strncmp(sub, "18", 2) == 0 || strncmp(sub, "19", 2) == 0)
            return arg_len == 0;
        if (strncmp(sub, "20", 2) == 0 || strncmp(sub, "21", 2) == 0)
            return true;
    }
    return false;
}

// ---------------------------------------------------------------- TinyUSB hooks (from hid_app.c)

bool valve_is_valve(uint8_t dev_addr) {
    uint16_t vid = 0, pid = 0;
    tuh_vid_pid_get(dev_addr, &vid, &pid);
    return vid == VALVE_VID && pid == VALVE_PID;
}

void valve_mount(uint8_t dev_addr, uint8_t idx) {
    valve_t *v = find(0);
    if (!v) {
        printf("VALVE: no slot for addr %u\n", dev_addr);
        return;
    }
    v->dev_addr = dev_addr;
    v->idx = idx;
    printf("VALVE: addr %u ready (HID instance %u)\n", dev_addr, idx);
    app_eventf("#VALVE connected v%u\n", dev_addr);
}

void valve_unmount(uint8_t dev_addr) {
    valve_t *v = find(dev_addr);
    if (!v)
        return;
    v->dev_addr = 0;
    if (req.busy && req.dev_addr == dev_addr) {
        req.busy = false;
        app_eventf("#%c%u ERR removed\n", req.kind, dev_addr);
    }
    printf("VALVE: addr %u removed\n", dev_addr);
    app_eventf("#VALVE disconnected v%u\n", dev_addr);
}

static void finish(void) {
    // strip CR LF and a trailing 0 of the text reply
    size_t n = req.received;
    while (n && (reply[n - 1] == '\r' || reply[n - 1] == '\n' || reply[n - 1] == 0))
        n--;
    printf("VALVE: v%u << %u bytes in %u report(s), %lu ms\n", req.dev_addr, (unsigned)n, req.reports,
           (unsigned long)(now_ms() - req.t_sent));
    if (req.kind == 'C') {
        // controller type: 2 bytes little endian
        unsigned type = req.received >= 2 ? (unsigned)(reply[0] | (reply[1] << 8)) : 0;
        app_eventf("#C%u %04X %04X\n", req.dev_addr, req.tick, type);
        req.busy = false;
        return;
    }
    char head[24];
    int h;
    if (req.kind == 'T')
        h = snprintf(head, sizeof head, "#T%u %04X ", req.dev_addr, req.tick);
    else
        h = snprintf(head, sizeof head, "#V%u ", req.dev_addr);
    if (!net_queue_fits((size_t)h + n + 1)) {
        app_eventf("#%c%u ERR reply too long for the TCP buffer (%u bytes)\n", req.kind, req.dev_addr, (unsigned)n);
    } else {
        net_queue(head, (size_t)h);
        net_queue((const char *)reply, n);
        net_queue("\n", 1);
    }
    req.busy = false;
}

// returns true if the report belonged to a valve (then it is not shown as generic HID)
bool valve_report(uint8_t dev_addr, const uint8_t *r, uint16_t len) {
    if (!find(dev_addr))
        return false;
    if (!req.busy || req.dev_addr != dev_addr || len < HEADER_LEN) {
        printf("VALVE: v%u unsolicited report ignored (%u bytes, code 0x%02X)\n", dev_addr, len, len > 4 ? r[4] : 0);
        return true;
    }
    if (!req.got_first) {
        uint16_t uid = r[0] | (r[1] << 8);
        uint16_t msg_len = r[2] | (r[3] << 8);
        if (uid != req.uid) {
            printf("VALVE: v%u stale reply ignored (uid %u, expected %u)\n", dev_addr, uid, req.uid);
            return true;                // reply to an older request
        }
        req.reports++;
        req.code = r[4];
        if (req.code == CODE_ERROR) {
            printf("VALVE: v%u packet error 0x%02X\n", dev_addr, len > HEADER_LEN ? r[HEADER_LEN] : 0);
            app_eventf("#%c%u ERR packet error 0x%02X\n", req.kind, dev_addr, len > HEADER_LEN ? r[HEADER_LEN] : 0);
            req.busy = false;
            return true;
        }
        if (req.code != req.want_code || msg_len < HEADER_LEN || msg_len - HEADER_LEN > REPLY_MAX) {
            printf("VALVE: v%u bad reply (code 0x%02X, length %u)\n", dev_addr, req.code, msg_len);
            app_eventf("#%c%u ERR bad reply (code 0x%02X, length %u)\n", req.kind, dev_addr, req.code, msg_len);
            req.busy = false;
            return true;
        }
        req.got_first = true;
        req.tick = r[5] | (r[6] << 8);
        req.expected = msg_len - HEADER_LEN;
        size_t n = req.expected < FIRST_PAYLOAD ? req.expected : FIRST_PAYLOAD;
        if (n > (size_t)(len - HEADER_LEN))
            n = len - HEADER_LEN;
        memcpy(reply, r + HEADER_LEN, n);
        req.received = n;
    } else {
        if (len < CONT_HEADER || r[4] != CODE_CONT) {
            printf("VALVE: v%u unexpected report in a long reply (code 0x%02X)\n", dev_addr, len > 4 ? r[4] : 0);
            return true;
        }
        req.reports++;
        size_t n = r[8] | (r[9] << 8);
        if (n > (size_t)(len - CONT_HEADER))
            n = len - CONT_HEADER;
        if (n > req.expected - req.received)
            n = req.expected - req.received;
        memcpy(reply + req.received, r + CONT_HEADER, n);
        req.received += n;
    }
    req.t_start = now_ms();             // timeout counts per report
    if (req.received >= req.expected)
        finish();
    return true;
}

// ---------------------------------------------------------------- requests (from net.c)

void valve_request(uint8_t dev_addr, char kind, const char *cmd) {
    valve_t *v = find(dev_addr);
    if (kind == 'C')
        cmd = "";                       // message 0x16 has no payload
    if (dev_addr == 0 || !v) {
        app_eventf("#%c%u ERR no valve\n", kind, dev_addr);
        return;
    }
    if (kind != 'C' && !allowed(cmd)) {
        printf("VALVE: v%u blocked \"%s\"\n", dev_addr, cmd);
        app_eventf("#%c%u ERR blocked (only read commands, W1, W2 and counter acknowledges are allowed)\n", kind, dev_addr);
        return;
    }
    if (req.busy) {
        printf("VALVE: v%u busy (request to v%u still open)\n", dev_addr, req.dev_addr);
        app_eventf("#%c%u ERR busy\n", kind, dev_addr);
        return;
    }
    size_t n = strlen(cmd);
    if (n + 2 > FIRST_PAYLOAD) {
        app_eventf("#%c%u ERR command too long\n", kind, dev_addr);
        return;
    }

    static uint8_t out[REPORT_LEN];
    memset(out, 0, sizeof out);
    uint16_t uid = next_uid++;
    uint16_t msg_len = (uint16_t)(kind == 'C' ? HEADER_LEN : HEADER_LEN + n + 2);
    out[0] = uid & 0xff;
    out[1] = uid >> 8;
    out[2] = msg_len & 0xff;
    out[3] = msg_len >> 8;
    out[4] = kind == 'C' ? CODE_CTYPE : CODE_TEXT;
    if (kind != 'C') {
        memcpy(out + HEADER_LEN, cmd, n);
        out[HEADER_LEN + n] = '\r';
        out[HEADER_LEN + n + 1] = '\n';
    }

    const char *path = "interrupt OUT";
    bool ok = tuh_hid_send_report(dev_addr, v->idx, 0, out, sizeof out);
    if (!ok) {                          // no interrupt OUT endpoint: SET_REPORT over EP0
        path = "SET_REPORT";
        ok = tuh_hid_set_report(dev_addr, v->idx, 0, HID_REPORT_TYPE_OUTPUT, out, sizeof out);
    }
    if (!ok) {
        printf("VALVE: v%u send failed \"%s\"\n", dev_addr, cmd);
        app_eventf("#%c%u ERR send failed\n", kind, dev_addr);
        return;
    }
    printf("VALVE: v%u >> %s (uid %u, %s)\n", dev_addr, kind == 'C' ? "controller type" : cmd, uid, path);
    memset(&req, 0, sizeof req);
    req.busy = true;
    req.kind = kind;
    req.want_code = kind == 'C' ? CODE_CTYPE : CODE_TEXT;
    req.dev_addr = dev_addr;
    req.uid = uid;
    req.t_start = req.t_sent = now_ms();
}

size_t valve_list(char *buf, size_t size) {
    int n = snprintf(buf, size, "#VALVES");
    for (int i = 0; i < VALVE_MAX && n > 0 && (size_t)n < size; i++)
        if (valves[i].dev_addr)
            n += snprintf(buf + n, size - n, " v%u", valves[i].dev_addr);
    if (n > 0 && (size_t)n < size)
        n += snprintf(buf + n, size - n, "\n");
    return n < 0 ? 0 : ((size_t)n < size ? (size_t)n : size - 1);
}

void valve_task(void) {
    if (req.busy && now_ms() - req.t_start > TIMEOUT_MS) {
        printf("VALVE: v%u timeout (uid %u, %u of %u bytes, %u report(s))\n", req.dev_addr, req.uid,
               (unsigned)req.received, (unsigned)req.expected, req.reports);
        req.busy = false;
        app_eventf("#%c%u ERR timeout\n", req.kind, req.dev_addr);
    }
}
