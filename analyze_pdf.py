#!/usr/bin/env python3
"""
Analyze the structure of Gezangen Zions PDF to understand layout and content organization.
"""

import json
from PyPDF2 import PdfReader
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import os
import sys

def analyze_pdf_structure(pdf_path):
    """Analyze basic PDF structure."""
    print(f"Analyzing PDF structure: {pdf_path}")
    
    reader = PdfReader(pdf_path)
    print(f"Number of pages: {len(reader.pages)}")
    
    # Get basic info about first few pages
    for i in range(min(5, len(reader.pages))):
        page = reader.pages[i]
        print(f"Page {i+1}:")
        print(f"  Size: {page.mediabox.width} x {page.mediabox.height}")
        
        # Extract text from page
        try:
            text = page.extract_text()
            # Get first 100 chars and clean up
            preview = ' '.join(text.replace('\n', ' ').split())[:100]
            print(f"  Text preview: {preview}...")
        except Exception as e:
            print(f"  Text extraction error: {e}")
        print()

def load_hymn_metadata(json_path):
    """Load the hymn metadata from JSON."""
    print(f"Loading hymn metadata: {json_path}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    hymns = data.get('hymns', [])
    print(f"Found {len(hymns)} hymns in metadata")
    
    # Show some examples
    for i in range(min(5, len(hymns))):
        hymn = hymns[i]
        print(f"Hymn {hymn['num']}: {hymn['title']}")
    
    return hymns

def test_ocr_on_page(pdf_path, page_num=0):
    """Test OCR on a specific page."""
    print(f"Testing OCR on page {page_num + 1}...")
    
    try:
        # Convert first page to image
        images = convert_from_path(pdf_path, first_page=page_num+1, last_page=page_num+1, dpi=150)
        if not images:
            print("No images converted")
            return
            
        image = images[0]
        print(f"Converted page to image: {image.size}")
        
        # Run OCR with Dutch language
        ocr_text = pytesseract.image_to_string(image, lang='nld+eng')
        print("OCR Text preview (first 500 chars):")
        print(ocr_text[:500])
        
        # Look for hymn numbers
        lines = ocr_text.split('\n')
        numbers_found = []
        for line in lines:
            if any(char.isdigit() for char in line) and len(line.strip()) < 20:
                numbers_found.append(line.strip())
        
        print(f"\nPossible hymn numbers found: {numbers_found[:10]}")
        
    except Exception as e:
        print(f"OCR test failed: {e}")

if __name__ == "__main__":
    # File paths
    original_pdf = "#Gezangen Zions.original.pdf"
    json_file = "gezangen-zions.json"
    
    if not os.path.exists(original_pdf):
        print(f"PDF file not found: {original_pdf}")
        sys.exit(1)
    
    if not os.path.exists(json_file):
        print(f"JSON file not found: {json_file}")
        sys.exit(1)
    
    print("=== PDF Analysis ===")
    analyze_pdf_structure(original_pdf)
    
    print("\n=== Hymn Metadata Analysis ===")
    hymns = load_hymn_metadata(json_file)
    
    print("\n=== OCR Test ===")
    test_ocr_on_page(original_pdf, 0)  # Test first page