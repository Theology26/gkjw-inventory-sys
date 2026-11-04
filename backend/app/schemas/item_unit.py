from datetime import date, datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from app.models.item_unit import ConditionStatus, LifecycleStatus
from app.models.history_log import HistoryActionType


class ConditionDistribution(BaseModel):
    """
    Sub-form untuk memecah porsi kondisi barang saat bulk input.
    Contoh: Dari 10 unit -> 4 Baik, 3 Kurang Baik, 3 Rusak Berat.
    """
    baik: int = Field(0, ge=0)
    kurang_baik: int = Field(0, ge=0)
    rusak_berat: int = Field(0, ge=0)


class BulkCreateUnitRequest(BaseModel):
    """
    Schema input penambahan barang massal (1 submit = N unit fisik berlabel).
    Mendukung Condition Splitter.
    """
    pokja_code: str = Field(..., min_length=3, max_length=3, description="Kode POKJA: MAU, MVI, dsb.")
    name: str = Field(..., min_length=2, max_length=150, description="Nama barang: Mic Wireless, Kursi, dsb.")
    brand_model: str = Field("-", max_length=150, description="Merk/tipe: KREZT KRU-4810A")
    category: Optional[str] = Field(None, max_length=80)
    quantity: int = Field(..., ge=1, le=500, description="Jumlah unit fisik yang akan di-generate")
    condition_status: Optional[ConditionStatus] = ConditionStatus.BAIK
    condition_split: Optional[ConditionDistribution] = None
    location_id: int
    acquisition_date: Optional[date] = None
    notes: Optional[str] = None


class BulkCreateUnitResponseData(BaseModel):
    item_id: int
    item_name: str
    brand_model: str
    pokja_code: str
    quantity: int
    generated_unit_codes: List[str]
    pokja_last_sequence: int
    condition_summary: Optional[Dict[str, int]] = None


class BulkCreateUnitResponse(BaseModel):
    status: str = "success"
    message: str
    data: BulkCreateUnitResponseData


class UnitUpdateRequest(BaseModel):
    condition_status: Optional[ConditionStatus] = None
    location_id: Optional[int] = None
    notes: Optional[str] = None
    remarks: Optional[str] = Field(None, description="Catatan alasan perubahan untuk audit trail")


class DecommissionRequest(BaseModel):
    reason: str = Field(..., min_length=5, description="Alasan penghapusan/berita acara")


class UnitHistoryLogResponse(BaseModel):
    id: int
    unit_code: str
    action_type: HistoryActionType
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    remarks: Optional[str] = None
    changed_by_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ItemUnitResponse(BaseModel):
    unit_code: str
    item_id: int
    item_name: str
    brand_model: str
    pokja_code: str
    pokja_name: str
    location_id: int
    location_name: str
    condition_status: ConditionStatus
    lifecycle_status: LifecycleStatus
    unit_photo_path: Optional[str] = None
    acquisition_date: Optional[date] = None
    notes: Optional[str] = None
    decommissioned_at: Optional[datetime] = None
    decommission_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
