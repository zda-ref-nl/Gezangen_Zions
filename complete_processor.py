#!/usr/bin/env python3
"""
Complete Gezangen Zions Automation Tool

This comprehensive script can:
1. Split all hymns into individual PDFs
2. Add proper metadata to each PDF
3. Organize files by categories/topics
4. Generate an index of created files
"""

import json
import os
import re
from PyPDF2 import PdfReader, PdfWriter
from typing import List, Dict, Optional
import argparse
import csv

class GezangenZionsProcessor:
    def __init__(self, pdf_path: str, json_path: str, output_dir: str = "gezangen_zions_individual"):
        self.pdf_path = pdf_path
        self.json_path = json_path
        self.output_dir = output_dir
        self.reader = None
        self.hymns_metadata = {}
        self.topics = {}
        
    def load_data(self):
        """Load PDF and hymn metadata."""
        print("Loading PDF and metadata...")
        
        # Load PDF
        self.reader = PdfReader(self.pdf_path)
        print(f"PDF loaded: {len(self.reader.pages)} pages")
        
        # Load JSON metadata
        with open(self.json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Process hymns
        hymns = data.get('hymns', [])
        for hymn in hymns:
            self.hymns_metadata[hymn['num']] = hymn
        
        # Process topics
        topics = data.get('topics', [])
        for topic in topics:
            self.topics[topic['name']] = {
                'start': int(topic['start']),
                'end': int(topic['end'])
            }
        
        print(f"Metadata loaded: {len(self.hymns_metadata)} hymns, {len(self.topics)} topics")
        
        # Create output directories
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, 'by_topic'), exist_ok=True)
        
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

    def estimate_pages_per_hymn(self) -> Dict[str, List[int]]:
        """Systematically distribute pages based on hymn complexity."""
        total_pages = len(self.reader.pages)
        
        content_start_page = 10  # Skip title/index pages
        content_end_page = total_pages - 5  # Skip appendix pages
        content_pages = content_end_page - content_start_page
        
        print(f"Content pages: {content_start_page} to {content_end_page} ({content_pages} pages)")
        
        hymn_page_map = {}
        current_page = content_start_page
        
        # Process hymns in numerical order
        for i in range(1, len(self.hymns_metadata) + 1):
            hymn_num = str(i)
            if hymn_num not in self.hymns_metadata:
                continue
                
            # Calculate pages needed for this hymn
            pages_needed = self.calculate_hymn_complexity(hymn_num)
            
            # Ensure we don't go beyond available pages
            if current_page + pages_needed > content_end_page:
                pages_needed = max(1, content_end_page - current_page)
            
            if current_page < content_end_page:
                # Assign pages to this hymn
                pages = list(range(current_page, current_page + pages_needed))
                hymn_page_map[hymn_num] = pages
                current_page += pages_needed
            else:
                # No more pages available
                break
        
        print(f"Systematically mapped {len(hymn_page_map)} hymns to pages")
        return hymn_page_map
    
    def create_hymn_pdf(self, hymn_num: str, pages: List[int], add_to_topic_dir: bool = True):
        """Create a PDF for individual hymn with rich metadata."""
        metadata = self.hymns_metadata.get(hymn_num, {})
        
        title = metadata.get('title', f'Hymn {hymn_num}')
        safe_title = re.sub(r'[^\w\s-]', '', title).strip()
        safe_title = re.sub(r'[-\s]+', '_', safe_title)[:50]
        
        filename = f"{hymn_num.zfill(3)}_{safe_title}.pdf"
        main_output_path = os.path.join(self.output_dir, filename)
        
        # Create PDF writer
        writer = PdfWriter()
        
        # Add valid pages
        valid_pages = [p for p in pages if 0 <= p < len(self.reader.pages)]
        if not valid_pages:
            print(f"Warning: No valid pages for hymn {hymn_num}")
            return None
        
        for page_num in valid_pages:
            writer.add_page(self.reader.pages[page_num])
        
        # Add comprehensive metadata
        verses = metadata.get('stanzas', {}).get('verses', [])
        verse_count = len(verses)
        
        writer.add_metadata({
            '/Title': f"{hymn_num}. {title}",
            '/Subject': f'Gezangen Zions - Hymn {hymn_num} ({verse_count} verses)',
            '/Creator': 'Gezangen Zions Complete Processor',
            '/Producer': 'PyPDF2',
            '/Keywords': f'Gezangen Zions, Hymn {hymn_num}, Dutch Reformed'
        })
        
        # Write main PDF
        with open(main_output_path, 'wb') as output_file:
            writer.write(output_file)
        
        # Also copy to topic directory if requested
        if add_to_topic_dir:
            topic_name = self.find_hymn_topic(int(hymn_num))
            if topic_name:
                topic_dir = os.path.join(self.output_dir, 'by_topic', self.sanitize_filename(topic_name))
                os.makedirs(topic_dir, exist_ok=True)
                topic_path = os.path.join(topic_dir, filename)
                
                with open(topic_path, 'wb') as output_file:
                    writer.write(output_file)
        
        return main_output_path
    
    def find_hymn_topic(self, hymn_num: int) -> Optional[str]:
        """Find which topic category a hymn belongs to."""
        for topic_name, range_info in self.topics.items():
            if range_info['start'] <= hymn_num <= range_info['end']:
                return topic_name
        return None
    
    def sanitize_filename(self, name: str) -> str:
        """Create safe filename from topic name."""
        safe = re.sub(r'[^\w\s-]', '', name).strip()
        safe = re.sub(r'[-\s]+', '_', safe)
        return safe[:40]  # Limit length
    
    def process_all_hymns(self, max_hymns: int = None):
        """Process all hymns into individual PDFs."""
        print("Processing all hymns...")
        
        hymn_page_map = self.estimate_pages_per_hymn()
        
        # Determine range
        if max_hymns:
            hymn_nums = [str(i) for i in range(1, min(max_hymns + 1, len(self.hymns_metadata) + 1))]
        else:
            hymn_nums = [str(i) for i in range(1, len(self.hymns_metadata) + 1)]
        
        hymn_nums = [n for n in hymn_nums if n in hymn_page_map]
        
        print(f"Processing {len(hymn_nums)} hymns...")
        
        created_files = []
        
        for hymn_num in hymn_nums:
            if hymn_num not in self.hymns_metadata:
                continue
                
            metadata = self.hymns_metadata[hymn_num]
            pages = hymn_page_map[hymn_num]
            
            print(f"Processing Hymn {hymn_num}: {metadata['title']}")
            
            output_path = self.create_hymn_pdf(hymn_num, pages)
            if output_path:
                created_files.append({
                    'hymn_num': hymn_num,
                    'title': metadata['title'],
                    'file_path': output_path,
                    'pages': pages,
                    'topic': self.find_hymn_topic(int(hymn_num)),
                    'verse_count': len(metadata.get('stanzas', {}).get('verses', []))
                })
        
        self.generate_index(created_files)
        
        print(f"\n✅ Successfully processed {len(created_files)} hymns")
        print(f"Main output directory: {self.output_dir}")
        print(f"Topic-organized files: {self.output_dir}/by_topic/")
        
        return created_files
    
    def generate_index(self, created_files: List[Dict]):
        """Generate index files for the created hymns."""
        print("Generating index files...")
        
        # Generate CSV index
        csv_path = os.path.join(self.output_dir, 'hymn_index.csv')
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['hymn_num', 'title', 'filename', 'topic', 'verse_count', 'estimated_pages']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for item in created_files:
                writer.writerow({
                    'hymn_num': item['hymn_num'],
                    'title': item['title'],
                    'filename': os.path.basename(item['file_path']),
                    'topic': item['topic'] or 'Unknown',
                    'verse_count': item['verse_count'],
                    'estimated_pages': len(item['pages'])
                })
        
        # Generate HTML index
        html_path = os.path.join(self.output_dir, 'index.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(self.generate_html_index(created_files))
        
        print(f"Created index files: {csv_path}, {html_path}")
    
    def generate_html_index(self, created_files: List[Dict]) -> str:
        """Generate HTML index of all hymns."""
        html = '''<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gezangen Zions - Individual Hymns</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        .topic-section { margin: 20px 0; }
        h1 { color: #333; }
        h2 { color: #666; margin-top: 30px; }
    </style>
</head>
<body>
    <h1>🎵 Gezangen Zions - Individual Hymn PDFs</h1>
    <p>Generated individual PDF files for each hymn in the Gezangen Zions songbook.</p>
    
    <h2>📊 Statistics</h2>
    <ul>
        <li>Total Hymns: ''' + str(len(created_files)) + '''</li>
        <li>Topics: ''' + str(len(self.topics)) + '''</li>
        <li>Generated: ''' + str(len(created_files)) + ''' PDF files</li>
    </ul>
    
    <h2>📖 All Hymns</h2>
    <table>
        <thead>
            <tr>
                <th>Hymn #</th>
                <th>Title</th>
                <th>Topic</th>
                <th>Verses</th>
                <th>File</th>
            </tr>
        </thead>
        <tbody>'''
        
        for item in created_files:
            filename = os.path.basename(item['file_path'])
            html += f'''
            <tr>
                <td>{item['hymn_num']}</td>
                <td>{item['title']}</td>
                <td>{item['topic'] or 'Unknown'}</td>
                <td>{item['verse_count']}</td>
                <td><a href="{filename}">{filename}</a></td>
            </tr>'''
        
        html += '''
        </tbody>
    </table>
    
    <h2>📁 Organization</h2>
    <p>Files are organized in two ways:</p>
    <ul>
        <li><strong>Main directory:</strong> All hymns numbered sequentially</li>
        <li><strong>by_topic/ directory:</strong> Hymns grouped by theological topics</li>
    </ul>
    
    <hr>
    <p><small>Generated by Gezangen Zions Complete Processor</small></p>
</body>
</html>'''
        
        return html

def main():
    parser = argparse.ArgumentParser(description='Complete Gezangen Zions hymn processor')
    parser.add_argument('--pdf', default='#Gezangen Zions.original.pdf', help='Input PDF file')
    parser.add_argument('--json', default='gezangen-zions.json', help='Hymn metadata JSON file')
    parser.add_argument('--output', default='gezangen_zions_individual', help='Output directory')
    parser.add_argument('--max-hymns', type=int, help='Maximum number of hymns to process (for testing)')
    parser.add_argument('--quiet', action='store_true', help='Reduce output verbosity')
    
    args = parser.parse_args()
    
    # Check input files
    if not os.path.exists(args.pdf):
        print(f"Error: PDF file not found: {args.pdf}")
        return 1
        
    if not os.path.exists(args.json):
        print(f"Error: JSON file not found: {args.json}")
        return 1
    
    # Create processor and run
    processor = GezangenZionsProcessor(args.pdf, args.json, args.output)
    processor.load_data()
    
    created_files = processor.process_all_hymns(args.max_hymns)
    
    if not args.quiet:
        print(f"\n🎵 Complete processing finished!")
        print(f"✅ Created {len(created_files)} individual hymn PDFs")
        print(f"📁 Main directory: {args.output}")
        print(f"📂 By topic: {args.output}/by_topic/")
        print(f"📋 Index files: hymn_index.csv, index.html")
        
        # Show topic summary
        topics = {}
        for item in created_files:
            topic = item['topic'] or 'Unknown'
            topics[topic] = topics.get(topic, 0) + 1
        
        print(f"\n📊 Hymns by topic:")
        for topic, count in sorted(topics.items()):
            print(f"  {topic}: {count} hymns")
    
    return 0

if __name__ == "__main__":
    exit(main())