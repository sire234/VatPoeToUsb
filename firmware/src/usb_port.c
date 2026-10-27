// USB-A port power: USB_EN (GPIO26) drives the TPS2553 load switch, VBUS_SENSE (ADC3) monitors VBUS.
//
// The TPS2553 limits the current (532-659 mA) but its FAULT output is not connected. An overload
// shows up as a VBUS dip, so the port is switched off when VBUS stays below VBUS_FAULT_V for
// FAULT_DEBOUNCE_MS (README "Inbetriebnahme": threshold 4.0-4.2 V, not 4.5 V, because VBUS can be
// 4.6 V worst case at 500 mA). Retries back off from RETRY_MIN_MS to RETRY_MAX_MS.
#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/adc.h"
#include "app.h"

#define VBUS_FAULT_V        4.1f
#define FAULT_DEBOUNCE_MS   50
#define BLANK_MS            100     // ignore the inrush dip right after switching on
#define RETRY_MIN_MS        1000
#define RETRY_MAX_MS        32000
#define STABLE_MS           10000   // this long without a fault resets the backoff

static bool port_on;
static bool fault;
static float vbus;
static uint32_t t_switched, t_below, t_retry, retry_delay = RETRY_MIN_MS, t_sample;

static uint32_t now_ms(void) {
    return to_ms_since_boot(get_absolute_time());
}

static float read_vbus(void) {
    return adc_read() * (3.3f / 4096.0f) / BOARD_VBUS_SENSE_FACTOR;
}

void usb_port_init(void) {
    gpio_init(BOARD_USB_EN_PIN);
    gpio_set_dir(BOARD_USB_EN_PIN, GPIO_OUT);
    gpio_put(BOARD_USB_EN_PIN, 0);

    adc_init();
    adc_gpio_init(BOARD_VBUS_SENSE_PIN);
    adc_select_input(BOARD_VBUS_SENSE_ADC);
    vbus = read_vbus();
}

void usb_port_set(bool on) {
    gpio_put(BOARD_USB_EN_PIN, on);
    port_on = on;
    t_switched = now_ms();
    t_below = 0;
    if (on)
        fault = false;
    // after switching off, VBUS only decays through R32/R33 (tau ~ 27 s, design_risks R-USB-4)
}

void usb_port_task(void) {
    uint32_t now = now_ms();

    if (now != t_sample) {          // 1 kHz sampling, IIR filter (~4 ms)
        t_sample = now;
        vbus += (read_vbus() - vbus) * 0.25f;
    }

    if (port_on) {
        if (now - t_switched < BLANK_MS)
            return;
        if (vbus < VBUS_FAULT_V) {
            if (!t_below)
                t_below = now;
            else if (now - t_below >= FAULT_DEBOUNCE_MS) {
                usb_port_set(false);
                fault = true;
                t_retry = now + retry_delay;
                printf("USB: VBUS %.2f V < %.1f V -> port off, retry in %lu ms\n",
                       vbus, VBUS_FAULT_V, (unsigned long)retry_delay);
                app_eventf("#USB overload, port off (VBUS %.2f V)\n", vbus);
                retry_delay = retry_delay * 2 > RETRY_MAX_MS ? RETRY_MAX_MS : retry_delay * 2;
            }
        } else {
            t_below = 0;
            if (now - t_switched > STABLE_MS)
                retry_delay = RETRY_MIN_MS;
        }
    } else if (fault && (int32_t)(now - t_retry) >= 0) {
        printf("USB: retry, port on\n");
        usb_port_set(true);
    }
}

bool usb_port_is_on(void) {
    return port_on;
}

bool usb_port_fault(void) {
    return fault;
}

float usb_port_vbus(void) {
    return vbus;
}
