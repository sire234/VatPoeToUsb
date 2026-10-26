# T520B157M006ATE035 — KEMET T520 KO-CAP Polymer-Tantal 150 uF / 6.3 V, Case B (3528-21), ESR 35 mOhm

Quelle: KEMET T520-Serie Datenblatt, `T520B157M006ATE035.pdf`.

| Spec | Value |
|------|-------|
| Kapazitaet / Nennspannung | 150 uF +-20 % / 6.3 V |
| ESR | 35 mOhm max @ 100 kHz |
| Case B (3528-21) | L 3.5 +-0.2, W 2.8 +-0.2, **H 1.9 +-0.2 mm (max 2.1)** |
| Temperatur | -55..+105 C (T520) |
| Ripple | siehe Part-Number-Tabelle im Datenblatt (Zahl hier nicht verifiziert) |

## Pinout
Polarisiert: Anode (+) = Seite mit Balken/Markierung; Fuss +5V (VBUS_USB), Kathode an GND. KiCad `CP_EIA-3528-21_Kemet-B`.

## Notes
- 6.3 V Nennspannung bei 5.0-5.2 V (VBUS): Derating 81 %; Hersteller empfiehlt <= 80 % -> knapp ueber, bei 5.0 V = 79 % ok. Polymer: kein Kurzschlussrisiko wie MnO2.
- Hoehe 2.1 max.
