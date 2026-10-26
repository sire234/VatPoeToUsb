# BZT52C6V2 — BORN Zener-Diode 6,2 V, 500 mW, SOD-123 (D12)

Quelle: BORN BZT52Cxx Datenblatt (Rev. 2022-Jan-1-A), `BZT52C6V2.pdf` (LCSC C271260, Text gelesen 2026-10-23; Tabellenspalten im Text verschoben, Werte über die Zeile 6,2/5,8/6,6 zugeordnet).

| Spec | Wert |
|------|------|
| V_Z @ I_ZT 5 mA | 6,2 V nom (5,8 … 6,6 V) |
| Z_ZT | max 10 Ω |
| I_R | max 3 µA @ 4 V |
| P_D | 500 mW |
| V_F | 0,9 V @ 10 mA |
| T_J / Lagerung | 150 °C / −55 … +150 °C |

## Pinout
Pin 1 = Kathode (Ring) → **+5V**, Pin 2 = Anode → GND (KiCad `D_Zener`, `Diode_SMD:D_SOD-123`).

## Hinweise
- OVP-Klemme an +5V: sperrt sicher bis 5,8 V (Modul max 5,25 V, mit R9 = 0 Ω max 5,65 V).
- 500 mW → nur Spitzenbegrenzung, keine Dauerklemmung.
