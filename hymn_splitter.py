#!/usr/bin/env python3
"""
Advanced Gezangen Zions Hymn Splitter

This script automatically splits the Gezangen Zions PDF into individual hymn files.
It uses OCR to detect hymn boundaries and the JSON metadata to validate and organize content.
"""

import json
import os
import re
from PyPDF2 import PdfReader, PdfWriter
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from typing import List, Dict, Tuple, Optional
import argparse

class HymnSplitter:
    def __init__(self, pdf_path: str, json_path: str, output_dir: str = "individual_hymns"):
        self.pdf_path = pdf_path
        self.json_path = json_path
        self.output_dir = output_dir
        self.reader = None
        self.hymns_metadata = []
        self.page_mappings = []
        
    def load_data(self):
        """Load PDF and hymn metadata."""
        print("Loading PDF and metadata...")
        
        # Load PDF
        self.reader = PdfReader(self.pdf_path)
        print(f"PDF loaded: {len(self.reader.pages)} pages")
        
        # Load JSON metadata
        with open(self.json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.hymns_metadata = data.get('hymns', [])
        print(f"Metadata loaded: {len(self.hymns_metadata)} hymns")
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
    
    def detect_hymn_numbers_on_page(self, page_num: int, use_ocr: bool = True) -> List[str]:
        """Detect hymn numbers on a specific page."""
        page = self.reader.pages[page_num]
        hymn_numbers = []
        
        # Try PDF text extraction first
        try:
            pdf_text = page.extract_text()
            lines = [line.strip() for line in pdf_text.split('\n') if line.strip()]
            
            for line in lines[:10]:  # Check first 10 lines
                # Look for hymn number patterns
                match = re.search(r'^\s*(\d+)\.?\s*$', line)
                if match:
                    hymn_numbers.append(match.group(1))
                    break  # Usually only one hymn number per page
                    
        except Exception as e:
            print(f"PDF text extraction failed for page {page_num + 1}: {e}")
        
        # If no numbers found and OCR requested, try OCR
        if not hymn_numbers and use_ocr:
            try:
                images = convert_from_path(self.pdf_path, first_page=page_num+1, last_page=page_num+1, dpi=150)
                if images:
                    image = images[0]
                    ocr_text = pytesseract.image_to_string(image, lang='nld+eng')
                    lines = [line.strip() for line in ocr_text.split('\n') if line.strip()]
                    
                    for line in lines[:15]:  # Check more lines with OCR
                        # Look for hymn number patterns
                        match = re.search(r'^\s*(\d+)\.?\s*$', line)
                        if match:
                            hymn_numbers.append(match.group(1))
                        # Also check for numbers followed by titles
                        match = re.search(r'^\s*(\d+)\.\s+([A-Za-z].*)', line)
                        if match:
                            hymn_numbers.append(match.group(1))
                        
            except Exception as e:
                print(f"OCR failed for page {page_num + 1}: {e}")
        
        return list(set(hymn_numbers))  # Remove duplicates
    
    def map_hymns_to_pages(self, start_page: int = 8, end_page: int = None) -> Dict[str, List[int]]:
        """Map hymn numbers to page ranges."""
        if end_page is None:
            end_page = len(self.reader.pages)
            
        print(f"Mapping hymns to pages {start_page + 1} to {end_page}...")
        
        hymn_page_map = {}
        
        for page_num in range(start_page, end_page):
            print(f"Analyzing page {page_num + 1}...", end=' ')
            
            hymn_numbers = self.detect_hymn_numbers_on_page(page_num)
            
            if hymn_numbers:
                print(f"Found hymns: {', '.join(hymn_numbers)}")
                for num in hymn_numbers:
                    if num not in hymn_page_map:
                        hymn_page_map[num] = []
                    hymn_page_map[num].append(page_num)
            else:
                print("No hymns detected")
        
        return hymn_page_map
    
    def get_hymn_metadata(self, hymn_num: str) -> Optional[Dict]:
        """Get metadata for a specific hymn number."""
        for hymn in self.hymns_metadata:
            if hymn.get('num') == hymn_num:
                return hymn
        return None
    
    def create_individual_hymn_pdf(self, hymn_num: str, pages: List[int], metadata: Dict = None):
        """Create a PDF for a single hymn."""
        if not metadata:
            metadata = self.get_hymn_metadata(hymn_num)
        
        title = metadata.get('title', f'Hymn {hymn_num}') if metadata else f'Hymn {hymn_num}'
        safe_title = re.sub(r'[^\w\s-]', '', title).strip()
        safe_title = re.sub(r'[-\s]+', '_', safe_title)
        
        filename = f"{hymn_num.zfill(3)}_{safe_title}.pdf"
        output_path = os.path.join(self.output_dir, filename)
        
        writer = PdfWriter()
        
        # Add pages for this hymn
        for page_num in sorted(pages):
            if 0 <= page_num < len(self.reader.pages):
                writer.add_page(self.reader.pages[page_num])
        
        # Add metadata to PDF
        if metadata:
            writer.add_metadata({
                '/Title': f"{hymn_num}. {title}",
                '/Subject': 'Gezangen Zions - Individual Hymn',
                '/Creator': 'Gezangen Zions Hymn Splitter',
                '/Producer': 'PyPDF2'
            })
        
        # Write PDF
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        print(f"Created: {filename}")
        
        return output_path
    
    def split_hymns(self, start_page: int = 8, max_hymns: int = None):
        """Split the PDF into individual hymn files."""
        print("Starting hymn splitting process...")
        
        # Map hymns to pages
        hymn_page_map = self.map_hymns_to_pages(start_page)
        
        print(f"\nFound {len(hymn_page_map)} unique hymns")
        
        # Sort hymns numerically
        sorted_hymn_nums = sorted(hymn_page_map.keys(), key=lambda x: int(x) if x.isdigit() else float('inf'))
        
        if max_hymns:
            sorted_hymn_nums = sorted_hymn_nums[:max_hymns]
        
        # Create individual PDFs
        created_files = []
        for hymn_num in sorted_hymn_nums:
            pages = hymn_page_map[hymn_num]
            metadata = self.get_hymn_metadata(hymn_num)
            
            print(f"\nProcessing Hymn {hymn_num} (pages: {[p+1 for p in pages]})")
            if metadata:
                print(f"  Title: {metadata['title']}")
                verse_count = len(metadata.get('stanzas', {}).get('verses', []))
                print(f"  Verses: {verse_count}")
            
            output_path = self.create_individual_hymn_pdf(hymn_num, pages, metadata)
            created_files.append(output_path)
        
        print(f"\n✅ Successfully created {len(created_files)} individual hymn PDFs")
        print(f"Output directory: {self.output_dir}")
        
        return created_files

def main():
    parser = argparse.ArgumentParser(description='Split Gezangen Zions PDF into individual hymns')
    parser.add_argument('--pdf', default='#Gezangen Zions.original.pdf', help='Input PDF file')
    parser.add_argument('--json', default='gezangen-zions.json', help='Hymn metadata JSON file')
    parser.add_argument('--output', default='individual_hymns', help='Output directory')
    parser.add_argument('--start-page', type=int, default=8, help='Page to start analysis (0-indexed)')
    parser.add_argument('--max-hymns', type=int, help='Maximum number of hymns to process (for testing)')
    
    args = parser.parse_args()
    
    # Check if input files exist
    if not os.path.exists(args.pdf):
        print(f"Error: PDF file not found: {args.pdf}")
        return 1
        
    if not os.path.exists(args.json):
        print(f"Error: JSON file not found: {args.json}")
        return 1
    
    # Create splitter and run
    splitter = HymnSplitter(args.pdf, args.json, args.output)
    splitter.load_data()
    
    created_files = splitter.split_hymns(args.start_page, args.max_hymns)
    
    print(f"\n🎵 Hymn splitting completed! Created {len(created_files)} files.")
    
    return 0

if __name__ == "__main__":
    exit(main())