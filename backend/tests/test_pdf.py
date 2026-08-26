"""Tests for PDF validation service."""

import pytest
from app.services.pdf import validate_pdf, InvalidPDFError


def test_valid_pdf_magic_bytes():
    """Should not raise for valid PDF header."""
    fake_pdf = b"%PDF-1.4 some content here"
    validate_pdf(fake_pdf)  # Should not raise


def test_invalid_file_not_pdf():
    """Should raise for non-PDF file."""
    text_file = b"This is just a text file renamed to .pdf"
    with pytest.raises(InvalidPDFError):
        validate_pdf(text_file)


def test_empty_file():
    """Should raise for empty file."""
    with pytest.raises(InvalidPDFError):
        validate_pdf(b"")


def test_image_file():
    """Should raise for image file (PNG header)."""
    png_header = b"\x89PNG\r\n\x1a\n"
    with pytest.raises(InvalidPDFError):
        validate_pdf(png_header)
