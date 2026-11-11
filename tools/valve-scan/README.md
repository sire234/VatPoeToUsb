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
```

mDNS braucht UDP-Port 5353 (wird mit dem Windows-mDNS-Dienst geteilt). Blockiert die Windows-Firewall
eingehende Multicast-Antworten, beim ersten Start „Zugriff zulassen“ wählen oder die IP direkt angeben.

## Bauen

```
dotnet publish -c Release -o publish
```

Ergebnis: `publish/valve-scan.exe` (win-x64, self-contained, getrimmt, ≈ 11 MB).
