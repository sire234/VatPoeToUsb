# W55RP20 — WIZnet SiP: RP2040 + W5500 (Hardwired TCP/IP, 10/100 PHY) + 2 MB Flash, QFN-68

Quelle: WIZnet W55RP20 Datenblatt V1.0.0 (chinesisch, 36 Seiten), `W55RP20.pdf`; Pin-Tabellen (S.8-12), Package (S.29), Elektrik (S.31-35) als PNG gerendert und gelesen. Status: Pinliste VERIFIZIERT.

| Spec | Value |
|------|-------|
| Package | QFN-68 8.00 x 8.00 mm, Pitch 0.40, Pad b 0.15-0.25, L 0.35-0.45, Hoehe A 0.80-0.90 (typ 0.85), EP (Pin 69 = GND) D2/E2 6.15-6.25 (typ 6.2) |
| Land Pattern | **Datenblatt Abschnitt 5.2 "TBD"**; Fig. 5: "PAD SIZE 236 x 23* mil" (ca. 6.0 x 0.58 mm Angabe unklar) -> Pad-Masse UNVERIFIZIERT |
| IOVDD | 1.62-3.63 V (abs. max 3.63 V; Pin-Spannung max IOVDD+0.5) |
| DVDD (Core) | 1.05-1.16 V (typ 1.1); aus VREG_VOUT |
| VREG_VIN | 1.62-3.63 V; VREG_VOUT 1.1 V max 100 mA |
| USB_VDD | 3.135-3.63 V; ADC_AVDD 1.62-3.63 V |
| W5500-VDD / AVDD | 2.97-3.63 V (typ 3.3 V) |
| Gehaeusetemperatur | Tc -40..+85 C |
| ESD | HBM 2 kV (FT-Pins 4 kV), CDM 500 V |
| W5500 25-MHz-Quarz | 25 MHz, +-30 ppm, **CL 18 pF**, C0 max 7 pF, Drive 59.12 uW/MHz |
| RP2040-Quarz | 12 MHz (USB-Bootloader braucht 12 MHz) an XIN/XOUT |
| W5500 PMODE | PMODE[2:0] intern Pull-up 77 k (62-112 k) -> Default 111 = alle Funktionen, Auto-Neg. |

## Pinliste (Top View, QFN-68; Pin 1 oben links, unten Seite links 1-17, unten 18-34, rechts 35-51 aufwaerts, oben 52-68)
| Pin | Name | Chip | Funktion |
|-----|------|------|----------|
| 1 | TXN | W5500 | TX diff - |
| 2 | TXP | W5500 | TX diff + |
| 3 | AVDD | W5500 | 3.3 V analog |
| 4 | RXN | W5500 | RX diff - |
| 5 | RXP | W5500 | RX diff + |
| 6 | AVDD | W5500 | 3.3 V analog |
| 7 | EXRES1 | W5500 | 12.4 k 1 % nach GND |
| 8 | AVDD | W5500 | 3.3 V analog |
| 9-12 | GPIO4-7 | RP2040 | GPIO |
| 13 | IOVDD | RP2040 | IO-Versorgung 3.3 V |
| 14-17 | GPIO8-11 | RP2040 | GPIO |
| 18-21 | GPIO12-15 | RP2040 | GPIO |
| 22 | TESTEN | RP2040 | Testmodus: **an GND** |
| 23 / 24 | XIN / XOUT | RP2040 | 12-MHz-Quarz |
| 25 | IOVDD | RP2040 | 3.3 V |
| 26 | DVDD | RP2040 | 1.1 V Core (an VREG_VOUT) |
| 27 / 28 | SWCLK / SWD | RP2040 | Debug |
| 29 | RUN | RP2040 | Reset (low = Reset), Pull-up / an IOVDD wenn unbenutzt |
| 30 | GPIO16 | RP2040 | GPIO |
| 31 | AVDD | W5500 | 3.3 V analog |
| 32 | VBG | W5500 | Bandgap-Ausgang (offen) |
| 33 | TOCAP | W5500 | **4.7 uF** nach GND, Leitung kurz |
| 34 | AVDD | W5500 | 3.3 V analog |
| 35 | 1V2O | W5500 | **10 nF** nach GND (1.2 V Reg.) |
| 36 | SPDLED | W5500 | low = 100 Mbps |
| 37 | LINKLED | W5500 | low = Link |
| 38 | DUPLED | W5500 | low = Full Duplex |
| 39 | ACTLED | W5500 | low = Aktivitaet |
| 40 / 41 | GPIO18 / GPIO19 | RP2040 | GPIO |
| 42 | VDD | W5500 | 3.3 V digital |
| 43 | IOVDD | RP2040 | 3.3 V |
| 44 / 45 | XI / XO | W5500 | 25-MHz-Quarz |
| 46-49 | GPIO26-29 / ADC0-3 | RP2040 | GPIO/ADC |
| 50 / 51 / 52 | PMODE2 / 1 / 0 | W5500 | PHY-Modus (intern Pull-up) |
| 53 | IOVDD | RP2040 | 3.3 V |
| 54 | ADC_AVDD | RP2040 | ADC-Versorgung (1.62-3.63 V) |
| 55 | VREG_VIN | RP2040 | Regler-Eingang |
| 56 | VREG_VOUT | RP2040 | 1.1 V Ausgang |
| 57 / 58 | USB_DM / USB_DP | RP2040 | USB FS (27 R in Serie extern) |
| 59 | USB_VDD | RP2040 | 3.3 V USB-PHY |
| 60 | IOVDD | RP2040 | 3.3 V |
| 61 | DVDD | RP2040 | 1.1 V Core |
| 62 | VDD | Flash | Flash-Versorgung 3.3 V |
| 63 | BOOT | RP2040 | QSPI_SS/BOOTSEL: low beim Reset = BOOTSEL |
| 64 | IOVDD | RP2040 | 3.3 V |
| 65-68 | GPIO0-3 | RP2040 | GPIO |
| 69 (EP) | GND | gemeinsam | Masse |
Versorgungspins: IOVDD 13, 25, 43, 53, 60, 64; DVDD 26, 61; AVDD (W5500) 3, 6, 8, 31, 34; VDD (W5500) 42; VDD Flash 62; ADC_AVDD 54; VREG_VIN 55; USB_VDD 59. **Identisch mit net_plan.md** (verifiziert).

## GPIO / interne Verbindungen
- Nach aussen gefuehrt: GPIO0-16, 18, 19, 26-29. Datenblatt-GPIO-Funktionstabelle (Table 5, S.17-18) fuehrt nur diese. GPIO0 F2 = UART0 TX, GPIO1 F2 = UART0 RX; GPIO18 F9 = USB OVCUR DET, GPIO26 F9 = USB VBUS EN (RP2040-Standard).
- **GPIO17 und GPIO20-25 sind nicht herausgefuehrt.** Das Datenblatt sagt nur: "Einer der beiden PIO-Bloecke wird fuer die Kommunikation mit dem W5500 benutzt" (4.8). Die Zuordnung steht nicht im Datenblatt, ist aber **VERIFIZIERT (2. Review 2026-10-23) aus WIZnet-PICO-C (W55RP20-Port)**: CS = GPIO20, SCK = GPIO21, MISO = GPIO22, MOSI = GPIO23, INTn = GPIO24, RSTn = GPIO25, Zugriff ueber PIO-SPI (`USE_PIO`). Die WS2812-LED (GPIO28) muss deshalb auf dem **anderen PIO-Block** laufen (`pio_claim_free_sm_and_add_program`).
- Stromverbrauch (5.4.6): "TBD".

## Notes
- Referenz-Beschaltung des W5500 verlangt: EXRES1 12.4 k 1 %, TOCAP 4.7 uF, 1V2O 10 nF, 25-MHz-Quarz CL 18 pF (Y2 18 pF + 27 pF C0G Lasten: CL = 27*27/54 + Cstray ~ 17-18 pF OK).
- USB: 27 R in Serie an DP/DM extern (Datenblatt).
- BOM: Package-Masse/Hoehe 0.9 max, MSL3 laut sourced_bom.
