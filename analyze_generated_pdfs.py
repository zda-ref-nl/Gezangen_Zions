#!/usr/bin/env python3
"""
Analyze the generated PDF files to understand what content they contain
"""

from PyPDF2 import PdfReader
import os
import re

def analyze_pdf_content(pdf_path):
    """Analyze what's in a PDF file"""
    print(f"\n=== Analyzing {os.path.basename(pdf_path)} ===")
    
    try:
        reader = PdfReader(pdf_path)
        print(f"Pages: {len(reader.pages)}")
        
        for i, page in enumerate(reader.pages):
            print(f"\nPage {i+1}:")
            text = page.extract_text()
            
            # Look for hymn numbers
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            hymn_numbers = []
            titles = []
            
            for j, line in enumerate(lines[:15]):  # Check first 15 lines
                # Look for hymn number patterns
                match = re.search(r'^\s*(\d+)\.?\s*$', line)
                if match:
                    hymn_numbers.append(match.group(1))
                
                # Look for hymn number followed by title
                match = re.search(r'^\s*(\d+)\.\s*(.+)', line)
                if match:
                    hymn_numbers.append(match.group(1))
                    titles.append(match.group(2))
                
                # Look for potential titles (capitalized lines)
                if line.isupper() and len(line) > 3:
                    titles.append(line)
            
            if hymn_numbers:
                print(f"  Hymn numbers found: {', '.join(set(hymn_numbers))}")
            if titles:
                print(f"  Potential titles: {', '.join(set(titles)[:3])}")
            
            # Show first few lines of text
            if lines:
                print(f"  First lines: {' | '.join(lines[:5])}")
            
    except Exception as e:
        print(f"Error analyzing {pdf_path}: {e}")

def main():
    output_dir = 'gezangen_zions_individual'
    if not os.path.exists(output_dir):
        print(f"Output directory {output_dir} not found")
        return
    
    pdf_files = [f for f in os.listdir(output_dir) if f.endswith('.pdf')]
    pdf_files.sort()
    
    for filename in pdf_files:
        pdf_path = os.path.join(output_dir, filename)
        analyze_pdf_content(pdf_path)

if __name__ == "__main__":
    main()