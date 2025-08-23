#!/usr/bin/env python3
"""
Analyze specific pages that likely contain hymns to understand layout.
"""

import json
from PyPDF2 import PdfReader
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import os
import re

def find_hymn_pages(pdf_path, start_page=5, end_page=15):
    """Look for pages that contain hymns."""
    print(f"Analyzing pages {start_page} to {end_page} for hymn content...")
    
    reader = PdfReader(pdf_path)
    
    for i in range(start_page, min(end_page, len(reader.pages))):
        print(f"\n--- Page {i+1} ---")
        page = reader.pages[i]
        
        try:
            # Extract text using PyPDF2
            pdf_text = page.extract_text()
            print("PDF Text preview:")
            preview = ' '.join(pdf_text.replace('\n', ' ').split())[:200]
            print(f"  {preview}...")
            
            # Convert to image for OCR
            images = convert_from_path(pdf_path, first_page=i+1, last_page=i+1, dpi=200)
            if images:
                image = images[0]
                
                # Run OCR
                ocr_text = pytesseract.image_to_string(image, lang='nld+eng')
                
                # Look for hymn numbers at start of lines
                lines = [line.strip() for line in ocr_text.split('\n') if line.strip()]
                hymn_numbers = []
                
                for line in lines[:20]:  # Check first 20 lines
                    # Look for patterns like "1.", "123", etc.
                    match = re.search(r'^\s*(\d+)\.?\s*$', line)
                    if match:
                        hymn_numbers.append(match.group(1))
                    # Also look for numbers followed by text that might be titles
                    match = re.search(r'^\s*(\d+)\.?\s+([A-Za-z].*)', line)
                    if match:
                        hymn_numbers.append(f"{match.group(1)}: {match.group(2)[:30]}...")
                
                print("OCR Hymn numbers found:")
                for num in hymn_numbers[:5]:
                    print(f"  {num}")
                
                if not hymn_numbers:
                    print("  No clear hymn numbers detected")
                    
                # Look for musical notation indicators
                if any(word in ocr_text.lower() for word in ['♪', '♫', 'nota', 'melodie', 'psalm']):
                    print("  Possible musical notation detected")
                
        except Exception as e:
            print(f"  Error analyzing page: {e}")

def match_with_metadata(json_path):
    """Load hymn metadata to understand expected content."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    hymns = data.get('hymns', [])
    print(f"\nFirst 10 hymns from metadata:")
    
    for i in range(min(10, len(hymns))):
        hymn = hymns[i]
        title = hymn.get('title', 'No title')
        verses = hymn.get('stanzas', {}).get('verses', [])
        verse_count = len(verses)
        
        print(f"  {hymn['num']}: {title} ({verse_count} verses)")
        
        # Show first verse if available
        if verses and verses[0]:
            first_line = verses[0][0] if verses[0] else "No text"
            print(f"      First line: {first_line}")

if __name__ == "__main__":
    pdf_path = "#Gezangen Zions.original.pdf"
    json_path = "gezangen-zions.json"
    
    if not os.path.exists(pdf_path):
        print(f"PDF file not found: {pdf_path}")
        exit(1)
    
    # Analyze pages likely to contain hymns (skip title pages)
    find_hymn_pages(pdf_path, start_page=8, end_page=18)
    
    print("\n" + "="*60)
    match_with_metadata(json_path)