from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class Pokja(Base):
    """
    Tabel Master 24 POKJA / Komisi GKJW Sukun.
    Menyimpan kode 3 huruf resmi dan sequence counter untuk stiker fisik.
    """
    __tablename__ = "pokja"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(3), unique=True, nullable=False, index=True)  # MAU, MVI, KTP, etc.
    name = Column(String(120), unique=True, nullable=False)
    last_sequence = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    items = relationship("Item", back_populates="pokja", cascade="all, delete-orphan")
    users = relationship("User", back_populates="pokja")
    documents = relationship("ChurchDocument", back_populates="pokja")

