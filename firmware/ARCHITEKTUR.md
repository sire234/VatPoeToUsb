# Firmware-Architektur – PoE-USB-HID-Bridge

Diese Übersicht erklärt, wie die Software auf der Bridge aufgebaut ist und wie die Daten durch das Gerät fliessen.
Sie richtet sich an Leserinnen und Leser ohne tiefe Embedded-Kenntnisse.

## Was macht die Bridge?

Die Bridge verbindet USB-Geräte mit dem Netzwerk. Sie wird über das Netzwerkkabel mit Strom versorgt (PoE).

- **Tastaturen und Barcode-Scanner:** Was getippt oder gescannt wird, schickt die Bridge als Text ins Netzwerk.
- **VAT-Ventile:** Ein PC im Netzwerk kann Werte der Ventile lesen (z. B. Position, Firmware-Version, Fehler).
  Schreibende Befehle sind gesperrt.
- **Auffindbar im Netz:** Die Bridge meldet sich unter einem eigenen Namen (`poe-hid-xxxxxx.local`), so dass sie
  ohne Kenntnis der IP-Adresse gefunden wird.

```mermaid
flowchart LR
    subgraph USB-Seite
        T[Tastatur / Scanner]
        V[VAT-Ventile]
        H[USB-Hub]
    end
    subgraph Bridge
        B[PoE-USB-HID-Bridge]
    end
    subgraph Netzwerk
        PC[PC / Leitsystem]
        S[Switch mit PoE]
    end
    T --> H
    V --> H
    H -- USB --> B
    B -- Ethernet --> S
    S -- Strom über PoE --> B
    S --- PC
```

## Die Bausteine

Die Software besteht aus wenigen, klar getrennten Teilen. Jeder Teil hat genau eine Aufgabe.

```mermaid
flowchart TB
    subgraph USB["USB-Seite"]
        USBHOST[USB-Steuerung<br/>erkennt angesteckte Geräte]
        HID[Eingabegeräte<br/>Tastatur, Maus, Scanner]
        VALVE[Ventil-Kommunikation<br/>Befehle senden, Antworten zusammensetzen]
        PORT[USB-Stromversorgung<br/>ein/aus, Überlastschutz]
    end
    subgraph NET["Netzwerk-Seite"]
        TCP[Befehls-Schnittstelle<br/>Port 5000]
        DHCP[IP-Adresse beziehen]
        MDNS[Namensdienst<br/>poe-hid-xxxxxx.local]
    end
    subgraph SYS["Allgemein"]
        MAIN[Hauptablauf]
        LOG[Diagnose-Protokoll]
        LED[Status-LED]
        WD[Wächter<br/>Neustart bei Hänger]
    end

    USBHOST --> HID
    USBHOST --> VALVE
    HID --> TCP
    VALVE <--> TCP
    PORT --> USBHOST
    MAIN --> USB
    MAIN --> NET
    MAIN --> LED
    LOG --> TCP
    WD -. überwacht .-> MAIN
```

| Baustein | Aufgabe in einem Satz |
|---|---|
| Hauptablauf | Ruft alle anderen Bausteine reihum immer wieder auf, viele tausend Mal pro Sekunde. |
| USB-Steuerung | Erkennt, was am USB-Anschluss steckt (auch hinter einem Hub), und meldet es den zuständigen Bausteinen. |
| Eingabegeräte | Übersetzt Tastendrücke in Text und Mausbewegungen in kurze Meldungen. |
| Ventil-Kommunikation | Verpackt Lesebefehle für die Ventile, wartet auf die Antwort und setzt lange Antworten wieder zusammen. Blockiert schreibende Befehle. |
| USB-Stromversorgung | Schaltet den Strom am USB-Anschluss und schaltet ihn bei Überlast (Kurzschluss, zu grosser Verbraucher) ab. |
| Befehls-Schnittstelle | Nimmt Befehle eines PCs entgegen und schickt Antworten und Eingaben zurück. |
| IP-Adresse beziehen | Holt sich automatisch eine Adresse im Netz; klappt das nicht, gilt eine feste Ersatzadresse. |
| Namensdienst | Antwortet, wenn ein PC nach `poe-hid-xxxxxx.local` oder nach Bridges allgemein fragt. |
| Diagnose-Protokoll | Merkt sich die letzten Ereignisse, damit man bei Problemen nachsehen kann, was passiert ist. |
| Status-LED | Zeigt den Zustand an (Start, kein Netz, Adresssuche, bereit, USB-Überlast). |
| Wächter | Startet die Bridge automatisch neu, falls die Software einmal hängen sollte. |

## Der Hauptablauf

Die Bridge hat kein Betriebssystem. Ein einziger Ablauf erledigt alle Aufgaben nacheinander in einer endlosen Runde.
Jede Aufgabe ist kurz und wartet nie lange, dadurch reagiert die Bridge trotzdem sofort.

```mermaid
flowchart LR
    A[Wächter beruhigen] --> B[USB-Geräte bedienen]
    B --> C[USB-Strom überwachen]
    C --> D[Ventil-Anfragen auf Zeitüberschreitung prüfen]
    D --> E[Netzwerk bedienen<br/>Befehle, Antworten, Namensdienst]
    E --> F[Status-LED aktualisieren]
    F --> A
```

## Ablauf beim Einschalten

```mermaid
sequenceDiagram
    participant B as Bridge
    participant U as USB-Geräte
    participant N as Netzwerk
    B->>B: Start, Diagnose-Protokoll und LED an
    B->>U: USB-Steuerung starten, dann USB-Strom einschalten
    U-->>B: Geräte melden sich (Hub, Tastatur, Ventile)
    B->>N: Netzwerkkabel prüfen (Link)
    B->>N: IP-Adresse anfragen
    N-->>B: Adresse erhalten (oder Ersatzadresse nach 15 s)
    B->>N: "Ich bin poe-hid-xxxxxx" bekanntgeben
    Note over B: bereit – LED leuchtet
```

## Beispiel 1: Ein Barcode wird gescannt

```mermaid
sequenceDiagram
    participant S as Scanner
    participant B as Bridge
    participant P as PC
    S->>B: Tastendrücke über USB
    B->>B: in Text übersetzen
    B->>P: "4006381333931" + Zeilenende
    Note over B: LED flackert kurz
```

Ist gerade kein PC verbunden, wird der Text verworfen.

## Beispiel 2: Ein PC liest einen Wert aus einem Ventil

```mermaid
sequenceDiagram
    participant P as PC
    participant B as Bridge
    participant V as Ventil
    P->>B: "Lies die Firmware-Version von Ventil 1"
    B->>B: erlaubter Lesebefehl? ja
    B->>V: Befehl über USB
    V-->>B: Antwort (bei langen Antworten in vielen Stücken)
    B->>B: Stücke zusammensetzen
    B-->>P: "Ventil 1: TEST-F01…"
```

Regeln dabei:

- **Nur lesen:** Befehle, die etwas am Ventil verändern würden, lehnt die Bridge ab, bevor sie das Ventil erreichen.
- **Eins nach dem anderen:** Es läuft immer nur eine Ventil-Anfrage gleichzeitig. Eine zweite muss warten.
- **Zeitlimit:** Antwortet das Ventil nicht innerhalb einer Sekunde, meldet die Bridge eine Zeitüberschreitung.

## Wie findet ein PC die Bridge?

```mermaid
sequenceDiagram
    participant P as PC (z. B. valve-scan)
    participant B as Bridge
    P->>B: Rundruf "Gibt es hier Bridges?"
    B-->>P: "Ja: poe-hid-380019, Adresse 192.168.22.103, Port 5000"
    Note over P: Im WLAN geht die erste Antwort manchmal verloren,<br/>deshalb fragt der PC mehrmals.
    P->>B: Verbindung aufbauen
    B-->>P: Statuszeile
```

## Zustände und Status-LED

```mermaid
stateDiagram-v2
    [*] --> Start
    Start --> KeinNetz: Software läuft
    KeinNetz --> Adresssuche: Netzwerkkabel erkannt
    Adresssuche --> Bereit: IP-Adresse erhalten
    Bereit --> KeinNetz: Kabel abgezogen
    Bereit --> USBUeberlast: zu viel Strom am USB
    USBUeberlast --> Bereit: Neuversuch erfolgreich

    Start: Start – LED an
    KeinNetz: Kein Netz – kurzer Blitz pro Sekunde
    Adresssuche: Adresssuche – blinkt schnell
    Bereit: Bereit – LED an, flackert bei Eingaben
    USBUeberlast: USB-Überlast – 3 Blitze, Pause
```

## Schutzmechanismen

| Was kann passieren? | Was macht die Bridge? |
|---|---|
| Software hängt | Der Wächter startet die Bridge nach 3 Sekunden neu. |
| USB-Gerät zieht zu viel Strom oder hat einen Kurzschluss | Strom am USB-Anschluss wird abgeschaltet und später erneut versucht (erst nach 1 s, dann immer länger bis 32 s). |
| Ventil antwortet nicht | Nach 1 Sekunde Meldung „Zeitüberschreitung“, die Bridge arbeitet normal weiter. |
| Jemand schickt einen schreibenden Ventilbefehl | Wird abgelehnt und erreicht das Ventil nie. |
| Gerät mit virtuellem CD-Laufwerk (wie die Ventile) | Das Laufwerk wird ignoriert, nur die Datenschnittstelle des Ventils wird genutzt. |
| PC liest zu langsam oder ist nicht verbunden | Daten werden verworfen, die Bridge läuft weiter. |

## Diagnose

Bei Problemen gibt es zwei Wege, ins Innere zu schauen:

```mermaid
flowchart LR
    E[Ereignisse in der Bridge<br/>z. B. Gerät erkannt, Anfrage beantwortet] --> R[Programmier-Adapter<br/>am Stecker J3]
    E --> P[Diagnose-Protokoll<br/>letzte Ereignisse im Speicher]
    P --> T[Abruf über das Netzwerk<br/>z. B. valve-scan --verbose]
    R --> D[Entwickler-PC]
```

- **Über das Netzwerk:** Ohne Zusatzgerät, z. B. mit `valve-scan --verbose`. Zeigt die letzten Ereignisse seit dem Start
  und live alles, was während des Laufs passiert.
- **Über den Programmier-Adapter:** Für Entwickler, mit einem Raspberry Pi Pico als Adapter am Stecker J3. Damit wird
  auch neue Software aufgespielt.

## Grenzen

- Nur **ein** PC kann gleichzeitig mit der Bridge verbunden sein.
- Höchstens **2 Hubs** und **8 USB-Geräte**.
- Tastatur-Übersetzung nur für **US-Tastaturlayout** (Scanner entsprechend einstellen).
- Keine Anmeldung oder Verschlüsselung: Jeder im Netz kann sich verbinden. Die Ventile sind durch die Lese-Sperre geschützt.
- USB-Sticks werden nicht unterstützt.
