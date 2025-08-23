#!/usr/bin/env python3
"""
Original splitpdf.py - Left/Right Page Splitting

This script splits each page of a PDF horizontally into left and right halves.
It was the original approach before the advanced hymn-based splitting.

For individual hymn splitting, use:
- complete_processor.py (recommended)
- fast_hymn_splitter.py (for testing)
"""

from PyPDF2 import PdfReader, PdfWriter
import argparse

def split_pdf_left_right(input_pdf, output_pdf):
    """Split each page horizontally into left and right halves."""
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    print(f"Processing {len(reader.pages)} pages...")

    for i, page in enumerate(reader.pages):
        width = page.mediabox.upper_right[0]  # Breedte van de pagina
        height = page.mediabox.upper_right[1]  # Hoogte van de pagina

        # Linkerhelft van de pagina
        left_page = PdfWriter()
        left_page.add_page(page)
        left_page.pages[0].mediabox.upper_right = (width / 2, height)
        writer.add_page(left_page.pages[0])

        # Rechterhelft van de pagina
        right_page = PdfWriter()
        right_page.add_page(page)
        right_page.pages[0].mediabox.upper_left = (width / 2, height)
        writer.add_page(right_page.pages[0])
        
        if (i + 1) % 10 == 0:
            print(f"Processed {i + 1} pages...")

    # Schrijf het gesplitste resultaat naar een nieuwe PDF
    with open(output_pdf, 'wb') as output_file:
        writer.write(output_file)
    
    print(f"✅ Created: {output_pdf}")
    return output_pdf

def main():
    parser = argparse.ArgumentParser(description='Split PDF pages left/right')
    parser.add_argument('--input', default='#Gezangen Zions.original.pdf', help='Input PDF file')
    parser.add_argument('--output', default='corrected_output.pdf', help='Output PDF file')
    
    args = parser.parse_args()
    
    print("📄 PDF Left/Right Page Splitter")
    print("=" * 40)
    print(f"Input: {args.input}")
    print(f"Output: {args.output}")
    print()
    
    result = split_pdf_left_right(args.input, args.output)
    
    print(f"\n✅ Page splitting completed!")
    print(f"💡 For individual hymn splitting, use complete_processor.py instead")
    
    return 0

if __name__ == "__main__":
    # Run main function when called directly
    exit(main())

# Legacy compatibility - run with original parameters if imported
if __name__ != "__main__":
    split_pdf_left_right("#Gezangen Zions.original.pdf", "corrected_output.pdf")
