# C1812X472K202T — IHHEC (Holy Stone) MLCC 4,7 nF 2 kV X7R, 1812 (C24)

Quelle: Hochvolt-NP0/X7R-Katalog, `C1812X472K202T.pdf` (LCSC C106172, Text gelesen 2026-10-23).

| Spec | Wert |
|------|------|
| Kapazität / Toleranz | 4,7 nF (472) ±10 % (K) |
| Nennspannung | 2000 V DC (Code 202) |
| Dielektrikum | X7R, D.F. ≤ 2,5 % |
| Prüfspannung | 120 % U_R (U_R ≥ 1000 V) |
| Bauform | 1812 |

## Pinout
Unpolarisiert; SHIELD_RJ45 → GND (parallel zu R7 1 MΩ).

## Hinweise
- **Kein Y-zertifizierter Kondensator.** Er liegt nicht über der PoE-Isolationsgrenze, aber in Serie mit dem J1-internen 1 nF/2 kV (Bob-Smith → Schirm) – siehe design_risks R-ISO-7, Hipot am Muster.
