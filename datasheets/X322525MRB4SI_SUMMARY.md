# X322525MRB4SI — YXC 25 MHz Quarz, 3.2 x 2.5 mm (YSX321SL-Familie)

Quelle: YXC YSX321SL Datenblatt (1 S.), `X322525MRB4SI.pdf` (visuell gelesen). **WICHTIG: Das LCSC-Datenblatt ist das generische YSX321SL-Blatt; es nennt CL "10 pF, 20 pF, or specify". 18 pF (sourced_bom/JLC-Attribut) ist im Datenblatt NICHT bestaetigt -> UNVERIFIZIERT.**

| Spec | Value |
|------|-------|
| Frequenz-Bereich | 8-64 MHz, AT-Fundamental |
| Toleranz | +-10 ppm / +-20 ppm (nach Bestellcode), Temperatur +-20 ppm (-40..+85 C) |
| C0 | max 3 pF |
| Drive Level | 10-200 uW (100 uW typ) |
| ESR | 16-31 MHz: max 50 Ohm |
| Alterung | +-3 ppm/Jahr |
| Hoehe | 0.7 +-0.1 mm |
| Betrieb/Lagerung | -40..+85 C / -55..+125 C |

## Pinout (4 Pads)
| Pad | Funktion |
|-----|----------|
| 1 | Kristall (unten links) |
| 2 | GND (unten rechts) |
| 3 | Kristall (oben rechts) |
| 4 | GND (oben links) |
Kristall-Anschluesse diagonal (Pad 1 und 3), 2 und 4 GND. Land Pattern: Pads 1.4 x 1.2 mm, x-Luecke 0.8, y-Luecke 0.5 (-> y-Mitte/Mitte 1.7 mm).

## Notes
- W5500 verlangt CL = 18 pF (W55RP20-DS). Mit C27/C28 27 pF C0G: CL = 13.5 + Stray ca. 3-4 pF = 17-18 pF -> passt, falls das Teil wirklich 18 pF hat. Bei Bestellung Typenschild/Hersteller-Bestaetigung pruefen.
