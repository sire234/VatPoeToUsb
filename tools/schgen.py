"""schgen - redraw a KiCad 10 schematic sheet with real wires.

Takes the existing (SKiDL-generated, label-only) sheet as data source: lib_symbols,
symbol UUIDs, fields and instance paths are kept, so the PCB link (footprint path
/<sheet uuid>/<symbol uuid>) stays intact. Placement and wiring are given by a small
per-sheet layout script, e.g.:

    s = Sheet.load('status_led.kicad_sch', pwr_prefix=7)
    s.place('R38', 73.66, 60.96, 90)
    s.wire(s.pin('R38', '2'), (93.98, 60.96), s.pin('D11', 'A'))
    s.power('GND', s.pin('D11', 'K'), down=7.62)
    s.save('status_led.kicad_sch')

Coordinates in mm, schematic y axis points down, rotations CCW in degrees as in eeschema.
Keep everything on the 1.27 mm grid.
"""
import math
import re
import uuid as _uuid

GRID = 1.27


# ----------------------------------------------------------------------------
# Minimal s-expression parser that keeps source spans (to copy blocks verbatim)
# ----------------------------------------------------------------------------
class Node(list):
    start = 0
    end = 0

    @property
    def tag(self):
        return self[0] if self and isinstance(self[0], Atom) else None

    def find(self, tag):
        for c in self:
            if isinstance(c, Node) and c.tag == tag:
                return c
        return None

    def findall(self, tag):
        return [c for c in self if isinstance(c, Node) and c.tag == tag]


class Atom(str):
    quoted = False


def parse(text):
    stack, root = [], Node()
    i, n = 0, len(text)
    cur = root
    while i < n:
        ch = text[i]
        if ch == '(':
            node = Node(); node.start = i
            cur.append(node); stack.append(cur); cur = node; i += 1
        elif ch == ')':
            cur.end = i + 1; cur = stack.pop(); i += 1
        elif ch == '"':
            j = i + 1; buf = []
            while text[j] != '"':
                if text[j] == '\\':
                    buf.append(text[j:j + 2]); j += 2
                else:
                    buf.append(text[j]); j += 1
            a = Atom(''.join(buf)); a.quoted = True
            cur.append(a); i = j + 1
        elif ch.isspace():
            i += 1
        else:
            j = i
            while j < n and not text[j].isspace() and text[j] not in '()':
                j += 1
            cur.append(Atom(text[i:j])); i = j
    return root[0]


def q(s):
    return '"' + str(s).replace('"', '\\"') + '"'


def fmt(v):
    v = round(v, 4)
    if abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    return ('%.4f' % v).rstrip('0').rstrip('.')


def uid():
    return str(_uuid.uuid4())


def snap(p):
    return (round(round(p[0] / GRID) * GRID, 4), round(round(p[1] / GRID) * GRID, 4))


# ----------------------------------------------------------------------------
# Library symbol pin geometry
# ----------------------------------------------------------------------------
class LibSym:
    def __init__(self, node, src):
        self.name = str(node[1])
        self.raw = src[node.start:node.end]
        self.pins = []          # (unit, number, name, x, y)
        for sub in node.findall('symbol'):
            m = re.match(r'.*_(\d+)_(\d+)$', str(sub[1]))
            unit = int(m.group(1)) if m else 0
            style = int(m.group(2)) if m else 1
            if style not in (0, 1):
                continue
            for p in sub.findall('pin'):
                at = p.find('at')
                num = p.find('number'); nam = p.find('name')
                self.pins.append((unit, str(num[1]), str(nam[1]), float(at[1]), float(at[2])))
        self.is_power = node.find('power') is not None

    def pin_xy(self, key, unit=1):
        hits = [p for p in self.pins if p[0] in (0, unit) and (p[1] == key or p[2] == key)]
        if not hits:
            raise KeyError('%s: no pin %s' % (self.name, key))
        nums = {h[1] for h in hits}
        if len(nums) > 1:
            raise KeyError('%s: pin name %s ambiguous (%s), use the number' % (self.name, key, sorted(nums)))
        return hits[0][3], hits[0][4]


def xform(lx, ly, X, Y, rot, mirror=None):
    if mirror == 'y':
        lx = -lx
    elif mirror == 'x':
        ly = -ly
    r = math.radians(rot)
    rx = lx * math.cos(r) - ly * math.sin(r)
    ry = lx * math.sin(r) + ly * math.cos(r)
    return (round(X + rx, 4), round(Y - ry, 4))


# ----------------------------------------------------------------------------
# Sheet
# ----------------------------------------------------------------------------
class Comp:
    def __init__(self, node, src):
        self.lib_id = str(node.find('lib_id')[1])
        self.uuid = str(node.find('uuid')[1])
        unit = node.find('unit')
        self.unit = int(unit[1]) if unit else 1
        self.flags = {}
        for k in ('exclude_from_sim', 'in_bom', 'on_board', 'dnp'):
            f = node.find(k)
            if f:
                self.flags[k] = str(f[1])
        self.props = []         # (name, value, hidden)
        for p in node.findall('property'):
            eff = p.find('effects')
            hidden = bool(eff and (eff.find('hide') is not None))
            self.props.append([str(p[1]), str(p[2]), hidden])
        self.pin_uuids = {str(p[1]): str(p.find('uuid')[1]) for p in node.findall('pin')}
        inst = node.find('instances').find('project')
        self.project = str(inst[1])
        path = inst.find('path')
        self.path = str(path[1])
        self.ref = self.prop('Reference')
        self.placed = None      # (x, y, rot, mirror)
        self.field_pos = {}

    def prop(self, name):
        for p in self.props:
            if p[0] == name:
                return p[1]
        return None

    def set_prop(self, name, value, hidden=True):
        for p in self.props:
            if p[0] == name:
                p[1] = value
                return
        self.props.append([name, value, hidden])


class Sheet:
    @classmethod
    def load(cls, path, pwr_prefix, project=None):
        s = cls()
        s.src = open(path, encoding='utf-8').read()
        s.tree = parse(s.src)
        s.pwr_prefix = pwr_prefix
        s.pwr_count = 0
        s.header = {}
        for tag in ('version', 'generator', 'generator_version', 'uuid', 'paper'):
            s.header[tag] = s.tree.find(tag)
        s.title_block = s.tree.find('title_block')
        s.title = {}
        for c in s.title_block[1:]:
            if c.tag == 'comment':
                s.title['comment %s' % c[1]] = str(c[2])
            else:
                s.title[str(c.tag)] = str(c[1])
        s.libs = {}
        for ls in s.tree.find('lib_symbols').findall('symbol'):
            sym = LibSym(ls, s.src)
            s.libs[sym.name] = sym
        s.comps = {}
        s.project = s.path = None
        for node in s.tree.findall('symbol'):
            c = Comp(node, s.src)
            s.project, s.path = c.project, c.path
            if s.libs[c.lib_id].is_power:
                continue          # power symbols are redrawn
            s.comps[c.ref] = c
        if project:
            s.project = project
        s.items = []              # emitted top-level text blocks
        s.wires = []              # ((x1,y1),(x2,y2))
        s.pin_points = []         # all placed pin coordinates
        s.label_points = []
        s.nc_points = []
        return s

    # ---- library handling ----
    def add_lib_symbol(self, kicad_sym_file, name, lib_nick):
        """Copy a symbol from a KiCad .kicad_sym library into lib_symbols as lib_nick:name."""
        text = open(kicad_sym_file, encoding='utf-8').read()
        tree = parse(text)
        for node in tree.findall('symbol'):
            if str(node[1]) == name:
                raw = text[node.start:node.end]
                raw = raw.replace('(symbol "%s"' % name, '(symbol "%s:%s"' % (lib_nick, name), 1)
                if node.find('extends') is not None:
                    raise ValueError('derived symbol %s not supported' % name)
                sym = LibSym(parse(raw), raw)
                self.libs[sym.name] = sym
                return sym
        raise KeyError(name)

    def new_comp(self, ref, lib_id, value, footprint, fields=(), unit=1):
        """Add a component that the source sheet does not have yet. UUIDs are derived from
        the sheet path and the reference, so regenerating keeps the PCB link stable."""
        c = Comp.__new__(Comp)
        c.lib_id, c.unit, c.flags = lib_id, unit, {}
        c.uuid = str(_uuid.uuid5(_uuid.NAMESPACE_URL, 'schgen:%s:%s' % (self.path, ref)))
        c.props = [['Reference', ref, False], ['Value', value, False], ['Footprint', footprint, True],
                   ['Datasheet', '', True], ['Description', '', True]] + [[k, v, True] for k, v in fields]
        c.pin_uuids = {p[1]: str(_uuid.uuid5(_uuid.NAMESPACE_URL, 'schgen:%s:%s:%s' % (self.path, ref, p[1])))
                       for p in self.libs[lib_id].pins if p[0] in (0, unit)}
        c.project, c.path, c.ref = self.project, self.path, ref
        c.placed, c.field_pos, c.fields_angle = None, {}, None
        self.comps[ref] = c
        return c

    def drop_comp(self, ref):
        del self.comps[ref]

    # ---- placement ----
    def place(self, ref, x, y, rot=0, mirror=None, ref_at=None, val_at=None, fields_angle=None):
        """Place a component. ref_at / val_at: (dx, dy) of the field centre relative to the
        symbol origin; defaults depend on the orientation."""
        c = self.comps[ref]
        c.placed = (x, y, rot, mirror)
        lib = self.libs[c.lib_id]
        for p in lib.pins:
            if p[0] in (0, c.unit):
                self.pin_points.append(xform(p[3], p[4], x, y, rot, mirror))
        vertical = rot % 180 == 0
        if ref_at is None:
            ref_at = (5.08, -1.27) if vertical else (0, -3.81)
        if val_at is None:
            val_at = (5.08, 1.27) if vertical else (0, 3.81)
        c.field_pos = {'Reference': ref_at, 'Value': val_at}
        c.fields_angle = fields_angle

    def pin(self, ref, key):
        c = self.comps[ref]
        if c.placed is None:
            raise ValueError(ref + ' not placed')
        lx, ly = self.libs[c.lib_id].pin_xy(str(key), c.unit)
        x, y, rot, mirror = c.placed
        return xform(lx, ly, x, y, rot, mirror)

    # ---- drawing primitives ----
    def wire(self, *pts):
        pts = [tuple(round(v, 4) for v in p) for p in pts]
        for a, b in zip(pts, pts[1:]):
            if a == b:
                continue
            if a[0] != b[0] and a[1] != b[1]:
                raise ValueError('wire not orthogonal: %s -> %s' % (a, b))
            self.wires.append((a, b))
        return pts[-1]

    def route(self, a, b, via='h'):
        """L-shaped connection a -> b. via='h': horizontal first, 'v': vertical first."""
        if a[0] == b[0] or a[1] == b[1]:
            return self.wire(a, b)
        corner = (b[0], a[1]) if via == 'h' else (a[0], b[1])
        return self.wire(a, corner, b)

    def flag(self, at, **stub):
        """PWR_FLAG symbol (power:PWR_FLAG) at 'at', optional stub like power()."""
        return self.power('PWR_FLAG', at, **stub)

    def power(self, net, at, down=None, up=None, left=None, right=None):
        """Power symbol (power:<net>) connected to 'at', optionally via a stub wire.
        GND-like symbols point down by default, supply symbols up."""
        lib_id = 'power:' + net
        if lib_id not in self.libs:
            raise KeyError(lib_id + ' not in lib_symbols (add_lib_symbol first)')
        x, y = at
        if down is not None:
            end = (x, y + down)
        elif up is not None:
            end = (x, y - up)
        elif left is not None:
            end = (x - left, y)
        elif right is not None:
            end = (x + right, y)
        else:
            end = (x, y)
        end = (round(end[0], 4), round(end[1], 4))
        self.wire((x, y), end)
        is_gnd = net.upper().startswith('GND') or net.upper() in ('VSS', 'GNDA')
        is_flag = net == 'PWR_FLAG'
        # direction the symbol body points to
        if end[1] > y or (end == (x, y) and is_gnd):
            d = 'down'
        elif end[1] < y or end == (x, y):
            d = 'up'
        elif end[0] < x:
            d = 'left'
        else:
            d = 'right'
        base = 'down' if is_gnd else 'up'
        order = ['up', 'left', 'down', 'right']          # CCW rotation steps of 90 deg
        rot = ((order.index(d) - order.index(base)) % 4) * 90
        self.pwr_count += 1
        ref = '#%s%d%03d' % ('FLG' if is_flag else 'PWR', self.pwr_prefix, self.pwr_count)   # e.g. #PWR7001
        off = {'down': (0, 5.08), 'up': (0, -5.08), 'left': (-5.08, 0), 'right': (5.08, 0)}[d]
        vang = 0 if d in ('up', 'down') else 0
        if not is_gnd and d in ('up', 'down'):
            off = (0, -3.81) if d == 'up' else (0, 3.81)
        if is_flag and d == 'up':
            off = (0, -5.08)
        if is_gnd and d in ('up', 'down'):
            off = (0, 3.81) if d == 'down' else (0, -3.81)
        if d in ('left', 'right'):
            off = (-6.35, 0) if d == 'left' else (6.35, 0)
        self.items.append(self._symbol_text(
            lib_id, end[0], end[1], rot, None, uid(), {'in_bom': 'no', 'on_board': 'no'},
            [['Reference', ref, True], ['Value', net, False],
             ['Footprint', '', True], ['Datasheet', '', True], ['Description', '', True]],
            {'Reference': (0, 0), 'Value': off}, {'1': uid()}, ref, 1, vang))
        self.pin_points.append(end)
        return end

    def glabel(self, name, at, angle=180, shape='passive'):
        """Global label anchored at 'at'. angle 180: body to the left, 0: to the right,
        90: up, 270: down."""
        x, y = round(at[0], 4), round(at[1], 4)
        just = {0: 'left', 180: 'right', 90: 'left', 270: 'right'}[angle]
        self.items.append(
            '\t(global_label %s\n\t\t(shape %s)\n\t\t(at %s %s %d)\n\t\t(fields_autoplaced yes)\n'
            '\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify %s)\n\t\t)\n'
            '\t\t(uuid %s)\n\t\t(property "Intersheetrefs" "${INTERSHEET_REFS}"\n\t\t\t(at %s %s 0)\n'
            '\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t\t(hide yes)\n\t\t\t)\n\t\t)\n\t)\n'
            % (q(name), shape, fmt(x), fmt(y), angle, just, q(uid()), fmt(x), fmt(y)))
        self.label_points.append((x, y))

    def noconnect(self, at):
        self.items.append('\t(no_connect\n\t\t(at %s %s)\n\t\t(uuid %s)\n\t)\n' % (fmt(at[0]), fmt(at[1]), q(uid())))
        self.nc_points.append((round(at[0], 4), round(at[1], 4)))

    def text(self, s, x, y, size=1.8, bold=False):
        b = ' (bold yes)' if bold else ''
        self.items.append(
            '\t(text %s\n\t\t(exclude_from_sim no)\n\t\t(at %s %s 0)\n\t\t(effects\n\t\t\t(font\n'
            '\t\t\t\t(size %s %s)%s\n\t\t\t)\n\t\t\t(justify left bottom)\n\t\t)\n\t\t(uuid %s)\n\t)\n'
            % (q(s), fmt(x), fmt(y), fmt(size), fmt(size), b, q(uid())))

    def frame(self, x1, y1, x2, y2):
        self.items.append(
            '\t(rectangle\n\t\t(start %s %s)\n\t\t(end %s %s)\n\t\t(stroke\n\t\t\t(width 0.254)\n'
            '\t\t\t(type dash)\n\t\t)\n\t\t(fill\n\t\t\t(type none)\n\t\t)\n\t\t(uuid %s)\n\t)\n'
            % (fmt(x1), fmt(y1), fmt(x2), fmt(y2), q(uid())))

    # ---- output ----
    def _symbol_text(self, lib_id, x, y, rot, mirror, u, flags, props, fpos, pin_uuids, ref, unit,
                     fangle=None):
        fa = rot % 180 if fangle is None else fangle
        out = ['\t(symbol\n\t\t(lib_id %s)\n\t\t(at %s %s %d)\n' % (q(lib_id), fmt(x), fmt(y), rot)]
        if mirror:
            out.append('\t\t(mirror %s)\n' % mirror)
        out.append('\t\t(unit %d)\n' % unit)
        fl = {'exclude_from_sim': 'no', 'in_bom': 'yes', 'on_board': 'yes', 'dnp': 'no'}
        fl.update(flags)
        for k in ('exclude_from_sim', 'in_bom', 'on_board', 'dnp'):
            out.append('\t\t(%s %s)\n' % (k, fl[k]))
        out.append('\t\t(uuid %s)\n' % q(u))
        for name, value, hidden in props:
            dx, dy = fpos.get(name, (0, 0))
            hide = '\t\t\t\t(hide yes)\n' if hidden else ''
            out.append('\t\t(property %s %s\n\t\t\t(at %s %s %d)\n\t\t\t(effects\n\t\t\t\t(font\n'
                       '\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n%s\t\t\t)\n\t\t)\n'
                       % (q(name), q(value), fmt(x + dx), fmt(y + dy), fa, hide))
        for num, pu in pin_uuids.items():
            out.append('\t\t(pin %s\n\t\t\t(uuid %s)\n\t\t)\n' % (q(num), q(pu)))
        out.append('\t\t(instances\n\t\t\t(project %s\n\t\t\t\t(path %s\n\t\t\t\t\t(reference %s)\n'
                   '\t\t\t\t\t(unit %d)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)\n'
                   % (q(self.project), q(self.path), q(ref), unit))  # project may be renamed
        return ''.join(out)

    def _split_wires(self):
        """Split wires at every pin, label or other wire end lying in their interior, so that
        T-connections are explicit (KiCad connects only at wire ends) and get a junction."""
        points = set(self.pin_points) | set(self.label_points)
        for a, b in self.wires:
            points.add(a); points.add(b)
        out = []
        for a, b in self.wires:
            cuts = sorted((p for p in points if _on_segment_interior(p, a, b)),
                          key=lambda p: abs(p[0] - a[0]) + abs(p[1] - a[1]))
            pts = [a] + cuts + [b]
            out.extend(zip(pts, pts[1:]))
        self.wires = list(dict.fromkeys(out))

    def _junctions(self):
        ends = {}
        for a, b in self.wires:
            for p in (a, b):
                ends[p] = ends.get(p, 0) + 1
        pins = set(self.pin_points)
        return [p for p, cnt in ends.items() if cnt + (1 if p in pins else 0) >= 3]

    def crossings(self):
        """Interior-interior wire crossings (not connected in KiCad, but confusing to read)."""
        res = []
        for i, (a, b) in enumerate(self.wires):
            for c, d in self.wires[i + 1:]:
                if a[0] == b[0] and c[1] == d[1]:
                    x, y = a[0], c[1]
                elif a[1] == b[1] and c[0] == d[0]:
                    x, y = c[0], a[1]
                else:
                    continue
                if _on_segment_interior((x, y), a, b) and _on_segment_interior((x, y), c, d):
                    res.append((x, y))
        return res

    def check(self):
        """Dangling wire ends (not on a pin, label, power, other wire or no-connect)."""
        problems = []
        anchors = set(self.pin_points) | set(self.label_points) | set(self.nc_points)
        ends = {}
        for a, b in self.wires:
            for p in (a, b):
                ends[p] = ends.get(p, 0) + 1
        for p, cnt in ends.items():
            if cnt < 2 and p not in anchors:
                problems.append(('dangling wire end', p))
        for c in self.comps.values():
            if c.placed is None:
                problems.append(('not placed', c.ref))
        return problems

    def save(self, path):
        self._split_wires()
        for x in self.crossings():
            print('note: wires cross (not connected) at', x)
        probs = self.check()
        if probs:
            raise ValueError('schematic check failed: %s' % probs)
        h = self.header
        out = ['(kicad_sch\n']
        for tag in ('version', 'generator', 'generator_version', 'uuid', 'paper'):
            n = h[tag]
            v = n[1]
            out.append('\t(%s %s)\n' % (tag, q(v) if v.quoted else v))
        out.append('\t(title_block\n')
        for k, v in self.title.items():
            if k.startswith('comment '):
                out.append('\t\t(comment %s %s)\n' % (k.split()[1], q(v)))
            else:
                out.append('\t\t(%s %s)\n' % (k, q(v)))
        out.append('\t)\n\t(lib_symbols\n')
        used = {c.lib_id for c in self.comps.values()} | {i.split('"')[1] for i in self.items
                                                          if i.startswith('\t(symbol')}
        for name in sorted(used):
            raw = self.libs[name].raw
            out.append('\t\t' + raw.replace('\n', '\n\t\t').rstrip('\t') + '\n')
        out.append('\t)\n')
        for j in self._junctions():
            out.append('\t(junction\n\t\t(at %s %s)\n\t\t(diameter 0)\n\t\t(color 0 0 0 0)\n'
                       '\t\t(uuid %s)\n\t)\n' % (fmt(j[0]), fmt(j[1]), q(uid())))
        for a, b in self.wires:
            out.append('\t(wire\n\t\t(pts\n\t\t\t(xy %s %s) (xy %s %s)\n\t\t)\n\t\t(stroke\n'
                       '\t\t\t(width 0)\n\t\t\t(type default)\n\t\t)\n\t\t(uuid %s)\n\t)\n'
                       % (fmt(a[0]), fmt(a[1]), fmt(b[0]), fmt(b[1]), q(uid())))
        for c in sorted(self.comps.values(), key=lambda c: c.ref):
            x, y, rot, mirror = c.placed
            out.append(self._symbol_text(c.lib_id, x, y, rot, mirror, c.uuid, c.flags, c.props,
                                         c.field_pos, c.pin_uuids, c.ref, c.unit, c.fields_angle))
        out.extend(self.items)
        out.append('\t(embedded_fonts no)\n)\n')
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(''.join(out))


def _on_segment_interior(p, a, b):
    (x, y), (x1, y1), (x2, y2) = p, a, b
    if x1 == x2 == x:
        return min(y1, y2) < y < max(y1, y2)
    if y1 == y2 == y:
        return min(x1, x2) < x < max(x1, x2)
    return False
