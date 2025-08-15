#!/usr/bin/env python3
import argparse
from pathlib import Path
from pypdf import PdfReader, PdfWriter


def split_pdf_to_pages(input_pdf_path: str, output_dir_path: str) -> None:
	input_path = Path(input_pdf_path)
	output_dir = Path(output_dir_path)
	output_dir.mkdir(parents=True, exist_ok=True)

	reader = PdfReader(str(input_path))
	for page_index in range(len(reader.pages)):
		writer = PdfWriter()
		writer.add_page(reader.pages[page_index])
		output_file = output_dir / f"page_{page_index + 1:03d}.pdf"
		with output_file.open("wb") as f_out:
			writer.write(f_out)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Split a PDF into individual page PDFs")
	parser.add_argument("input", help="Path to input PDF file")
	parser.add_argument("output", help="Path to output directory")
	args = parser.parse_args()

	split_pdf_to_pages(args.input, args.output)