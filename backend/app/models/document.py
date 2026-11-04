from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class ChurchDocument(Base):
    """
    Tabel Arsip Dokumen Gereja (Nota, Garansi, BPKB, Sertifikat, SK, Berita Acara).
    """
    __tablename__ = "church_documents"

    id = Column(Integer, primary_key=True, index=True)
    doc_number = Column(String(100), nullable=True, index=True)
    title = Column(String(200), nullable=False)
    pokja_id = Column(Integer, ForeignKey("pokja.id", ondelete="SET NULL"), nullable=True, index=True)
    related_item_id = Column(Integer, ForeignKey("items.id", ondelete="SET NULL"), nullable=True, index=True)
    file_path = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, webp, jpg, png, docx
    file_size_bytes = Column(BigInteger, nullable=False, default=0)
    physical_storage_loc = Column(String(150), nullable=True)  # Lokasi map arsip fisik di gereja
    uploaded_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    pokja = relationship("Pokja", back_populates="documents")
    related_item = relationship("Item", back_populates="documents")
    uploader = relationship("User", back_populates="uploaded_documents")

