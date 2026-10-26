"""Simple 3D body models for the project footprints that have none, so 3D renders show the
real parts. Boxes use the body outline (F.Fab, matches the datasheets) and the datasheet height:
  U1 Ag9905-LPB 21.21 x 13.92 x 8.00 mm, J1 HR871150C 16.0 x 21.2 x 13.3 mm,
  J2 BX-TYPE-A-MWT4P 13.8 x 15.2 x 7.0 mm (all top mount, from datasheets/*_SUMMARY.md).
U5 (W55RP20, QFN-68 8x8) gets the KiCad stock QFN-68 8x8 model (same body, pin 1 top left).
The model reference is added to the project footprint library and to the footprints in the board.
Usage: python tools/make_3d_models.py <board.kicad_pcb>
"""
import os

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schgen import parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FP_DIR = os.path.join(ROOT, 'footprints', 'poe_usb_hid_bridge.pretty')
MODEL_DIR = os.path.join(ROOT, '3dmodels', 'poe_usb_hid_bridge.3dshapes')
MODEL_VAR = '${KIPRJMOD}/../../3dmodels/poe_usb_hid_bridge.3dshapes/'

# footprint: (model file, fab box x0, y0, x1, y1 in footprint coords [mm], height mm, RGB)
BOXES = {
    'Silvertel_Ag9900LPB_SMD': ('Silvertel_Ag9905-LPB.wrl', -10.65, -7.01, 10.65, 7.01, 8.0, (0.12, 0.12, 0.14)),
    'HanRun_HR871150C': ('HanRun_HR871150C.wrl', -8.05, -10.85, 8.05, 10.45, 13.3, (0.55, 0.56, 0.58)),
    'BX-TYPE-A-MWT4P': ('BX-TYPE-A-MWT4P.wrl', -0.05, -7.65, 13.85, 7.65, 7.0, (0.60, 0.61, 0.63)),
}
STOCK = {
    'W55RP20_QFN-68-1EP_8x8mm_P0.4mm_EP6.2x6.2mm':
        '${KICAD10_3DMODEL_DIR}/Package_DFN_QFN.3dshapes/QFN-68-1EP_8x8mm_P0.4mm_EP5.2x5.2mm.step',
}


def wrl_box(x0, y0, x1, y1, h, rgb):
    """VRML 2 cuboid; KiCad: 1 VRML unit = 0.1 inch, z up, y up (footprint y points down)."""
    s = 1 / 2.54
    X0, X1, Y0, Y1, Z = x0 * s, x1 * s, -y1 * s, -y0 * s, h * s
    pts = [(X0, Y0, 0), (X1, Y0, 0), (X1, Y1, 0), (X0, Y1, 0),
           (X0, Y0, Z), (X1, Y0, Z), (X1, Y1, Z), (X0, Y1, Z)]
    faces = '0,3,2,1,-1, 4,5,6,7,-1, 0,1,5,4,-1, 1,2,6,5,-1, 2,3,7,6,-1, 3,0,4,7,-1'
    return ('#VRML V2.0 utf8\nShape {\n  appearance Appearance { material Material { diffuseColor %.3f %.3f %.3f '
            'specularColor 0.3 0.3 0.3 shininess 0.3 } }\n  geometry IndexedFaceSet {\n    solid FALSE\n'
            '    coord Coordinate { point [ %s ] }\n    coordIndex [ %s ]\n  }\n}\n'
            % (rgb + (', '.join('%.4f %.4f %.4f' % p for p in pts), faces)))


def model_block(path, indent):
    lines = ['(model "%s"' % path,
             '\t(offset', '\t\t(xyz 0 0 0)', '\t)',
             '\t(scale', '\t\t(xyz 1 1 1)', '\t)',
             '\t(rotate', '\t\t(xyz 0 0 0)', '\t)',
             ')']
    return ''.join(indent + line + '\n' for line in lines)


def add_model(text, start, end, path, indent):
    """Insert a model block before the closing paren of the footprint block [start, end)."""
    block = text[start:end]
    if '(model "%s"' % path in block:
        return text                                            # already there
    close = block.rfind(')')
    block = block[:close].rstrip() + '\n' + model_block(path, indent) + indent[:-1] + ')'
    return text[:start] + block + text[end:]


os.makedirs(MODEL_DIR, exist_ok=True)
paths = {}
for fp, (fname, x0, y0, x1, y1, h, rgb) in BOXES.items():
    with open(os.path.join(MODEL_DIR, fname), 'w', encoding='utf-8', newline='\n') as f:
        f.write(wrl_box(x0, y0, x1, y1, h, rgb))
    paths[fp] = MODEL_VAR + fname
paths.update(STOCK)

# project footprint library
for fp, path in paths.items():
    fn = os.path.join(FP_DIR, fp + '.kicad_mod')
    text = open(fn, encoding='utf-8').read()
    tree = parse(text)
    text = add_model(text, tree.start, tree.end, path, '\t')
    open(fn, 'w', encoding='utf-8', newline='\n').write(text)
    print('library', fp)

# board
board = sys.argv[1]
text = open(board, encoding='utf-8').read()
tree = parse(text)
blocks = [(n.start, n.end, str(n[1]).split(':')[-1]) for n in tree.findall('footprint')]
for start, end, name in sorted(blocks, reverse=True):          # back to front keeps offsets valid
    if name in paths:
        text = add_model(text, start, end, paths[name], '\t\t')
        print('board', name)
open(board, 'w', encoding='utf-8', newline='\n').write(text)
