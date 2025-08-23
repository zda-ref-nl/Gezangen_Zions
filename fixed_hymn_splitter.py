#!/usr/bin/env python3
"""
Fixed Gezangen Zions Hymn Splitter

This implementation uses systematic page allocation based on hymn complexity
instead of trying to detect boundaries from unreliable text extraction.
"""

import json
import os
import re
from PyPDF2 import PdfReader, PdfWriter
from typing import List, Dict, Optional
import argparse

class FixedHymnSplitter:
    def __init__(self, pdf_path: str, json_path: str, output_dir: str = "fixed_individual_hymns"):
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
        
        # Load JSON metadata
        with open(self.json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Process hymns into lookup dictionary
        hymns = data.get('hymns', [])
        for hymn in hymns:
            self.hymns_metadata[hymn['num']] = hymn
        
        print(f"Metadata loaded: {len(self.hymns_metadata)} hymns")
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
    
    def calculate_hymn_complexity(self, hymn_num: str) -> int:
        """Calculate how many pages a hymn likely needs based on its content."""
        if hymn_num not in self.hymns_metadata:
            return 1
            
        metadata = self.hymns_metadata[hymn_num]
        stanzas = metadata.get('stanzas', {})
        verses = stanzas.get('verses', [])
        refrain = stanzas.get('refrain', [])
        
        # Calculate total text lines
        verse_lines = sum(len(verse) for verse in verses)
        refrain_lines = len(refrain) if refrain else 0
        
        # Estimate total content (refrain typically repeats after each verse)
        total_lines = verse_lines
        if refrain_lines > 0:
            total_lines += refrain_lines * max(1, len(verses) // 2)
        
        # Convert to estimated pages (assuming ~20-25 lines per page including music notation)
        if total_lines <= 18:
            return 1  # Short hymn, likely fits on one page
        elif total_lines <= 40:
            return 2  # Medium hymn
        else:
            return 3  # Long hymn, max 3 pages
    
    def create_systematic_page_mapping(self, start_page: int = 10, end_page: int = None) -> Dict[str, List[int]]:
        """Create systematic page mapping based on hymn complexity."""
        if end_page is None:
            end_page = len(self.reader.pages) - 5  # Leave some pages for appendix
        
        available_pages = end_page - start_page
        total_hymns = len([h for h in self.hymns_metadata.keys() if h.isdigit()])
        
        print(f"Distributing {available_pages} pages among {total_hymns} hymns")
        print(f"Average pages per hymn: {available_pages / total_hymns:.1f}")
        
        hymn_page_map = {}
        current_page = start_page
        
        # Process hymns in numerical order
        for i in range(1, total_hymns + 1):
            hymn_num = str(i)
            if hymn_num not in self.hymns_metadata:
                continue
            
            # Calculate pages needed for this hymn
            pages_needed = self.calculate_hymn_complexity(hymn_num)
            
            # Ensure we don't go beyond available pages
            if current_page + pages_needed > end_page:
                pages_needed = max(1, end_page - current_page)
            
            if current_page < end_page:
                # Assign pages to this hymn
                pages = list(range(current_page, current_page + pages_needed))
                hymn_page_map[hymn_num] = pages
                current_page += pages_needed
            else:
                # No more pages available
                break
        
        print(f"Mapped {len(hymn_page_map)} hymns to pages")
        return hymn_page_map
    
    def create_individual_hymn_pdf(self, hymn_num: str, pages: List[int]) -> Optional[str]:
        """Create a PDF for a single hymn."""
        metadata = self.hymns_metadata.get(hymn_num, {})
        
        title = metadata.get('title', f'Hymn {hymn_num}')
        safe_title = re.sub(r'[^\w\s-]', '', title).strip()
        safe_title = re.sub(r'[-\s]+', '_', safe_title)[:50]
        
        filename = f"{hymn_num.zfill(3)}_{safe_title}.pdf"
        output_path = os.path.join(self.output_dir, filename)
        
        # Validate pages exist
        valid_pages = [p for p in pages if 0 <= p < len(self.reader.pages)]
        if not valid_pages:
            print(f"Warning: No valid pages for hymn {hymn_num}")
            return None
        
        writer = PdfWriter()
        
        # Add pages for this hymn
        for page_num in valid_pages:
            writer.add_page(self.reader.pages[page_num])
        
        # Add metadata
        verses = metadata.get('stanzas', {}).get('verses', [])
        verse_count = len(verses)
        
        writer.add_metadata({
            '/Title': f"{hymn_num}. {title}",
            '/Subject': f'Gezangen Zions - Hymn {hymn_num} ({verse_count} verses)',
            '/Creator': 'Fixed Gezangen Zions Hymn Splitter',
            '/Producer': 'PyPDF2',
            '/Keywords': f'Gezangen Zions, Hymn {hymn_num}, Dutch Reformed'
        })
        
        # Write PDF
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        # Show info
        file_size_kb = os.path.getsize(output_path) // 1024
        print(f"Created: {filename} ({file_size_kb} KB, {len(valid_pages)} pages)")
        
        return output_path
    
    def split_hymns(self, start_hymn: int = 1, max_hymns: int = None):
        """Split PDF using systematic page allocation."""
        print("Starting fixed hymn splitting...")
        
        # Create systematic page mapping
        hymn_page_map = self.create_systematic_page_mapping()
        
        # Determine which hymns to process
        if max_hymns:
            hymn_numbers = [str(i) for i in range(start_hymn, start_hymn + max_hymns)]
        else:
            hymn_numbers = [h for h in hymn_page_map.keys() if int(h) >= start_hymn]
        
        hymn_numbers = [h for h in hymn_numbers if h in hymn_page_map]
        
        print(f"Processing {len(hymn_numbers)} hymns...")
        
        created_files = []
        
        for hymn_num in sorted(hymn_numbers, key=int):
            if hymn_num not in hymn_page_map:
                continue
            
            pages = hymn_page_map[hymn_num]
            metadata = self.hymns_metadata.get(hymn_num, {})
            
            title = metadata.get('title', 'Unknown')
            verse_count = len(metadata.get('stanzas', {}).get('verses', []))
            
            print(f"\nProcessing Hymn {hymn_num}: {title}")
            print(f"  Verses: {verse_count}, Estimated pages: {len(pages)}")
            print(f"  Page range: {pages[0]+1}-{pages[-1]+1}")
            
            output_path = self.create_individual_hymn_pdf(hymn_num, pages)
            if output_path:
                created_files.append({
                    'hymn_num': hymn_num,
                    'title': title,
                    'file_path': output_path,
                    'pages': pages,
                    'verse_count': verse_count
                })
        
        print(f"\n✅ Successfully created {len(created_files)} individual hymn PDFs")
        print(f"Output directory: {self.output_dir}")
        
        # Show summary statistics
        if created_files:
            total_pages = sum(len(item['pages']) for item in created_files)
            avg_pages = total_pages / len(created_files)
            
            print(f"\nSummary:")
            print(f"  Total hymns processed: {len(created_files)}")
            print(f"  Total pages used: {total_pages}")
            print(f"  Average pages per hymn: {avg_pages:.1f}")
            
            # Show page distribution
            page_counts = {}
            for item in created_files:
                count = len(item['pages'])
                page_counts[count] = page_counts.get(count, 0) + 1
            
            print(f"  Page distribution:")
            for pages, hymn_count in sorted(page_counts.items()):
                print(f"    {hymn_count} hymns with {pages} page(s)")
        
        return created_files

def main():
    parser = argparse.ArgumentParser(description='Fixed systematic splitting of Gezangen Zions PDF')
    parser.add_argument('--pdf', default='#Gezangen Zions.original.pdf', help='Input PDF file')
    parser.add_argument('--json', default='gezangen-zions.json', help='Hymn metadata JSON file')
    parser.add_argument('--output', default='fixed_individual_hymns', help='Output directory')
    parser.add_argument('--start-hymn', type=int, default=1, help='Starting hymn number')
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
    splitter = FixedHymnSplitter(args.pdf, args.json, args.output)
    splitter.load_data()
    
    created_files = splitter.split_hymns(args.start_hymn, args.max_hymns)
    
    print(f"\n🎵 Fixed hymn splitting completed! Created {len(created_files)} files.")
    
    return 0

if __name__ == "__main__":
    exit(main())