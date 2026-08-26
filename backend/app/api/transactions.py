from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.models.invoice import Invoice
from app.models.transaction import Transaction
from app.services.auth import get_current_user

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


class TransactionWithInvoice(BaseModel):
    id: int
    date: str
    description: str
    amount: float
    category: str
    invoice_month: int
    invoice_year: int
    invoice_bank: str | None

    class Config:
        from_attributes = True


@router.get("/", response_model=list[TransactionWithInvoice])
def list_transactions(
    category: str = Query(None),
    month: int = Query(None),
    year: int = Query(None),
    bank: str = Query(None),
    search: str = Query(None),
    date_from: str = Query(None),
    date_to: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all transactions with optional filters."""
    query = (
        db.query(Transaction)
        .join(Invoice)
        .filter(Invoice.user_id == current_user.id)
    )

    if category:
        query = query.filter(Transaction.category == category)
    if month:
        query = query.filter(Invoice.month == month)
    if year:
        query = query.filter(Invoice.year == year)
    if bank:
        query = query.filter(Invoice.bank.ilike(f"%{bank}%"))
    if search:
        query = query.filter(Transaction.description.ilike(f"%{search}%"))
    if date_from:
        query = query.filter(Transaction.date >= date_from)
    if date_to:
        query = query.filter(Transaction.date <= date_to)

    query = query.order_by(Invoice.year.desc(), Invoice.month.desc(), Transaction.id)
    results = query.all()

    return [
        TransactionWithInvoice(
            id=t.id,
            date=t.date,
            description=t.description,
            amount=t.amount,
            category=t.category,
            invoice_month=t.invoice.month,
            invoice_year=t.invoice.year,
            invoice_bank=t.invoice.bank,
        )
        for t in results
    ]


@router.get("/categories")
def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all categories with totals across all invoices."""
    transactions = (
        db.query(Transaction)
        .join(Invoice)
        .filter(Invoice.user_id == current_user.id)
        .all()
    )

    categories = {}
    for t in transactions:
        if t.category not in categories:
            categories[t.category] = {"total": 0, "count": 0, "months": {}}
        categories[t.category]["total"] += t.amount
        categories[t.category]["count"] += 1

        month_key = f"{t.invoice.year}-{t.invoice.month:02d}"
        if month_key not in categories[t.category]["months"]:
            categories[t.category]["months"][month_key] = 0
        categories[t.category]["months"][month_key] += t.amount

    result = []
    for name, data in sorted(categories.items(), key=lambda x: x[1]["total"], reverse=True):
        result.append({
            "name": name,
            "total": round(data["total"], 2),
            "count": data["count"],
            "months": {k: round(v, 2) for k, v in sorted(data["months"].items())},
        })

    return result


class UpdateTransactionCategory(BaseModel):
    category: str


@router.put("/{transaction_id}/category")
def update_transaction_category(
    transaction_id: int,
    data: UpdateTransactionCategory,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update the category of a specific transaction."""
    transaction = (
        db.query(Transaction)
        .join(Invoice)
        .filter(Transaction.id == transaction_id, Invoice.user_id == current_user.id)
        .first()
    )
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    transaction.category = data.category
    db.commit()
    return {"message": "Category updated"}
