// TinyUSB configuration: host only on the RP2040 native USB (USB-A port J2)
#ifndef _TUSB_CONFIG_H_
#define _TUSB_CONFIG_H_

#ifndef CFG_TUSB_MCU
#error CFG_TUSB_MCU must be defined
#endif

#ifndef CFG_TUSB_OS
#define CFG_TUSB_OS             OPT_OS_PICO
#endif

#ifndef CFG_TUSB_DEBUG
#define CFG_TUSB_DEBUG          0
#endif

#define CFG_TUH_MEM_SECTION
#define CFG_TUH_MEM_ALIGN       __attribute__ ((aligned(4)))

#define CFG_TUH_ENABLED         1
#define BOARD_TUH_RHPORT        0
#define CFG_TUH_MAX_SPEED       OPT_MODE_FULL_SPEED   // RP2040 USB is full speed only

#define CFG_TUH_ENUMERATION_BUFSIZE 256

#define CFG_TUH_HUB             1                     // one external hub (e.g. keyboard + stick)
#define CFG_TUH_DEVICE_MAX      (3 * CFG_TUH_HUB + 1) // devices behind the hub + the hub itself
#define CFG_TUH_HID             (3 * CFG_TUH_DEVICE_MAX) // keyboards often have 2-3 HID interfaces
#define CFG_TUH_MSC             1
#define CFG_TUH_CDC             0
#define CFG_TUH_VENDOR          0

#define CFG_TUH_HID_EPIN_BUFSIZE    64
#define CFG_TUH_HID_EPOUT_BUFSIZE   64

#endif
