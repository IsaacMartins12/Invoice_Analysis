from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.user import User
from app.models.invoice import Invoice
from app.models.transaction import Transaction
from app.services.auth import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary")
def get_summary(
    month: int = Query(None),
    year: int = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get spending summary for the user, optionally filtered by month/year."""
    query = (
        db.query(Transaction)
        .join(Invoice)
        .filter(Invoice.user_id == current_user.id)
    )

    if month and year:
        query = query.filter(Invoice.month == month, Invoice.year == year)
    elif year:
        query = query.filter(Invoice.year == year)

    transactions = query.all()

    if not transactions:
        return {
            "total_spending": 0,
            "transaction_count": 0,
            "by_category": {},
            "by_month": {},
        }

    # By category
    by_category = {}
    for txn in transactions:
        cat = txn.category
        if cat not in by_category:
            by_category[cat] = {"total": 0, "count": 0}
        by_category[cat]["total"] += txn.amount
        by_category[cat]["count"] += 1

    # By month (for evolution chart)
    by_month = {}
    for txn in transactions:
        inv = txn.invoice
        key = f"{inv.year}-{inv.month:02d}"
        if key not in by_month:
            by_month[key] = 0
        by_month[key] += txn.amount

    total_spending = sum(t.amount for t in transactions)

    return {
        "total_spending": round(total_spending, 2),
        "transaction_count": len(transactions),
        "by_category": {
            k: {"total": round(v["total"], 2), "count": v["count"]}
            for k, v in sorted(by_category.items(), key=lambda x: x[1]["total"], reverse=True)
        },
        "by_month": {k: round(v, 2) for k, v in sorted(by_month.items())},
    }
