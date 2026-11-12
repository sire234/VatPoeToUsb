// Minimal mDNS responder (RFC 6762) with DNS-SD (RFC 6763) on a W5500 UDP multicast socket.
//
//   poe-hid-xxxxxx.local                         A    own IPv4 address (xxxxxx = last 3 MAC bytes)
//   _poehid._tcp.local                           PTR  "PoE-HID-Bridge xxxxxx._poehid._tcp.local"
//   PoE-HID-Bridge xxxxxx._poehid._tcp.local     SRV  port 5000, target poe-hid-xxxxxx.local
//                                                TXT  txtvers=1, data=hid-ascii
//   _services._dns-sd._udp.local                 PTR  _poehid._tcp.local (service type enumeration)
//
// Simplifications: no probing / conflict resolution (the name contains the MAC, so it is unique),
// no known-answer suppression, all answers multicast (also for QU questions), no IPv6/AAAA,
// no legacy unicast queries (source port != 5353; ping, browsers and dns-sd/avahi use 5353).
#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include "pico/stdlib.h"
#include "wizchip_conf.h"
#include "socket.h"
#include "app.h"

#define MDNS_PORT       5353
#define TTL_HOST        120         // A, SRV (RFC 6762 §10)
#define TTL_OTHER       4500        // PTR, TXT
#define SERVICE_PORT    5000

#define TYPE_A      1
#define TYPE_PTR    12
#define TYPE_TXT    16
#define TYPE_SRV    33
#define TYPE_ANY    255
#define CLASS_IN    1
#define CACHE_FLUSH 0x8000

enum { R_A = 1, R_PTR_SVC = 2, R_SRV = 4, R_TXT = 8, R_PTR_ENUM = 16 };

static const uint8_t mdns_ip[4] = { 224, 0, 0, 251 };
static const uint8_t mdns_mac[6] = { 0x01, 0x00, 0x5e, 0x00, 0x00, 0xfb };

static const char svc_name[] = "_poehid._tcp.local";
static const char enum_name[] = "_services._dns-sd._udp.local";
static char host_name[32];          // "poe-hid-xxxxxx.local"
static char inst_name[64];          // "PoE-HID-Bridge xxxxxx._poehid._tcp.local"

static uint8_t sock = 0xff;
static uint8_t pkt[1472];
static int announce_left;
static uint32_t t_announce;

// ---- names ----

const char *mdns_hostname(void) {
    return host_name[0] ? host_name : "-";
}

// read a (possibly compressed) name at *off into "a.b.c" (lower case); advances *off past it
static bool read_name(const uint8_t *msg, size_t len, size_t *off, char *out, size_t size) {
    size_t pos = *off, n = 0;
    bool jumped = false;
    int hops = 0;

    while (pos < len) {
        uint8_t l = msg[pos];
        if (l == 0) {
            if (!jumped)
                *off = pos + 1;
            out[n] = 0;
            return true;
        }
        if ((l & 0xc0) == 0xc0) {   // compression pointer
            if (pos + 1 >= len || ++hops > 8)
                return false;
            if (!jumped)
                *off = pos + 2;
            jumped = true;
            pos = ((l & 0x3f) << 8) | msg[pos + 1];
            continue;
        }
        if (pos + 1 + l > len || n + l + 2 > size)
            return false;
        if (n)
            out[n++] = '.';
        for (uint8_t i = 0; i < l; i++)
            out[n++] = (char)tolower(msg[pos + 1 + i]);
        pos += 1 + l;
    }
    return false;
}

static bool name_eq(const char *lower, const char *name) {
    while (*lower && *name)
        if (*lower++ != tolower((unsigned char)*name++))
            return false;
    return *lower == *name;
}

// ---- response builder ----

static size_t put_u16(uint8_t *p, size_t n, uint16_t v) {
    p[n] = v >> 8;
    p[n + 1] = v & 0xff;
    return n + 2;
}

static size_t put_u32(uint8_t *p, size_t n, uint32_t v) {
    n = put_u16(p, n, v >> 16);
    return put_u16(p, n, v & 0xffff);
}

// "a.b.c" -> 1a1b1c0 (no compression; labels in our names never contain dots)
static size_t put_name(uint8_t *p, size_t n, const char *name) {
    while (*name) {
        const char *dot = strchr(name, '.');
        size_t l = dot ? (size_t)(dot - name) : strlen(name);
        p[n++] = (uint8_t)l;
        memcpy(&p[n], name, l);
        n += l;
        name += l + (dot ? 1 : 0);
    }
    p[n++] = 0;
    return n;
}

// record header; returns the offset of RDLENGTH, filled in by end_rr()
static size_t begin_rr(uint8_t *p, size_t *n, const char *name, uint16_t type, uint16_t cls, uint32_t ttl) {
    *n = put_name(p, *n, name);
    *n = put_u16(p, *n, type);
    *n = put_u16(p, *n, cls);
    *n = put_u32(p, *n, ttl);
    size_t rdlen_at = *n;
    *n += 2;
    return rdlen_at;
}

static void end_rr(uint8_t *p, size_t n, size_t rdlen_at) {
    put_u16(p, rdlen_at, (uint16_t)(n - rdlen_at - 2));
}

static size_t put_records(uint8_t *p, size_t n, int mask) {
    size_t r;
    if (mask & R_A) {
        uint8_t ip[4];
        getSIPR(ip);
        r = begin_rr(p, &n, host_name, TYPE_A, CLASS_IN | CACHE_FLUSH, TTL_HOST);
        memcpy(&p[n], ip, 4);
        n += 4;
        end_rr(p, n, r);
    }
    if (mask & R_PTR_SVC) {
        r = begin_rr(p, &n, svc_name, TYPE_PTR, CLASS_IN, TTL_OTHER);
        n = put_name(p, n, inst_name);
        end_rr(p, n, r);
    }
    if (mask & R_SRV) {
        r = begin_rr(p, &n, inst_name, TYPE_SRV, CLASS_IN | CACHE_FLUSH, TTL_HOST);
        n = put_u16(p, n, 0);           // priority
        n = put_u16(p, n, 0);           // weight
        n = put_u16(p, n, SERVICE_PORT);
        n = put_name(p, n, host_name);
        end_rr(p, n, r);
    }
    if (mask & R_TXT) {
        static const char *const txt[] = { "txtvers=1", "data=hid-ascii" };
        r = begin_rr(p, &n, inst_name, TYPE_TXT, CLASS_IN | CACHE_FLUSH, TTL_OTHER);
        for (size_t i = 0; i < sizeof txt / sizeof txt[0]; i++) {
            size_t l = strlen(txt[i]);
            p[n++] = (uint8_t)l;
            memcpy(&p[n], txt[i], l);
            n += l;
        }
        end_rr(p, n, r);
    }
    if (mask & R_PTR_ENUM) {
        r = begin_rr(p, &n, enum_name, TYPE_PTR, CLASS_IN, TTL_OTHER);
        n = put_name(p, n, svc_name);
        end_rr(p, n, r);
    }
    return n;
}

static int count_bits(int m) {
    int c = 0;
    for (; m; m &= m - 1)
        c++;
    return c;
}

static void send_response(int answers, int additional) {
    static uint8_t out[512];            // all five records need ~ 250 bytes
    size_t n = 0;
    n = put_u16(out, n, 0);             // ID 0
    n = put_u16(out, n, 0x8400);        // response, authoritative
    n = put_u16(out, n, 0);             // questions
    n = put_u16(out, n, (uint16_t)count_bits(answers));
    n = put_u16(out, n, 0);             // authority
    n = put_u16(out, n, (uint16_t)count_bits(additional));
    n = put_records(out, n, answers);
    n = put_records(out, n, additional);
    int32_t r = sendto(sock, out, (uint16_t)n, (uint8_t *)mdns_ip, MDNS_PORT);
    if (r != (int32_t)n)
        printf("mDNS: send failed (%ld)\n", (long)r);
}

// ---- query handling ----

static uint32_t stat_rx, stat_answered, stat_legacy;

static const char *type_name(uint16_t type) {
    switch (type) {
    case TYPE_A:   return "A";
    case TYPE_PTR: return "PTR";
    case TYPE_TXT: return "TXT";
    case TYPE_SRV: return "SRV";
    case TYPE_ANY: return "ANY";
    default:       return "?";
    }
}

void mdns_stats(uint32_t *rx, uint32_t *answered, uint32_t *legacy) {
    *rx = stat_rx;
    *answered = stat_answered;
    *legacy = stat_legacy;
}

static void records_string(int mask, char *buf, size_t size) {
    snprintf(buf, size, "%s%s%s%s%s", mask & R_PTR_SVC ? " PTR" : "", mask & R_PTR_ENUM ? " PTR(enum)" : "",
             mask & R_SRV ? " SRV" : "", mask & R_TXT ? " TXT" : "", mask & R_A ? " A" : "");
}

static void handle_query(const uint8_t *msg, size_t len, const uint8_t *from, uint16_t port) {
    if (len < 12)
        return;
    uint16_t flags = (msg[2] << 8) | msg[3];
    uint16_t qdcount = (msg[4] << 8) | msg[5];
    if (flags & 0xf800)                 // a response or not a standard query
        return;

    int answers = 0, additional = 0;
    size_t off = 12;
    char name[128];
    char asked[96] = "";                // our names that were asked for, for the debug log
    size_t asked_len = 0;

    for (uint16_t q = 0; q < qdcount; q++) {
        if (!read_name(msg, len, &off, name, sizeof name) || off + 4 > len)
            return;
        uint16_t type = (msg[off] << 8) | msg[off + 1];
        bool qu = msg[off + 2] & 0x80;
        uint16_t cls = ((msg[off + 2] << 8) | msg[off + 3]) & 0x7fff;   // without the QU bit
        off += 4;
        if (cls != CLASS_IN && cls != TYPE_ANY)
            continue;
        bool any = type == TYPE_ANY;
        int before = answers;

        if (name_eq(name, host_name) && (type == TYPE_A || any)) {
            answers |= R_A;
        } else if (name_eq(name, svc_name) && (type == TYPE_PTR || any)) {
            answers |= R_PTR_SVC;
            additional |= R_SRV | R_TXT | R_A;
        } else if (name_eq(name, enum_name) && (type == TYPE_PTR || any)) {
            answers |= R_PTR_ENUM;
        } else if (name_eq(name, inst_name)) {
            if (type == TYPE_SRV || any) {
                answers |= R_SRV;
                additional |= R_A;
            }
            if (type == TYPE_TXT || any)
                answers |= R_TXT;
        }
        if (answers != before && asked_len < sizeof asked - 1)
            asked_len += (size_t)snprintf(asked + asked_len, sizeof asked - asked_len, " %s %s%s",
                                          type_name(type), name, qu ? " (QU)" : "");
    }
    if (!answers)
        return;                         // query for other devices: counted only

    char rec[48];
    if (port != MDNS_PORT) {
        // legacy unicast query (RFC 6762 6.7) would need a unicast reply with the query ID: not supported
        stat_legacy++;
        printf("mDNS: query from %u.%u.%u.%u:%u ignored (source port not 5353):%s\n",
               from[0], from[1], from[2], from[3], port, asked);
        return;
    }
    additional &= ~answers;
    records_string(answers, rec, sizeof rec);
    printf("mDNS: query from %u.%u.%u.%u:%s -> answer%s\n", from[0], from[1], from[2], from[3], asked, rec);
    stat_answered++;
    send_response(answers, additional);
}

// ---- socket ----

void mdns_start(uint8_t sn) {
    uint8_t mac[6];
    getSHAR(mac);
    snprintf(host_name, sizeof host_name, "poe-hid-%02x%02x%02x.local", mac[3], mac[4], mac[5]);
    snprintf(inst_name, sizeof inst_name, "PoE-HID-Bridge %02x%02x%02x.%s", mac[3], mac[4], mac[5], svc_name);

    // the multicast group must be in the socket registers before the socket is opened
    sock = sn;
    close(sock);
    setSn_DHAR(sock, (uint8_t *)mdns_mac);
    setSn_DIPR(sock, (uint8_t *)mdns_ip);
    setSn_DPORT(sock, MDNS_PORT);
    if (socket(sock, Sn_MR_UDP, MDNS_PORT, SF_MULTI_ENABLE) != sock) {
        printf("mDNS: cannot open socket\n");
        sock = 0xff;
        return;
    }
    printf("mDNS: %s, service \"%s\"\n", host_name, inst_name);
    mdns_announce();
}

void mdns_stop(void) {
    if (sock != 0xff)
        close(sock);
    sock = 0xff;
}

void mdns_announce(void) {
    announce_left = 2;                  // RFC 6762 §8.3: at least two, one second apart
    t_announce = to_ms_since_boot(get_absolute_time());
}

void mdns_task(void) {
    if (sock == 0xff)
        return;

    if (getSn_RX_RSR(sock) > 0) {
        uint8_t from[4];
        uint16_t port;
        int32_t len = recvfrom(sock, pkt, sizeof pkt, from, &port);
        if (len > 0) {
            stat_rx++;
            handle_query(pkt, (size_t)len, from, port);
        }
    }

    uint32_t now = to_ms_since_boot(get_absolute_time());
    if (announce_left && (int32_t)(now - t_announce) >= 0) {
        printf("mDNS: announcement (%d left)\n", announce_left - 1);
        send_response(R_A | R_PTR_SVC | R_SRV | R_TXT, 0);
        announce_left--;
        t_announce = now + 1000;
    }
}
