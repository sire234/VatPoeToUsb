# PoE → USB-Host-HID-Bridge (poe_usb_hid_bridge) – Rev 4g

Ein Gerät, das über **ein Ethernet-Kabel mit PoE (IEEE 802.3af)** gespeist wird und an einem **USB-A-Host-Port** ein HID-Gerät (Tastatur, Barcode-Scanner, Maus) betreibt. Die HID-Daten stellt die Firmware über Ethernet bereit.

| | |
|---|---|
| Stand | **Rev 4g** (2026-10-26: MagJack-LEDs wieder beschaltet, R5/R6; Rev 4f: D11 normale grüne LED statt WS2812B, C64 entfällt; Schaltplan mit Leitungen gezeichnet, Pin-1-Punkte im Bestückungsdruck) auf Basis **Rev 4e** inkl. Review-Korrekturen K1/H1, 2026-10-23 · **2. Review (2026-10-23):** Funktion HID → USB → MCU → Ethernet und PoE → 5 V bestätigt, keine KRITISCH/HOCH-Befunde in der Schaltung, K1/H1 verifiziert; Bohrdaten-Nullpunkt, U4-Wärme-Vias und USB-GND-Stitching behoben |
| Board | 20 × 80 mm, 6 Lagen, 1,6 mm (JLC06161H-3313), beidseitig bestückt, für ein **Kunststoffrohr** Innen-Ø 25 mm (**max. 40 °C Umgebung** empfohlen) |
| PoE | Silvertel **Ag9905-LPB** (802.3af Class 0, isoliert 5 V / 1,4 A), Brücken MB6S, TVS SMAJ58A · speisende PSE muss **IEEE 802.3af/at ≥ 48 V** sein (kein passives 24-V-PoE) |
| MCU + Ethernet | WIZnet **W55RP20** (RP2040 + W5500 + 2 MB Flash); 12 MHz Abracon ABM8-272-T3 + 2 × 15 pF (RPi-Referenz); RX über Koppel-C C65/C66 6,8 nF (WIZnet „connected CT") |
| USB | USB-A-Host, TPS2553-Lastschalter (532–659 mA), USBLC6-ESD |
| Status | MagJack-LEDs an J1 (grün = Link ← U5 LINKLED, gelb = Activity ← U5 ACTLED, aktiv low, R5/R6 330 Ω an +3V3) und eine **grüne 0603-LED** D11 (MEIHUA MHT193CGCT, 569 nm) an GPIO28 über R38 330 Ω, High = an (≈ 3,5 mA) |
| Debug | nur **SWD** über Randpads J3 (1 SWCLK, 2 GND, 3 SWDIO, 4 +3V3) für eine 2,54-mm-Stiftleiste |
| Prüfstatus | ERC 0 Fehler / 0 Warnungen · DRC (2026-10-23 13:47) 0 Errors / 0 Unconnected / 0 Parity, 23 Warnungen (nur Silkscreen/Bibliothek) |
| Bauteile | 85 Referenzen / 46 Netze → 75 Positionen bei JLC + U1 beigestellt (9 DNP inkl. J3/U1, TP9 nur Pad) · ≈ 25 USD/Board bei 10 Stk |

## Ordnerstruktur (gültige Dateien)

```text
PoeToUSB/
├── README.md                      dieser Überblick
├── SPEC.md                        Anforderungen (Stand Rev 4e)
├── pipeline_state.json            Pipeline-Status
├── architecture/
│   ├── block_diagram.md           Blöcke B1–B7, Isolationsgrenze
│   ├── net_plan.md                alle Netze, Pin-für-Pin je Block, Netzklassen
│   ├── ic_selection.md            Bauteilwahl und Begründungen
│   ├── skeleton_bom.md            funktionale Stückliste je Block, Auslegung R25
│   ├── power_budget.md            Strom-/Leistungs-/Wärmebudget
│   ├── mechanical_concept.md      Rohr, Höhenhülle, Platzierung, Stackup
│   └── design_risks.md            offene Risiken, Review-Befunde, Entscheidungen OD-1…13
├── sourcing/sourced_bom.md        Einkaufs-BOM (85 Refs, LCSC/MPN/Kosten)
├── datasheets/                    Datenblätter + *_SUMMARY.md, Index README.md
├── circuits/poe_usb_hid_bridge/   SKiDL-Quellcode (Quelle der Wahrheit)
│   ├── __main__.py                Zusammenbau, ERC, Netzlisten-Export
│   ├── ethernet_magjack.py        B1
│   ├── poe_pd_module.py           B2
│   ├── ldo_3v3.py                 B4
│   ├── mcu_w55rp20.py             B5
│   ├── usb_host_port.py           B6
│   └── status_led.py              B7
├── libs/poe_usb_hid_bridge.kicad_sym          Projekt-Symbole
├── footprints/poe_usb_hid_bridge.pretty/      Projekt-Footprints
├── kicad/poe_usb_hid_bridge_rev4g/            KiCad-10-Projekt (Schaltplan mit Leitungen + Board); Rev 4e/4f bleiben daneben
└── outputs/
    ├── poe_usb_hid_bridge_rev4g.net           Netzliste
    ├── poe_usb_hid_bridge_rev4g_bom.xml       BOM (SKiDL-XML)
    ├── poe_usb_hid_bridge_rev4g_erc.txt       ERC-Protokoll (SKiDL)
    ├── poe_usb_hid_bridge_rev4g_schematic.pdf Schaltplan-PDF (mit Leitungen)
    ├── layout_rev4g/                          3D-Renders (oben, unten, iso, Detail Pin-1-Punkte, R5/R6)
    └── fab_rev4g_release/                     Fertigungsdaten (Gerber, Drill, BOM, CPL) – gültig
```

Ältere Revisionen (Netzlisten, Layouts, Fab-Daten Rev 3–4d, Snapshots) liegen noch im Projekt, gelten aber nicht mehr.

## Projekt öffnen

1. **KiCad 10** starten → `kicad/poe_usb_hid_bridge_rev4g/poe_usb_hid_bridge_rev4g.kicad_pro` öffnen. Die Projekt-Bibliotheken sind über die lokalen `sym-lib-table`/`fp-lib-table` eingebunden.
2. Der Schaltplan ist hierarchisch (ein Sheet je Block: `ethernet_magjack`, `poe_pd_module`, `ldo_3v3`, `mcu_w55rp20`, `usb_host_port`, `status_led`).
3. Netzliste neu erzeugen (optional): in `circuits/` mit installiertem SKiDL `python -m poe_usb_hid_bridge` ausführen → schreibt `outputs/poe_usb_hid_bridge_rev4g.net` und `_bom.xml` (KiCad-10-Bibliothekspfade sind in `__main__.py` gesetzt).

## Fertigungsdaten

Ort: **`outputs/fab_rev4g_release/`** (Gerber, Bohrdaten, JLC-BOM und -CPL, ZIP `poe_usb_hid_bridge_rev4g_gerber_drill.zip`; Stand 2026-10-26; DRC 0 Errors / 0 Unconnected / 0 Parity, 18 Warnungen Silkscreen/J1). **Nicht verwenden:** `fab_rev4f_final/` und `fab_rev4g_final/` – dort liegen die Gerber auf absoluten Koordinaten, die Bohrdaten auf dem Board-Ursprung (100 mm Versatz, Review 2026-10-26). U1 ist im JLC-Export DNP (Beistellteil), J3 (SWD-Randpads), TP9 und alle DNP-Optionen erscheinen nicht in der CPL.

**Behobener Exportfehler (2026-10-23):** Die Bohrdaten hatten einen anderen Nullpunkt als die Gerbers (Versatz 100 mm, Board-Ursprung bei 100/100). Bohrdaten wurden mit `--drill-origin plot` neu exportiert, das ZIP neu gepackt. Bei jedem Neu-Export so vorgehen (KiCad 10, im Ordner `kicad/poe_usb_hid_bridge_rev4e/`):

```text
kicad-cli pcb export gerbers --use-drill-file-origin --layers "F.Cu,In1.Cu,In2.Cu,In3.Cu,In4.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts" -o ../../outputs/fab_rev4g_release/gerber/ poe_usb_hid_bridge_rev4g.kicad_pcb
kicad-cli pcb export drill --format excellon --drill-origin plot --excellon-separate-th --generate-map --map-format gerberx2 -o ../../outputs/fab_rev4g_release/gerber/ poe_usb_hid_bridge_rev4g.kicad_pcb
```

**Wichtig:** Gerber immer mit `--use-drill-file-origin` exportieren, Bohrdaten mit `--drill-origin plot` – beide liegen dann auf dem Board-Ursprung (Ecke RJ45-Seite, X0 … 80).

- Gerber und Bohrdaten müssen denselben Nullpunkt haben (`plot`); im JLC-Gerber-Viewer prüfen, dass die Bohrungen auf den Pads liegen.
- **Nicht `--board-plot-params` verwenden:** Im Board ist der Plotparameter `drillshape=1` gesetzt → Bohrmarken in den Kupferlagen. Entweder ohne Board-Plotparameter exportieren oder `drillshape` vorher auf 0 setzen.
- **Bei J1 nicht „Footprints aus Bibliothek aktualisieren"**: Der J1-Footprint ist lokal angepasst (verkleinerte Pads/ISO-Keepout, R-ISO-3); die DRC-Warnung `lib_footprint_mismatch` ist deshalb gewollt.
- DRC (13:47): 0 Errors / 0 Unconnected / 0 Parity, 23 Warnungen (Silkscreen, J1-Bibliotheksabgleich).

## Bestell-Checkliste (JLCPCB)

- [ ] **6 Lagen, 1,6 mm, Stackup JLC06161H-3313** wählen; Lagenbelegung In1 GND, In2 VBUS, In3 +5V, In4 +3V3.
- [ ] **Impedanzkontrolle** bestellen: ETH 100 Ω diff. (0,13 / 0,2 mm), USB 90 Ω diff. (0,15 / 0,18 mm) – mit dem JLC-Impedanzrechner für JLC06161H-3313 gegenprüfen.
- [ ] **Vias:** Standard 0,45/0,3 mm; in der Rule-Area `U5_FANOUT` **3 Vias 0,4/0,2 mm mit 0,1 mm Abstand** → entsprechende Fertigungsoption (Aufpreis; optional vorher durch 0,45/0,3 ersetzen, dann entfällt er).
- [ ] **Via-in-Pad gefüllt und gedeckelt (POFV)** – im Board nicht als Attribut gesetzt → bei der Bestellung wählen und diese **POFV-Liste** beilegen (Koordinaten x/y in mm, Board-Ursprung = Ecke RJ45-Seite):
  - *Via-Mitte im Pad:* U1 Pad 1 × 2 (41,6/4,2; 42,4/4,2), C52.1 (62,32/13,56), U4-EP × 3 (49,15/14,04; 49,15/14,60; 49,15/15,16).
  - *Via-Rand berührt Pad:* U5.54 (60,79/12,25), C55.1 (59,34/4,68), R22.1 (57,05/4,2), C50.2 (49,6/10,3).
- [ ] **U1 Ag9905-LPB beistellen** (DigiKey 5061-AG9905-LPB-ND) → JLC-Consignment-SMT, sonst Handreflow; **nur Oberseite**. Für Consignment **U1 in BOM und CPL aufnehmen** (im aktuellen Export DNP).
- [ ] **Paste auf DNP-Pads:** Die Pastenschablone druckt auch auf die Pads von U1, C1, C14, R8, R9, C30 → bei JLC akzeptieren bzw. Hinweis geben (U1-Consignment braucht die Paste).
- [ ] **CPL-Rotationen** sind KiCad-Winkel → im JLC-Placement-Viewer jede Lage prüfen, besonders U5, U4, U6, U7, C11, C18, D1–D3, D12, D11, Y1/Y2. Bei **Y1/Y2 nach Datenblatt-Pin-1 ausrichten, nicht nach der Fase** – eine 90°-Fehllage legt die Quarzpins auf GND.
- [ ] **Lagerbestand (live 2026-10-23):** **W55RP20 C43229502 nur 89 Stk → bei JLC reservieren!** · ABM8-272-T3 C20625731 3 388 · HR871150C C19724786 328 · USB-A C18077687 488. C65/C66 (C93654) und C25/C26 15 pF (C1548) in der JLC-BOM kontrollieren.
- [ ] **D11 grüne LED (C2962098):** Polarität (Kathode = Pad 1, in der Draufsicht unten) im JLC-Placement-Viewer prüfen; kein Backen mehr nötig (WS2812B entfallen).
- [ ] **Footprint-1:1-Prüfungen** mit Ausdruck: U1 (Ag9905-LPB, Pin-1-Lage!), J1 (HR871150C), J2 (BX-TYPE-A-MWT4P); zusätzlich U5-Land-Pattern.
- [ ] J1 ist THT → JLC-THT-Lötservice; **20 Extended-Typen** (≈ 60 USD/Bestellung).
- [ ] **Optional (Review-Empfehlung, Hipot):** R7 statt 0603 als 1206-HV-Widerstand – im aktuellen Board nicht umgesetzt (design_risks R-ISO-8).
- [ ] **Speisung klären:** Router/Switch/Injektor muss **IEEE 802.3af/at mit ≥ 48 V** liefern; passives 24-V-PoE funktioniert nicht.
- [ ] **Gehäuse:** Kunststoffrohr Innen-Ø 25 mm, Endkappen mit Lüftungsschlitzen; Einsatz bei **max. 40 °C Umgebung** einplanen.
- [ ] Vor dem Bestellen Stock/Preise in `sourcing/sourced_bom.md` neu prüfen.

## Inbetriebnahme

1. **Erstes Einschalten:** normgerechter **802.3af/at-PoE-Injektor bzw. -Switch (≥ 48 V)**, idealerweise mit Strombegrenzung – kein passives 24-V-PoE; +5V an TP9 und +3V3 an J3 Pin 4 messen (Erwartung: 4,75–5,25 V bzw. 3,30 V; Leerlauf ≈ 180 mA an +5V_RAW mit Link).
2. **Programmierung nur über SWD:** 1×4-Stiftleiste (2,54 mm) liegend auf die Randpads J3 löten, Pins ragen über die Board-Kante: Pin 1 SWCLK, 2 GND, 3 SWDIO, 4 +3V3. Pins 1–3 entsprechen der SWD-Reihenfolge des Raspberry Pi Pico bzw. des 3-Pin-Kabels der Raspberry Pi Debug Probe (OpenOCD `rp2040.cfg`); +3V3 nur als Referenz, das Board über PoE versorgen. Es gibt keinen BOOTSEL-Taster, kein UART und keinen Reset-Pin – der USB-A-Port ist Host und taugt nicht für den USB-Bootloader.
3. **Firmware:** Pico-SDK + **TinyUSB-Host** (`tuh_hid_*`) + **WIZnet ioLibrary** (W5500 über das interne PIO-SPI des W55RP20; GPIO20–25 intern).
   - GPIO26 = `USB_EN` (aktiv-high, Default AUS), GPIO28 = `LED_DIN` (normaler GPIO-Ausgang, High = grüne LED an; PWM möglich), GPIO29/ADC3 = `VBUS_SENSE` (Faktor 0,405).
   - `PICO_BOARD`, Flash-Grösse 2 MB und boot2 wie beim **WIZnet W55RP20-EVB** einstellen.
   - W5500-Anbindung (verifiziert, WIZnet-PICO-C): CS 20, SCK 21, MISO 22, MOSI 23, INT 24, RST 25 über PIO-SPI (`USE_PIO`). Die Status-LED braucht seit Rev 4f keinen PIO mehr.
   - Überlast über `VBUS_SENSE` erkennen: **Schwelle ≈ 4,0–4,2 V** (nicht 4,5 V – im Normalbetrieb sind Worst Case ≈ 4,6 V möglich), Messwert mitteln und **> 50 ms entprellen**, dann `USB_EN` abschalten (Retry mit Backoff).
   - Nach `USB_EN = 0` entlädt sich VBUS nur über den Teiler (τ ≈ 27 s): vor einem Neustart des Ports warten bzw. per `VBUS_SENSE` prüfen, dass VBUS abgefallen ist.
   - MagJack-LEDs (Rev 4g) werden direkt vom W5500 angesteuert (Link grün, Activity gelb) – keine Firmware nötig. Link-Status zusätzlich über **PHYCFGR** lesbar.
   - Status-LED: ≈ 3,5 mA bei Dauer-An, kein Einfluss auf das +3V3-Budget.
   - Quarz Y1 entspricht der Raspberry-Pi-Referenz (ABM8-272-T3, 2 × 15 pF, 1 kΩ); `PICO_XOSC_STARTUP_DELAY_MULTIPLIER` kann auf dem SDK-Default bleiben (64 als Reserve schadet nicht).
4. Danach PoE vom Ziel-Router/-Switch (802.3af/at, ≥ 48 V): Detection, Link 10/100, USB-Gerät anstecken.
5. **Thermik prüfen:** im geschlossenen Kunststoffrohr bei Volllast (USB 0,5 A) und USB-Kurzschluss die Temperaturen an U1, U5, U4 und J1 messen; Betrieb nur bis **40 °C Umgebung** (W55RP20 Tc ≤ 85 °C, J1 ≤ 70 °C).
6. **R9 (VBUS-Abgleich) nur bei Bedarf:** +5V_RAW höchstens 5,25 V – R9 = 0 Ω (5,65 V) ist unzulässig.

## Offene Prüfpunkte am Muster

| Punkt | Was prüfen | Option |
|---|---|---|
| **Thermik** | Temperatur an U1, U5, U4, J1 im geschlossenen Rohr bei Volllast und USB-Kurzschluss (erwartet ≈ 68–80 °C bei 40 °C Umgebung) | Kunststoffrohr: Umgebung ≤ 40 °C, Lüftungsschlitze in den Endkappen; Isolation zum Rohr unkritisch. U4 hat jetzt 3 Thermal-Vias im EP + 2 GND-Vias |
| **VBUS / R9** | VBUS am Port unter 0,5 A (Worst Case ≈ 4,6 V) | R9 ADJ → GND bestücken, Ziel +5V_RAW ≈ 5,10 V, **max. 5,25 V** (R9 = 0 Ω → 5,65 V unzulässig) |
| **PoE-Detection / C1** | Detection mit 2–3 verschiedenen PSEs | C1 bleibt DNP; nur bei Bedarf bestücken |
| **Hipot 1500 VAC** | Isolation primär ↔ sekundär inkl. J1-Pfad (R-ISO-3, R-ISO-7, ETH_RXN 1,8 mm zu J1.7 R-ISO-9); Modul ist für 1500-V-DC-Impuls spezifiziert | C24 DNP als Option; R7 0603 ist im Hipot überlastet → 1206-HV empfohlen (R-ISO-8) |
| **Mindestlast / R8** | Geräusch im Leerlauf (< 200 mA) | R8 100 Ω (1206) bestücken |
| **RUN-Pull-up** | Störfestigkeit ohne externen Reset-Pull-up/C | 10 k (+ 100 nF) von RUN (U5.29) an +3V3 nachrüsten |
| **Ethernet** | Link 10/100, Paketverlust bei 100 m (RX jetzt mit C65/C66); W5500-Stabilität (C61 nicht direkt an TOCAP, Abblock Pin 42/43 > 5 mm) | siehe design_risks R-ETH-1, R-LAY-7, R-PI-12 |
| **Mechanik** | D3 (SMA, Bottom) hat nur ≈ 0,25 mm Reserve zur Rohrwand; J2 laut Datenblatt 15,2 mm breit (Laschen) / 7,0 mm hoch | Einbau ins Rohr vorsichtig prüfen |
| Weitere | Quarz-Anlauf kurz kontrollieren, USB-Signalqualität, LED-Helligkeit an 3,3 V, D11-Polarität | siehe `architecture/design_risks.md` §4 (offene Review-Empfehlungen) |

## Revisionsverlauf (Kurz)

Rev 1–3 diskreter Flyback (TPS23753A + POE70P) · Rev 3 30-mm-Board verworfen · Rev 4 Ag9905LP-Modul · Rev 4b WS2812B + Tag-Connect · Rev 4c Brücken-Variante verworfen · Rev 4d Minimal-Debug (nur SWD), LED an +3V3 · **Rev 4e Ag9905-LPB (SMT)** · Rev 4e Review: K1 RX-Koppel-C C65/C66, H1 Quarz nach RPi-Referenz, Kunststoffrohr ≤ 40 °C · **Rev 4f** D11 normale grüne LED (C64 entfällt), ganzer Schaltplan mit Leitungen, Pin-1-Punkte, 3D-Modelle U1/U5/J1/J2 · **Rev 4g** MagJack-LEDs wieder beschaltet (R5/R6, Leitungen auf In3).
