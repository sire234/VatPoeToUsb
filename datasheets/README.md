# Datenblatt-Index – poe_usb_hid_bridge (Stand Rev 4e nach Review K1/H1, 2026-10-23)

## Verwendete Bauteile (Rev 4e)

| Bauteil (MPN) | Funktion | Ref | Datenblatt | Kurzfassung |
|---|---|---|---|---|
| Silvertel **Ag9905-LPB** | PoE-PD-Modul 5 V / 1,4 A, Class 0, SMT | U1 | `Ag9900_V3.5_2026-03_LPB.pdf` | `Ag9900_V3.5_2026-03_LPB_SUMMARY.md` |
| WIZnet **W55RP20** | RP2040 + W5500 + 2 MB Flash, QFN-68 | U5 | `W55RP20.pdf` | `W55RP20_SUMMARY.md` |
| HanRun **HR871150C** | RJ45-PoE-MagJack 10/100 | J1 | `HR871150C.pdf` | `HR871150C_SUMMARY.md` |
| Bossie **BX-TYPE-A-MWT4P** | USB-A-Buchse liegend | J2 | `BX-TYPE-A-MWT4P.pdf` | `BX-TYPE-A-MWT4P_SUMMARY.md` |
| TI **TLV75733PDRVR** | LDO 3,3 V / 1 A, WSON-6 | U4 | `TLV75733PDRVR.pdf` | `TLV75733PDRVR_SUMMARY.md` |
| TI **TPS2553DBVR** | USB-Lastschalter (R_ILIM) | U6 | `TPS2553DBVR.pdf` | `TPS2553DBVR_SUMMARY.md` |
| ST **USBLC6-2SC6** | USB-ESD | U7 | `USBLC6-2SC6.pdf` | `USBLC6-2SC6_SUMMARY.md` |
| Worldsemi **WS2812B-2020-V6** | adressierbare RGB-LED | D11 | `WS2812B-2020-V6.pdf` *(neu)* | `WS2812B-2020-V6_SUMMARY.md` *(neu)* |
| MDD **MB6S** | Brückengleichrichter Mode A/B | D1, D2 | `MB6S.pdf` | `MB6S_SUMMARY.md` |
| MDD **SMAJ58A** | TVS 58 V | D3 | `SMAJ58A.pdf` (identisch mit `SMAJ43A.pdf`, Serienblatt) | `SMAJ58A_SUMMARY.md` |
| BORN **BZT52C6V2** | OVP-Zener 6,2 V | D12 | `BZT52C6V2.pdf` *(neu)* | `BZT52C6V2_SUMMARY.md` *(neu)* |
| Abracon **ABM8-272-T3** | Quarz 12 MHz, C_L 10 pF, ESR ≤ 50 Ω (Review H1, RPi-Referenz) | Y1 | `ABM8-272-T3.pdf` (Drawing #456603) | `ABM8-272-T3_SUMMARY.md` |
| YXC **X322525MRB4SI** | Quarz 25 MHz, 18 pF | Y2 | `X322525MRB4SI.pdf` | `X322525MRB4SI_SUMMARY.md` |
| AISHI **SA11AM101A19R15XXX** | Polymer-C 100 µF 10 V 15 mΩ | C11 | `SA11AM101A19R15XXX.pdf` *(neu)* | `SA11AM101A19R15XXX_SUMMARY.md` *(neu)* |
| KEMET **T520B157M006ATE035** | Polymer-Ta 150 µF 6,3 V (VBUS) | C18 | `T520B157M006ATE035.pdf` | `T520B157M006ATE035_SUMMARY.md` |
| TAI-TECH **HCB3216KF-601T30** | Ferrit 600 Ω / 3 A, 1206 | FB1 | `HCB3216KF-601T30.pdf` | `HCB3216KF-601T30_SUMMARY.md` |
| Murata **BLM18PG121SN1D** | Ferrit 120 Ω / 2 A, 0603 | FB2 | `BLM18PG121SN1D.pdf` *(neu)* | `BLM18PG121SN1D_SUMMARY.md` *(neu)* |
| IHHEC **C1812X472K202T** | 4,7 nF 2 kV, Schirm-C | C24 | `C1812X472K202T.pdf` *(neu)* | `C1812X472K202T_SUMMARY.md` *(neu)* |
| PSA **FK12X222K502EGQ** | Y2-Kondensator 2,2 nF (DNP-Option) | C14 | `FK12X222K502EGQ.pdf` | `FK12X222K502EGQ_SUMMARY.md` |

Ohne eigenes Datenblatt (Standard-Passive, Werte in `sourcing/sourced_bom.md`): Widerstände UNI-ROYAL 0402/0603/1206 (R1–R4, R7, R8, R22, R25, R26, R28–R34, R37, R38), Samsung-/FH-MLCC (C1, C10, C12, C13, C15–C17, C19–C21, C23, C25–C30, C40–C62, C64; C25/C26 seit Review 15 pF FH 0402CG150J500NT), YAGEO-MLCC C65/C66 (6,8 nF 50 V X7R 0402, CC0402KRX7R9BB682 – RX-Koppel-C, Review K1). R9 hat keinen Wert (DNP, Abgleich am Muster).

**Referenz für das Ag9900-Datenblatt V2.4:** `Ag9900_V2.4_2020-04_LP.pdf` beschreibt die nicht mehr verwendete DIL-Variante Ag9905LP (Rev 4–4d). Für Rev 4e gilt V3.5 (enthält LP und LPB).

## Nicht mehr verwendete Bauteile (Löschkandidaten – nicht gelöscht)

| Datei(en) | Bauteil | War verwendet in |
|---|---|---|
| `TPS23753APWR.pdf`, `_SUMMARY.md` | TI PoE-PD + PWM | Rev 1–3 (diskreter Flyback) |
| `POE70P-50LD.pdf`, `_SUMMARY.md` | Coilcraft Flyback-Übertrager | Rev 1–3 |
| `FDC2512.pdf`, `FDC2512_onsemi.pdf`, `_SUMMARY.md` | 150-V-MOSFET Q1 | Rev 1–3 |
| `LTV-357T-C.pdf`, `_SUMMARY.md` | Optokoppler U2 | Rev 1–3 |
| `TLV431BIDBZR.pdf`, `_SUMMARY.md` | Shunt-Referenz U3 | Rev 1–3 |
| `PMEG4050EP.pdf`, `_SUMMARY.md` | Sekundär-Schottky D10 | Rev 1–3 |
| `ES1D.pdf`, `_SUMMARY.md` | Clamp-Diode D7 | Rev 1–3 |
| `SMAJ43A.pdf`, `_SUMMARY.md` | Clamp-TVS D8 (PDF identisch mit SMAJ58A.pdf) | Rev 1–3 |
| `LVF303015-100M-N.pdf`, `_SUMMARY.md` | Pi-Filter-Drossel (NFND, schon Rev 2 ersetzt) | Rev 1 |
| `X322512MSB4SI_SUMMARY.md` (kein eigenes PDF, Familienblatt = `X322525MRB4SI.pdf`, das für Y2 weiter gilt) | YXC 12-MHz-Quarz 20 pF | Rev 2 – Rev 4e vor Review (ersetzt durch ABM8-272-T3, H1) |
| `E6C0606RGBC3UDA.pdf`, `_SUMMARY.md` | EKINGLUX RGB-LED | Rev 2–4 |
| `2N7002.pdf`, `_SUMMARY.md` | LED-Low-Side-FETs Q2–Q4 | Rev 2–4 |
| `KMR211NGLFS.pdf`, `_SUMMARY.md` | BOOTSEL-Taster SW1 | Rev 1–4b |
| `Ag9900_V2.4_2020-04_LP.pdf` | Ag9905LP (DIL) | Rev 4–4d (nur noch als historische Referenz im Docstring von `poe_pd_module.py` erwähnt) |

Für TC2050 (Tag-Connect, Rev 4b), HY931147C (Rev 1), TDK VLS3012CX und TPS2051B lagen nie Datenblätter in diesem Ordner.
