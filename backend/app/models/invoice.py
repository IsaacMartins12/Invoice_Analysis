from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    bank = Column(String, nullable=True)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    file_name = Column(String, nullable=False)
    content_hash = Column(String, nullable=True, index=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="invoices")
    transactions = relationship("Transaction", back_populates="invoice", cascade="all, delete-orphan")
