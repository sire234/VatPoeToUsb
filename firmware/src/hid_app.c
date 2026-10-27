// HID host: keyboards / barcode scanners -> ASCII text, mice -> "#MOUSE" lines, other HID -> hex.
// Keyboards and mice run in the boot protocol (TinyUSB default), i.e. fixed 8 / 3-5 byte reports.
// The ASCII table is the US layout; set barcode scanners to "USB keyboard, US layout".
#include <stdio.h>
#include "tusb.h"
#include "app.h"

static const uint8_t keycode2ascii[128][2] = { HID_KEYCODE_TO_ASCII };

// previous keyboard report per device address, to detect newly pressed keys
static hid_keyboard_report_t prev_kbd[CFG_TUH_DEVICE_MAX + 1];

static const char *protocol_name(uint8_t p) {
    return p == HID_ITF_PROTOCOL_KEYBOARD ? "keyboard" : p == HID_ITF_PROTOCOL_MOUSE ? "mouse" : "generic";
}

static bool key_in_report(const hid_keyboard_report_t *r, uint8_t keycode) {
    for (int i = 0; i < 6; i++)
        if (r->keycode[i] == keycode)
            return true;
    return false;
}

static void process_keyboard(uint8_t dev_addr, const hid_keyboard_report_t *r) {
    hid_keyboard_report_t *prev = &prev_kbd[dev_addr];
    bool shift = r->modifier & (KEYBOARD_MODIFIER_LEFTSHIFT | KEYBOARD_MODIFIER_RIGHTSHIFT);
    char out[12];
    size_t n = 0;

    for (int i = 0; i < 6; i++) {
        uint8_t kc = r->keycode[i];
        if (kc == 0 || kc >= 128 || key_in_report(prev, kc))
            continue;
        char ch = (char)keycode2ascii[kc][shift ? 1 : 0];
        if (ch == '\r') {           // Enter / keypad Enter: end of a barcode
            out[n++] = '\r';
            out[n++] = '\n';
        } else if (ch) {
            out[n++] = ch;
        }
    }
    *prev = *r;
    if (n)
        app_emit(out, n);
}

static void process_mouse(const uint8_t *report, uint16_t len) {
    if (len < 3)
        return;
    const hid_mouse_report_t *m = (const hid_mouse_report_t *)report;
    app_eventf("#MOUSE b=%u x=%d y=%d w=%d\n", m->buttons, m->x, m->y, len >= 4 ? m->wheel : 0);
}

static void process_generic(uint8_t dev_addr, uint8_t idx, const uint8_t *report, uint16_t len) {
    char line[16 + 3 * 64 + 2];
    size_t n = snprintf(line, sizeof line, "#HID %u.%u:", dev_addr, idx);
    for (uint16_t i = 0; i < len && i < 64; i++)
        n += snprintf(line + n, sizeof line - n, " %02x", report[i]);
    n += snprintf(line + n, sizeof line - n, "\n");
    app_emit(line, n);
}

void tuh_hid_mount_cb(uint8_t dev_addr, uint8_t idx, const uint8_t *desc, uint16_t desc_len) {
    uint16_t vid = 0, pid = 0;
    tuh_vid_pid_get(dev_addr, &vid, &pid);
    uint8_t proto = tuh_hid_interface_protocol(dev_addr, idx);

    printf("HID: mount addr %u idx %u %04x:%04x %s, report desc %u bytes\n",
           dev_addr, idx, vid, pid, protocol_name(proto), desc_len);
    app_eventf("#HID connected %u.%u %04x:%04x %s\n", dev_addr, idx, vid, pid, protocol_name(proto));

    if (proto == HID_ITF_PROTOCOL_KEYBOARD)
        memset(&prev_kbd[dev_addr], 0, sizeof prev_kbd[dev_addr]);
    if (!tuh_hid_receive_report(dev_addr, idx))
        printf("HID: cannot request report from %u.%u\n", dev_addr, idx);
}

void tuh_hid_umount_cb(uint8_t dev_addr, uint8_t idx) {
    printf("HID: unmount addr %u idx %u\n", dev_addr, idx);
    app_eventf("#HID disconnected %u.%u\n", dev_addr, idx);
}

void tuh_hid_report_received_cb(uint8_t dev_addr, uint8_t idx, const uint8_t *report, uint16_t len) {
    switch (tuh_hid_interface_protocol(dev_addr, idx)) {
    case HID_ITF_PROTOCOL_KEYBOARD:
        if (len >= sizeof(hid_keyboard_report_t))
            process_keyboard(dev_addr, (const hid_keyboard_report_t *)report);
        break;
    case HID_ITF_PROTOCOL_MOUSE:
        process_mouse(report, len);
        break;
    default:
        process_generic(dev_addr, idx, report, len);
        break;
    }
    led_activity();

    if (!tuh_hid_receive_report(dev_addr, idx))
        printf("HID: cannot request report from %u.%u\n", dev_addr, idx);
}
