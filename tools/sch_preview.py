"""Export the schematic PDF and render the page of one sheet to PNG for review.
Usage: python tools/sch_preview.py <root.kicad_sch> <sheet file name> <out.png> [clip x0,y0,x1,y1 in mm]"""
import os
import subprocess
import sys
import tempfile
import pymupdf

root, sheet, out = sys.argv[1:4]
pdf = os.path.join(tempfile.gettempdir(), 'schprev_%d.pdf' % os.getpid())
subprocess.run([r'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe', 'sch', 'export', 'pdf', '-o', pdf, root],
               check=True, capture_output=True)
doc = pymupdf.open(pdf)
for page in doc:
    if 'File: %s' % sheet in page.get_text():
        clip = None
        if len(sys.argv) > 4:
            x0, y0, x1, y1 = (float(v) * 72 / 25.4 for v in sys.argv[4].split(','))
            clip = pymupdf.Rect(x0, y0, x1, y1)
        page.get_pixmap(dpi=130, clip=clip).save(out)
        print('page', page.number + 1, '->', out)
        break
else:
    print('sheet not found')
doc.close()
os.remove(pdf)
