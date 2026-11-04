from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class Location(Base):
    """
    Tabel Master Ruangan / Titik Lokasi Penyimpanan GKJW Sukun.
    """
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, index=True)
    building_zone = Column(String(100), nullable=True)  # Gedung Utama, Gedung Timur, dsb.
    room_photo_path = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    extra = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    units = relationship("ItemUnit", back_populates="location")

