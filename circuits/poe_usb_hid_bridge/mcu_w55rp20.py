"""B5 W55RP20 MCU block — RP2040 + W5500 + Flash SiP with decoupling, +3V3A ferrite, crystals, EXRES, TOCAP/1V2O, RUN/BOOTSEL, SWD/UART test pads
Block from: architecture/net_plan.md section 8 "B5"
Interface nets: +3V3, +3V3A, GND, ETH_TXP, ETH_TXN, ETH_RXP, ETH_RXN, USB_DP_MCU, USB_DM_MCU, USB_EN, VBUS_SENSE, LED_DIN,
                ETH_LED_LINK_N, ETH_LED_ACT_N
Rev 4b: RGB GPIOs reduced to one line LED_DIN = GPIO28 (pin 48), GPIO27 (47) and GPIO19 (41) NC.
Rev 4f: LED_DIN drives the plain green status LED D11 (name kept from the WS2812 design).
Rev 4g: W5500 LED outputs 37 LINKLED / 39 ACTLED drive the MagJack LEDs (Rev 4b-4f: NC).
Rev 4d (based on Rev 4b, Rev-4c bridges/pads NOT taken over):
  - UART0 (GPIO0/1, pins 65/66) open, no pads.
  - RUN (pin 29) open: RP2040 DS Table 619 "RUN ... Reset State Pull-Up" (Pico DS: ~50 kOhm
    on-chip pull-up). R23, C63 and the RUN pad removed.
  - BOOT/QSPI_SS (pin 63) open: RP2040 DS Table 616 "QSPI_CSn ... Reset State Pull-Up"; SW1, R24
    and BOOT pad removed. BOOTSEL only via SWD / firmware (reset_usb_boot).
  - USB_OC_N removed: GPIO18 (pin 40) NC.
  - J3 (TC2050) replaced by DNP solder pads TP1 SWCLK, TP2 SWDIO, TP3 GND, TP4 +3V3 (D1.5 mm).
"""
import os
os.environ.setdefault('KICAD10_SYMBOL_DIR', r'C:\Program Files\KiCad\10.0\share\kicad\symbols')
os.environ.setdefault('KICAD_SYMBOL_DIR',    r'C:\Program Files\KiCad\10.0\share\kicad\symbols')
from skidl import *
PROJECT_LIBS = r'C:\Users\simon\Documents\Projects\Test\PoeToUSB\libs'
if PROJECT_LIBS not in lib_search_paths[KICAD]:
    lib_search_paths[KICAD].append(PROJECT_LIBS)


@SubCircuit
def mcu_w55rp20(v3v3, v3v3a, gnd, eth_txp, eth_txn, eth_rxp, eth_rxn,
                usb_dp_mcu, usb_dm_mcu, usb_en, vbus_sense, led_din, eth_led_link_n, eth_led_act_n):
    """W55RP20 SiP (RP2040 + W5500 + QSPI flash) with all support circuitry.

    Args:
        v3v3: +3V3 digital rail (IOVDD, VREG_VIN, W5500 VDD, flash, USB_VDD, ADC)
        v3v3a: +3V3A analog rail for the W5500 PHY, generated here via FB2 from +3V3
        gnd: Ground reference
        eth_txp, eth_txn: Ethernet TX differential pair to the MagJack
        eth_rxp, eth_rxn: Ethernet RX differential pair from the MagJack
        usb_dp_mcu, usb_dm_mcu: RP2040 USB D+/D- (to series resistors in B6)
        usb_en: GPIO26 -> USB power switch enable
        vbus_sense: GPIO29/ADC3 <- VBUS divider
        led_din: GPIO28 (pin 48) -> green status LED D11 via R38 (Rev 4f, high = on)
        eth_led_link_n: W5500 LINKLED (pin 37, low = link) -> MagJack green LED cathode
        eth_led_act_n: W5500 ACTLED (pin 39, low = activity) -> MagJack yellow LED cathode
    """
    # ------------------------------------------------------------------
    # Internal nets (names per net_plan section 8 B5)
    # ------------------------------------------------------------------
    # +1V1: output of the RP2040 internal regulator (VREG_VOUT pin 56) feeding
    # DVDD pins 26/61. VREG_VOUT is power_out so it drives this net itself;
    # the POWER drive flag keeps ERC consistent for the DVDD power_in pins.
    p1v1 = Net('+1V1');            p1v1.drive = POWER
    eth_exres   = Net('ETH_EXRES')
    w5500_tocap = Net('W5500_TOCAP')
    w5500_1v2o  = Net('W5500_1V2O')
    xtal12_xin  = Net('XTAL12_XIN')
    xtal12_xout = Net('XTAL12_XOUT')
    xtal12_xo_r = Net('XTAL12_XO_R')
    xtal25_xi   = Net('XTAL25_XI')
    xtal25_xo   = Net('XTAL25_XO')
    swclk       = Net('SWCLK')
    swdio       = Net('SWDIO')
    # Rev 4d: RUN, QSPI_SS_BOOT, BOOT_SW, UART0_TX, UART0_RX removed (pins open)

    # Small helpers (keep BOM metadata uniform)
    def cap(ref, val, fp, mpn, lcsc, a, b, dnp=False):
        c = Part('Device', 'C', ref=ref, value=val, footprint=fp)
        c.fields['MPN'] = mpn; c.fields['LCSC'] = lcsc
        if dnp:
            c.fields['DNP'] = 'DNP'
        c[1] += a; c[2] += b
        return c

    def res(ref, val, mpn, lcsc, a, b):
        r = Part('Device', 'R', ref=ref, value=val, footprint='Resistor_SMD:R_0402_1005Metric')
        r.fields['MPN'] = mpn; r.fields['LCSC'] = lcsc
        r[1] += a; r[2] += b
        return r

    C0402 = 'Capacitor_SMD:C_0402_1005Metric'
    C0603 = 'Capacitor_SMD:C_0603_1608Metric'

    # ------------------------------------------------------------------
    # U5 — W55RP20 (project symbol; pins addressed by package pin number)
    # ------------------------------------------------------------------
    u5 = Part('poe_usb_hid_bridge', 'W55RP20', ref='U5', value='W55RP20',
              footprint='poe_usb_hid_bridge:W55RP20_QFN-68-1EP_8x8mm_P0.4mm_EP6.2x6.2mm')
    u5.fields['MPN'] = 'W55RP20'; u5.fields['LCSC'] = 'C43229502'

    # +3V3 digital: IOVDD 13/25/43/53/60/64, W5500 VDD 42, ADC_AVDD 54,
    # VREG_VIN 55, USB_VDD 59, VDD_FLASH 62
    for n in (13, 25, 42, 43, 53, 54, 55, 59, 60, 62, 64):
        u5[n] += v3v3
    # +3V3A analog (via FB2): AVDD 3/6/8/31/34
    for n in (3, 6, 8, 31, 34):
        u5[n] += v3v3a
    # +1V1 core: VREG_VOUT 56 -> DVDD 26/61
    for n in (56, 26, 61):
        u5[n] += p1v1
    # Ground: TESTEN 22 tied low (test mode disabled), EP 69
    u5[22] += gnd
    u5[69] += gnd

    # Ethernet PHY pairs
    u5[1] += eth_txn
    u5[2] += eth_txp
    u5[4] += eth_rxn
    u5[5] += eth_rxp
    u5[7] += eth_exres          # EXRES1 (12.4k 1 % to GND)
    u5[33] += w5500_tocap       # TOCAP 4.7uF
    u5[35] += w5500_1v2o        # 1V2O 10nF
    u5[37] += eth_led_link_n    # LINKLED (low = link) -> MagJack green LED (Rev 4g)
    u5[39] += eth_led_act_n     # ACTLED (low = activity) -> MagJack yellow LED (Rev 4g)

    # Crystals
    u5[23] += xtal12_xin        # RP2040 XIN
    u5[24] += xtal12_xout       # RP2040 XOUT (via R37 to Y1)
    u5[44] += xtal25_xi         # W5500 XI
    u5[45] += xtal25_xo         # W5500 XO

    # Debug (SWD only, Rev 4d)
    u5[27] += swclk
    u5[28] += swdio

    # Application GPIO
    u5[46] += usb_en            # GPIO26/ADC0
    u5[48] += led_din           # GPIO28/ADC2 -> green status LED (Rev 4f)
    u5[49] += vbus_sense        # GPIO29/ADC3
    u5[57] += usb_dm_mcu
    u5[58] += usb_dp_mcu

    # Intentionally unused pins
    # 9-12 GPIO4-7, 14-21 GPIO8-15, 30 GPIO16, 32 VBG, 36 SPDLED, 38 DUPLED,
    # 50/51/52 PMODE2/1/0 (internal pull-ups select default mode), 67/68 GPIO2/3,
    # Rev 4b: 41 GPIO19, 47 GPIO27 (37 LINKLED / 39 ACTLED used again since Rev 4g)
    # Rev 4d: 29 RUN (internal pull-up), 40 GPIO18, 63 BOOT/QSPI_SS (internal pull-up),
    #         65/66 GPIO0/1 (UART0, reserve)
    for n in (9, 10, 11, 12, 14, 15, 16, 17, 18, 19, 20, 21,
              29, 30, 32, 36, 38, 40, 41, 47, 50, 51, 52, 63, 65, 66, 67, 68):
        u5[n] += NC

    # ------------------------------------------------------------------
    # +3V3A ferrite bead (digital -> analog PHY supply)
    # ------------------------------------------------------------------
    fb2 = Part('Device', 'FerriteBead', ref='FB2', value='120R@100MHz',
               footprint='Inductor_SMD:L_0603_1608Metric')
    fb2.fields['MPN'] = 'BLM18PG121SN1D'; fb2.fields['LCSC'] = 'C14709'
    fb2[1] += v3v3
    fb2[2] += v3v3a

    # ------------------------------------------------------------------
    # Decoupling (net_plan B5 table)
    # ------------------------------------------------------------------
    M104 = 'CL05B104KO5NNNC'
    # IOVDD pins 13/25/43/53/60/64
    for ref in ('C40', 'C41', 'C42', 'C43', 'C44', 'C45'):
        cap(ref, '100nF', C0402, M104, 'C1525', v3v3, gnd)
    cap('C46', '10uF', C0603, 'CL10A106KP8NNNC', 'C19702', v3v3, gnd)   # +3V3 bulk
    cap('C47', '1uF',  C0402, 'CL05A105KA5NQNC', 'C52923', v3v3, gnd)   # VREG_VIN (55)
    cap('C48', '1uF',  C0402, 'CL05A105KA5NQNC', 'C52923', p1v1, gnd)   # VREG_VOUT (56)
    cap('C49', '100nF', C0402, M104, 'C1525', p1v1, gnd)                # DVDD 26
    cap('C50', '100nF', C0402, M104, 'C1525', p1v1, gnd)                # DVDD 61
    for ref in ('C51', 'C52', 'C53', 'C54'):                            # 59/54/62/42
        cap(ref, '100nF', C0402, M104, 'C1525', v3v3, gnd)
    # AVDD 3/6/8/31/34 on +3V3A
    for ref in ('C55', 'C56', 'C57', 'C58', 'C59'):
        cap(ref, '100nF', C0402, M104, 'C1525', v3v3a, gnd)
    cap('C60', '10uF', C0603, 'CL10A106KP8NNNC', 'C19702', v3v3a, gnd)  # +3V3A bulk

    # W5500 internal regulator caps (layout: C61 directly at TOCAP pin 33, shortest trace, DS p.10)
    cap('C61', '4.7uF', C0603, 'CL10A475KO8NNNC', 'C19666', w5500_tocap, gnd)
    cap('C62', '10nF',  C0402, 'CL05B103KB5NNNC', 'C15195', w5500_1v2o, gnd)

    # EXRES1 bias resistor (1 % required)
    res('R22', '12.4k', '0402WGF1242TCE', 'C11692', eth_exres, gnd)

    # ------------------------------------------------------------------
    # 12 MHz crystal Y1 (RP2040) - H1 (Rev 4e review): exactly per Raspberry Pi reference
    # ("Hardware design with RP2040" / Pico): Abracon ABM8-272-T3, CL 10 pF, ESR <= 50 ohm
    # (DS drawing #456603), 2 x 15 pF C0G, 1k series R37 on XOUT. Crystal on pins 1/3, 2/4 = GND.
    # ------------------------------------------------------------------
    y1 = Part('Device', 'Crystal_GND24', ref='Y1', value='12MHz 10pF',
              footprint='Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm')
    y1.fields['MPN'] = 'Abracon ABM8-272-T3'; y1.fields['LCSC'] = 'C20625731'
    y1[1] += xtal12_xin
    y1[3] += xtal12_xo_r
    y1[2] += gnd
    y1[4] += gnd
    cap('C25', '15pF', C0402, '0402CG150J500NT', 'C1548', xtal12_xin, gnd)
    cap('C26', '15pF', C0402, '0402CG150J500NT', 'C1548', xtal12_xo_r, gnd)
    res('R37', '1k', '0402WGF1001TCE', 'C11702', xtal12_xout, xtal12_xo_r)

    # ------------------------------------------------------------------
    # 25 MHz crystal Y2 (W5500) with 27 pF loads
    # ------------------------------------------------------------------
    y2 = Part('Device', 'Crystal_GND24', ref='Y2', value='25MHz 18pF',
              footprint='Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm')
    y2.fields['MPN'] = 'X322525MRB4SI'; y2.fields['LCSC'] = 'C70593'
    y2[1] += xtal25_xi
    y2[3] += xtal25_xo
    y2[2] += gnd
    y2[4] += gnd
    cap('C27', '27pF', C0402, '0402CG270J500NT', 'C1557', xtal25_xi, gnd)
    cap('C28', '27pF', C0402, '0402CG270J500NT', 'C1557', xtal25_xo, gnd)

    # ------------------------------------------------------------------
    # Rev 4d: no RUN pull-up/cap, no BOOTSEL button (both pins have on-chip pull-ups).
    # SWD edge pad field J3 (Rev 4e, replaces the Rev-4d pads TP1-TP4; TP9 +5V lives in B2):
    # 4 SMD pads 1.5 x 3.0 mm, pitch 2.54 mm, 0.3 mm from the board edge, for a hand-soldered
    # 1x04 2.54 mm pin header laid flat (pins beyond the edge). DNP, no BOM/CPL entry.
    # Pinout 1 SWCLK, 2 GND, 3 SWDIO (= Raspberry Pi Pico SWD order), 4 +3V3.
    # ------------------------------------------------------------------
    j3 = Part('Connector_Generic', 'Conn_01x04', ref='J3', value='SWD',
              footprint='poe_usb_hid_bridge:SWD_Edge_1x04_P2.54mm_SMD')
    j3.fields['MPN'] = ''; j3.fields['LCSC'] = ''; j3.fields['DNP'] = 'DNP'
    j3.fields['Note'] = 'edge pad field for a 2.54 mm pin header, hand-soldered'
    j3[1] += swclk
    j3[2] += gnd
    j3[3] += swdio
    j3[4] += v3v3
