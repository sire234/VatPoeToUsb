"""Wired layout of sheet B4 ldo_3v3 (TLV75733P, C15 input, C16 output).
Usage: python tools/sheet_ldo_3v3.py <source project dir (label-only rev4e)> <target project dir>
"""
from sheet_common import open_sheet, finish

s, dst = open_sheet('ldo_3v3', 4, 'B4 ldo_3v3 – 3,3-V-LDO TLV75733P',
                    ['+5V → U4 → +3V3 (1 A); EN fest an +5V; C15 4,7 µF am Eingang, C16 10 µF am Ausgang'],
                    frame_size=(170.18, 106.68))

y = 60.96                                       # +5V / +3V3 rail line
s.place('U4', 101.6, y + 2.54, 0, ref_at=(0, -10.16), val_at=(0, -7.62))
s.place('C15', 83.82, y + 7.62, 0)
s.place('C16', 121.92, y + 7.62, 0)

# input: +5V -> C15 -> IN, EN tied to IN
vin = s.power('+5V', (71.12, y))
s.wire(vin, s.pin('U4', 'IN'))
s.wire(s.pin('C15', '1'), (83.82, y))
en = s.pin('U4', 'EN')
s.wire(en, (90.17, en[1]), (90.17, y))
# output: OUT -> C16 -> +3V3
s.wire(s.pin('U4', 'OUT'), (134.62, y))
s.wire(s.pin('C16', '1'), (121.92, y))
s.power('+3V3', (134.62, y))
# grounds
for ref in ('C15', 'C16'):
    s.power('GND', s.pin(ref, '2'), down=3.81)
s.power('GND', s.pin('U4', '3'), down=3.81)
s.noconnect(s.pin('U4', '2'))
s.noconnect(s.pin('U4', '5'))

finish(s, dst)
