// Bring-up test for the PoE-USB-HID bridge: blink D11 (GPIO28), print over RTT
#include <stdio.h>
#include "pico/stdlib.h"

int main(void) {
    stdio_init_all();
    gpio_init(BOARD_STATUS_LED_PIN);
    gpio_set_dir(BOARD_STATUS_LED_PIN, GPIO_OUT);

    for (unsigned n = 0;; n++) {
        gpio_put(BOARD_STATUS_LED_PIN, n & 1);
        if (n % 2 == 0) printf("blinky %u\n", n / 2);
        sleep_ms(250);
    }
}
