# IC & Key Component Selection – poe_usb_hid_bridge (Rev 4e)

Stand: 2026-10-26 · gültiger Endstand **Rev 4g**. Bezugsdaten (LCSC/JLC-Tier, Stock, Preise) in `sourcing/sourced_bom.md`, Datenblätter in `datasheets/` (Index `datasheets/README.md`).

Bewertungskriterien: Funktion/Normkonformität · Bauhöhe/Fläche (20 mm Breite, Rohr Ø 25) · Thermik im geschlossenen Rohr · Bestückbarkeit bei JLCPCB · Bewährtheit · Kosten.

## Endauswahl

| Ref | Funktion | Gewählt | Begründung / Eckdaten | Verworfen / Fallback |
|---|---|---|---|---|
| U1 | PoE-PD + isolierter 5-V-Wandler | **Silvertel Ag9905-LPB** (Low-Profile-SMT, Beistellteil) | 802.3af Class 0, 5,00 V (4,75–5,25 V), 1,4 A, 7 W ≤ 70 °C / 4,5 W @ 85 °C, Thermoschutz, 1500 V Impulstest, 21,21 × 13,92 × 8,0 (max 9,2) mm, MSL 1, Reflow nur Top. Ersetzt ≈ 34 Bauteile des diskreten Flybacks. Status „Preferred" in DS V3.5 | Ag9905LP (DIL, nicht lieferbar, Rev 4–4d); Ag9905-MTB (13,4 mm hoch); diskreter TPS23753A-Flyback (Rev 1–3) |
| J1 | RJ45-PoE-MagJack | **HanRun HR871150C** | 16 × 13,3 mm, PoE Mode A + B herausgeführt (P7–P10), 1 gemeinsamer chipseitiger CT (P3), 1500 Vrms Isolation; 0…+70 °C | HY931147C (15,2 mm hoch, 18 mm breit, Stock 0); Mid-Mount-MagJack mit PoE nicht am Markt |
| D1, D2 | Brückengleichrichter | **MDD MB6S** | 600 V / 0,5–1 A, 2,6 mm; vom Modul-DS empfohlen (MB4S/MB6S) | ABS10 (flacher), Schottky-Brücken (Leckstrom stört Signatur) |
| D3 | TVS | **MDD SMAJ58A** | vom Modul-DS gefordert (Fig. 14) | – |
| C11 | Modul-Ausgangs-C ≥ 100 µF low-ESR | **AISHI SA11AM101A19R15XXX** | 100 µF 10 V Polymer, ESR 15 mΩ, Ripple 2,5 A, 7343 × 1,9 mm | Ymin MPD101M1AD19015R (gleicher FP); jieerrui MA10V100M6X6 (6 mm hoch) |
| D12 | OVP-Klemme +5V | **BZT52C6V2** (BORN) | V_Z 5,8–6,6 V > 5,65 V (ADJ max) | – |
| FB1 | Post-Filter | **TAI-TECH HCB3216KF-601T30** | 600 Ω / 3 A / 40 mΩ, 1206 | Murata BLM31KN601SN1L |
| U4 | 3,3-V-LDO | **TI TLV75733PDRVR** | 1 A, WSON-6 mit EP (θJA ≈ 70–85 K/W), P_V 0,31–0,48 W | AP2112K (SOT-23-5, thermisch ungeeignet), AMS1117 (gross); Buck als Option |
| U5 | µC + Ethernet | **WIZnet W55RP20** (fix) | RP2040 + W5500 + 2 MB Flash, QFN-68 8 × 8, Tc max 85 °C | – |
| Y1 | 12 MHz | **Abracon ABM8-272-T3** (C_L 10 pF, ESR ≤ 50 Ω, LCSC C20625731, Extended) + 2 × 15 pF C0G (C25/C26) + R37 1 k | Review H1: exakt die Raspberry-Pi-Referenz („Hardware design with RP2040"/Pico) → gesicherter XOSC-Anlauf; Mehrkosten ≈ 0,44 USD + 1 Extended-Typ | YXC X322512MSB4SI (20 pF, Basic) + 2 × 33 pF (Rev 2 – Rev 4e vor Review, footprint-gleich) |
| C65, C66 | ETH-RX-Koppel-C | **YAGEO CC0402KRX7R9BB682** 6,8 nF 50 V X7R 0402 (C93654, Extended) | Review K1: WIZnet-W5500-Referenz „connected CT" verlangt DC-Trennung der RX-Pins vom CT (+3V3A) | kein Basic-Typ 6,8 nF/0402 verfügbar |
| Y2 | 25 MHz | **YXC X322525MRB4SI** (18 pF) + 2 × 27 pF | W5500-Vorgabe C_L 18 pF, ±30 ppm | X322525MOB4SI (nur 12 pF) |
| U6 | USB-Lastschalter | **TI TPS2553DBVR**, R_ILIM 44,2 kΩ | einstellbar: 532–659 mA inkl. Toleranz; EN aktiv-high; FAULT ungenutzt | TPS2051B (fix bis 1,3 A, EN aktiv-low), AP2553W6 (pinkompatible Zweitquelle) |
| U7 | USB-ESD | **ST USBLC6-2SC6** | Industriestandard, VBUS-Referenz | USBLC6-2P6, TPD2E2U06 |
| J2 | USB-A liegend | **Bossie BX-TYPE-A-MWT4P** (SMD, 13,5 mm tief) | bei JLC bestückbar | Amphenol 87520-0010BLF (Handlöten) |
| D11 | Status-LED | **MEIHUA MHT193CGCT** grün 0603 (Rev 4f) | 569 nm AlGaInP, Vf ≈ 2,2 V → an 3,3-V-GPIO über 330 Ω ≈ 3,5 mA | InGaN-Grün (Vf ≈ 3 V, zu wenig Reserve); WS2812B-2020-V6 (Rev 4b–4e) |
| C18 | VBUS-Bulk | **KEMET T520B157M006ATE035** | 150 µF 6,3 V Polymer-Ta, 2,1 mm | Panasonic 6TPE150MAZB |
| C14 | Y-Kap (Option) | **PSA FK12X222K502EGQ** 2,2 nF X1/Y2 (DNP) | Y2-zertifiziert, 1812 | Murata GA343 (nur Y3) |

## Begründung der Schlüsselentscheidungen

### PoE-Modul statt diskretem Flyback (Rev 4)
| Kriterium | Ag9905-LPB (gewählt) | Rev 1–3 diskret (TPS23753A + POE70P) |
|---|---|---|
| Norm / Klasse | 802.3af, Class 0 (fest) | 802.3af, Class 2 |
| Ausgang | 5,00 V ±5 %, 1,4 A, Thermoschutz | 5,07 V ±1,5 %, ≈ 1 A |
| Isolation | im Modul | T1/Opto/Y-Kap + 3-mm-L-Grenze auf dem Board |
| Teile | 1 Modul + Brücken/TVS/C-Ausgang | ≈ 34 Teile, T1 10,9 mm hoch |
| Entwicklungsrisiko | gering | Regelschleife, T1-Sättigung, EMV, Pi-Filter |
| Kosten | ≈ 9 USD (DigiKey) | ≈ 2,7 USD T1 + ≈ 3,3 USD SMD + ≈ 10 Extended-Typen |

### LPB statt LP (Rev 4e)
Ag9905LP (DIL) nicht lieferbar (DigiKey/JLC Stock 0); im DS V3.5 sind LPB/MTB „Preferred". LPB ist elektrisch/thermisch identisch, aber **anderes Pinout (5 Pads)** und anderer Footprint (`Silvertel_Ag9900LPB_SMD`, Reflow-Land-Pattern DS Fig. 21; Handlöt-Variante `_HandSolder` nach Fig. 22 liegt in der Bibliothek). Die Unterseite unter dem Modul ist frei (keine THT-Pins).

### TPS2553 mit 44,2 kΩ
Die Formeln des TPS2553-DS ergeben 537/591/653 mA (min/typ/max), inkl. ±1 % 532–659 mA → ein 500-mA-Gerät wird nie begrenzt, und der USB-Fehlerfall bleibt im thermischen Budget des Moduls (≤ 4,52 W an +5V_RAW).

### LDO TLV75733P statt AP2112K
P_V bis 0,48 W im geschlossenen Rohr; SOT-23-5 (θJA ≈ 250 K/W) wäre zu heiss, WSON mit EP + Vias ist ausreichend.

### Status-LED D11 (Rev 4f) und MagJack-LEDs (Rev 4g)
D11: normale grüne 0603-LED mit niedriger Vf (569 nm) statt WS2812B – kein PIO, kein Backen (MSL), ein GPIO aktiv-high. MagJack-LEDs: direkt vom W5500 (LINKLED/ACTLED, aktiv low, Push-Pull), Anoden über R5/R6 330 Ω an +3V3 (≈ 4 mA) – Link/Activity ohne Firmware.

## Bibliotheksteile (Projekt)

- Symbole `libs/poe_usb_hid_bridge.kicad_sym`: **verwendet** `Ag9905-LPB`, `HR871150C`, `W55RP20`, `TPS2553`, `MB6S_MDD`; **nicht mehr verwendet** `Ag9905LP`, `TPS23753A`, `TLV431_DBZ`, `POE70P-50LD`, `E6C0606RGBC3UDA`.
- Footprints `footprints/poe_usb_hid_bridge.pretty`: **verwendet** `Silvertel_Ag9900LPB_SMD`, `HanRun_HR871150C`, `BX-TYPE-A-MWT4P`, `W55RP20_QFN-68-1EP_8x8mm_P0.4mm_EP6.2x6.2mm`; Reserve `Silvertel_Ag9900LPB_SMD_HandSolder`; **nicht mehr verwendet** `Silvertel_Ag9900LP_DIL8`, `Coilcraft_POE70P`, `EKINGLUX_1616_RGB`.

---

## Änderungshistorie

- **Rev 1 (2026-10-21):** Auswahl ohne Live-Daten: J1 HY931147C, U1 TPS23753APW + T1 POE70P-50LD + Q1 FDC2512 + U2 LTV-357T-C + U3 TLV431B + D10 PMEG4050EP, Y1 ABM8-272-T3, D11 Kingbright APTF1616 an +3V3.
- **Rev 2 (2026-10-21):** J1 HR871150C, L1 TDK VLS3012CX, R_S 0,75 Ω, T1 Consignment, Y1 X322512MSB4SI, Y2 X322525MRB4SI, J2 BX-TYPE-A-MWT4P, D11 E6C0606RGBC3UDA an +5V mit 3 × 2N7002, R25 44,2 k.
- **Rev 3 (2026-10-22):** unverändert (nur Layoutvariante 30 × 80 mm, verworfen).
- **Rev 4 (2026-10-22):** diskreter Flyback verworfen → Ag9905LP (DIL); C11 Polymer 100 µF.
- **Rev 4b (2026-10-22):** D11 → WS2812B-2020-V6 (Q2–Q4 entfallen); Test-Pads → Tag-Connect-Pad-Feld TC2050 (J3), SW1 bleibt.
- **Rev 4c (2026-10-22):** Brücken-/Pad-Variante – verworfen.
- **Rev 4d (2026-10-22):** SW1 KMR211NGLFS und Tag-Connect entfallen (nur SWD-Pads), LED an +3V3.
- **Rev 4e (2026-10-23):** Ag9905-LPB statt Ag9905LP.
- **Rev 4e Review (2026-10-23):** Y1 zurück auf ABM8-272-T3 + 2 × 15 pF (H1); neu C65/C66 6,8 nF RX-Koppel-C (K1).
