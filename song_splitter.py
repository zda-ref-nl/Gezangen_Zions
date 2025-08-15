#!/usr/bin/env python3
import argparse
import re
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from pypdf import PdfReader, PdfWriter


def normalize_whitespace(text: str) -> str:
	return re.sub(r"\s+", " ", text).strip()


def remove_accents(text: str) -> str:
	# Convert to ASCII where possible, drop remaining combining marks
	nfkd = unicodedata.normalize("NFKD", text)
	return "".join(ch for ch in nfkd if not unicodedata.combining(ch))


def slugify(text: str, max_length: int = 80) -> str:
	text = remove_accents(text)
	text = text.lower()
	# Replace non-alphanumeric with hyphens
	text = re.sub(r"[^a-z0-9]+", "-", text)
	text = text.strip("-")
	if len(text) > max_length:
		text = text[:max_length].rstrip("-")
	return text or "untitled"


def extract_candidate_title_lines(page_text: str) -> List[str]:
	lines = [ln.strip() for ln in page_text.splitlines()]
	# Drop empty and boilerplate lines commonly seen on cover/foreword
	drop_patterns = [
		re.compile(r"^ge[z|s]angen zions$", re.I),
		re.compile(r"^voorwoord$", re.I),
		re.compile(r"^inhoud$", re.I),
		re.compile(r"^\d+$"),
	]
	candidates: List[str] = []
	for ln in lines:
		if not ln:
			continue
		if any(pat.search(ln) for pat in drop_patterns):
			continue
		# Prefer lines likely to be titles: relatively short, word-like, not a full paragraph
		if 3 <= len(ln) <= 80 and (" " in ln or len(ln) >= 5):
			candidates.append(ln)
	# De-duplicate while preserving order
	seen: set = set()
	unique: List[str] = []
	for c in candidates:
		key = c.lower()
		if key not in seen:
			seen.add(key)
			unique.append(c)
	return unique


def infer_title_from_text(page_text: Optional[str]) -> Optional[str]:
	if not page_text:
		return None
	text = normalize_whitespace(page_text)
	if not text:
		return None
	lines = extract_candidate_title_lines(page_text)
	if lines:
		return lines[0]
	# Fallback: first 8 words
	words = text.split()
	if not words:
		return None
	return " ".join(words[:8])


def ensure_unique_name(base_name: str, used: Dict[str, int]) -> str:
	count = used.get(base_name, 0)
	if count == 0:
		used[base_name] = 1
		return base_name
	count += 1
	used[base_name] = count
	return f"{base_name}-{count}"


def split_pdf_with_titles(input_pdf_path: str, output_dir_path: str, name_by_title: bool) -> List[Tuple[int, Path, str]]:
	input_path = Path(input_pdf_path)
	output_dir = Path(output_dir_path)
	output_dir.mkdir(parents=True, exist_ok=True)

	reader = PdfReader(str(input_path))
	used_names: Dict[str, int] = {}
	results: List[Tuple[int, Path, str]] = []

	for page_index in range(len(reader.pages)):
		page_num = page_index + 1
		page_text: Optional[str] = None
		try:
			page_text = reader.pages[page_index].extract_text() or ""
		except Exception:
			page_text = ""

		if name_by_title:
			title = infer_title_from_text(page_text) or f"page-{page_num:03d}"
			slug = slugify(title)
			base_name = f"{page_num:03d}-{slug}"
		else:
			base_name = f"page-{page_num:03d}"

		final_name = ensure_unique_name(base_name, used_names)
		output_file = output_dir / f"{final_name}.pdf"

		writer = PdfWriter()
		writer.add_page(reader.pages[page_index])
		with output_file.open("wb") as f_out:
			writer.write(f_out)

		results.append((page_num, output_file, page_text or ""))

	return results


def write_index_csv(index_path: Path, rows: List[Tuple[int, Path, str]]) -> None:
	with index_path.open("w", encoding="utf-8") as f:
		f.write("page,filename,title_snippet\n")
		for page_num, path, text in rows:
			first_line = (text.splitlines() or [""])[0].strip()
			first_line = first_line.replace("\t", " ").replace(",", " ")
			f.write(f"{page_num},{path.name},{first_line}\n")


def main() -> None:
	parser = argparse.ArgumentParser(description="Split a PDF into one PDF per page, optionally naming by detected title.")
	parser.add_argument("input", help="Path to input PDF file")
	parser.add_argument("output", help="Path to output directory")
	parser.add_argument("--name-by-title", action="store_true", help="Attempt to name files by a detected title on the page")
	parser.add_argument("--index-csv", default=None, help="Optional path to write an index CSV")
	args = parser.parse_args()

	rows = split_pdf_with_titles(args.input, args.output, name_by_title=args.name_by_title)
	if args.index_csv:
		write_index_csv(Path(args.index_csv), rows)

	print(f"Wrote {len(rows)} PDFs to {args.output}")
	if args.index_csv:
		print(f"Index: {args.index_csv}")


if __name__ == "__main__":
	main()