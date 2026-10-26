"""Add a filled silkscreen dot next to pin 1 of every part where orientation matters
(ICs, crystals, diodes/LED, polarised caps; U5 is left out - its footprint already has a pin-1 dot). The dot goes on the silk layer of the side the
part is mounted on, at the first free spot around pad 1 (clear of all pads of that side and
of the board edge). Dots are board graphics in the group "PIN1_MARKS" (footprints stay
identical to the library, no lib_footprint_mismatch). Re-running replaces the group.
Usage: <KiCad python> tools/pcb_pin1_marks.py <board.kicad_pcb>   (modified in place)
"""
import math
import sys
import pcbnew

REFS = ['U1', 'U4', 'U6', 'U7', 'Y1', 'Y2', 'D1', 'D2', 'D3', 'D11', 'D12', 'C11', 'C18']
DOT_D = 0.5          # dot diameter, mm
PAD_CLEAR = 0.15     # silk to pad / solder-mask opening
EDGE_CLEAR = 0.3     # silk to board edge
mm, MM = pcbnew.ToMM, pcbnew.FromMM

b = pcbnew.LoadBoard(sys.argv[1])

# dots of a previous run (removed after all geometry has been read: the SWIG wrappers
# of KiCad 10 return untyped objects once something has been removed from the board)
old_groups = [g for g in b.Groups() if g.GetName() == 'PIN1_MARKS']
old_dots = [item for g in old_groups for item in g.GetItems()]
old_ids = {item.m_Uuid.AsString() for item in old_dots}

edge = b.GetBoardEdgesBoundingBox()
ex0, ey0, ex1, ey1 = mm(edge.GetLeft()), mm(edge.GetTop()), mm(edge.GetRight()), mm(edge.GetBottom())

fps = {f.GetReference(): f for f in b.GetFootprints()}
pads_by_side = {pcbnew.F_Cu: [], pcbnew.B_Cu: []}
for f in fps.values():
    for p in f.Pads():
        bb = p.GetBoundingBox()
        box = (mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom()))
        for side in (pcbnew.F_Cu, pcbnew.B_Cu):
            if p.IsOnLayer(side):
                pads_by_side[side].append(box)


# existing silkscreen per side (footprint outlines, polygons, texts) - dots should stand free
silk_by_side = {pcbnew.F_Cu: [], pcbnew.B_Cu: []}
for f in fps.values():
    for g in list(f.GraphicalItems()) + [f.Reference(), f.Value()]:
        lay = g.GetLayer()
        if lay not in (pcbnew.F_SilkS, pcbnew.B_SilkS):
            continue
        if hasattr(g, 'IsVisible') and not g.IsVisible():
            continue
        side = pcbnew.F_Cu if lay == pcbnew.F_SilkS else pcbnew.B_Cu
        if g.GetClass() == 'PCB_SHAPE' and g.GetShape() == pcbnew.SHAPE_T_SEGMENT:
            s, e = g.GetStart(), g.GetEnd()
            silk_by_side[side].append(('seg', mm(s.x), mm(s.y), mm(e.x), mm(e.y), mm(g.GetWidth()) / 2))
        else:
            bb = g.GetBoundingBox()
            silk_by_side[side].append(('box', mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom()), 0))
for g in b.GetDrawings():
    if g.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS) and g.m_Uuid.AsString() not in old_ids:
        side = pcbnew.F_Cu if g.GetLayer() == pcbnew.F_SilkS else pcbnew.B_Cu
        bb = g.GetBoundingBox()
        silk_by_side[side].append(('box', mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom()), 0))


def seg_dist(x, y, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    l2 = dx * dx + dy * dy
    u = 0 if l2 == 0 else max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / l2))
    return math.hypot(x - x1 - u * dx, y - y1 - u * dy)


def silk_free(x, y, side, clear=0.15):
    r = DOT_D / 2
    for it in silk_by_side[side]:
        if it[0] == 'seg':
            d = seg_dist(x, y, *it[1:5]) - it[5]
        else:
            d = box_dist(x, y, it[1:5])
        if d < r + clear:
            return False
    return True


def box_dist(x, y, box):
    dx = max(box[0] - x, 0, x - box[2])
    dy = max(box[1] - y, 0, y - box[3])
    return math.hypot(dx, dy)


def free(x, y, side):
    r = DOT_D / 2
    if not (ex0 + EDGE_CLEAR + r <= x <= ex1 - EDGE_CLEAR - r and ey0 + EDGE_CLEAR + r <= y <= ey1 - EDGE_CLEAR - r):
        return False
    return all(box_dist(x, y, bx) >= r + PAD_CLEAR for bx in pads_by_side[side])


for item in old_dots:
    b.Remove(item)
for g in old_groups:
    b.Remove(g)

def body_box(f):
    """Bounding box of the part body (fab layer graphics), mm."""
    fab = pcbnew.B_Fab if f.IsFlipped() else pcbnew.F_Fab
    boxes = [g.GetBoundingBox() for g in f.GraphicalItems() if g.GetLayer() == fab and g.GetClass() == 'PCB_SHAPE']
    if not boxes:
        return None
    return (min(mm(x.GetLeft()) for x in boxes), min(mm(x.GetTop()) for x in boxes),
            max(mm(x.GetRight()) for x in boxes), max(mm(x.GetBottom()) for x in boxes))


def unambiguous(f, pad1, x, y):
    """Dot not hidden under the body and clearly nearer to pad 1 than to any other pad."""
    body = body_box(f)
    if body and body_box_dist(x, y, body) < 0.1:
        return False
    d1 = math.hypot(x - mm(pad1.GetPosition().x), y - mm(pad1.GetPosition().y))
    for p in f.Pads():
        if p.GetNumber() != '1' and math.hypot(x - mm(p.GetPosition().x), y - mm(p.GetPosition().y)) < d1 * 1.25:
            return False
    return True


def body_box_dist(x, y, box):
    inside = box[0] <= x <= box[2] and box[1] <= y <= box[3]
    return -1 if inside else box_dist(x, y, box)


group = pcbnew.PCB_GROUP(b)
group.SetName('PIN1_MARKS')
b.Add(group)
for ref in REFS:
    f = fps[ref]
    side = pcbnew.B_Cu if f.IsFlipped() else pcbnew.F_Cu
    silk = pcbnew.B_SilkS if f.IsFlipped() else pcbnew.F_SilkS
    pad1 = [p for p in f.Pads() if p.GetNumber() == '1'][0]
    bb = pad1.GetBoundingBox()
    px, py = mm(pad1.GetPosition().x), mm(pad1.GetPosition().y)
    hw, hh = mm(bb.GetWidth()) / 2, mm(bb.GetHeight()) / 2
    cx, cy = mm(f.GetPosition().x), mm(f.GetPosition().y)
    out = math.atan2(py - cy, px - cx) if (px, py) != (cx, cy) else 0.0
    # candidate directions: outward from the part centre first, then all around
    angles = [out] + [out + s * math.radians(a) for a in range(15, 181, 15) for s in (1, -1)]
    spot = None
    for relaxed, extra in [(False, e) for e in (0.0, 0.2, 0.4, 0.7, 1.0)] + [(True, e) for e in (0.0, 0.2, 0.4)]:
        for a in angles:
            ux, uy = math.cos(a), math.sin(a)
            # distance from pad centre to the pad box edge along (ux, uy)
            t = min(hw / abs(ux) if abs(ux) > 1e-9 else 1e9, hh / abs(uy) if abs(uy) > 1e-9 else 1e9)
            d = t + PAD_CLEAR + DOT_D / 2 + 0.02 + extra
            x, y = round(px + ux * d, 3), round(py + uy * d, 3)
            if free(x, y, side) and unambiguous(f, pad1, x, y) and (relaxed or silk_free(x, y, side)):
                spot = (x, y)
                break
        if spot:
            break
    if spot is None:
        print('%-4s no free spot found' % ref)
        continue
    dot = pcbnew.PCB_SHAPE(b)
    dot.SetShape(pcbnew.SHAPE_T_CIRCLE)
    dot.SetLayer(silk)
    dot.SetCenter(pcbnew.VECTOR2I(MM(spot[0]), MM(spot[1])))
    dot.SetEnd(pcbnew.VECTOR2I(MM(spot[0] + DOT_D / 4), MM(spot[1])))   # radius D/4 + width D/2 -> filled dot of D
    dot.SetWidth(MM(DOT_D / 2))
    dot.SetFilled(True)
    b.Add(dot)
    group.AddItem(dot)
    print('%-4s %s dot at %.3f / %.3f (pad 1 at %.2f / %.2f)' % (ref, 'B' if f.IsFlipped() else 'T', spot[0], spot[1], px, py))

b.Save(sys.argv[1])
print('saved', sys.argv[1])
