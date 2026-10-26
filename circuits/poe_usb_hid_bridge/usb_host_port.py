"""USB Host Port (B6) - USB-A host port with TPS2553 load switch, USBLC6 ESD, series R, VBUS sense
Block from: architecture/block_diagram.md (net_plan.md section 8, B6)
Interface nets: +5V, GND, USB_EN, USB_DP_MCU, USB_DM_MCU, VBUS_SENSE
Rev 4d (based on Rev 4b; Rev-4c bridges not used): USB_OC_N removed. TPS2553 FAULT (open-drain,
pin 4) left unconnected (allowed per TPS2553 DS: FAULT is an open-drain flag output); R27
pull-up removed, so the +3V3 port is no longer needed. Overcurrent protection itself is in U6.
"""
import os
os.environ.setdefault('KICAD10_SYMBOL_DIR', r'C:\Program Files\KiCad\10.0\share\kicad\symbols')
os.environ.setdefault('KICAD_SYMBOL_DIR',    r'C:\Program Files\KiCad\10.0\share\kicad\symbols')
from skidl import *
PROJECT_LIBS = r'C:\Users\simon\Documents\Projects\Test\PoeToUSB\libs'
if PROJECT_LIBS not in lib_search_paths[KICAD]:
    lib_search_paths[KICAD].append(PROJECT_LIBS)


def _fields(part, mpn, lcsc, dnp=False):
    """Attach sourcing fields (MPN / LCSC / DNP) to a part."""
    part.fields['MPN'] = mpn
    part.fields['LCSC'] = lcsc
    if dnp:
        part.fields['DNP'] = 'DNP'


@SubCircuit
def usb_host_port(v5, gnd, usb_en, usb_dp_mcu, usb_dm_mcu, vbus_sense):
    """USB-A host port: TPS2553 current-limited load switch, ESD, series resistors, VBUS sense.

    Args:
        v5: +5V supply (U6 IN)
        gnd: Ground reference
        usb_en: Load-switch enable from MCU (active high, 100k pull-down keeps it off at boot)
        usb_dp_mcu: D+ from the MCU USB PHY (before 27R series resistor)
        usb_dm_mcu: D- from the MCU USB PHY (before 27R series resistor)
        vbus_sense: Divided VBUS (100k/68k + 100nF) to MCU ADC
    """
    # ---- Internal nets (names per net_plan B6) ----
    vbus_usb = Net('VBUS_USB')      # driven by U6 OUT (power_out)
    ilim_set = Net('ILIM_SET')
    usb_dp = Net('USB_DP')          # connector side of the 27R series resistor
    usb_dm = Net('USB_DM')
    usb_shield = Net('USB_SHIELD')

    # ---- U6: TPS2553 load switch. R25 44.2k on ILIM sets the current limit ----
    u6 = Part('poe_usb_hid_bridge', 'TPS2553', ref='U6', value='TPS2553DBVR',
              footprint='Package_TO_SOT_SMD:SOT-23-6')
    _fields(u6, 'TPS2553DBVR', 'C55266')
    u6[1] += v5            # IN
    u6[2] += gnd           # GND
    u6[3] += usb_en        # EN
    u6[4] += NC            # FAULT (open drain) unused since Rev 4d
    u6[5] += ilim_set      # ILIM
    u6[6] += vbus_usb      # OUT

    r25 = Part('Device', 'R', ref='R25', value='44.2k', footprint='Resistor_SMD:R_0402_1005Metric')
    _fields(r25, '0402WGF4422TCE', 'C25895')
    r25[1] += ilim_set
    r25[2] += gnd

    r26 = Part('Device', 'R', ref='R26', value='100k', footprint='Resistor_SMD:R_0402_1005Metric')
    _fields(r26, '0402WGF1003TCE', 'C25741')
    r26[1] += usb_en       # keeps switch off while MCU pin is high-Z
    r26[2] += gnd

    # Input capacitor
    c17 = Part('Device', 'C', ref='C17', value='1uF 50V', footprint='Capacitor_SMD:C_0603_1608Metric')
    _fields(c17, 'CL10A105KB8NNNC', 'C15849')
    c17[1] += v5
    c17[2] += gnd

    # ---- VBUS output capacitors ----
    c18 = Part('Device', 'C_Polarized', ref='C18', value='150uF 6.3V',
               footprint='Capacitor_Tantalum_SMD:CP_EIA-3528-21_Kemet-B')
    _fields(c18, 'T520B157M006ATE035', 'C212682')
    c18[1] += vbus_usb     # pin 1 = +
    c18[2] += gnd

    c19 = Part('Device', 'C', ref='C19', value='10uF 10V', footprint='Capacitor_SMD:C_0603_1608Metric')
    _fields(c19, 'CL10A106KP8NNNC', 'C19702')
    c19[1] += vbus_usb
    c19[2] += gnd

    c20 = Part('Device', 'C', ref='C20', value='100nF', footprint='Capacitor_SMD:C_0402_1005Metric')
    _fields(c20, 'CL05B104KO5NNNC', 'C1525')
    c20[1] += vbus_usb
    c20[2] += gnd

    # ---- U7: USBLC6-2SC6 ESD protection on D+/D-/VBUS (SOT-23-6 footprint override) ----
    u7 = Part('Power_Protection', 'USBLC6-2SC6', ref='U7', value='USBLC6-2SC6',
              footprint='Package_TO_SOT_SMD:SOT-23-6')
    _fields(u7, 'USBLC6-2SC6', 'C7519')
    u7[1] += usb_dp
    u7[6] += usb_dp
    u7[2] += gnd
    u7[3] += usb_dm
    u7[4] += usb_dm
    u7[5] += vbus_usb

    # ---- 27R series resistors (MCU side -> connector side) ----
    r28 = Part('Device', 'R', ref='R28', value='27', footprint='Resistor_SMD:R_0402_1005Metric')
    _fields(r28, '0402WGF270JTCE', 'C25100')
    r28[1] += usb_dp_mcu
    r28[2] += usb_dp

    r29 = Part('Device', 'R', ref='R29', value='27', footprint='Resistor_SMD:R_0402_1005Metric')
    _fields(r29, '0402WGF270JTCE', 'C25100')
    r29[1] += usb_dm_mcu
    r29[2] += usb_dm

    # ---- 15k host pull-downs, DNP (in netlist, not assembled) ----
    r30 = Part('Device', 'R', ref='R30', value='15k', footprint='Resistor_SMD:R_0402_1005Metric')
    _fields(r30, '0402WGF1502TCE', 'C25756', dnp=True)
    r30[1] += usb_dp
    r30[2] += gnd

    r31 = Part('Device', 'R', ref='R31', value='15k', footprint='Resistor_SMD:R_0402_1005Metric')
    _fields(r31, '0402WGF1502TCE', 'C25756', dnp=True)
    r31[1] += usb_dm
    r31[2] += gnd

    # ---- VBUS sense divider 100k/68k + 100nF filter ----
    r32 = Part('Device', 'R', ref='R32', value='100k', footprint='Resistor_SMD:R_0402_1005Metric')
    _fields(r32, '0402WGF1003TCE', 'C25741')
    r32[1] += vbus_usb
    r32[2] += vbus_sense

    r33 = Part('Device', 'R', ref='R33', value='68k', footprint='Resistor_SMD:R_0402_1005Metric')
    _fields(r33, '0402WGF6802TCE', 'C36871')
    r33[1] += vbus_sense
    r33[2] += gnd

    c29 = Part('Device', 'C', ref='C29', value='100nF', footprint='Capacitor_SMD:C_0402_1005Metric')
    _fields(c29, 'CL05B104KO5NNNC', 'C1525')
    c29[1] += vbus_sense
    c29[2] += gnd

    # ---- J2: USB-A receptacle ----
    j2 = Part('Connector', 'USB_A', ref='J2', value='BX-TYPE-A-MWT4P',
              footprint='poe_usb_hid_bridge:BX-TYPE-A-MWT4P')
    _fields(j2, 'BX-TYPE-A-MWT4P', 'C18077687')
    j2[1] += vbus_usb      # VBUS
    j2[2] += usb_dm        # D-
    j2[3] += usb_dp        # D+
    j2[4] += gnd           # GND
    j2['SH'] += usb_shield # shield (pins 5/6)

    # ---- Shield: 0R to GND, optional 4.7nF (DNP) ----
    r34 = Part('Device', 'R', ref='R34', value='0R', footprint='Resistor_SMD:R_0603_1608Metric')
    _fields(r34, '0603WAF0000T5E', 'C21189')
    r34[1] += usb_shield
    r34[2] += gnd

    c30 = Part('Device', 'C', ref='C30', value='4.7nF', footprint='Capacitor_SMD:C_0603_1608Metric')
    _fields(c30, 'CL10B472KB8NNNC', 'C1621', dnp=True)
    c30[1] += usb_shield
    c30[2] += gnd
