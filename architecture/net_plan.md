# Net Plan – poe_usb_hid_bridge (Rev 4e)

Stand: 2026-10-26 · gültiger Endstand **Rev 4g** · Quelle der Wahrheit: SKiDL-Code `circuits/poe_usb_hid_bridge/` (Netzliste `outputs/poe_usb_hid_bridge_rev4g.net`: **85 Teile, 46 Netze**, ERC 0/0).
Typen: `PWR-P` / `GND-P` (Primär), `PWR-S` / `GND-S` (Sekundär), `ANA`, `DIFF100` / `DIFF90`, `SIG`, `CLK`, `DBG`.

---

## 1. Netze

### 1.1 Primärseite (Isolationsgruppe PRI, Netzklasse `POE_HV`)

| Netz | Typ | Verbindungen |
|---|---|---|
| `PSE_CT12` | PWR-P (37–57 V, bel. Polarität) | J1.7 (CT Paar 1/2) → D1.3 (~) |
| `PSE_CT36` | PWR-P | J1.8 (CT Paar 3/6) → D1.4 (~) |
| `PSE_SP45` | PWR-P | J1.9 (Reservepaar 4/5) → D2.3 (~) |
| `PSE_SP78` | PWR-P | J1.10 (Reservepaar 7/8) → D2.4 (~) |
| `VDD_POE` | PWR-P (+) | D1.1, D2.1 (+), D3.1 (K), C1.1 (DNP), **U1.4 (VIN+)** |
| `VSS` | GND-P (−) | D1.2, D2.2 (−), D3.2 (A), C1.2 (DNP), **U1.5 (VIN−)**, C14.1 (DNP) |

### 1.2 Sekundärseite – Leistung

| Netz | Typ | Verbindungen |
|---|---|---|
| `+5V_RAW` | PWR-S (5,00 V, 4,75–5,25) | **U1.1 (+VDC)**, C11.1 (+), C12.1, C10.1, R8.1 (DNP), FB1.1 |
| `AG_ADJ` | ANA-S | **U1.3 (ADJ)**, R9.1 (DNP) – offen = 5,00 V |
| `+5V` | PWR-S | FB1.2, C13.1, D12.1 (K), TP9, U4.6 (IN), U4.4 (EN), C15.1, U6.1 (IN), C17.1 |
| `+3V3` | PWR-S | U4.1 (OUT), C16.1, U5 IOVDD 13/25/43/53/60/64, U5.42 (W5500 VDD), U5.54 (ADC_AVDD), U5.55 (VREG_VIN), U5.59 (USB_VDD), U5.62 (VDD_FLASH), C40–C47, C51–C54, FB2.1, R5.2, R6.2 (MagJack-LED-Anoden), J3.4 |
| `+3V3A` | PWR-S (W5500 analog) | FB2.2, U5 AVDD 3/6/8/31/34, C55–C59, C60.1, R1.1, R2.1, **J1.3 (gemeinsamer CT)**, C23.1 |
| `+1V1` | PWR-S (Core) | U5.56 (VREG_VOUT), U5.26, U5.61 (DVDD), C48.1, C49.1, C50.1 |
| `VBUS_USB` | PWR-S (geschaltet) | U6.6 (OUT), C18.1 (+), C19.1, C20.1, U7.5, J2.1, R32.1 |
| `ILIM_SET` | ANA-S | U6.5, R25.1 (44,2 k → GND) |
| `GND` | GND-S | **U1.2 (−VDC)**, alle Sekundär-Entkoppel-C (Pin 2), C11.2, C12.2, C13.2, C14.2 (DNP), R8.2, R9.2, D12.2, U4.3, U4.7 (EP), U5.22 (TESTEN), U5.69 (EP), R22.2, Y1.2/4, Y2.2/4, C25–C28 (Pin 2), U6.2, U7.2, J2.4, R26.2, R30.2/R31.2 (DNP), R33.2, R34.2, C30.2 (DNP), R7.2, C24.2, C21.2, C23.2, D11.2, J3.2 |

### 1.3 Sekundärseite – Signale

| Netz | Typ | Verbindungen |
|---|---|---|
| `ETH_TXP` / `ETH_TXN` | DIFF100 | U5.2 / U5.1 ↔ J1.1 / J1.2; R1 / R2 (49,9 Ω) → +3V3A |
| `ETH_RXP` / `ETH_RXN` | DIFF100 (chipseitig) | U5.5 / U5.4, C65.2 / C66.2, R3.1 / R4.1 (49,9 Ω → `ETH_RX_TERM`) |
| `ETH_RXP_J` / `ETH_RXN_J` | DIFF100 (J1-seitig, **neu K1**) | J1.4 / J1.5 ↔ C65.1 / C66.1 (6,8 nF X7R in Serie = DC-Trennung der RX-Pins vom CT +3V3A; im Code `do_erc = False`, rein passiv) |
| `ETH_RX_TERM` | ANA-S | R3.2, R4.2, C21.1 (10 nF → GND) – **keine** DC-Verbindung zu +3V3A; zusammen mit C65/C66 wie WIZnet-W5500-Referenz „connected CT" |
| `SHIELD_RJ45` | Chassis | J1.SH → R7 (1 MΩ) ∥ C24 (4,7 nF/2 kV) → GND |
| `USB_DP_MCU` / `USB_DM_MCU` | DIFF90 | U5.58 / U5.57 ↔ R28.1 / R29.1 |
| `USB_DP` / `USB_DM` | DIFF90 | R28.2 / R29.2 ↔ U7.1+U7.6 / U7.3+U7.4 ↔ J2.3 / J2.2; R30.1 / R31.1 (15 k, DNP) |
| `USB_SHIELD` | Chassis | J2.SH → R34 (0 Ω) ∥ C30 (4,7 nF, DNP) → GND |
| `USB_EN` | SIG | U5.46 (GPIO26) → U6.3 (EN); R26 100 k → GND |
| `VBUS_SENSE` | ANA | R32.2, R33.1, C29.1, U5.49 (GPIO29/ADC3); Faktor 0,405 (2,02 V bei 5,00 V) |
| `LED_DIN` | SIG (3,3 V, statisch/PWM) | U5.48 (GPIO28) → R38.1 (330 Ω) – Name historisch (Rev 4b–4e WS2812-Daten) |
| `LED_DIN_R` | SIG | R38.2 → D11.2 (Anode); D11.1 (Kathode) → GND |
| `ETH_LED_LINK_N` | SIG (aktiv low) | U5.37 (LINKLED) → J1.14 (grün K) |
| `ETH_LED_ACT_N` | SIG (aktiv low) | U5.39 (ACTLED) → J1.12 (gelb K) |
| `ETH_LED_LINK_A` / `ETH_LED_ACT_A` | SIG | J1.13 / J1.11 (Anoden) → R6.1 / R5.1 (330 Ω an +3V3) |
| `SWCLK` / `SWDIO` | DBG | U5.27 / U5.28 ↔ J3.1 / J3.3 |
| `XTAL12_XIN` | CLK | U5.23, Y1.1, C25.1 |
| `XTAL12_XOUT` | CLK | U5.24, R37.1 |
| `XTAL12_XO_R` | CLK | R37.2, Y1.3, C26.1 |
| `XTAL25_XI` / `XTAL25_XO` | CLK | U5.44, Y2.1, C27.1 / U5.45, Y2.3, C28.1 |
| `ETH_EXRES` | ANA | U5.7, R22.1 (12,4 k 1 %) |
| `W5500_TOCAP` / `W5500_1V2O` | ANA | U5.33, C61.1 (4,7 µF) / U5.35, C62.1 (10 nF) |

## 2. Isolationsüberquerer

| Primär ↔ Sekundär | Teil | Bemerkung |
|---|---|---|
| `VDD_POE`/`VSS` ↔ `+5V_RAW`/`GND` | U1 Ag9905-LPB | 1500 V Impulstest (DS V3.5 §6), F.Cu-Keepout im Footprint |
| `VSS` ↔ `GND` | C14 2,2 nF X1/Y2 | **DNP** (EMV-Option; DS V3.5 Fig. 16 zeigt 2 × 4,7 nF/2 kV) |
| J1-Bob-Smith-Bus ↔ `SHIELD_RJ45` → `GND` | J1-intern 1 nF/2 kV, extern R7 ∥ C24 | einziger bestückter Y-Pfad (≈ 0,8 nF), siehe design_risks R-ISO-7 |

## 3. W55RP20 (U5) – vollständige Pinbelegung

Quelle: W55RP20 DS V1.0.0 (`datasheets/W55RP20_SUMMARY.md`).

| Pin | Name | Netz | | Pin | Name | Netz |
|---|---|---|---|---|---|---|
| 1 | TXN | **ETH_TXN** | | 35 | 1V2O | W5500_1V2O |
| 2 | TXP | **ETH_TXP** | | 36 | SPDLED | NC |
| 3 | AVDD | +3V3A | | 37 | LINKLED | **ETH_LED_LINK_N** |
| 4 | RXN | **ETH_RXN** | | 38 | DUPLED | NC |
| 5 | RXP | **ETH_RXP** | | 39 | ACTLED | **ETH_LED_ACT_N** |
| 6 | AVDD | +3V3A | | 40 | GPIO18 | NC (Reserve) |
| 7 | EXRES1 | ETH_EXRES | | 41 | GPIO19 | NC (Reserve) |
| 8 | AVDD | +3V3A | | 42 | VDD (W5500) | +3V3 |
| 9–12 | GPIO4–7 | NC | | 43 | IOVDD | +3V3 |
| 13 | IOVDD | +3V3 | | 44 / 45 | XI / XO | XTAL25_XI / XTAL25_XO |
| 14–21 | GPIO8–15 | NC | | 46 | GPIO26/ADC0 | **USB_EN** |
| 22 | TESTEN | GND | | 47 | GPIO27/ADC1 | NC (Reserve) |
| 23 / 24 | XIN / XOUT | XTAL12_XIN / XTAL12_XOUT | | 48 | GPIO28/ADC2 | **LED_DIN** |
| 25 | IOVDD | +3V3 | | 49 | GPIO29/ADC3 | **VBUS_SENSE** |
| 26 | DVDD | +1V1 | | 50–52 | PMODE2/1/0 | NC (interne Pull-ups → 111, Auto-Neg.) |
| 27 | SWCLK | SWCLK | | 53 | IOVDD | +3V3 |
| 28 | SWDIO | SWDIO | | 54 | ADC_AVDD | +3V3 |
| 29 | RUN | NC (interner Pull-up) | | 55 | VREG_VIN | +3V3 |
| 30 | GPIO16 | NC | | 56 | VREG_VOUT | +1V1 |
| 31 | AVDD | +3V3A | | 57 / 58 | USB_DM / USB_DP | **USB_DM_MCU** / **USB_DP_MCU** |
| 32 | VBG | NC | | 59 | USB_VDD | +3V3 |
| 33 | TOCAP | W5500_TOCAP | | 60 | IOVDD | +3V3 |
| 34 | AVDD | +3V3A | | 61 | DVDD | +1V1 |
| | | | | 62 | VDD_FLASH | +3V3 |
| | | | | 63 | BOOT (QSPI_SS) | NC (interner Pull-up) |
| | | | | 64 | IOVDD | +3V3 |
| | | | | 65 / 66 | GPIO0 / GPIO1 | NC (UART0-Reserve) |
| | | | | 67 / 68 | GPIO2 / GPIO3 | NC |
| | | | | 69 (EP) | GND | GND |

GPIO17 und GPIO20–25 sind nicht herausgeführt (interne W5500-Anbindung). Zuordnung **verifiziert** (2. Review 2026-10-23, WIZnet-PICO-C, W55RP20-Port): CS 20, SCK 21, MISO 22, MOSI 23, INTn 24, RSTn 25, PIO-SPI (`USE_PIO`). GPIO28 (Status-LED D11) ist seit Rev 4f ein normaler GPIO-Ausgang (kein PIO).

**Offene Pins (bewusst, Datenblatt-geprüft):** RUN (29) – RP2040-DS Tab. 619 „Reset State Pull-Up", Pico-DS ≈ 50 kΩ; BOOT/QSPI_SS (63) – RP2040-DS Tab. 616 „Reset State Pull-Up"; SPDLED/DUPLED (36/38) – Push-Pull-Ausgänge, offen zulässig.

## 4. Pin-für-Pin je Block

Format `Ref.Pin → Netz`; zweipolige Passive Pin 1 / Pin 2. Ports **fett**.

### B1 – `ethernet_magjack()`
Ports: **PSE_CT12, PSE_CT36, PSE_SP45, PSE_SP78, ETH_TXP, ETH_TXN, ETH_RXP, ETH_RXN, +3V3A, +3V3, GND, ETH_LED_LINK_N, ETH_LED_ACT_N** (intern `ETH_RXP_J`, `ETH_RXN_J`, `ETH_RX_TERM`, `SHIELD_RJ45`, `ETH_LED_ACT_A`, `ETH_LED_LINK_A`)

| Ref.Pin | Netz | Ref.Pin | Netz |
|---|---|---|---|
| J1.1 (TD+) | **ETH_TXP** | J1.7 (VC1+, 1/2) | **PSE_CT12** |
| J1.2 (TD−) | **ETH_TXN** | J1.8 (VC1−, 3/6) | **PSE_CT36** |
| J1.3 (CT gemeinsam) | **+3V3A** | J1.9 (VC2+, 4/5) | **PSE_SP45** |
| J1.4 (RD+) | ETH_RXP_J (→ C65 → **ETH_RXP**) | J1.10 (VC2−, 7/8) | **PSE_SP78** |
| J1.5 (RD−) | ETH_RXN_J (→ C66 → **ETH_RXN**) | J1.11 / J1.12 (gelb A/K) | ETH_LED_ACT_A / **ETH_LED_ACT_N** |
| J1.6 | – (kein Pin) | J1.13 / J1.14 (grün A/K) | ETH_LED_LINK_A / **ETH_LED_LINK_N** |
| | | J1.SH (Schirm) | SHIELD_RJ45 |

| Ref | Wert | Pin 1 | Pin 2 |
|---|---|---|---|
| R1 / R2 | 49,9 Ω 0402 | +3V3A | ETH_TXP / ETH_TXN |
| C65 / C66 | 6,8 nF 50 V X7R 0402 (K1) | ETH_RXP_J / ETH_RXN_J | ETH_RXP / ETH_RXN |
| R3 / R4 | 49,9 Ω 0402 | ETH_RXP / ETH_RXN | ETH_RX_TERM |
| C21 | 10 nF 0402 | ETH_RX_TERM | GND |
| C23 | 100 nF 0402 | +3V3A | GND (an J1.3) |
| R7 | 1 MΩ 0603 | SHIELD_RJ45 | GND |
| C24 | 4,7 nF 2 kV 1812 | SHIELD_RJ45 | GND |
| R5 / R6 | 330 Ω 0402 (Rev 4g, Bottom neben J1) | ETH_LED_ACT_A / ETH_LED_LINK_A | **+3V3** |

### B2 – `poe_pd_module()`
Ports: **PSE_CT12, PSE_CT36, PSE_SP45, PSE_SP78, +5V, GND**

U1 Ag9905-LPB (DS V3.5 Tab. 2): **1 +VDC · 2 −VDC · 3 ADJ · 4 VIN+ · 5 VIN−**.

| Ref.Pin | Netz | Ref.Pin | Netz |
|---|---|---|---|
| U1.1 (+VDC) | +5V_RAW | U1.4 (VIN+) | VDD_POE |
| U1.2 (−VDC) | **GND** | U1.5 (VIN−) | VSS |
| U1.3 (ADJ) | AG_ADJ | | |
| D1.1 / .2 / .3 / .4 | VDD_POE / VSS / **PSE_CT12** / **PSE_CT36** | D2.1 / .2 / .3 / .4 | VDD_POE / VSS / **PSE_SP45** / **PSE_SP78** |
| D3.1 (K) / D3.2 (A) | VDD_POE / VSS | D12.1 (K) / D12.2 (A) | **+5V** / **GND** |
| FB1.1 / FB1.2 | +5V_RAW / **+5V** | TP9 | **+5V** |

| Ref | Wert | Pin 1 | Pin 2 | Bestückung |
|---|---|---|---|---|
| C1 | 100 nF 100 V 0805 | VDD_POE | VSS | **DNP** (Detection-Kapazität, R4-3) |
| C10 | 100 nF 0402 | +5V_RAW | GND | bestückt |
| C11 | 100 µF 10 V Polymer 7343 | +5V_RAW (+) | GND | bestückt, nahe U1.1/U1.2 |
| C12 | 22 µF 25 V 0805 | +5V_RAW | GND | bestückt |
| C13 | 22 µF 25 V 0805 | +5V | GND | bestückt |
| C14 | 2,2 nF X1/Y2 1812 | VSS | GND | **DNP** |
| R8 | 100 Ω 1206 (RB) | +5V_RAW | GND | **DNP** (Mindestlast) |
| R9 | offen (ADJ-Trimm) | AG_ADJ | GND | **DNP** (nach GND hebt V_out, 0 Ω → 5,65 V) |

### B4 – `ldo_3v3()`
Ports: **+5V, +3V3, GND**

| Ref.Pin | Netz |
|---|---|
| U4.6 IN, U4.4 EN | **+5V** |
| U4.1 OUT | **+3V3** |
| U4.3 GND, U4.7 EP | **GND** |
| U4.2, U4.5 | NC |
| C15 4,7 µF 0603 | +5V / GND |
| C16 10 µF 0603 | +3V3 / GND |

### B5 – `mcu_w55rp20()`
Ports: **+3V3, +3V3A, GND, ETH_TXP, ETH_TXN, ETH_RXP, ETH_RXN, USB_DP_MCU, USB_DM_MCU, USB_EN, VBUS_SENSE, LED_DIN** (U5-Pins siehe §3)

| Ref | Wert | Pin 1 | Pin 2 | Bemerkung |
|---|---|---|---|---|
| C40–C45 | 100 nF 0402 | +3V3 | GND | IOVDD 13/25/43/53/60/64 |
| C46 | 10 µF 0603 | +3V3 | GND | Bulk |
| C47 | 1 µF 0402 | +3V3 | GND | VREG_VIN 55 |
| C48 | 1 µF 0402 | +1V1 | GND | VREG_VOUT 56 |
| C49 / C50 | 100 nF | +1V1 | GND | DVDD 26 / 61 |
| C51–C54 | 100 nF | +3V3 | GND | USB_VDD 59 / ADC 54 / Flash 62 / W5500-VDD 42 |
| C55–C59 | 100 nF | +3V3A | GND | AVDD 3/6/8/31/34 |
| C60 | 10 µF 0603 | +3V3A | GND | Bulk |
| FB2 | 120 Ω@100 MHz 0603 | +3V3 | +3V3A | |
| C61 | 4,7 µF 0603 | W5500_TOCAP | GND | DS S. 10 fordert „direkt an U5.33, kein Via" – im Layout **nicht direkt am Pin** (Review, offen: design_risks R-LAY-7) |
| C62 | 10 nF 0402 | W5500_1V2O | GND | |
| R22 | 12,4 k 1 % | ETH_EXRES | GND | |
| Y1 | 12 MHz, C_L 10 pF, ESR ≤ 50 Ω – **Abracon ABM8-272-T3** (H1) | 1 = XTAL12_XIN, 3 = XTAL12_XO_R | 2, 4 = GND | Raspberry-Pi-Referenz |
| C25 / C26 | **15 pF C0G** | XTAL12_XIN / XTAL12_XO_R | GND | Raspberry-Pi-Referenz |
| R37 | 1 k | XTAL12_XOUT | XTAL12_XO_R | Leitungslängen XIN 3,2 mm, XOUT 2,2 mm, XO_R 9,7 mm |
| Y2 | 25 MHz 18 pF | 1 = XTAL25_XI, 3 = XTAL25_XO | 2, 4 = GND | |
| C27 / C28 | 27 pF C0G | XTAL25_XI / XTAL25_XO | GND | |
| J3 | SWD-Randpads 1×4, Raster 2,54 mm, Pads 1,5 × 3,0 mm (DNP) | 1 SWCLK / 2 GND / 3 SWDIO / 4 +3V3 | – | einziger Programmierzugang; Stiftleiste 2,54 mm liegend auflöten, Pins ragen über die Board-Kante (Pins 1–3 = Pico-SWD-Reihenfolge) |

### B6 – `usb_host_port()`
Ports: **+5V, GND, USB_EN, USB_DP_MCU, USB_DM_MCU, VBUS_SENSE**

| Ref.Pin | Netz | Ref.Pin | Netz |
|---|---|---|---|
| U6.1 IN | **+5V** | U7.1, U7.6 (I/O1) | USB_DP |
| U6.2 GND | **GND** | U7.2 GND | **GND** |
| U6.3 EN | **USB_EN** | U7.3, U7.4 (I/O2) | USB_DM |
| U6.4 FAULT | NC (Open-Drain, ungenutzt) | U7.5 VBUS | VBUS_USB |
| U6.5 ILIM | ILIM_SET | J2.1 VBUS / J2.2 D− | VBUS_USB / USB_DM |
| U6.6 OUT | VBUS_USB | J2.3 D+ / J2.4 GND | USB_DP / **GND** |
| | | J2.SH (Schirm) | USB_SHIELD |

| Ref | Wert | Pin 1 | Pin 2 |
|---|---|---|---|
| R25 | 44,2 k 1 % | ILIM_SET | GND |
| R26 | 100 k | USB_EN | GND |
| C17 | 1 µF 50 V | +5V | GND |
| C18 | 150 µF 6,3 V Polymer-Ta | VBUS_USB (+) | GND |
| C19 / C20 | 10 µF / 100 nF | VBUS_USB | GND |
| R28 / R29 | 27 Ω | USB_DP_MCU / USB_DM_MCU | USB_DP / USB_DM |
| R30 / R31 (DNP) | 15 k | USB_DP / USB_DM | GND |
| R32 / R33 | 100 k / 68 k | VBUS_USB / VBUS_SENSE | VBUS_SENSE / GND |
| C29 | 100 nF | VBUS_SENSE | GND |
| R34 | 0 Ω 0603 | USB_SHIELD | GND |
| C30 (DNP) | 4,7 nF 0603 | USB_SHIELD | GND |

### B7 – `status_led()`
Ports: **GND, LED_DIN** (Rev 4f)

| Ref.Pin | Netz |
|---|---|
| D11.1 K | **GND** |
| D11.2 A | LED_DIN_R |
| R38 330 Ω | **LED_DIN** / LED_DIN_R |

D11 MEIHUA MHT193CGCT (569 nm, Vf ≈ 2,2 V): GPIO28 High = an, I_F ≈ (3,3 − 2,1) V / 330 Ω ≈ 3,5 mA. C64 entfällt.

## 5. Netzklassen (KiCad-Projekt Rev 4g)

| Klasse | Netze | Breite / Abstand |
|---|---|---|
| `POE_HV` | PSE_CT12/36, PSE_SP45/78, VDD_POE, VSS | 0,3 / 0,3 mm untereinander; **≥ 3,0 mm zu jedem anderen Netz, alle Lagen** (DRU `ISO_PRI_SEC_3mm`) |
| `PWR_5V` | +5V_RAW, +5V, VBUS_USB | 0,6 mm bzw. Flächen |
| `Power` | +3V3, +3V3A, +1V1, GND | 0,3 mm bzw. Flächen |
| `ETH` | ETH_TXP/TXN, ETH_RXP/RXN, ETH_RXP_J/RXN_J | 100 Ω diff.: 0,13 / Gap 0,2 mm (gekoppelt in `ETH_COUPLED`), Skew ≤ 0,1 mm; RX gesamt inkl. C65/C66 P/N 60,525/60,529 mm |
| `USB` | USB_DP/DM, USB_DP_MCU/DM_MCU | 90 Ω diff.: 0,15 / Gap 0,18 mm, Länge ≤ 30 mm |
| `Default` | Rest | 0,15 / 0,15 mm |

DRC-Ausnahmen (DRU): U1-intern 0,5 mm, C14 0,5 mm, J1-Courtyard 1,0 mm (dokumentierte Abweichung R-ISO-3), U5-Courtyard 0,15 mm, in `U5_FANOUT` Vias 0,4/0,2 mm und 0,1 mm Abstand.

## 6. Pinbelegungs-Fallen

| Ref | Teil | Falle |
|---|---|---|
| U1 | Ag9905-LPB | **5 Pads, nicht pinkompatibel zur LP/DIL-Variante** (1 +VDC, 2 −VDC, 3 ADJ, 4 VIN+, 5 VIN−); Pin-1-Dreieck im Silkscreen; nur Top-Montage |
| J1 | HR871150C | Pin 6 fehlt; Schirm als Pin „SH"; P1/P2- bzw. P4/P5-Polarität mittlere Sicherheit (100BASE-TX unkritisch, W5500 Auto-Polarity) |
| D1, D2 | MB6S (MDD) | 1 = +, 2 = −, 3/4 = ~ – nur für MDD geprüft |
| D11 | MHT193CGCT 0603 | 1 = K (GND), 2 = A; Kathodenmarke im JLC-Viewer prüfen |
| J1 LEDs | HR871150C | 11 gelb A, 12 gelb K, 13 grün A, 14 grün K (DS S. 1/3 geprüft 2026-10-26) |
| U4 | TLV75733PDRVR | 1 OUT, 2 NC, 3 GND, 4 EN, 5 NC, 6 IN, 7 EP |
| U7 | USBLC6-2SC6 | 1/6 = I/O1 (D+), 3/4 = I/O2 (D−), 2 GND, 5 VBUS |
| J2 | BX-TYPE-A-MWT4P | 1 VBUS, 2 D−, 3 D+, 4 GND, SH Schirm (Custom-FP) |
| Y1, Y2 | Abracon ABM8 / YXC 3225-4 | 1/3 Quarz, 2/4 GND |
| C11, C18 | gepolt | Pin 1 = + |

---

## Änderungshistorie

- **Rev 1 (2026-10-21):** Netzplan mit diskretem Flyback (TPS23753A, T1, Opto/TLV431: `RTN`, `VIN_FLY`, `SW_DRAIN`, `CTL`, `VC`, `FB_*` …), J1 HY931147C, LED-Netze `LED_R/G/B` aktiv-low an +3V3.
- **Rev 2 (2026-10-21):** J1 HR871150C (1 CT, `ETH_RCT`/C22 entfallen), T1-Pinout korrigiert, LED an +5V über 2N7002 (aktiv-high), R13/`CS_SH`, Snubber-Knoten.
- **Rev 3 (2026-10-22):** 30 × 80-mm-Layoutvariante – verworfen.
- **Rev 4 (2026-10-22):** Leistungsteil durch Ag9905LP (DIL, 8 Pins) ersetzt; alle Flyback-Netze entfallen, neu `AG_ADJ`.
- **Rev 4b (2026-10-22):** `ETH_LED_*`, `LED_R/G/B` entfallen, neu `LED_DIN`/`LED_DIN_R`; Debug-Feld J3 (TC2050) mit SWD/UART/RUN/BOOT.
- **Rev 4c (2026-10-22):** Brücken R45–R49/`LED_VDD` – verworfen.
- **Rev 4d (2026-10-22):** `RUN`, `QSPI_SS_BOOT`, `BOOT_SW`, `UART0_TX/RX`, `USB_OC_N` entfallen; J3 → TP1–TP4; D11/C64 an +3V3.
- **Rev 4e (2026-10-23):** U1 Ag9905-LPB (SMT, 5 Pads); TP1–TP4 → **J3 SWD-Randpads** (`poe_usb_hid_bridge:SWD_Edge_1x04_P2.54mm_SMD`, 1 SWCLK, 2 GND, 3 SWDIO, 4 +3V3).
- **Rev 4e (2026-10-23):** U1 Ag9905-LPB: Netze unverändert, U1-Pinnummern neu (5 Pads).
- **Rev 4e Review (2026-10-23):** K1: C65/C66 6,8 nF in Serie im RX-Paar, neue Netze `ETH_RXP_J`/`ETH_RXN_J` (84 Teile, 42 Netze); H1: Y1 ABM8-272-T3 (C_L 10 pF), C25/C26 15 pF.
- **Rev 4f (2026-10-26):** D11 normale grüne LED (`LED_DIN_R` → Anode), C64 entfällt; D11 nicht mehr an +3V3.
- **Rev 4g (2026-10-26):** neu `ETH_LED_LINK_N`/`ETH_LED_ACT_N` (U5.37/39 ↔ J1.14/12) und `ETH_LED_LINK_A`/`ETH_LED_ACT_A` (J1.13/11 ↔ R6/R5 an +3V3); 85 Teile, 46 Netze.
