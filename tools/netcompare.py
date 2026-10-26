"""Compare two KiCad netlists (.net) by connectivity: net name -> set of (ref, pin).
Usage: python tools/netcompare.py <reference.net> <check.net> [--refs R1,R2,...]
With --refs only the pins of the given references are compared (one sheet at a time)."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schgen import parse


def nets(path):
    tree = parse(open(path, encoding='utf-8').read())
    out = {}
    for n in tree.find('nets').findall('net'):
        name = str(n.find('name')[1]).split('/')[-1]
        nodes = frozenset((str(x.find('ref')[1]), str(x.find('pin')[1])) for x in n.findall('node'))
        if len(nodes) == 1 and name.startswith('unconnected-'):
            continue
        out[name] = nodes
    return out


def restrict(ns, refs):
    out = {}
    for name, nodes in ns.items():
        sub = frozenset(n for n in nodes if n[0] in refs)
        if sub:
            out[name] = sub
    return out


a, b = nets(sys.argv[1]), nets(sys.argv[2])
if '--refs' in sys.argv:
    refs = set(sys.argv[sys.argv.index('--refs') + 1].split(','))
    a, b = restrict(a, refs), restrict(b, refs)
groups_a = {v: k for k, v in a.items()}
groups_b = {v: k for k, v in b.items()}
ok = True
for g, name in groups_a.items():
    if g not in groups_b:
        ok = False; print('only in ref :', name, sorted(g))
    elif groups_b[g] != name:
        ok = False; print('name differs:', name, '->', groups_b[g])
for g, name in groups_b.items():
    if g not in groups_a:
        ok = False; print('only in check:', name, sorted(g))
print('IDENTICAL connectivity (%d nets)' % len(a) if ok else 'DIFFERENT')
sys.exit(0 if ok else 1)
