# X322512MSB4SI — YXC 12 MHz Quarz, 3,2 × 2,5 mm (Y1)

Quelle: Das LCSC-Datenblatt zu C9002 ist **byte-identisch** mit dem generischen YXC-YSX321SL-Familienblatt `X322525MRB4SI.pdf` (gleiche MD5, 2026-10-23 geprüft) → keine eigene PDF-Datei abgelegt. Daten siehe `X322525MRB4SI_SUMMARY.md`.

| Spec | Wert |
|------|------|
| Frequenz | 12 MHz, AT-Grundton |
| C_L | 20 pF (Bestellcode „S"; JLC-Attribut – im Familienblatt nur „10 pF, 20 pF or specify") |
| Toleranz | ±10 ppm (JLC-Attribut) |
| Höhe | 0,7 ± 0,1 mm |
| Temperatur | −40 … +85 °C |

## Pinout
1 / 3 = Quarz (diagonal), 2 / 4 = GND. Pin 1 → XTAL12_XIN, Pin 3 → XTAL12_XO_R (über R37 1 kΩ an XOUT).

## Hinweise
- Lasten C25/C26 33 pF C0G → C_L ≈ 16,5 + 3 pF Streu ≈ 19,5 pF.
- Anschwingen bei Kälte/Wärme am Muster prüfen (design_risks R-TIM-1); FW `PICO_XOSC_STARTUP_DELAY_MULTIPLIER=64`.
- LCSC-Bestand am 2026-10-23: 4 065 Stk (Basic) – deutlich weniger als 2026-10-21 (206 k).
