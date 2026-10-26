"""Print the components of a sheet with their pins (number, name, lib position) and the
net of each pin from the SKiDL netlist - input for writing a sheet layout script.
Usage: python tools/sheetinfo.py <sheet.kicad_sch> <netlist.net>"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schgen import Sheet, parse

s = Sheet.load(sys.argv[1], pwr_prefix=0)
tree = parse(open(sys.argv[2], encoding='utf-8').read())
pinnet = {}
for n in tree.find('nets').findall('net'):
    name = str(n.find('name')[1])
    for x in n.findall('node'):
        pinnet[(str(x.find('ref')[1]), str(x.find('pin')[1]))] = name
for ref in sorted(s.comps, key=lambda r: (r.rstrip('0123456789'), int(''.join(c for c in r if c.isdigit()) or 0))):
    c = s.comps[ref]
    lib = s.libs[c.lib_id]
    dnp = ' DNP' if c.flags.get('dnp') == 'yes' else ''
    print('%s %s %s%s' % (ref, c.lib_id, c.prop('Value'), dnp))
    for u, num, name, x, y in sorted(lib.pins, key=lambda p: (p[0], p[1].zfill(3))):
        if u in (0, c.unit):
            print('   %3s %-12s (%6.2f,%6.2f) %s' % (num, name, x, y, pinnet.get((ref, num), 'NC')))
print('power symbols in lib:', [k for k in s.libs if k.startswith('power:')])
