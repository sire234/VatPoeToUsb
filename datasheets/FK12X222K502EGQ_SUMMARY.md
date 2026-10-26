# FK12X222K502EGQ — PSA (Prosperity) X1/Y2 sicherheitszertifizierter MLCC, 2.2 nF, 250 VAC, 1812

Quelle: Prosperity FK/FH Safety MLCC Datenblatt, `FK12X222K502EGQ.pdf` (Text gelesen).

| Spec | Value |
|------|-------|
| Typcode | FK (X1/Y2) - 12 (1812) - X7R - 222 (2200 pF) - K (+-10 %) - 502 (**5 kV Impulsspannung**) - E (Embossed Tape) - G (Dicke-Code) - Q (Anti-Arcing) |
| Zertifizierung | X1/Y2: IEC 60384-14:2013/AMD1:2016, UL 60384-14 / UL 62368-1 (E346791, E231248), TUV (R 50041666 & R 50359148), CQC (CQC20001247849), ENEC-03020 (FK-Serie) |
| Nennspannung | 250 VAC (Y2) |
| Abmessungen 1812 | L 4.5 +0.6/-0.3 mm, W 3.2 +-0.4 mm, Dicke laut Code G: ca. 2.0 +-0.2 mm (Mapping Tabelle 8/ Kapazitaetstabelle nicht eindeutig -> UNVERIFIZIERT), Anschluss MB 0.5 +-0.25 |
| Temperatur | -55..+125 C |
| Dielektrikum | X7R (Kapazitaetsbereich X1/Y2 100 pF..4700 pF bei 5 kV) |

## Notes
- Y2-Kondensator C14 ueberbrueckt die Isolationsbarriere (RTN <-> GND). Kriechstrecke zwischen den 1812-Pads ca. 2-3 mm; fuer Y2 (Basic/Functional-Isolation PoE 1500 Vrms) Platinen-Clearance zwischen Primaer- und Sekundaerkupfer separat auslegen.
- Datenblatt Teil: Keine Pinpolaritaet.
