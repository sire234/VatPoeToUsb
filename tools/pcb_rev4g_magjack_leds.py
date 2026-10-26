"""Rev 4g board change: MagJack LEDs driven again (J1.11-14, R5/R6, U5 LINKLED/ACTLED).
Usage: <KiCad python> tools/pcb_rev4g_magjack_leds.py <board.kicad_pcb>   (modified in place)

- nets: J1.11 ETH_LED_ACT_A, J1.12 ETH_LED_ACT_N, J1.13 ETH_LED_LINK_A, J1.14 ETH_LED_LINK_N,
        U5.37 ETH_LED_LINK_N, U5.39 ETH_LED_ACT_N
- R5/R6 (0402, bottom side - the top side is under the RJ45 body) left of the LED anode pads,
  +3V3 side via to the In4 +3V3 plane
- cathodes: F.Cu stub from U5.37/U5.39 to a via, then routed on In3 (empty left of x 145,
  crosses the +5V plane only near U5) to the THT pads J1.14 / J1.12 by tools/pcb_grid_router.py
"""
import os
import sys
import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pcb_grid_router import GridRouter, simplify

MM, mm = pcbnew.FromMM, pcbnew.ToMM
SHEET = 'c6b30813-9c97-5654-98f3-c50d8b4e9fb1'          # ethernet_magjack sheet symbol
SYMBOL = {'R5': '8785faf4-13c6-56e9-8bd4-576c953762f2', 'R6': 'dcc21e00-4d08-54d7-bad7-b13beec49da8'}
W = 0.15                                                 # signal track width (as the other 3V3 signals)

b = pcbnew.LoadBoard(sys.argv[1])
fps = {f.GetReference(): f for f in b.GetFootprints()}
assert 'R5' not in fps and 'R6' not in fps, 'already applied'


def net(name):
    n = b.FindNet(name)
    if n is None:
        n = pcbnew.NETINFO_ITEM(b, name)
        b.Add(n)
        n = b.FindNet(name)
    return n


def pad(ref, num):
    return [p for p in fps[ref].Pads() if p.GetNumber() == num][0]


def track(pts, name, layer, width=W):
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        t = pcbnew.PCB_TRACK(b)
        t.SetStart(pcbnew.VECTOR2I(MM(ax), MM(ay))); t.SetEnd(pcbnew.VECTOR2I(MM(bx), MM(by)))
        t.SetWidth(MM(width)); t.SetLayer(layer); t.SetNet(net(name))
        b.Add(t)


def via(x, y, name, d=0.45, drill=0.3):
    v = pcbnew.PCB_VIA(b)
    v.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
    v.SetWidth(MM(d)); v.SetDrill(MM(drill)); v.SetNet(net(name))
    b.Add(v)


# ---- nets on existing pads ----
for (ref, num), name in {('J1', '11'): 'ETH_LED_ACT_A', ('J1', '12'): 'ETH_LED_ACT_N',
                         ('J1', '13'): 'ETH_LED_LINK_A', ('J1', '14'): 'ETH_LED_LINK_N',
                         ('U5', '37'): 'ETH_LED_LINK_N', ('U5', '39'): 'ETH_LED_ACT_N'}.items():
    pad(ref, num).SetNet(net(name))

# ---- R5 / R6 next to the anode pads (bottom side, pad 1 = anode towards J1) ----
lib = r'C:\Program Files\KiCad\10.0\share\kicad\footprints\Resistor_SMD.pretty'
for ref, anode_pad, anode in (('R5', '11', 'ETH_LED_ACT_A'), ('R6', '13', 'ETH_LED_LINK_A')):
    ap = pad('J1', anode_pad).GetPosition()
    ax, ay = mm(ap.x), mm(ap.y)
    fp = pcbnew.FootprintLoad(lib, 'R_0402_1005Metric')
    fp.SetReference(ref); fp.SetValue('330R')
    fp.SetFPID(pcbnew.LIB_ID('Resistor_SMD', 'R_0402_1005Metric'))
    fp.SetPath(pcbnew.KIID_PATH('/%s/%s' % (SHEET, SYMBOL[ref])))
    fp.SetSheetname('/ethernet_magjack1/'); fp.SetSheetfile('ethernet_magjack.kicad_sch')
    fp.SetPosition(pcbnew.VECTOR2I(MM(ax - 1.72), MM(ay)))
    b.Add(fp)                                            # flip only works on a board item
    fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    for k, v in (('MPN', '0402WGF3300TCE'), ('LCSC', 'C25104')):
        fp.SetField(k, v); fp.GetField(k).SetVisible(False); fp.GetField(k).SetLayer(pcbnew.B_Fab)
    fp.Reference().SetVisible(False)
    fps[ref] = fp
    if mm(pad(ref, '1').GetPosition().x) < mm(pad(ref, '2').GetPosition().x):
        fp.SetOrientationDegrees(180)                    # pad 1 (anode) must face J1
    for p in fp.Pads():
        p.SetNet(net(anode if p.GetNumber() == '1' else '+3V3'))
    p1, p2 = pad(ref, '1').GetPosition(), pad(ref, '2').GetPosition()
    track([(mm(p1.x), mm(p1.y)), (ax, ay)], anode, pcbnew.B_Cu, 0.2)
    vy = ay - 1.2
    track([(mm(p2.x), mm(p2.y)), (mm(p2.x), vy)], '+3V3', pcbnew.B_Cu, 0.2)
    via(mm(p2.x), vy, '+3V3')
    print(ref, 'at', round(ax - 1.72, 3), round(ay, 3), '+3V3 via', round(mm(p2.x), 3), round(vy, 3))

# ---- cathodes: U5 pad -> via (F.Cu stub) ----
ends = {}
for num, name, (vx, vy, d, drill) in (('37', 'ETH_LED_LINK_N', (154.1, 115.0, 0.4, 0.2)),
                                      ('39', 'ETH_LED_ACT_N', (154.9, 115.65, 0.45, 0.3))):
    pp = pad('U5', num).GetPosition()
    track([(mm(pp.x), mm(pp.y)), (vx, vy)], name, pcbnew.F_Cu)
    via(vx, vy, name, d, drill)
    ends[name] = (vx, vy)

# ---- route the cathodes on In3 ----
order = [('ETH_LED_LINK_N', '14'), ('ETH_LED_ACT_N', '12')]
routes = {}
for i, (name, jpad) in enumerate(order):
    r = GridRouter(b, pcbnew.In3_Cu, (100.0, 100.0, 170.0, 120.0), res=0.05, width=W)
    r.load(name)
    for other, pts in routes.items():
        r.add_track(pts)
    jp = pad('J1', jpad).GetPosition()
    start = (mm(jp.x), mm(jp.y))
    path = r.route(start, ends[name], escape=1.0)
    if path is None:
        raise SystemExit('no route for ' + name)
    pts = simplify(path)
    pts[0], pts[-1] = start, ends[name]
    routes[name] = pts
    length = sum(((bx - ax) ** 2 + (by - ay) ** 2) ** 0.5 for (ax, ay), (bx, by) in zip(pts, pts[1:]))
    print(name, '%d segments, %.1f mm' % (len(pts) - 1, length), pts)
    track(pts, name, pcbnew.In3_Cu)

pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(sys.argv[1])
print('saved')
