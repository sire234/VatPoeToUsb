# TLV75733PDRVR — TI 1 A Low-I_Q LDO, 3.3 V fix, WSON-6 2x2 (DRV)

Quelle: TI TLV757P Datenblatt, `TLV75733PDRVR.pdf`; Pin-Tabelle (Table 4-1) visuell gelesen. VERIFIZIERT (Pinout).

| Spec | Value |
|------|-------|
| Package | WSON-6 (DRV) 2 x 2 mm, Thermal Pad (intern GND), Hoehe ca. 0.8 mm |
| V_IN | 1.45-5.5 V; abs. max -0.3..6.0 V |
| V_OUT | 3.3 V fix, I_OUT max 1 A |
| I_Q | 25 uA typ |
| C_IN / C_OUT | >= 1 uF (effektiv > 0.47 uF nach Derating; 50 % angenommen) |
| Tj | -40..125 C |
| Besonderheit | aktiver Output-Discharge bei Disable (P-Version), Foldback-Strombegrenzung |
Hinweis: Orderable-Tabelle im Text-Extrakt war spaltenverschoben (Zeile "TLV75733PDRVR ... SOT-23 (DBV)"); Teil mit Suffix DRV = WSON-6.

## Pinout (DRV, WSON-6)
| Pin | Name | Function |
|-----|------|----------|
| 1 | OUT | Ausgang 3.3 V |
| 2 | NC | keine interne Verbindung |
| 3 | GND | Masse |
| 4 | EN | Enable (high = an) |
| 5 | NC | keine interne Verbindung |
| 6 | IN | Eingang |
| EP | Thermal Pad | intern GND, an grosse Massefläche |

## Notes
- IN und EN verbinden (net_plan: U4 IN/EN an +5V). Layout: Datenblatt Fig. 7-8 (DRV).
- Land Pattern: KiCad Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm (BOM) - EP 1.0 x 1.6 mm gegen DS-Zeichnung pruefen.
