# Skeleton BOM – poe_usb_hid_bridge (Rev 4e)

Stand: 2026-10-26 · gültiger Endstand **Rev 4g**. Funktionale Stückliste je Block mit Auslegungsbegründungen. Die vollständige Einkaufsliste (alle 85 Refs mit MPN, LCSC, Tier, Preis, Seite) steht in `sourcing/sourced_bom.md`.
Tier: `B` Basic, `P` Preferred, `E` Extended, `CS` Beistellteil. Seite: `T` Top, `B` Bottom (aus dem Rev-4e-Board).

## B1 – ethernet_magjack

| Funktion | Ref | Wert | MPN | Tier | Seite | Hinweis |
|---|---|---|---|---|---|---|
| RJ45-PoE-MagJack 10/100 | J1 | HR871150C | HanRun HR871150C | E (THT) | T | 1 TD+, 2 TD−, 3 CT, 4 RD+, 5 RD−, 7–10 PoE, 11/12 LED gelb A/K (Activity), 13/14 LED grün A/K (Link), SH Schirm. 0…+70 °C |
| TX-Bias 49,9 Ω 1 % | R1, R2 | 49,9 Ω | 0402WGF499JTCE | B | T | → +3V3A |
| RX-Koppel-C (K1) | C65, C66 | 6,8 nF 50 V X7R 0402 | YAGEO CC0402KRX7R9BB682 | E | B | in Serie J1.4/J1.5 (ETH_RXP_J/_RXN_J) ↔ ETH_RXP/ETH_RXN; x ≈ 24,2 im RX-Kanal |
| RX-Terminierung 49,9 Ω 1 % | R3, R4 | 49,9 Ω | 0402WGF499JTCE | B | B | chipseitig → ETH_RX_TERM |
| RX-AC-Mittelpunkt | C21 | 10 nF | CL05B103KB5NNNC | B | B | |
| CT-Abblock | C23 | 100 nF | CL05B104KO5NNNC | B | B | an J1.3 |
| Schirm-Ableitwiderstand | R7 | 1 MΩ 0603 | 0603WAF1004T5E | B | B | |
| Schirm-Kondensator | C24 | 4,7 nF 2 kV 1812 | C1812X472K202T | E | B | |

**C22 entfällt (seit Rev 2):** Beim HR871150C sind TX- und RX-CT intern auf P3 verbunden; P3 liegt auf +3V3A (C23). Die RX-Anpassung bleibt über C21 DC-frei gegen den CT. **Seit dem Review (K1)** trennen C65/C66 (6,8 nF in Serie) die RX-Pins des W5500 DC-mässig vom CT – so verlangt es die WIZnet-W5500-Referenz „connected CT"; vorher lagen die RX-Pins DC auf 3,3 V.

## B2 – poe_pd_module

| Funktion | Ref | Wert | MPN | Tier | Seite | Hinweis |
|---|---|---|---|---|---|---|
| PoE-PD-Modul 5 V, Class 0, isoliert, SMT | U1 | Ag9905-LPB | Silvertel Ag9905-LPB | **CS** | **T (nur Top)** | 1 +VDC, 2 −VDC, 3 ADJ, 4 VIN+, 5 VIN−; 8,0 (max 9,2) mm; DNP im JLC-Export |
| Brücke Mode A / B | D1, D2 | MB6S | MDD MB6S-50MIL | E | B | 1 +, 2 −, 3/4 ~ |
| TVS 58 V | D3 | SMAJ58A | MDD SMAJ58A | E | B | DS Fig. 14 |
| Eingangs-C (Option) | C1 | 100 nF 100 V 0805 | CL21B104KCFNNNE | B | B | **DNP** (Detection, R4-3) |
| Ausgangs-C low-ESR (Pflicht) | C11 | 100 µF 10 V Polymer 15 mΩ | AISHI SA11AM101A19R15XXX | E | B | 7343 × 1,9 mm, Ripple 2,5 A |
| Ausgangs-Keramik | C12 | 22 µF 25 V 0805 | CL21A226MAQNNNE | B | B | DS „C2 = 10 µF 25 V" |
| HF-C | C10 | 100 nF 0402 | CL05B104KO5NNNC | B | B | |
| Mindestlast RB (Option) | R8 | 100 Ω 1206 | 1206W4F1000T5E | B | B | **DNP** (R4-4) |
| ADJ-Trimm (Option) | R9 | offen | – | – | B | **DNP** (R4-2) |
| Post-Filter-Ferrit | FB1 | 600 Ω / 3 A 1206 | HCB3216KF-601T30 | E | B | DCR 40 mΩ |
| Post-Filter-C | C13 | 22 µF 25 V 0805 | CL21A226MAQNNNE | B | B | |
| OVP-Zener | D12 | BZT52C6V2 | BZT52C6V2 | E | B | K = +5V |
| Y2-Kap VSS ↔ GND (Option) | C14 | 2,2 nF X1/Y2 1812 | FK12X222K502EGQ | E | B | **DNP** (EMV-Option) |
| Test-Pad +5V | TP9 | Pad Ø 1,0 | – | – | B | |

## B4 – ldo_3v3

| Funktion | Ref | Wert | MPN | Tier | Seite |
|---|---|---|---|---|---|
| LDO 3,3 V / 1 A | U4 | TLV75733PDRVR | TI | E | T |
| Eingang | C15 | 4,7 µF 16 V 0603 | CL10A475KO8NNNC | B | T |
| Ausgang | C16 | 10 µF 10 V 0603 | CL10A106KP8NNNC | B | T |

## B5 – mcu_w55rp20

| Funktion | Ref | Wert | MPN | Tier | Seite | Hinweis |
|---|---|---|---|---|---|---|
| µC + Ethernet-SiP | U5 | W55RP20 | WIZnet W55RP20 | E | T | QFN-68, MSL 3, reservieren |
| IOVDD-Abblock | C40–C45 | 100 nF | CL05B104KO5NNNC | B | B | |
| +3V3-Bulk | C46 | 10 µF 0603 | CL10A106KP8NNNC | B | B | |
| VREG_VIN / VREG_VOUT | C47, C48 | 1 µF 25 V 0402 | CL05A105KA5NQNC | B | B | |
| DVDD, USB_VDD, ADC, Flash, W5500-VDD, AVDD | C49–C59 | 100 nF | CL05B104KO5NNNC | B | B | |
| +3V3A-Bulk | C60 | 10 µF 0603 | CL10A106KP8NNNC | B | B | |
| +3V3A-Ferrit | FB2 | 120 Ω@100 MHz | BLM18PG121SN1D | B | B | |
| TOCAP | C61 | 4,7 µF 0603 | CL10A475KO8NNNC | B | T | soll direkt an U5.33 – im Layout nicht direkt (Review, offen R-LAY-7) |
| 1V2O | C62 | 10 nF | CL05B103KB5NNNC | B | B | |
| EXRES1 | R22 | 12,4 k 1 % | 0402WGF1242TCE | E | B | |
| Quarz 12 MHz | Y1 | 12 MHz, C_L 10 pF, ESR ≤ 50 Ω | Abracon ABM8-272-T3 | E | T | H1: Raspberry-Pi-Referenz |
| Y1-Lasten | C25, C26 | 15 pF C0G | 0402CG150J500NT | B | T | C_L ≈ 7,5 + ≈ 3 pF Streu ≈ 10,5 pF |
| XOUT-Serien-R | R37 | 1 k | 0402WGF1001TCE | B | T | wie RPi-Referenz |
| Quarz 25 MHz | Y2 | 18 pF | YXC X322525MRB4SI | E | T | W5500-Vorgabe |
| Y2-Lasten | C27, C28 | 27 pF C0G | 0402CG270J500NT | P | T | |
| SWD-Randpads | J3 | 1×4, 2,54 mm, Pads 1,5 × 3,0 mm | – | – | T (Kante) | DNP, 1 SWCLK / 2 GND / 3 SWDIO / 4 +3V3, für liegend aufgelötete Stiftleiste |

## B6 – usb_host_port

| Funktion | Ref | Wert | MPN | Tier | Seite | Hinweis |
|---|---|---|---|---|---|---|
| USB-Lastschalter | U6 | TPS2553DBVR | TI | E | B | FAULT offen |
| R_ILIM | R25 | 44,2 k 1 % | 0402WGF4422TCE | E | B | Auslegung unten |
| EN-Pull-down | R26 | 100 k | 0402WGF1003TCE | B | B | VBUS beim Boot AUS |
| U6-Eingang | C17 | 1 µF 50 V 0603 | CL10A105KB8NNNC | B | B | |
| VBUS-Bulk | C18 | 150 µF 6,3 V Polymer-Ta | KEMET T520B157M006ATE035 | E | B | USB ≥ 120 µF |
| VBUS 10 µF / 100 nF | C19, C20 | | CL10A106KP8NNNC / CL05B104KO5NNNC | B | B | |
| USB-ESD | U7 | USBLC6-2SC6 | ST | E | B | |
| USB-Serien-R | R28, R29 | 27 Ω | 0402WGF270JTCE | E | T | |
| Host-Pull-downs | R30, R31 | 15 k | 0402WGF1502TCE | B | B | **DNP** (RP2040 intern) |
| USB-A-Buchse | J2 | BX-TYPE-A-MWT4P | Bossie | E | T | Custom-FP |
| VBUS-Teiler | R32, R33 | 100 k / 68 k | 0402WGF1003TCE / 0402WGF6802TCE | B / P | B | |
| VBUS_SENSE-Filter | C29 | 100 nF | CL05B104KO5NNNC | B | B | |
| USB-Schirm | R34 | 0 Ω 0603 | 0603WAF0000T5E | B | B | |
| USB-Schirm-C (Option) | C30 | 4,7 nF 0603 | CL10B472KB8NNNC | E | B | **DNP** |

### Auslegung R25 (TPS2553 R_ILIM)
Formeln (TPS2553-DS, R in kΩ, I in mA): nom = 23950/R^0,977 · min = 25230/R^1,016 · max = 22980/R^0,94. Fenster für max ≤ 680 mA **und** min > 500 mA: 42,3 kΩ ≤ R ≤ 47,4 kΩ.

| R25 | nom | min | max | inkl. R ±1 % | Bewertung |
|---|---|---|---|---|---|
| 40,2 k | 649 | 592 | 714 | 586 / 721 | zu hoch |
| **44,2 k (gewählt)** | **591** | **537** | **653** | **532 / 659** | ausgewogen |
| 47 k (Basic) | 557 | 505 | 616 | 500 / 622 | keine Reserve für 500-mA-Geräte |

Seit Rev 4 (Class 0) ist die Klassengrenze kein Kriterium mehr; die Begrenzung bleibt wegen des Modul-Deratings (4,5 W @ 85 °C).

## B7 – status_led

| Funktion | Ref | Wert | MPN | Tier | Seite | Hinweis |
|---|---|---|---|---|---|---|
| Status-LED grün | D11 | MHT193CGCT 0603 | MEIHUA | E | T | GPIO28 → R38 → D11 → GND |
| LED-Vorwiderstand | R38 | 330 Ω | 0402WGF3300TCE | B | B | ≈ 3,5 mA |
| MagJack-LED-Vorwiderstände (B1) | R5 / R6 | 330 Ω | 0402WGF3300TCE | B | B | Anoden J1.11/J1.13 → +3V3, ≈ 4 mA |

## Mengen

85 Referenzen · 9 DNP (C1, C14, C30, R8, R9, R30, R31, J3, U1 im JLC-Export) · TP9 nur Pad → **75 Positionen bei JLC + U1 beigestellt = 76 bestückte Bauteile** · 20 Extended-Typen.
Nicht vergebene Refs (historisch): B3, R10–R21, R23, R24, R27, R35, R36, R39–R44, C2–C9, C22, C31–C39, C63, C64, D4–D10, Q1–Q4, L1, T1, U2, U3, SW1, TP1–TP8, TP10.

---

## Änderungshistorie

- **Rev 1 (2026-10-21):** Skeleton aus Architektur (TPS23753A-Flyback, T1, Q1, U2/U3, D7–D10, L1; RGB-LED an +3V3).
- **Rev 2 (2026-10-21):** Refs/Werte final nach Sourcing; Kostenreduktion K1–K16 (Y1 Basic, Passive vereinheitlicht, T1 Consignment), R11 0,75 Ω, R25 44,2 k, C22 entfällt, RGB-LED an +5V mit Q2–Q4; 119 Positionen + T1.
- **Rev 3 (2026-10-22):** unverändert (verworfene 30-mm-Layoutvariante).
- **Rev 4 (2026-10-22):** diskreter Flyback (34 Refs) → U1 Ag9905LP (DIL); C11 Polymer, C1/C14/R8/R9 DNP; 104 Refs, 85 JLC + U1.
- **Rev 4b (2026-10-22):** D11 WS2812B, Q2–Q4/R39–R44/R5/R6 entfallen, J3 Tag-Connect statt TP1–TP8/TP10; 87 Refs, 76 JLC + U1.
- **Rev 4c (2026-10-22):** Brücken R45–R49 + Pads D2,0 – verworfen.
- **Rev 4d (2026-10-22):** R23, C63, R24, SW1, R27, J3 entfallen; TP1–TP4 neu; D11 an +3V3; 85 Refs, 72 JLC + U1.
- **Rev 4e (2026-10-23):** U1 Ag9905-LPB; TP1–TP4 → J3 SWD-Randpads; 82 Refs, 72 JLC + U1.
- **Rev 4e (2026-10-23):** U1 Ag9905-LPB (SMT, nur Top).
- **Rev 4e Review (2026-10-23):** + C65/C66 (K1); Y1 ABM8-272-T3, C25/C26 15 pF (H1); 84 Refs, 74 JLC + U1.
