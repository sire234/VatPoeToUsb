// Ethernet: link supervision, DHCP (fallback to a static address), TCP server on TCP_PORT.
//
// The TCP client receives everything app_emit() produces: plain ASCII from keyboards / barcode
// scanners ("\r\n" after Enter) and '#'-prefixed lines for events, mice and other HID devices.
// Commands from the client (one per line): "status", "usb on", "usb off".
// Test: nc <ip> 5000   (or PuTTY, connection type "Raw")
#include <stdio.h>
#include <string.h>
#include "pico/stdlib.h"
#include "pico/unique_id.h"
#include "wizchip_conf.h"
#include "socket.h"
#include "dhcp.h"
#include "app.h"

#define SOCK_DHCP       0
#define SOCK_TCP        1
#define SOCK_MDNS       2
#define TCP_PORT        5000
#define DHCP_TIMEOUT_MS 15000
#define TX_BUF          2048

// used when DHCP fails
static const uint8_t static_ip[4] = { 192, 168, 1, 200 };
static const uint8_t static_sn[4] = { 255, 255, 255, 0 };
static const uint8_t static_gw[4] = { 192, 168, 1, 1 };

static net_state_t state = NET_NO_CHIP;
static bool using_dhcp;
static uint8_t dhcp_buf[1024];
static uint32_t t_dhcp_start, t_dhcp_tick, t_link_check;
static bool client_connected;

static char tx_buf[TX_BUF];             // ring buffer, filled by app_emit()
static size_t tx_head, tx_tail;
static char rx_line[64];
static size_t rx_len;

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

void net_init(void) {
    w5500_pio_spi_init();
    w5500_hw_reset();

    uint8_t buf_sizes[2][8] = { { 2, 2, 2, 2, 2, 2, 2, 2 }, { 2, 2, 2, 2, 2, 2, 2, 2 } };  // KB per socket
    if (ctlwizchip(CW_INIT_WIZCHIP, buf_sizes) != 0 || getVERSIONR() != 0x04) {
        printf("NET: W5500 not found (VERSIONR 0x%02x)\n", getVERSIONR());
        state = NET_NO_CHIP;
        return;
    }

    // MAC from the flash unique ID, locally administered (02:xx:xx:xx:xx:xx)
    pico_unique_board_id_t id;
    pico_get_unique_board_id(&id);
    wiz_NetInfo info = { .mac = { 0x02, id.id[3], id.id[4], id.id[5], id.id[6], id.id[7] },
                         .dhcp = NETINFO_DHCP };
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

static void handle_command(const char *cmd) {
    char reply[192];
    size_t n;

    if (strcmp(cmd, "status") == 0) {
        n = app_status(reply, sizeof reply);
    } else if (strcmp(cmd, "usb on") == 0) {
        usb_port_set(true);
        n = snprintf(reply, sizeof reply, "#OK usb on\n");
    } else if (strcmp(cmd, "usb off") == 0) {
        usb_port_set(false);
        n = snprintf(reply, sizeof reply, "#OK usb off\n");
    } else if (cmd[0]) {
        n = snprintf(reply, sizeof reply, "#ERR commands: status, usb on, usb off\n");
    } else {
        return;
    }
    net_queue(reply, n);
}

static void tcp_task(void) {
    switch (getSn_SR(SOCK_TCP)) {
    case SOCK_ESTABLISHED: {
        if (getSn_IR(SOCK_TCP) & Sn_IR_CON) {
            setSn_IR(SOCK_TCP, Sn_IR_CON);
            uint8_t ip[4];
            getSn_DIPR(SOCK_TCP, ip);
            printf("NET: client %u.%u.%u.%u connected\n", ip[0], ip[1], ip[2], ip[3]);
            client_connected = true;
            tx_head = tx_tail = 0;
            rx_len = 0;
            char banner[128];
            size_t n = app_status(banner, sizeof banner);
            net_queue(banner, n);
        }

        uint8_t rx[64];
        int32_t len = getSn_RX_RSR(SOCK_TCP);
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

        // send what is contiguous in the ring buffer; send() blocks until the W5500 accepted it
        if (tx_tail != tx_head) {
            size_t n = tx_head > tx_tail ? tx_head - tx_tail : TX_BUF - tx_tail;
            int32_t sent = send(SOCK_TCP, (uint8_t *)&tx_buf[tx_tail], (uint16_t)n);
            if (sent > 0)
                tx_tail = (tx_tail + (size_t)sent) % TX_BUF;
        }
        break;
    }
    case SOCK_CLOSE_WAIT:
        disconnect(SOCK_TCP);
        break;
    case SOCK_CLOSED:
        if (client_connected)
            printf("NET: client disconnected\n");
        client_connected = false;
        socket(SOCK_TCP, Sn_MR_TCP, TCP_PORT, 0);
        break;
    case SOCK_INIT:
        listen(SOCK_TCP);
        break;
    default:
        break;
    }
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
        } else if (link && state == NET_NO_LINK) {
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
        if (using_dhcp && DHCP_run() == DHCP_IP_CHANGED)   // lease renewal
            mdns_announce();
        tcp_task();
        mdns_task();
    }
}
