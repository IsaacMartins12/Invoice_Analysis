from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.models.invoice import Invoice
from app.models.transaction import Transaction
from app.services.auth import get_current_user
from app.services.pdf import extract_text_from_pdf
from app.services.extractor import extract_transactions
from app.services.llm import categorize_transactions

router = APIRouter(prefix="/api/invoices", tags=["invoices"])


class TransactionOut(BaseModel):
    id: int
    date: str
    description: str
    amount: float
    category: str

    class Config:
        from_attributes = True


class InvoiceOut(BaseModel):
    id: int
    bank: str | None
    month: int
    year: int
    file_name: str
    uploaded_at: str
    transactions: list[TransactionOut] = []

    class Config:
        from_attributes = True

    @classmethod
    def from_invoice(cls, invoice):
        return cls(
            id=invoice.id,
            bank=invoice.bank,
            month=invoice.month,
            year=invoice.year,
            file_name=invoice.file_name,
            uploaded_at=invoice.uploaded_at.isoformat() if invoice.uploaded_at else "",
            transactions=invoice.transactions,
        )


class InvoiceListItem(BaseModel):
    id: int
    bank: str | None
    month: int
    year: int
    file_name: str
    uploaded_at: str
    total_amount: float
    transaction_count: int


@router.post("/upload", response_model=InvoiceOut)
async def upload_invoice(
    file: UploadFile = File(...),
    month: int = Form(...),
    year: int = Form(...),
    bank: str = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a PDF invoice, extract transactions via LLM, and save to database."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    # Read PDF and extract text
    file_bytes = await file.read()
    pdf_text, pages = extract_text_from_pdf(file_bytes)

    if not pdf_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")

    # Generate content hash to detect exact duplicates regardless of month/year chosen
    import hashlib
    content_hash = hashlib.sha256(pdf_text.encode()).hexdigest()

    # Check if this exact PDF was already uploaded by this user
    existing_hash = (
        db.query(Invoice)
        .filter(
            Invoice.user_id == current_user.id,
            Invoice.content_hash == content_hash,
        )
        .first()
    )
    if existing_hash:
        raise HTTPException(
            status_code=409,
            detail=f"Esta fatura já foi enviada anteriormente ({existing_hash.month:02d}/{existing_hash.year})."
        )

    # Step 1: Extract transactions with regex (100% accurate)
    raw_transactions, detected_bank = extract_transactions(pdf_text)

    if not raw_transactions:
        raise HTTPException(
            status_code=422,
            detail="No transactions found. Bank not supported or unrecognized format."
        )

    # Use detected bank if user didn't provide one
    invoice_bank = bank or detected_bank

    # Check for duplicate invoice (same user + bank + month + year)
    existing = (
        db.query(Invoice)
        .filter(
            Invoice.user_id == current_user.id,
            Invoice.month == month,
            Invoice.year == year,
            Invoice.bank == invoice_bank,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Já existe uma fatura do {invoice_bank} de {month:02d}/{year}. Exclua a anterior se quiser substituir."
        )

    # Step 2: Categorize with LLM (or fallback to rules)
    categorized = categorize_transactions(raw_transactions)

    if not categorized:
        raise HTTPException(status_code=422, detail="No transactions found in invoice")

    # Save invoice
    invoice = Invoice(
        user_id=current_user.id,
        bank=invoice_bank,
        month=month,
        year=year,
        file_name=file.filename,
        content_hash=content_hash,
    )
    db.add(invoice)
    db.flush()

    # Save transactions
    for txn in categorized:
        transaction = Transaction(
            invoice_id=invoice.id,
            date=txn.get("date", ""),
            description=txn.get("description", ""),
            amount=txn.get("amount", 0),
            category=txn.get("category", "Outros"),
        )
        db.add(transaction)

    db.commit()
    db.refresh(invoice)
    return InvoiceOut.from_invoice(invoice)


@router.get("/", response_model=list[InvoiceListItem])
def list_invoices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all invoices for the current user."""
    invoices = (
        db.query(Invoice)
        .filter(Invoice.user_id == current_user.id)
        .order_by(Invoice.year.desc(), Invoice.month.desc())
        .all()
    )

    result = []
    for inv in invoices:
        total = sum(t.amount for t in inv.transactions)
        result.append(
            InvoiceListItem(
                id=inv.id,
                bank=inv.bank,
                month=inv.month,
                year=inv.year,
                file_name=inv.file_name,
                uploaded_at=inv.uploaded_at.isoformat(),
                total_amount=total,
                transaction_count=len(inv.transactions),
            )
        )
    return result


@router.get("/{invoice_id}", response_model=InvoiceOut)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific invoice with all transactions."""
    invoice = (
        db.query(Invoice)
        .filter(Invoice.id == invoice_id, Invoice.user_id == current_user.id)
        .first()
    )
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    return InvoiceOut.from_invoice(invoice)


@router.delete("/{invoice_id}")
def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an invoice and its transactions."""
    invoice = (
        db.query(Invoice)
        .filter(Invoice.id == invoice_id, Invoice.user_id == current_user.id)
        .first()
    )
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    db.delete(invoice)
    db.commit()
    return {"message": "Invoice deleted"}
