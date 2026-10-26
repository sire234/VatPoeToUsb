# MB6S — MDD (MicroDiode) 600 V 1 A Glass-Passivated Bridge Rectifier, MBS (TO-269AA)

Quelle: MDD MB1S-MB10S Rev. 2024A2, `MB6S.pdf`; Seite 1 als PNG gelesen. Pinzuordnung VERIFIZIERT (nur fuer MDD-Teil C2487).

| Spec | Value |
|------|-------|
| Package | MBS / TO-269AA, Body ca. 4.9 x 4.0 mm, Lead-Spanne 7.0 mm max; Hoehe 2.3-2.7 mm (BOM 2.6 ok, max 2.7) |
| V_RRM / V_RMS | 600 V / 420 V |
| I_F(AV) | 1.0 A (Tc = 115 C); I_FSM 35 A |
| V_F | 1.1 V @ 1 A je Zweig (Zweige: 2 in Serie -> ca. 1.1 V Verlust je Brueckenpfad ... 2 Dioden = ca. 1.0-1.1 V je Diode) |
| I_R | 5 uA (25 C) / 40 uA (125 C) |
| R_thJA | 85 C/W (mit grossem Kupfer), R_thJC 25 C/W |
| Tj | -55..+150 C |

## Pinout (Schaltbild des Datenblatts, MBS)
| Pin | Funktion |
|-----|----------|
| 1 | **+** (DC-Ausgang, Plus) |
| 2 | **-** (DC-Ausgang, Minus) |
| 3 | ~ (AC) |
| 4 | ~ (AC) |
Physisch: + und - liegen am selben Gehaeuse-Ende (Pins 1,2), die beiden ~ am anderen (3,4). KiCad `Package_TO_SOT_SMD:TO-269AA` hat Pads 1 (-3.075,-1.27), 2 (-3.075,+1.27), 3 (+3.075,+1.27), 4 (+3.075,-1.27): gleiche Gruppierung (1,2 | 3,4) und gleicher Umlaufsinn -> Nummern stimmen mit MDD-Datenblatt ueberein. ACHTUNG: andere Hersteller (ST, Shikues) koennen abweichend nummerieren; bei Wechsel des Herstellers Pinout neu pruefen.
Pad-Layout (Datenblatt S.3): P1 6.00, P2 2.40, Q1 1.84, Q2 1.20 mm (KiCad: 1.0 x 0.8-Pads bei +-3.075 mm).

## Notes
- PoE: D1/D2 gleichrichten die Mode-A/Mode-B-Paare (Eingang ~ = AC1/AC2 an Pins 3/4, + = VDD_POE Pin 1, - = VSS Pin 2). 2 x 1.1 V Verlust bei 0.15 A OK. Peak-Sperrspannung 600 V >> 57 V.
