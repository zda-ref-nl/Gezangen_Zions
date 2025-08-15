SHELL := /usr/bin/bash

ORIG := /workspace/#Gezangen Zions.original.pdf
ONEPER := /workspace/#Gezangen Zions.onePerPage.pdf
OUT := /workspace/output
PAGES := $(OUT)/pages
MXML := $(OUT)/musicxml
PDFS := $(OUT)/pdf
MXML_ORIG := $(OUT)/musicxml_orig
PDFS_ORIG := $(OUT)/pdf_orig
INDEX := $(OUT)/pages_index.csv

.PHONY: all split omr typeset setup clean omr_orig typeset_orig

all: split omr typeset

setup:
	bash /workspace/scripts/setup_tools.sh

split:
	python3 /workspace/song_splitter.py "$(ORIG)" "$(PAGES)" --name-by-title --index-csv "$(INDEX)"

omr:
	mkdir -p "$(MXML)"
	bash /workspace/scripts/omr_audiveris.sh "$(PAGES)" "$(MXML)" --threads 2 || true

typeset:
	mkdir -p "$(PDFS)"
	bash /workspace/scripts/musicxml_to_lilypond.sh "$(MXML)" "$(PDFS)" || true

omr_orig:
	mkdir -p "$(MXML_ORIG)"
	bash /workspace/scripts/omr_audiveris.sh "$(ORIG)" "$(MXML_ORIG)" --threads 2 || true

typeset_orig:
	mkdir -p "$(PDFS_ORIG)"
	bash /workspace/scripts/musicxml_to_lilypond.sh "$(MXML_ORIG)" "$(PDFS_ORIG)" || true

clean:
	rm -rf "$(OUT)"
	mkdir -p "$(OUT)"