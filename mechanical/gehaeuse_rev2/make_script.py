"""Builds the SolidCraft command script for enclosure v2 (headless run via solidcraft-cli)."""
import json
import sys

OUT = sys.argv[1]          # output dir for exports
SCRIPT = sys.argv[2]       # script json path

JY, JZ = 6.242915, -13.308494   # flank/tube junction (15 deg flank from (7.5,-18), r 14.7)
C = []


def cmd(c, **p):
    C.append({"command": c, "params": p})


def profile(name, offset):
    cmd("sketch.create", plane="YZ", offset=offset, name=name)
    cmd("sketch.arc.center_point", center=[0, 0], start=[JY, JZ], end=[-JY, JZ])
    cmd("sketch.line", points=[[-JY, JZ], [-7.5, -18], [7.5, -18], [JY, JZ]], infer=False)
    cmd("sketch.finish")


# ---------------- Rohr ----------------
cmd("parameters.add", name="ri", expression="12.7 mm")
cmd("parameters.add", name="Lt", expression="80.1 mm")
profile("ProfilSkizze", -2)
cmd("solid.extrude", distance=82.1, name="Rohrkoerper", body_name="Rohr")
cmd("solid.fillet", edges=[[40, JY, JZ], [40, -JY, JZ]], radius=2.5, name="Uebergang_R2_5")
cmd("solid.fillet", edges=[[40, 7.5, -18], [40, -7.5, -18]], radius=1.2, name="Sockelkante_R1_2")
cmd("solid.fillet", edges=[[-2, 0, 14.7]], radius=1.2, name="Stirnkante_RJ45")
cmd("solid.chamfer", edges=[[80.1, 0, 14.7]], distance=0.5, name="Fase_Deckelseite")
cmd("solid.cylinder", radius="ri", height=81, base=[0, 0, 0], axis="X", operation="cut",
    targets=["Rohr"], name="Innenraum")
cmd("solid.box", length=3.1, width=16.6, height=13.7, center=[-1.45, 0, 1.75], operation="cut",
    targets=["Rohr"], name="RJ45_Ausschnitt")
# PCB guide rails (slot 1.9 mm high at z -6.75 ... -4.85)
cmd("sketch.create", plane="YZ", name="SchieneSkizze")
cmd("sketch.line", points=[[9.65, -3.5], [13, -3.5], [11.5, -8.1], [9.65, -8.1], [9.65, -6.75],
                           [10.35, -6.75], [10.35, -4.85], [9.65, -4.85]], closed=True, infer=False)
cmd("sketch.finish")
cmd("solid.extrude", distance="Lt", operation="join", targets=["Rohr"], name="Schiene_R")
cmd("solid.mirror", features=["Schiene_R"], plane="XZ", combine=True, name="Schiene_L")
# 4 cable tie tunnels 8 x 2.1
cmd("solid.box", length=8, width=24, height=2.1, corner=[2, -12, -17], operation="cut",
    targets=["Rohr"], name="Kabelbinder")
cmd("solid.pattern.rectangular", features=["Kabelbinder"], dir1=[1, 0, 0], count1=4, spacing1=22,
    name="Kabelbinder_4x")
# hidden snap groove inside (r 12.6 ... 13.6, 45 deg release flank)
cmd("sketch.create", plane="XZ", name="NutSkizze")
cmd("sketch.line", points=[[71.7, -12.6], [71.7, -13.6], [73.5, -13.6], [74.5, -12.6]],
    closed=True, infer=False)
cmd("sketch.finish")
cmd("solid.revolve", axis="X", operation="cut", targets=["Rohr"], name="Rastnut")
# status LED window above D11, countersunk (taper)
cmd("sketch.create", plane="XY", offset=16, name="LEDSkizze")
cmd("sketch.circle.center", center=[63.03, -3.56], diameter=5.34)
cmd("sketch.finish")
cmd("solid.extrude", distance=6, direction="negative", taper="-21 deg", operation="cut",
    targets=["Rohr"], name="LED_Fenster")
# logo, 0.6 mm radial deboss
cmd("sketch.create", plane="XY", offset=15, name="LogoSkizze")
cmd("sketch.text", text="VAT", at=[53, -3], height=6, font="Arial", bold=True, align="center")
cmd("sketch.finish")
cmd("solid.extrude", distance=6, direction="negative", operation="new", name="LogoPrisma",
    body_name="LogoTool")
LOGO = ["LogoTool", "LogoTool (2)", "LogoTool (3)"]
cmd("solid.cylinder", radius=14.1, height=30, base=[40, 0, 0], axis="X", operation="cut",
    targets=LOGO, name="LogoTiefe")
cmd("solid.combine", target="Rohr", tools=LOGO, operation="cut")
# vent slots over the PoE module, chamfered by a tapered cut (2.0 inside, ~3.0 outside)
cmd("sketch.create", plane="XY", offset=16, name="LuftSkizze")
cmd("sketch.slot.overall", p0=[17.2, 0], p1=[44.8, 0], width=3.64)
cmd("sketch.finish")
cmd("solid.extrude", distance=6, direction="negative", taper="-13.8 deg", operation="cut",
    targets=["Rohr"], name="Luftschlitz")
cmd("solid.pattern.circular", features=["Luftschlitz"], axis="X", count=9, angle="200 deg",
    alignment="center", name="Luftschlitze")

# ---------------- Deckel ----------------
profile("DeckelSkizze", "Lt")
cmd("solid.extrude", distance=2, operation="new", name="Deckelplatte", body_name="Deckel")
cmd("solid.fillet", edges=[[81.1, JY, JZ], [81.1, -JY, JZ]], radius=2.5, body="Deckel",
    name="Deckel_Uebergang")
cmd("solid.fillet", edges=[[81.1, 7.5, -18], [81.1, -7.5, -18]], radius=1.2, body="Deckel",
    name="Deckel_Sockelkante")
cmd("solid.fillet", edges=[[82.1, 0, 14.7]], radius=1.2, body="Deckel", name="Deckel_Aussenkante")
cmd("solid.box", length=3, width=15.6, height=7.4, center=[81.1, 0, -1.3], operation="cut",
    targets=["Deckel"], name="USB_Ausschnitt")
cmd("sketch.create", plane="YZ", offset=82.1, name="RahmenSkizze")
cmd("sketch.rectangle.rounded", p0=[-9.3, -6.5], p1=[9.3, 3.9], radius=1.5)
cmd("sketch.finish")
cmd("solid.extrude", distance=0.6, direction="negative", operation="cut", targets=["Deckel"],
    name="USB_Rahmen")
cmd("solid.box", length=8.2, width=6, height=1.2, corner=[71.9, -3, 11], operation="join",
    targets=["Deckel"], name="Rastarm")
cmd("sketch.create", plane="XZ", name="HakenSkizze")
cmd("sketch.line", points=[[71.9, -12.0], [73.0, -13.2], [73.3, -13.2], [74.3, -12.0]],
    closed=True, infer=False)
cmd("sketch.finish")
cmd("solid.extrude", distance=5, direction="symmetric", operation="join", targets=["Deckel"],
    name="Rasthaken")
cmd("solid.pattern.circular", features=["Rastarm", "Rasthaken"], axis="X", count=3,
    angle="180 deg", alignment="center", name="Rastarme_3x")
cmd("solid.box", length=6.1, width=6, height=1.2, corner=[74, -3, -12.2], operation="join",
    targets=["Deckel"], name="Fuehrungslasche")
cmd("solid.box", length=0.7, width=7, height=3.5, corner=[80.1, -3.5, -18.5], operation="cut",
    targets=["Deckel"], name="Hebelkerbe")

# ---------------- PCB dummies (fit check only, not exported for printing) ----------------
for n, l, w, h, c in (("Dummy_PCB", 80, 20, 1.6, [0, -10, -6.6]),
                      ("Dummy_J1", 21.9, 16.1, 13.3, [-0.6, -8.05, -5]),
                      ("Dummy_J2", 13.9, 15.3, 7, [66.15, -7.65, -5]),
                      ("Dummy_U1", 21.21, 13.92, 8, [23.9, -6.96, -5]),
                      ("Dummy_J1_Pins", 19, 14, 3, [1, -7, -9.6]),
                      ("Dummy_Bottom", 60, 14, 2.6, [20, -7, -9.2])):
    cmd("solid.box", length=l, width=w, height=h, corner=c, operation="new", body_name=n, name=n)

# ---------------- print layout for Bambu A1 (copies, on the bed) ----------------
cmd("solid.move", bodies=["Rohr"], axis=[0, 1, 0], angle="-90 deg", copy=True)
cmd("body.rename", body="Rohr (2)", name="Druck_Rohr")
cmd("solid.move", bodies=["Druck_Rohr"], translate=[108, 128, 2])
cmd("solid.move", bodies=["Deckel"], axis=[0, 1, 0], angle="90 deg", copy=True)
cmd("body.rename", body="Deckel (2)", name="Druck_Deckel")
cmd("solid.move", bodies=["Druck_Deckel"], translate=[155, 128, 82.1])

# ---------------- exports ----------------
def exp(name, bodies, **kw):
    cmd("file.export", path=OUT + "\\" + name, bodies=bodies, **kw)


exp("A1_gehaeuse_druckplatte.3mf", ["Druck_Rohr", "Druck_Deckel"], quality="fine")
exp("A1_rohr_stehend.stl", ["Druck_Rohr"], quality="fine")
exp("A1_deckel_flach.stl", ["Druck_Deckel"], quality="fine")
exp("rohr.stl", ["Rohr"])
exp("deckel.stl", ["Deckel"])
exp("gehaeuse.3mf", ["Rohr", "Deckel"])
exp("gehaeuse.step", ["Rohr", "Deckel"])

json.dump({"commands": C}, open(SCRIPT, "w", encoding="utf-8"), indent=1)
print(len(C), "commands")
