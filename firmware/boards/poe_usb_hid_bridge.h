/*
 * Board definition: PoE-USB-HID bridge Rev 4g (WIZnet W55RP20 = RP2040 + W5500 + 2 MB flash)
 * Flash/boot2 as on the WIZnet W55RP20-EVB; pin numbers from architecture/net_plan.md.
 */

#ifndef _BOARDS_POE_USB_HID_BRIDGE_H
#define _BOARDS_POE_USB_HID_BRIDGE_H

pico_board_cmake_set(PICO_PLATFORM, rp2040)

#define POE_USB_HID_BRIDGE

// --- board signals ---
#define BOARD_USB_EN_PIN        26  // TPS2553 EN, active high, R26 pull-down -> port off at reset
#define BOARD_STATUS_LED_PIN    28  // D11 green via R38 330 R, high = on ("LED_DIN")
#define BOARD_VBUS_SENSE_PIN    29  // ADC3, divider R32 100k / R33 68k
#define BOARD_VBUS_SENSE_ADC    3
#define BOARD_VBUS_SENSE_FACTOR 0.405f

// --- W5500 inside the W55RP20 (not bonded out), PIO-SPI ---
#define W5500_CS_PIN            20
#define W5500_SCK_PIN           21
#define W5500_MISO_PIN          22
#define W5500_MOSI_PIN          23
#define W5500_INT_PIN           24
#define W5500_RST_PIN           25

#ifndef PICO_DEFAULT_LED_PIN
#define PICO_DEFAULT_LED_PIN    BOARD_STATUS_LED_PIN
#endif

// no UART, I2C or SPI pins are bonded out (GPIO0/1 open, see design_risks R4d-1)

// --- flash: 2 MB in the W55RP20 package ---
#define PICO_BOOT_STAGE2_CHOOSE_W25Q080 1

#ifndef PICO_FLASH_SPI_CLKDIV
#define PICO_FLASH_SPI_CLKDIV 2
#endif

pico_board_cmake_set_default(PICO_FLASH_SIZE_BYTES, (2 * 1024 * 1024))
#ifndef PICO_FLASH_SIZE_BYTES
#define PICO_FLASH_SIZE_BYTES (2 * 1024 * 1024)
#endif

// crystal Y1 = Raspberry Pi reference (ABM8-272-T3); extra start-up margin
#ifndef PICO_XOSC_STARTUP_DELAY_MULTIPLIER
#define PICO_XOSC_STARTUP_DELAY_MULTIPLIER 64
#endif

#ifndef PICO_RP2040_B0_SUPPORTED
#define PICO_RP2040_B0_SUPPORTED 0
#endif

#endif
