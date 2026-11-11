// Hardware bring-up test for the PoE-USB-HID bridge (Rev 4g, W55RP20), powered without PoE.
// Every step prints PASS/FAIL over RTT; afterwards a status line (link, VBUS, temperature).
#include <stdarg.h>
#include <stdio.h>
#include <string.h>
#include "pico/stdlib.h"
#include "pico/unique_id.h"
#include "hardware/adc.h"
#include "hardware/clocks.h"
#include "hardware/flash.h"
#include "hardware/pio.h"
#include "hardware/sync.h"

static int fails;

static void result(bool ok, const char *name, const char *fmt, ...) __attribute__((format(printf, 3, 4)));
static void result(bool ok, const char *name, const char *fmt, ...) {
    char buf[160];
    va_list ap;
    va_start(ap, fmt);
    vsnprintf(buf, sizeof buf, fmt, ap);
    va_end(ap);
    printf("[%s] %-26s %s\n", ok ? "PASS" : "FAIL", name, buf);
    if (!ok)
        fails++;
}

static bool near(float v, float nominal, float tol) {
    return v > nominal - tol && v < nominal + tol;
}

// ---------------------------------------------------------------- 1. clocks
static void test_clocks(void) {
    printf("\n== 1. Takte ==\n");
    uint32_t xosc = frequency_count_khz(CLOCKS_FC0_SRC_VALUE_XOSC_CLKSRC);
    uint32_t sys  = frequency_count_khz(CLOCKS_FC0_SRC_VALUE_CLK_SYS);
    uint32_t usb  = frequency_count_khz(CLOCKS_FC0_SRC_VALUE_CLK_USB);
    uint32_t rosc = frequency_count_khz(CLOCKS_FC0_SRC_VALUE_ROSC_CLKSRC);
    result(near(xosc, 12000, 60), "Quarz Y1 12 MHz", "%lu kHz", (unsigned long)xosc);
    result(near(sys, 125000, 600), "clk_sys 125 MHz", "%lu kHz", (unsigned long)sys);
    result(near(usb, 48000, 240), "clk_usb 48 MHz", "%lu kHz", (unsigned long)usb);
    printf("       %-26s %lu kHz\n", "ROSC (Info)", (unsigned long)rosc);
}

// ---------------------------------------------------------------- 2. flash
#define TEST_SECTOR_OFS (PICO_FLASH_SIZE_BYTES - FLASH_SECTOR_SIZE)

static void test_flash(void) {
    printf("\n== 2. QSPI-Flash ==\n");
    uint8_t tx[4] = {0x9f, 0, 0, 0}, rx[4] = {0};
    uint32_t irq = save_and_disable_interrupts();
    flash_do_cmd(tx, rx, 4);
    restore_interrupts(irq);
    uint32_t size = (rx[3] >= 0x10 && rx[3] <= 0x19) ? 1u << rx[3] : 0;
    result(rx[1] != 0x00 && rx[1] != 0xff, "JEDEC-ID", "%02X %02X %02X", rx[1], rx[2], rx[3]);
    result(size == PICO_FLASH_SIZE_BYTES, "Groesse 2 MB", "%lu KB", (unsigned long)(size / 1024));

    char id[2 * PICO_UNIQUE_BOARD_ID_SIZE_BYTES + 1];
    pico_get_unique_board_id_string(id, sizeof id);
    printf("       %-26s %s\n", "Unique ID (Info)", id);

    static uint8_t pattern[FLASH_PAGE_SIZE];
    for (unsigned i = 0; i < sizeof pattern; i++)
        pattern[i] = (uint8_t)(i * 7 + 0x5a);
    const uint8_t *mapped = (const uint8_t *)(XIP_BASE + TEST_SECTOR_OFS);

    irq = save_and_disable_interrupts();
    flash_range_erase(TEST_SECTOR_OFS, FLASH_SECTOR_SIZE);
    restore_interrupts(irq);
    bool erased = true;
    for (unsigned i = 0; i < FLASH_SECTOR_SIZE; i++)
        if (mapped[i] != 0xff) { erased = false; break; }

    irq = save_and_disable_interrupts();
    flash_range_program(TEST_SECTOR_OFS, pattern, sizeof pattern);
    restore_interrupts(irq);
    bool written = memcmp(mapped, pattern, sizeof pattern) == 0;

    irq = save_and_disable_interrupts();
    flash_range_erase(TEST_SECTOR_OFS, FLASH_SECTOR_SIZE);
    restore_interrupts(irq);
    result(erased && written, "Erase/Write/Verify", "letzter Sektor 0x%06X: erase %s, write %s",
           TEST_SECTOR_OFS, erased ? "ok" : "FEHLER", written ? "ok" : "FEHLER");
}

// ---------------------------------------------------------------- 3./4. ADC, USB port
static float adc_volts(unsigned input) {
    adc_select_input(input);
    uint32_t sum = 0;
    for (int i = 0; i < 64; i++)
        sum += adc_read();
    return sum / 64.0f * 3.3f / 4096.0f;
}

static float temp_c(void) {
    return 27.0f - (adc_volts(4) - 0.706f) / 0.001721f;
}

static float vbus_v(void) {
    return adc_volts(BOARD_VBUS_SENSE_ADC) / BOARD_VBUS_SENSE_FACTOR;
}

static void test_adc_usb(void) {
    printf("\n== 3. ADC ==\n");
    adc_init();
    adc_set_temp_sensor_enabled(true);
    adc_gpio_init(BOARD_VBUS_SENSE_PIN);
    float t = temp_c();
    result(t > 0 && t < 70, "Chiptemperatur", "%.1f C", t);

    printf("\n== 4. USB-Port (TPS2553, VBUS_SENSE) ==\n");
    gpio_init(BOARD_USB_EN_PIN);
    gpio_set_dir(BOARD_USB_EN_PIN, GPIO_OUT);
    gpio_put(BOARD_USB_EN_PIN, 0);
    float off0 = vbus_v();
    printf("       %-26s %.2f V (Rest entlaedt langsam, tau ~27 s)\n", "VBUS aus (Start)", off0);

    gpio_put(BOARD_USB_EN_PIN, 1);
    sleep_ms(50);
    float on = vbus_v();
    // supplied here from the Pico VBUS (PC USB port) via TP9 and TPS2553
    result(on > 4.4f && on < 5.4f, "VBUS an", "%.2f V (erwartet 4,4-5,4 V)", on);

    gpio_put(BOARD_USB_EN_PIN, 0);
    sleep_ms(300);
    float off = vbus_v();
    result(off < on - 0.05f, "VBUS wieder aus", "%.2f V (faellt langsam ueber R32/R33)", off);
}

// ---------------------------------------------------------------- 5. W5500 (PIO-SPI, GPIO20-23)
static PIO pio = pio0;
static uint sm;
static const uint16_t spi_cpha0_instr[] = { 0x6101, 0x5101 };
static const pio_program_t spi_cpha0_program = { .instructions = spi_cpha0_instr, .length = 2, .origin = -1 };

static void spi_init_pio(float clkdiv) {
    gpio_init(W5500_CS_PIN);  gpio_set_dir(W5500_CS_PIN, GPIO_OUT);  gpio_put(W5500_CS_PIN, 1);
    gpio_init(W5500_RST_PIN); gpio_set_dir(W5500_RST_PIN, GPIO_OUT); gpio_put(W5500_RST_PIN, 1);
    gpio_init(W5500_INT_PIN); gpio_set_dir(W5500_INT_PIN, GPIO_IN);  gpio_pull_up(W5500_INT_PIN);

    uint offset = pio_add_program(pio, &spi_cpha0_program);
    sm = pio_claim_unused_sm(pio, true);
    pio_sm_config c = pio_get_default_sm_config();
    sm_config_set_wrap(&c, offset, offset + 1);
    sm_config_set_sideset(&c, 1, false, false);
    sm_config_set_out_pins(&c, W5500_MOSI_PIN, 1);
    sm_config_set_in_pins(&c, W5500_MISO_PIN);
    sm_config_set_sideset_pins(&c, W5500_SCK_PIN);
    sm_config_set_out_shift(&c, false, true, 8);
    sm_config_set_in_shift(&c, false, true, 8);
    sm_config_set_clkdiv(&c, clkdiv);
    uint32_t out_mask = (1u << W5500_SCK_PIN) | (1u << W5500_MOSI_PIN);
    pio_sm_set_pins_with_mask(pio, sm, 0, out_mask);
    pio_sm_set_pindirs_with_mask(pio, sm, out_mask, out_mask | (1u << W5500_MISO_PIN));
    pio_gpio_init(pio, W5500_MOSI_PIN);
    pio_gpio_init(pio, W5500_MISO_PIN);
    pio_gpio_init(pio, W5500_SCK_PIN);
    hw_set_bits(&pio->input_sync_bypass, 1u << W5500_MISO_PIN);
    pio_sm_init(pio, sm, offset, &c);
    pio_sm_set_enabled(pio, sm, true);
}

static void xfer(const uint8_t *tx, uint8_t *rx, size_t len) {
    io_rw_8 *txf = (io_rw_8 *)&pio->txf[sm];
    io_rw_8 *rxf = (io_rw_8 *)&pio->rxf[sm];
    size_t tr = len, rr = len;
    while (tr || rr) {
        if (tr && !pio_sm_is_tx_fifo_full(pio, sm)) { *txf = tx ? *tx++ : 0; tr--; }
        if (rr && !pio_sm_is_rx_fifo_empty(pio, sm)) { uint8_t b = *rxf; if (rx) *rx++ = b; rr--; }
    }
}

// W5500 frame: address (16 bit), control byte (BSB[4:0] RWB OM[1:0]), data; common block BSB = 0
static void w5500_read(uint16_t addr, uint8_t *buf, size_t len) {
    uint8_t hdr[3] = { addr >> 8, addr & 0xff, 0x00 };
    gpio_put(W5500_CS_PIN, 0);
    xfer(hdr, NULL, 3);
    xfer(NULL, buf, len);
    gpio_put(W5500_CS_PIN, 1);
}

static void w5500_write(uint16_t addr, const uint8_t *buf, size_t len) {
    uint8_t hdr[3] = { addr >> 8, addr & 0xff, 0x04 };
    gpio_put(W5500_CS_PIN, 0);
    xfer(hdr, NULL, 3);
    xfer(buf, NULL, len);
    gpio_put(W5500_CS_PIN, 1);
}

static uint8_t w5500_reg(uint16_t addr) {
    uint8_t v;
    w5500_read(addr, &v, 1);
    return v;
}

#define W5500_SHAR    0x0009
#define W5500_PHYCFGR 0x002E
#define W5500_VERSION 0x0039

static void print_phy(uint8_t phy) {
    printf("link %s, %s, %s duplex", (phy & 1) ? "UP" : "down",
           (phy & 2) ? "100 Mbit" : "10 Mbit", (phy & 4) ? "full" : "half");
}

static void test_w5500(void) {
    printf("\n== 5. W5500 ==\n");
    spi_init_pio(8.0f);                   // slow first: SCK = 125 MHz / 32 = 3.9 MHz
    gpio_put(W5500_RST_PIN, 0);
    sleep_ms(1);
    gpio_put(W5500_RST_PIN, 1);
    sleep_ms(2);

    uint8_t ver = w5500_reg(W5500_VERSION);
    result(ver == 0x04, "VERSIONR (3,9 MHz)", "0x%02X (erwartet 0x04)", ver);

    const uint8_t mac[6] = { 0x02, 0x55, 0xaa, 0x33, 0xcc, 0x0f };
    uint8_t back[6] = {0};
    w5500_write(W5500_SHAR, mac, 6);
    w5500_read(W5500_SHAR, back, 6);
    result(memcmp(mac, back, 6) == 0, "Register R/W (SHAR)", "%02X:%02X:%02X:%02X:%02X:%02X",
           back[0], back[1], back[2], back[3], back[4], back[5]);

    pio_sm_set_clkdiv(pio, sm, 2.0f);     // production speed: 15.6 MHz
    int bad = 0;
    for (int i = 0; i < 1000; i++)
        if (w5500_reg(W5500_VERSION) != 0x04)
            bad++;
    result(bad == 0, "VERSIONR x1000 (15,6 MHz)", "%d Fehler", bad);

    result(gpio_get(W5500_INT_PIN), "INTn Ruhepegel high", "%d", gpio_get(W5500_INT_PIN));

    uint8_t phy = w5500_reg(W5500_PHYCFGR);
    printf("       %-26s 0x%02X ", "PHYCFGR", phy);
    print_phy(phy);
    printf(" (ohne Kabel ist down korrekt)\n");
}

// ---------------------------------------------------------------- main
int main(void) {
    stdio_init_all();
    gpio_init(BOARD_STATUS_LED_PIN);
    gpio_set_dir(BOARD_STATUS_LED_PIN, GPIO_OUT);
    gpio_put(BOARD_STATUS_LED_PIN, 1);
    sleep_ms(1500);                       // give the RTT host time to attach

    printf("\n######## HW-Test PoE-USB-HID-Bridge Rev 4g ########\n");
    test_clocks();
    test_flash();
    test_adc_usb();
    test_w5500();
    printf("\n######## Ergebnis: %s (%d Fehler) ########\n\n", fails ? "FEHLER" : "ALLES OK", fails);

    // status loop: LED 1 Hz = all ok, 5 Hz = failures; prints on link change and every 10 s
    uint8_t last_phy = 0xff;
    absolute_time_t next_print = get_absolute_time();
    for (unsigned n = 0;; n++) {
        gpio_put(BOARD_STATUS_LED_PIN, n & 1);
        sleep_ms(fails ? 100 : 500);
        uint8_t phy = w5500_reg(W5500_PHYCFGR);
        if (phy != last_phy || time_reached(next_print)) {
            printf("status: ");
            print_phy(phy);
            printf(" | VBUS %.2f V | %.1f C\n", vbus_v(), temp_c());
            last_phy = phy;
            next_print = make_timeout_time_ms(10000);
        }
    }
}
