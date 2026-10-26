# USBLC6-2SC6 — ST Very-low-capacitance ESD protection (USB 2.0), SOT-23-6L

Quelle: ST USBLC6-2 Datenblatt, `USBLC6-2SC6.pdf` (Text gelesen).

| Spec | Value |
|------|-------|
| Package | SOT-23-6L, Hoehe ca. 1.45 mm max |
| Schutz | 2 Datenleitungen + VBUS, USB 2.0 bis 480 Mbit/s |
| V_BR | min 6 V @ 1 mA (zwischen VBUS und GND) |
| V_CL | 17 V @ 1 A (8/20 us, I/O->GND), hoeher bei 5 A |
| Kapazitaet I/O-GND | 2.5 pF typ (3.5 max) @ 1.65 V |
| I_R | max 150 nA (Datenblatt-Kopf) |
| ESD | IEC 61000-4-2 +-15 kV Luft / +-8 kV Kontakt |

## Pinout (Fig. 1, SOT23-6L Top View)
| Pin | Name |
|-----|------|
| 1 | I/O1 |
| 2 | GND |
| 3 | I/O2 |
| 4 | I/O2 |
| 5 | VBUS |
| 6 | I/O1 |
Durchschleif-Pads: 1<->6 (Leitung 1), 3<->4 (Leitung 2) -> Layout: D+ ueber Pads 1/6, D- ueber 3/4 (wie net_plan).

## Notes
- GND-Pin 2 kurz und mit Via an GND; VBUS-Pin 5 direkt an VBUS_USB. Datenblatt Abschnitt "How to ensure good ESD protection" beachten.
