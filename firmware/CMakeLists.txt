# Example firmware for the PoE-USB-HID bridge (Rev 4g, W55RP20)
#   USB host (TinyUSB): hub, keyboard/barcode scanner, mouse, generic HID, USB stick (FatFs)
#   Ethernet (W5500 via PIO-SPI, WIZnet ioLibrary): DHCP, TCP server for the HID data, mDNS/DNS-SD
#   Debug output: SEGGER RTT over SWD (no UART on the board)
cmake_minimum_required(VERSION 3.13)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)   # for VS Code IntelliSense (.vscode/settings.json)

set(PICO_BOARD poe_usb_hid_bridge)
set(PICO_BOARD_HEADER_DIRS ${CMAKE_CURRENT_LIST_DIR}/boards)

include(pico_sdk_import.cmake)

project(poe_usb_hid_bridge C CXX ASM)
set(CMAKE_C_STANDARD 11)
pico_sdk_init()

# WIZnet ioLibrary (W5500 driver, sockets, DHCP); local copy via -DIOLIBRARY_PATH=...
set(IOLIBRARY_TAG v3.2.0)   # 9dd655dfe1047937066ace80832c63bfb5f1ab47
if (NOT IOLIBRARY_PATH)
    include(FetchContent)
    FetchContent_Declare(iolibrary
        GIT_REPOSITORY https://github.com/Wiznet/ioLibrary_Driver.git
        GIT_TAG ${IOLIBRARY_TAG}
        GIT_SHALLOW TRUE)
    FetchContent_Populate(iolibrary)
    set(IOLIBRARY_PATH ${iolibrary_SOURCE_DIR})
endif()

add_library(iolibrary STATIC
    ${IOLIBRARY_PATH}/Ethernet/wizchip_conf.c
    ${IOLIBRARY_PATH}/Ethernet/socket.c
    ${IOLIBRARY_PATH}/Ethernet/W5500/w5500.c
    ${IOLIBRARY_PATH}/Internet/DHCP/dhcp.c)
target_include_directories(iolibrary PUBLIC
    ${IOLIBRARY_PATH}/Ethernet
    ${IOLIBRARY_PATH}/Internet/DHCP)
target_compile_definitions(iolibrary PUBLIC _WIZCHIP_=W5500)
target_compile_options(iolibrary PRIVATE -w)

# FatFs as shipped with TinyUSB (lib/tinyusb/lib/fatfs); disk_* glue is in src/msc_app.c
set(FATFS_DIR ${PICO_TINYUSB_PATH}/lib/fatfs/source)
add_library(fatfs STATIC
    ${FATFS_DIR}/ff.c
    ${FATFS_DIR}/ffsystem.c
    ${FATFS_DIR}/ffunicode.c)
target_include_directories(fatfs PUBLIC ${FATFS_DIR})
target_compile_options(fatfs PRIVATE -w)

add_executable(poe_usb_hid_bridge
    src/main.c
    src/led.c
    src/usb_port.c
    src/hid_app.c
    src/msc_app.c
    src/w5500_pio_spi.c
    src/net.c
    src/mdns.c)
target_include_directories(poe_usb_hid_bridge PRIVATE src)
target_compile_options(poe_usb_hid_bridge PRIVATE -Wall -Wextra -Wno-unused-parameter)
target_link_libraries(poe_usb_hid_bridge PRIVATE
    pico_stdlib
    pico_unique_id
    hardware_adc
    hardware_pio
    tinyusb_host
    iolibrary
    fatfs)

# printf -> RTT (J-Link / probe-rs); UART and USB stdio are not available on this board
pico_enable_stdio_rtt(poe_usb_hid_bridge 1)
pico_enable_stdio_uart(poe_usb_hid_bridge 0)
pico_enable_stdio_usb(poe_usb_hid_bridge 0)

# ELF + BIN (flash via SWD); no UF2: there is no BOOTSEL / USB device boot path
pico_add_bin_output(poe_usb_hid_bridge)
pico_add_map_output(poe_usb_hid_bridge)
