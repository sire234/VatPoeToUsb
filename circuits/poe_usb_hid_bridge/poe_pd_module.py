"""B2 poe_pd_module (Rev 4e) - PoE PD with Silvertel Ag9905-LPB SMT module (Rev 4-4d: Ag9905LP DIL), replaces Rev-3 blocks
poe_frontend (B2) + pd_flyback (B3, TPS23753A discrete flyback).

Block from: architecture/block_diagram.md (Rev 4, B2), architecture/net_plan.md section 8 "B2 (Rev 4)"
Interface nets: PSE_CT12, PSE_CT36, PSE_SP45, PSE_SP78, +5V, GND
Internal nets:  VDD_POE, VSS (PoE primary, after bridges), +5V_RAW (module output), AG_ADJ

Datasheet: Silvertel Ag9900 V3.5 (March 2026) for the LPB (datasheets/Ag9900_V3.5_2026-03_LPB.pdf);
  V2.4 (April 2020) for the external circuit.
  LPB Table 2: 1 = +VDC, 2 = -VDC, 3 = ADJ, 4 = VIN+, 5 = VIN-   (LP was 1,2 +VDC / 3 -VDC / 4 ADJ / 5,6 VIN+ / 7,8 VIN-)
  Fig. 3/7: BR1/BR2 (MB6S) to VIN+/VIN-, SMAJ58A across the module input,
            C1 >= 100 uF low-ESR + 10 uF ceramic at the output, RB >= I_load,min (200 mA)
  Fig. 19:  optional 4.7 nF/2 kV Y caps input <-> output (EMC)  -> C14 option (DNP)
"""
import os
os.environ.setdefault('KICAD10_SYMBOL_DIR', r'C:\Program Files\KiCad\10.0\share\kicad\symbols')
os.environ.setdefault('KICAD_SYMBOL_DIR',    r'C:\Program Files\KiCad\10.0\share\kicad\symbols')
from skidl import *
PROJECT_LIBS = r'C:\Users\simon\Documents\Projects\Test\PoeToUSB\libs'
if PROJECT_LIBS not in lib_search_paths[KICAD]:
    lib_search_paths[KICAD].append(PROJECT_LIBS)


def _mk(lib, sym, ref, value, fp, mpn='', lcsc='', dnp=False):
    """Create a part with the mandatory fields (MPN, LCSC, optional DNP)."""
    p = Part(lib, sym, ref=ref, value=value, footprint=fp)
    p.fields['MPN'] = mpn
    p.fields['LCSC'] = lcsc
    if dnp:
        p.fields['DNP'] = 'DNP'
    return p


@SubCircuit
def poe_pd_module(pse_ct12, pse_ct36, pse_sp45, pse_sp78, v5, gnd):
    """PoE PD front-end + isolated 5 V supply with the Silvertel Ag9905LP module.

    The module contains the IEEE 802.3af signature (Class 0), hotswap and the
    1500 V isolated DC/DC converter. The only primary/secondary crossing on the
    board is the module itself (plus the optional, DNP Y-cap C14 and the J1-internal
    Bob-Smith/shield path in block B1).

    Args:
        pse_ct12: Cable-side centre tap pair 1/2 (J1.7), 37-57 V, any polarity (Mode A)
        pse_ct36: Cable-side centre tap pair 3/6 (J1.8) (Mode A)
        pse_sp45: Spare pair 4/5 (J1.9) (Mode B)
        pse_sp78: Spare pair 7/8 (J1.10) (Mode B)
        v5: filtered 5 V rail after FB1 (net '+5V')
        gnd: secondary ground (GND), = module -VDC
    """
    # ---------------- internal nets ----------------
    # VDD_POE / VSS: rectified PoE rail. The bridges are passive pins, so the
    # nets are declared as POWER sources for the module's power_in VIN pins.
    vdd_poe = Net('VDD_POE'); vdd_poe.drive = POWER
    vss = Net('VSS');         vss.drive = POWER
    v5_raw = Net('+5V_RAW')   # module +VDC (power_out) before FB1
    adj = Net('AG_ADJ')       # module ADJ, open (5.00 V) unless R9 is fitted

    # ---------------- PRIMARY: bridges + TVS (unchanged parts from Rev 3 B2) ----------------
    # MDD MB6S pinout: 1 = DC+, 2 = DC-, 3/4 = AC.
    d1 = _mk('poe_usb_hid_bridge', 'MB6S_MDD', 'D1', 'MB6S', 'Package_TO_SOT_SMD:TO-269AA',
             'MDD MB6S-50MIL', 'C2487')
    d1[1] += vdd_poe; d1[2] += vss; d1[3] += pse_ct12; d1[4] += pse_ct36      # Mode A
    d2 = _mk('poe_usb_hid_bridge', 'MB6S_MDD', 'D2', 'MB6S', 'Package_TO_SOT_SMD:TO-269AA',
             'MDD MB6S-50MIL', 'C2487')
    d2[1] += vdd_poe; d2[2] += vss; d2[3] += pse_sp45; d2[4] += pse_sp78      # Mode B

    # D3: SMAJ58A across the module input (DS Fig. 7). Pin 1 = K (VDD_POE), 2 = A (VSS).
    d3 = _mk('Device', 'D_Zener', 'D3', 'SMAJ58A', 'Diode_SMD:D_SMA', 'MDD SMAJ58A', 'C123816')
    d3[1] += vdd_poe; d3[2] += vss

    # C1: input HF capacitor 100 nF/100 V - DNP by default. The module already presents
    # the 802.3af signature incl. its input capacitance; an extra 100 nF could push the
    # detection capacitance above 0.12 uF. Fit only after a detection test with the PSE.
    c1 = _mk('Device', 'C', 'C1', '100nF 100V X7R', 'Capacitor_SMD:C_0805_2012Metric',
             'CL21B104KCFNNNE', 'C28233', dnp=True)
    c1[1] += vdd_poe; c1[2] += vss

    # ---------------- U1: Silvertel Ag9905-LPB (Rev 4e, low-profile SMT, 5 pads) ----------------
    # Rev 4e: Ag9905LP (DIL) not available -> Ag9905-LPB. Pinout DIFFERS from the LP
    # (Ag9900 DS V3.5 Table 2): 1 +VDC, 2 -VDC, 3 ADJ, 4 VIN+, 5 VIN-.
    # Reflow land pattern DS Fig. 21 incl. isolation keep-out; top side only (DS p.16), MSL1.
    u1 = _mk('poe_usb_hid_bridge', 'Ag9905-LPB', 'U1', 'Ag9905-LPB',
             'poe_usb_hid_bridge:Silvertel_Ag9900LPB_SMD', 'Ag9905-LPB', '', dnp=True)
    u1.fields['Consigned'] = 'Silvertel Ag9905-LPB via distributor; JLC consigned SMT placement or hand reflow'
    u1.fields['Height'] = '8.0 mm (max 9.2)'
    u1[4] += vdd_poe                        # VIN+
    u1[5] += vss                            # VIN-
    u1[1] += v5_raw                         # +VDC
    u1[2] += gnd                            # -VDC = secondary GND
    u1[3] += adj                            # ADJ (open = 5.00 V)

    # R9: ADJ trim option, DNP. ADJ -> -VDC raises Vout (0 R = 5.65 V), ADJ -> +VDC lowers it
    # (DS Table 3). Footprint placed to GND (raise) to compensate USB-path drop if needed.
    r9 = _mk('Device', 'R', 'R9', 'DNP (ADJ trim)', 'Resistor_SMD:R_0603_1608Metric',
             '', '', dnp=True)
    r9[1] += adj; r9[2] += gnd

    # ---------------- SECONDARY: output capacitors, bleed, post filter ----------------
    # C11: >= 100 uF low-ESR at the module output pins (DS Sec. 2.1, mandatory for stability).
    # AISHI SA11AM101A19R15XXX: 100 uF/10 V polymer, ESR 15 mOhm, 7343, h ~1.9 mm (top or bottom).
    c11 = _mk('Device', 'C_Polarized', 'C11', '100uF 10V polymer 15mR',
              'Capacitor_Tantalum_SMD:CP_EIA-7343-31_Kemet-D', 'SA11AM101A19R15XXX', 'C135491')
    c11[1] += v5_raw; c11[2] += gnd
    # C12: ceramic next to C11 (DS Fig. 3 "C2 = 10 uF 25 V"); 22 uF/25 V Basic part reused.
    c12 = _mk('Device', 'C', 'C12', '22uF 25V X5R', 'Capacitor_SMD:C_0805_2012Metric',
              'CL21A226MAQNNNE', 'C45783')
    c12[1] += v5_raw; c12[2] += gnd
    c10 = _mk('Device', 'C', 'C10', '100nF', 'Capacitor_SMD:C_0402_1005Metric',
              'CL05B104KO5NNNC', 'C1525')
    c10[1] += v5_raw; c10[2] += gnd
    # R8: minimum-load bleeder RB (DS Fig. 3, I_load,min 200 mA) - DNP. The board draws
    # ~180 mA idle; fit only if audible noise / MPS problems are seen (100 R = 50 mA, 0.25 W).
    r8 = _mk('Device', 'R', 'R8', '100R 1206', 'Resistor_SMD:R_1206_3216Metric',
             '1206W4F1000T5E', 'C17901', dnp=True)
    r8[1] += v5_raw; r8[2] += gnd

    fb1 = _mk('Device', 'FerriteBead', 'FB1', '600R 3A', 'Inductor_SMD:L_1206_3216Metric',
              'HCB3216KF-601T30', 'C357023')
    fb1[1] += v5_raw; fb1[2] += v5
    c13 = _mk('Device', 'C', 'C13', '22uF 25V', 'Capacitor_SMD:C_0805_2012Metric',
              'CL21A226MAQNNNE', 'C45783')
    c13[1] += v5; c13[2] += gnd
    # D12 (M1, kept): OVP clamp zener on +5V. V_Z 6.2 V (5.8-6.6) > module max 5.25 V
    # (and > 5.65 V with ADJ trimmed fully up). K = +5V, A = GND.
    d12 = _mk('Device', 'D_Zener', 'D12', 'BZT52C6V2', 'Diode_SMD:D_SOD-123',
              'BZT52C6V2', 'C271260')
    d12[1] += v5; d12[2] += gnd
    tp9 = Part('Connector', 'TestPoint', ref='TP9', value='TP_+5V',
               footprint='TestPoint:TestPoint_Pad_D1.0mm')
    tp9.fields['MPN'] = ''; tp9.fields['LCSC'] = ''
    tp9[1] += v5

    # ---------------- isolation crossing option: Y-cap VSS <-> GND (DNP) ----------------
    # DS Fig. 19 uses 2x 4.7 nF/2 kV between input and output for EMC. One Y2-rated
    # 2.2 nF position is kept as option; DNP keeps the isolation free of extra leakage.
    c14 = _mk('Device', 'C', 'C14', '2.2nF 250VAC X1/Y2', 'Capacitor_SMD:C_1812_4532Metric',
              'FK12X222K502EGQ', 'C53026446', dnp=True)
    c14[1] += vss; c14[2] += gnd
