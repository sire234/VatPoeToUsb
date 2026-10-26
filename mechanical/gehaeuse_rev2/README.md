# Gehäuse Rev 2 – PoE-USB-HID-Bridge (2026-10-26)

Überarbeitung von `../gehaeuse_rev1` mit schönerer Form, unsichtbarer Rastung und aufgewertetem Deckel.
Aufgebaut mit SolidCraft (`poe_usb_gehaeuse_v2.solidcraft`; headless aus dem Skript, siehe unten).
Koordinaten: x = Rohrachse (0 = RJ45-Platinenkante, 80 = USB-Kante), z = Höhe (0 = Rohrachse), y = −(KiCad-y − 10).

## Druckdateien für Bambu Lab A1
- **`A1_gehaeuse_druckplatte.3mf`**: beide Teile in Druckorientierung auf der Platte (Rohr stehend, RJ45-Seite unten; Deckel flach, Aussenseite unten, Rastarme oben). In Bambu Studio öffnen, Filament wählen, slicen.
- Einzeln: `A1_rohr_stehend.stl`, `A1_deckel_flach.stl`. Montagelage: `rohr.stl`, `deckel.stl`, `gehaeuse.3mf`, `gehaeuse.step`.
- Einstellungen: PETG, 0,2 mm Schicht, 3 Wandlinien, 15 % Füllung, **keine Stützen**, **Brim 5 mm für das Rohr**, Naht auf „hinten/ausgerichtet“ auf die Sockelseite legen.
- Gewicht: Rohr ≈ 22,7 g, Deckel ≈ 1,8 g.

## Änderungen gegenüber Rev 1
| Bereich | Rev 2 |
|---|---|
| Profil | Rohr (Aussen-Ø 29,4) mit Sockel als **ein Profil**: Sockelflanken 15° nach aussen, Hohlkehle R 2,5 ins Rohr, Sockelkanten R 1,2, Auflage 15 mm breit bei z −18 |
| Kanten | RJ45-Stirnkante R 1,2, Rohrende Deckelseite Fase 0,5, Deckel-Aussenkante R 1,2 |
| Deckel | gleiches Profil wie das Rohr (schliesst mit dem Sockel ab), 2,0 mm dick; **vertiefter Rahmen** 18,6 × 10,4 (R 1,5, 0,6 tief) um den USB-Ausschnitt 15,6 × 7,4 → USB-Buchse liegt wie bisher ≈ 1,4–1,6 mm hinter der Fläche |
| Rastung | **unsichtbar**: umlaufende Innennut im Rohr (x 71,7 … 74,5, r bis 13,6, 45°-Flanke), 3 Rastarme mit 45°-Haken (5 mm breit, 0,5 mm Eingriff); keine Fenster mehr aussen |
| Öffnen | **Hebelkerbe** unten zwischen Deckel und Sockel (7 × 0,7 mm): kleinen Schraubendreher einsetzen und den Deckel abhebeln |
| Lüftung | 9 Schlitze über dem PoE-Modul, durch konischen Schnitt **angefast** (innen 2,0, aussen ≈ 3,0 mm) |
| Status-LED | Bohrung über D11 **angesenkt** (innen Ø 2,4, aussen Ø 4) |
| Kabelbinder | 4 Tunnel 8 × 2,1 quer durch den Sockel (x 2 … 10, 24 … 32, 46 … 54, 68 … 76) |
| Logo | „VAT“ (Arial Bold, 6 mm) 0,6 mm radial vertieft, Platzhalter bis zum echten SVG |

Unverändert: Innen-Ø 25,4, RJ45-Ausschnitt 16,6 × 13,7, Platinenführung (Nut 1,9 mm), Führungslasche unten am Deckel.

## Prüfung
SolidCraft-Interferenzprüfung Rohr, Deckel und Dummy-Körper (PCB, J1, J2, U1, J1-Pins, Unterseiten-Bauteile 2,6 mm): 0 Kollisionen, alle Paare vollständig geprüft.

## Hinweise
- Die Lichtleiter-Idee für die LED im Deckel wurde nicht umgesetzt: D11 sitzt 17 mm hinter dem Deckel, ein gedruckter Lichtleiter bräuchte transparentes Material. Stattdessen ist die LED-Bohrung im Rohr angesenkt. Option: einen Ø-3-mm-Acrylstab in die Bohrung kleben.
- Rastung (0,5 mm Eingriff, 45°) und Nut nach dem ersten Druck prüfen; zu fest → Hakenhöhe in `HakenSkizze` verkleinern, zu lose → Nut-Radius 13,6 → 13,8.

## Neu aufbauen
Das Modell entsteht aus `make_script.py` (Kopie hier im Ordner): `python make_script.py <ausgabeordner> script.json`, dann
`solidcraft-cli run script.json --save poe_usb_gehaeuse_v2.solidcraft` (≈ 3 min, die Lüftungsschlitz-Musterung dauert am längsten).
