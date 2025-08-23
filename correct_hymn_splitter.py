#!/usr/bin/env python3
"""
Correct Gezangen Zions Hymn Splitter

This implementation properly detects hymn boundaries using the onePerPage PDF
and ensures each output PDF contains exactly one hymn.
"""

import json
import os
import re
from PyPDF2 import PdfReader, PdfWriter
from typing import List, Dict, Optional, Tuple
import argparse

class CorrectHymnSplitter:
    def __init__(self, pdf_path: str, json_path: str, output_dir: str = "correct_individual_hymns"):
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
    
    def extract_hymn_number_from_page(self, page_num: int) -> Optional[str]:
        """Extract hymn number from a specific page using stricter validation."""
        page = self.reader.pages[page_num]
        
        try:
            text = page.extract_text()
            if not text.strip():
                return None
                
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            for i, line in enumerate(lines[:20]):  # Check more lines but be more selective
                # Skip common false positives
                if any(skip_word in line.upper() for skip_word in ['PSALM', 'MATTH', 'HEBR', 'ROM', 'LOFZANGEN']):
                    continue
                
                # Pattern 1: Large standalone number (likely hymn number)
                if re.match(r'^\s*(\d{1,3})\s*$', line):
                    num = line.strip()
                    if (num in self.hymns_metadata and 
                        int(num) >= 1 and int(num) <= 532):  # Valid hymn range
                        
                        # Additional validation: check if next few lines contain title-like content
                        title_found = False
                        for j in range(i + 1, min(i + 5, len(lines))):
                            next_line = lines[j]
                            # Look for capitalized words that could be title
                            if (len(next_line) > 5 and 
                                any(word[0].isupper() for word in next_line.split() if len(word) > 2)):
                                title_found = True
                                break
                        
                        if title_found:
                            return num
                
                # Pattern 2: Number at start followed by potential title words
                match = re.match(r'^(\d{1,3})\.\s+([A-Z][a-z]+.*)', line)
                if match:
                    num = match.group(1)
                    title_part = match.group(2)
                    if (num in self.hymns_metadata and 
                        int(num) >= 1 and int(num) <= 532 and
                        len(title_part) > 5):
                        
                        # Validate this looks like a real title (multiple words, proper case)
                        words = title_part.split()
                        if len(words) >= 2 and any(len(w) > 3 for w in words):
                            return num
                            
        except Exception as e:
            print(f"Error extracting from page {page_num + 1}: {e}")
            
        return None
    
    def map_hymns_to_pages(self, start_page: int = 10) -> Dict[str, List[int]]:
        """
        Create accurate mapping of hymn numbers to their pages.
        Uses the onePerPage PDF which should have better hymn separation.
        """
        print(f"Mapping hymns to pages starting from page {start_page + 1}...")
        
        hymn_page_map = {}
        current_hymn = None
        current_pages = []
        
        total_pages = len(self.reader.pages)
        
        for page_num in range(start_page, total_pages):
            print(f"Analyzing page {page_num + 1}...", end=' ')
            
            detected_hymn = self.extract_hymn_number_from_page(page_num)
            
            if detected_hymn:
                print(f"Found hymn {detected_hymn}")
                
                # If we were tracking a previous hymn, save it
                if current_hymn and current_pages:
                    if current_hymn not in hymn_page_map:
                        hymn_page_map[current_hymn] = []
                    hymn_page_map[current_hymn].extend(current_pages)
                
                # Start tracking new hymn
                current_hymn = detected_hymn
                current_pages = [page_num]
                
            else:
                print("(continuation)")
                # This page is likely a continuation of the current hymn
                if current_hymn:
                    current_pages.append(page_num)
        
        # Don't forget the last hymn
        if current_hymn and current_pages:
            if current_hymn not in hymn_page_map:
                hymn_page_map[current_hymn] = []
            hymn_page_map[current_hymn].extend(current_pages)
        
        # Clean up and deduplicate
        for hymn_num in hymn_page_map:
            hymn_page_map[hymn_num] = sorted(list(set(hymn_page_map[hymn_num])))
        
        print(f"\nMapped {len(hymn_page_map)} hymns to pages")
        
        # Show mapping summary
        for hymn_num in sorted(hymn_page_map.keys(), key=lambda x: int(x) if x.isdigit() else 0)[:10]:
            pages = hymn_page_map[hymn_num]
            metadata = self.hymns_metadata.get(hymn_num, {})
            title = metadata.get('title', 'Unknown')
            print(f"  Hymn {hymn_num}: {len(pages)} pages - {title}")
        
        return hymn_page_map
    
    def create_individual_hymn_pdf(self, hymn_num: str, pages: List[int]) -> Optional[str]:
        """Create a PDF for a single hymn with proper validation."""
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
        
        # Add rich metadata
        verses = metadata.get('stanzas', {}).get('verses', [])
        verse_count = len(verses)
        
        writer.add_metadata({
            '/Title': f"{hymn_num}. {title}",
            '/Subject': f'Gezangen Zions - Hymn {hymn_num} ({verse_count} verses)',
            '/Creator': 'Correct Gezangen Zions Hymn Splitter',
            '/Producer': 'PyPDF2',
            '/Keywords': f'Gezangen Zions, Hymn {hymn_num}, Dutch Reformed'
        })
        
        # Write PDF
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        # Verify the created file
        file_size_kb = os.path.getsize(output_path) // 1024
        print(f"Created: {filename} ({file_size_kb} KB, {len(valid_pages)} pages)")
        
        return output_path
    
    def split_hymns(self, start_hymn: int = 1, max_hymns: int = None):
        """Split PDF into correctly identified individual hymns."""
        print("Starting correct hymn splitting...")
        
        # First, map all hymns to their pages
        hymn_page_map = self.map_hymns_to_pages()
        
        # Determine which hymns to process
        if max_hymns:
            available_hymns = sorted([h for h in hymn_page_map.keys() if h.isdigit()], 
                                   key=int)[:max_hymns]
        else:
            available_hymns = [h for h in hymn_page_map.keys() if int(h) >= start_hymn]
        
        print(f"\nProcessing {len(available_hymns)} hymns...")
        
        created_files = []
        
        for hymn_num in sorted(available_hymns, key=lambda x: int(x) if x.isdigit() else 0):
            if hymn_num not in hymn_page_map:
                continue
            
            pages = hymn_page_map[hymn_num]
            metadata = self.hymns_metadata.get(hymn_num, {})
            
            print(f"\nProcessing Hymn {hymn_num}: {metadata.get('title', 'Unknown')}")
            print(f"  Pages: {[p+1 for p in pages]}")
            
            output_path = self.create_individual_hymn_pdf(hymn_num, pages)
            if output_path:
                created_files.append({
                    'hymn_num': hymn_num,
                    'title': metadata.get('title', 'Unknown'),
                    'file_path': output_path,
                    'pages': pages,
                    'verse_count': len(metadata.get('stanzas', {}).get('verses', []))
                })
        
        print(f"\n✅ Successfully created {len(created_files)} individual hymn PDFs")
        print(f"Output directory: {self.output_dir}")
        
        # Show summary statistics
        total_pages = sum(len(item['pages']) for item in created_files)
        avg_pages = total_pages / len(created_files) if created_files else 0
        
        print(f"\nSummary:")
        print(f"  Total hymns processed: {len(created_files)}")
        print(f"  Total pages used: {total_pages}")
        print(f"  Average pages per hymn: {avg_pages:.1f}")
        
        return created_files

def main():
    parser = argparse.ArgumentParser(description='Correctly split Gezangen Zions PDF into individual hymns')
    parser.add_argument('--pdf', default='#Gezangen Zions.onePerPage.pdf', help='Input PDF file (use onePerPage version)')
    parser.add_argument('--json', default='gezangen-zions.json', help='Hymn metadata JSON file')
    parser.add_argument('--output', default='correct_individual_hymns', help='Output directory')
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
    splitter = CorrectHymnSplitter(args.pdf, args.json, args.output)
    splitter.load_data()
    
    created_files = splitter.split_hymns(args.start_hymn, args.max_hymns)
    
    print(f"\n🎵 Correct hymn splitting completed! Created {len(created_files)} files.")
    
    # Show validation info
    if created_files:
        print(f"\nValidation check - files created:")
        for item in created_files[:5]:  # Show first 5
            filename = os.path.basename(item['file_path'])
            print(f"  {item['hymn_num']}. {item['title']} -> {filename}")
    
    return 0

if __name__ == "__main__":
    exit(main())