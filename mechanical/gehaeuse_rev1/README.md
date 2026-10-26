# Gehäuse Rev 1 – PoE-USB-HID-Bridge (Vorschlag, 2026-10-26)

Erstellt mit SolidCraft (`poe_usb_gehaeuse.solidcraft`). Druckdaten: `rohr.stl`, `deckel.stl`, `gehaeuse.3mf`; CAD-Austausch: `gehaeuse.step`.
Koordinaten: x = Rohrachse (0 = RJ45-Platinenkante, 80 = USB-Kante), z = Höhe (0 = Rohrachse), y = −(KiCad-y − 10).

| Teil | Mass |
|---|---|
| Rohr | Innen-Ø 25,4, Wand 2,0 (Aussen-Ø 29,4), Länge 82,1 (x −2 … 80,1), Boden 2 mm auf der RJ45-Seite |
| RJ45-Ausschnitt | 16,6 × 13,7 (y ±8,3, z −5,1 … 8,6); die Platinenkante liegt an der Stirnwand an |
| Platinenführung | 2 Schienen über die ganze Länge, Nut 1,9 hoch (PCB 1,6) bei z −6,75 … −4,85, Nutgrund y ±10,35, Auflage 0,35–0,7 mm |
| Lüftung PoE | 9 Langlöcher 2 × 26 mm (x 18 … 44) über dem Modul U1, im Abstand von 25° über ±100° |
| Status-LED | Bohrung Ø 2,5 über D11 (x 63,0 / y −3,56) |
| Logo | „VAT“ (Arial Bold, 6 mm hoch) 0,6 mm radial vertieft auf der Oberseite, x ≈ 46 … 60 – Platzhalter |
| Kabelbinder | durchgehender Sockel unten über die ganze Rohrlänge (x −2 … 80,1, 13 breit, flache Auflage z −18), **4 Tunnel 8 × 2,1** quer (durch die ganze Sockelbreite) bei x 2 … 10, 24 … 32, 46 … 54, 68 … 76 (Raster 22 mm; Kabelbinder bis ≈ 7,5 mm breit, 1,8 mm dick) |
| Deckel | Platte 1,6 mm, USB-Ausschnitt 15,6 × 7,4 (z −5,0 … 2,4), 3 Rastarme (oben, links, rechts) 8,3 × 6 × 1,2 mit Haken 1,1 mm, rasten in Fenster 2,1 × 6,8 im Rohr (x 71,5 … 73,6); Führungslasche unten |

Geprüft (SolidCraft-Interferenzprüfung): Rohr/Deckel und Dummy-Körper für PCB, J1, J2, U1, J1-Pins und die Bauteile der Unterseite (2,6 mm) ohne Kollision.

## Druckdateien für Bambu Lab A1
- **`A1_gehaeuse_druckplatte.3mf`**: beide Teile bereits in Druckorientierung auf der Platte (Rohr stehend, RJ45-Seite unten; Deckel flach, Aussenseite unten, Rastarme oben), Mitte bei ≈ (128/128), 14 mm Abstand. In Bambu Studio öffnen, Filament wählen, slicen.
- Einzeln: `A1_rohr_stehend.stl`, `A1_deckel_flach.stl` (gleiche Orientierung).
- Einstellungen: PETG (Bambu PETG Basic/HF), 0,2 mm Schicht, 3 Wandlinien, 15 % Füllung, **keine Stützen**, **Brim 5 mm für das Rohr** (82 mm hoch auf kleiner Fläche).

## Druckhinweise
- Rohr **stehend** drucken (RJ45-Stirnseite auf dem Bett): Schienen, Schlitze und Fenster ohne Stützmaterial; der USB-seitige Fuss hat eine 45°-Schräge.
- Deckel mit der Aussenseite auf dem Bett, Rastarme nach oben.
- Material: **PETG** empfohlen (Rastarme mit ≈ 1,6 % Biegedehnung, Wärme der PoE-Seite); PLA geht, die Arme sind dann spröder.
- Öffnen: Haken durch die drei Fenster mit einem kleinen Schraubendreher eindrücken.

## Offene Punkte
- Das echte VAT-Logo als SVG nachliefern (`sketch.insert_svg` statt Text).
- Die USB-Buchse liegt ≈ 1,5 mm hinter der Deckelfläche; die Steckertülle muss in den Ausschnitt 15,6 × 7,4 passen, sonst den Deckel im Bereich der Öffnung dünner machen.
- Die Passung der Führungsnut (1,9 mm) und der Rastung nach dem ersten Druck prüfen.
