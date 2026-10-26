"""Rev 4f board change: D11 WS2812B-2020 -> green 0603 LED, C64 removed.
Usage: <KiCad python> tools/pcb_rev4f_led.py <board.kicad_pcb>   (board is modified in place)
"""
import sys
import pcbnew

FP_LIB = r'C:\Program Files\KiCad\10.0\share\kicad\footprints\LED_SMD.pretty'
mm, MM = pcbnew.ToMM, pcbnew.FromMM

b = pcbnew.LoadBoard(sys.argv[1])
net = lambda name: b.FindNet(name)


def footprint(ref):
    for f in b.GetFootprints():
        if f.GetReference() == ref:
            return f
    raise KeyError(ref)


def at(item_pt, x, y, tol=0.01):
    return abs(mm(item_pt.x) - x) < tol and abs(mm(item_pt.y) - y) < tol


c64, old = footprint('C64'), footprint('D11')   # look up before removing anything

# ---- remove copper that only served the WS2812 VDD pad and C64 ----
remove = []
for t in b.GetTracks():
    s, e, n = t.GetStart(), t.GetEnd(), t.GetNetname()
    if t.GetClass() == 'PCB_VIA':
        if n == '+3V3' and at(s, 160.788, 112.245):            # via of the old D11 VDD stub
            remove.append(t)
        continue
    if n == '+3V3' and at(s, 161.85, 112.685) and at(e, 160.788, 112.245):
        remove.append(t)                                       # old D11 pad 4 (VDD) stub
    elif n == '+3V3' and at(s, 162.82, 116.0) and at(e, 162.21, 116.0):
        remove.append(t)                                       # C64 pad 1
    elif n == 'GND' and ((at(s, 163.78, 115.616, 0.02) and at(e, 163.78, 116.0)) or
                         (at(s, 164.225, 115.171, 0.02) and at(e, 163.78, 115.616, 0.02))):
        remove.append(t)                                       # C64 pad 2
assert len(remove) == 5, [(r.GetClass(), r.GetNetname()) for r in remove]
for t in remove:
    b.Remove(t)

b.Remove(c64)

# ---- replace D11 ----
path = old.GetPath()
b.Remove(old)

fp = pcbnew.FootprintLoad(FP_LIB, 'LED_0603_1608Metric')
fp.SetReference('D11')
fp.SetValue('green')
fp.SetFPID(pcbnew.LIB_ID('LED_SMD', 'LED_0603_1608Metric'))
fp.GetField(pcbnew.FIELD_T_DESCRIPTION).SetText('Light emitting diode')
fp.SetPath(path)
fp.SetLayer(pcbnew.F_Cu)
# Anode (pad 2) covers the LED_DIN_R track end (162.95/112.685), cathode (pad 1) the GND track
# end (162.95/114.515). Position chosen between the +3V3 via 162.32/113.56 (lies in the pad gap)
# and the USB_EN via 163.95/114.45: hole clearance >= 0.25 mm and copper clearance >= 0.15 mm.
fp.SetPosition(pcbnew.VECTOR2I(MM(163.03), MM(113.56)))
fp.SetOrientationDegrees(90)
for name, value in (('MPN', 'MEIHUA MHT193CGCT'), ('LCSC', 'C2962098')):
    fp.SetField(name, value)
    fp.GetField(name).SetVisible(False)
    fp.GetField(name).SetLayer(pcbnew.F_Fab)
fp.Reference().SetVisible(False)          # as before: refdes hidden (no room on the 20 mm board)
b.Add(fp)
for p in fp.Pads():
    p.SetNet(net({'1': 'GND', '2': 'LED_DIN_R'}[p.GetNumber()]))
    print('D11 pad', p.GetNumber(), p.GetNetname(), round(mm(p.GetPosition().x), 3), round(mm(p.GetPosition().y), 3))

# refill zones and save
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(sys.argv[1])
print('saved', sys.argv[1])
