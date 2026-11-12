# valve-scan

Kleines Kommandozeilen-Tool (.NET 10, eine einzige EXE, keine .NET-Installation nötig):

1. sucht PoE-USB-HID-Bridges per **mDNS** (`_poehid._tcp.local`, 3 s),
2. listet pro Bridge die angeschlossenen **VAT-Ventile** (`valves`),
3. setzt pro Ventil das Zahlenformat auf hex (W1, wie die Legacy-CPA beim Verbinden) und liest einige Parameter
   (Seriennummer, Firmware, Serie, Control/Access Mode, Fehler, Warnungen, Position, Druck).

Es werden nur Lesebefehle gesendet (plus W1); die Bridge-Firmware blockiert alles andere ohnehin.
Befehle und Datentypen: `firmware/src/valve-commands.md`.

## Aufruf

```
valve-scan                  Bridges per mDNS suchen
valve-scan 192.168.1.200    mDNS überspringen, diese Bridge verwenden
valve-scan --verbose        Debug-Ausgabe (Kurzform -v), siehe unten
valve-scan --no-wait        am Ende nicht auf Enter warten (für Skripte)
valve-scan --endurance      Dauertest (alias --dauertest), siehe unten
valve-scan --endurance --duration 3600 192.168.1.200
```

## Dauertest (`--endurance`)

Liest auf allen Ventilen der (ersten) Bridge ohne Pause reihum alle Parameter, alle 50 Runden zusätzlich
den kompletten Parameterbaum (`g:1E18`, ≈ 98 KB in 56 Teilen ≈ 1 800 USB-Reports pro Ventil).
Unveränderliche Werte (Seriennummer, Firmware, Serie, Baum-Länge + SHA-256) werden mit dem ersten Wert
verglichen; eine Abweichung zählt als `MISMATCH`. Alle 5 s eine Statuszeile (Anfragen, Rate, Fehler,
Antwortzeit avg / p99 / max am PC gemessen), am Ende eine Zusammenfassung und `PASSED` / `FAILED`
(Exit-Code 0 / 2). Fehler werden nach Art gezählt: `bridge: timeout` (Ventil antwortet nicht in 1 s),
`bridge: busy`, `PC timeout` (keine Antwortzeile der Bridge in 3 s) usw.
Abbruch mit Enter oder Ctrl+C, oder nach `--duration <s>`. Nur Lesebefehle (plus W1 einmal am Anfang).
Mit `--verbose` läuft die Firmware-Debug-Ausgabe mit (sehr viel Text).

Am Ende wartet das Tool auf Enter (damit das Fenster beim Doppelklick offen bleibt), außer mit
`--no-wait` oder bei umgeleiteter Eingabe.

## Debug-Ausgabe (`--verbose`)

Graue Zeilen mit Zeit seit Programmstart:

- `mDNS:` verwendete Schnittstellen, jede Anfrage (wird nach 0 / 0,5 / 1 / 2 s wiederholt, weil Multicast
  im WLAN verloren gehen kann) und jede empfangene PTR/SRV/A-Antwort mit Absender,
- `TCP >>` / `TCP <<` jede gesendete und empfangene Zeile,
- `FW-LOG` (gelb): Debug-Verlauf der Bridge seit ihrem Start (`log`), `FW` (türkis): Live-Ausgabe der
  Firmware während des Laufs (`debug on`), jeweils mit der Uptime der Bridge.

mDNS braucht UDP-Port 5353 (wird mit dem Windows-mDNS-Dienst geteilt). Blockiert die Windows-Firewall
eingehende Multicast-Antworten, beim ersten Start „Zugriff zulassen“ wählen oder die IP direkt angeben.

## Bauen

```
dotnet publish -c Release -o publish
```

Ergebnis: `publish/valve-scan.exe` (win-x64, self-contained, getrimmt, ≈ 11 MB).
