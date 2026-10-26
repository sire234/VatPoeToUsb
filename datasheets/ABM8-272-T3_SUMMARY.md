# Abracon ABM8-272-T3 – Quarz 12 MHz (Y1)

Quelle: `ABM8-272-T3.pdf` (Abracon Drawing #456603, Ausgabe 16.11.2023, Rev. IR; LCSC C20625731).

| Parameter | Wert |
|---|---|
| Frequenz / Mode | 12,000 MHz, Grundton (AT) |
| Toleranz @25 °C / Stabilität −40…+85 °C | ±30 ppm / ±30 ppm |
| ESR (R1) | **max. 50 Ω** |
| Lastkapazität CL | **10 pF** |
| Shunt-Kapazität C0 | max. 3,0 pF |
| Drive Level | typ. 10 µW, max. 200 µW |
| Alterung | ±5 ppm (1. Jahr) |
| Gehäuse | 3,2 × 2,5 × 0,8 mm Keramik, 4 Pads; Land Pattern 1,4 × 1,1 mm, Raster 2,2 × 1,6 mm |
| Pinbelegung | Quarz zwischen #1 und #3 (diagonal), #2/#4 = Gehäuse → GND; Fase kann an #1, #3 oder #4 sein (elektrisch ohne Bedeutung) |
| MSL | 1 (hermetisch) |
| Verpackung | T3 = 3 000 Stk/Rolle |

Verwendung (Rev 4e, H1): exakt wie Raspberry-Pi-Referenz („Hardware design with RP2040" / Pico): ABM8-272-T3, 2 × 15 pF C0G (C25/C26, FH 0402CG150J500NT C1548) → C_L ≈ 15/2 + ≈ 3 pF Streu ≈ 10,5 pF, 1 kΩ Serien-R an XOUT (R37). KiCad: Symbol `Device:Crystal_GND24`, Footprint `Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm` (1/3 Quarz, 2/4 GND) – wie im offiziellen RP2040-Minimal-Design.

JLC (2026-10-23, API live): C20625731 Extended, Stock 4 388, 0,5315 USD @10.
