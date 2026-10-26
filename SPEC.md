# SPEC – poe_usb_hid_bridge (Stand Rev 4g, 2026-10-26)

PoE → USB-Host-(HID)-Bridge auf schmalem PCB für ein Rohr mit Innen-Ø 25 mm.
Ursprung: Interview/Plan vom 2026-10-21 (Ideenquelle `poe_usb_host_kicad_v0.2`). Diese Fassung beschreibt den **umgesetzten Endstand Rev 4e**; die ursprünglichen Vorgaben und ihre Änderungen stehen in der Historie am Ende.

---

## Functional

- **Zweck:** Ein Gerät, das über ein einziges Ethernet-Kabel mit PoE gespeist wird und an einem USB-A-Host-Port ein HID-Gerät (Tastatur, Barcode-Scanner, Maus usw.) betreibt. Die HID-Daten stellt die Firmware über Ethernet (TCP/UDP) bereit.
- **Eingänge:**
  - RJ45, 10/100BASE-T, PoE IEEE 802.3af, PD-Seite, Mode A und Mode B, beliebige Polarität.
  - USB-HID-Gerät am USB-A (Full-Speed 12 Mbit/s oder Low-Speed 1,5 Mbit/s), ein Port, kein Hub.
- **Ausgänge:**
  - Ethernet-Datenstrom (Firmware nicht Teil dieses Auftrags).
  - USB-VBUS 5 V, strombegrenzt 532–659 mA (TPS2553, R_ILIM 44,2 kΩ), per GPIO schaltbar, Default AUS.
  - Eine grüne Status-LED (D11, 0603, MEIHUA MHT193CGCT) an einem GPIO (aktiv-high).
  - Link-/Activity-LEDs im MagJack J1 (grün = Link, gelb = Activity), direkt vom W5500 angesteuert.
- **µC + Ethernet:** WIZnet **W55RP20** (RP2040 + W5500 + 2 MB QSPI-Flash, QFN-68 8 × 8 mm).
  - 12-MHz-Quarz (RP2040) exakt nach Raspberry-Pi-Referenz: Abracon ABM8-272-T3 (C_L 10 pF, ESR ≤ 50 Ω), 2 × 15 pF C0G, 1 kΩ an XOUT; 25-MHz-Quarz (W5500, C_L 18 pF).
  - RP2040-USB-PHY als Host (TinyUSB `tuh_hid_*`); W5500 über das interne PIO-SPI (WIZnet ioLibrary).
- **GPIO-Belegung:** GPIO26 = `USB_EN`, GPIO28 = `LED_DIN` (Status-LED D11 über R38 330 Ω; Netzname historisch), GPIO29/ADC3 = `VBUS_SENSE` (Teiler 100 k/68 k). Alle übrigen GPIO offen (Reserve).
- **Debug/Service:** nur **SWD** über die Randpads J3 (Bottom, Längskante; 1 SWCLK, 2 GND, 3 SWDIO, 4 +3V3) für eine liegend aufgelötete 2,54-mm-Stiftleiste. Kein UART, kein BOOTSEL-Taster, kein Reset-Pad (RUN und QSPI_SS nutzen die internen Pull-ups des RP2040; externer RUN-Pull-up/C als Review-Empfehlung offen).
- **Überwachung:** kein Überstrom-Flag; Überlast erkennt die Firmware über `VBUS_SENSE`. Ethernet-Link/Activity zeigen die MagJack-LEDs direkt (W5500 LINKLED/ACTLED, aktiv low, R5/R6 330 Ω an +3V3).

## Power

- **Eingang:** PoE IEEE 802.3af, 37–57 V am PD (Modul: 36–57 V, Anlauf ≥ 42 V). **Speisende PSE (Router/Switch/Injektor) muss IEEE 802.3af/at mit ≥ 48 V sein** – passives 24-V-PoE funktioniert nicht.
  - Zwei Brückengleichrichter MB6S (Mode A + Mode B), TVS SMAJ58A über dem Moduleingang.
- **PD + Wandler:** Silvertel **Ag9905-LPB** (Low-Profile-SMT-Modul): Signatur, **Class 0**, Hotswap und isolierter DC/DC im Modul.
  - Ausgang 5,00 V (4,75–5,25 V), max. 1,4 A, 7 W ≤ 70 °C / 4,5 W @ 85 °C, Mindestlast 200 mA (Option R8).
  - Ausgangs-C 100 µF Polymer 15 mΩ + 22 µF + 100 nF; ADJ offen (Trimm-Option R9, DNP; +5V_RAW darf 5,25 V nicht überschreiten – R9 = 0 Ω/5,65 V unzulässig).
- **Isolation:** 1500 V (Modul: Impulstest; IEEE 802.3 Kap. 33) zwischen PoE-Primärseite und Sekundär-GND.
  - Leiterbahn-Abstand ≥ 3,0 mm auf allen Lagen (DRC-Regel, Rule-Area `ISO_BAND`).
  - Barriere-Überquerer: nur U1, die DNP-Option C14 (Y2) und J1-intern (Bob-Smith → Schirm).
- **Sekundärschienen:**
  - **+5V_RAW** (Modulausgang) → FB1 → **+5V** (OVP-Zener BZT52C6V2): speist LDO und USB-Lastschalter.
  - **+3V3:** LDO TLV75733P (1 A, WSON-6). Versorgt W55RP20 und die Status-LED. 1,1-V-Core aus dem internen RP2040-Regler.
  - **+3V3A:** aus +3V3 über FB2 (W5500-AVDD, MagJack-CT).
  - **VBUS_USB:** +5V über TPS2553, Bulk 150 µF + 10 µF + 100 nF.
- **Budget (typ./max., Details `architecture/power_budget.md`):** +5V_RAW 3,44 W typ., 4,52 W im USB-Fehlerfall; am PD ≤ 5,9 W ≪ 12,95 W (Class 0). Wärme im Rohr ≈ 2,0 W typ. / 2,6 W.
- **Sleep-Modi:** keine (Dauerbetrieb).

## Interface

| Schnittstelle | Ausführung | Hinweise |
|---|---|---|
| Ethernet + PoE | HanRun HR871150C (RJ45-MagJack, PoE-CT Mode A/B herausgeführt, 1 gemeinsamer chipseitiger CT) | Top-Mount, THT, Stirnseite x = 0; LEDs Link/Activity an U5 (Rev 4g) |
| Ethernet-PHY-Seite | W5500 TXP/TXN/RXP/RXN, 100 Ω diff. | 49,9 Ω TX-Bias an +3V3A, RX über Koppel-C C65/C66 6,8 nF (DC-Trennung vom CT, WIZnet-Referenz „connected CT"), RX-Terminierung 49,9 Ω + 10 nF chipseitig, CT an +3V3A |
| USB-Host | USB-A-Buchse BX-TYPE-A-MWT4P (SMD, liegend), Stirnseite x = 80 | 90 Ω diff., 27 Ω Serien-R, ESD USBLC6-2SC6; 15-k-Pull-downs DNP (RP2040 intern) |
| Status-LED | D11 grün 0603 (MHT193CGCT), GPIO28 → R38 330 Ω → D11 → GND (≈ 3,5 mA) | Top, nahe J2 |
| Ethernet-LEDs | MagJack J1 gelb (11/12) = Activity ← U5.39, grün (13/14) = Link ← U5.37; R5/R6 330 Ω an +3V3 (≈ 4 mA) | R5/R6 Bottom neben J1 |
| Debug | SWD-Randpads J3 1 × 4, 2,54 mm (Bottom, Längskante) | Programmierung ausschliesslich über SWD |

## Physical

- **Gehäuse:** **Kunststoffrohr** Innen-Ø 25 mm (Isolation zum Rohr damit unkritisch); PCB-Oberseite 5,0 mm unter der Rohrachse (versetzt), siehe `architecture/mechanical_concept.md`.
- **PCB:** **20 × 80 mm**, **6 Lagen**, 1,6 mm, Stackup **JLC06161H-3313**, beidseitig bestückt.
- **Höhen:** Top max. J1 13,3 mm, U1 8,0 (max. 9,2) mm, J2; Bottom nur flache SMD (max. MB6S 2,6 mm).
- **Bauweise:** SMD; THT nur J1. U1 ist reflowfähig, aber **nur Top** zulässig.
- **Temperatur:** ursprünglich 0 … +50 °C Umgebung gefordert; mit dem Kunststoffrohr (schlechtere Wärmeabfuhr als Alu, innen ≈ 68–80 °C bei 40 °C) **max. 40 °C Umgebung empfohlen** (W55RP20 Tc,max 85 °C, HR871150C 0…70 °C, Modul-Derating); Temperaturen am Muster messen.
- **Regulatorisch:** IEEE-802.3af-PD-Konformität über das Modul; keine formale Zertifizierung im Prototyp.

## Production

- **Fertigung:** JLCPCB PCBA, 6 Lagen, Impedanzkontrolle (100 Ω ETH, 90 Ω USB).
  - 85 Referenzen / 46 Netze, davon 9 DNP (inkl. J3 und U1 im JLC-Export) und TP9 (Pad) → **75 Positionen bei JLC + U1 Beistellteil = 76 bestückte Bauteile**.
  - U1 Ag9905-LPB: bei JLC nicht lieferbar → Beistellteil (DigiKey), JLC-Consignment-SMT oder Handreflow.
  - U5 W55RP20: geringer JLC-Bestand → reservieren.
- **Stückzahl:** Prototyp, 5–10 Stück. **Kosten:** ≈ 25 USD/Board bei 10 Stk (ohne PCB/Grundgebühren, siehe `sourcing/sourced_bom.md`).
- **Werkzeug:** SKiDL (`circuits/poe_usb_hid_bridge/`) → Netzliste → KiCad 10 (`kicad/poe_usb_hid_bridge_rev4g/`).

## Annahmen (gültig)

1. Ein USB-Port, Full-/Low-Speed, HID-Gerät ≤ 500 mA; kein Hub.
2. Kein Hilfs-DC-Eingang.
3. Ethernet nur 10/100, kein Auto-MDIX im W5500 (Gegenstelle übernimmt).
4. Kein Ethernet-ESD zusätzlich zur MagJack-Isolation (Prototyp).
5. Firmware ausserhalb des Auftrags; die Hardware legt nur die GPIO-Belegung fest.

## Nicht-Ziele

- Firmware-Entwicklung, Zertifizierung (CE/FCC/UL), PoE+ (802.3at), Gigabit, mehrere USB-Ports.

---

## Änderungshistorie der Spezifikation

- **Rev 1 (2026-10-21):** Ursprüngliche Vorgaben: TPS23753A-Flyback mit TLV431/Opto, Klasse 1/2, 4 Lagen, 20 × 65–75 mm, RGB-LED mit gemeinsamer Anode an 3,3 V (3 GPIO), SWD-/UART-/RUN-/BOOTSEL-Pads, OC-Flag, TPS2051B, AP2112K-LDO.
- **Rev 2 (2026-10-21):** J1 → HR871150C; Klasse 2; TPS2553 statt TPS2051B (Klassengrenze); TLV75733P statt AP2112K (Thermik); RGB-LED an +5V mit 3 × 2N7002.
- **Rev 3 (2026-10-22):** Layoutversuch 30 × 80 mm / 35-mm-Rohr mit diskretem Flyback – verworfen.
- **Rev 4 (2026-10-22):** Diskreter Flyback (Rev 1–3) ersetzt durch PoE-Modul Ag9905LP (DIL), Class 0; zurück auf 20 × ≈ 80 mm im 25-mm-Rohr.
- **Rev 4b (2026-10-22):** Adressierbare LED WS2812B-2020-V6 (1 GPIO), MagJack-LEDs ungenutzt, Debug-Pad-Feld Tag-Connect TC2050; Layout 6 Lagen.
- **Rev 4c (2026-10-22):** Variante mit 0-Ω-Brücken und grösseren Pads – verworfen, nicht übernommen.
- **Rev 4d (2026-10-22):** Minimal-Debug: UART, RUN, BOOTSEL, OC-Flag entfallen; Tag-Connect → SWD-Pads TP1–TP4; LED an +3V3.
- **Rev 4e (2026-10-23):** U1 Ag9905-LPB (SMT, 5 Pads) statt Ag9905LP (DIL nicht lieferbar); TP1–TP4 → SWD-Randpads J3.
- **Rev 4e Review (2026-10-23):** K1 RX-Koppel-C C65/C66 6,8 nF; H1 Y1 ABM8-272-T3 + 2 × 15 pF; Kunststoffrohr, Umgebung ≤ 40 °C; PSE 802.3af/at ≥ 48 V. 84 Refs / 42 Netze.
- **Rev 4f (2026-10-26):** Status-LED D11 normale grüne 0603-LED statt WS2812B, C64 entfällt; Schaltplan vollständig mit Leitungen gezeichnet; Pin-1-Punkte im Bestückungsdruck.
- **Rev 4g (2026-10-26):** MagJack-LEDs wieder beschaltet (R5/R6, U5 LINKLED/ACTLED). 85 Refs / 46 Netze.
