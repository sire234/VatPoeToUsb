// Status LED D11 (GPIO28, high = on)
#include "pico/stdlib.h"
#include "app.h"

static led_mode_t mode = LED_BOOT;
static absolute_time_t activity_until;

void led_init(void) {
    gpio_init(BOARD_STATUS_LED_PIN);
    gpio_set_dir(BOARD_STATUS_LED_PIN, GPIO_OUT);
    gpio_put(BOARD_STATUS_LED_PIN, 1);
}

void led_set_mode(led_mode_t m) {
    mode = m;
}

void led_activity(void) {
    activity_until = make_timeout_time_ms(30);
}

void led_task(void) {
    uint32_t t = to_ms_since_boot(get_absolute_time());
    bool on;

    switch (mode) {
    case LED_NO_LINK:
        on = (t % 1000) < 100;
        break;
    case LED_NO_IP:
        on = (t % 250) < 125;
        break;
    case LED_USB_FAULT: {
        uint32_t p = t % 1500;
        on = p < 900 && (p % 300) < 150;
        break;
    }
    case LED_READY:
        on = time_reached(activity_until);
        break;
    case LED_BOOT:
    default:
        on = true;
        break;
    }
    gpio_put(BOARD_STATUS_LED_PIN, on);
}
