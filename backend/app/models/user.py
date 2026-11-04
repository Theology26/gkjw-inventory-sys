from datetime import datetime
import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserRole(str, enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    POKJA_ADMIN = "POKJA_ADMIN"
    VIEWER = "VIEWER"


class User(Base):
    """
    Tabel Pengguna Aplikasi (Pengurus POKJA, Tim Inventaris, & Majelis).
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=False, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.VIEWER)
    pokja_id = Column(Integer, ForeignKey("pokja.id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    pokja = relationship("Pokja", back_populates="users")
    created_units = relationship("ItemUnit", back_populates="creator")
    history_logs = relationship("UnitHistoryLog", back_populates="changer")
    uploaded_documents = relationship("ChurchDocument", back_populates="uploader")

