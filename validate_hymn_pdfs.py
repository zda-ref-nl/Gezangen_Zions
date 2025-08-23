#!/usr/bin/env python3
"""
Validate the generated hymn PDFs to see what content they actually contain
"""

from PyPDF2 import PdfReader
import os
import re

def validate_hymn_pdf(pdf_path):
    """Validate what content is in a hymn PDF"""
    print(f"\n=== Validating {os.path.basename(pdf_path)} ===")
    
    try:
        reader = PdfReader(pdf_path)
        print(f"Pages: {len(reader.pages)}")
        
        for i, page in enumerate(reader.pages):
            print(f"\nPage {i+1} content:")
            text = page.extract_text()
            
            if text.strip():
                # Look for hymn numbers in the text
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                
                hymn_numbers = []
                titles = []
                
                for line in lines[:20]:  # Check first 20 lines
                    # Look for standalone numbers that could be hymn numbers
                    if re.match(r'^\d{1,3}$', line.strip()):
                        hymn_numbers.append(line.strip())
                    
                    # Look for number followed by text
                    match = re.match(r'^(\d{1,3})\.\s*(.+)', line)
                    if match:
                        hymn_numbers.append(match.group(1))
                        titles.append(match.group(2)[:50])
                    
                    # Look for potential title lines (capitalized)
                    if len(line) > 5 and any(word[0].isupper() for word in line.split()):
                        if not any(skip in line.upper() for skip in ['PAGE', 'PSALM', 'MATTH', 'GEZANGEN', 'LOFZANGEN']):
                            titles.append(line[:50])
                
                if hymn_numbers:
                    print(f"  Potential hymn numbers: {', '.join(set(hymn_numbers))}")
                if titles:
                    print(f"  Potential titles/content: {' | '.join(set(titles)[:3])}")
                
                # Show first few lines for context
                print(f"  First lines: {' | '.join(lines[:5])}")
            else:
                print("  (No extractable text)")
        
    except Exception as e:
        print(f"Error validating {pdf_path}: {e}")

def main():
    output_dir = 'fixed_individual_hymns'
    if not os.path.exists(output_dir):
        print(f"Output directory {output_dir} not found")
        return
    
    pdf_files = [f for f in os.listdir(output_dir) if f.endswith('.pdf')]
    pdf_files.sort()
    
    # Validate first few files
    for filename in pdf_files[:5]:  # Just first 5 for now
        pdf_path = os.path.join(output_dir, filename)
        validate_hymn_pdf(pdf_path)

if __name__ == "__main__":
    main()