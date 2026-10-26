"""Wired layout of sheet B6 usb_host_port (TPS2553 switch, VBUS caps + sense divider,
27 R series resistors, USBLC6 ESD, USB-A J2, shield R34/C30).
Usage: python tools/sheet_usb_host_port.py <source project dir (label-only rev4e)> <target project dir>
"""
from sheet_common import open_sheet, finish

s, dst = open_sheet('usb_host_port', 6, 'B6 usb_host_port – USB-A-Host',
                    ['TPS2553 Lastschalter (R25 44,2 k → 532–659 mA), FAULT offen; VBUS-Teiler R32/R33 → VBUS_SENSE (Faktor 0,405)',
                     'USB-Daten: 27-Ω-Serien-R R28/R29 → USBLC6 ESD → J2;  R30/R31 (15 k) und C30 DNP'],
                    frame_size=(269.24, 144.78))

# ---------------- power path: +5V -> U6 -> VBUS_USB -> J2 ----------------
s.place('U6', 101.6, 76.2, 0, ref_at=(0, -8.89), val_at=(0, -6.35))
s.place('C17', 53.34, 77.47, 0, ref_at=(-5.08, -1.27), val_at=(-5.08, 1.27))
s.place('R26', 81.28, 80.01, 0, ref_at=(-5.08, -1.27), val_at=(-5.08, 1.27))
s.place('R25', 86.36, 90.17, 0)
s.place('J2', 241.3, 80.01, 0, mirror='y', ref_at=(0, -11.43), val_at=(0, -8.89))

vin = s.power('+5V', (45.72, 73.66))
s.wire(vin, s.pin('U6', 'IN'))
s.power('GND', s.pin('C17', '2'), down=2.54)

en = s.pin('U6', 'EN')
s.wire(en, (73.66, en[1]))
s.glabel('USB_EN', (73.66, en[1]), angle=180)
s.power('GND', s.pin('R26', '2'), down=2.54)

ilim = s.pin('U6', 'ILIM')
s.wire(ilim, (86.36, ilim[1]), s.pin('R25', '1'))
s.glabel('ILIM_SET', s.pin('R25', '1'), angle=0)
s.power('GND', s.pin('R25', '2'), down=2.54)
s.power('GND', s.pin('U6', 'GND'), down=3.81)
s.noconnect(s.pin('U6', 'FAULT'))

vbus_y = s.pin('U6', 'OUT')[1]
s.wire(s.pin('U6', 'OUT'), s.pin('J2', 'VBUS'))
s.wire((116.84, vbus_y), (116.84, vbus_y - 5.08))
s.glabel('VBUS_USB', (116.84, vbus_y - 5.08), angle=90)
for ref, x in (('C18', 124.46), ('C19', 137.16), ('C20', 149.86)):
    s.place(ref, x, vbus_y + 3.81, 0)
    s.power('GND', s.pin(ref, '2'), down=2.54)

# VBUS sense divider R32/R33 with filter C29
s.place('R32', 162.56, vbus_y + 3.81, 0)
s.place('R33', 162.56, vbus_y + 11.43, 0)
s.place('C29', 175.26, vbus_y + 11.43, 0)
node = s.pin('R32', '2')
s.wire(node, s.pin('C29', '1'), (180.34, node[1]))
s.glabel('VBUS_SENSE', (180.34, node[1]), angle=0)
s.power('GND', s.pin('R33', '2'), down=2.54)
s.power('GND', s.pin('C29', '2'), down=2.54)

# ---------------- data path: MCU -> 27 R -> USBLC6 -> J2 ----------------
dp_y, dm_y = 105.41, 120.65
s.place('R28', 91.44, dp_y, 90)
s.place('R29', 91.44, dm_y, 90)
s.place('R30', 106.68, dp_y + 3.81, 0)
s.place('R31', 106.68, dm_y + 3.81, 0)
s.place('U7', 200.66, dp_y, 0, ref_at=(7.62, -6.35), val_at=(7.62, -3.81))

s.wire(s.pin('R28', '1'), (76.2, dp_y))
s.glabel('USB_DP_MCU', (76.2, dp_y), angle=180)
s.wire(s.pin('R29', '1'), (76.2, dm_y))
s.glabel('USB_DM_MCU', (76.2, dm_y), angle=180)

io1_l, io2_l = s.pin('U7', '1'), s.pin('U7', '3')
s.wire(s.pin('R28', '2'), io1_l)
s.wire(s.pin('R29', '2'), (190.5, dm_y), (190.5, io2_l[1]), io2_l)
s.wire((99.06, dp_y), (99.06, dp_y - 5.08))
s.glabel('USB_DP', (99.06, dp_y - 5.08), angle=90)
s.wire((99.06, dm_y), (99.06, dm_y + 5.08))
s.glabel('USB_DM', (99.06, dm_y + 5.08), angle=270)
s.power('GND', s.pin('R30', '2'), down=2.54)
s.power('GND', s.pin('R31', '2'), down=2.54)

vb = s.pin('U7', 'VBUS')
s.wire(vb, (vb[0], vbus_y))                      # straight up to the VBUS rail
s.power('GND', s.pin('U7', 'GND'), down=2.54)

io1_r, io2_r = s.pin('U7', '6'), s.pin('U7', '4')
jdp, jdm = s.pin('J2', 'D+'), s.pin('J2', 'D-')
s.wire(io1_r, (220.98, io1_r[1]), (220.98, jdp[1]), jdp)
s.wire(io2_r, (223.52, io2_r[1]), (223.52, jdm[1]), jdm)
# USBLC6 I/O pins 1/6 and 3/4 are separate symbol pins of the same net -> label both sides
s.wire((213.36, io1_r[1]), (213.36, io1_r[1] - 5.08))
s.glabel('USB_DP', (213.36, io1_r[1] - 5.08), angle=90)
s.wire((215.9, io2_r[1]), (215.9, io2_r[1] + 5.08))
s.glabel('USB_DM', (215.9, io2_r[1] + 5.08), angle=270)

# ---------------- connector ground and shield ----------------
s.power('GND', s.pin('J2', 'GND'), down=2.54)
sh = s.pin('J2', 'SH')
s.place('R34', sh[0], sh[1] + 8.89, 0, ref_at=(-5.08, -1.27), val_at=(-5.08, 1.27))
s.place('C30', sh[0] + 7.62, sh[1] + 8.89, 0)
tap = (sh[0], sh[1] + 2.54)
s.wire(sh, s.pin('R34', '1'))
s.wire(tap, (sh[0] + 7.62, tap[1]), s.pin('C30', '1'))
s.wire((sh[0] + 7.62, tap[1]), (sh[0] + 12.7, tap[1]))
s.glabel('USB_SHIELD', (sh[0] + 12.7, tap[1]), angle=0)
s.power('GND', s.pin('R34', '2'), down=2.54)
s.power('GND', s.pin('C30', '2'), down=2.54)

finish(s, dst)
