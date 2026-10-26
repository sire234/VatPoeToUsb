"""Small grid router (A*, 8 directions) for single tracks on one copper layer of a KiCad board.
Used for Rev 4g to route the MagJack LED cathodes on In3 without touching existing copper.

Obstacles (with clearance to the track edge): pads, holes and vias of other nets, tracks of
other nets on the layer, rule areas that forbid tracks, board edge. Primary (POE_HV) copper
keeps 3.0 mm (J1 pads inside the J1 courtyard: 1.0 mm, documented ISO_EXC_J1 rule). Copper
zones of other nets may be crossed (they refill around the track) but cost extra, so the
router keeps such cuts short.
"""
import heapq
import math

import numpy as np
import pcbnew

mm = pcbnew.ToMM
HV = {'PSE_CT12', 'PSE_CT36', 'PSE_SP45', 'PSE_SP78', 'VDD_POE', 'VSS'}


def points_in_polygon(X, Y, pts):
    """Vectorised even-odd point-in-polygon test."""
    inside = np.zeros(X.shape, dtype=bool)
    n = len(pts)
    for i in range(n):
        (xa, ya), (xb, yb) = pts[i], pts[(i + 1) % n]
        if ya == yb:
            continue
        cond = (Y >= min(ya, yb)) & (Y < max(ya, yb))
        xc = xa + (Y - ya) * (xb - xa) / (yb - ya)
        inside ^= cond & (X < xc)
    return inside


class GridRouter:
    def __init__(self, board, layer, box, res=0.05, width=0.15, clearance=0.2,
                 hole_clearance=0.25, edge_clearance=0.3, zone_cost=4.0, turn_cost=0.6):
        self.b, self.layer, self.res, self.w = board, layer, res, width
        self.x0, self.y0, self.x1, self.y1 = box
        self.nx = int(round((self.x1 - self.x0) / res)) + 1
        self.ny = int(round((self.y1 - self.y0) / res)) + 1
        xs = self.x0 + np.arange(self.nx) * res
        ys = self.y0 + np.arange(self.ny) * res
        self.X, self.Y = np.meshgrid(xs, ys)            # [iy, ix]
        self.free = np.full(self.X.shape, np.inf)       # min free distance to obstacles
        self.cost = np.ones(self.X.shape)
        self.clr, self.hclr, self.eclr = clearance, hole_clearance, edge_clearance
        self.zone_cost, self.turn_cost = zone_cost, turn_cost

    # ---- obstacle primitives: store (distance from centre line to obstacle) - needed gap ----
    def _apply(self, dist, need):
        np.minimum(self.free, dist - need, out=self.free)

    def circle(self, x, y, r, need):
        self._apply(np.hypot(self.X - x, self.Y - y) - r, need)

    def rect(self, cx, cy, hw, hh, need):
        dx = np.maximum(np.abs(self.X - cx) - hw, 0)
        dy = np.maximum(np.abs(self.Y - cy) - hh, 0)
        self._apply(np.hypot(dx, dy), need)

    def segment(self, x1, y1, x2, y2, half, need):
        vx, vy = x2 - x1, y2 - y1
        l2 = vx * vx + vy * vy
        u = np.zeros_like(self.X) if l2 == 0 else np.clip(((self.X - x1) * vx + (self.Y - y1) * vy) / l2, 0, 1)
        self._apply(np.hypot(self.X - x1 - u * vx, self.Y - y1 - u * vy) - half, need)

    def polygon_block(self, pts, need):
        inside = points_in_polygon(self.X, self.Y, pts)
        self.free[inside] = -1
        # keep the track edge out of the area as well
        for (ax, ay), (bx, by) in zip(pts, pts[1:] + pts[:1]):
            self.segment(ax, ay, bx, by, 0, need)

    # ---- collect obstacles from the board ----
    def load(self, net, j1_courtyard=None):
        half = self.w / 2
        L = self.layer

        def need_for(other, in_j1=False):
            if other in HV:
                return half + (1.0 if in_j1 else 3.0)
            return half + self.clr

        for f in self.b.GetFootprints():
            for p in f.Pads():
                if p.GetNetname() == net and net:
                    continue
                pos = p.GetPosition(); px, py = mm(pos.x), mm(pos.y)
                if not (self.x0 - 5 < px < self.x1 + 5 and self.y0 - 5 < py < self.y1 + 5):
                    continue
                attr = p.GetAttribute()
                if attr == pcbnew.PAD_ATTRIB_NPTH:
                    self.circle(px, py, mm(p.GetDrillSize().x) / 2, half + self.hclr)
                    continue
                if not p.IsOnLayer(L):
                    continue
                in_j1 = f.GetReference() == 'J1'
                need = need_for(p.GetNetname(), in_j1)
                sz = p.GetSize(L)
                if p.GetShape(L) == pcbnew.PAD_SHAPE_CIRCLE:
                    self.circle(px, py, mm(sz.x) / 2, need)
                else:
                    bb = p.GetBoundingBox()
                    self.rect((mm(bb.GetLeft()) + mm(bb.GetRight())) / 2, (mm(bb.GetTop()) + mm(bb.GetBottom())) / 2,
                              (mm(bb.GetRight()) - mm(bb.GetLeft())) / 2, (mm(bb.GetBottom()) - mm(bb.GetTop())) / 2, need)
                if attr == pcbnew.PAD_ATTRIB_PTH:
                    self.circle(px, py, mm(p.GetDrillSize().x) / 2, half + self.hclr)
        for t in self.b.GetTracks():
            if t.GetNetname() == net:
                continue
            s, e = t.GetStart(), t.GetEnd()
            if t.GetClass() == 'PCB_VIA':
                x, y = mm(s.x), mm(s.y)
                if self.x0 - 3 < x < self.x1 + 3 and self.y0 - 3 < y < self.y1 + 3:
                    self.circle(x, y, mm(t.GetWidth(pcbnew.F_Cu)) / 2, need_for(t.GetNetname()))
                    self.circle(x, y, mm(t.GetDrillValue()) / 2, half + self.hclr)
            elif t.GetLayer() == L:
                self.segment(mm(s.x), mm(s.y), mm(e.x), mm(e.y), mm(t.GetWidth()) / 2, need_for(t.GetNetname()))
        for z in self.b.Zones():
            o = z.Outline(); ol = o.Outline(0)
            pts = [(mm(ol.CPoint(j).x), mm(ol.CPoint(j).y)) for j in range(ol.PointCount())]
            if z.GetIsRuleArea():
                if z.GetDoNotAllowTracks() and z.IsOnLayer(L):
                    self.polygon_block(pts, half + 0.01)
            elif z.IsOnLayer(L) and z.GetNetname() != net:
                inside = points_in_polygon(self.X, self.Y, pts)
                self.cost[inside] = np.maximum(self.cost[inside], self.zone_cost)
                if z.GetNetname() in HV:
                    self.polygon_block(pts, half + 3.0)
        e = self.b.GetBoardEdgesBoundingBox()
        ex0, ey0, ex1, ey1 = mm(e.GetLeft()), mm(e.GetTop()), mm(e.GetRight()), mm(e.GetBottom())
        edge = np.minimum.reduce([self.X - ex0, ex1 - self.X, self.Y - ey0, ey1 - self.Y])
        self._apply(edge, half + self.eclr)

    def add_track(self, pts, net_is_hv=False):
        """Make a routed track an obstacle for the next one."""
        half = self.w / 2
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            self.segment(ax, ay, bx, by, half, half + self.clr)

    def add_via(self, x, y, d, drill):
        self.circle(x, y, d / 2, self.w / 2 + self.clr)
        self.circle(x, y, drill / 2, self.w / 2 + self.hclr)

    # ---- search ----
    def idx(self, x, y):
        return int(round((y - self.y0) / self.res)), int(round((x - self.x0) / self.res))

    def route(self, start, goal, escape=0.0):
        """A* from start to goal (mm). Cells within 'escape' mm of start/goal are allowed even if
        blocked (the track has to leave the pad/via it starts on)."""
        ok = self.free >= 0
        for (x, y) in (start, goal):
            ok |= np.hypot(self.X - x, self.Y - y) <= escape
        s, g = self.idx(*start), self.idx(*goal)
        dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        h = lambda a: math.hypot(a[0] - g[0], a[1] - g[1])
        openq = [(h(s), 0.0, s, -1)]
        best = {(s, -1): 0.0}
        came = {}
        while openq:
            f, gc, cur, d = heapq.heappop(openq)
            if cur == g:
                path = [cur]
                key = (cur, d)
                while key in came:
                    key = came[key]
                    path.append(key[0])
                path.reverse()
                return [(self.x0 + ix * self.res, self.y0 + iy * self.res) for iy, ix in path]
            if gc > best.get((cur, d), math.inf):
                continue
            for k, (dy, dx) in enumerate(dirs):
                ny, nx = cur[0] + dy, cur[1] + dx
                if not (0 <= ny < self.ny and 0 <= nx < self.nx) or not ok[ny, nx]:
                    continue
                step = (1.414 if dy and dx else 1.0) * self.cost[ny, nx]
                if d != -1 and d != k:
                    step += self.turn_cost
                ng = gc + step
                key = ((ny, nx), k)
                if ng < best.get(key, math.inf):
                    best[key] = ng
                    came[key] = (cur, d)
                    heapq.heappush(openq, (ng + h((ny, nx)), ng, (ny, nx), k))
        return None


def simplify(pts):
    """Merge collinear grid steps into straight segments."""
    if len(pts) < 3:
        return pts
    out = [pts[0]]
    for a, b, c in zip(pts, pts[1:], pts[2:]):
        d1 = (round((b[0] - a[0]) / 0.001), round((b[1] - a[1]) / 0.001))
        d2 = (round((c[0] - b[0]) / 0.001), round((c[1] - b[1]) / 0.001))
        if d1 != d2:
            out.append(b)
    out.append(pts[-1])
    return [(round(x, 3), round(y, 3)) for x, y in out]
