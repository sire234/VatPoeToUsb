# Design Review — poe_usb_hid_bridge Rev 4g (2026-10-26)

Umfang: SKiDL-Code (`circuits/poe_usb_hid_bridge/`), KiCad-Projekt `kicad/poe_usb_hid_bridge_rev4g/` (Schaltplan + Board),
Ausgaben `outputs/*rev4g*`, `sourcing/sourced_bom.md`, `SPEC.md`, `architecture/*.md`, `README.md`, `pipeline_state.json`.

## Summary

ERC: **PASS** | Architektur: OK (Doku veraltet) | Code: OK | Footprints: **PASS** | DRC: **PASS** | Fertigungsdaten: **1 Fehler behoben**

Severity: 1 HIGH (behoben), 3 MEDIUM, 5 LOW

| Prüfung | Ergebnis |
|---|---|
| SKiDL-ERC | 0 Fehler / 0 Warnungen (`outputs/poe_usb_hid_bridge_rev4g_erc.txt`) |
| KiCad-ERC (alle 7 Blätter) | 0 Verstösse |
| Netzliste KiCad ↔ SKiDL | identisch, 46 Netze (`tools/netcompare.py`) |
| Footprint-Validierung | 41/41 gefunden (KiCad-10-Bibliothek + Projekt-Bibliothek) |
| DRC mit Schaltplan-Parität | 0 Fehler, 0 unverbunden, 0 Parität, 18 Warnungen (Silkscreen, J1 `lib_footprint_mismatch` gewollt) |
| Refs/Werte/LCSC | Schaltplan = Netzliste = PCB = 85 Refs; JLC-BOM = CPL = 75 Positionen, alle CPL-Koordinaten/Seiten stimmen |
| MagJack-LED-Belegung | gegen HR871150C-Datenblatt (S. 1 Schaltbild, S. 3 PCB-Layout) und W55RP20-Pinliste geprüft: 11/13 Anode, 12/14 Kathode, U5.37 LINKLED, U5.39 ACTLED – korrekt |

## Findings

| # | Severity | Area | Issue | Suggested Fix / Status |
|---|----------|------|-------|---------------|
| 1 | HIGH | Fertigung | In `outputs/fab_rev4f_final/` und `outputs/fab_rev4g_final/` liegen die Gerber auf absoluten Koordinaten (Kontur X100…180), die Bohrdaten auf dem Board-Ursprung (X0…80) → Bohrungen 100 mm versetzt (gleicher Fehler wie R-LAY-8, Rev 4e). Ursache: Gerber-Export mit `--layers` ohne `--use-drill-file-origin`. | **Behoben:** Neu-Export in `outputs/fab_rev4g_release/` (`kicad-cli pcb export gerbers --use-drill-file-origin …`, Bohrdaten `--drill-origin plot`); geprüft: Kontur X0…80, Via 54,1/15,0 in Kupfer und Bohrdatei identisch. README/pipeline_state zeigen auf den neuen Ordner. Die zwei fehlerhaften Ordner nicht verwenden und löschen (Hook verhindert Löschen durch Claude). |
| 2 | MEDIUM | Isolation | Neue In3-Leitung ETH_LED_LINK_N läuft im J1-Pinfeld (114,05/109,2 → 119,3/108,4) bis **2,23 mm** an J1.7 (PSE_CT12) heran. DRC akzeptiert das nur über die J1-Ausnahme `ISO_EXC_J1` (≥ 1,0 mm). ETH_LED_ACT_N hält > 3 mm. | **Erledigt:** als **R-ISO-10** in `design_risks.md` aufgenommen; im Hipot-Test (1500 VAC) mitprüfen; liegt im Bereich der bereits akzeptierten J1-Abstände (J1.5↔J1.7 1,25 mm, ETH_RXN_J 1,83 mm). Alternative ohne Ausnahme: Link-LED wieder unbeschaltet lassen. |
| 3 | MEDIUM | Layout | Die beiden LED-Leitungen schneiden auf In3 zwei Kanäle in die +5V-Fläche bei U5 (x 145–163). Die Fläche bleibt zusammenhängend, der Weg Einspeisung (145,4/103) → U4 (148,5/111,6) wird aber länger und schmaler. | Unkritisch bei ≈ 250 mA für U4; bei Thermik-/Spannungsmessung am Muster +5V an U4 kontrollieren. |
| 4 | MEDIUM | Doku | SPEC.md und architecture/*.md beschreiben noch Rev 4e (WS2812B, C64, MagJack-LEDs NC, 84 Refs/42 Netze), z. B. SPEC.md:17/21/23/50/65/95, net_plan.md:3/28/49-50/75/77/105/120/222-233, block_diagram.md:46/77/99, skeleton_bom.md:10/103-110, design_risks.md:63/79/86, power_budget.md:28/105, mechanical_concept.md:17/88; pipeline_state.json enthält noch die Empfehlungen „WS2812 auf anderem PIO-Block" und „R4b-1 backen". | **Erledigt (2026-10-26):** SPEC.md und alle architecture/*.md auf Rev 4g nachgeführt; pipeline_state.json-Empfehlungen (PIO, Backen) ersetzt, R-ISO-10 und R-PI-14 (In3-+5V-Fläche) ergänzt. |
| 5 | LOW | Code | Veraltete Kommentare: `mcu_w55rp20.py:3-5` (RGB/LED_DIN-Datenleitung, LINKLED/ACTLED NC), `ethernet_magjack.py:126` („Rev 4f" statt 4g). | **Erledigt:** Kommentare/Docstrings auf Rev 4g korrigiert (nur Kommentare, Netzliste unverändert). |
| 6 | LOW | Code/Netze | Netznamen `LED_DIN`/`LED_DIN_R` stammen aus dem WS2812-Design (bewusst beibehalten, damit das Layout unverändert bleibt). | Optional beim nächsten grösseren Layout-Schritt in `LED_STAT`/`LED_STAT_A` umbenennen. |
| 7 | LOW | Konvention | Abblock-Kondensatoren heissen C40…C62 statt `C_DECOUP_*` (Plugin-Konvention). | Bewusst so belassen (Referenzen sind in Layout, BOM und CPL etabliert). |
| 8 | LOW | Silkscreen | D11-Silk berührt das J2-Silk-Polygon (164,0/114,4); J3-Beschriftung liegt teilweise auf Pads (≈ 163,2/114,35); einige Pin-1-Punkte liegen bis ≈ 2 mm vom Pin entfernt (U1, D3, C18), weil näher kein freier Platz ist. | Kosmetisch, JLC schneidet Silk an Pads ab. |
| 9 | LOW | BOM | Doppelte BOM-Zeilen mit gleichem LCSC (C12/C13 C45783; C19 getrennt von C16/C46/C60 C19702). | Harmlos; optional zusammenfassen. |

## Bestätigt ohne Befund

- LED-Ströme: MagJack ≈ 4 mA (330 Ω, Vf ≈ 2 V), D11 ≈ 3,5 mA – im +3V3-Budget vernachlässigbar.
- J1-Footprint: LED-Pads (±4,085 / ±6,625, 4,08 mm vor den Montagelöchern) stimmen mit dem Datenblatt-Layout S. 3 überein (vorher als „unverifiziert" markiert).
- R5/R6 auf der Unterseite (Oberseite liegt unter dem RJ45-Gehäuse), CPL-Rotation 180° wie die übrigen Bottom-Teile im JLC-Viewer prüfen (R-LAY-9).
- Gerber-ZIP (`fab_rev4g_release`): 18 Dateien wie Rev 4e (6 Kupferlagen, Maske, Paste, Silk, Kontur, PTH/NPTH + Karten, Job-Datei).

## Fazit

Schaltung, Schaltplan und Board Rev 4g sind elektrisch konsistent und DRC-sauber. Für die Bestellung **ausschliesslich `outputs/fab_rev4g_release/`** verwenden. Vor der Bestellung: Befund 2 (R-ISO-10) bewusst freigeben oder die Link-LED weglassen. Befunde 1, 4 und 5 sind behoben.
