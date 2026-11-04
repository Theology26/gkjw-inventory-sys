from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ItemBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    brand_model: str = Field("-", max_length=150)
    category: Optional[str] = Field(None, max_length=80)
    description: Optional[str] = None


class ItemCreate(ItemBase):
    pokja_id: int


class ItemSimple(ItemBase):
    id: int
    pokja_id: int
    default_photo_path: Optional[str] = None

    class Config:
        from_attributes = True


class ItemCatalogResponse(ItemBase):
    """
    Schema untuk Mode Tampilan Katalog Terkelompok (Expandable Master-Detail)
    Anti-AI-Slop & Anti-Redundansi.
    """
    id: int
    pokja_id: int
    pokja_code: str
    pokja_name: str
    default_photo_path: Optional[str] = None
    total_units: int = 0
    baik_count: int = 0
    kurang_baik_count: int = 0
    rusak_berat_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True

