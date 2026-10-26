# HR871150C — HanRun RJ45 MagJack 10/100 PoE mit LEDs (THT, right angle)

Quelle: HanRun HR871150C Rev. 00, 4 Seiten, `HR871150C.pdf`. Schaltbild (S.1), Mechanik (S.2), PCB Layout (S.3) als PNG gerendert und visuell gelesen. Status: Pinout aus Schaltbild **gelesen und topologisch nachvollzogen** (Verbindungen verfolgt); Koordinaten aus Zeichnung gemessen -> Footprint vor Fertigung nochmals gegen S.3 pruefen. Polaritaet der Chip-Seite (P1/P2 bzw. P4/P5 = +/-) ist aus der Wicklungs-Punktlage abgeleitet (mittlere Sicherheit).

| Spec | Value |
|------|-------|
| Masse | Breite 16.00 mm, Tiefe 21.20 mm, **Hoehe 13.30 mm** (aus PCB), Schirm-Nase 3.50 mm |
| PoE | designed fuer 57 VDC, 350 mA je Mittelanzapfung (17.5 W mit 2, 35 W mit 4 Anzapfungen) |
| Magnetik | 2 x 1CT:1CT, OCL >= 350 uH @100 kHz/8 mA DC, IL <= -1.0 dB (1-100 MHz) |
| Isolation | 2250 VDC (UTP- zu Chip-Seite), min 1500 Vrms |
| Temperatur | Betrieb 0..+70 C, Lagerung -40..+85 C |
| LEDs | Links Gelb 585 nm, rechts Gruen 568 nm (Sicht von vorn); Vf 1.8-2.8 V @ 20 mA |
| Pin 6 | **entfernt (nicht vorhanden)** |
| Intern | 4 x (22 nF/100 V + 75 R) Bob-Smith je Mittelanzapfung (kabelseitig) gegen gemeinsamen Bus; Bus ueber 1000 pF/2 kV zum SHIELD |

## Pinbelegung (Pad-Nummern)
| Pad | Name | Funktion |
|-----|------|----------|
| P1 | TD+ (TX+) | Chip-Seite Paar 1/2, = RJ45 J1 (unteres Wicklungsende) |
| P2 | TD- (TX-) | Chip-Seite Paar 1/2, = J2 |
| **P3** | **CT (gemeinsam TX+RX)** | **EINE gemeinsame Chip-Seiten-Mittelanzapfung fuer BEIDE Uebertrager (intern gebrueckt)** |
| P4 | RD+ (RX+) | Chip-Seite Paar 3/6, = J3 |
| P5 | RD- (RX-) | Chip-Seite Paar 3/6, = J6 |
| P6 | - | nicht bestueckt |
| **P7** | VC1+ | kabelseitige Mittelanzapfung **Paar 1/2** (Mode A), PoE-Zugang |
| **P8** | VC1- | kabelseitige Mittelanzapfung **Paar 3/6** (Mode A) |
| **P9** | VC2+ | **Reservepaar 4/5** (J4+J5 intern verbunden) (Mode B) |
| **P10** | VC2- | **Reservepaar 7/8** (J7+J8 intern verbunden) (Mode B) |
| 11 | LED gelb Anode | (Dreieck-Seite) |
| 12 | LED gelb Kathode | |
| 13 | LED gruen Anode | |
| 14 | LED gruen Kathode | |
| SHIELD | Schirm | 2 Schirm-Laschen (Ø1.63 THT) + intern 1 nF/2 kV zum Bus |
Mapping zu Net-Plan: PSE_CT12 -> P7 -> D1 AC1; PSE_CT36 -> P8 -> D1 AC2; PSE_SP45 -> P9 -> D2 AC1; PSE_SP78 -> P10 -> D2 AC2 (bestaetigt; Reservepaare werden herausgefuehrt; die 4/5- und 7/8-Paare sind zusaetzlich intern mit 75 R + 22 nF Bob-Smith an den Bus gelegt, nur AC, kein DC-Pfad).

**Abweichung net_plan.md:** net_plan fuehrt getrennte Nets `ETH_TCT` (-> +3V3A) und `ETH_RCT` (-> C22 -> GND). Beim HR871150C gibt es nur EINEN Chip-seitigen CT (P3). Folge: P3 -> +3V3A (mit C23 100 nF); C22 (RCT-Block) hat keinen Anschlusspunkt (entfaellt/DNP). RX-Paar liegt dadurch DC auf +3V3A am Uebertrager; R3/R4/C21 ueber ETH_RX_TERM bleiben AC-gekoppelt (kein DC-Pfad) - Funktion gegen WIZnet-Referenz W5500/W55RP20 pruefen (offen).
LED-Beschaltung: Anode (P11/P13) ueber 330 R an +3V3, Kathode (P12/P14) an U5 LINKLED/ACTLED (aktiv low); (3.3-2.0)/330 = 4 mA. Welche Farbe Link/Act = Designentscheidung (Gelb links).

## Footprint-Geometrie (Draufsicht/Komponentenseite, Ursprung = Mitte der beiden Ø3.25-Loecher, +y = Vorderseite/Steckoeffnung)
- Ø3.25 mm (x2) Positionierstifte bei (+-5.715, 0) [Abstand 11.43].
- Signalpins Ø0.89 mm, Raster 2.54: untere Reihe y = -8.89: P1 x=+5.715, P3 +3.175, P5 +0.635, P7 -1.905, P9 -4.445; obere Reihe y = -6.35: P2 x=+4.445, P4 +1.905, (P6 fehlt bei -0.635), P8 -3.175, P10 -5.715.
- LED-Pins Ø1.02 mm bei y = +4.08: P14 x=-6.625, P13 -4.085, P12 +4.085, P11 +6.625 (Raster 2.54, 13.25 zwischen 14 und 11).
- Schirm-Pins Ø1.63 mm (x2) bei (+-7.745, ca. -3.0) [Abstand 15.49]; y-Wert aus Zeichnung gemessen (+-0.3).
- Vorderkante y = +10.80, Hinterkante y = -10.40 (Summe 21.20). Panel-Ausschnitt 16.54 x 14.00 mm.
- Hinweis: Zeichnung nicht massstabsgetreu bei einzelnen Masslinien (13.25/4.08 vs. Bildmessung weichen ab) -> Masszahlen massgebend, y der Schirmpins/LED UNVERIFIZIERT.
