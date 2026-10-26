"""Wired layout of sheet B1 ethernet_magjack (HR871150C, TX/RX 49.9 R termination, RX coupling
caps C65/C66, CT decoupling, shield R7 || C24, PoE pairs to B2).
Usage: python tools/sheet_ethernet_magjack.py <source project dir (label-only rev4e)> <target project dir>
"""
from sheet_common import open_sheet, finish

s, dst = open_sheet('ethernet_magjack', 1, 'B1 ethernet_magjack – RJ45-MagJack HR871150C',
                    ['PHY-Seite (SEKUNDÄR, links): TX-Paar mit 49,9 Ω an +3V3A (R1/R2); CT an +3V3A (C23)',
                     'RX über Koppel-C C65/C66 6,8 nF (DC-Trennung, WIZnet-Referenz), Terminierung R3/R4 + C21',
                     'Kabelseite (PRIMÄR, rechts): J1.7–J1.10 → PSE_CT12/CT36/SP45/SP78 (zu B2); Schirm über R7 ∥ C24 an GND',
                     'MagJack-LEDs (Rev 4g): grün J1.13/14 = Link ← U5 LINKLED, gelb J1.11/12 = Activity ← U5 ACTLED,',
                     'aktiv low; Anoden über R5/R6 330 Ω an +3V3 (≈ 4 mA)'],
                    frame_size=(233.68, 157.48))

s.place('J1', 177.8, 88.9, 0, ref_at=(-10.16, -15.24), val_at=(-10.16, -12.7))
TXP, TXN, CT, RXP, RXN = 63.5, 71.12, 88.9, 109.22, 124.46
XL = 101.6                                   # left label column

# ---- fan-out of the PHY-side pins into widely spaced rows ----
tdp, tdm, ct = s.pin('J1', 'TD+'), s.pin('J1', 'TD-'), s.pin('J1', 'CT')
rdp, rdm = s.pin('J1', 'RD+'), s.pin('J1', 'RD-')
s.wire(tdp, (157.48, tdp[1]), (157.48, TXP), (XL, TXP))
s.wire(tdm, (154.94, tdm[1]), (154.94, TXN), (XL, TXN))
s.glabel('ETH_TXP', (XL, TXP), angle=180)
s.glabel('ETH_TXN', (XL, TXN), angle=180)

# TX termination: R1 TXP -> +3V3A (up), R2 TXN -> CT row (+3V3A)
s.place('R1', 137.16, TXP - 3.81, 0)
s.wire(s.pin('R1', '1'), (137.16, TXP - 10.16))
s.glabel('+3V3A', (137.16, TXP - 10.16), angle=90)
s.place('R2', 142.24, 77.47, 180)
s.wire((142.24, TXN), s.pin('R2', '2'))
s.wire(s.pin('R2', '1'), (142.24, CT))

# centre tap = +3V3A, decoupled by C23
s.wire(ct, (127.0, CT))
s.glabel('+3V3A', (127.0, CT), angle=180)
s.place('C23', 134.62, CT + 3.81, 0, ref_at=(-5.08, -1.27), val_at=(-5.08, 1.27))
s.power('GND', s.pin('C23', '2'), down=2.54)
s.flag((151.13, CT), up=2.54)

# RX: J1 -> coupling cap -> PHY, termination R3/R4 to ETH_RX_TERM, C21 to GND
s.wire(rdp, (154.94, rdp[1]), (154.94, RXP))
s.wire(rdm, (157.48, rdm[1]), (157.48, RXN))
s.place('C65', 144.78, RXP, 270, ref_at=(0, -3.81), val_at=(0, 3.81))
s.place('C66', 144.78, RXN, 270, ref_at=(0, -3.81), val_at=(0, 3.81))
s.wire((154.94, RXP), s.pin('C65', '1'))
s.wire((157.48, RXN), s.pin('C66', '1'))
s.wire((151.13, RXP), (151.13, RXP - 5.08))
s.glabel('ETH_RXP_J', (151.13, RXP - 5.08), angle=90)
s.wire((151.13, RXN), (151.13, RXN + 5.08))
s.glabel('ETH_RXN_J', (151.13, RXN + 5.08), angle=270)
s.wire(s.pin('C65', '2'), (XL, RXP))
s.wire(s.pin('C66', '2'), (XL, RXN))
s.glabel('ETH_RXP', (XL, RXP), angle=180)
s.glabel('ETH_RXN', (XL, RXN), angle=180)

s.place('R3', 127.0, RXP + 3.81, 0)
s.place('R4', 127.0, RXN - 3.81, 180)
term = s.pin('R3', '2')
s.place('C21', 113.03, term[1], 270, ref_at=(0, -3.81), val_at=(0, 3.81))
s.wire(term, s.pin('C21', '1'))
s.power('GND', s.pin('C21', '2'), left=2.54)
s.wire(term, (129.54, term[1]))
s.glabel('ETH_RX_TERM', (129.54, term[1]), angle=0)

# ---- cable side: PoE pairs to B2 ----
for pin, net in (('VC1+', 'PSE_CT12'), ('VC1-', 'PSE_CT36'), ('VC2+', 'PSE_SP45'), ('VC2-', 'PSE_SP78')):
    p = s.pin('J1', pin)
    s.wire(p, (205.74, p[1]))
    s.glabel(net, (205.74, p[1]), angle=0)

# ---- shield: R7 || C24 to GND ----
sh = s.pin('J1', 'SH')
s.place('R7', 190.5, 72.39, 0)
s.place('C24', 200.66, 72.39, 0)
s.wire(sh, (177.8, 68.58), (190.5, 68.58))
s.wire((190.5, 68.58), (200.66, 68.58), (210.82, 68.58))
s.glabel('SHIELD_RJ45', (210.82, 68.58), angle=0)
s.power('GND', s.pin('R7', '2'), down=2.54)
s.power('GND', s.pin('C24', '2'), down=2.54)

# ---- MagJack LEDs (Rev 4g): cathodes to U5 LINKLED/ACTLED, anodes via R5/R6 to +3V3 ----
s.add_lib_symbol(r'C:\Program Files\KiCad\10.0\share\kicad\symbols\power.kicad_sym', '+3V3', 'power')
for ref in ('R5', 'R6'):
    s.new_comp(ref, 'Device:R', '330R', 'Resistor_SMD:R_0402_1005Metric',
               [('MPN', '0402WGF3300TCE'), ('LCSC', 'C25104')])
# rows below J1, rightmost pin takes the top row (no crossings)
for pin, row, kind, net, rref in (('14', 104.14, 'K', 'ETH_LED_LINK_N', None),
                                  ('13', 114.3, 'A', 'ETH_LED_LINK_A', 'R6'),
                                  ('12', 124.46, 'K', 'ETH_LED_ACT_N', None),
                                  ('11', 134.62, 'A', 'ETH_LED_ACT_A', 'R5')):
    p = s.pin('J1', pin)
    if kind == 'K':
        s.wire(p, (p[0], row), (185.42, row))
        s.glabel(net, (185.42, row), angle=0)
    else:
        s.place(rref, 205.74, row - 3.81, 180)         # pin 1 (anode) on the row, pin 2 up to +3V3
        s.wire(p, (p[0], row), (215.9, row))
        s.glabel(net, (215.9, row), angle=0)
        s.power('+3V3', s.pin(rref, '2'), up=0)

finish(s, dst)
