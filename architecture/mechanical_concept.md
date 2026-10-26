# Mechanical Concept – poe_usb_hid_bridge (Rev 4e, Rohr Ø 25 mm)

Stand: 2026-10-26 · gültiger Endstand **Rev 4g** · Board: `kicad/poe_usb_hid_bridge_rev4g/poe_usb_hid_bridge_rev4g.kicad_pcb`.
Koordinaten (alle Masse in mm): **x** = Längsachse (0 = RJ45-Stirnseite, 80 = USB-Stirnseite), **y** = Breite (0 = Kante mit ETH-Kanal), **z** = Höhe (0 = Rohrachse). Board-Ursprung in KiCad bei (100, 100).

## 1. Eckdaten

| Parameter | Wert |
|---|---|
| Rohr | **Kunststoffrohr**, Innen-Ø 25,0 (r = 12,5); Umgebung max. 40 °C empfohlen |
| PCB | **20,0 × 80,0**, **6 Lagen**, 1,6 mm, Stackup **JLC06161H-3313** |
| PCB-Lage im Rohr | **versetzt:** Oberseite bei z = −5,0, Unterseite bei z = −6,6 |
| RJ45 J1 | HR871150C Top-Mount (THT), Stirnseite x = 0, Mitte (x 10,8 / y 10) |
| PoE-Modul U1 | Ag9905-LPB, Top, Mitte bei x 34,5 / y 10, Modulachse entlang x |
| MCU U5 | W55RP20, Top, x 56,5 / y 10 |
| USB-A J2 | BX-TYPE-A-MWT4P liegend, Top, Stirnseite x = 80 (Bezugspunkt x 66,2 / y 10); 15,2 breit (Laschen) × 7,0 hoch |
| Status-LED D11 | Top, x 63,03 / y 13,56 (vor J2), grüne 0603-LED (Rev 4f) |
| R5 / R6 (MagJack-LED-R) | Bottom, x 5,0 / y 3,375 und 14,085 (neben J1.11 / J1.13) |
| SWD-Randpads J3 | **Bottom**, Längskante y = 20 bei x ≈ 59,4 (Pads 0,3 mm von der Kante, 4 × 2,54 mm); Stiftleiste liegend, Pins über die Kante |

## 2. Warum versetztes PCB?

1. Ein PoE-MagJack in Mid-Mount-Bauform ist nicht am Markt (nur Mid-Mount-Buchsen ohne Magnetik).
2. Mit der Oberseite 5,0 mm unter der Achse passt der 13,3 mm hohe MagJack mit Seitenluft, und oben bleibt Platz für das 8–9,2 mm hohe Modul.
3. Preis: Die Unterseiten-Hülle ist flacher – dort nur flache SMD-Teile.

## 3. Höhenhülle (Sehnenrechnung)

Halbe Sehnenbreite s(z) = √(r² − z²). PCB-Kanten (halbe Breite 10): Unterseite z = −6,6 → s = 10,62 → 0,62 mm Luft je Seite. Ab d = 5,9 kollidieren die Kanten.

| \|y − 10\| | 0 | 4 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|
| oben (über Top-Kupfer) | 17,5 | 16,8 | 16,0 | 15,4 | 14,6 | 13,7 | 12,5 |
| unten (unter Bottom) | 5,9 | 5,2 | 4,4 | 3,8 | 3,0 | 2,1 | 0,9 |

Prüfung der hohen Teile:
- **J1** (16 breit, 13,3 hoch): Oberkante z = 8,3, s(8,3) = 9,35 > 8 ✓ (≈ 1,3 Seitenluft).
- **U1** Ag9905-LPB: Freihaltung K/2 = 7,76 → Hülle ≈ 14,8 ≥ 9,2 (max. Höhe) ✓, Reserve ≥ 5,6.
- **J2** USB-A laut Datenblatt **15,2 breit (inkl. Laschen) × 7,0 hoch** (bisher hier fälschlich 13,1 × 5,7; korrigiert nach 2. Review): z −5,0 … +2,0, halbe Breite 7,6 < s(2,0) = 12,3 ✓ – vollständig im Kreis. Endkappen-Ausschnitt entsprechend grösser vorsehen (§7).
- **Bottom:** höchste Teile MB6S (D1/D2, 2,6 bei |y − 10| ≈ 5,9 → Hülle ≈ 4,4) ✓, C18 2,1, C11 1,9. **D3 SMA 2,4 hat nur ≈ 0,25 mm Reserve zur Rohrwand** (2. Review, Lage nahe der Kante) → knapp, beim Einbau prüfen (design_risks R-TH-6). Die THT-Pins von J1 stehen unten ≈ 1,5–3 mm über. Unter U1 ist die Unterseite frei nutzbar (SMD-Modul ohne Pins).

## 4. Platzierung (Rev 4e, aus dem Board)

| Zone | x-Bereich | Top | Bottom |
|---|---|---|---|
| Z1 RJ45 | 0–21 | J1 | R7, C24 (Schirm), C23 |
| Z2 Primärinsel + Modul | 16–45 | U1 (VIN-Pads Richtung y ≈ 15,8, Ausgangs-Pads Richtung y ≈ 4,2) | D1, D2, D3, C1 (y ≈ 15,6–18,4), C14 (DNP, über der Grenze), R8, R9 (DNP), C11 (x 35,3 / y 6,5) · **C65/C66** (RX-Koppel-C, x ≈ 24,2 / y ≈ 0,8–1,8 im ETH-Kanal, sekundär) |
| Z3 Sekundär-Leistung | 42–50 | U4, C15, C16 | C10, C12, C13, FB1, D12, TP9 |
| Z4 MCU | 48–63 | U5, Y1 (+C25/C26/R37, kurze XIN-Leitung 3,2 mm), Y2 (+C27/C28), C61 (neben U5, nicht direkt an Pin 33 – R-LAY-7), R1, R2, D11 | Entkopplung C40–C60, C62 als Ring unter U5, FB2, R3, R4, C21, R22, R38, C64 · J3 (SWD-Randpads, Bottom an der Längskante y = 20, x ≈ 59,4) |
| Z5 USB | 63–80 | J2, R28, R29 | U6, U7, C17–C20, C29, R25, R26, R30–R34, C30 |

Bestückung beidseitig; **U1 nur Top** (DS V3.5 §8: nicht kopfüber durch den Reflow).

## 5. Isolationsgrenze

- **Primärinsel:** x ≈ 16–45, y ≈ 12–19,7 (Flächen `F_VDD_POE_PRI` auf F.Cu, `B_VSS_PRI` auf B.Cu); J1-PoE-Pins 7–10, D1–D3, C1, U1-Pads 4/5.
- **Keepout (alle 6 Lagen):** Rule-Area `ISO_BAND` (x 21,2–47,7, y 9,0–20,5, Grenzstreifen um die Insel) und `ISO_BAND_J1` (x 13,2–16,2, y 10,2–20,5); im U1-Footprint zusätzlich der gestufte 3-mm-F.Cu-Keepout nach DS Fig. 21. Die Sekundär-Flächen der Innenlagen sind durch diese Keepouts von der Primärinsel getrennt (Primärflächen nur auf F.Cu/B.Cu; die PSE-Leitungen J1 → D1/D2 laufen zusätzlich als Leiterbahnen auf In1/In2 innerhalb der Insel).
- **DRC:** `ISO_PRI_SEC_3mm` (Netzklasse `POE_HV` ↔ Rest ≥ 3,0 mm Abstand und Bohrungsabstand, alle Lagen); Ausnahmen nur innerhalb U1, C14 und J1 (J1: 1,0 mm, dokumentierte Abweichung R-ISO-3).
- **ETH-Kanal:** Die ETH-Paare laufen an der Längskante (Rule-Area `ETH_COUPLED`, x 28–55, y 0,4–1,6) an der Primärinsel vorbei zu U5 – Sekundärseite, ≥ 3 mm zur Insel. Im RX-Paar sitzen die Koppel-C C65/C66 (Bottom, x ≈ 24,2); RX-Länge gesamt P/N 60,525/60,529 mm. Ausnahme: ETH_RXN hat an J1 nur 1,8 mm zu J1.7 (PSE_CT12) – Teil der J1-Ausnahme (design_risks R-ISO-9).

## 6. Stackup und Lagenbelegung

| Lage | Dicke (Board-Setup) | Funktion |
|---|---|---|
| F.Cu | 35 µm | Bauteile, Signale, GND-Fläche `F_GND_SEC`, Primärfläche `F_VDD_POE_PRI`, `F_5VRAW` am Modulausgang |
| Prepreg | 0,0994 | |
| In1.Cu | 15 µm | **GND** (Referenz für ETH/USB auf F.Cu) |
| Core | 0,55 | |
| In2.Cu | 15 µm | **VBUS_USB** (Insel x 65–79,5) |
| Prepreg | 0,1088 | |
| In3.Cu | 15 µm | **+5V** (x 44,9–79,7) |
| Core | 0,55 | |
| In4.Cu | 15 µm | **+3V3** |
| Prepreg | 0,0994 | |
| B.Cu | 35 µm | Bauteile, GND `B_GND_SEC`, Primär `B_VSS_PRI`, `B_5VRAW` |

Gesamtdicke 1,6 mm. Bei der Bestellung **JLC06161H-3313** wählen und die Leiterbahngeometrie mit dem JLC-Impedanzrechner bestätigen:

| Netzklasse | Ziel | Geometrie im Board |
|---|---|---|
| `ETH` | 100 Ω diff. | 0,13 mm / Gap 0,2 mm |
| `USB` | 90 Ω diff. | 0,15 mm / Gap 0,18 mm, ≤ 30 mm |

**Vias:** Standard 0,45/0,3 mm (und 0,6/0,3 mm); nur innerhalb der Rule-Area `U5_FANOUT` (x 51,3–62,0, y 4,3–15,1) **0,4/0,2 mm** mit 0,1 mm Abstand – im Board sind es nur **3 Vias**, sie lösen aber den JLC-Aufpreis aus (akzeptiert; Review: Ersatz durch 0,45/0,3 prüfen). **Via-in-Pad:** bei JLC „Via-in-Pad, gefüllt und gedeckelt (POFV)" bestellen (im Board sind keine Filling-/Capping-Attribute gesetzt) und die POFV-Liste beilegen: Via-Mitte im Pad – U1 Pad 1 × 2 (41,6/4,2; 42,4/4,2), C52.1 (62,32/13,56), U4-EP × 3 (49,15/14,04; 49,15/14,60; 49,15/15,16); Via-Rand berührt Pad – U5.54 (60,79/12,25), C55.1 (59,34/4,68), R22.1 (57,05/4,2), C50.2 (49,6/10,3).
**Ergänzt 2026-10-23 (2. Review):** U4: 3 Thermal-Vias im EP + 2 GND-Vias südlich (49,40/16,10; 48,75/16,25); USB-Bereich: 5 GND-Stitching-Vias (66,25/5,25; 68,50/12,50; 70,75/9,00; 69,25/13,75; 72,75/13,25).

## 7. Endkappen, Sichtbarkeit

- RJ45-Seite: Ausschnitt ≈ 16,5 × 14 mm, Unterkante z ≈ −5,0. Die MagJack-LEDs (gelb links = Activity, grün rechts = Link, Sicht von vorn) sind seit Rev 4g beschaltet – Ausschnitt so, dass sie sichtbar bleiben.
- USB-Seite: Ausschnitt für die Buchsenöffnung ≈ 13,5 × 6,2 mm unterhalb der Achse (Buchsenkörper mit Laschen 15,2 × 7,0 mm muss hinter der Kappe Platz haben); D11 (Top-View) ist durch ein Fenster/Lichtleiter Ø 2 mm in der USB-Endkappe sichtbar.
- Board-Führung über Nut in den Endkappen; Seitenluft 0,6 mm je Seite.

## 8. Wärmeableitung

- Gehäuse ist ein **Kunststoffrohr** Innen-Ø 25 mm (User-Entscheidung 2026-10-23): Die Isolation zum Rohr ist damit unkritisch (kein leitfähiges Gehäuse, R-ISO-5 entschärft). Die Wärmeabfuhr ist schlechter als bei Aluminium (innen ≈ +5–10 K; bei 40 °C Umgebung ≈ 68–80 °C Board-Temperatur) → **max. Umgebungstemperatur 40 °C empfohlen**; Lüftungsschlitze in den Endkappen sinnvoll; Temperaturen am Muster messen. Ein Wärmeleitpad zur Rohrwand bringt beim Kunststoffrohr wenig; Wärme über die Kupferflächen und die Endkappen-Öffnungen abführen.
- Falls später doch ein Metallrohr/Metallkappen verwendet werden: Primärkupfer (VSS/VDD_POE) **nicht** an das Gehäuse koppeln (R-ISO-5 lebt dann wieder auf).
- U1: Kupferflächen an +VDC/−VDC beidseitig mit Vias; optional Wärmeleitgel unter dem Modul (DS Fig. 13).

---

## Änderungshistorie

- **Rev 1/2 (2026-10-21):** 20 × 76 mm (zulässig bis 80), 4 Lagen JLC04161H-3313, versetztes PCB, L-förmige Isolationsgrenze für den diskreten Flyback (T1 POE70P 10,9 mm hoch, Schlitz unter T1), J1 HY931147C → HR871150C.
- **Rev 3 (2026-10-22):** Variante 30 × 80 mm im 35-mm-Rohr, PCB mittig, Flyback mit Isolationsbändern – **verworfen** (Layout-Stände `outputs/layout_30mm`, `fab_30mm`).
- **Rev 4 (2026-10-22):** Ag9905LP (DIL, THT-Pins unten ≈ 1,4 mm), zurück zu 20 × ≈ 80 mm / 25-mm-Rohr; Primärinsel schrumpft auf J1-PoE + Brücken + Modul-VIN.
- **Rev 4b (2026-10-22):** Layout auf 6 Lagen; Tag-Connect-Feld J3 an U5.
- **Rev 4c (2026-10-22):** Variante mit Brücken/grossen Pads – verworfen.
- **Rev 4d (2026-10-22):** J3 → SWD-Pads TP1–TP4; Board DRC 0/0 (Fab-Daten `outputs/fab_rev4d_final`).
- **Rev 4e (2026-10-23):** U1 Ag9905-LPB (SMT): neuer Footprint, Unterseite unter dem Modul frei, gestufter Keepout; DRC 0 Errors / 0 Unconnected / 0 Parity.
- **Rev 4e Review (2026-10-23):** C65/C66 im RX-Kanal (Bottom, x ≈ 24,2), Y1 ABM8-272-T3 mit kürzerer XIN-Leitung (3,2 mm); Kunststoffrohr, Umgebung ≤ 40 °C; J3 auf Bottom (y = 20) dokumentiert. DRC (11:45): 0 Errors, 0 Unconnected, 0 Parity, 23 Silkscreen-/Bibliotheks-Warnungen.
- **2. Review (2026-10-23):** U4-Wärme-Vias und USB-GND-Stitching ergänzt, POFV-Liste aktualisiert; J2-Masse (15,2 × 7,0) und D3-Reserve (≈ 0,25 mm) korrigiert; DRC (13:47) unverändert 0/0/0, 23 Warnungen.
