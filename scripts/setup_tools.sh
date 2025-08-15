#!/usr/bin/env bash
set -euo pipefail

TOOLS_DIR="/workspace/tools"
AUDI_DIR=""
LILYPOND_DIR=""
mkdir -p "$TOOLS_DIR"

log() { printf "[setup_tools] %s\n" "$*"; }

download_audiveris() {
	log "Downloading Audiveris..."
	cd "$TOOLS_DIR"
	# Try known versions
	local versions=("5.3.1" "5.3.0" "5.2.1" "5.2.0" "5.1.0")
	local url=""
	for v in "${versions[@]}"; do
		url="https://github.com/Audiveris/audiveris/releases/download/${v}/audiveris-${v}-bin.zip"
		if wget -q --timeout=20 --tries=1 --spider "$url"; then
			log "Found Audiveris ${v} at $url"
			wget -q -O audiveris-bin.zip "$url"
			unzip -q -o audiveris-bin.zip
			AUDI_DIR=$(ls -d audiveris-* | head -n1)
			if [ -n "$AUDI_DIR" ] && [ -d "$AUDI_DIR/bin" ]; then
				log "Audiveris installed in: $TOOLS_DIR/$AUDI_DIR"
				return 0
			fi
		fi
		log "Version $v not available, trying next..."
	done
	log "ERROR: Could not download Audiveris."
	return 1
}

download_lilypond() {
	log "Downloading LilyPond..."
	cd "$TOOLS_DIR"
	local versions=("2.24.3" "2.24.2" "2.24.1")
	local url=""
	for v in "${versions[@]}"; do
		# Try GitLab release URL first
		url="https://gitlab.com/lilypond/lilypond/-/releases/v${v}/downloads/lilypond-${v}-linux-x86_64.tar.xz"
		if wget -q --timeout=20 --tries=1 --spider "$url"; then
			log "Found LilyPond ${v} at $url"
			wget -q -O lilypond.tar.xz "$url"
			tar -xJf lilypond.tar.xz
			LILYPOND_DIR=$(ls -d lilypond-* | head -n1)
			if [ -n "$LILYPOND_DIR" ] && [ -d "$LILYPOND_DIR/bin" ]; then
				log "LilyPond installed in: $TOOLS_DIR/$LILYPOND_DIR"
				return 0
			fi
		fi
		# Try alternate mirror path
		url="https://lilypond.org/downloads/binaries/linux-x86_64/lilypond-${v}-linux-x86_64.tar.xz"
		if wget -q --timeout=20 --tries=1 --spider "$url"; then
			log "Found LilyPond ${v} at $url"
			wget -q -O lilypond.tar.xz "$url"
			tar -xJf lilypond.tar.xz
			LILYPOND_DIR=$(ls -d lilypond-* | head -n1)
			if [ -n "$LILYPOND_DIR" ] && [ -d "$LILYPOND_DIR/bin" ]; then
				log "LilyPond installed in: $TOOLS_DIR/$LILYPOND_DIR"
				return 0
			fi
		fi
		log "Version $v not available, trying next..."
	done
	log "ERROR: Could not download LilyPond."
	return 1
}

main() {
	if [ ! -d "$TOOLS_DIR" ]; then mkdir -p "$TOOLS_DIR"; fi
	if [ ! -d "$TOOLS_DIR" ]; then log "ERROR: Cannot create tools dir $TOOLS_DIR"; exit 1; fi

	if [ ! -d "$TOOLS_DIR"/audiveris-* ]; then
		download_audiveris || true
	else
		log "Audiveris already present."
	fi

	if [ ! -d "$TOOLS_DIR"/lilypond-* ]; then
		download_lilypond || true
	else
		log "LilyPond already present."
	fi

	log "Setup complete."
}

main "$@"