from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    store_name = Column(String, nullable=False)
    store_cnpj = Column(String, nullable=True)
    date = Column(String, nullable=False)
    total = Column(Float, nullable=False)
    access_key = Column(String, unique=True, nullable=True)  # Chave de acesso NFC-e
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="receipts")
    items = relationship("ReceiptItem", back_populates="receipt", cascade="all, delete-orphan")


class ReceiptItem(Base):
    __tablename__ = "receipt_items"

    id = Column(Integer, primary_key=True, index=True)
    receipt_id = Column(Integer, ForeignKey("receipts.id"), nullable=False)
    raw_description = Column(String, nullable=False)  # Original: "EXTR POM ELEF 340G"
    description = Column(String, nullable=False)       # Normalized: "Extrato de Tomate Elefante 340g"
    quantity = Column(Float, nullable=False, default=1.0)
    unit = Column(String, nullable=True)               # "KG", "UN", "L"
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    category = Column(String, nullable=False, default="Outros")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    receipt = relationship("Receipt", back_populates="items")


class ProductDictionary(Base):
    """User-confirmed product name mappings.
    Once confirmed, LLM is no longer needed for this abbreviation."""
    __tablename__ = "product_dictionary"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    raw_description = Column(String, nullable=False)   # "EXTR POM"
    normalized_name = Column(String, nullable=False)    # "Extrato de Tomate"
    category = Column(String, nullable=False)           # "Molhos/Condimentos"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
