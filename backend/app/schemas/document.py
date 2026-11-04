from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class DocumentBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    doc_number: Optional[str] = Field(None, max_length=100)
    pokja_id: Optional[int] = None
    related_item_id: Optional[int] = None
    physical_storage_loc: Optional[str] = Field(None, max_length=150)


class DocumentCreate(DocumentBase):
    pass


class DocumentResponse(DocumentBase):
    id: int
    file_path: str
    file_type: str
    file_size_bytes: int
    pokja_code: Optional[str] = None
    item_name: Optional[str] = None
    uploaded_by_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

