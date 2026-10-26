"""Wired layout of sheet B5 mcu_w55rp20 (W55RP20 U5 with all decoupling, FB2, crystals Y1/Y2,
EXRES R22, TOCAP C61, 1V2O C62, SWD pads J3).
Usage: python tools/sheet_mcu_w55rp20.py <source project dir (label-only rev4e)> <target project dir>

Layout: U5 in the middle. Top pins -> +3V3 rails with C40-C47 (left) and C51-C54 (right), +1V1
rail with C48-C50. Bottom pins -> +3V3A rail with C55-C60 and FB2. Left pins: Ethernet labels,
then a fan-out (staggered verticals, no crossings) to the EXRES/TOCAP/1V2O parts, the two
crystals and the SWD pads. Right pins: application GPIO labels.
"""
from sheet_common import open_sheet, finish

s, dst = open_sheet('mcu_w55rp20', 5, 'B5 mcu_w55rp20 – W55RP20 (RP2040 + W5500)',
                    ['Entkopplung C40–C60, FB2 → +3V3A; Quarze Y1 12 MHz (CL 10 pF, 2 × 15 pF, R37 1 k wie RP2040-Referenz) / '
                     'Y2 25 MHz; EXRES R22, TOCAP C61 (direkt an Pin 33), 1V2O C62',
                     'SWD-Randpads J3 (1 SWCLK, 2 GND, 3 SWDIO, 4 +3V3) für Stiftleiste 2,54 mm (DNP). '
                     'RUN, BOOT/QSPI_SS, GPIO0/1, GPIO18 offen'],
                    frame_size=(330.2, 274.32))

UX, UY = 203.2, 127.0
s.place('U5', UX, UY, 0, ref_at=(0, -5.08), val_at=(0, -2.54))
P = lambda n: s.pin('U5', str(n))


def cap_down(ref, x, y_top, **kw):
    """Vertical part with pin 1 at (x, y_top), pin 2 to GND below."""
    s.place(ref, x, y_top + 3.81, 0, **kw)
    s.power('GND', s.pin(ref, '2'), down=2.54)


# ---------------- top pins: +3V3 (left group, right group) and +1V1 ----------------
RAIL3, RAIL11 = 73.66, 60.96
left3 = [13, 25, 43, 53, 60, 64]            # IOVDD
right3 = [54, 59]                            # ADC_AVDD, USB_VDD
for n in left3 + right3:
    s.wire(P(n), (P(n)[0], RAIL3))
s.wire((101.6, RAIL3), (P(64)[0], RAIL3))
s.power('+3V3', (101.6, RAIL3))
for ref, x in zip(['C40', 'C41', 'C42', 'C43', 'C44', 'C45', 'C46', 'C47'],
                  [180.34, 170.18, 160.02, 149.86, 139.7, 129.54, 119.38, 109.22]):
    cap_down(ref, x, RAIL3)
s.wire((P(54)[0], RAIL3), (266.7, RAIL3))
s.power('+3V3', (266.7, RAIL3))
for ref, x in zip(['C51', 'C52', 'C53', 'C54'], [223.52, 233.68, 243.84, 254.0]):
    cap_down(ref, x, RAIL3)

for n in (26, 61):                           # DVDD
    s.wire(P(n), (P(n)[0], RAIL11))
s.wire((P(26)[0], RAIL11), (309.88, RAIL11))
s.glabel('+1V1', (309.88, RAIL11), angle=0)
for ref, x in zip(['C48', 'C49', 'C50'], [279.4, 289.56, 299.72]):
    cap_down(ref, x, RAIL11)

# ---------------- bottom pins ----------------
RAILA = 248.92
for n in (3, 6, 8, 31, 34):                  # AVDD -> +3V3A
    s.wire(P(n), (P(n)[0], RAILA))
s.wire((P(34)[0], RAILA), (59.69, RAILA))
for ref, x in zip(['C55', 'C56', 'C57', 'C58', 'C59', 'C60'],
                  [180.34, 170.18, 160.02, 149.86, 139.7, 129.54]):
    cap_down(ref, x, RAILA)
s.place('FB2', 55.88, RAILA, 90, ref_at=(0, -3.81), val_at=(0, 3.81))
s.power('+3V3', s.pin('FB2', '1'), left=2.54)
s.wire((66.04, RAILA), (66.04, RAILA - 5.08))
s.glabel('+3V3A', (66.04, RAILA - 5.08), angle=90)

for n in (42, 62, 55):                       # VDD, VDD_FLASH, VREG_VIN -> +3V3
    s.wire(P(n), (P(n)[0], 170.18))
s.wire((P(42)[0], 170.18), (P(55)[0], 170.18))
s.power('+3V3', (P(62)[0], 170.18), down=2.54)
s.wire(P(56), (P(56)[0], 172.72))            # VREG_VOUT -> +1V1
s.glabel('+1V1', (P(56)[0], 172.72), angle=270)
s.power('GND', P(69), down=2.54)

# ---------------- left pins ----------------
XP = P(1)[0]                                 # left pin column
for n, net in ((1, 'ETH_TXN'), (2, 'ETH_TXP'), (4, 'ETH_RXN'), (5, 'ETH_RXP'),
               (37, 'ETH_LED_LINK_N'), (39, 'ETH_LED_ACT_N')):
    s.wire(P(n), (175.26, P(n)[1]))
    s.glabel(net, (175.26, P(n)[1]), angle=180)

# EXRES: straight row
ex = P(7)
s.wire(ex, (137.16, ex[1]))
s.glabel('ETH_EXRES', (137.16, ex[1]), angle=180)
s.place('R22', 147.32, ex[1] + 3.81, 0)
s.power('GND', s.pin('R22', '2'), down=2.54)


# fan-out rows (pin -> jog column -> target row); lower rows jog closer to the IC
rows = [(33, 120.65), (35, 135.89), (44, 151.13), (45, 158.75),
        (23, 186.69), (24, 194.31), (22, 207.01), (27, 220.98), (28, 226.06)]
jog = {}
for i, (n, ty) in enumerate(rows):
    x = XP - 2.54 * (len(rows) - i)
    jog[n] = x
    s.wire(P(n), (x, P(n)[1]), (x, ty))

# TOCAP / 1V2O
for n, ref, net, ty in ((33, 'C61', 'W5500_TOCAP', 120.65), (35, 'C62', 'W5500_1V2O', 135.89)):
    s.wire((jog[n], ty), (137.16, ty))
    s.glabel(net, (137.16, ty), angle=180)
    cap_down(ref, 147.32, ty)


def crystal(y_ref, c_in, c_out, net_in, net_out, row_in, row_out, cin_y, out_from):
    """Crystal block: vertical crystal (pin 1 top) at x 137.16, input row continues left to the
    input load cap and label, output row arrives from the right with load cap and label stub."""
    xc = 137.16
    s.place(y_ref, xc, cin_y + 3.81, 270, ref_at=(12.7, -1.27), val_at=(12.7, 1.27))
    s.wire(row_in, s.pin(y_ref, '1'))
    s.wire(s.pin(y_ref, '1'), (116.84, cin_y))
    s.glabel(net_in, (116.84, cin_y), angle=180)
    s.place(c_in, 127.0, cin_y + 3.81, 0, ref_at=(-5.08, -1.27), val_at=(-5.08, 1.27))
    s.power('GND', s.pin(c_in, '2'), down=2.54)
    g = s.pin(y_ref, '2')
    s.power('GND', g, down=2.54)
    s.wire(out_from, s.pin(y_ref, '3'))
    cap_down(c_out, 147.32, cin_y + 7.62, ref_at=(-5.08, -1.27), val_at=(-5.08, 1.27))
    s.wire((152.4, cin_y + 7.62), (152.4, cin_y + 10.16))
    s.glabel(net_out, (152.4, cin_y + 10.16), angle=270)


# Y2 25 MHz (W5500): XI pin 44, XO pin 45
crystal('Y2', 'C27', 'C28', 'XTAL25_XI', 'XTAL25_XO',
        (jog[44], 151.13), None, 151.13, (jog[45], 158.75))
# Y1 12 MHz (RP2040): XIN pin 23, XOUT pin 24 via R37
s.place('R37', 160.02, 194.31, 270, ref_at=(0, -3.81), val_at=(0, 3.81))
s.wire((jog[24], 194.31), s.pin('R37', '1'))
s.wire((167.64, 194.31), (167.64, 196.85))
s.glabel('XTAL12_XOUT', (167.64, 196.85), angle=270)
crystal('Y1', 'C25', 'C26', 'XTAL12_XIN', 'XTAL12_XO_R',
        (jog[23], 186.69), None, 186.69, s.pin('R37', '2'))

# SWD pads J3 (mirrored: pins on the right)
s.place('J3', 165.1, 223.52, 0, mirror='y', ref_at=(-2.54, -7.62), val_at=(-2.54, 10.16))
s.wire((jog[27], 220.98), s.pin('J3', '1'))
s.wire((jog[28], 226.06), s.pin('J3', '3'))
s.power('GND', s.pin('J3', '2'), right=2.54)
s.power('+3V3', s.pin('J3', '4'), right=2.54)
s.wire((175.26, 220.98), (175.26, 218.44))
s.glabel('SWCLK', (175.26, 218.44), angle=90)
s.wire((180.34, 226.06), (180.34, 231.14))
s.glabel('SWDIO', (180.34, 231.14), angle=270)

# TESTEN tied low (test mode off)
s.wire((jog[22], 207.01), (170.18, 207.01))
s.power('GND', (170.18, 207.01), down=2.54)

# ---------------- right pins: application GPIO ----------------
for n, net in ((46, 'USB_EN'), (48, 'LED_DIN'), (49, 'VBUS_SENSE'), (57, 'USB_DM_MCU'), (58, 'USB_DP_MCU')):
    s.wire(P(n), (228.6, P(n)[1]))
    s.glabel(net, (228.6, P(n)[1]), angle=0)

# ---------------- unused pins ----------------
lib = s.libs[s.comps['U5'].lib_id]
used = set(left3 + right3 + [26, 61, 3, 6, 8, 31, 34, 42, 62, 55, 56, 69, 1, 2, 4, 5, 7, 22, 37, 39,
                             33, 35, 44, 45, 23, 24, 27, 28, 46, 48, 49, 57, 58])
for unit, num, name, x, y in lib.pins:
    if int(num) not in used:
        s.noconnect(P(num))

finish(s, dst)
