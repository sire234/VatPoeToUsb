# TPS2553DBVR — TI Precision adjustable current-limited power switch, 1.5 A, EN active high

Quelle: TI SLVS841F (Aug 2016), `TPS2553DBVR.pdf` (ti.com/lit/ds/symlink/tps2553.pdf). VERIFIZIERT.

| Spec | Value |
|------|-------|
| Package | SOT-23-6 (DBV) 2.90 x 1.60 mm |
| VIN | 2.5-6.5 V; abs. max -0.3..7 V an IN/OUT/EN/ILIM/FAULT |
| R_ON | 85 mOhm (DBV) |
| Dauerstrom | bis 1.5 A; Strombegrenzung 75 mA ... 1.7 A einstellbar |
| R_ILIM Bereich | 15 k ... 232 k (1 %) ; ILIM direkt an IN = 75 mA |
| EN-Schwelle | 0.66-1.375 V; TPS2553 = **aktiv HIGH** (TPS2552 = aktiv low) |
| FAULT | Open-Drain, aktiv low bei Ueberstrom/Uebertemperatur/Rueckwaertsspannung |
| Reaktion Kurzschluss | ca. 2 us typ; Constant-Current-Modus (TPS2553; -1 = Latch-off) |
| Temperatur | Tj -40..125 C |

## Formeln (Gl. 1, R_ILIM in kOhm, I in mA)
- I_OS,nom = 23950 / R^0.977
- I_OS,min = 25230 / R^1.016 ... (Datenblatt: min = 25230/R^1.016; max = 22980/R^0.94)
**R_ILIM = R25 = 44.2 k (gueltig seit Rev 2):** nom = 23950/44.2^0.977 = ca. **590 mA**; min ca. **537 mA**; max ca. 653 mA (inkl. R +-1 %: 532-659 mA). Ein 500-mA-Geraet wird nie begrenzt, der USB-Fehlerfall bleibt im Modul-Budget (Auslegung `architecture/skeleton_bom.md`). Kontrolle der Formel: 49.9 k -> Datenblatt 520 mA typ., Formel 525 mA.
*Historisch (Rev 1):* 40.2 k -> nom 649 / min 592 / max 714 mA, verworfen.

## Pinout SOT-23-6 (DBV, Top View)
| Pin | Name | Function |
|-----|------|----------|
| 1 | IN | Eingang, 1 uF (BOM: 100 nF empfohlen auch am Eingang) |
| 2 | GND | Masse |
| 3 | EN | Enable, aktiv high (TPS2553) |
| 4 | FAULT | Open-Drain, aktiv low |
| 5 | ILIM | R_ILIM nach GND (nah am Pin, kurze Leitung) |
| 6 | OUT | Ausgang (USB VBUS) |

## Notes
- Typische Applikation: Datenblatt S.1 (Fig. 1, R_ILIM 20 k, 120 uF am Ausgang fuer USB), Layout-Hinweise nach Section 10.
- ILIM-Leitung kurz, kein Rauschen koppeln.
- Reverse-Voltage-Comparator schaltet ab, wenn OUT > IN.
