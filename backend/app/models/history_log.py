from datetime import datetime
import enum
from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base


class HistoryActionType(str, enum.Enum):
    CREATED = "CREATED"
    CONDITION_CHANGED = "CONDITION_CHANGED"
    LOCATION_MOVED = "LOCATION_MOVED"
    DECOMMISSIONED = "DECOMMISSIONED"
    RESTORED = "RESTORED"


class UnitHistoryLog(Base):
    """
    Tabel Riwayat Mutasi & Audit Trail Unit Barang.
    Mencatat jejak perubahan kondisi dan perpindahan lokasi fisik barang.
    """
    __tablename__ = "unit_history_logs"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, index=True, autoincrement=True)
    unit_code = Column(String(15), ForeignKey("item_units.unit_code", ondelete="RESTRICT"), nullable=False, index=True)
    changed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action_type = Column(SQLEnum(HistoryActionType), nullable=False)
    old_value = Column(String(255), nullable=True)
    new_value = Column(String(255), nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    unit = relationship("ItemUnit", back_populates="history_logs")
    changer = relationship("User", back_populates="history_logs")
