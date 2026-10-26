# Sourced BOM – poe_usb_hid_bridge (Rev 4g)

Stand: 2026-10-26 · gültiger Endstand **Rev 4g** (= Rev 4e + D11 normale grüne LED, C64 entfällt [Rev 4f] + MagJack-LEDs wieder beschaltet mit R5/R6 [Rev 4g]; Netzliste `outputs/poe_usb_hid_bridge_rev4g.net`: **85 Referenzen, 46 Netze**, JLC-Export `outputs/fab_rev4g_final/`: 75 CPL-Positionen). Die Abgleich-Angaben unten beziehen sich auf Rev 4e; Rev 4f/4g unterscheiden sich nur in D11/C64/R5/R6.
Geprüft gegen die Netzliste `outputs/poe_usb_hid_bridge_rev4e.net` (SKiDL, 2026-10-23 11:35: **84 Referenzen, 42 Netze**), den KiCad-Schaltplan `kicad/poe_usb_hid_bridge_rev4e/*.kicad_sch`, das Board `poe_usb_hid_bridge_rev4e.kicad_pcb` und den JLC-Export `outputs/fab_rev4e_final/` (BOM/CPL 2026-10-23 11:45: 74 CPL-Positionen). Seite (T/B) aus dem Board.
Preise/Tiers: JLCPCB-Parts-API (2026-10-21/22, Preis-Staffel ≈ 10 Stk, USD); **Y1, C25/C26, C65/C66 live 2026-10-23**; U1: DigiKey live 2026-10-23. Stock ändert sich täglich – vor Bestellung neu prüfen.

## Mengen

| | Anzahl |
|---|---|
| Referenzen in Netzliste / Schaltplan / Board | **85** (Rev 4e nach Review: + C65, C66; Rev 4f: − C64; Rev 4g: + R5, R6) |
| DNP (Feld `DNP`) | 9: C1, C14, C30, R8, R9, R30, R31, J3 (SWD-Randpads), U1 (U1 = Beistellteil) |
| Test-Pad ohne Bauteil | TP9 (+5V) |
| **Bestückte Positionen bei JLC** | **75** (= 85 − 9 DNP − TP9; deckt sich mit der JLC-CPL) |
| Beistellteil | U1 Ag9905-LPB |
| **Bestückte Bauteile gesamt** | **76** |
| Extended-Typen (bestückt) | **20**: C19724786, C106172, C2487, C123816, C135491, C357023, C271260, C2868428, C43229502, C11692, C70593, C55266, C25895, C212682, C7519, C25100, C18077687, **C2962098 (D11 grün, Rev 4f)**, C20625731 (Y1), C93654 (C65/C66) |
| Preferred (ohne Gebühr) | C1557, C36871 |

## BOM (alle 85 Referenzen)

| Ref | Block | Funktion | Wert | MPN | Hersteller | LCSC | JLC-Tier | USD @10 | Footprint | Seite | Bestückung |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C1 | B2 | Eingangs-C (Option) | 100nF 100V X7R | CL21B104KCFNNNE | Samsung | C28233 | Basic | 0,0247 | `C_0805_2012Metric` | B | **DNP** |
| C10 | B2 | HF-C +5V_RAW | 100nF | CL05B104KO5NNNC | Samsung | C1525 | Basic | 0,0037 | `C_0402_1005Metric` | B | JLC |
| C11 | B2 | Modul-Ausgangs-C low-ESR | 100uF 10V polymer 15mR | SA11AM101A19R15XXX | AISHI | C135491 | Extended | 0,3974 | `CP_EIA-7343-31_Kemet-D` | B | JLC |
| C12 | B2 | Ausgangs-Keramik | 22uF 25V X5R | CL21A226MAQNNNE | Samsung | C45783 | Basic | 0,1837 | `C_0805_2012Metric` | B | JLC |
| C13 | B2 | Post-Filter-C | 22uF 25V | CL21A226MAQNNNE | Samsung | C45783 | Basic | 0,1837 | `C_0805_2012Metric` | B | JLC |
| C14 | B2 | Y2-Kap VSS–GND (Option) | 2.2nF 250VAC X1/Y2 | FK12X222K502EGQ | PSA | C53026446 | Extended | 0,5429 | `C_1812_4532Metric` | B | **DNP** |
| C15 | B4 | LDO-Eingang | 4.7uF | CL10A475KO8NNNC | Samsung | C19666 | Basic | 0,0197 | `C_0603_1608Metric` | T | JLC |
| C16 | B4 | LDO-Ausgang | 10uF | CL10A106KP8NNNC | Samsung | C19702 | Basic | 0,0272 | `C_0603_1608Metric` | T | JLC |
| C17 | B6 | U6-Eingang | 1uF 50V | CL10A105KB8NNNC | Samsung | C15849 | Basic | 0,0153 | `C_0603_1608Metric` | B | JLC |
| C18 | B6 | VBUS-Bulk | 150uF 6.3V | T520B157M006ATE035 | KEMET | C212682 | Extended | 0,5216 | `CP_EIA-3528-21_Kemet-B` | B | JLC |
| C19 | B6 | VBUS 10 µF | 10uF 10V | CL10A106KP8NNNC | Samsung | C19702 | Basic | 0,0272 | `C_0603_1608Metric` | B | JLC |
| C20 | B6 | VBUS HF | 100nF | CL05B104KO5NNNC | Samsung | C1525 | Basic | 0,0037 | `C_0402_1005Metric` | B | JLC |
| C21 | B1 | RX-AC-Mittelpunkt | 10nF | CL05B103KB5NNNC | Samsung | C15195 | Basic | 0,0041 | `C_0402_1005Metric` | B | JLC |
| C23 | B1 | CT-Abblock | 100nF | CL05B104KO5NNNC | Samsung | C1525 | Basic | 0,0037 | `C_0402_1005Metric` | B | JLC |
| C24 | B1 | Schirm-C 2 kV | 4.7nF 2kV | C1812X472K202T | IHHEC | C106172 | Extended | 0,201 | `C_1812_4532Metric` | B | JLC |
| C25 | B5 | Y1-Last (RPi-Referenz) | 15pF C0G | 0402CG150J500NT | FH | C1548 | Basic | 0,0038 | `C_0402_1005Metric` | T | JLC |
| C26 | B5 | Y1-Last (RPi-Referenz) | 15pF C0G | 0402CG150J500NT | FH | C1548 | Basic | 0,0038 | `C_0402_1005Metric` | T | JLC |
| C27 | B5 | Y2-Last | 27pF | 0402CG270J500NT | FH | C1557 | Preferred | 0,0026 | `C_0402_1005Metric` | T | JLC |
| C28 | B5 | Y2-Last | 27pF | 0402CG270J500NT | FH | C1557 | Preferred | 0,0026 | `C_0402_1005Metric` | T | JLC |
| C29 | B6 | VBUS_SENSE-Filter | 100nF | CL05B104KO5NNNC | Samsung | C1525 | Basic | 0,0037 | `C_0402_1005Metric` | B | JLC |
| C30 | B6 | USB-Schirm-C (Option) | 4.7nF | CL10B472KB8NNNC | Samsung | C1621 | Extended | 0,0097 | `C_0603_1608Metric` | B | **DNP** |
| C40 | B5 | IOVDD-Abblock | 100nF | CL05B104KO5NNNC | Samsung | C1525 | Basic | 0,0037 | `C_0402_1005Metric` | B | JLC |
| C41 | B5 | IOVDD-Abblock | 100nF | CL05B104KO5NNNC | Samsung | C1525 | Basic | 0,0037 | `C_0402_1005Metric` | B | JLC |
| C42 | B5 | IOVDD-Abblock | 100nF | CL05B104KO5NNNC | Samsung | C1525 | Basic | 0,0037 | `C_0402_1005Metric` | B | JLC |
| C43 | B5 | IOVDD-Abblock | 100nF | CL05B104KO5NNNC | Samsung | C1525 | Basic | 0,0037 | `C_0402_1005Metric` | B | JLC |
| C44 | B5 | IOVDD-Abblock | 100nF | CL05B104KO5NNNC | Samsung | C1525 | Basic | 0,0037 | `C_0402_1005Metric` | B | JLC |
| C45 | B5 | IOVDD-Abblock | 100nF | CL05B104KO5NNNC | Samsung | C1525 | Basic | 0,0037 | `C_0402_1005Metric` | B | JLC |
| C46 | B5 | +3V3-Bulk | 10uF | CL10A106KP8NNNC | Samsung | C19702 | Basic | 0,0272 | `C_0603_1608Metric` | B | JLC |
| C47 | B5 | VREG_VIN | 1uF | CL05A105KA5NQNC | Samsung | C52923 | Basic | 0,0075 | `C_0402_1005Metric` | B | JLC |
| C48 | B5 | VREG_VOUT | 1uF | CL05A105KA5NQNC | Samsung | C52923 | Basic | 0,0075 | `C_0402_1005Metric` | B | JLC |
| C49 | B5 | DVDD | 100nF | CL05B104KO5NNNC | Samsung | C1525 | Basic | 0,0037 | `C_0402_1005Metric` | B | JLC |
| C50 | B5 | DVDD | 100nF | CL05B104KO5NNNC | Samsung | C1525 | Basic | 0,0037 | `C_0402_1005Metric` | B | JLC |
| C51 | B5 | USB_VDD | 100nF | CL05B104KO5NNNC | Samsung | C1525 | Basic | 0,0037 | `C_0402_1005Metric` | B | JLC |
| C52 | B5 | ADC_AVDD | 100nF | CL05B104KO5NNNC | Samsung | C1525 | Basic | 0,0037 | `C_0402_1005Metric` | B | JLC |
| C53 | B5 | VDD_FLASH | 100nF | CL05B104KO5NNNC | Samsung | C1525 | Basic | 0,0037 | `C_0402_1005Metric` | B | JLC |
| C54 | B5 | W5500-VDD | 100nF | CL05B104KO5NNNC | Samsung | C1525 | Basic | 0,0037 | `C_0402_1005Metric` | B | JLC |
| C55 | B5 | AVDD-Abblock | 100nF | CL05B104KO5NNNC | Samsung | C1525 | Basic | 0,0037 | `C_0402_1005Metric` | B | JLC |
| C56 | B5 | AVDD-Abblock | 100nF | CL05B104KO5NNNC | Samsung | C1525 | Basic | 0,0037 | `C_0402_1005Metric` | B | JLC |
| C57 | B5 | AVDD-Abblock | 100nF | CL05B104KO5NNNC | Samsung | C1525 | Basic | 0,0037 | `C_0402_1005Metric` | B | JLC |
| C58 | B5 | AVDD-Abblock | 100nF | CL05B104KO5NNNC | Samsung | C1525 | Basic | 0,0037 | `C_0402_1005Metric` | B | JLC |
| C59 | B5 | AVDD-Abblock | 100nF | CL05B104KO5NNNC | Samsung | C1525 | Basic | 0,0037 | `C_0402_1005Metric` | B | JLC |
| C60 | B5 | +3V3A-Bulk | 10uF | CL10A106KP8NNNC | Samsung | C19702 | Basic | 0,0272 | `C_0603_1608Metric` | B | JLC |
| C61 | B5 | TOCAP | 4.7uF | CL10A475KO8NNNC | Samsung | C19666 | Basic | 0,0197 | `C_0603_1608Metric` | T | JLC |
| C62 | B5 | 1V2O | 10nF | CL05B103KB5NNNC | Samsung | C15195 | Basic | 0,0041 | `C_0402_1005Metric` | B | JLC |
| C65 | B1 | ETH-RX-Koppel-C P (K1, in Serie J1.4 ↔ ETH_RXP) | 6.8nF 50V X7R | CC0402KRX7R9BB682 | YAGEO | C93654 | Extended | 0,0021 | `C_0402_1005Metric` | B | JLC |
| C66 | B1 | ETH-RX-Koppel-C N (K1, in Serie J1.5 ↔ ETH_RXN) | 6.8nF 50V X7R | CC0402KRX7R9BB682 | YAGEO | C93654 | Extended | 0,0021 | `C_0402_1005Metric` | B | JLC |
| D1 | B2 | Brücke Mode A | MB6S | MDD MB6S-50MIL | MDD | C2487 | Extended | 0,0277 | `TO-269AA` | B | JLC |
| D2 | B2 | Brücke Mode B | MB6S | MDD MB6S-50MIL | MDD | C2487 | Extended | 0,0277 | `TO-269AA` | B | JLC |
| D3 | B2 | TVS 58 V | SMAJ58A | MDD SMAJ58A | MDD | C123816 | Extended | 0,0453 | `D_SMA` | B | JLC |
| D11 | B7 | Status-LED grün (aktiv-high an GPIO28 über R38) | green | MHT193CGCT (569 nm, Vf 2,2 V, 11,2 mcd @ 5 mA) | MEIHUA | C2962098 | Extended | 0,0439 | `LED_0603_1608Metric` | T | JLC |
| D12 | B2 | OVP-Zener +5V | BZT52C6V2 | BZT52C6V2 | BORN | C271260 | Extended | 0,0175 | `D_SOD-123` | B | JLC |
| FB1 | B2 | Post-Filter-Ferrit | 600R 3A | HCB3216KF-601T30 | TAI-TECH | C357023 | Extended | 0,0545 | `L_1206_3216Metric` | B | JLC |
| FB2 | B5 | +3V3A-Ferrit | 120R@100MHz | BLM18PG121SN1D | Murata | C14709 | Basic | 0,0152 | `L_0603_1608Metric` | B | JLC |
| J1 | B1 | RJ45-PoE-MagJack (THT) | HR871150C | HanRun HR871150C | HanRun | C19724786 | Extended | 2,08 | `HanRun_HR871150C` | T | JLC |
| J2 | B6 | USB-A-Buchse | BX-TYPE-A-MWT4P | BX-TYPE-A-MWT4P | Bossie | C18077687 | Extended | 0,12 | `BX-TYPE-A-MWT4P` | T | JLC |
| R1 | B1 | ETH TX-Bias | 49.9R | 0402WGF499JTCE | UNI-ROYAL | C25120 | Basic | 0,0023 | `R_0402_1005Metric` | T | JLC |
| R2 | B1 | ETH TX-Bias | 49.9R | 0402WGF499JTCE | UNI-ROYAL | C25120 | Basic | 0,0023 | `R_0402_1005Metric` | T | JLC |
| R3 | B1 | ETH RX-Term. | 49.9R | 0402WGF499JTCE | UNI-ROYAL | C25120 | Basic | 0,0023 | `R_0402_1005Metric` | B | JLC |
| R4 | B1 | ETH RX-Term. | 49.9R | 0402WGF499JTCE | UNI-ROYAL | C25120 | Basic | 0,0023 | `R_0402_1005Metric` | B | JLC |
| R5 | B1 | MagJack-LED gelb (Activity), Anoden-R an +3V3 (Rev 4g) | 330R | 0402WGF3300TCE | UNI-ROYAL | C25104 | Basic | 0,0011 | `R_0402_1005Metric` | B | JLC |
| R6 | B1 | MagJack-LED grün (Link), Anoden-R an +3V3 (Rev 4g) | 330R | 0402WGF3300TCE | UNI-ROYAL | C25104 | Basic | 0,0011 | `R_0402_1005Metric` | B | JLC |
| R7 | B1 | Schirm-Ableit-R | 1M | 0603WAF1004T5E | UNI-ROYAL | C22935 | Basic | 0,0021 | `R_0603_1608Metric` | B | JLC |
| R8 | B2 | Mindestlast RB (Option) | 100R 1206 | 1206W4F1000T5E | UNI-ROYAL | C17901 | Basic | 0,0059 | `R_1206_3216Metric` | B | **DNP** |
| R9 | B2 | ADJ-Trimm (Option) | DNP (ADJ trim) | – | – | – | – | – | `R_0603_1608Metric` | B | **DNP** (Wert am Muster) |
| R22 | B5 | EXRES1 | 12.4k | 0402WGF1242TCE | UNI-ROYAL | C11692 | Extended | 0,0013 | `R_0402_1005Metric` | B | JLC |
| R25 | B6 | R_ILIM | 44.2k | 0402WGF4422TCE | UNI-ROYAL | C25895 | Extended | 0,0017 | `R_0402_1005Metric` | B | JLC |
| R26 | B6 | EN-Pull-down | 100k | 0402WGF1003TCE | UNI-ROYAL | C25741 | Basic | 0,0015 | `R_0402_1005Metric` | B | JLC |
| R28 | B6 | USB-Serien-R | 27 | 0402WGF270JTCE | UNI-ROYAL | C25100 | Extended | 0,0013 | `R_0402_1005Metric` | T | JLC |
| R29 | B6 | USB-Serien-R | 27 | 0402WGF270JTCE | UNI-ROYAL | C25100 | Extended | 0,0013 | `R_0402_1005Metric` | T | JLC |
| R30 | B6 | Host-Pull-down (Option) | 15k | 0402WGF1502TCE | UNI-ROYAL | C25756 | Basic | 0,001 | `R_0402_1005Metric` | B | **DNP** |
| R31 | B6 | Host-Pull-down (Option) | 15k | 0402WGF1502TCE | UNI-ROYAL | C25756 | Basic | 0,001 | `R_0402_1005Metric` | B | **DNP** |
| R32 | B6 | VBUS-Teiler oben | 100k | 0402WGF1003TCE | UNI-ROYAL | C25741 | Basic | 0,0015 | `R_0402_1005Metric` | B | JLC |
| R33 | B6 | VBUS-Teiler unten | 68k | 0402WGF6802TCE | UNI-ROYAL | C36871 | Preferred | 0,002 | `R_0402_1005Metric` | B | JLC |
| R34 | B6 | USB-Schirm 0 Ω | 0R | 0603WAF0000T5E | UNI-ROYAL | C21189 | Basic | 0,0022 | `R_0603_1608Metric` | B | JLC |
| R37 | B5 | XOUT-Serien-R | 1k | 0402WGF1001TCE | UNI-ROYAL | C11702 | Basic | 0,0013 | `R_0402_1005Metric` | T | JLC |
| R38 | B7 | LED-Daten-Serien-R | 330R | 0402WGF3300TCE | UNI-ROYAL | C25104 | Basic | 0,0011 | `R_0402_1005Metric` | B | JLC |
| J3 | B5 | SWD-Randpads (1 SWCLK, 2 GND, 3 SWDIO, 4 +3V3) für 1×4-Stiftleiste 2,54 mm | SWD | – | – | – | – | – | `poe_usb_hid_bridge:SWD_Edge_1x04_P2.54mm_SMD` | T | **DNP** (nur Pads; Stiftleiste von Hand, z. B. Standard 1×4 2,54 mm) |
| TP9 | B2 | Test-Pad +5V | TP_+5V | – | – | – | – | – | `TestPoint_Pad_D1.0mm` | B | Pad (keine Bestückung) |
| U1 | B2 | PoE-PD-Modul 5 V Class 0 | Ag9905-LPB | Ag9905-LPB (Rolle: Ag9905-LPB-15TR) | Silvertel | – (C5373039 Stock 0) | Beistellteil | 9,00 (DigiKey @1) | `Silvertel_Ag9900LPB_SMD` | T | **Beistellteil** (DNP im JLC-Export) |
| U4 | B4 | LDO 3,3 V | TLV75733PDRVR | TLV75733PDRVR | TI | C2868428 | Extended | 0,30 | `WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm` | T | JLC |
| U5 | B5 | MCU + Ethernet SiP | W55RP20 | W55RP20 | WIZnet | C43229502 | Extended | 4,27 | `W55RP20_QFN-68-1EP_8x8mm_P0.4mm_EP6.2x6.2mm` | T | JLC (**reservieren**) |
| U6 | B6 | USB-Lastschalter | TPS2553DBVR | TPS2553DBVR | TI | C55266 | Extended | 0,4515 | `SOT-23-6` | B | JLC |
| U7 | B6 | USB-ESD | USBLC6-2SC6 | USBLC6-2SC6 | ST | C7519 | Extended | 0,1786 | `SOT-23-6` | B | JLC |
| Y1 | B5 | Quarz 12 MHz (H1, RPi-Referenz) | 12MHz 10pF | ABM8-272-T3 | Abracon | C20625731 | Extended | 0,5315 | `Crystal_SMD_3225-4Pin_3.2x2.5mm` | T | JLC |
| Y2 | B5 | Quarz 25 MHz | 25MHz 18pF | X322525MRB4SI | YXC | C70593 | Extended | 0,099 | `Crystal_SMD_3225-4Pin_3.2x2.5mm` | T | JLC |

## Beistell- und Engpass-Teile

- **U1 Silvertel Ag9905-LPB:** JLC/LCSC C5373039 Stock 0 (11,45 USD) → **Beistellteil**. DigiKey 5061-AG9905-LPB-ND: 1 713 Stk, 9,00 USD @1 / 8,75 @100 (live 2026-10-23, 16 Wochen Werkslieferzeit); Farnell 4472714 ≈ 211 Stk (Snapshot, unverifiziert); Mouser kein Listing gefunden. Rolle Ag9905-LPB-15TR: MOQ 400, 9,24 USD. MSL 1, Reflow J-STD-020, **nur Oberseite**. Bestückung per JLC-Consignment (SMT) oder Handreflow (Heissluft/Hotplate). Nicht verwechseln mit Ag9905-MTB (13,4 mm hoch) oder Ag9905LP (DIL, anderes Pinout).
- **U5 W55RP20 (C43229502):** Bestand bei JLC knapp (2026-10-21: 94 Stk, **live 2026-10-23: 89 Stk**) → **sofort bei JLC reservieren**. MSL 3.
- **Bestände live 2026-10-23 (2. Review):** ABM8-272-T3 C20625731 3 388 · HR871150C C19724786 328 · USB-A BX-TYPE-A-MWT4P C18077687 488.
- **U1-Consignment:** U1 ist im JLC-Export DNP → für die Consignment-Bestückung U1 in BOM und CPL aufnehmen. Paste wird auch auf die DNP-Pads (U1, C1, C14, R8, R9, C30) gedruckt.
- **D11 MEIHUA MHT193CGCT (C2962098, Extended, Rev 4f):** normale grüne 0603-LED, JLC-Stock 2026-10-26: 21 793 Stk. Bewusst AlGaInP/569 nm mit Vf ≈ 2,2 V – „echt grüne" InGaN-LEDs (≈ 3 V) hätten an 3,3 V über R38 kaum Strom. Ersetzt die WS2812B-2020-V6 (kein Backen mehr nötig). Polarität (Kathode = Pad 1) im JLC-Placement-Viewer prüfen.
- **Y1 Abracon ABM8-272-T3 (C20625731, Extended):** JLC-Stock 2026-10-23: 4 388 Stk (später am Tag 3 388), 0,5315 USD @10 – für 5–10 Boards ausreichend. Ersetzt seit dem Review (H1) den YXC X322512MSB4SI (C9002, 20 pF), damit Quarz, Lasten (2 × 15 pF) und R37 1 kΩ genau der Raspberry-Pi-Referenz entsprechen.
- **C65/C66 6,8 nF (C93654, Extended):** kein Basic-Typ mit 6,8 nF/0402 verfügbar; JLC-Stock 2026-10-23: 329 566 Stk.
- **J1 HR871150C:** THT, wird von JLC wellen-/handgelötet; Single Source (Stock 2026-10-21: 348, 2026-10-23: 328).
- **R9:** kein Wert festgelegt (ADJ-Abgleich am Muster, z. B. Basic 0603WAF-Reihe).

## Kosten (Prototyp)

| Posten | USD |
|---|---|
| Bauteile bei JLC (75 Positionen, ohne U1/DNP/Pads) | **≈ 10,06 /Board** (Summe aus obiger Tabelle; davon Y1 0,53; R5/R6 Rev 4g +0,002) |
| Extended-Aufschlag 20 Typen × ≈ 3 USD | ≈ 60 /Bestellung (10 Stk: 6,00 /Board; 5 Stk: 12,00 /Board) |
| U1 Ag9905-LPB (DigiKey) | 9,00 /Board |
| **Summe bei 10 Stk** | **≈ 25,06 /Board** (Rev 4e 25,11: D11 −0,05, C64 entfällt) |
| **Summe bei 5 Stk** | **≈ 31,06 /Board** (Rev 4e 31,11) |
| Nicht enthalten | PCB (6 Lagen, 20 × 80 mm, Impedanz, Via-in-Pad), Bestückungsgrundgebühr, THT-Aufschlag J1, Consignment-Gebühr U1, Versand |

## Abgleich mit Schaltplan und Netzliste (2026-10-23)

- Referenzen: Netzliste = KiCad-Schaltplan = Board = 84, keine fehlenden oder zusätzlichen Refs; JLC-CPL 74 Positionen, JLC-BOM enthält C65/C66 (C93654), C25/C26 (C1548) und Y1 (C20625731).
- Werte, Footprints, MPN, LCSC: in allen Quellen identisch.
- DNP: XML-Feld `DNP` deckt sich mit KiCad `(dnp yes)` / `exclude_from_bom`. **Ausnahme U1:** im Schaltplan `dnp yes`, aber `in_bom yes` (bewusst: erscheint in der BOM als Beistellteil, nicht in der CPL).
- TP9 hat weder DNP noch LCSC (reines Pad) – im JLC-BOM-Export ausfiltern bzw. als „nicht bestücken" behandeln.

---

## Änderungshistorie

- **Rev 1 (2026-10-21):** Erst-Sourcing über JLC-API (pcbparts-MCP nicht verfügbar): 50 Extended-Typen, ≈ 30 USD Bauteile/Board; J1 HY931147C → HR871150C ersetzt (Höhe/Stock).
- **Rev 2 (2026-10-21):** Kostenreduktion K1–K16 (18 Extended-Typen weniger, Y1 Basic-Quarz, Passive vereinheitlicht), T1 POE70P-50LD als Consignment, R25 44,2 k, D12 BZT52C6V2 (M1); 119 bestückte Positionen + T1, ≈ 23–26 USD/Board bei 10 Stk.
- **Rev 3 (2026-10-22):** Layoutvariante 30 × 80 mm – BOM unverändert, verworfen.
- **Rev 4 (2026-10-22):** Diskreter Flyback (TPS23753A, T1, Q1, U2, U3, D7–D10, L1, C2–C9, C31–C33, R10–R20, R35/R36/R41; 34 Refs) entfällt; U1 Ag9905LP (DIL, Consignment), C11 Polymer 100 µF; 85 Positionen + U1, 19 Extended-Typen.
- **Rev 4b (2026-10-22):** D11 WS2812B-2020-V6 statt E6C0606 + Q2–Q4/R39–R44; R5/R6 entfallen; J3 Tag-Connect-Pad-Feld (DNP); 76 Positionen + U1.
- **Rev 4c (2026-10-22):** 0-Ω-Brücken (C17168) und Pads D2,0 – verworfen, nicht übernommen.
- **Rev 4d (2026-10-22):** R23, C63, R24, SW1 (KMR211NGLFS), R27, J3 entfallen; TP1–TP4 neu; 72 Positionen + U1, 18 Extended-Typen.
- **Rev 4e (2026-10-23):** U1 Ag9905-LPB; TP1–TP4 → J3 SWD-Randpads (DNP, kein BOM/CPL); 82 Refs, weiterhin 72 Positionen + U1, Kosten unverändert.
- **Rev 4e (2026-10-23):** U1 Ag9905-LPB (SMT) statt Ag9905LP (DIL, nicht lieferbar); Modulpreis 9,00 statt 9,50/9,75 USD.
- **Rev 4e Review (2026-10-23):** K1: + C65/C66 6,8 nF X7R 0402 (C93654) als RX-Koppel-C; H1: Y1 ABM8-272-T3 (C20625731) statt X322512MSB4SI, C25/C26 15 pF (C1548) statt 33 pF. 84 Refs, 74 Positionen + U1, 20 Extended-Typen; ≈ 25,11 USD/Board bei 10 Stk.
- **Rev 4f (2026-10-26):** D11 WS2812B-2020-V6 (C52917434) → normale grüne 0603-LED MEIHUA MHT193CGCT (C2962098), aktiv-high an GPIO28 über R38 330 Ω (≈ 3,5 mA); C64 (LED-Abblock) entfällt. 83 Refs, 73 Positionen + U1, weiterhin 20 Extended-Typen; ≈ 25,06 USD/Board bei 10 Stk.
- **Rev 4g (2026-10-26):** MagJack-LEDs wieder beschaltet: R5/R6 330 Ω (C25104, Basic, Unterseite neben J1) an +3V3, Kathoden an U5 LINKLED (grün) / ACTLED (gelb). 85 Refs, 75 Positionen + U1, weiterhin 20 Extended-Typen; Kosten praktisch unverändert (≈ 25,06 USD/Board bei 10 Stk).
