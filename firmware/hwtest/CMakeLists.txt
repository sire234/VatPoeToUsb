# Hardware bring-up test (no PoE needed): clocks, flash, ADC, USB port switch, W5500.
# Results go to SEGGER RTT:  probe-rs run --chip RP2040 build/hwtest.elf
cmake_minimum_required(VERSION 3.13)

set(PICO_BOARD poe_usb_hid_bridge)
set(PICO_BOARD_HEADER_DIRS ${CMAKE_CURRENT_LIST_DIR}/../boards)

include(${CMAKE_CURRENT_LIST_DIR}/../pico_sdk_import.cmake)

project(hwtest C CXX ASM)
set(CMAKE_C_STANDARD 11)
pico_sdk_init()

add_executable(hwtest main.c)
target_compile_options(hwtest PRIVATE -Wall -Wextra)
target_link_libraries(hwtest PRIVATE
    pico_stdlib
    pico_unique_id
    hardware_adc
    hardware_clocks
    hardware_flash
    hardware_pio)

pico_enable_stdio_rtt(hwtest 1)
pico_enable_stdio_uart(hwtest 0)
pico_enable_stdio_usb(hwtest 0)

pico_add_bin_output(hwtest)
