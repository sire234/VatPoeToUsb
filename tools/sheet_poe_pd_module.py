"""Wired layout of sheet B2 poe_pd_module (bridges D1/D2, TVS D3, Ag9905-LPB U1, output caps,
FB1, D12, TP9, DNP options C1/C14/R8/R9).
Usage: python tools/sheet_poe_pd_module.py <source project dir (label-only rev4e)> <target project dir>
"""
from sheet_common import open_sheet, finish

s, dst = open_sheet('poe_pd_module', 2, 'B2 poe_pd_module – PoE-PD-Modul Silvertel Ag9905-LPB',
                    ['Mode-A/B-Brücken D1/D2 (MB6S) → TVS D3 SMAJ58A → U1 Ag9905-LPB (Class 0, 1500 V isoliert)',
                     'Ausgang +5V_RAW: C11 100 µF Polymer + C12 22 µF + C10 → FB1 → +5V, D12 OVP-Zener, TP9',
                     'DNP-Optionen: C1 (Eingangs-C), R8 (Mindestlast RB), R9 (ADJ-Trimm), C14 (Y-Kap VSS↔GND)',
                     'ISOLATIONSGRENZE: PRIMÄR = PSE_*, VDD_POE, VSS (U1 Pins 4/5) | SEKUNDÄR = +5V_RAW, AG_ADJ, GND, +5V (U1 Pins 1-3)'],
                    frame_size=(396.24, 142.24))

VDD, VSS = 63.5, 116.84                      # primary rails
BY = 83.82                                   # bridge centre line

# ---------------- primary: bridges -> VDD_POE / VSS ----------------
for ref, x, ac1, ac2 in (('D1', 60.96, 'PSE_CT12', 'PSE_CT36'), ('D2', 111.76, 'PSE_SP45', 'PSE_SP78')):
    s.place(ref, x, BY, 0, ref_at=(-5.08, -10.16), val_at=(5.08, -10.16))
    a1, a2 = s.pin(ref, 'AC1'), s.pin(ref, 'AC2')
    s.wire(a1, (a1[0] - 2.54, a1[1]))
    s.glabel(ac1, (a1[0] - 2.54, a1[1]), angle=180)
    s.wire(a2, (a2[0] + 2.54, a2[1]))
    s.glabel(ac2, (a2[0] + 2.54, a2[1]), angle=0)
    s.wire(s.pin(ref, 'DC+'), (x, VDD))
    s.wire(s.pin(ref, 'DC-'), (x, VSS))

s.place('D3', 142.24, BY, 270, ref_at=(5.08, -1.27), val_at=(5.08, 1.27))      # K (VDD_POE) on top
s.place('C1', 160.02, BY, 0)
for ref, top, bot in (('D3', 'K', 'A'), ('C1', '1', '2')):
    s.wire(s.pin(ref, top), (s.pin(ref, top)[0], VDD))
    s.wire(s.pin(ref, bot), (s.pin(ref, bot)[0], VSS))

s.place('U1', 205.74, BY, 0, ref_at=(0, -10.16), val_at=(0, -7.62))
vp, vm = s.pin('U1', 'VIN+'), s.pin('U1', 'VIN-')
s.wire((45.72, VDD), (182.88, VDD), (182.88, vp[1]), vp)
s.wire((45.72, VSS), (185.42, VSS), (185.42, vm[1]), vm)
s.glabel('VDD_POE', (45.72, VDD), angle=180)
s.glabel('VSS', (45.72, VSS), angle=180)
s.flag((175.26, VDD), up=2.54)
s.flag((175.26, VSS), up=2.54)

# Y cap across the isolation barrier (DNP)
s.place('C14', 167.64, VSS + 3.81, 0)
s.power('GND', s.pin('C14', '2'), down=2.54)

# ---------------- secondary: +5V_RAW -> FB1 -> +5V ----------------
raw = s.pin('U1', '+VDC')
ry = raw[1]
s.wire(raw, (306.07, ry))
s.wire((231.14, ry), (231.14, ry - 5.08))
s.glabel('+5V_RAW', (231.14, ry - 5.08), angle=90)
for ref, x in (('C11', 243.84), ('C12', 264.16), ('C10', 279.4), ('R8', 294.64)):
    s.place(ref, x, ry + 3.81, 0)
    s.power('GND', s.pin(ref, '2'), down=2.54)

adj = s.pin('U1', 'ADJ')
s.place('R9', 226.06, adj[1] + 15.24, 0)
s.wire(adj, (226.06, adj[1]), s.pin('R9', '1'))
s.glabel('AG_ADJ', (226.06, adj[1]), angle=0)
s.power('GND', s.pin('R9', '2'), down=2.54)

vneg = s.pin('U1', '-VDC')
s.power('GND', vneg, down=7.62)
# PWR_FLAG for the secondary GND (U1 -VDC is the only source)
s.flag((250.19, 121.92))
s.power('GND', (250.19, 121.92), down=2.54)

s.place('FB1', 309.88, ry, 90, ref_at=(0, -3.81), val_at=(0, 3.81))
s.place('C13', 325.12, ry + 3.81, 0)
s.place('D12', 340.36, ry + 3.81, 270, ref_at=(5.08, -1.27), val_at=(5.08, 1.27))
s.wire(s.pin('FB1', '2'), (375.92, ry))
s.wire(s.pin('C13', '1'), (325.12, ry))
s.wire(s.pin('D12', 'K'), (340.36, ry))
s.power('GND', s.pin('C13', '2'), down=2.54)
s.power('GND', s.pin('D12', 'A'), down=2.54)
s.place('TP9', 355.6, ry, 0, ref_at=(0, -7.62), val_at=(0, -5.08))
s.power('+5V', (365.76, ry))
s.flag((375.92, ry))

finish(s, dst)
