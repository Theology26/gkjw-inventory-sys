from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class LocationBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    building_zone: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None


class LocationCreate(LocationBase):
    pass


class LocationResponse(LocationBase):
    id: int
    room_photo_path: Optional[str] = None
    total_units: int = 0
    created_at: datetime

    class Config:
        from_attributes = True

