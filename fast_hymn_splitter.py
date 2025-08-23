#!/usr/bin/env python3
"""
Fast Gezangen Zions Hymn Splitter

A more efficient approach that uses the known structure and patterns.
"""

import json
import os
import re
from PyPDF2 import PdfReader, PdfWriter
from typing import List, Dict, Tuple, Optional
import argparse

class FastHymnSplitter:
    def __init__(self, pdf_path: str, json_path: str, output_dir: str = "individual_hymns"):
        self.pdf_path = pdf_path
        self.json_path = json_path
        self.output_dir = output_dir
        self.reader = None
        self.hymns_metadata = {}
        
    def load_data(self):
        """Load PDF and hymn metadata."""
        print("Loading PDF and metadata...")
        
        # Load PDF
        self.reader = PdfReader(self.pdf_path)
        print(f"PDF loaded: {len(self.reader.pages)} pages")
        
        # Load JSON metadata and create lookup
        with open(self.json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        hymns = data.get('hymns', [])
        for hymn in hymns:
            self.hymns_metadata[hymn['num']] = hymn
        
        print(f"Metadata loaded: {len(self.hymns_metadata)} hymns")
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
    
    def estimate_hymn_pages(self) -> Dict[str, List[int]]:
        """Systematically estimate hymn distribution based on content complexity."""
        total_pages = len(self.reader.pages)
        content_start_page = 10  # Skip title/index pages  
        content_end_page = total_pages - 5  # Skip appendix pages
        content_pages = content_end_page - content_start_page
        
        print(f"Content pages available: {content_pages}")
        
        hymn_page_map = {}
        current_page = content_start_page
        
        # Process hymns in numerical order
        for i in range(1, min(len(self.hymns_metadata) + 1, 101)):  # Process first 100 hymns
            hymn_num = str(i)
            if hymn_num not in self.hymns_metadata:
                continue
            
            # Calculate pages needed based on content
            metadata = self.hymns_metadata[hymn_num]
            verses = metadata.get('stanzas', {}).get('verses', [])
            refrain = metadata.get('stanzas', {}).get('refrain', [])
            
            # Calculate complexity
            verse_lines = sum(len(verse) for verse in verses)
            refrain_lines = len(refrain) if refrain else 0
            total_lines = verse_lines + (refrain_lines * max(1, len(verses) // 2))
            
            # Estimate pages based on content
            if total_lines <= 18:
                pages_needed = 1
            elif total_lines <= 40:
                pages_needed = 2
            else:
                pages_needed = 3
            
            # Ensure we don't exceed available pages
            if current_page + pages_needed > content_end_page:
                pages_needed = max(1, content_end_page - current_page)
            
            if current_page < content_end_page:
                pages = list(range(current_page, current_page + pages_needed))
                hymn_page_map[hymn_num] = pages
                current_page += pages_needed
            else:
                break
        
        print(f"Mapped {len(hymn_page_map)} hymns systematically")
        return hymn_page_map
    
    def create_individual_hymn_pdf(self, hymn_num: str, pages: List[int]):
        """Create a PDF for a single hymn."""
        metadata = self.hymns_metadata.get(hymn_num, {})
        
        title = metadata.get('title', f'Hymn {hymn_num}')
        safe_title = re.sub(r'[^\w\s-]', '', title).strip()
        safe_title = re.sub(r'[-\s]+', '_', safe_title)[:50]  # Limit length
        
        filename = f"{hymn_num.zfill(3)}_{safe_title}.pdf"
        output_path = os.path.join(self.output_dir, filename)
        
        writer = PdfWriter()
        
        # Add pages for this hymn (only valid pages)
        valid_pages = [p for p in pages if 0 <= p < len(self.reader.pages)]
        for page_num in valid_pages:
            writer.add_page(self.reader.pages[page_num])
        
        if not valid_pages:
            print(f"Warning: No valid pages for hymn {hymn_num}")
            return None
        
        # Add metadata to PDF
        writer.add_metadata({
            '/Title': f"{hymn_num}. {title}",
            '/Subject': 'Gezangen Zions - Individual Hymn',
            '/Creator': 'Fast Gezangen Zions Hymn Splitter',
            '/Producer': 'PyPDF2'
        })
        
        # Write PDF
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        return output_path
    
    def split_hymns_batch(self, start_hymn: int = 1, max_hymns: int = 20):
        """Split hymns in batch mode using estimates."""
        print(f"Starting batch split for hymns {start_hymn} to {start_hymn + max_hymns - 1}...")
        
        # Get estimated mappings
        hymn_page_map = self.estimate_hymn_pages()
        
        # Process requested hymns
        created_files = []
        processed = 0
        
        for i in range(start_hymn, start_hymn + max_hymns):
            hymn_num = str(i)
            
            if hymn_num not in self.hymns_metadata:
                continue
                
            if hymn_num not in hymn_page_map:
                continue
            
            metadata = self.hymns_metadata[hymn_num]
            pages = hymn_page_map[hymn_num]
            
            print(f"Processing Hymn {hymn_num}: {metadata['title']}")
            print(f"  Estimated pages: {[p+1 for p in pages]}")
            
            output_path = self.create_individual_hymn_pdf(hymn_num, pages)
            if output_path:
                created_files.append(output_path)
                processed += 1
        
        print(f"\n✅ Successfully created {processed} individual hymn PDFs")
        print(f"Output directory: {self.output_dir}")
        
        return created_files

def main():
    parser = argparse.ArgumentParser(description='Fast split of Gezangen Zions PDF into individual hymns')
    parser.add_argument('--pdf', default='#Gezangen Zions.original.pdf', help='Input PDF file')
    parser.add_argument('--json', default='gezangen-zions.json', help='Hymn metadata JSON file')
    parser.add_argument('--output', default='individual_hymns', help='Output directory')
    parser.add_argument('--start', type=int, default=1, help='Starting hymn number')
    parser.add_argument('--count', type=int, default=20, help='Number of hymns to process')
    
    args = parser.parse_args()
    
    # Check if input files exist
    if not os.path.exists(args.pdf):
        print(f"Error: PDF file not found: {args.pdf}")
        return 1
        
    if not os.path.exists(args.json):
        print(f"Error: JSON file not found: {args.json}")
        return 1
    
    # Create splitter and run
    splitter = FastHymnSplitter(args.pdf, args.json, args.output)
    splitter.load_data()
    
    created_files = splitter.split_hymns_batch(args.start, args.count)
    
    print(f"\n🎵 Fast hymn splitting completed! Created {len(created_files)} files.")
    
    # Show sample of created files
    if created_files:
        print("\nSample of created files:")
        for f in created_files[:5]:
            size_kb = os.path.getsize(f) // 1024
            filename = os.path.basename(f)
            print(f"  {filename} ({size_kb} KB)")
    
    return 0

if __name__ == "__main__":
    exit(main())