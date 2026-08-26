import pdfplumber
from io import BytesIO


class InvalidPDFError(Exception):
    """Raised when file is not a valid PDF."""
    pass


class PasswordProtectedPDFError(Exception):
    """Raised when PDF is password protected."""
    pass


def validate_pdf(file_bytes: bytes) -> None:
    """Validate that the file is actually a PDF."""
    # PDF files start with %PDF magic bytes
    if not file_bytes[:5].startswith(b"%PDF-"):
        raise InvalidPDFError(
            "O arquivo enviado não é um PDF válido. "
            "Verifique se selecionou o arquivo correto."
        )


def extract_text_from_pdf(file_bytes: bytes) -> tuple[str, list[str]]:
    """Extract text from a PDF file.
    
    Returns:
        Tuple of (full_text, list_of_pages)
    
    Raises:
        InvalidPDFError: If file is not a valid PDF
        PasswordProtectedPDFError: If PDF is password protected
    """
    validate_pdf(file_bytes)

    try:
        pages = []
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    pages.append(extracted)

        full_text = "\n".join(pages)
        return full_text, pages

    except Exception as e:
        error_msg = str(e).lower()
        if "password" in error_msg or "encrypted" in error_msg:
            raise PasswordProtectedPDFError(
                "Este PDF está protegido por senha. "
                "Abra o PDF no seu computador, remova a senha e tente novamente."
            )
        raise InvalidPDFError(f"Erro ao processar o PDF: {e}")
