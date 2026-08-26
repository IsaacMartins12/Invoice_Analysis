from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.models.receipt import Receipt, ReceiptItem, ProductDictionary
from app.services.auth import get_current_user
from app.services.receipt_parser import parse_nfce_url
from app.services.product_normalizer import (
    normalize_items,
    save_to_dictionary,
    PRODUCT_CATEGORIES,
)

router = APIRouter(prefix="/api/receipts", tags=["receipts"])


# --- Schemas ---

class ReceiptItemOut(BaseModel):
    id: int
    raw_description: str
    description: str
    quantity: float
    unit: str | None
    unit_price: float
    total_price: float
    category: str

    class Config:
        from_attributes = True


class ReceiptOut(BaseModel):
    id: int
    store_name: str
    store_cnpj: str | None
    date: str
    total: float
    created_at: str
    items: list[ReceiptItemOut] = []

    class Config:
        from_attributes = True


class ReceiptListItem(BaseModel):
    id: int
    store_name: str
    date: str
    total: float
    item_count: int


class ScanRequest(BaseModel):
    url: str


class UpdateItemRequest(BaseModel):
    description: str
    category: str
    save_to_dictionary: bool = True


# --- Routes ---

@router.post("/scan", response_model=ReceiptOut)
def scan_receipt(
    data: ScanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Scan a NFC-e receipt from its QR Code URL."""

    # Check if already scanned
    existing = db.query(Receipt).filter(Receipt.access_key != None).first()
    # We'll check by URL content later if needed

    # Parse the NFC-e
    try:
        parsed = parse_nfce_url(data.url)
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not parse receipt: {e}")

    if not parsed.items:
        raise HTTPException(status_code=422, detail="No items found in receipt")

    # Check duplicate by access key
    if parsed.access_key:
        dup = (
            db.query(Receipt)
            .filter(
                Receipt.user_id == current_user.id,
                Receipt.access_key == parsed.access_key,
            )
            .first()
        )
        if dup:
            raise HTTPException(status_code=409, detail="This receipt was already scanned")

    # Normalize descriptions using dictionary + LLM
    raw_descs = [item.raw_description for item in parsed.items]
    normalized = normalize_items(raw_descs, current_user.id, db)

    # Save receipt
    receipt = Receipt(
        user_id=current_user.id,
        store_name=parsed.store_name,
        store_cnpj=parsed.store_cnpj,
        date=parsed.date,
        total=parsed.total,
        access_key=parsed.access_key or None,
    )
    db.add(receipt)
    db.flush()

    # Save items
    for i, item in enumerate(parsed.items):
        norm = normalized[i] if i < len(normalized) else {"name": item.raw_description, "category": "Outros"}
        receipt_item = ReceiptItem(
            receipt_id=receipt.id,
            raw_description=item.raw_description,
            description=norm["name"],
            quantity=item.quantity,
            unit=item.unit,
            unit_price=item.unit_price,
            total_price=item.total_price,
            category=norm["category"],
        )
        db.add(receipt_item)

    db.commit()
    db.refresh(receipt)

    return ReceiptOut(
        id=receipt.id,
        store_name=receipt.store_name,
        store_cnpj=receipt.store_cnpj,
        date=receipt.date,
        total=receipt.total,
        created_at=receipt.created_at.isoformat(),
        items=receipt.items,
    )


@router.get("/", response_model=list[ReceiptListItem])
def list_receipts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all receipts for the current user."""
    receipts = (
        db.query(Receipt)
        .filter(Receipt.user_id == current_user.id)
        .order_by(Receipt.created_at.desc())
        .all()
    )
    return [
        ReceiptListItem(
            id=r.id,
            store_name=r.store_name,
            date=r.date,
            total=r.total,
            item_count=len(r.items),
        )
        for r in receipts
    ]


@router.get("/categories")
def get_product_categories():
    """Get available product categories."""
    return PRODUCT_CATEGORIES


@router.get("/summary")
def receipt_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get spending summary across all receipts."""
    items = (
        db.query(ReceiptItem)
        .join(Receipt)
        .filter(Receipt.user_id == current_user.id)
        .all()
    )

    if not items:
        return {"total": 0, "item_count": 0, "by_category": {}, "receipt_count": 0}

    by_category = {}
    for item in items:
        cat = item.category
        if cat not in by_category:
            by_category[cat] = {"total": 0, "count": 0}
        by_category[cat]["total"] += item.total_price
        by_category[cat]["count"] += 1

    receipt_count = (
        db.query(Receipt)
        .filter(Receipt.user_id == current_user.id)
        .count()
    )

    total = sum(item.total_price for item in items)

    return {
        "total": round(total, 2),
        "item_count": len(items),
        "receipt_count": receipt_count,
        "by_category": {
            k: {"total": round(v["total"], 2), "count": v["count"]}
            for k, v in sorted(by_category.items(), key=lambda x: x[1]["total"], reverse=True)
        },
    }


@router.get("/{receipt_id}", response_model=ReceiptOut)
def get_receipt(
    receipt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific receipt with items."""
    receipt = (
        db.query(Receipt)
        .filter(Receipt.id == receipt_id, Receipt.user_id == current_user.id)
        .first()
    )
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")

    return ReceiptOut(
        id=receipt.id,
        store_name=receipt.store_name,
        store_cnpj=receipt.store_cnpj,
        date=receipt.date,
        total=receipt.total,
        created_at=receipt.created_at.isoformat(),
        items=receipt.items,
    )


@router.put("/items/{item_id}")
def update_item(
    item_id: int,
    data: UpdateItemRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an item's description/category and optionally save to dictionary."""
    item = (
        db.query(ReceiptItem)
        .join(Receipt)
        .filter(ReceiptItem.id == item_id, Receipt.user_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item.description = data.description
    item.category = data.category

    # Save to dictionary for future auto-resolution
    if data.save_to_dictionary:
        save_to_dictionary(
            raw_description=item.raw_description,
            normalized_name=data.description,
            category=data.category,
            user_id=current_user.id,
            db=db,
        )

    db.commit()
    return {"message": "Item updated"}


@router.delete("/{receipt_id}")
def delete_receipt(
    receipt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a receipt and its items."""
    receipt = (
        db.query(Receipt)
        .filter(Receipt.id == receipt_id, Receipt.user_id == current_user.id)
        .first()
    )
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")

    db.delete(receipt)
    db.commit()
    return {"message": "Receipt deleted"}
