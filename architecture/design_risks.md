# Design Risks – poe_usb_hid_bridge (Rev 4e)

Stand: 2026-10-26 · gültiger Endstand **Rev 4g**. Bewertung: **H** hoch (kann Funktion/Fertigung verhindern), **M** mittel (Nacharbeit wahrscheinlich), **N** niedrig.

## 1. Offene Risiken

### Isolation
| ID | Risiko | Bew. | Massnahme | Stufe |
|---|---|---|---|---|
| R-ISO-1 | 3 mm Abstand primär ↔ sekundär auf allen 6 Lagen | M | Rule-Areas `ISO_BAND`/`ISO_BAND_J1`, DRU `ISO_PRI_SEC_3mm`, gestufter Keepout im U1-Footprint; DRC Rev 4e 0 Fehler | erledigt (Layout) |
| R-ISO-3 | J1-Footprint: Kriechstrecke Pad 5 ↔ 7 nur 1,24 mm, SH ↔ Pin 10 1,97 mm (< 3 mm) | M | **Vom User akzeptierte Abweichung (Review M4):** Pads 5/7/10 auf Ø 1,3 mm verkleinert, Keepout `ISO_KEEPOUT_PRI_SEC` zwischen P7 und P4/P5, Lötstopp-Steg; HR871150C-DS: 2250 VDC / 1500 Vrms. **Hipot am Muster** | Muster |
| R-ISO-5 | Isolation zum Rohr: Wärmeleitpad/Board-Kante an einem **Aluminiumrohr** überbrückt die 1500-V-Isolation (Primärkupfer ↔ Rohr ↔ Sekundär) | **entschärft** | Gehäuse ist ein **Kunststoffrohr** (User-Entscheidung 2026-10-23) → kein leitfähiges Gehäuse, Isolation zum Rohr unkritisch. Gilt nur, solange kein Metallrohr/keine Metallkappe verwendet wird | – |
| R-ISO-7 | J1-intern Bob-Smith-Bus → 1 nF/2 kV → Schirm → C24 4,7 nF → GND = einziger bestückter Y-Pfad (≈ 0,8 nF); beim Hipot ≈ 1,75 kV am internen 1 nF | M | Hipot 1500 VAC / 60 s am Muster; Option C24 DNP (nur R7). Hinweis: Das Modul selbst ist laut DS V3.5 nur für den **1500-V-DC-Impulstest** spezifiziert (IEC 60950 6.2 b) – Prüfart abstimmen | Muster |
| R-ISO-8 | **R7 (1 MΩ, 0603) im Hipot überlastet:** ohne C24 (bzw. bei DC-Hipot) liegt fast die volle Prüfspannung über R7; 0603 ist nur für ≈ 50–75 V Arbeitsspannung spezifiziert → Überschlag/Schaden möglich (Review, nicht umgesetzt) | M | **Empfehlung:** R7 als 1206-HV-Widerstand (≥ 1,5–2 kV, z. B. Hochspannungs-Dickschicht) bestücken; bis dahin Hipot nur mit Bewusstsein dieses Pfads | offen (Empfehlung) |
| R-ISO-9 | **Abstände primär ↔ sekundär < 3 mm innerhalb der J1-Ausnahme** (`ISO_BAND_J1`/Courtyard 1,0 mm; Review, nicht umgesetzt): ETH_RXN (sekundär) 1,8 mm zu J1.7 (PSE_CT12); zusätzlich laut 2. Review (Isolation N-1): **PSE_CT12 ↔ J1.5 1,74 mm (In1)**, **PSE_SP78 ↔ J1-SH 2,47 mm (In2)**, **J1.8 ↔ ETH_RXN_J 2,95 mm (B.Cu)** | M | als Teil der akzeptierten J1-Abweichung (R-ISO-3) führen; Hipot am Muster deckt die Pfade mit ab; nächste Revision: Innenlagen-Leiterbahnen um J1 auf ≥ 3 mm ziehen | Muster |
| R-ISO-10 | **Rev 4g: MagJack-LED-Leitung ETH_LED_LINK_N** (sekundär, In3) läuft durch das J1-Pinfeld und kommt bis **2,23 mm** an J1.7 (PSE_CT12) heran (114,05/109,2 → 119,3/108,4); DRC-konform nur über `ISO_EXC_J1` (≥ 1,0 mm). ETH_LED_ACT_N hält > 3 mm. | M | als Teil der J1-Ausnahme (R-ISO-3/-9) führen; Hipot 1500 VAC am Muster deckt den Pfad ab; Alternative: Link-LED unbeschaltet lassen | Muster |

### Power / PoE-Modul
| ID | Risiko | Bew. | Massnahme | Stufe |
|---|---|---|---|---|
| **R4-1** | **Modul-Derating** 7 W ≤ 70 °C, **4,5 W @ 85 °C**. Bei 40 °C Umgebung im Kunststoffrohr ≈ 68–80 °C Innentemperatur → USB-Fehlerfall (4,52 W) noch knapp unter der 70-°C-Kennlinie; bei 50 °C Umgebung (78–90 °C) an der Grenze → Thermoschutz, +5V-Einbruch/Reset | **M** (bei ≤ 40 °C) / H (bei 50 °C) | OD-11 (Kunststoffrohr: **Umgebung ≤ 40 °C**), +VDC/−VDC-Kupferflächen beidseitig + Vias, FW schaltet `USB_EN` bei Überlast (Einbruch an `VBUS_SENSE`) ab; **Temperaturmessung am Muster** | Mechanik/FW/Muster |
| **R4-2** | +5V-Toleranz 4,75–5,25 V → VBUS am Port **Worst Case ≈ 4,6 V @ 500 mA** (Modul 4,75 V − FB1 − TPS2553 R_DS(on) heiss; Review) – < 4,75 V USB-Spec | M | R9 (ADJ → GND, DNP) am Muster abgleichen, Ziel +5V_RAW ≈ 5,10 V. **Obergrenze: +5V_RAW ≤ 5,25 V** (Modul-Spezifikation); **R9 = 0 Ω → 5,65 V ist unzulässig** (über der Modul-/USB-Grenze, D12 würde nahe an die Klemmung kommen). R9 nur in Schritten von oben (hochohmig) her bestimmen | Muster |
| **R4-3** | Detection-Kapazität: externer C1 könnte C_det > 0,12 µF ergeben | M | **C1 DNP**; nur nach Detection-Test mit 2–3 PSEs bestücken | Muster |
| **R4-4** | Mindestlast 200 mA vs. Leerlauf ≈ 180 mA (Link) / ≈ 100 mA (ohne Link) → Geräusch | M | R8 (100 Ω, DNP) nur bei Bedarf (+0,25 W); MPS mit ≈ 20–30 mA erfüllt | Muster |
| R4-8 | Ausgangs-Ripple/ESR bei Kälte | N | Polymer C11 (15 mΩ) | – |
| R-PI-6 | USB-Hotplug mit grosser Eingangskapazität | N | TPS2553-Begrenzung, C18 150 µF, LDO-Headroom 1,7 V | – |
| R-PI-7 | Start-up mit USB-Last | N | `USB_EN` per R26 bis FW-Start low | – |
| R-PI-11 | **PSE-Anforderung:** Das Modul braucht eine normgerechte **IEEE-802.3af/at-PSE (≥ 48 V nominal**, Detection/Classification, Anlauf ≥ 42 V). Passive 24-V-PoE-Injektoren (z. B. vieler WLAN-Geräte) funktionieren **nicht** (UVLO 30–36 V) | M | in README/Bestell- und Inbetriebnahme-Checkliste dokumentiert; Router/Switch vor dem Einsatz prüfen | Doku/User |
| R-PI-12 | **Abblockung W5500-VDD (U5.42) und IOVDD (U5.43) > 5 mm** vom Pin entfernt (Review, nicht umgesetzt) | N–M | am Muster Ripple an +3V3 nahe U5 und Ethernet-Stabilität prüfen; bei Problemen 100 nF direkt an Pin 42/43 nachrüsten (nächste Revision) | Muster |
| R-PI-13 | LDO U4 ohne Thermal-Vias im EP (1. Review) | **behoben** | 2026-10-23 im Layout ergänzt: **3 Vias 0,45/0,3 im EP** (49,15/14,04; 49,15/14,60; 49,15/15,16) + **2 GND-Vias südlich des Pads** (49,40/16,10; 48,75/16,25). EP-Vias stehen auf der POFV-Liste (R-LAY-5). Temperatur U4 am Muster trotzdem messen | erledigt |

### Modul U1 Ag9905-LPB
| ID | Risiko | Bew. | Massnahme | Stufe |
|---|---|---|---|---|
| R4e-1 | Pinout weicht von LP ab (5 statt 8 Pins); Verwechslung LP/LPB/MTB | M | Eigenes Symbol `Ag9905-LPB` + Footprint `Silvertel_Ag9900LPB_SMD`; Netzliste geprüft (1 +5V_RAW, 2 GND, 3 AG_ADJ, 4 VDD_POE, 5 VSS); Layout neu zugeordnet | erledigt |
| R4e-2 | Footprint aus DS-Zeichnung (Fig. 21, Top-View aus gespiegelter Bottom-View Fig. 2) | M | **1:1-Ausdruck gegen das echte Modul vor der Bestellung**; Pin-1-Dreieck im Bestückungsdruck | vor Bestellung |
| R4e-3 | Gestufter Isolations-Keepout bis 1 mm unter die Körperkante | M | DRC Rev 4e 0 Fehler | erledigt |
| R4e-4 | Löten: bottom-terminiertes 21-mm-Modul, JLC-Bestand 0 | M | JLC-Consignment-SMT bevorzugt, sonst Heissluft/Hotplate; **nur Top**. Alternativ-Footprint `_HandSolder` in der Bibliothek | Fertigung |
| R4e-5 | Wärme nur über die Pads | N–M | +VDC/−VDC-Kupferflächen mit Vias, Via-in-Pad an Pad 1 (gefüllt/gedeckelt bestellen) | Fertigung |
| R4-6 | Beschaffung (Single Source) | N | DigiKey 1 713 Stk (2026-10-23), 9,00 USD; Farnell als Zweitquelle (unverifiziert) | Sourcing |

### Thermik
| ID | Risiko | Bew. | Massnahme | Stufe |
|---|---|---|---|---|
| R-TH-1 | **W55RP20 Tc,max 85 °C**. Kunststoffrohr leitet schlechter ab als Alu (innen ≈ +5–10 K): bei **40 °C Umgebung ≈ 68–80 °C** Board-/Lufttemperatur (Reserve 5–17 K), bei 50 °C Umgebung 78–90 °C (Grenzwert verletzt) | **M** (bei ≤ 40 °C) / H (bei 50 °C) | **Umgebung ≤ 40 °C** (Betriebsvorgabe), Lüftungsschlitze in den Endkappen, ggf. Takt senken; **Thermoelement am Muster** (U1, U5, U4, J1) bei Volllast und USB-Kurzschluss | Mechanik/User (OD-11)/Muster |
| R-TH-3 | LDO-Verlust 0,31–0,48 W | N–M | EP jetzt mit 3 Thermal-Vias + 2 GND-Vias (R-PI-13 behoben); Messung am Muster; Buck als spätere Option | Muster |
| R-TH-4 | USB-Kurzschluss → U6 taktet thermisch | N | FW: bei `VBUS_SENSE` **< ≈ 4,0–4,2 V** (gemittelt, **> 50 ms entprellt**) `USB_EN` abschalten, Retry mit Backoff. Nicht 4,5 V: im Normalbetrieb ist VBUS Worst Case ≈ 4,6 V → Fehlauslösung | Firmware |
| R-TH-6 | **Höhenreserven im Rohr:** D3 (SMA, Bottom) nur ≈ 0,25 mm Reserve zur Rohrwand; J2 laut Datenblatt 15,2 mm breit (Laschen) / 7,0 mm hoch (2. Review) | M | `mechanical_concept.md` korrigiert; Einbau am Muster prüfen; nächste Revision: D3 näher an die Board-Mitte | Muster/Mechanik |
| R-TH-5 | **HR871150C nur 0…+70 °C**; J1 sitzt an der Kappenöffnung (kühlste Stelle), bei 40 °C Umgebung erwartet ≈ 55–65 °C | **M** (bei ≤ 40 °C) / H (bei 50 °C) | OD-11 Pflicht (≤ 40 °C). Alternative −40…+85 °C: HR873168AE (Masse prüfen) | User/Mechanik/Muster |

### Layout / Fertigung
| ID | Risiko | Bew. | Massnahme | Stufe |
|---|---|---|---|---|
| R-LAY-1 | Hohe Via-Dichte unter U5 (QFN-68 P0,4) | M | Rule-Area `U5_FANOUT`: im Board nur **3 Vias 0,4/0,2 mm** mit 0,1 mm Abstand – lösen trotzdem den JLC-Aufpreis für 0,2-mm-Bohrungen aus (Review: prüfen, ob sie sich durch 0,45/0,3 ersetzen lassen, dann entfällt der Aufpreis); ausserhalb 0,45/0,3 | Bestellung |
| R-LAY-5 | **POFV-Liste (Via-in-Pad gefüllt/gedeckelt):** Vias in Pads sind im Board nicht als Filling/Capping attributiert | M | bei der Bestellung „Via-in-Pad (POFV)" wählen und die Liste beilegen (x/y mm). *Via-Mitte im Pad:* U1 Pad 1 × 2 (41,6/4,2; 42,4/4,2), C52.1 (62,32/13,56), U4-EP × 3 (49,15/14,04; 49,15/14,60; 49,15/15,16). *Via-Rand berührt Pad:* U5.54 (60,79/12,25), C55.1 (59,34/4,68), R22.1 (57,05/4,2), C50.2 (49,6/10,3). Sonst Lot-Absaugung | Bestellung |
| R-LAY-6 | Wenig GND-Stitching im USB-Bereich (1. Review) | **entschärft** | 2026-10-23 **5 GND-Stitching-Vias** ergänzt (66,25/5,25; 68,50/12,50; 70,75/9,00; 69,25/13,75; 72,75/13,25); USB-FS ist tolerant, Signalqualität/EMV am Muster prüfen | Muster |
| R-LAY-8 | **Bohrdaten-Nullpunkt ≠ Gerber-Nullpunkt** (Versatz 100 mm) im ersten Fab-Export | **behoben** | 2026-10-23 mit `--drill-origin plot` neu exportiert, ZIP neu gepackt (`outputs/fab_rev4e_final`, 13:47). Board-Plotparameter `drillshape=1` → bei Export mit `--board-plot-params` Bohrmarken; nicht verwenden oder `drillshape` 0 | erledigt / Export-Regel |
| R-LAY-9 | **CPL-Rotationen** sind KiCad-Winkel; JLC-Bibliotheksteile haben teils andere Nulllagen | M | im JLC-Placement-Viewer prüfen, besonders U5, U4, U6, U7, C11, C18, D1–D3, D12, D11, Y1/Y2; **Y1/Y2 nach Datenblatt-Pin-1, nicht nach Fase** (90°-Fehllage legt die Quarzpins auf GND) | Bestellung |
| R-LAY-10 | **Paste auf DNP-Pads** (U1, C1, C14, R8, R9, C30) wird gedruckt | N | akzeptieren (U1-Consignment braucht sie); für U1-Consignment U1 in BOM/CPL aufnehmen | Bestellung |
| R-LAY-11 | J1-Footprint lokal angepasst (ISO, R-ISO-3) → DRC `lib_footprint_mismatch` | N | **nicht „Footprints aus Bibliothek aktualisieren"** bei J1, sonst gehen die ISO-Anpassungen verloren | Layout |
| R-LAY-7 | **C61 (TOCAP) nicht direkt am Pin U5.33** (Review; DS fordert kürzeste Verbindung ohne Via) | M | am Muster Stabilität der W5500-1,2-V-Regelung/Ethernet (Link, Paketverlust) prüfen; nächste Revision: C61 direkt an Pin 33 | Muster |
| R-LAY-2 | W55RP20-Land-Pattern im DS „TBD" | M | Footprint gegen DS-Masse (EP 6,2, Pitch 0,4) geprüft; 1:1-Ausdruck | vor Bestellung |
| R-LAY-4 | THT-Pins J1 auf Bottom | N | Bottom-SMDs mit Abstand; JLC-THT-Lötservice | Fertigung |
| R4b-1 | ~~D11 MSL 5a~~ – entfällt mit Rev 4f (D11 normale 0603-LED); Polarität (K = Pad 1) im JLC-Viewer prüfen | N | Placement-Viewer | Fertigung |
| R-AV-2 | W55RP20 Single Source, **JLC-Bestand live 2026-10-23 nur 89 Stk** (C43229502) | **M–H** | **Bei JLC sofort reservieren.** Weitere Bestände (live 2026-10-23): ABM8-272-T3 3 388, HR871150C 328, USB-A C18077687 488 | Bestellung |
| R-AV-3 | HR871150C Single Source; P1/P2- und P4/P5-Polarität mittlere Sicherheit | M | 1:1-Ausdruck; Link-Test am Muster | Muster |

### Signal / USB / Ethernet
| ID | Risiko | Bew. | Massnahme | Stufe |
|---|---|---|---|---|
| R-TIM-1 / **H1** | XOSC-Anlauf: der Basic-Quarz X322512MSB4SI (C_L 20 pF, 2 × 33 pF, ESR nicht garantiert ≤ 50 Ω) wich von der RP2040-Referenz ab | **behoben** | **Review-Befund H1 umgesetzt (2026-10-23):** Y1 = **Abracon ABM8-272-T3** (12 MHz, C_L 10 pF, ESR ≤ 50 Ω, LCSC C20625731), C25/C26 = **15 pF C0G** (0402CG150J500NT, C1548), R37 1 kΩ unverändert – exakt wie Raspberry Pi „Hardware design with RP2040"/Pico. Layout: XTAL12_XIN 3,2 mm (vorher 10,2), XOUT 2,2 mm, XO_R 9,7 mm. Quelle: `datasheets/ABM8-272-T3_SUMMARY.md`. Anlauf am Muster trotzdem kurz prüfen | erledigt |
| R-TIM-2 | 25-MHz-Genauigkeit (±30 ppm) | N | C_L 18 pF mit 2 × 27 pF | – |
| R-TIM-3 | USB-FS-Signalqualität | N | 90-Ω-Paar ≤ 30 mm (DRU), USBLC6 an der Buchse | – |
| R-TIM-4 | W55RP20 ohne Auto-MDIX | N | Gegenstelle (Switch) übernimmt | Doku |
| R-TIM-5 | GPIO20–25 (W5500-intern) nicht dokumentiert | N (HW) / M (FW) | FW nach WIZnet-SDK | Firmware |
| R-ETH-1 / **K1** | Gemeinsamer CT (J1.3) an +3V3A: ohne Koppel-C lagen die RX-Pins DC auf 3,3 V – widerspricht der WIZnet-W5500-Referenz „connected CT" | **behoben** | **Review-Befund K1 umgesetzt (2026-10-23):** C65/C66 **6,8 nF X7R 0402** (YAGEO CC0402KRX7R9BB682, C93654) in Serie in ETH_RXP/ETH_RXN; J1-Seite neue Netze `ETH_RXP_J` (J1.4) / `ETH_RXN_J` (J1.5); R3/R4/C21 bleiben chipseitig. Quelle: WIZnet W5500 Reference Schematic (connected CT: RX DC-getrennt vom CT). Layout: C65/C66 Bottom bei x ≈ 24,2 im RX-Kanal, RX gesamt P/N 60,525/60,529 mm. Link 10/100 und Paketverlust bei 100 m am Muster prüfen | erledigt |
| R-USB-1 | Externe 15 k parallel zu RP2040-intern → 7,5 kΩ | – | R30/R31 DNP (OD-10) | erledigt |
| R-USB-2 | HID-Geräte > 500 mA lösen Begrenzung aus | N | dokumentieren; FW wertet `VBUS_SENSE` aus | Doku |
| R-USB-4 | VBUS entlädt nach `USB_EN = 0` nur über R32/R33 (τ ≈ 27 s) → „Port aus" ist lange nicht spannungsfrei | N | FW: vor Neustart des Ports warten bzw. per `VBUS_SENSE` prüfen | Firmware |
| R-FW-1 | **Firmware-Randbedingungen (2. Review):** W5500-SiP-Pins verifiziert (WIZnet-PICO-C: CS 20, SCK 21, MISO 22, MOSI 23, INT 24, RST 25, `USE_PIO`); Status-LED D11 seit Rev 4f normaler GPIO-Ausgang (kein PIO nötig); `PICO_BOARD`, Flash 2 MB und boot2 wie **WIZnet W55RP20-EVB**; Link-Status über W5500 **PHYCFGR** | N (HW) / M (FW) | in README/Inbetriebnahme dokumentiert | Firmware |
| R-EMI-4 | Gleichtaktstrom über Schirm/Y-Pfade | N | Schirm über R7 ∥ C24, USB-Schirm R34 (C30 DNP-Option), C14 Y2-Option | Muster |
| R-EMI-5 | Keine Ethernet-ESD | N | Prototyp akzeptiert | – |

### Vereinfachungen Rev 4b/4d (bewusst)
| ID | Vereinfachung | Bew. | Massnahme |
|---|---|---|---|
| R4b-3 | ~~Link/Activity nur per Firmware über D11~~ – seit Rev 4g zeigen die MagJack-LEDs Link/Activity direkt | – | – |
| R4d-1 | Kein UART (GPIO0/1 offen) | N | Debug über SWD (RTT); USB-CDC nicht möglich (Host-Port) |
| R4d-2 | Kein BOOTSEL-Taster | N | Programmierung **nur über SWD** (J3-Randpads, 2,54-mm-Stiftleiste liegend aufgelötet); bei leerem Flash startet der USB-Bootloader, der am Host-Port nicht nutzbar ist |
| R4d-3 | **RUN ohne externen Pull-up/C** (intern ≈ 50 kΩ Pull-up; Review empfiehlt 10 k + 100 nF, nicht umgesetzt) – ESD/Störimpulse können Resets auslösen | N–M | Reset via SWD/Power-Cycle; Störfestigkeit am Muster prüfen, Fallback 10 k an +3V3 (+ optional 100 nF) fliegend nachrüsten |
| R4e-6 | SWD-Stiftleiste J3 hält nur auf SMD-Pads (keine Durchkontaktierung), Zugkraft auf die Leiste kann Pads abheben | N | Leiste nur zum Programmieren auflöten bzw. mit Kleber sichern; Kabel zugentlastet führen; Pads 1,5 × 3,0 mm, 0,3 mm von der Kante |
| R4d-4 | Kein Überstrom-Flag (U6 FAULT offen) | N | Begrenzung 532–659 mA aktiv; FW erkennt Überlast über `VBUS_SENSE` |
| R4d-5 | LED an +3V3 (VDD-Untergrenze) | N | Helligkeit/Farbe am Muster; FW ≤ 30 % |
| R4d-6 | C61 TOCAP an U5.33 | M | **nicht** direkt am Pin (Review) → offen, siehe R-LAY-7 |

## 2. Entscheidungen (OD) – Endstand

| # | Thema | Entscheidung |
|---|---|---|
| OD-1 | PoE-Klasse | **Class 0** (fest im Modul; Rev 1–3: Klasse 2) |
| OD-2 | Mechanik RJ45 | **versetztes PCB** + Standard-PoE-MagJack |
| OD-3 | Flyback-Höhe | entfällt (Modul) |
| OD-4 | USB-Lastschalter | **TPS2553**, R_ILIM 44,2 k |
| OD-5 | PD-Konzept | **Modul Ag9905-LPB** (Rev 1–3: TPS23753A + Opto) |
| OD-6 | 3,3-V-Erzeugung | **LDO TLV75733P**; Buck nur nach Thermikmessung |
| OD-7 | Status-LED | **grüne 0603-LED D11 an GPIO28** (Rev 4f; Rev 4b–4e WS2812B-2020-V6, Rev 2–4 RGB an +5V mit N-FETs); MagJack-LEDs ab Rev 4g an W5500 LINKLED/ACTLED |
| OD-8 | PCB-Länge | **80 mm** |
| OD-9 | LED-Position | Top-View an der USB-Stirnseite + Kappenfenster |
| OD-10 | 15-k-Pull-downs | **DNP** |
| OD-11 | Thermik/Rohr | **Entschieden: Kunststoffrohr** Innen-Ø 25 mm (2026-10-23) – Isolation zum Gehäuse unkritisch (R-ISO-5 entschärft); Wärmeabfuhr schlechter als Alu → **max. Umgebung 40 °C** empfohlen, Lüftungsschlitze in den Endkappen, Temperaturen am Muster messen |
| OD-12 | Y-Kondensator | 2,2 nF Y2 als **DNP-Option** (C14) |
| OD-13 | RJ45-Schirm | 1 MΩ ∥ 4,7 nF/2 kV an GND |

## 3. Geschlossen (Kurzliste)

Mit dem Wegfall des diskreten Flybacks (Rev 4) erledigt: R-ISO-2, R-ISO-4, R-ISO-6, R-PI-1 … R-PI-5, R-PI-8 … R-PI-10, R-EMI-1 … R-EMI-3, R-TH-2, R-TIM-6, R-AV-1, R-AV-4, R-AV-5, R-ASM-1. Weiter: R-USB-3 (R25 44,2 k), R-LED-1/-2 (WS2812B), R-H-1 (HR871150C 13,3 mm), R-LAY-3 (80 mm freigegeben), R4-5 (Bauhöhe, LPB max 9,2 mm passt), R4-7 (ersetzt durch R4e-2), R4-9 (Rev-3-Dateien im Paket – nur Aufräumpunkt).
Rev-4e-Review (2026-10-23): **K1** (RX-Koppel-C C65/C66, R-ETH-1) und **H1** (Y1 ABM8-272-T3 + 2 × 15 pF, R-TIM-1) behoben; **R-ISO-5** durch Kunststoffrohr entschärft.

## 4. Offene Review-Empfehlungen (vom User nicht umgesetzt) – Kurzliste

| Punkt | Risiko-ID | Empfehlung |
|---|---|---|
| TOCAP C61 nicht direkt an U5.33 | R-LAY-7 | nächste Revision direkt an den Pin |
| Abblock Pin 42/43 > 5 mm | R-PI-12 | 100 nF näher an Pin 42/43 |
| ~~LDO U4 ohne Thermal-Vias im EP~~ | R-PI-13 / R-TH-3 | **behoben** (3 EP-Vias + 2 GND-Vias) |
| ~~Wenig GND-Stitching im USB-Bereich~~ | R-LAY-6 | **entschärft** (5 GND-Vias) |
| R7 0603 im Hipot überlastet | R-ISO-8 | 1206-HV-Widerstand |
| ETH_RXN 1,8 mm zu J1.7 + weitere J1-Abstände 1,74/2,47/2,95 mm | R-ISO-9 | als J1-ISO-Ausnahme geführt, Hipot |
| ETH_LED_LINK_N (In3) 2,23 mm zu J1.7 | R-ISO-10 | als J1-ISO-Ausnahme geführt, Hipot |
| RUN ohne externen Pull-up/C | R4d-3 | 10 k + 100 nF nachrüsten bei Problemen |
| R9-Obergrenze | R4-2 | +5V_RAW ≤ 5,25 V; 0 Ω (5,65 V) unzulässig |
| VBUS Worst Case ≈ 4,6 V @ 500 mA | R4-2 | R9-Abgleich, Messung am Muster |
| PSE muss 802.3af/at ≥ 48 V sein | R-PI-11 | kein passives 24-V-PoE |
| 3 Vias 0,4/0,2 (Aufpreis) | R-LAY-1 | ggf. durch 0,45/0,3 ersetzen |
| POFV-Liste | R-LAY-5 | bei Bestellung beilegen (10 Vias, Liste in R-LAY-5) |
| D3 Höhenreserve ≈ 0,25 mm, J2 15,2 × 7,0 mm | R-TH-6 | Einbau prüfen |
| CPL-Rotationen, Paste auf DNP, J1-Footprint nicht aktualisieren | R-LAY-9 … R-LAY-11 | Bestellung/Layout |

---

## Änderungshistorie

- **Rev 1 (2026-10-21):** Risiken des diskreten Flybacks (Isolation L-Grenze, Regelschleife, T1-Sättigung, EMV) und offene Entscheidungen OD-1 … OD-13.
- **Rev 2 (2026-10-21):** T1-Pinout verifiziert, R25 44,2 k, LED an +5V; neu R-TH-5 (J1 0…70 °C), R-ISO-7, R-ETH-1, R-PI-8 … -10.
- **Rev 3 (2026-10-22):** Layoutvariante 30 × 80 mm – verworfen.
- **Rev 4 (2026-10-22):** Modul Ag9905LP: Flyback-Risiken geschlossen, neu R4-1 … R4-9.
- **Rev 4b (2026-10-22):** WS2812B (MSL 5), Tag-Connect-Feld.
- **Rev 4c (2026-10-22):** verworfen.
- **Rev 4d (2026-10-22):** bewusste Vereinfachungen R4d-1 … R4d-6.
- **Rev 4e (2026-10-23):** Ag9905-LPB: R4e-1 … R4e-5; Layout-DRC 0/0/0.
- **Rev 4e Review (2026-10-23):** K1 und H1 behoben; Kunststoffrohr: R-ISO-5 entschärft, Thermik (R4-1, R-TH-1, R-TH-5) bei ≤ 40 °C Umgebung auf M neu bewertet; neu R-ISO-8, R-ISO-9, R-PI-11 … R-PI-13, R-LAY-5 … R-LAY-7 (offene Review-Empfehlungen); R4-2 mit R9-Obergrenze und VBUS ≈ 4,6 V.
- **Rev 4f/4g (2026-10-26):** D11 normale grüne LED (R4b-1 entfällt), MagJack-LEDs beschaltet (R4b-3 erledigt), neu **R-ISO-10**; In3-+5V-Fläche durch die LED-Leitungen zweimal eingeschnitten (Fläche zusammenhängend, +5V an U4 am Muster messen).
- **2. Review (2026-10-23):** Funktion HID → USB → MCU → Ethernet und PoE → 5 V bestätigt, keine KRITISCH/HOCH-Befunde in der Schaltung, K1/H1 verifiziert, W5500-SiP-Pins verifiziert. Behoben: R-LAY-8 (Bohrdaten-Nullpunkt), R-PI-13 (U4-Wärme-Vias); entschärft: R-LAY-6 (5 GND-Stitching-Vias). Neu: R-TH-6, R-LAY-9 … R-LAY-11, R-USB-4, R-FW-1; R-ISO-9 um drei J1-Abstände ergänzt; R-LAY-5 POFV-Liste aktualisiert; R-AV-2 (W55RP20 nur 89 Stk); R-TH-4 FW-Schwelle 4,0–4,2 V.
