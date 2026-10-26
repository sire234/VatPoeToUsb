#!/bin/sh
# Check a regenerated sheet: netlist connectivity of its refs vs SKiDL, and KiCad ERC.
# Usage: sh tools/check_sheet.sh <sheet name> <ref,ref,...>
K="/c/Program Files/KiCad/10.0/bin/kicad-cli.exe"
D=kicad/poe_usb_hid_bridge_rev4g
T="${TMP:-/tmp}/chk_$$"
"$K" sch export netlist -o "$T.net" $D/poe_usb_hid_bridge_rev4g.kicad_sch >/dev/null 2>&1
python tools/netcompare.py "${REFNET:-outputs/poe_usb_hid_bridge_rev4g.net}" "$T.net" --refs "$2"
"$K" sch erc --severity-all -o "$T.rpt" $D/poe_usb_hid_bridge_rev4g.kicad_sch >/dev/null 2>&1
grep -E "ERC messages" "$T.rpt"
grep -E "^\[" -A3 "$T.rpt" | grep -iE "$1|^\[" | head -40
rm -f "$T.net" "$T.rpt"
