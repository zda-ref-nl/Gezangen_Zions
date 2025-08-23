# Gezangen Zions Hymn Splitter

Automatische verwerking van het Gezangen Zions PDF naar individuele liederenbestanden met OCR en muziekblad herkenning.

## 🎯 Overzicht

Dit project implementeert een complete oplossing voor het automatisch splitsen van het Gezangen Zions hymnenboek in individuele PDF-bestanden. Elk lied wordt opgeslagen als een apart A4-geformatteerd PDF-document met volledige metadata.

## ✨ Functionaliteit

- ✅ **Automatische liederensplitsing**: Splitst alle 532+ hymnen in individuele PDF-bestanden
- ✅ **Intelligente paginadistributie**: Gebruikt metadata en tekstanalyse voor optimale pagina-indeling  
- ✅ **Rijke metadata**: Voegt titel, topicategorieën, en coupletaantal toe aan elke PDF
- ✅ **Topicorganisatie**: Organiseert bestanden volgens de originele categorieën (Eere- en Lofzangen, De Heilige Geest, etc.)
- ✅ **Index generatie**: Creëert HTML en CSV indexen voor eenvoudig zoeken
- ✅ **A4 formaat**: Alle uitvoer geoptimaliseerd voor standaard A4 afdrukken

## 📁 Projectstructuur

```
├── #Gezangen Zions.original.pdf    # Origineel PDF-bestand (14MB)  
├── gezangen-zions.json             # Complete metadata (532 hymnen, 36 categorieën)
├── complete_processor.py           # Hoofdscript voor volledige verwerking
├── fast_hymn_splitter.py           # Snelle versie voor testen
├── hymn_splitter.py                # OCR-gebaseerde versie (uitgebreid)
├── analyze_pdf.py                  # PDF structuuranalyse
├── analyze_hymn_pages.py           # Liederenpagina detectie
└── splitpdf.py                     # Origineel (links/rechts splitsing)
```

## 🚀 Gebruik

### Volledige verwerking (aanbevolen)

```bash
# Verwerk alle hymnen
python3 complete_processor.py

# Test met eerste 50 hymnen  
python3 complete_processor.py --max-hymns 50

# Aangepaste uitvoermap
python3 complete_processor.py --output mijn_gezangen --max-hymns 100
```

### Snelle verwerking (voor testen)

```bash
# Eerste 10 hymnen
python3 fast_hymn_splitter.py --count 10

# Hymnen 50-70
python3 fast_hymn_splitter.py --start 50 --count 20
```

## 📊 Uitvoer

Het script creëert de volgende structuur:

```
gezangen_zions_individual/
├── 001_Prijst_de_Heer_met_blijde_galmen.pdf
├── 002_Grote_God_U_loven_wij.pdf
├── ...
├── 532_Leer_mij_aanbidden_Heer.pdf
├── index.html                      # Browsable index
├── hymn_index.csv                  # Spreadsheet-compatibel
└── by_topic/
    ├── Eere_en_Lofzangen/
    ├── De_Heilige_Geest/  
    ├── Jezus_Leven_op_Aarde/
    └── ...
```

### Bestandsformaat

Elke PDF bevat:
- ✅ Originele pagina's met tekst en muzieknotatie
- ✅ PDF metadata (titel, onderwerp, trefwoorden)
- ✅ A4-formaat optimalisatie
- ✅ Volledige zoekbare tekst

## 🔧 Technische Details

### Vereisten

```bash
pip3 install PyPDF2 pillow pytesseract pdf2image
sudo apt-get install tesseract-ocr tesseract-ocr-nld poppler-utils
```

### Algoritme

1. **PDF Analyse**: Laadt originele PDF (193 pagina's) en metadata (532 hymnen)
2. **Intelligente Paginadistributie**: 
   - Analyseert coupletaantal en tekstcomplexiteit
   - Schat benodigde pagina's per hymne (1-4 pagina's)
   - Houdt rekening met refreinen en langere composities
3. **Metadata Integratie**: Gebruikt gezangen-zions.json voor:
   - Titel en coupletinformatie
   - Topicategorieën (36 theologische thema's)
   - Tekstinhoud voor validatie
4. **PDF Generatie**: Creëert individuele A4 PDFs met rijke metadata
5. **Organisatie**: Sorteert op nummer + categorieën

### OCR Integration

Voor geavanceerde gebruik ondersteunt het project:
- Tesseract OCR met Nederlandse taalondersteuning
- Automatische liederennummerdetectie
- Tekstvalidatie tegen bekende metadata

## 📈 Resultaten

**Test Output (eerste 25 hymnen):**
- ✅ 25 individuele PDF-bestanden gegenereerd 
- 📁 Georganiseerd in "Eere- en Lofzangen" categorie
- 📋 HTML en CSV indexen gegenereerd
- 💾 Totale grootte: ~2.5MB (gemiddeld 100KB per hymne)

**Geschatte Volledige Output:**
- 📄 532 individuele PDF-bestanden
- 📂 36 topicategorieën 
- 💾 ~50-75MB totale uitvoer
- ⚡ Verwerkingstijd: ~5-10 minuten

## 🎵 Liederenorganisatie

Het originele Gezangen Zions bevat 36 categorieën:

1. **Eere- en Lofzangen** (1-33)
2. **De Heilige Geest** (34-42)  
3. **Jezus' Leven op Aarde** (43-53)
4. **Jezus Onze Hoogepriester** (54-56)
5. **De Heilige Schrift** (57-67)
... [zie gezangen-zions.json voor complete lijst]

## 🔄 Workflow

```
Origineel PDF (14MB) 
    ↓
JSON Metadata Analyse (532 hymnen)
    ↓  
Intelligente Paginadistributie
    ↓
Individual PDF Generatie (A4)
    ↓
Metadata Integratie + Topicorganisatie
    ↓
Index Generatie (HTML/CSV)
    ↓
✅ 532 Individuele Hymnbestanden
```

## 🚀 Toegevoegde Waarde

- ✅ **Eenvoudig delen**: Individuele hymnen per email of messenger
- ✅ **Selectief afdrukken**: Print alleen benodigde liederen
- ✅ **Digitaal archief**: Doorzoekbare collectie met metadata
- ✅ **Toegankelijkheid**: Verbeterde digitalisering voor kerken en persoonlijk gebruik
- ✅ **Flexibiliteit**: Verschillende organisatiemethoden (nummer/topic)

## 📝 Licentie

Dit project is ontwikkeld voor educatief gebruik en digitalisering van religieus erfgoed. Het respecteert auteursrechten van het originele Gezangen Zions materiaal.