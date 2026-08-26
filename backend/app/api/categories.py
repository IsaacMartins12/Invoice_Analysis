from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.invoice import Invoice
from app.services.auth import get_current_user

router = APIRouter(prefix="/api/categories", tags=["categories"])

# Default categories (always available)
DEFAULT_CATEGORIES = [
    {"name": "Transporte", "emoji": "🚗"},
    {"name": "Alimentação", "emoji": "🍔"},
    {"name": "Mercado", "emoji": "🛒"},
    {"name": "Telefone/Internet/Streaming", "emoji": "📱"},
    {"name": "Saúde/Academia", "emoji": "💪"},
    {"name": "Compras", "emoji": "🛍️"},
    {"name": "Viagem/Lazer", "emoji": "✈️"},
    {"name": "Taxas/Seguros", "emoji": "💳"},
    {"name": "Assinaturas", "emoji": "📋"},
    {"name": "Outros", "emoji": "📦"},
]


class CategoryCreate(BaseModel):
    name: str
    emoji: str = "📦"


class CategoryOut(BaseModel):
    id: int | None
    name: str
    emoji: str
    is_default: bool

    class Config:
        from_attributes = True


@router.get("/", response_model=list[CategoryOut])
def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all categories (default + user-created)."""
    # Default categories
    result = [
        CategoryOut(id=None, name=c["name"], emoji=c["emoji"], is_default=True)
        for c in DEFAULT_CATEGORIES
    ]

    # User custom categories
    custom = (
        db.query(Category)
        .filter(Category.user_id == current_user.id)
        .order_by(Category.name)
        .all()
    )
    for c in custom:
        result.append(
            CategoryOut(id=c.id, name=c.name, emoji=c.emoji, is_default=False)
        )

    return result


@router.post("/", response_model=CategoryOut)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new custom category."""
    # Check if name already exists (default or custom)
    default_names = [c["name"].upper() for c in DEFAULT_CATEGORIES]
    if data.name.upper() in default_names:
        raise HTTPException(status_code=400, detail="Category already exists as default")

    existing = (
        db.query(Category)
        .filter(Category.user_id == current_user.id, Category.name == data.name)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")

    category = Category(
        user_id=current_user.id,
        name=data.name,
        emoji=data.emoji,
    )
    db.add(category)
    db.commit()
    db.refresh(category)

    return CategoryOut(id=category.id, name=category.name, emoji=category.emoji, is_default=False)


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a custom category."""
    category = (
        db.query(Category)
        .filter(Category.id == category_id, Category.user_id == current_user.id)
        .first()
    )
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    old_name = category.name
    category.name = data.name
    category.emoji = data.emoji

    # Update all transactions that used the old name
    transactions = (
        db.query(Transaction)
        .join(Invoice)
        .filter(Invoice.user_id == current_user.id, Transaction.category == old_name)
        .all()
    )
    for t in transactions:
        t.category = data.name

    db.commit()
    db.refresh(category)

    return CategoryOut(id=category.id, name=category.name, emoji=category.emoji, is_default=False)


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a custom category. Transactions using it will be moved to 'Outros'."""
    category = (
        db.query(Category)
        .filter(Category.id == category_id, Category.user_id == current_user.id)
        .first()
    )
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Move transactions to "Outros"
    transactions = (
        db.query(Transaction)
        .join(Invoice)
        .filter(Invoice.user_id == current_user.id, Transaction.category == category.name)
        .all()
    )
    for t in transactions:
        t.category = "Outros"

    db.delete(category)
    db.commit()
    return {"message": "Category deleted, transactions moved to 'Outros'"}
