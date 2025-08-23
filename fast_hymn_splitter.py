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
        """Estimate hymn distribution based on known patterns."""
        total_pages = len(self.reader.pages)
        content_pages = total_pages - 15  # Assume ~15 pages are title/index etc.
        total_hymns = len(self.hymns_metadata)
        
        # Rough estimate: content_pages / total_hymns pages per hymn on average
        pages_per_hymn = max(1, content_pages // total_hymns)
        
        print(f"Estimating {pages_per_hymn} pages per hymn on average")
        
        # Create estimated mapping
        hymn_page_map = {}
        current_page = 10  # Start after title pages
        
        for i in range(1, min(total_hymns + 1, 101)):  # Process first 100 hymns
            hymn_num = str(i)
            if hymn_num in self.hymns_metadata:
                # Estimate 1-3 pages per hymn based on content
                metadata = self.hymns_metadata[hymn_num]
                verses = metadata.get('stanzas', {}).get('verses', [])
                refrain = metadata.get('stanzas', {}).get('refrain', [])
                
                # Estimate pages needed based on verse count
                verse_count = len(verses)
                has_refrain = len(refrain) > 0
                
                if verse_count <= 3:
                    pages_needed = 1
                elif verse_count <= 6:
                    pages_needed = 2
                else:
                    pages_needed = 3
                
                # Add extra page for refrain or if it's a longer hymn
                if has_refrain or verse_count > 4:
                    pages_needed = min(pages_needed + 1, 3)
                
                # Assign pages
                pages = list(range(current_page, current_page + pages_needed))
                hymn_page_map[hymn_num] = pages
                current_page += pages_needed
                
                if current_page >= total_pages:
                    break
        
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