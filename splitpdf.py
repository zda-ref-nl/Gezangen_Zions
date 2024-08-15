from PyPDF2 import PdfReader, PdfWriter

def split_pdf(input_pdf, output_pdf):
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    for page in reader.pages:
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

    # Schrijf het gesplitste resultaat naar een nieuwe PDF
    with open(output_pdf, 'wb') as output_file:
        writer.write(output_file)

split_pdf("#Gezangen Zions.original.pdf", "corrected_output.pdf")
