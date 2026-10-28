# Gehäuse eckig Rev 1 – PoE-USB-HID-Bridge (Variante 2, 2026-10-26)

Zweiteiliges, eckiges Gehäuse: **Wanne** (unten, mit Sockel und Kabelbinder-Tunneln) und **Deckel** (oben, rastet ein).
Der RJ45-Stecker ragt oben ≈ 1,5 mm aus dem Deckel; alles andere ist verdeckt.
Aufgebaut mit SolidCraft headless aus `make_script.py` → `poe_usb_gehaeuse_eckig.solidcraft`.
Koordinaten: x längs (0 = RJ45-Platinenkante), y = −(KiCad-y − 10), z = 0 an der PCB-Unterseite.

## Druckdateien für Bambu Lab A1
- **`A1_eckig_druckplatte.3mf`**: Wanne (Boden unten) und Deckel (kopfüber, Oberseite unten) nebeneinander auf der Platte.
- Einzeln: `A1_wanne.stl`, `A1_deckel_kopfueber.stl`; Montagelage: `gehaeuse_eckig.3mf`, `gehaeuse_eckig.step`.
- PETG, 0,2 mm Schicht, 3 Wände, 15 % Füllung, **keine Stützen** (Kabelbinder-Tunnel überbrücken 8 mm), kein Brim nötig.
- Gewicht: Wanne ≈ 13,7 g, Deckel ≈ 6,9 g.

## Masse
| Teil | Wert |
|---|---|
| Aussen | 84,1 × 24,4 × 22,1 mm (z −8,7 … 13,4), RJ45 bis z 14,9; Ecken R 2, Deckel-Oberkante R 1,5, Wand 2 mm |
| Trennfuge | z 4,0 (2,4 mm über der Platinenoberseite) – als bewusste Linie rundum |
| Wanne | Boden z −5,4 … −3,4; Auflageleisten für die Platine an beiden Längsseiten (|y| ≥ 9,6, frei von den Unterseiten-Bauteilen); Front unterhalb der Platine geschlossen (Anschlag), RJ45 von oben eingelegt |
| Sockel | 80 × 18 × 3,4 mm, Fase 0,8, **4 Kabelbinder-Tunnel 8 × 2,1** quer bei x 2, 24, 46, 68 |
| Deckel | Innenhöhe bis z 11,4 (PoE-Modul max. 10,8); RJ45-Aussparung 24,6 × 16,7 durch Front und Dach; USB-Ausschnitt 15,6 × 7,4 in Stirnwand (Deckel + Wanne) |
| Rastung | 4 Rastlippen (je 14 mm, 0,8 mm dick) innen an den Längswänden, Nocken greifen 0,35 mm in die Wand (Einführschräge unten 45°, Haltekante oben 30° zur Waagrechten) in je eine Rasttasche der Wanne (z 2,45 … 3,2, 0,55 mm tief, nur 0,15 mm länger als die Lippe pro Ende); die Taschenoberkante liegt auf der Haltekante, der eingerastete Deckel wird nach unten gezogen – die Taschenenden sind der Längsanschlag, der Deckel kann nicht mehr längs verschoben werden; die Lippen drücken die Platine zugleich auf die Auflageleisten |
| Lüftung | Dach: 5 Querschlitze über dem PoE-Modul (angefast 2 → 3 mm); Seiten: 2 Schlitze je Seite im Deckel + 1 Zuluftschlitz je Seite in der Wanne unter der Platine (Kamineffekt) |
| Status-LED | Bohrung im Dach über D11, angesenkt Ø 2,4 → 4 |
| Logo | „VAT“ 5,5 mm, 0,6 mm tief in der Seitenwand (+y) – Platzhalter bis zum echten SVG |

## Montage / Öffnen
Platine von oben in die Wanne legen (RJ45 vorne, USB hinten), Deckel aufsetzen und andrücken, bis alle vier Lippen einrasten.
Öffnen: Deckel an der USB-Seite seitlich auseinanderziehen bzw. mit einem flachen Schraubendreher in der Trennfuge abhebeln.

## Prüfung
Interferenzprüfung Wanne/Deckel gegen Dummy-Körper (PCB, J1, J2, U1 mit 9,2 mm, J1-Pins, Unterseiten-Bauteile 2,6 mm): 0 Kollisionen, alle Paare vollständig geprüft.

## Offen
- Rastkraft nach dem Druck prüfen. Die Rastung wurde verstärkt: vorher 0,2 mm Hinterschnitt, 45° beidseitig. Ist sie jetzt zu fest, die Nockenspitze in `make_script.py` von 10,55 auf 10,45 reduzieren. Ist sie immer noch zu schwach, auf 10,65 erhöhen und die Tasche entsprechend tiefer machen.
- Echtes VAT-Logo als SVG.
