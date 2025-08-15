#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   scripts/musicxml_to_lilypond.sh <input-xml-or-dir> <output-dir>
#
# It tries these tools:
#   - musescore4 / musescore3 CLI to convert MusicXML -> PDF directly
#   - musicxml2ly + lilypond to convert XML -> LY -> PDF

INPUT="${1:-}"
OUTPUT="${2:-}"

if [ -z "$INPUT" ] || [ -z "$OUTPUT" ]; then
	echo "Usage: $0 <input-xml-or-dir> <output-dir>" >&2
	exit 1
fi

# Detect tools
MSCORE_BIN=""
for c in mscore museval musescore musescore3 musescore4; do
	if command -v "$c" >/dev/null 2>&1; then MSCORE_BIN="$c"; break; fi
	done

LILYPOND_BIN="${LILYPOND_BIN:-}"
if [ -z "$LILYPOND_BIN" ]; then
	LILYPOND_BIN=$(ls -1d /workspace/tools/lilypond-*/bin/lilypond 2>/dev/null | head -n1 || true)
fi
if [ -z "$LILYPOND_BIN" ]; then
	LILYPOND_BIN=$(command -v lilypond || true)
fi

MXML2LY_BIN="${MXML2LY_BIN:-}"
if [ -z "$MXML2LY_BIN" ]; then
	MXML2LY_BIN=$(command -v musicxml2ly || true)
fi

mkdir -p "$OUTPUT"

convert_with_musescore() {
	local xml="$1"; local outdir="$2"
	local base=$(basename "$xml")
	local stem="${base%.*}"
	echo "[typeset] MuseScore: $base"
	"$MSCORE_BIN" -o "$outdir/$stem.pdf" "$xml" >/dev/null 2>&1 || return 1
}

convert_with_lilypond() {
	local xml="$1"; local outdir="$2"
	local base=$(basename "$xml")
	local stem="${base%.*}"
	echo "[typeset] LilyPond: $base"
	local lyfile="$outdir/$stem.ly"
	"$MXML2LY_BIN" "$xml" -o "$lyfile" >/dev/null 2>&1 || return 1
	"$LILYPOND_BIN" -o "$outdir/$stem" "$lyfile" >/dev/null 2>&1 || return 1
}

process_one() {
	local xml="$1"
	if [ -n "$MSCORE_BIN" ]; then
		convert_with_musescore "$xml" "$OUTPUT" && return 0
	fi
	if [ -n "$MXML2LY_BIN" ] && [ -n "$LILYPOND_BIN" ]; then
		convert_with_lilypond "$xml" "$OUTPUT" && return 0
	fi
	echo "[typeset] ERROR: No available toolchain to convert $xml" >&2
	return 1
}

export -f process_one convert_with_musescore convert_with_lilypond
export MSCORE_BIN MXML2LY_BIN LILYPOND_BIN OUTPUT

if [ -d "$INPUT" ]; then
	mapfile -t files < <(find "$INPUT" -maxdepth 1 -type f \( -iname '*.xml' -o -iname '*.musicxml' \) | sort)
	for f in "${files[@]}"; do process_one "$f"; done
else
	process_one "$INPUT"
fi

echo "[typeset] Done. Output: $OUTPUT"