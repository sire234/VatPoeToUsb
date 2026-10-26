"""3.3V LDO — TLV75733P (1 A, WSON-6) generating +3V3 from +5V
Block from: architecture/block_diagram.md (B4 ldo_3v3)
Interface nets: +5V (v5), +3V3 (v3v3), GND (gnd)
"""
import os
os.environ.setdefault('KICAD10_SYMBOL_DIR', r'C:\Program Files\KiCad\10.0\share\kicad\symbols')
os.environ.setdefault('KICAD_SYMBOL_DIR',    r'C:\Program Files\KiCad\10.0\share\kicad\symbols')
from skidl import *
PROJECT_LIBS = r'C:\Users\simon\Documents\Projects\Test\PoeToUSB\libs'
if PROJECT_LIBS not in lib_search_paths[KICAD]:
    lib_search_paths[KICAD].append(PROJECT_LIBS)


@SubCircuit
def ldo_3v3(v5, v3v3, gnd):
    """B4: TLV75733PDRVR fixed 3.3 V LDO, +5V -> +3V3.

    Args:
        v5: +5V secondary rail (LDO input, also tied to EN = always on)
        v3v3: +3V3 logic rail (LDO output)
        gnd: Ground reference
    """
    # --- U4: LDO (net_plan §8 B4) ---
    # Pins: 1 OUT, 2 NC, 3 GND, 4 EN, 5 NC, 6 IN, 7 EP (GND)
    u4 = Part('Regulator_Linear', 'TLV75733PDRV', ref='U4', value='TLV75733PDRVR',
              footprint='Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm')
    u4.fields['MPN'] = 'TLV75733PDRVR'
    u4.fields['LCSC'] = 'C2868428'

    u4['IN'] += v5          # pin 6
    u4['EN'] += v5          # pin 4, tied to IN: regulator always enabled
    u4['OUT'] += v3v3       # pin 1
    u4['GND'] += gnd        # pin 3
    u4[7] += gnd            # exposed pad -> GND (thermal)
    u4[2] += NC             # NC pins (net_plan: NC)
    u4[5] += NC

    # --- C15: input capacitor 4.7 uF 16 V X5R, +5V -> GND ---
    c15 = Part('Device', 'C', ref='C15', value='4.7uF', footprint='Capacitor_SMD:C_0603_1608Metric')
    c15.fields['MPN'] = 'CL10A475KO8NNNC'
    c15.fields['LCSC'] = 'C19666'
    c15[1] += v5
    c15[2] += gnd

    # --- C16: output capacitor 10 uF 10 V X5R, +3V3 -> GND ---
    c16 = Part('Device', 'C', ref='C16', value='10uF', footprint='Capacitor_SMD:C_0603_1608Metric')
    c16.fields['MPN'] = 'CL10A106KP8NNNC'
    c16.fields['LCSC'] = 'C19702'
    c16[1] += v3v3
    c16[2] += gnd
