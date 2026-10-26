"""Shared setup for the per-sheet layout scripts (Rev 4f wired schematic)."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schgen import Sheet

PROJECT = 'poe_usb_hid_bridge_rev4g'
REV = '4g'
DATE = '2026-10-26'


def open_sheet(name, pwr_prefix, title, lines, frame_size=None):
    """Load <src>/<name>.kicad_sch (argv[1], label-only Rev 4e sheet), set title block, heading,
    description lines and frame. Returns (sheet, target path)."""
    src = os.path.join(sys.argv[1], name + '.kicad_sch')
    dst = os.path.join(sys.argv[2], name + '.kicad_sch')
    s = Sheet.load(src, pwr_prefix=pwr_prefix, project=PROJECT)
    s.title['title'] = 'PoE to USB HID Bridge – ' + title
    s.title.update({'date': DATE, 'rev': REV,
                    'comment 1': 'Rev %s, generiert aus outputs/poe_usb_hid_bridge_rev%s.net (SKiDL)' % (REV, REV),
                    'comment 2': 'Bauteile im Sheet verdrahtet; Netze zu anderen Sheets über globale Labels / Power-Symbole'})
    x2, y2 = frame_size or (404.76, 180.34)
    s.frame(15.24, 15.24, x2, y2)
    s.text(title, 20.32, 22.86, size=3.0, bold=True)
    for i, line in enumerate(lines):
        s.text(line, 20.32, 30.48 + 5.08 * i)
    return s, dst


def finish(s, dst):
    s.save(dst)
    print('ok', dst)
