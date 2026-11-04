from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class Item(Base):
    """
    Tabel Master Katalog Barang (Level 1 Normalisasi).
    Satu master item mewakili tipe barang yang sama (misal: Mic Wireless KREZT KRU-4810A).
    """
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    pokja_id = Column(Integer, ForeignKey("pokja.id", ondelete="RESTRICT"), nullable=False, index=True)
    name = Column(String(150), nullable=False, index=True)
    brand_model = Column(String(150), nullable=False, default="-")
    category = Column(String(80), nullable=True, index=True)
    default_photo_path = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Unique constraint per POKJA + Nama + Merk
    __table_args__ = (
        UniqueConstraint("pokja_id", "name", "brand_model", name="uq_pokja_item_brand"),
    )

    # Relationships
    pokja = relationship("Pokja", back_populates="items")
    units = relationship("ItemUnit", back_populates="item", cascade="all, delete-orphan")
    documents = relationship("ChurchDocument", back_populates="related_item")

