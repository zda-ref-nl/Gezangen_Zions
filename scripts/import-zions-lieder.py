#!/usr/bin/env python3
"""
Zions-Lieder (DE) van songs.sdarm.life -> JSON in hetzelfde formaat als
src/data/hymnal/nl-gezangen-zions.json (Gezangen Zions-site).

Bron: de officiële LLM/Markdown-API van sdarm.life (zie songs.sdarm.life/llms.txt).
Eén request voor de hele bundel; per-lied-fallback met nette rate limit (max ~60/min).

Uitvoer (data/zions-lieder/):
    bundel.json      volledige bundel (formaat van nl-gezangen-zions.json)
    index.json       metadata + lijst van deelbestanden
    deel-NN.json     liederen per 100, gelezen door de Zions-Lieder-artifact

Gebruik:
    python3 scripts/import-zions-lieder.py [uitvoermap]
Draait wekelijks via .github/workflows/import-zions-lieder.yml.
"""
import json
import re
import sys
import time
import urllib.request

API = "https://api.sdarm.life/api/v1/llm"
SLUG = "zions-lieder"
UA = "zda-ref.nl liederen-import (contact: info@zda-ref.nl)"

RE_SONG = re.compile(r"^##\s+(\d+)\.\s+(.+?)\s*$")
RE_LABEL = re.compile(r"^\*\*(.+?)\*\*\s*$")
RE_SITE = re.compile(r"^Site:\s*(\S+)")


def get(url: str) -> str:
    for poging in range(5):
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/markdown, text/plain"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wacht = int(e.headers.get("Retry-After", "10"))
                print(f"429 – wacht {wacht}s", file=sys.stderr)
                time.sleep(wacht)
                continue
            raise
    raise RuntimeError(f"Mislukt na 5 pogingen: {url}")


def parse(md: str) -> list[dict]:
    """Parse Markdown met '## N. Titel', '**1**'-strofen en '**Refrain**'."""
    liederen, lied, blok = [], None, None

    def sluit_blok():
        nonlocal blok
        if lied is not None and blok and blok["regels"]:
            if blok["soort"] == "refrain":
                # Alleen het eerste refrein bewaren (zelfde gedrag als NL-bundel)
                if not lied["stanzas"]["refrain"]:
                    lied["stanzas"]["refrain"] = blok["regels"]
            else:
                lied["stanzas"]["verses"].append(blok["regels"])
        blok = None

    for raw in md.splitlines():
        regel = raw.rstrip()
        if m := RE_SONG.match(regel):
            sluit_blok()
            lied = {"number": int(m.group(1)), "title": m.group(2).strip(),
                    "topic": "", "stanzas": {"verses": [], "refrain": []}, "_id": None}
            liederen.append(lied)
            continue
        if lied is None:
            continue
        if m := RE_SITE.match(regel):
            sluit_blok()
            lied["_id"] = m.group(1).rstrip("/").split("/")[-1]
            continue
        if m := RE_LABEL.match(regel):
            sluit_blok()
            label = m.group(1).strip().lower()
            blok = {"soort": "refrain" if label.startswith(("refrain", "chor", "kehr")) else "vers", "regels": []}
            continue
        if regel.strip() in ("", "---"):
            continue
        if regel.startswith("#"):
            continue
        if blok is None:  # tekst zonder label: behandel als strofe
            blok = {"soort": "vers", "regels": []}
        blok["regels"].append(regel.strip())
    sluit_blok()
    return liederen


OUT_DIR = "data/zions-lieder"
DEEL_GROOTTE = 100  # liederen per deelbestand (klein genoeg voor de GitHub-connector)


def schrijf_als_gewijzigd(pad: str, obj) -> bool:
    import os
    tekst = json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n"
    if os.path.exists(pad) and open(pad, encoding="utf-8").read() == tekst:
        return False
    os.makedirs(os.path.dirname(pad), exist_ok=True)
    with open(pad, "w", encoding="utf-8") as f:
        f.write(tekst)
    return True


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else OUT_DIR
    md = get(f"{API}/songbooks/{SLUG}")
    liederen = parse(md)

    # Fallback: lege liederen per stuk ophalen (songbook-endpoint kan ingekort zijn)
    leeg = [l for l in liederen if not l["stanzas"]["verses"] and l["_id"]]
    for i, l in enumerate(leeg, 1):
        print(f"Los ophalen {i}/{len(leeg)}: {l['number']}", file=sys.stderr)
        los = parse(get(f"{API}/songs/{l['_id']}"))
        if los:
            l["stanzas"] = los[0]["stanzas"]
        time.sleep(1.1)  # < 60 requests per minuut

    liederen = [l for l in liederen if l["stanzas"]["verses"]]
    liederen.sort(key=lambda l: l["number"])
    for l in liederen:
        l.pop("_id", None)
    if len(liederen) < 100:
        sys.exit(f"Te weinig liederen ({len(liederen)}); bron gewijzigd? Niets weggeschreven.")

    meta = {"id": "zions-lieder", "name": "Zions-Lieder", "language": "de",
            "totalHymns": len(liederen), "source": "SDARM Germany (songs.sdarm.life)"}

    # Volledige bundel, zelfde vorm als src/data/hymnal/nl-gezangen-zions.json
    gewijzigd = schrijf_als_gewijzigd(f"{out}/bundel.json", {**meta, "hymns": liederen, "topics": []})

    # Delen + index voor de Zions-Lieder-artifact
    delen = []
    for i in range(0, len(liederen), DEEL_GROOTTE):
        naam = f"deel-{i // DEEL_GROOTTE + 1:02d}.json"
        stuk = liederen[i:i + DEEL_GROOTTE]
        gewijzigd |= schrijf_als_gewijzigd(f"{out}/{naam}", stuk)
        delen.append({"bestand": naam, "van": stuk[0]["number"], "tot": stuk[-1]["number"]})
    gewijzigd |= schrijf_als_gewijzigd(f"{out}/index.json", {**meta, "delen": delen})

    print(f"{len(liederen)} liederen, {len(delen)} delen, "
          f"{sum(1 for l in liederen if l['stanzas']['refrain'])} met refrein. "
          f"{'Gewijzigd' if gewijzigd else 'Geen wijzigingen'}.")
    nummers = {l["number"] for l in liederen}
    ontbrekend = sorted(set(range(1, max(nummers) + 1)) - nummers)
    if ontbrekend:
        print(f"LET OP, ontbrekende nummers: {ontbrekend}")


if __name__ == "__main__":
    main()
