#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   scripts/omr_audiveris.sh <input-pdf-or-dir> <output-dir> [--threads N]
#
# Requires Audiveris. Detection order:
#   1) $AUDIVERIS_BIN
#   2) /workspace/tools/audiveris-*/bin/Audiveris
#   3) audiveris in PATH

INPUT="${1:-}"
OUTPUT="${2:-}"
THREADS=1
if [ "${3:-}" = "--threads" ]; then
	THREADS="${4:-1}"
fi

if [ -z "$INPUT" ] || [ -z "$OUTPUT" ]; then
	echo "Usage: $0 <input-pdf-or-dir> <output-dir> [--threads N]" >&2
	exit 1
fi

# Detect Audiveris binary
AUDI_BIN="${AUDIVERIS_BIN:-}"
if [ -z "$AUDI_BIN" ]; then
	# Try local tools dir
	AUDI_BIN=$(ls -1d /workspace/tools/audiveris-*/bin/Audiveris 2>/dev/null | head -n1 || true)
fi
if [ -z "$AUDI_BIN" ]; then
	AUDI_BIN=$(command -v audiveris || true)
fi
if [ -z "$AUDI_BIN" ]; then
	echo "ERROR: Audiveris binary not found. Set AUDIVERIS_BIN or run scripts/setup_tools.sh" >&2
	exit 2
fi

mkdir -p "$OUTPUT"

process_one() {
	local pdf="$1"
	echo "[omr] Processing: $pdf"
	"$AUDI_BIN" -batch -export -output "$OUTPUT" "$pdf" >/dev/null 2>&1 || {
		echo "[omr] WARN: Failed: $pdf" >&2
		return 1
	}
}

export -f process_one
export AUDI_BIN OUTPUT

if [ -d "$INPUT" ]; then
	mapfile -t files < <(find "$INPUT" -maxdepth 1 -type f -iname '*.pdf' | sort)
	if [ "${#files[@]}" -eq 0 ]; then
		echo "No PDF files found in $INPUT" >&2
		exit 0
	fi
	if command -v parallel >/dev/null 2>&1 && [ "$THREADS" -gt 1 ]; then
		printf '%s\n' "${files[@]}" | parallel -j "$THREADS" process_one {}
	else
		for f in "${files[@]}"; do process_one "$f"; done
	fi
else
	process_one "$INPUT"
fi

echo "[omr] Done. Output: $OUTPUT"