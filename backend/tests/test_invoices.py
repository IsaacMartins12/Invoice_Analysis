"""Tests for invoice upload and management endpoints."""

import os


def _get_bradesco_pdf():
    """Get the Bradesco test PDF if available."""
    path = os.path.join(os.path.dirname(__file__), "..", "..", "faturas", "Bradesco_Fatura.pdf")
    if os.path.exists(path):
        with open(path, "rb") as f:
            return f.read()
    return None


def _get_nubank_pdf():
    """Get the Nubank test PDF if available."""
    path = os.path.join(os.path.dirname(__file__), "..", "..", "faturas", "Nubank_2026-03-03.pdf")
    if os.path.exists(path):
        with open(path, "rb") as f:
            return f.read()
    return None


def test_upload_invalid_file_extension(client, auth_headers):
    """Should reject non-PDF files."""
    response = client.post(
        "/api/invoices/upload",
        files={"file": ("test.txt", b"hello", "text/plain")},
        data={"month": "1", "year": "2026"},
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_upload_fake_pdf(client, auth_headers):
    """Should reject file that has .pdf extension but isn't actually a PDF."""
    response = client.post(
        "/api/invoices/upload",
        files={"file": ("fake.pdf", b"not a real pdf content", "application/pdf")},
        data={"month": "1", "year": "2026"},
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert "PDF válido" in response.json()["detail"]


def test_upload_without_auth(client):
    """Should reject upload without authentication."""
    response = client.post(
        "/api/invoices/upload",
        files={"file": ("test.pdf", b"%PDF-1.4 content", "application/pdf")},
        data={"month": "1", "year": "2026"},
    )
    assert response.status_code == 401


def test_list_invoices_empty(client, auth_headers):
    """Should return empty list for new user."""
    response = client.get("/api/invoices/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_delete_nonexistent_invoice(client, auth_headers):
    """Should return 404 for nonexistent invoice."""
    response = client.delete("/api/invoices/999", headers=auth_headers)
    assert response.status_code == 404
