"""SolidCraft command script: rectangular enclosure (variant 2) for the PoE-USB-HID bridge.

Coordinates: x along the board (0 = RJ45 board edge, 80 = USB edge), y = -(KiCad y - 10),
z = 0 at the PCB bottom (PCB top at 1.6). Two parts:
  Wanne  (tray)  z -8.7 ... 4.0: floor, PCB ledges, 4 cable tie tunnels in the plinth
  Deckel (cover) z  4.0 ... 13.4: RJ45 sticks out through the top, USB opening in the end wall,
                                  snap lips that click into a groove inside the tray walls
Usage: python make_script.py <export dir> <script.json>
"""
import json
import sys

OUT, SCRIPT = sys.argv[1], sys.argv[2]
C = []


def cmd(c, **p):
    C.append({"command": c, "params": p})


X0, X1 = -2.0, 82.1           # outer length (inner 0 ... 80.1)
YO = 12.2                     # outer half width (inner 10.2)
ZB, ZS, ZT = -5.4, 4.0, 13.4  # tray bottom, seam, cover top
W = 2.0                       # wall
LIPS = ((26, 40), (56, 70))   # snap lip x ranges (per side)

# ---------------- Wanne (tray) ----------------
cmd("solid.box", length=X1 - X0, width=2 * YO, height=ZS - ZB, corner=[X0, -YO, ZB],
    body_name="Wanne", name="Wanne_Block")
cmd("solid.fillet", body="Wanne", radius=2, name="Wanne_Ecken",
    edges=[[X0, YO, 0], [X0, -YO, 0], [X1, YO, 0], [X1, -YO, 0]])
cmd("solid.shell", body="Wanne", faces=[[40, 0, ZS]], thickness=W, name="Wanne_Schale")
# plinth with chamfered foot and 4 cable tie tunnels (8 x 2.1, through in y)
cmd("solid.box", length=80, width=18, height=3.4, corner=[0, -9, -8.7], operation="join",
    targets=["Wanne"], name="Sockel")
cmd("solid.chamfer", body="Wanne", distance=0.8, name="Sockel_Fase",
    edges=[[40, 9, -8.7], [40, -9, -8.7], [0, 0, -8.7], [80, 0, -8.7]])
cmd("solid.box", length=8, width=30, height=2.1, corner=[2, -15, -7.5], operation="cut",
    targets=["Wanne"], name="Kabelbinder")
cmd("solid.pattern.rectangular", features=["Kabelbinder"], dir1=[1, 0, 0], count1=4,
    spacing1=22, name="Kabelbinder_4x")
# PCB ledges along both long sides (PCB bottom at z 0), clear of bottom parts (|y| <= 9.47)
cmd("solid.box", length=80.1, width=0.65, height=3.4, corner=[0, 9.6, -3.4], operation="join",
    targets=["Wanne"], name="Auflage_R")
cmd("solid.box", length=80.1, width=0.65, height=3.4, corner=[0, -10.25, -3.4], operation="join",
    targets=["Wanne"], name="Auflage_L")
# RJ45 front: wall only below the PCB top inside the jack width
cmd("solid.box", length=3.2, width=16.7, height=4, corner=[-3, -8.35, 1.6], operation="cut",
    targets=["Wanne"], name="RJ45_Wanne")
# snap pockets inside both long walls, only as long as the lips (+0.15 per end): the lip ends
# hit the pocket ends, so the cover cannot slide lengthwise on the tray
for i, (xa, xb) in enumerate(LIPS):
    for side, y in (("R", 10.1), ("L", -10.7)):
        cmd("solid.box", length=xb - xa + 0.3, width=0.6, height=1.0, corner=[xa - 0.15, y, 2.5],
            operation="cut", targets=["Wanne"], name=f"Rasttasche_{side}{i}")
# low air intake slots under the PCB (PoE side)
cmd("sketch.create", plane="XZ", name="ZuluftSkizze")
cmd("sketch.slot.overall", p0=[24, 1.5], p1=[44, 1.5], width=2)
cmd("sketch.finish")
cmd("solid.extrude", distance=30, direction="symmetric", operation="cut", targets=["Wanne"],
    name="Zuluft")

# ---------------- Deckel (cover) ----------------
cmd("solid.box", length=X1 - X0, width=2 * YO, height=ZT - ZS, corner=[X0, -YO, ZS],
    body_name="Deckel", name="Deckel_Block")
cmd("solid.fillet", body="Deckel", radius=2, name="Deckel_Ecken",
    edges=[[X0, YO, 8.7], [X0, -YO, 8.7], [X1, YO, 8.7], [X1, -YO, 8.7]])
cmd("solid.fillet", body="Deckel", radius=1.5, name="Deckel_Oberkante", edges=[[40, YO, ZT]])
cmd("solid.shell", body="Deckel", faces=[[40, 0, ZS]], thickness=W, name="Deckel_Schale")
# RJ45 jack through the top and the front (jack body x -0.6 ... 21.3, |y| <= 8.05)
cmd("solid.box", length=24.65, width=16.7, height=11, corner=[-3, -8.35, 3.9], operation="cut",
    targets=["Deckel"], name="RJ45_Aussparung")
# USB opening (J2 z 1.6 ... 8.6, |y| <= 7.65) through cover and tray end walls
cmd("solid.box", length=3.5, width=15.6, height=7.4, corner=[79.5, -7.8, 1.6], operation="cut",
    targets=["Deckel", "Wanne"], name="USB_Ausschnitt")
# snap lips (2 per side, x 26-40 and 56-70): lip, bridge into the cover wall, 45 deg bump
for i, (xa, xb) in enumerate(LIPS):
    cmd("solid.box", length=xb - xa, width=0.8, height=2.95, corner=[xa, 9.35, 1.65],
        operation="join", targets=["Deckel"], name=f"Lippe_{i}")
    cmd("solid.box", length=xb - xa, width=1.25, height=0.6, corner=[xa, 9.35, 4.0],
        operation="join", targets=["Deckel"], name=f"Steg_{i}")
    cmd("sketch.create", plane="YZ", offset=xa, name=f"NockeSkizze_{i}")
    cmd("sketch.line", points=[[10.0, 2.6], [10.4, 3.0], [10.0, 3.4]], closed=True, infer=False)
    cmd("sketch.finish")
    cmd("solid.extrude", distance=xb - xa, operation="join", targets=["Deckel"], name=f"Nocke_{i}")
cmd("solid.mirror", features=["Lippe_0", "Steg_0", "Nocke_0", "Lippe_1", "Steg_1", "Nocke_1"],
    plane="XZ", combine=True, name="Rastlippen_L")
# status LED above D11, countersunk
cmd("sketch.create", plane="XY", offset=14, name="LEDSkizze")
cmd("sketch.circle.center", center=[63.03, -3.56], diameter=4.48)
cmd("sketch.finish")
cmd("solid.extrude", distance=4, direction="negative", taper="-21.8 deg", operation="cut",
    targets=["Deckel"], name="LED_Fenster")
# logo on the +y side wall, 0.6 mm deep (sketch x = -X so it reads correctly from outside)
cmd("sketch.create", plane={"origin": [0, YO, 0], "x_dir": [-1, 0, 0], "y_dir": [0, 0, 1]},
    name="LogoSkizze")
cmd("sketch.text", text="VAT", at=[-58, 5.2], height=5.5, font="Arial", bold=True,
    align="center")
cmd("sketch.finish")
cmd("solid.extrude", distance=0.6, direction="negative", operation="cut", targets=["Deckel"],
    name="Logo_VAT")
# side vents (2 rows) over the PoE module
cmd("sketch.create", plane="XZ", name="SeitenluftSkizze")
cmd("sketch.slot.overall", p0=[24, -6.5], p1=[44, -6.5], width=2)
cmd("sketch.slot.overall", p0=[24, -9.5], p1=[44, -9.5], width=2)
cmd("sketch.finish")
cmd("solid.extrude", distance=30, direction="symmetric", operation="cut", targets=["Deckel"],
    name="Seitenluft")
# top vents across the module, chamfered by a tapered cut (2.0 inside, 3.0 outside)
cmd("sketch.create", plane="XY", offset=14, name="DachluftSkizze")
cmd("sketch.slot.overall", p0=[24.5, -7.3], p1=[24.5, 7.3], width=3.3)
cmd("sketch.finish")
cmd("solid.extrude", distance=4, direction="negative", taper="-14 deg", operation="cut",
    targets=["Deckel"], name="Dachluft")
cmd("solid.pattern.rectangular", features=["Dachluft"], dir1=[1, 0, 0], count1=5, spacing1=5,
    name="Dachluft_5x")

# ---------------- PCB dummies (fit check only) ----------------
for n, l, w, h, c in (("Dummy_PCB", 80, 20, 1.6, [0, -10, 0]),
                      ("Dummy_J1", 21.9, 16.1, 13.3, [-0.6, -8.05, 1.6]),
                      ("Dummy_J2", 13.9, 15.3, 7, [66.15, -7.65, 1.6]),
                      ("Dummy_U1", 21.21, 13.92, 9.2, [23.9, -6.96, 1.6]),
                      ("Dummy_J1_Pins", 19, 14, 3, [1, -7, -3]),
                      ("Dummy_Bottom", 60, 14, 2.6, [20, -7, -2.6])):
    cmd("solid.box", length=l, width=w, height=h, corner=c, operation="new", body_name=n, name=n)

# ---------------- print layout for Bambu A1 ----------------
cmd("solid.move", bodies=["Wanne"], translate=[88, 128, 8.7], copy=True)
cmd("body.rename", body="Wanne (2)", name="Druck_Wanne")
cmd("solid.move", bodies=["Deckel"], axis=[1, 0, 0], angle="180 deg", copy=True)
cmd("body.rename", body="Deckel (2)", name="Druck_Deckel")
cmd("solid.move", bodies=["Druck_Deckel"], translate=[88, 160, ZT])


def exp(name, bodies, **kw):
    cmd("file.export", path=OUT + "\\" + name, bodies=bodies, **kw)


exp("A1_eckig_druckplatte.3mf", ["Druck_Wanne", "Druck_Deckel"], quality="fine")
exp("A1_wanne.stl", ["Druck_Wanne"], quality="fine")
exp("A1_deckel_kopfueber.stl", ["Druck_Deckel"], quality="fine")
exp("gehaeuse_eckig.3mf", ["Wanne", "Deckel"])
exp("gehaeuse_eckig.step", ["Wanne", "Deckel"])

json.dump({"commands": C}, open(SCRIPT, "w", encoding="utf-8"), indent=1)
print(len(C), "commands")
