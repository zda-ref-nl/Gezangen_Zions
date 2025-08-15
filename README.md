# Gezangen Zions – Liederen uit PDF naar losse PDF's

Deze repository bevat scripts om uit de meegeleverde bundel-PDF elk lied opnieuw op te bouwen in een losse PDF met uitsluitend gratis tooling.

## Overzicht van de pipeline

1. Splitsen naar 1 PDF per pagina met heuristische bestandsnamen
2. (Optioneel) OMR met Audiveris: van bladmuziek-PDF naar MusicXML
3. Typesetten naar PDF via MuseScore of LilyPond

Alle stappen zijn te starten via `make`.

## Vereisten

- Linux x86_64
- Java (is aanwezig in deze omgeving)
- Netwerktoegang om binaries te downloaden

Zonder root-rechten worden Audiveris en LilyPond in `/workspace/tools` gedownload.

## Snelstart

```bash
make split         # Genereert 1-PDF-per-pagina in output/pages + index CSV
make setup         # Download Audiveris en LilyPond lokaal (geen root nodig)
make omr           # Zet per pagina PDF -> MusicXML (output/musicxml)
make typeset       # Zet MusicXML -> PDF (output/pdf)
```

De complete run kan met:

```bash
make all
```

Uitvoer:
- `output/pages/` – pagina-PDF's met heuristische bestandsnamen
- `output/pages_index.csv` – index met paginanummer, bestandsnaam, eerste tekstregel
- `output/musicxml/` – MusicXML-bestanden uit Audiveris (indien OMR gelukt is)
- `output/pdf/` – Eind-PDF's per lied via MuseScore/LilyPond

## Opmerkingen over nauwkeurigheid

- De originele PDF bevat zowel tekst als notatie. Tekstextractie lukt vaak, maar muziekherkenning (OMR) is niet 100% accuraat. Handmatige correcties kunnen nodig zijn.
- MuseScore CLI kan MusicXML direct naar PDF exporteren. Als MuseScore niet beschikbaar is, gebruikt het script `musicxml2ly` + `lilypond`.

## Handmatig alternatief (alleen splitsen)

Als je enkel één-PDF-per-lied nodig hebt zonder OCR/OMR, kun je `make split` gebruiken en de resulterende pagina-PDF's direct gebruiken of handmatig groeperen.

## Bekende beperkingen

- De OMR-stap vereist Audiveris en kan mislukken op complexe bladmuziek of lage scan-kwaliteit.
- Voor volledige foutloze reconstructie is vaak (korte) handmatige nabewerking nodig.