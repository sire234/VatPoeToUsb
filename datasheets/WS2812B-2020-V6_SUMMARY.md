# WS2812B-2020-V6 — Worldsemi adressierbare RGB-LED, 2,0 × 2,0 mm (D11)

Quelle: Worldsemi WS2812B-2020-V6 Datenblatt (10 S.), `WS2812B-2020-V6.pdf` (LCSC C52917434, Text gelesen 2026-10-23).

| Spec | Wert |
|------|------|
| Versorgung VDD | +3,3 … +5,3 V |
| VIH (DIN) | min 0,55 · VDD (bei 3,3 V → 1,82 V) |
| VIL | max 0,3 · VDD (Tabelle unscharf gedruckt) |
| Strom je Kanal | 12 mA (weiss voll 36 mA) |
| Ruhestrom | < 1 µA (alle Kanäle aus) |
| Datenrate | 800 kbit/s, Einzeldraht-RZ, 24 bit **GRB**, MSB zuerst, Reset > 280 µs |
| Betriebstemperatur | −40 … +85 °C (Tabellenreihenfolge; Lagerung lose −40 … +105, auf Rolle −40 … +70) |
| Abmessungen | 2,0 × 2,0 × 0,84 mm, PLCC-4 |
| MSL | **5a** (J-STD-020) → vor Reflow backen |
| Abblock-C | „Cn typisch 100 nF" direkt an VDD (S. 6) → C64 |

## Pinout (DS S. 2)
| Pin | Name | Projekt-Netz |
|-----|------|--------------|
| 1 | DO | NC (Einzel-LED) |
| 2 | GND | GND |
| 3 | DI | LED_DIN_R (über R38 330 Ω von GPIO28) |
| 4 | VDD | +3V3 (Rev 4d) |

## Hinweise
- KiCad `LED_SMD:LED_WS2812B-2020_PLCC4_2.0x2.0mm` entspricht dem Pinout, ist aber 180° zur DS-Draufsicht gedreht → Polaritätsmarke im Layout prüfen.
- Bei VDD = 3,3 V liegt die LED an der Untergrenze: Blau/Grün ggf. dunkler (am Muster prüfen). Firmware-Helligkeit ≤ 30 %.
