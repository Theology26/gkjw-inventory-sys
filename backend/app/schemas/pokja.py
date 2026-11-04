from datetime import datetime
from pydantic import BaseModel, Field


class PokjaBase(BaseModel):
    code: str = Field(..., min_length=3, max_length=3, description="Kode 3 huruf POKJA: MAU, MVI, dsb.")
    name: str = Field(..., min_length=3, max_length=120)


class PokjaCreate(PokjaBase):
    pass


class PokjaResponse(PokjaBase):
    id: int
    last_sequence: int
    total_items: int = 0
    total_units: int = 0
    created_at: datetime

    class Config:
        from_attributes = True

