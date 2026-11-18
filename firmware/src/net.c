// Ethernet: link supervision, DHCP (fallback to a static address), TCP server on TCP_PORT.
//
// The TCP client receives everything app_emit() produces: plain ASCII from keyboards / barcode
// scanners ("\r\n" after Enter) and '#'-prefixed lines for events, mice and other HID devices.
// Commands from the client (one per line): "status", "usb on", "usb off", "valves",
// "v<addr> <text command>" (VAT valve, e.g. "v1 p:0B0F10010000", reply "#V1 <reply>", see valve.c),
// "log" (debug history: "#LOG <uptime s> <text>" lines, then "#LOG end"),
// "debug on" / "debug off" (live debug output "#DBG <uptime s> <text>", off on every new connection).
// Test: nc <ip> 5000   (or PuTTY, connection type "Raw")
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "pico/stdlib.h"
#include "hardware/flash.h"
#include "hardware/sync.h"
#include "wizchip_conf.h"
#include "socket.h"
#include "dhcp.h"
#include "app.h"

#define SOCK_DHCP       0
#define SOCK_TCP        1
#define SOCK_MDNS       2
#define TCP_PORT        5000
#define DHCP_TIMEOUT_MS 15000
#define TX_BUF          8192            // a valve reply part can be about 4 KB

// used when DHCP fails
static const uint8_t static_ip[4] = { 192, 168, 1, 200 };
static const uint8_t static_sn[4] = { 255, 255, 255, 0 };
static const uint8_t static_gw[4] = { 192, 168, 1, 1 };

static net_state_t state = NET_NO_CHIP;
static bool using_dhcp;
static uint8_t dhcp_buf[1024];
static uint32_t t_dhcp_start, t_dhcp_tick, t_link_check, t_slow_poll;

// Without a link, the PHY is reset every LINK_RETRY_MS: at PoE power-up the supply rises in steps and
// the W5500 PHY sometimes never starts auto-negotiation. Every LINK_FULL_RESET-th attempt resets the
// whole chip (hardware reset line) instead.
#define LINK_RETRY_MS   5000
#define LINK_FULL_RESET 3
static uint32_t t_no_link;              // since when there has been no link
static uint32_t link_retries;           // PHY resets since the link was lost
static bool client_connected;

static char tx_buf[TX_BUF];             // ring buffer, filled by app_emit()
static size_t tx_head, tx_tail;
static bool tx_sending;                 // SEND issued, SEND_OK not seen yet
static bool rx_more;                    // more received data than one pass reads
static uint32_t t_tcp_poll;             // last full pass of tcp_task(), us
static char rx_line[96];
static size_t rx_len;

static bool debug_live;                 // "debug on": forward new log lines as "#DBG ..."
static uint32_t debug_cursor;
static bool log_dump;                   // "log": history being sent as "#LOG ..."
static uint32_t log_cursor;

static uint32_t now_ms(void) {
    return to_ms_since_boot(get_absolute_time());
}

net_state_t net_state(void) {
    return state;
}

void net_ip_string(char *buf, size_t size) {
    uint8_t ip[4];
    getSIPR(ip);
    snprintf(buf, size, "%u.%u.%u.%u", ip[0], ip[1], ip[2], ip[3]);
}

void net_queue(const char *s, size_t len) {
    if (!client_connected)
        return;
    while (len--) {
        size_t next = (tx_head + 1) % TX_BUF;
        if (next == tx_tail)
            return;                     // client too slow: drop
        tx_buf[tx_head] = *s++;
        tx_head = next;
    }
}

bool net_queue_fits(size_t len) {
    size_t used = (tx_head + TX_BUF - tx_tail) % TX_BUF;
    return client_connected && len < TX_BUF - 1 - used;
}

// MAC from the flash unique ID, locally administered (02:xx:xx:xx:xx:xx).
// The W55RP20 contains a Puya P25Q16 whose 128-bit UID starts with the lot code ("UM8868" + wafer),
// so the 64 bits pico_get_unique_board_id() reads are the same on many boards. Hence the full
// 128-bit UID (command 0x4B, 4 dummy bytes, 16 bytes) is read and hashed (FNV-1a 64) into 5 bytes.
static void make_mac(uint8_t mac[6]) {
    static uint8_t uid_mac[6];
    if (!uid_mac[0]) {                  // read once; net_init() runs again after a W5500 reset
        uint8_t tx[21] = { 0x4b }, rx[21] = { 0 };
        uint32_t irq = save_and_disable_interrupts();   // no XIP while the command runs
        flash_do_cmd(tx, rx, sizeof rx);
        restore_interrupts(irq);

        uint64_t h = 0xcbf29ce484222325ull;
        printf("FLASH: UID ");
        for (int i = 5; i < 21; i++) {
            printf("%02x", rx[i]);
            h = (h ^ rx[i]) * 0x100000001b3ull;
        }
        printf("\n");
        uid_mac[0] = 0x02;
        for (int i = 1; i < 6; i++)
            uid_mac[i] = (uint8_t)(h >> (8 * (i - 1)));
    }
    memcpy(mac, uid_mac, 6);
}

void net_init(void) {
    w5500_pio_spi_init();
    w5500_hw_reset();

    // KB per socket (TX, RX; at most 16 KB each). Only DHCP, TCP and mDNS are used. The TCP socket gets
    // 8 KB TX so that a whole valve reply (up to about 4 KB) goes out at once without waiting for an ACK
    // of the client (Windows delays ACKs by up to 200 ms); mDNS gets 8 KB RX for multicast bursts.
    uint8_t buf_sizes[2][8] = { { [SOCK_DHCP] = 2, [SOCK_TCP] = 8, [SOCK_MDNS] = 4 },
                                { [SOCK_DHCP] = 2, [SOCK_TCP] = 4, [SOCK_MDNS] = 8 } };
    if (ctlwizchip(CW_INIT_WIZCHIP, buf_sizes) != 0 || getVERSIONR() != 0x04) {
        printf("NET: W5500 not found (VERSIONR 0x%02x)\n", getVERSIONR());
        state = NET_NO_CHIP;
        return;
    }

    wiz_NetInfo info = { .dhcp = NETINFO_DHCP };
    make_mac(info.mac);
    ctlnetwork(CN_SET_NETINFO, &info);
    printf("NET: W5500 ok, MAC %02x:%02x:%02x:%02x:%02x:%02x\n",
           info.mac[0], info.mac[1], info.mac[2], info.mac[3], info.mac[4], info.mac[5]);
    state = NET_NO_LINK;
}

static void use_static_ip(void) {
    wiz_NetInfo info;
    ctlnetwork(CN_GET_NETINFO, &info);
    memcpy(info.ip, static_ip, 4);
    memcpy(info.sn, static_sn, 4);
    memcpy(info.gw, static_gw, 4);
    info.dhcp = NETINFO_STATIC;
    ctlnetwork(CN_SET_NETINFO, &info);
}

// moves debug log lines into the TCP send buffer as far as they fit (history first, then live)
static void forward_debug(void) {
    char text[168], out[176];
    while (log_dump || debug_live) {
        uint32_t *cursor = log_dump ? &log_cursor : &debug_cursor;
        uint32_t before = *cursor;
        if (!debug_log_read(cursor, text, sizeof text)) {
            if (!log_dump)
                return;                 // live: nothing new
            if (!net_queue_fits(9))
                return;
            net_queue("#LOG end\n", 9);
            log_dump = false;
            continue;
        }
        int n = snprintf(out, sizeof out, "%s %s\n", log_dump ? "#LOG" : "#DBG", text);
        if (n <= 0 || !net_queue_fits((size_t)n)) {
            *cursor = before;           // retry when there is room
            return;
        }
        net_queue(out, (size_t)n);
    }
}

static void handle_command(const char *cmd) {
    char reply[192];
    size_t n;

    // Valve commands are logged by valve.c after the USB transfer was started (a printf takes about
    // 60 us and would delay every request).
    bool valve_cmd = (cmd[0] == 'v' || cmd[0] == 't' || cmd[0] == 'c') && isdigit((unsigned char)cmd[1]);
    if (cmd[0] && !valve_cmd)
        printf("NET: command \"%s\"\n", cmd);

    if (strcmp(cmd, "log") == 0) {
        log_cursor = debug_log_oldest();
        log_dump = true;
        return;
    } else if (strcmp(cmd, "debug on") == 0) {
        debug_cursor = debug_log_newest();
        debug_live = true;
        n = snprintf(reply, sizeof reply, "#OK debug on\n");
    } else if (strcmp(cmd, "debug off") == 0) {
        debug_live = false;
        n = snprintf(reply, sizeof reply, "#OK debug off\n");
    } else if (strcmp(cmd, "status") == 0) {
        n = app_status(reply, sizeof reply);
    } else if (strcmp(cmd, "usb on") == 0) {
        usb_port_set(true);
        n = snprintf(reply, sizeof reply, "#OK usb on\n");
    } else if (strcmp(cmd, "usb off") == 0) {
        usb_port_set(false);
        n = snprintf(reply, sizeof reply, "#OK usb off\n");
    } else if (strcmp(cmd, "valves") == 0) {
        n = valve_list(reply, sizeof reply);
    } else if ((cmd[0] == 'v' || cmd[0] == 't') && isdigit((unsigned char)cmd[1])) {
        char *rest;
        unsigned long addr = strtoul(cmd + 1, &rest, 10);
        if (*rest != ' ' || addr > 255) {
            n = snprintf(reply, sizeof reply, "#ERR usage: v<addr> <command> or t<addr> <command>, e.g. v1 p:0B0F10010000\n");
        } else {
            while (*rest == ' ')
                rest++;
            valve_request((uint8_t)addr, cmd[0] == 't' ? 'T' : 'V', rest);
            return;
        }
    } else if (cmd[0] == 'c' && isdigit((unsigned char)cmd[1])) {
        char *rest;
        unsigned long addr = strtoul(cmd + 1, &rest, 10);
        if (*rest != 0 || addr > 255) {
            n = snprintf(reply, sizeof reply, "#ERR usage: c<addr>, e.g. c1\n");
        } else {
            valve_request((uint8_t)addr, 'C', "");
            return;
        }
    } else if (cmd[0]) {
        n = snprintf(reply, sizeof reply, "#ERR commands: status, usb on, usb off, valves, v<addr> <command>, t<addr> <command>, c<addr>, log, debug on, debug off\n");
    } else {
        return;
    }
    if (valve_cmd)
        printf("NET: command \"%s\"\n", cmd);   // usage error
    net_queue(reply, n);
}

// Moves as much of the ring buffer into the W5500 as there is room for and starts one SEND, never waits.
// (The ioLibrary send() waits in a loop until the W5500 has room for the whole block, i.e. until the
// client acknowledged older data; that stalled the main loop, and with it the USB side, for up to 50 ms.)
// ir: Sn_IR as read in this pass.
static void tcp_flush(uint8_t ir) {
    if (ir & Sn_IR_SENDOK) {
        setSn_IR(SOCK_TCP, Sn_IR_SENDOK);
        tx_sending = false;
    } else if (tx_sending) {
        return;                         // previous SEND still running (a timeout closes the socket)
    }
    // Only the contiguous part of the ring; the rest after the wrap goes with the next SEND. Two
    // wiz_send_data() calls in a row (TX_WR written and read back at once) lost data on the hardware.
    size_t n = tx_head >= tx_tail ? tx_head - tx_tail : TX_BUF - tx_tail;
    size_t room = getSn_TX_FSR(SOCK_TCP);
    if (n > room)
        n = room;
    if (!n)
        return;
    wiz_send_data(SOCK_TCP, (uint8_t *)&tx_buf[tx_tail], (uint16_t)n);
    tx_tail = (tx_tail + n) % TX_BUF;
    setSn_CR(SOCK_TCP, Sn_CR_SEND);
    while (getSn_CR(SOCK_TCP))
        ;
    tx_sending = true;
}

// Usually one register read (Sn_IR) per main loop pass. The full pass (state, receive, send) runs when
// the W5500 flags something (connect, data, send done, disconnect, timeout), while data waits to be sent
// or read, and at least every TCP_POLL_US for state changes without a flag (listen, close). Polling every
// register in every pass took about 85 us of SPI traffic and so delayed every command.
#define TCP_POLL_US 1000

static void tcp_task(void) {
    forward_debug();
    uint8_t ir = getSn_IR(SOCK_TCP);
    uint32_t now = time_us_32();
    if (!ir && !rx_more && tx_head == tx_tail && now - t_tcp_poll < TCP_POLL_US)
        return;
    t_tcp_poll = now;

    switch (getSn_SR(SOCK_TCP)) {
    case SOCK_ESTABLISHED: {
        if (ir & Sn_IR_CON) {
            setSn_IR(SOCK_TCP, Sn_IR_CON);
            uint8_t ip[4];
            getSn_DIPR(SOCK_TCP, ip);
            printf("NET: client %u.%u.%u.%u connected\n", ip[0], ip[1], ip[2], ip[3]);
            client_connected = true;
            tx_head = tx_tail = 0;
            tx_sending = false;
            rx_len = 0;
            debug_live = false;
            log_dump = false;
            char banner[192];
            size_t n = app_status(banner, sizeof banner);
            net_queue(banner, n);
        }

        if (ir & Sn_IR_RECV)
            setSn_IR(SOCK_TCP, Sn_IR_RECV);     // clear before reading: data arriving later sets it again
        uint8_t rx[256];
        int32_t len = getSn_RX_RSR(SOCK_TCP);
        rx_more = len > (int32_t)sizeof rx;
        if (len > 0) {
            len = recv(SOCK_TCP, rx, len > (int32_t)sizeof rx ? (int32_t)sizeof rx : len);
            for (int32_t i = 0; i < len; i++) {
                char c = (char)rx[i];
                if (c == '\r' || c == '\n') {
                    rx_line[rx_len] = 0;
                    handle_command(rx_line);
                    rx_len = 0;
                } else if (rx_len < sizeof rx_line - 1) {
                    rx_line[rx_len++] = c;
                }
            }
        }

        forward_debug();                // e.g. "log" was just received
        tcp_flush(ir);
        break;
    }
    case SOCK_CLOSE_WAIT:
        disconnect(SOCK_TCP);
        break;
    case SOCK_CLOSED:
        if (client_connected)
            printf("NET: client disconnected\n");
        client_connected = false;
        tx_sending = false;
        rx_more = false;
        // no delayed ACK: a command is acknowledged at once, so a client that writes a command in
        // several pieces (Nagle) is not held up by the W5500's 200 ms ACK delay
        socket(SOCK_TCP, Sn_MR_TCP, TCP_PORT, SF_TCP_NODELAY);
        break;
    case SOCK_INIT:
        listen(SOCK_TCP);
        break;
    default:
        break;
    }
    // flags handled by the state above (close() in socket() clears all of them anyway)
    ir &= Sn_IR_DISCON | Sn_IR_TIMEOUT | (client_connected ? 0 : Sn_IR_RECV | Sn_IR_SENDOK);
    if (ir)
        setSn_IR(SOCK_TCP, ir);
}

void net_task(void) {
    if (state == NET_NO_CHIP)
        return;

    uint32_t now = now_ms();

    if (now - t_link_check >= 100) {
        t_link_check = now;
        bool link = wizphy_getphylink() == PHY_LINK_ON;

        if (!link && state != NET_NO_LINK) {
            printf("NET: link down\n");
            if (using_dhcp)
                DHCP_stop();
            close(SOCK_TCP);
            mdns_stop();
            client_connected = false;
            state = NET_NO_LINK;
            t_no_link = now;
            link_retries = 0;
        } else if (!link && now - t_no_link >= LINK_RETRY_MS) {
            t_no_link = now;
            link_retries++;
            if (link_retries % LINK_FULL_RESET == 0) {
                printf("NET: no link, chip reset (attempt %lu)\n", (unsigned long)link_retries);
                net_init();             // hardware reset, buffers and MAC again
                if (state == NET_NO_CHIP)
                    return;
            } else {
                printf("NET: no link, PHY reset (attempt %lu)\n", (unsigned long)link_retries);
                wizphy_reset();
            }
        } else if (link && state == NET_NO_LINK) {
            if (link_retries)
                printf("NET: link up after %lu reset(s)\n", (unsigned long)link_retries);
            link_retries = 0;
            printf("NET: link up, DHCP ...\n");
            DHCP_init(SOCK_DHCP, dhcp_buf);
            using_dhcp = true;
            t_dhcp_start = t_dhcp_tick = now;
            state = NET_DHCP;
        }
    }

    if (using_dhcp && now - t_dhcp_tick >= 1000) {
        t_dhcp_tick += 1000;
        DHCP_time_handler();
    }

    if (state == NET_DHCP) {
        uint8_t r = DHCP_run();         // the default callbacks write IP/SN/GW into the W5500
        if (r == DHCP_IP_LEASED || r == DHCP_IP_ASSIGN || r == DHCP_IP_CHANGED) {
            char ip[16];
            net_ip_string(ip, sizeof ip);
            printf("NET: DHCP %s, lease %lu s, TCP port %u\n", ip, (unsigned long)getDHCPLeasetime(), TCP_PORT);
            mdns_start(SOCK_MDNS);
            state = NET_READY;
        } else if (r == DHCP_FAILED || now - t_dhcp_start > DHCP_TIMEOUT_MS) {
            DHCP_stop();
            using_dhcp = false;
            use_static_ip();
            printf("NET: no DHCP, static %u.%u.%u.%u, TCP port %u\n",
                   static_ip[0], static_ip[1], static_ip[2], static_ip[3], TCP_PORT);
            mdns_start(SOCK_MDNS);
            state = NET_READY;
        }
    } else if (state == NET_READY) {
        tcp_task();                     // every pass: the commands
        // DHCP lease renewal and mDNS do not need every pass (each poll reads several W5500 registers)
        if (now != t_slow_poll) {       // about every 1 ms mDNS, every 10 ms DHCP
            static unsigned slow_count;
            t_slow_poll = now;
            mdns_task();
            if (using_dhcp && ++slow_count % 10 == 0 && DHCP_run() == DHCP_IP_CHANGED)
                mdns_announce();
        }
    }
}
