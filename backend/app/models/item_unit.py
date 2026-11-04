from datetime import datetime, date
import enum
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base


class ConditionStatus(str, enum.Enum):
    BAIK = "BAIK"
    KURANG_BAIK = "KURANG_BAIK"
    RUSAK_BERAT = "RUSAK_BERAT"


class LifecycleStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    BORROWED = "BORROWED"
    MAINTENANCE = "MAINTENANCE"
    DECOMMISSIONED = "DECOMMISSIONED"


class ItemUnit(Base):
    """
    Tabel Unit Fisik Berlabel (Level 2 Normalisasi).
    1 Baris = 1 Stiker Fisik Berlabel di GKJW Sukun (Immutable Primary Key).
    DILARANG keras melakukan HARD DELETE.
    """
    __tablename__ = "item_units"

    unit_code = Column(String(15), primary_key=True, index=True)  # Contoh: MAU-001
    item_id = Column(Integer, ForeignKey("items.id", ondelete="RESTRICT"), nullable=False, index=True)
    location_id = Column(Integer, ForeignKey("locations.id", ondelete="RESTRICT"), nullable=False, index=True)
    condition_status = Column(SQLEnum(ConditionStatus), nullable=False, default=ConditionStatus.BAIK, index=True)
    lifecycle_status = Column(SQLEnum(LifecycleStatus), nullable=False, default=LifecycleStatus.ACTIVE, index=True)
    unit_photo_path = Column(String(255), nullable=True)
    acquisition_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)

    # Decommission fields (Soft Delete dengan Berita Acara)
    decommissioned_at = Column(DateTime, nullable=True)
    decommission_reason = Column(Text, nullable=True)

    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    item = relationship("Item", back_populates="units")
    location = relationship("Location", back_populates="units")
    creator = relationship("User", back_populates="created_units")
    history_logs = relationship("UnitHistoryLog", back_populates="unit", cascade="all, delete-orphan")

