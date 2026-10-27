// PoE-USB-HID bridge, example firmware (Rev 4g, W55RP20)
//
// Main loop without RTOS: TinyUSB host, USB port supervision, Ethernet, USB stick log, status LED.
// Debug output (printf) goes to SEGGER RTT, read it with J-Link RTT Viewer or probe-rs.
#include <stdarg.h>
#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/watchdog.h"
#include "tusb.h"
#include "app.h"

#define WATCHDOG_MS 3000    // paused while the debugger halts the core

void app_emit(const char *s, size_t len) {
    net_queue(s, len);
    msc_log_queue(s, len);
}

void app_eventf(const char *fmt, ...) {
    char buf[128];
    va_list ap;
    va_start(ap, fmt);
    int n = vsnprintf(buf, sizeof buf, fmt, ap);
    va_end(ap);
    if (n > 0)
        app_emit(buf, (size_t)n < sizeof buf ? (size_t)n : sizeof buf - 1);
}

size_t app_status(char *buf, size_t size) {
    static const char *const net_names[] = { "no W5500", "no link", "DHCP", "ready" };
    char ip[16];
    net_ip_string(ip, sizeof ip);
    int n = snprintf(buf, size, "#STATUS up=%lus ip=%s host=%s net=%s usb=%s vbus=%.2fV stick=%s\n",
                     (unsigned long)(to_ms_since_boot(get_absolute_time()) / 1000), ip, mdns_hostname(),
                     net_names[net_state()],
                     usb_port_fault() ? "fault" : usb_port_is_on() ? "on" : "off",
                     usb_port_vbus(), msc_app_mounted() ? "logging" : "none");
    return n < 0 ? 0 : ((size_t)n < size ? (size_t)n : size - 1);
}

static void update_led(void) {
    if (usb_port_fault())
        led_set_mode(LED_USB_FAULT);
    else if (net_state() == NET_NO_LINK || net_state() == NET_NO_CHIP)
        led_set_mode(LED_NO_LINK);
    else if (net_state() == NET_DHCP)
        led_set_mode(LED_NO_IP);
    else
        led_set_mode(LED_READY);
}

// called by TinyUSB for every attached device (also hubs)
void tuh_mount_cb(uint8_t dev_addr) {
    uint16_t vid = 0, pid = 0;
    tuh_vid_pid_get(dev_addr, &vid, &pid);
    printf("USB: device %u attached, %04x:%04x\n", dev_addr, vid, pid);
}

void tuh_umount_cb(uint8_t dev_addr) {
    printf("USB: device %u removed\n", dev_addr);
}

int main(void) {
    stdio_init_all();
    led_init();
    printf("\nPoE-USB-HID bridge, example firmware (%s %s)\n", __DATE__, __TIME__);
    if (watchdog_caused_reboot())
        printf("WARNING: reset by watchdog\n");

    usb_port_init();                    // port stays off until the host stack runs
    tusb_rhport_init_t host_init = { .role = TUSB_ROLE_HOST, .speed = TUSB_SPEED_AUTO };
    tusb_init(BOARD_TUH_RHPORT, &host_init);
    usb_port_set(true);

    net_init();
    watchdog_enable(WATCHDOG_MS, true);

    while (true) {
        watchdog_update();
        tuh_task();
        usb_port_task();
        net_task();
        msc_app_task();
        update_led();
        led_task();
    }
}
