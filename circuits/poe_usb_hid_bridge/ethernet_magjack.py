"""Ethernet MagJack (B1) - HR871150C PoE RJ45 + TX/RX termination + shield RC
Block from: architecture/block_diagram.md (net_plan.md section 8, B1; Rev 4b)
Interface nets: PSE_CT12, PSE_CT36, PSE_SP45, PSE_SP78, ETH_TXP, ETH_TXN, ETH_RXP, ETH_RXN,
                +3V3A, +3V3, GND, ETH_LED_LINK_N, ETH_LED_ACT_N
Rev 4b: MagJack LEDs (J1.11-14) were no longer driven (R5/R6 removed, pins NC).
Rev 4g: MagJack LEDs driven again by the W5500 LED outputs (active low, push-pull):
green (J1.13 A / J1.14 K) = Link <- U5.37 LINKLED, yellow (J1.11 A / J1.12 K) = Activity
<- U5.39 ACTLED. Anodes via R5/R6 330 R to +3V3 (datasheets/HR871150C_SUMMARY.md:
Vf 1.8-2.8 V @ 20 mA -> (3.3 - 2.0) / 330 = ~4 mA). The LEDs are isolated two-terminal
diodes inside the jack, on the secondary (PHY) side.
"""
import os
os.environ.setdefault('KICAD10_SYMBOL_DIR', r'C:\Program Files\KiCad\10.0\share\kicad\symbols')
os.environ.setdefault('KICAD_SYMBOL_DIR',    r'C:\Program Files\KiCad\10.0\share\kicad\symbols')
from skidl import *
PROJECT_LIBS = r'C:\Users\simon\Documents\Projects\Test\PoeToUSB\libs'
if PROJECT_LIBS not in lib_search_paths[KICAD]:
    lib_search_paths[KICAD].append(PROJECT_LIBS)


# K1 (Rev 4e review): 6.8 nF X7R 0402 >= 50 V, RX DC-blocking caps (sourcing see sourced_bom.md)
CAP_6N8_MPN = 'YAGEO CC0402KRX7R9BB682'   # 6.8 nF 50 V X7R 10 %, JLC Extended (no Basic 6.8 nF)
CAP_6N8_LCSC = 'C93654'


@SubCircuit
def ethernet_magjack(pse_ct12, pse_ct36, pse_sp45, pse_sp78, eth_txp, eth_txn, eth_rxp, eth_rxn,
                     v3v3a, v3v3, gnd, eth_led_link_n, eth_led_act_n):
    """RJ45 MagJack with PoE center taps, Ethernet termination, shield RC and link/activity LEDs.

    Args:
        pse_ct12: PoE Mode-A center tap pair 1/2 (J1.7) to B2 bridge
        pse_ct36: PoE Mode-A center tap pair 3/6 (J1.8) to B2 bridge
        pse_sp45: PoE Mode-B spare pair 4/5 (J1.9) to B2 bridge
        pse_sp78: PoE Mode-B spare pair 7/8 (J1.10) to B2 bridge
        eth_txp: PHY TX+ (J1.1)
        eth_txn: PHY TX- (J1.2)
        eth_rxp: PHY RX+ (J1.4)
        eth_rxn: PHY RX- (J1.5)
        v3v3a: +3V3A analog supply for TX bias and the shared chip-side CT
        v3v3: +3V3 supply for the LED anodes (via R5/R6)
        gnd: Ground reference
        eth_led_link_n: green LED cathode (J1.14) <- U5 LINKLED (low = link)
        eth_led_act_n: yellow LED cathode (J1.12) <- U5 ACTLED (low = activity)
    """
    # Internal nets (names per net_plan.md)
    eth_rx_term = Net('ETH_RX_TERM')        # AC midpoint of RX termination
    shield = Net('SHIELD_RJ45')             # chassis shield of the MagJack

    # --- J1: HanRun HR871150C MagJack (project symbol, custom footprint) ---
    j1 = Part('poe_usb_hid_bridge', 'HR871150C', ref='J1', value='HR871150C',
              footprint='poe_usb_hid_bridge:HanRun_HR871150C')
    j1.fields['MPN'] = 'HanRun HR871150C'
    j1.fields['LCSC'] = 'C19724786'

    # Chip side: PHY pairs
    j1['1'] += eth_txp
    j1['2'] += eth_txn
    # RX pair via DC-blocking caps C65/C66 (K1, WIZnet W5500 ref. schematic "connected CT":
    # the RX pins must be DC-isolated from the common CT at +3V3A). J1 side = ETH_RXP_J/_RXN_J.
    eth_rxp_j = Net('ETH_RXP_J'); eth_rxn_j = Net('ETH_RXN_J')
    eth_rxp_j.do_erc = False; eth_rxn_j.do_erc = False   # passive-only nets (magnetics side)
    j1['4'] += eth_rxp_j
    j1['5'] += eth_rxn_j
    # Single shared chip-side center tap (TX+RX internally joined) -> +3V3A, decoupled by C23
    j1['3'] += v3v3a
    # Cable side: PoE center taps / spare pairs to B2 diode bridges
    j1['7'] += pse_ct12
    j1['8'] += pse_ct36
    j1['9'] += pse_sp45
    j1['10'] += pse_sp78
    # LEDs (Rev 4g): 11/12 yellow A/K = activity, 13/14 green A/K = link
    eth_led_act_a = Net('ETH_LED_ACT_A')
    eth_led_link_a = Net('ETH_LED_LINK_A')
    j1['11'] += eth_led_act_a
    j1['12'] += eth_led_act_n
    j1['13'] += eth_led_link_a
    j1['14'] += eth_led_link_n
    # Shield tabs (project symbol pin "SH")
    j1['SH'] += shield

    # --- TX bias: 49.9R from +3V3A to each TX line (close to PHY) ---
    r1 = Part('Device', 'R', ref='R1', value='49.9R', footprint='Resistor_SMD:R_0402_1005Metric')
    r2 = Part('Device', 'R', ref='R2', value='49.9R', footprint='Resistor_SMD:R_0402_1005Metric')
    for r in (r1, r2):
        r.fields['MPN'] = '0402WGF499JTCE'
        r.fields['LCSC'] = 'C25120'
    r1[1] += v3v3a
    r1[2] += eth_txp
    r2[1] += v3v3a
    r2[2] += eth_txn

    # --- RX termination: 49.9R each to ETH_RX_TERM, AC-grounded by C21 ---
    r3 = Part('Device', 'R', ref='R3', value='49.9R', footprint='Resistor_SMD:R_0402_1005Metric')
    r4 = Part('Device', 'R', ref='R4', value='49.9R', footprint='Resistor_SMD:R_0402_1005Metric')
    for r in (r3, r4):
        r.fields['MPN'] = '0402WGF499JTCE'
        r.fields['LCSC'] = 'C25120'
    r3[1] += eth_rxp
    r3[2] += eth_rx_term
    r4[1] += eth_rxn
    r4[2] += eth_rx_term

    # --- K1: RX DC-blocking caps 6.8 nF in series, J1 side <-> chip-side node (U5/R3/R4) ---
    for ref, a, b in (('C65', eth_rxp_j, eth_rxp), ('C66', eth_rxn_j, eth_rxn)):
        c = Part('Device', 'C', ref=ref, value='6.8nF 50V X7R', footprint='Capacitor_SMD:C_0402_1005Metric')
        c.fields['MPN'] = CAP_6N8_MPN
        c.fields['LCSC'] = CAP_6N8_LCSC
        c[1] += a     # J1 side
        c[2] += b     # chip side (U5 RXP/RXN, R3/R4)

    c21 = Part('Device', 'C', ref='C21', value='10nF', footprint='Capacitor_SMD:C_0402_1005Metric')
    c21.fields['MPN'] = 'CL05B103KB5NNNC'
    c21.fields['LCSC'] = 'C15195'
    c21[1] += eth_rx_term
    c21[2] += gnd

    # --- CT decoupling at J1.3 (C22 removed: only one chip-side CT) ---
    c23 = Part('Device', 'C', ref='C23', value='100nF', footprint='Capacitor_SMD:C_0402_1005Metric')
    c23.fields['MPN'] = 'CL05B104KO5NNNC'
    c23.fields['LCSC'] = 'C1525'
    c23[1] += v3v3a
    c23[2] += gnd

    # --- LED series resistors (Rev 4g): 330 R from +3V3 to the LED anodes, ~4 mA ---
    for ref, anode in (('R5', eth_led_act_a), ('R6', eth_led_link_a)):
        r = Part('Device', 'R', ref=ref, value='330R', footprint='Resistor_SMD:R_0402_1005Metric')
        r.fields['MPN'] = '0402WGF3300TCE'
        r.fields['LCSC'] = 'C25104'
        r[1] += anode
        r[2] += v3v3

    # --- Shield to GND: 1M bleed resistor + 4.7nF/2kV cap in parallel ---
    r7 = Part('Device', 'R', ref='R7', value='1M', footprint='Resistor_SMD:R_0603_1608Metric')
    r7.fields['MPN'] = '0603WAF1004T5E'
    r7.fields['LCSC'] = 'C22935'
    r7[1] += shield
    r7[2] += gnd

    c24 = Part('Device', 'C', ref='C24', value='4.7nF 2kV', footprint='Capacitor_SMD:C_1812_4532Metric')
    c24.fields['MPN'] = 'C1812X472K202T'
    c24.fields['LCSC'] = 'C106172'
    c24[1] += shield
    c24[2] += gnd
