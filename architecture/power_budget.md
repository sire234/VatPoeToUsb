# Power Budget – poe_usb_hid_bridge (Rev 4e)

Stand: 2026-10-26 · gültiger Endstand **Rev 4g**. Werte sind Abschätzungen aus Datenblatt-Typwerten; **(V)** = am Muster zu verifizieren.
Moduldaten: Silvertel Ag9900 DS V3.5 (Ag9905-LPB, elektrisch und thermisch identisch mit der LP-Variante). Spannungen: +5V_RAW 5,00 V, +3V3 3,30 V, PoE am PD 37–57 V (Rechnung mit 37 V = Worst Case).

## 1. Modulgrenzen (U1 Ag9905-LPB)

| Grösse | Wert | Bemerkung |
|---|---|---|
| +5V_RAW | **5,00 V (4,75–5,25 V)** | ADJ offen; Trimmoption R9 (ADJ → GND; DS Tab. 4: 0 Ω → 5,65 V). **Obergrenze +5V_RAW ≤ 5,25 V** – R9 = 0 Ω ist unzulässig |
| Eingang PSE | **IEEE 802.3af/at, ≥ 48 V nominal** | passives 24-V-PoE reicht nicht (UVLO 30–36 V, Anlauf ≥ 42 V) |
| Line/Load-Regulation | 0,01 % / 0,08 % | |
| I_out,max | **1,4 A** | |
| P_out,max | **7 W bis 70 °C, 4,5 W bei 85 °C** (Fig. 10 „LP(B) Operating Profile") | Thermoschutz reduziert die Leistung |
| Mindestlast | **200 mA** | darunter hörbares Geräusch, MPS-Risiko |
| η | Peak 83 % | Rechnung mit 80 % |
| Eingang | 36–57 V, Anlauf ≥ 42 V, UVLO 30–36 V, Surge 80 V / 1 ms | D3 SMAJ58A |
| Ausgangs-C | ≥ 100 µF low-ESR (Pflicht) + Keramik | C11 100 µF Polymer 15 mΩ (Ripple 2,5 A) + C12 22 µF + C10 100 nF |
| Ripple | 120 mVpp (Filter A) | FB1 + C13 als zusätzliches Post-Filter |

## 2. Lasten an +3V3 (LDO U4)

| Verbraucher | typ. [mA] | max. [mA] | Quelle |
|---|---|---|---|
| W5500-Teil (100BASE-TX, Link + Traffic) | 132 | 145 | W5500-DB **(V; W55RP20-DB „TBD")** |
| RP2040-Teil, 125 MHz, USB-Host aktiv | 30 | 50 | RP2040-DB/Pico **(V)** |
| Interner Flash | 5 | 15 | |
| Status-LED D11 (Rev 4f, grün 0603, 330 Ω) | 3,5 | 3,5 | GPIO28 High |
| MagJack-LEDs (Rev 4g, 2 × 330 Ω) | 4 (Link an) | 8 (Link + Activity) | W5500 LINKLED/ACTLED |
| Pull-ups, Teiler, Leckströme | 0,5 | 1 | |
| **Summe I(+3V3)** | **≈ 175** | **≈ 222** | TLV75733P (1 A) mit grosser Reserve |

**LDO-Verlust:** P_LDO = (V_5V − 3,3 V) · I = 1,70 V · 0,180 A = **0,31 W typ.** / 1,95 V (5,25 V) · 0,247 A = **0,48 W max.** θJA WSON-6 mit EP auf Mehrlagen-Kupfer ≈ 70–85 K/W **(V)** → ΔT ≈ 22–41 K. AP2112K (θJA ≈ 250 K/W) wäre ungeeignet.

## 3. Lasten an +5V_RAW

| Fall | P(+5V_RAW) | I(+5V_RAW) |
|---|---|---|
| Leerlauf ohne USB, Link aktiv | ≈ 0,9 W | **≈ 0,18 A** (< 200 mA Mindestlast) |
| Leerlauf ohne Link (Schätzung **(V)**) | ≈ 0,5 W | ≈ 0,10 A |
| Typisch (USB 0,5 A) | **3,44 W** | 0,69 A |
| Max. normal (USB 0,5 A, Logik max., LED voll) | **3,73 W** | 0,75 A |
| USB-Überlast (TPS2553 I_OS,max 0,659 A) | **4,52 W** | 0,90 A |

Reserve: 0,90 A ≪ 1,4 A ✓; 4,52 W < 7 W (≤ 70 °C) ✓, aber an der 4,5-W-Grenze bei 85 °C (siehe §6). *Die Zeilen stammen aus der Rev-4-Rechnung (LED damals an +5V); mit der LED an +3V3 (Rev 4d) läuft deren Strom über den LDO – die +5V_RAW-Summe ändert sich dadurch nur um wenige mW.*

## 4. PD-Eingangsleistung und Klasse

| Fall | P_in Modul (η 80 %) | I_in @ 37 V | Brücken (2 × 0,85 V) | **P am PD** |
|---|---|---|---|---|
| Leerlauf (Link) | 1,11 W | 0,030 A | 0,05 W | **1,16 W** |
| Typisch | 4,30 W | 0,116 A | 0,20 W | **4,50 W** |
| Max. normal | 4,66 W | 0,126 A | 0,21 W | **4,87 W** |
| USB-Überlast | 5,65 W | 0,153 A | 0,26 W | **5,91 W** |

**PoE-Klasse 0** (fest im Modul, 0,44–12,95 W) – alle Fälle weit darunter. Nachteil: Die PSE reserviert 15,4 W pro Port.
MPS (802.3af, ≥ 10 mA DC): Leerlauf mit Link ≈ 30 mA ✓, ohne Link ≈ 18–20 mA **(V)** ✓.

## 5. Mindestlast 200 mA
Leerlauf ohne USB-Gerät ≈ 180 mA (mit Link) bzw. ≈ 100 mA (ohne Link) → unter der Mindestlast: Lückbetrieb mit leisem Geräusch; laut DS arbeitet das Modul trotzdem sicher. Option **R8 (RB, 1206, DNP)**: 100 Ω → +50 mA / +0,25 W Wärme. Ein dauerhafter 200-mA-Bleeder (1 W) ist im Rohr nicht vertretbar.

## 6. Wärmebilanz im Rohr

| Quelle | typ. [W] | USB-Fehlerfall [W] |
|---|---|---|
| Ag9905-LPB (P_out/η − P_out) | 0,86 | 1,13 |
| Brücken D1/D2 | 0,20 | 0,26 |
| LDO | 0,31 | 0,48 |
| W55RP20 + LED (3,3-V-Leistung) | 0,59 | 0,82 |
| Lastschalter, FB1, Teiler | 0,05 | 0,08 |
| **Summe** | **≈ 2,0 W** | **≈ 2,8 W** |

- Grobabschätzung (natürliche Konvektion, h ≈ 10 W/m²K, Rohr ≈ 90 mm, R_th ≈ 12 K/W): ΔT Rohroberfläche ≈ 24 K typ. / 33 K Fehlerfall, innen +5–10 K bei Kunststoffrohr (Wand isoliert, Wärme muss über die Rohroberfläche und die Endkappen-Öffnungen) → **Board-/Lufttemperatur bei 40 °C Umgebung ≈ 68–80 °C**, bei 50 °C Umgebung ≈ 78–90 °C.
- Engpässe: W55RP20 Tc,max 85 °C; HR871150C 0…+70 °C; Modul-Derating 7 W ≤ 70 °C / 4,5 W @ 85 °C (bei 50 °C Umgebung liegt der USB-Fehlerfall 4,52 W an der Grenze → Thermoschutz, +5V-Einbruch möglich; Normalbetrieb ≤ 3,73 W hat ≈ 17 % Reserve). Bei ≤ 40 °C Umgebung bleiben 5–17 K Reserve zu 85 °C.
- Massnahmen (OD-11): Gehäuse ist ein **Kunststoffrohr** Innen-Ø 25 mm (User-Entscheidung 2026-10-23): Die Isolation zum Rohr ist damit unkritisch (kein leitfähiges Gehäuse, R-ISO-5 entschärft). Die Wärmeabfuhr ist schlechter als bei Aluminium → **max. Umgebungstemperatur 40 °C empfohlen**; Lüftungsschlitze in den Endkappen sinnvoll; **Temperaturen an U1, U5, U4, J1 am Muster messen**.
- Wärmepfad U1: nur über die SMD-Pads → Kupferflächen an Pad 1 (+VDC, `F_5VRAW`/`B_5VRAW`) und Pad 2 (−VDC = GND) auf beiden Aussenlagen mit Vias (DS Fig. 12); optional Wärmeleitgel > 1,5 W/m·K unter dem Modul (Fig. 13). VIN-Seite nicht thermisch an Sekundärkupfer/Rohr koppeln.
- Thermische Vias unter U5-EP und (seit 2026-10-23, 2. Review) **U4-EP: 3 Vias 0,45/0,3 + 2 GND-Vias südlich des Pads** (design_risks R-PI-13 behoben); U4-Temperatur am Muster trotzdem messen.

## 7. Spannungskette USB

- VBUS am Port = +5V_RAW − FB1 (≤ 0,04 V) − TPS2553 (85 mΩ typ. × 0,5 A ≈ 0,04 V) → **typ. 4,92 V**; mit R_DS(on) max. bei hoher Temperatur, FB1-DCR warm und Leiterbahn/Buchse **Worst Case ≈ 4,6 V @ 500 mA** (Review) (< 4,75 V USB-Spec bei Modul-Untergrenze 4,75 V).
- HID-Geräte arbeiten bis ≈ 4,4 V; formal eine Abweichung. Option: R9 (ADJ → GND) am Muster so wählen, dass +5V_RAW ≈ 5,10 V (Wert nicht im DS tabelliert, empirisch; von hochohmig her abgleichen). **Obergrenze +5V_RAW ≤ 5,25 V**; R9 = 0 Ω (5,65 V) ist unzulässig. D12 (min 5,8 V) würde zwar auch bei 5,65 V noch sperren.
- FW-Überlastschwelle an `VBUS_SENSE` deshalb ≈ 4,0–4,2 V (gemittelt, > 50 ms entprellt), nicht 4,5 V. Nach `USB_EN = 0` entlädt sich VBUS über R32/R33 mit τ ≈ 27 s.
- LDO-Headroom 1,70 V ✓; VBUS_SENSE 2,02 V bei 5,00 V (Faktor 0,405, Vollausschlag 3,3 V ≙ 8,15 V).

## 8. Strombelastung

| Bauteil | Auslegung | Rating |
|---|---|---|
| D1/D2 MB6S | 0,15 A (Fehlerfall) | 0,5 A ✓ |
| U1 Ag9905-LPB | 0,90 A | 1,4 A ✓ (Derating > 70 °C) |
| C11 Polymer | Modul-Ripple | 2,5 A rms ✓ |
| FB1 | 0,9 A | 3 A ✓ |
| U6 TPS2553 | 0,53–0,66 A (Limit) | ✓ |
| U4 LDO | 0,25 A | 1 A ✓ |
| FB2 | ≈ 0,15 A | 2 A ✓ |

---

## Änderungshistorie

- **Rev 1 (2026-10-21):** Flyback-Budget, Klasse 2 (≤ 6,49 W), R25 40,2 k, +5V 5,08 V.
- **Rev 2 (2026-10-21):** R25 44,2 k (USB-Fehlerfall 5,97 W am PD < 6,49 W), +5V 5,07 V (TLV431 68k/22k), RGB-LED an +5V, Flyback-η ≈ 82 %.
- **Rev 3 (2026-10-22):** unverändert (verworfene Layoutvariante).
- **Rev 4 (2026-10-22):** Ag9905LP-Modul: Class 0, 5,00 V ±5 %, Mindestlast 200 mA, Derating 4,5 W @ 85 °C; Wärme ≈ 2,0 W.
- **Rev 4b/4d (2026-10-22):** MagJack-LEDs entfallen, WS2812B an +3V3: I(+3V3) 180/247 mA, P_LDO 0,31/0,48 W.
- **Rev 4f/4g (2026-10-26):** D11 normale LED (3,5 mA), MagJack-LEDs 2 × ≈ 4 mA: I(+3V3) ≈ 175/222 mA, P_LDO ≈ 0,30/0,43 W – etwas entspannter als Rev 4e (Thermik-Rechnungen unten konservativ mit den Rev-4e-Werten belassen).
- **Rev 4e (2026-10-23):** Ag9905-LPB: Daten identisch, Wärmeabfuhr nur über Pads/Kupferflächen.
- **Rev 4e Review (2026-10-23):** Kunststoffrohr, Umgebung ≤ 40 °C (≈ 68–80 °C innen); VBUS Worst Case ≈ 4,6 V @ 500 mA; R9-Obergrenze 5,25 V; PSE 802.3af/at ≥ 48 V; U4-EP ohne Thermal-Vias.
- **2. Review (2026-10-23):** PoE → 5 V bestätigt; U4-EP-Vias ergänzt; FW-Schwelle VBUS 4,0–4,2 V, VBUS-Entladung τ ≈ 27 s. Budget sonst unverändert (C65/C66, Y1 ohne Einfluss).
