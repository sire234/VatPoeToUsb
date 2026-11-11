# Valve text commands for tests

This list shows text commands that can be sent to the valve. It also shows the reply that a test can expect. The list is not complete.

## Sources

- The protocol comes from `docs/analysis/legacy-analysis.md`, section 9.1.
- The data types and values come from the simulator set D: `src/Vat.Cpa.Simulator/Sets/D-connected-valve-2026-10-30.set.txt`. Set D is a copy of the development valve from 2026-10-30.
- The replies were computed from set D. They were not recorded on the valve. Live values such as the position can be different today.

## Format

- Request: `p:` + service with 2 hex digits + parameter ID with 8 hex digits + index with 2 hex digits. A write also adds the value.
- Reply: `p:` + error code with 2 hex digits + service + parameter ID + index + value. Error code `00` means OK.
- Numbers come back as hex. The application sets the hex format on every connect. This step is called W1.

## Value encoding

| Type | Format | Example |
|---|---|---|
| SInt8, UInt8 | 2 hex digits | `02` |
| UInt16 | 4 hex digits | `0000` |
| UInt32 | 8 hex digits | `0F100201` |
| Float32 | 8 hex digits, IEEE 754, most significant byte first | 69.0 is `428A0000`. 1.0 is `3F800000`. |
| String | ASCII text | `TEST-F01.STD.vXXX.xx-8d81aeb-dirty` |

## Read single values with `p:0B`

| Request | Parameter | Type | Expected reply | Meaning |
|---|---|---|---|---|
| `p:0B0F10010000` | Serial Number | String | `p:000B0F10010000<serial number>` | The serial number of the valve. |
| `p:0B0F10030200` | Device Firmware Version | String | `p:000B0F10030200TEST-F01.STD.vXXX.xx-8d81aeb-dirty` | The firmware text. |
| `p:0B0F10020100` | Device Series | UInt16 | `p:000B0F100201000001` | `1` is Simulation. |
| `p:0B0F02000000` | Control Mode | SInt8 | `p:000B0F0200000002` | `2` is Position. Other values: 0 Init, 3 Close, 4 Open, 6 Hold, 14 Error. |
| `p:0B0F0B000000` | Access Mode | SInt8 | `p:000B0F0B00000000` | `0` is Local. 1 is Remote. 2 is Remote Locked. |
| `p:0B0F30060000` | Error Number | UInt16 | `p:000B0F300600000000` | `0000` means no error. |
| `p:0B0F30070000` | Error Code | UInt16 | `p:000B0F300700000000` | `0000` means no error. |
| `p:0B0F30010000` | Warning Bitmap | UInt32 | `p:000B0F3001000000000000` | Each bit is one warning. Bit 0 is No Learn Data. |
| `p:0B1101000000` | Actual Position Axis 1 | Float32 | `p:000B1101000000428A0000` | 69.0 |
| `p:0B1102000000` | Target Position | Float32 | `p:000B1102000000428A0000` | 69.0. The range is 0 to 100. |
| `p:0B1103000000` | Position Control Speed | Float32 | `p:000B11030000003F800000` | 1.0 |
| `p:0B2006010000` | Cluster Actual Pressure | Float32 | `p:000B200601000000000000` | 0.0 |
| `p:0B0602010100` | Stringformat Integer | UInt8 | `p:000B060201010003` | `3` is hex with a fixed length. |
| `p:0B0611010000` | Response Code String 00 | String | `p:000B061101000000 No error` | The error text for code 00. |
| `p:0B06110A0000` | Response Code String 6E | String | `p:000B06110A00006E Wrong parameter ID` | The error text for code 6E. |
| `p:0B1E01010200` | Valve Status Member-IDs, element 0 | UInt32 array with 16 elements | `p:000B1E010102000F100201` | The first member is Device Series. |

## Compound reads with `p:29`

| Request | Expected reply | Content |
|---|---|---|
| `p:291E01010200` | `p:00291E01010200` + `0001;00;02;0000;0000;00000000;TEST-F01.STD.vXXX.xx-8d81aeb-dirty` | Valve Status: Device Series, Access Mode, Control Mode, Error Number, Error Code, Warning Bitmap, Firmware. |
| `p:291E01060200` | `p:00291E01060200` + `428A0000;428A0000;428A0000;428A0000;3F800000` | Chart: Actual Position, Target Position, both again, Position Control Speed. |

The reply only holds members that are assigned. An empty slot with the value `0` is left out.

## Tree commands with `g:`

These replies come in several parts. The first request ends with `START`, for example `g:1E18START`. Every further request is only `g:1E18`. The last part ends with RS `EnD` RS. RS is the byte `0x1E`.

| Command | Reply |
|---|---|
| `g:1E18` | The full parameter tree with IDs and names. Example: `0x0701;Pressure Control;Actual Pressure;…` |
| `g:1E17` | The state of each parameter. 0 is not visible. 1 is greyed. 2 is main window only. 3 is visible. 4 is protected. |
| `g:1E19` | The minimum and the maximum of each parameter. |
| `g:1E20<ID>` | The current values of the children of a tree item. Example: `g:1E2011000000`. |
| `g:1E21<ID>` | 9 attributes for each child: data type, access rights, options, number of elements, non-volatile, min, max, default, enum texts. |

## Negative tests

| Request | Expected reply | Reason |
|---|---|---|
| `p:0B0701000000` | `p:6E0B0701000000` | The development valve has no parameter `0x07010000`. |
| `p:0B1111111100` | `p:6E0B1111111100` | The ID does not exist. |

Error code `6E` means wrong parameter ID. Error code `1E` means the value is out of range.

## Commands that must not be sent

The read-only rule and the allow-list block these commands. A negative test can check that they are blocked.

- `p:01` SetValue, `p:08` SetWithoutScale and `p:2B` SetVolatile.
- `p:05`. Its meaning is unknown, so it counts as a write.
- `g:0f50`. It reads or writes memory and switches the simulation mode.
- Any other `g:` command.

The only allowed writes are the W1 writes on connect: `p:01060201010003` and `p:01060201020002`.

## Other simulator sets

Some types are different in the simulator sets A and B:

- Actual Position `0x11010000` is UInt32, not Float32.
- Target Pressure `0x07020000` is UInt32.
- The parameters `0x07010000` and `0x07020000` exist in A and B. So the first negative test only works with the development valve and set D.
