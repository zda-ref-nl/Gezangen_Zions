#!/usr/bin/env python3
"""
Analyze the original PDF structure to understand hymn layout
"""

from PyPDF2 import PdfReader
import re

def analyze_original_pdf(pdf_path):
    """Analyze the original PDF structure"""
    print(f"Analyzing original PDF: {pdf_path}")
    
    try:
        reader = PdfReader(pdf_path)
        print(f"Total pages: {len(reader.pages)}")
        
        # Analyze first 20 pages to understand structure
        for page_num in range(min(20, len(reader.pages))):
            page = reader.pages[page_num]
            text = page.extract_text()
            
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            hymn_numbers = []
            
            # Look for hymn numbers
            for line in lines[:10]:  # Check first 10 lines
                match = re.search(r'^\s*(\d+)\.?\s*$', line)
                if match:
                    hymn_numbers.append(match.group(1))
                
                match = re.search(r'^\s*(\d+)\.\s*(.+)', line)
                if match:
                    hymn_numbers.append(match.group(1))
            
            if hymn_numbers or page_num < 5:  # Show first 5 pages or pages with hymns
                print(f"\nPage {page_num + 1}:")
                if hymn_numbers:
                    print(f"  Hymn numbers: {', '.join(set(hymn_numbers))}")
                if lines:
                    print(f"  First lines: {' | '.join(lines[:3])}")
                    print(f"  Total lines: {len(lines)}")
        
        # Also check some middle pages
        print("\n=== Middle section analysis ===")
        middle_start = 50
        for page_num in range(middle_start, min(middle_start + 10, len(reader.pages))):
            page = reader.pages[page_num]
            text = page.extract_text()
            
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            hymn_numbers = []
            
            for line in lines[:10]:
                match = re.search(r'^\s*(\d+)\.?\s*$', line)
                if match:
                    hymn_numbers.append(match.group(1))
                
                match = re.search(r'^\s*(\d+)\.\s*(.+)', line)
                if match:
                    hymn_numbers.append(match.group(1))
            
            if hymn_numbers:
                print(f"\nPage {page_num + 1}:")
                print(f"  Hymn numbers: {', '.join(set(hymn_numbers))}")
                if lines:
                    print(f"  First lines: {' | '.join(lines[:3])}")
        
    except Exception as e:
        print(f"Error analyzing PDF: {e}")

def main():
    pdf_path = "#Gezangen Zions.original.pdf"
    analyze_original_pdf(pdf_path)

if __name__ == "__main__":
    main()