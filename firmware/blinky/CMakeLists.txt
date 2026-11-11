# Minimal bring-up test: blinks D11 (GPIO28) at 2 Hz, prints a counter over SEGGER RTT
cmake_minimum_required(VERSION 3.13)

set(PICO_BOARD poe_usb_hid_bridge)
set(PICO_BOARD_HEADER_DIRS ${CMAKE_CURRENT_LIST_DIR}/../boards)

include(${CMAKE_CURRENT_LIST_DIR}/../pico_sdk_import.cmake)

project(blinky C CXX ASM)
set(CMAKE_C_STANDARD 11)
pico_sdk_init()

add_executable(blinky main.c)
target_link_libraries(blinky PRIVATE pico_stdlib)

pico_enable_stdio_rtt(blinky 1)
pico_enable_stdio_uart(blinky 0)
pico_enable_stdio_usb(blinky 0)

pico_add_bin_output(blinky)
