import pdfplumber
from io import BytesIO


def extract_text_from_pdf(file_bytes: bytes) -> tuple[str, list[str]]:
    """Extract text from a PDF file.
    
    Returns:
        Tuple of (full_text, list_of_pages)
    """
    pages = []
    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                pages.append(extracted)

    full_text = "\n".join(pages)
    return full_text, pages
