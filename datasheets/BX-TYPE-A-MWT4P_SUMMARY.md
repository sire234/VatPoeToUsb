# BX-TYPE-A-MWT4P — Bossie USB-A Buchse, horizontal SMD (right angle)

Quelle: Bossie-Zeichnung (1 Seite, Vektor) `BX-TYPE-A-MWT4P.pdf`, als PNG gelesen. Pinout/Hoehe aus Zeichnung; Land-Pattern-Masse teils UNVERIFIZIERT (Beschriftung klein).

| Spec | Value |
|------|-------|
| Belastbarkeit | 1.5 A je Kontakt, 30 V DC, Kontaktwiderstand <= 30 mOhm, 500 V AC Dielektrikum |
| Steckkraft | max 3.57 kgf / min 1.02 kgf Zug |
| Aussenmasse | Breite 15.20 +-0.30 mm, **Hoehe 7.0 +-0.15 mm** (5.75 +-0.10 Teilmass), Tiefe 13.80 +-0.15 mm; Rastnase 1.50 mm |
| Befestigung | 2 Positionierstifte Ø1.2 / Ø1.40 (5.0 mm Abstand) + 2 Schirm-SMD-Pads 5.0 mm breit |
| Kontakte | Au im Steckbereich, Sn an Loetpads, Gehaeuse C2680 vernickelt |

## Pinout (Pads, Draufsicht PCB-Seite)
| Pad | Funktion |
|-----|----------|
| VBUS | USB-Pin 1 (+5 V) |
| R- (= D-) | USB-Pin 2 |
| R+ (= D+) | USB-Pin 3 |
| GND | USB-Pin 4 |
| Shield | 2 grosse Schirm-Pads/Laschen |
Padreihenfolge in der Zeichnung von oben: GND, R+ (D+), R- (D-), VBUS (jeweils 2.0 mm Pitch zwischen D+/D-; Gesamtabstand GND-VBUS 7.0 mm; Pad-Laenge 4.70 mm (GND) bzw. 3.00 mm (VBUS); Schirm-Pads 5.0 x 2.5 mm; Gesamt-Land 14.90 mm). Diese Masse bitte beim Footprint-Bau gegen die Zeichnung (S.1 unten Mitte) nochmals messen.

## Notes
- Hoehe 7.0 mm (BOM "typ. 6.5, V <= 7.0" -> 7.15 mm max ansetzen).
- Schirm nur SMD-Pads: mechanische Haltbarkeit (kein THT) bei haeufigem Stecken beschraenkt.
