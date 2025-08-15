SHELL := /usr/bin/bash

ORIG := /workspace/#Gezangen Zions.original.pdf
ONEPER := /workspace/#Gezangen Zions.onePerPage.pdf
OUT := /workspace/output
PAGES := $(OUT)/pages
MXML := $(OUT)/musicxml
PDFS := $(OUT)/pdf
INDEX := $(OUT)/pages_index.csv

.PHONY: all split omr typeset setup clean

all: split omr typeset

setup:
	bash /workspace/scripts/setup_tools.sh

split:
	python3 /workspace/song_splitter.py "$(ONEPER)" "$(PAGES)" --name-by-title --index-csv "$(INDEX)"

omr:
	mkdir -p "$(MXML)"
	bash /workspace/scripts/omr_audiveris.sh "$(PAGES)" "$(MXML)" --threads 2 || true

typeset:
	mkdir -p "$(PDFS)"
	bash /workspace/scripts/musicxml_to_lilypond.sh "$(MXML)" "$(PDFS)" || true

clean:
	rm -rf "$(OUT)"
	mkdir -p "$(OUT)"