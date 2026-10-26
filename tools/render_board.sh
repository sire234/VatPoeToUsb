#!/bin/sh
# Render top / bottom / iso images of the board as it will be built: the consigned part U1 is
# DNP in the JLC export but fitted, so a temporary copy without U1's DNP flag is rendered
# (all other DNP options stay hidden). The real board file is not changed.
# Usage: sh tools/render_board.sh <board.kicad_pcb> <output dir>
set -e
K="/c/Program Files/KiCad/10.0/bin/kicad-cli.exe"
B="$1"; O="$2"
T="$(dirname "$B")/_render_tmp.kicad_pcb"
# U1 is the only footprint with "smd exclude_from_pos_files dnp" (in BOM, not in CPL)
sed -e 's/(attr smd exclude_from_pos_files dnp)/(attr smd exclude_from_pos_files)/' "$B" > "$T"
"$K" pcb render -o "$O/render_top.png" -w 2384 -h 784 --side top --quality high "$T"
"$K" pcb render -o "$O/render_bottom.png" -w 2384 -h 784 --side bottom --quality high "$T"
"$K" pcb render -o "$O/render_iso.png" -w 2384 -h 1176 --side top --quality high --floor --rotate "-45,0,45" "$T"
"$K" pcb render -o "$O/render_iso_bottom.png" -w 2384 -h 1176 --side bottom --quality high --floor --rotate "-45,0,-45" "$T"
rm -f "$T" "${T%.kicad_pcb}.kicad_prl"
