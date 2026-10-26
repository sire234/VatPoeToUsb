# SMAJ58A — MDD 400 W unidirektionale TVS, DO-214AC (SMA)

Quelle: MDD SMAJ5.0(C)A-SMAJ440(C)A Rev. 2025A6, `SMAJ58A.pdf`; Elektrische Tabelle S.2 visuell gelesen (Textextraktion verschob Zeilen!).

| Spec | Value |
|------|-------|
| V_RWM (Stand-off) | **58.0 V** |
| V_BR | 64.4-71.2 V @ 1 mA |
| V_C max | 93.6 V @ I_PP = 4.3 A (10/1000 us) |
| P_PPM | 400 W (10/1000 us) |
| I_R | 1 uA @ V_RWM |
| I_FSM | 40 A |
| R_thJA / R_thJL | 120 / 30 C/W |
| Tj, Tstg | -65..+150 C |
| Package | SMA: L 4.0-4.6 (Body 3.8-4.5), B 2.3-2.8 mm, Hoehe 2.3-2.8 mm (BOM 2.4 ok) |

## Pinout
Unidirektional: Kathodenband = Kathode. D3: Kathode an VDD_POE, Anode an VSS.

## Notes
- PoE: max 57 V < V_RWM 58 V ok; Klemmung >64 V ... 93.6 V bei 4.3 A. TPS23753A Abs-Max 100 V an VDD -> V_C 93.6 V nur knapp darunter (Surge-Strom begrenzt).
- Der gleiche PDF-Datei deckt auch SMAJ43A ab (siehe SMAJ43A_SUMMARY.md).
