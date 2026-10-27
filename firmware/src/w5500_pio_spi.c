// W5500 inside the W55RP20: SPI on GPIO20-23 via PIO, because these pins do not match a hardware
// SPI pin set (SCK would have to be 18/22, TX 19/23). SPI mode 0, MSB first, 8-bit frames.
//
// PIO program (same as spi_cpha0 in pico-examples/pio/spi), hand-assembled so no pioasm
// (host compiler) is needed:
//     .side_set 1
//     out pins, 1  side 0 [1]   ; 0x6101  MOSI changes while SCK is low
//     in  pins, 1  side 1 [1]   ; 0x5101  MISO sampled on the rising edge
// 4 PIO cycles per bit: SCK = clk_sys / (4 * W5500_SPI_CLKDIV) = 125 MHz / 8 = 15.6 MHz.
#include "pico/stdlib.h"
#include "hardware/pio.h"
#include "wizchip_conf.h"
#include "app.h"

#define W5500_SPI_CLKDIV 2.0f

static const uint16_t spi_cpha0_instr[] = { 0x6101, 0x5101 };
static const pio_program_t spi_cpha0_program = {
    .instructions = spi_cpha0_instr,
    .length = 2,
    .origin = -1,
};

static PIO pio = pio0;
static uint sm;

static void xfer(const uint8_t *tx, uint8_t *rx, size_t len) {
    // 8-bit writes to the FIFO are replicated over all byte lanes, so with a left shift and an
    // 8-bit autopull the byte goes out MSB first; the received byte lands in the low bits
    io_rw_8 *txfifo = (io_rw_8 *)&pio->txf[sm];
    io_rw_8 *rxfifo = (io_rw_8 *)&pio->rxf[sm];
    size_t tx_remain = len, rx_remain = len;

    while (tx_remain || rx_remain) {
        if (tx_remain && !pio_sm_is_tx_fifo_full(pio, sm)) {
            *txfifo = tx ? *tx++ : 0;
            --tx_remain;
        }
        if (rx_remain && !pio_sm_is_rx_fifo_empty(pio, sm)) {
            uint8_t b = *rxfifo;
            if (rx)
                *rx++ = b;
            --rx_remain;
        }
    }
}

static void cs_select(void) {
    gpio_put(W5500_CS_PIN, 0);
}

static void cs_deselect(void) {
    gpio_put(W5500_CS_PIN, 1);
}

static uint8_t spi_read_byte(void) {
    uint8_t b;
    xfer(NULL, &b, 1);
    return b;
}

static void spi_write_byte(uint8_t b) {
    xfer(&b, NULL, 1);
}

static void spi_read_burst(uint8_t *buf, uint16_t len) {
    xfer(NULL, buf, len);
}

static void spi_write_burst(uint8_t *buf, uint16_t len) {
    xfer(buf, NULL, len);
}

void w5500_pio_spi_init(void) {
    gpio_init(W5500_CS_PIN);
    gpio_set_dir(W5500_CS_PIN, GPIO_OUT);
    gpio_put(W5500_CS_PIN, 1);

    gpio_init(W5500_RST_PIN);
    gpio_set_dir(W5500_RST_PIN, GPIO_OUT);
    gpio_put(W5500_RST_PIN, 1);

    gpio_init(W5500_INT_PIN);           // not used (polling), defined level only
    gpio_set_dir(W5500_INT_PIN, GPIO_IN);
    gpio_pull_up(W5500_INT_PIN);

    uint offset = pio_add_program(pio, &spi_cpha0_program);
    sm = pio_claim_unused_sm(pio, true);

    pio_sm_config c = pio_get_default_sm_config();
    sm_config_set_wrap(&c, offset, offset + spi_cpha0_program.length - 1);
    sm_config_set_sideset(&c, 1, false, false);
    sm_config_set_out_pins(&c, W5500_MOSI_PIN, 1);
    sm_config_set_in_pins(&c, W5500_MISO_PIN);
    sm_config_set_sideset_pins(&c, W5500_SCK_PIN);
    sm_config_set_out_shift(&c, false, true, 8);
    sm_config_set_in_shift(&c, false, true, 8);
    sm_config_set_clkdiv(&c, W5500_SPI_CLKDIV);

    uint32_t out_mask = (1u << W5500_SCK_PIN) | (1u << W5500_MOSI_PIN);
    pio_sm_set_pins_with_mask(pio, sm, 0, out_mask);
    pio_sm_set_pindirs_with_mask(pio, sm, out_mask, out_mask | (1u << W5500_MISO_PIN));
    pio_gpio_init(pio, W5500_MOSI_PIN);
    pio_gpio_init(pio, W5500_MISO_PIN);
    pio_gpio_init(pio, W5500_SCK_PIN);
    hw_set_bits(&pio->input_sync_bypass, 1u << W5500_MISO_PIN);

    pio_sm_init(pio, sm, offset, &c);
    pio_sm_set_enabled(pio, sm, true);

    reg_wizchip_cs_cbfunc(cs_select, cs_deselect);
    reg_wizchip_spi_cbfunc(spi_read_byte, spi_write_byte);
    reg_wizchip_spiburst_cbfunc(spi_read_burst, spi_write_burst);
}

void w5500_hw_reset(void) {
    gpio_put(W5500_RST_PIN, 0);
    sleep_ms(1);                        // RSTn low >= 500 us
    gpio_put(W5500_RST_PIN, 1);
    sleep_ms(2);                        // PLL lock (< 1 ms)
}
