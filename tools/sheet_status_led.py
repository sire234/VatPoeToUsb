"""Wired layout of sheet B7 status_led (Rev 4f: plain green LED D11, C64 removed).
Usage: python tools/sheet_status_led.py <source project dir (label-only rev4e)> <target project dir>
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schgen import Sheet

KICAD_SYM = r'C:\Program Files\KiCad\10.0\share\kicad\symbols'
src_file = os.path.join(sys.argv[1], 'status_led.kicad_sch')
sheet_file = os.path.join(sys.argv[2], 'status_led.kicad_sch')

s = Sheet.load(src_file, pwr_prefix=7, project='poe_usb_hid_bridge_rev4g')
s.title['title'] = 'PoE to USB HID Bridge – B7 status_led – grüne Status-LED'
s.title.update({'date': '2026-10-26', 'rev': '4g',
                'comment 1': 'Rev 4g, generiert aus outputs/poe_usb_hid_bridge_rev4g.net (SKiDL)'})
s.title['comment 2'] = 'Bauteile im Sheet verdrahtet; Netze zu anderen Sheets über globale Labels / Power-Symbole'

# Rev 4f: WS2812B-2020 -> Device:LED (keep the symbol UUID = PCB link), C64 removed
s.add_lib_symbol(os.path.join(KICAD_SYM, 'Device.kicad_sym'), 'LED', 'Device')
s.drop_comp('C64')
d11 = s.comps['D11']
d11.lib_id = 'Device:LED'
d11.set_prop('Value', 'green', hidden=False)
d11.set_prop('Footprint', 'LED_SMD:LED_0603_1608Metric')
d11.set_prop('Description', 'Light emitting diode')
d11.set_prop('MPN', 'MEIHUA MHT193CGCT')
d11.set_prop('LCSC', 'C2962098')
d11.pin_uuids = {'1': d11.pin_uuids['1'], '2': d11.pin_uuids['2']}

s.frame(15.24, 15.24, 200.66, 99.06)
s.text('B7 status_led – grüne Status-LED an GPIO28', 20.32, 22.86, size=3.0, bold=True)
s.text('GPIO28 (LED_DIN) → R38 330 Ω → D11 grün (MEIHUA MHT193CGCT, 569 nm, Vf ≈ 2,2 V) → GND', 20.32, 30.48)
s.text('High = LED an, I_F ≈ (3,3 V − 2,1 V) / 330 Ω ≈ 3,5 mA', 20.32, 35.56)

# GPIO28 -> R38 -> D11 anode, cathode -> GND (current flows top to bottom)
s.place('R38', 76.2, 54.61, 90)                 # horizontal, pin 1 left
s.place('D11', 99.06, 64.77, 90, ref_at=(5.08, -1.27), val_at=(5.08, 1.27))  # anode on top
s.glabel('LED_DIN', s.wire(s.pin('R38', '1'), (62.23, 54.61)), angle=180)
corner = s.wire(s.pin('R38', '2'), (99.06, 54.61))
s.wire(corner, s.pin('D11', 'A'))
s.glabel('LED_DIN_R', corner, angle=0)          # keeps the board net name
s.power('GND', s.pin('D11', 'K'), down=5.08)

s.save(sheet_file)
print('ok', sheet_file)
