// Interfaces between the firmware modules (all run in the main loop, no RTOS, no second core)
#ifndef APP_H
#define APP_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// ---- main.c ----
// HID data / events: to the TCP client (net.c) and to the log file on a USB stick (msc_app.c)
void app_emit(const char *s, size_t len);
void app_eventf(const char *fmt, ...) __attribute__((format(printf, 1, 2)));
size_t app_status(char *buf, size_t size);

// ---- led.c: status LED D11 ----
typedef enum {
    LED_BOOT,       // on: starting
    LED_NO_LINK,    // short flash every second: no Ethernet link
    LED_NO_IP,      // 4 Hz: link up, waiting for DHCP
    LED_READY,      // on, flickers off on HID activity
    LED_USB_FAULT,  // 3 flashes, pause: USB port switched off (overload)
} led_mode_t;

void led_init(void);
void led_set_mode(led_mode_t mode);
void led_activity(void);
void led_task(void);

// ---- usb_port.c: VBUS switch (TPS2553) and overload detection ----
void usb_port_init(void);
void usb_port_set(bool on);
void usb_port_task(void);
bool usb_port_is_on(void);
bool usb_port_fault(void);
float usb_port_vbus(void);

// ---- hid_app.c: TinyUSB HID host callbacks only ----

// ---- msc_app.c: USB stick, FatFs, HIDLOG.TXT ----
void msc_app_task(void);
void msc_log_queue(const char *s, size_t len);
bool msc_app_mounted(void);

// ---- w5500_pio_spi.c: W5500 inside the W55RP20 ----
void w5500_pio_spi_init(void);
void w5500_hw_reset(void);

// ---- net.c: link, DHCP, TCP server ----
typedef enum { NET_NO_CHIP, NET_NO_LINK, NET_DHCP, NET_READY } net_state_t;

void net_init(void);
void net_task(void);
net_state_t net_state(void);
void net_queue(const char *s, size_t len);
void net_ip_string(char *buf, size_t size);

// ---- mdns.c: poe-hid-xxxxxx.local + DNS-SD _poehid._tcp ----
void mdns_start(uint8_t sn);
void mdns_stop(void);
void mdns_announce(void);
void mdns_task(void);
const char *mdns_hostname(void);

#endif
