# Beispiel-Firmware – PoE-USB-HID-Bridge (Rev 4g, W55RP20)

Beispiel und Ausgangspunkt für die eigentliche Firmware. Pico-SDK + **TinyUSB-Host** + **WIZnet ioLibrary**, ohne RTOS, alles im Hauptloop auf Core 0.
**Noch nicht auf der Hardware getestet:** Sie ist gegen die Pinbelegung aus `architecture/net_plan.md` geschrieben und kompiliert fehlerfrei.

## Funktion

| Teil | Verhalten |
|---|---|
| USB-Host (J2) | Hub (1 Stück, bis 3 Geräte dahinter), Tastatur/Barcode-Scanner, Maus, beliebige HID-Geräte, USB-Stick |
| Tastatur / Scanner | Boot-Protokoll, Tastencodes → ASCII (**US-Layout**, Scanner auf „USB-Tastatur US“ stellen); Enter → `\r\n` |
| Maus / andere HID | Zeilen `#MOUSE b=… x=… y=… w=…` bzw. `#HID <addr>.<itf>: <hex>` |
| USB-Stick | FAT16/FAT32 (kein exFAT/NTFS). Alles, was an den TCP-Client geht, wird an `HIDLOG.TXT` angehängt (zeilenweise, mit `f_sync`) |
| Ethernet | DHCP (15 s), sonst fest **192.168.1.200/24**. **TCP-Server Port 5000**: liefert die HID-Daten, nimmt Befehle `status`, `usb on`, `usb off` an |
| mDNS / DNS-SD | Name **`poe-hid-xxxxxx.local`** (xxxxxx = letzte 3 MAC-Bytes, steht im RTT-Log und in `#STATUS`); Dienst `_poehid._tcp` „PoE-HID-Bridge xxxxxx“ auf Port 5000, TXT `txtvers=1`, `data=hid-ascii`. Ankündigung beim Start und bei IP-Wechsel |
| USB-Port-Schutz | `USB_EN` (GPIO26) erst nach dem Start des Host-Stacks an. `VBUS_SENSE` (ADC3, Faktor 0,405) mit 1 kHz, gefiltert; < 4,1 V für 50 ms → Port aus, Neuversuch nach 1 → 2 → … → 32 s |
| LED D11 (GPIO28) | an = Start · kurzer Blitz/s = kein Link · 4 Hz = DHCP · an (flackert bei HID-Daten) = bereit · 3 Blitze + Pause = USB-Überlast |
| Debug | `printf` → **SEGGER RTT** über SWD (kein UART auf dem Board) |
| Watchdog | 3 s, pausiert während der Debugger den Kern anhält |

Ausgabe am TCP-Client (Beispiel):
```
#STATUS up=42s ip=192.168.1.57 net=ready usb=on vbus=4.93V stick=logging
#HID connected 2.0 0c2e:0b61 keyboard
4006381333931
```

## Dateien

| Datei | Inhalt |
|---|---|
| `CMakeLists.txt` | Build; holt die ioLibrary (Tag v3.2.0) per FetchContent, FatFs kommt aus TinyUSB |
| `boards/poe_usb_hid_bridge.h` | Board-Definition: Pins, 2 MB Flash, boot2 W25Q080 (wie W55RP20-EVB) |
| `src/main.c` | Hauptloop, Status, Verteilung der HID-Daten |
| `src/hid_app.c` | HID-Host-Callbacks, Tastatur → ASCII |
| `src/msc_app.c` | USB-Stick: FatFs-Anbindung, `HIDLOG.TXT` |
| `src/usb_port.c` | `USB_EN`, VBUS-Messung, Überlastabschaltung |
| `src/net.c` | Link, DHCP, TCP-Server, Befehle |
| `src/mdns.c` | mDNS-Responder mit DNS-SD (Multicast-Socket 224.0.0.251:5353) |
| `src/w5500_pio_spi.c` | W5500-SPI über PIO (GPIO20–23 passen auf keinen Hardware-SPI), 15,6 MHz |
| `src/led.c` | Blinkmuster D11 |
| `src/tusb_config.h` | TinyUSB: Host, Full Speed, Hub + HID + MSC |

## Bauen

Benötigt: Pico-SDK **2.3.1** (mit Submodul `lib/tinyusb`), arm-none-eabi-gcc, CMake ≥ 3.13, Ninja. Hier vorhanden über STM32CubeCLT; das SDK liegt unter `C:\Users\simon\tools\pico-sdk-2.3.1`.

```sh
export PATH="/c/ST/STM32CubeCLT_1.21.0/GNU-tools-for-STM32/bin:/c/ST/STM32CubeCLT_1.21.0/CMake/bin:/c/ST/STM32CubeCLT_1.21.0/Ninja/bin:$PATH"
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DPICO_SDK_PATH=C:/Users/simon/tools/pico-sdk-2.3.1
cmake --build build
```
Ohne Internet: ioLibrary lokal angeben mit `-DIOLIBRARY_PATH=C:/Users/simon/tools/ioLibrary_Driver-3.2.0`.
Ergebnis: `build/poe_usb_hid_bridge.elf` (≈ 80 KB Flash, 15,5 KB RAM) und `.bin`. Kein UF2, da es keinen BOOTSEL-Weg gibt.

## Flashen und Debug-Ausgabe (J-Link)

Verdrahtung J-Link → J3: Pin 9 SWCLK → 1, Pin 4 GND → 2, Pin 7 SWDIO → 3, Pin 1 VTref → 4. Board über PoE versorgen.

```sh
JLink.exe -device RP2040_M0_0 -if SWD -speed 4000 -autoconnect 1 -CommanderScript flash.jlink
```
mit `flash.jlink`:
```
loadfile build/poe_usb_hid_bridge.elf
r
g
exit
```
Debug-Ausgabe: **J-Link RTT Viewer** (Device `RP2040_M0_0`, SWD, Auto-Detection des RTT-Blocks) oder über den MCP-Server `jlink-mcp` (`flash`, `rtt_connect`, `rtt_read`).
Mit einem Pico als Debugprobe: `probe-rs run --chip RP2040 build/poe_usb_hid_bridge.elf` (flasht und zeigt RTT).

## Testen

1. Board an PoE, LED blinkt 4 Hz bis DHCP fertig ist; IP steht im RTT-Log (`NET: DHCP …`).
2. `nc <ip> 5000` bzw. `nc poe-hid-xxxxxx.local 5000` (oder PuTTY, Verbindungsart „Raw“) – es kommt eine `#STATUS`-Zeile.
   mDNS prüfen: `ping poe-hid-xxxxxx.local`; Windows `Resolve-DnsName poe-hid-xxxxxx.local`; Dienst suchen mit `dns-sd -B _poehid._tcp` (macOS/Bonjour) oder `avahi-browse -r _poehid._tcp` (Linux).
3. Tastatur oder Scanner an J2 (oder über einen Hub zusammen mit einem Stick) – getippte Zeichen erscheinen im TCP-Client und in `HIDLOG.TXT`.
4. Befehle im Client: `status`, `usb off`, `usb on`.

## Bekannte Grenzen / nächste Schritte

- Low-Speed-Tastaturen **hinter einem Hub** brauchen PRE-Pakete; TinyUSB unterstützt das auf dem RP2040, mit den konkreten Geräten testen.
- Tastatur-Layout fest US; für QWERTZ eine eigene Tabelle statt `HID_KEYCODE_TO_ASCII`.
- mDNS vereinfacht: kein Probing/Konfliktauflösung (Name enthält die MAC), kein IPv6, keine „Legacy Unicast“-Anfragen von Port ≠ 5353 (z. B. `nslookup -port=5353`); ping, Browser, Bonjour und Avahi funktionieren. Der DHCP-Hostname bleibt der ioLibrary-Standard `WIZnet…`.
- Nur ein TCP-Client gleichzeitig; Daten werden verworfen, wenn kein Client verbunden ist oder er zu langsam liest.
- Die feste Ersatz-IP und der Port stehen im Code (`net.c`); eine Konfiguration z. B. aus `CONFIG.TXT` auf dem Stick wäre der nächste Schritt.
- Ein abgezogener Stick während eines Schreibvorgangs kann die letzte Zeile verlieren; FAT bleibt durch `f_sync` meist konsistent.
- Nach `usb off` liegt VBUS wegen des Teilers noch ≈ 27 s (τ) an (design_risks R-USB-4).
