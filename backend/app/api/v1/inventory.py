import io
from datetime import datetime, date
from typing import List, Optional
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_, case
from app.api.deps import get_db, get_current_user, require_admin, require_super_admin
from app.core.media import compress_and_save_image
from app.models.pokja import Pokja
from app.models.location import Location
from app.models.item import Item
from app.models.item_unit import ItemUnit, ConditionStatus, LifecycleStatus
from app.models.history_log import UnitHistoryLog, HistoryActionType
from app.models.user import User, UserRole
from app.schemas.item import ItemCatalogResponse
from app.schemas.item_unit import (
    BulkCreateUnitRequest,
    BulkCreateUnitResponse,
    BulkCreateUnitResponseData,
    ItemUnitResponse,
    UnitUpdateRequest,
    DecommissionRequest,
    UnitHistoryLogResponse,
)

router = APIRouter(prefix="/inventory", tags=["Inventaris & Unit Fisik"])


# ------------------------------------------------------------------------------
# 0. RINGKASAN PUBLIK (READ-ONLY TANPA LOGIN)
# ------------------------------------------------------------------------------
@router.get("/public/summary")
def get_public_summary(db: Session = Depends(get_db)):
    """
    Endpoint publik untuk menampilkan ringkasan data di Landing Page resmi gereja.
    Read-only, aman, dan tanpa data privat.
    """
    total_pokja = db.query(func.count(Pokja.id)).scalar() or 24
    total_items = db.query(func.count(Item.id)).scalar() or 0
    total_units = (
        db.query(func.count(ItemUnit.unit_code))
        .filter(ItemUnit.lifecycle_status != LifecycleStatus.DECOMMISSIONED)
        .scalar() or 0
    )
    total_good = (
        db.query(func.count(ItemUnit.unit_code))
        .filter(
            ItemUnit.condition_status == ConditionStatus.BAIK,
            ItemUnit.lifecycle_status != LifecycleStatus.DECOMMISSIONED
        )
        .scalar() or 0
    )
    return {
        "total_pokja": total_pokja,
        "total_items": total_items,
        "total_units": total_units,
        "total_good": total_good,
    }


# ------------------------------------------------------------------------------
# 1. MODE KATALOG TERKELOMPOK (GROUPED MODE - ANTI-REDUNDANSI)
# ------------------------------------------------------------------------------
@router.get("/catalog", response_model=List[ItemCatalogResponse])
def get_inventory_catalog(
    pokja_code: Optional[str] = Query(None, description="Filter kode POKJA: MAU, MVI, dsb."),
    search: Optional[str] = Query(None, description="Pencarian nama, merk, kategori, atau nomor stiker"),
    location_id: Optional[int] = Query(None, description="Filter ID lokasi ruangan"),
    condition_status: Optional[ConditionStatus] = Query(None, description="Filter kondisi fisik"),
    condition: Optional[ConditionStatus] = Query(None, description="Alias untuk filter kondisi fisik"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mode Katalog Terkelompok (Expandable Master-Detail):
    Menampilkan 1 baris per jenis barang beserta ringkasan agregasi kondisi unit fisik.
    Mendukung filter POKJA, kata kunci pencarian (termasuk nomor stiker), lokasi, dan kondisi fisik.
    """
    effective_condition = condition_status or condition

    unit_conditions = [
        ItemUnit.item_id == Item.id,
        ItemUnit.lifecycle_status != LifecycleStatus.DECOMMISSIONED,
    ]
    if location_id:
        unit_conditions.append(ItemUnit.location_id == location_id)
    if effective_condition:
        unit_conditions.append(ItemUnit.condition_status == effective_condition)

    query = (
        db.query(
            Item.id,
            Item.pokja_id,
            Pokja.code.label("pokja_code"),
            Pokja.name.label("pokja_name"),
            Item.name,
            Item.brand_model,
            Item.category,
            Item.default_photo_path,
            Item.description,
            Item.created_at,
            func.count(ItemUnit.unit_code).label("total_units"),
            func.coalesce(func.sum(case((ItemUnit.condition_status == ConditionStatus.BAIK, 1), else_=0)), 0).label("baik_count"),
            func.coalesce(func.sum(case((ItemUnit.condition_status == ConditionStatus.KURANG_BAIK, 1), else_=0)), 0).label("kurang_baik_count"),
            func.coalesce(func.sum(case((ItemUnit.condition_status == ConditionStatus.RUSAK_BERAT, 1), else_=0)), 0).label("rusak_berat_count"),
        )
        .join(Pokja, Pokja.id == Item.pokja_id)
    )

    if location_id or effective_condition:
        query = query.join(ItemUnit, and_(*unit_conditions))
    else:
        query = query.outerjoin(ItemUnit, and_(*unit_conditions))

    if current_user.role == UserRole.POKJA_ADMIN and current_user.pokja_id:
        query = query.filter(Item.pokja_id == current_user.pokja_id)
    elif pokja_code:
        query = query.filter(Pokja.code == pokja_code.strip().upper())

    if search and search.strip():
        s = f"%{search.strip().lower()}%"
        query = query.filter(
            or_(
                func.lower(Item.name).like(s),
                func.lower(Item.brand_model).like(s),
                func.lower(Item.category).like(s),
                func.lower(Pokja.code).like(s),
                func.lower(Pokja.name).like(s),
                Item.units.any(
                    and_(
                        func.lower(ItemUnit.unit_code).like(s),
                        ItemUnit.lifecycle_status != LifecycleStatus.DECOMMISSIONED
                    )
                )
            )
        )

    query = query.group_by(Item.id, Pokja.code, Pokja.name).order_by(Item.name.asc())

    rows = query.all()
    results = []
    for r in rows:
        results.append(
            ItemCatalogResponse(
                id=r.id,
                pokja_id=r.pokja_id,
                pokja_code=r.pokja_code,
                pokja_name=r.pokja_name,
                name=r.name,
                brand_model=r.brand_model,
                category=r.category,
                default_photo_path=r.default_photo_path,
                description=r.description,
                total_units=int(r.total_units),
                baik_count=int(r.baik_count),
                kurang_baik_count=int(r.kurang_baik_count),
                rusak_berat_count=int(r.rusak_berat_count),
                created_at=r.created_at,
            )
        )
    return results


@router.get("/catalog/{item_id}/units", response_model=List[ItemUnitResponse])
def get_units_for_catalog_item(
    item_id: int,
    location_id: Optional[int] = Query(None, description="Filter ID lokasi ruangan"),
    condition_status: Optional[ConditionStatus] = Query(None, description="Filter kondisi fisik"),
    condition: Optional[ConditionStatus] = Query(None, description="Alias kondisi fisik"),
    search: Optional[str] = Query(None, description="Pencarian kode stiker / catatan"),
    include_decommissioned: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Sub-Tabel Akordeon: Mengambil daftar seluruh unit fisik berlabel stiker
    untuk 1 master katalog barang tertentu saat baris diklik/expand.
    Mendukung filter lokasi, kondisi, dan kata kunci stiker.
    """
    effective_condition = condition_status or condition
    query = (
        db.query(ItemUnit)
        .join(Item, Item.id == ItemUnit.item_id)
        .join(Location, Location.id == ItemUnit.location_id)
        .filter(ItemUnit.item_id == item_id)
        .order_by(ItemUnit.unit_code.asc())
    )
    if not include_decommissioned:
        query = query.filter(ItemUnit.lifecycle_status != LifecycleStatus.DECOMMISSIONED)

    if location_id:
        query = query.filter(ItemUnit.location_id == location_id)
    if effective_condition:
        query = query.filter(ItemUnit.condition_status == effective_condition)
    if search and search.strip():
        s = f"%{search.strip().lower()}%"
        query = query.filter(
            or_(
                func.lower(ItemUnit.unit_code).like(s),
                func.lower(ItemUnit.notes).like(s),
                func.lower(Location.name).like(s),
            )
        )

    units = query.all()
    return [_format_unit_response(u) for u in units]


# ------------------------------------------------------------------------------
# 2. MODE SEMUA STIKER FISIK (FLAT UNIT LIST)
# ------------------------------------------------------------------------------
@router.get("/units", response_model=List[ItemUnitResponse])
def get_all_units(
    pokja_code: Optional[str] = Query(None, description="Filter kode POKJA"),
    location_id: Optional[int] = Query(None, description="Filter ID lokasi ruangan"),
    condition_status: Optional[ConditionStatus] = Query(None, description="Filter kondisi fisik"),
    condition: Optional[ConditionStatus] = Query(None, description="Alias kondisi fisik"),
    lifecycle_status: Optional[LifecycleStatus] = Query(None),
    search: Optional[str] = Query(None, description="Pencarian kode stiker, nama, merk, dsb."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mode Semua Stiker Fisik (Flat List):
    Menampilkan unit fisik berlabel per stiker (MAU-001, dsb.) untuk audit stock opname langsung.
    """
    effective_condition = condition_status or condition
    query = (
        db.query(ItemUnit)
        .join(Item, Item.id == ItemUnit.item_id)
        .join(Pokja, Pokja.id == Item.pokja_id)
        .join(Location, Location.id == ItemUnit.location_id)
        .order_by(ItemUnit.unit_code.asc())
    )

    if current_user.role == UserRole.POKJA_ADMIN and current_user.pokja_id:
        query = query.filter(Item.pokja_id == current_user.pokja_id)
    elif pokja_code:
        query = query.filter(Pokja.code == pokja_code.strip().upper())

    if location_id:
        query = query.filter(ItemUnit.location_id == location_id)

    if effective_condition:
        query = query.filter(ItemUnit.condition_status == effective_condition)

    if lifecycle_status:
        query = query.filter(ItemUnit.lifecycle_status == lifecycle_status)
    else:
        query = query.filter(ItemUnit.lifecycle_status != LifecycleStatus.DECOMMISSIONED)

    if search and search.strip():
        s = f"%{search.strip().lower()}%"
        query = query.filter(
            or_(
                func.lower(ItemUnit.unit_code).like(s),
                func.lower(Item.name).like(s),
                func.lower(Item.brand_model).like(s),
                func.lower(Item.category).like(s),
                func.lower(Pokja.code).like(s),
                func.lower(Pokja.name).like(s),
                func.lower(Location.name).like(s),
            )
        )

    units = query.all()
    return [_format_unit_response(u) for u in units]


# ------------------------------------------------------------------------------
# 3. ATOMIC BULK-CREATE UNIT GENERATOR DENGAN CONDITION SPLITTER
# ------------------------------------------------------------------------------
@router.post("/bulk-create", response_model=BulkCreateUnitResponse, status_code=status.HTTP_201_CREATED)
def bulk_create_units(
    payload: BulkCreateUnitRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    CORE ENDPOINT: Menambah barang baru dengan kuantitas N unit sekaligus secara atomik.
    Mendukung FITUR CONDITION SPLITTER (contoh: 10 unit -> 4 Baik, 3 Kurang Baik, 3 Rusak Berat).
    1. Normalisasi nama & merk barang.
    2. Cek apakah Master Item sudah ada; buat baru jika belum.
    3. Kunci row POKJA dengan SELECT ... FOR UPDATE untuk mengunci last_sequence.
    4. Generate kode berurutan: MAU-064 s/d MAU-073 (zero-padded).
    5. Petakan status kondisi sesuai porsi condition splitter secara berurutan.
    6. Bulk insert unit & catat event 'CREATED' ke unit_history_logs.
    7. Update pokja.last_sequence & COMMIT.
    """
    clean_pokja_code = payload.pokja_code.strip().upper()
    clean_name = payload.name.strip()
    clean_brand = (payload.brand_model or "-").strip()

    # Validasi POKJA
    pokja = db.query(Pokja).filter(Pokja.code == clean_pokja_code).first()
    if not pokja:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"POKJA dengan kode '{clean_pokja_code}' tidak ditemukan."
        )

    # Validasi hak akses POKJA_ADMIN (hanya boleh input ke POKJA-nya)
    if admin.role == UserRole.POKJA_ADMIN and admin.pokja_id and admin.pokja_id != pokja.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Anda hanya berwenang menambahkan inventaris untuk POKJA Anda sendiri."
        )

    # Validasi Lokasi
    location = db.query(Location).filter(Location.id == payload.location_id).first()
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lokasi ID {payload.location_id} tidak valid."
        )

    # Logika Condition Splitter
    conditions_sequence = []
    condition_summary = {}

    if payload.condition_split:
        cs = payload.condition_split
        total_split = cs.baik + cs.kurang_baik + cs.rusak_berat
        if total_split != payload.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Total pemecahan porsi kondisi ({total_split} unit) tidak sama dengan jumlah unit ({payload.quantity} unit)."
            )
        conditions_sequence.extend([ConditionStatus.BAIK] * cs.baik)
        conditions_sequence.extend([ConditionStatus.KURANG_BAIK] * cs.kurang_baik)
        conditions_sequence.extend([ConditionStatus.RUSAK_BERAT] * cs.rusak_berat)
        condition_summary = {
            "BAIK": cs.baik,
            "KURANG_BAIK": cs.kurang_baik,
            "RUSAK_BERAT": cs.rusak_berat
        }
    else:
        default_cond = payload.condition_status or ConditionStatus.BAIK
        conditions_sequence = [default_cond] * payload.quantity
        condition_summary = {default_cond.value: payload.quantity}

    try:
        # Step 1: Upsert Master Item
        item = (
            db.query(Item)
            .filter(
                Item.pokja_id == pokja.id,
                func.lower(Item.name) == clean_name.lower(),
                func.lower(Item.brand_model) == clean_brand.lower()
            )
            .first()
        )

        if not item:
            item = Item(
                pokja_id=pokja.id,
                name=clean_name,
                brand_model=clean_brand,
                category=payload.category.strip() if payload.category else None,
            )
            db.add(item)
            db.flush()

        # Step 2: Atomic Row Locking pada POKJA last_sequence
        locked_pokja = (
            db.query(Pokja)
            .filter(Pokja.id == pokja.id)
            .with_for_update()
            .first()
        )

        start_seq = locked_pokja.last_sequence + 1
        end_seq = locked_pokja.last_sequence + payload.quantity

        generated_codes = []
        new_units = []
        history_logs = []

        for idx, seq in enumerate(range(start_seq, end_seq + 1)):
            unit_code = f"{locked_pokja.code}-{seq:03d}"
            generated_codes.append(unit_code)
            unit_cond = conditions_sequence[idx]

            unit = ItemUnit(
                unit_code=unit_code,
                item_id=item.id,
                location_id=location.id,
                condition_status=unit_cond,
                lifecycle_status=LifecycleStatus.ACTIVE,
                acquisition_date=payload.acquisition_date or date.today(),
                notes=payload.notes,
                created_by=admin.id
            )
            new_units.append(unit)

            log = UnitHistoryLog(
                unit_code=unit_code,
                changed_by=admin.id,
                action_type=HistoryActionType.CREATED,
                old_value=None,
                new_value=f"Kondisi: {unit_cond.value}, Lokasi: {location.name}",
                remarks=f"Registrasi awal {payload.quantity} unit oleh {admin.name} ({admin.email})"
            )
            history_logs.append(log)

        db.add_all(new_units)
        db.add_all(history_logs)

        locked_pokja.last_sequence = end_seq
        db.commit()

        return BulkCreateUnitResponse(
            status="success",
            message=f"Berhasil menambahkan {payload.quantity} unit baru ke katalog {item.name} ({item.brand_model}).",
            data=BulkCreateUnitResponseData(
                item_id=item.id,
                item_name=item.name,
                brand_model=item.brand_model,
                pokja_code=locked_pokja.code,
                quantity=payload.quantity,
                generated_unit_codes=generated_codes,
                pokja_last_sequence=end_seq,
                condition_summary=condition_summary
            )
        )

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal melakukan bulk create inventaris: {str(e)}"
        )


# ------------------------------------------------------------------------------
# 4. UPLOAD FOTO FISIK (KATALOG / UNIT WEBP PIPELINE)
# ------------------------------------------------------------------------------
@router.post("/catalog/{item_id}/photo")
def upload_catalog_photo(
    item_id: int,
    file: UploadFile = File(...),
    apply_to_units: bool = Query(True, description="Terapkan foto ini ke seluruh unit fisik barang"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Mengunggah foto master katalog barang (termasuk saat registrasi awal barang baru).
    Otomatis dikompresi ke WebP (LANCZOS, max 1280px, quality 80%).
    Jika apply_to_units=True, unit fisik yang belum punya foto otomatis memakai foto ini.
    """
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Katalog barang tidak ditemukan.")

    photo_path = compress_and_save_image(file, subfolder="photos/items", custom_filename=f"ITEM-{item.id}")
    item.default_photo_path = photo_path

    if apply_to_units:
        units = db.query(ItemUnit).filter(ItemUnit.item_id == item.id).all()
        for u in units:
            if not u.unit_photo_path:
                u.unit_photo_path = photo_path

    db.commit()
    db.refresh(item)
    return {
        "status": "success",
        "item_id": item.id,
        "default_photo_path": photo_path,
        "message": "Foto barang berhasil diunggah dan dikompresi ke format .webp"
    }


@router.post("/units/{unit_code}/photo", response_model=ItemUnitResponse)
def upload_unit_photo(
    unit_code: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Mengunggah / memperbarui foto fisik spesifik 1 unit barang.
    Otomatis dikompresi ke WebP (LANCZOS, max 1280px, quality 80%) sesuai guardrail laptop server.
    Mendukung capture='environment' dari kamera ponsel petugas stock opname.
    """
    unit = db.query(ItemUnit).filter(ItemUnit.unit_code == unit_code.strip()).first()
    if not unit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unit tidak ditemukan.")

    photo_path = compress_and_save_image(file, subfolder="photos/items", custom_filename=unit.unit_code)
    unit.unit_photo_path = photo_path

    log = UnitHistoryLog(
        unit_code=unit.unit_code,
        changed_by=admin.id,
        action_type=HistoryActionType.CONDITION_CHANGED,
        old_value=None,
        new_value=f"Foto fisik diunggah: {photo_path}",
        remarks="Pembaruan dokumentasi foto kondisi fisik unit"
    )
    db.add(log)
    db.commit()
    db.refresh(unit)
    return _format_unit_response(unit)


# ------------------------------------------------------------------------------
# 5. EDIT KONDISI / MUTASI LOKASI UNIT TUNGGAL
# ------------------------------------------------------------------------------
@router.patch("/units/{unit_code}", response_model=ItemUnitResponse)
def update_unit(
    unit_code: str,
    payload: UnitUpdateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Memperbarui kondisi atau memindahkan lokasi 1 unit fisik tertentu
    tanpa mempengaruhi unit kembarannya yang lain.
    Mencatat riwayat perubahan secara otomatis ke unit_history_logs.
    """
    unit = db.query(ItemUnit).filter(ItemUnit.unit_code == unit_code.strip()).first()
    if not unit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unit tidak ditemukan.")

    if unit.lifecycle_status == LifecycleStatus.DECOMMISSIONED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unit telah dinonaktifkan (Decommissioned) dan tidak dapat diubah."
        )

    if payload.condition_status and payload.condition_status != unit.condition_status:
        old_cond = unit.condition_status.value
        new_cond = payload.condition_status.value
        unit.condition_status = payload.condition_status

        log = UnitHistoryLog(
            unit_code=unit.unit_code,
            changed_by=admin.id,
            action_type=HistoryActionType.CONDITION_CHANGED,
            old_value=old_cond,
            new_value=new_cond,
            remarks=payload.remarks or f"Kondisi diubah dari {old_cond} ke {new_cond}"
        )
        db.add(log)

    if payload.location_id and payload.location_id != unit.location_id:
        new_loc = db.query(Location).filter(Location.id == payload.location_id).first()
        if not new_loc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lokasi baru tidak valid.")

        old_loc_name = unit.location.name if unit.location else str(unit.location_id)
        unit.location_id = new_loc.id

        log = UnitHistoryLog(
            unit_code=unit.unit_code,
            changed_by=admin.id,
            action_type=HistoryActionType.LOCATION_MOVED,
            old_value=old_loc_name,
            new_value=new_loc.name,
            remarks=payload.remarks or f"Dipindahkan dari {old_loc_name} ke {new_loc.name}"
        )
        db.add(log)

    if payload.notes is not None:
        unit.notes = payload.notes

    db.commit()
    db.refresh(unit)
    return _format_unit_response(unit)


# ------------------------------------------------------------------------------
# 6. DECOMMISSION (IMMUTABLE ID & SOFT DELETE)
# ------------------------------------------------------------------------------
@router.post("/units/{unit_code}/decommission", response_model=ItemUnitResponse)
def decommission_unit(
    unit_code: str,
    payload: DecommissionRequest,
    db: Session = Depends(get_db),
    super_admin: User = Depends(require_super_admin)
):
    """
    Menonaktifkan (Soft Delete) unit fisik yang rusak total / hilang.
    Nomor ID stiker TIDAK PERNAH DIHAPUS dari database dan TIDAK DI-RECYCLE.
    """
    unit = db.query(ItemUnit).filter(ItemUnit.unit_code == unit_code.strip()).first()
    if not unit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unit tidak ditemukan.")

    if unit.lifecycle_status == LifecycleStatus.DECOMMISSIONED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unit ini sudah berstatus dinonaktifkan (Decommissioned)."
        )

    unit.lifecycle_status = LifecycleStatus.DECOMMISSIONED
    unit.decommissioned_at = datetime.utcnow()
    unit.decommission_reason = payload.reason.strip()

    log = UnitHistoryLog(
        unit_code=unit.unit_code,
        changed_by=super_admin.id,
        action_type=HistoryActionType.DECOMMISSIONED,
        old_value="ACTIVE",
        new_value="DECOMMISSIONED",
        remarks=f"Penonaktifan aset: {payload.reason.strip()}"
    )
    db.add(log)
    db.commit()
    db.refresh(unit)

    return _format_unit_response(unit)


# ------------------------------------------------------------------------------
# 7. RIWAYAT MUTASI UNIT (AUDIT TRAIL)
# ------------------------------------------------------------------------------
@router.get("/units/{unit_code}/history", response_model=List[UnitHistoryLogResponse])
def get_unit_history(
    unit_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mengambil seluruh catatan audit trail dan riwayat mutasi untuk 1 unit tertentu."""
    logs = (
        db.query(UnitHistoryLog)
        .filter(UnitHistoryLog.unit_code == unit_code.strip())
        .order_by(UnitHistoryLog.created_at.desc())
        .all()
    )
    results = []
    for log in logs:
        results.append(
            UnitHistoryLogResponse(
                id=log.id,
                unit_code=log.unit_code,
                action_type=log.action_type,
                old_value=log.old_value,
                new_value=log.new_value,
                remarks=log.remarks,
                changed_by_name=log.changer.name if log.changer else "Sistem",
                created_at=log.created_at
            )
        )
    return results


# ------------------------------------------------------------------------------
# 8. EKSPOR LAPORAN EXCEL (.XLSX) RESMI GEREJA
# ------------------------------------------------------------------------------
@router.get("/export/excel")
def export_inventory_excel(
    pokja_code: Optional[str] = Query(None),
    location_id: Optional[int] = Query(None),
    condition_status: Optional[ConditionStatus] = Query(None),
    condition: Optional[ConditionStatus] = Query(None),
    lifecycle_status: Optional[LifecycleStatus] = Query(None),
    search: Optional[str] = Query(None, description="Pencarian kode stiker, nama, atau merk"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mengunduh rekapitulasi data inventaris GKJW Sukun ke berkas Excel (.xlsx).
    Lengkap dengan POKJA, kondisi, lokasi, path foto bukti fisik, dan catatan.
    """
    effective_condition = condition_status or condition
    query = (
        db.query(ItemUnit)
        .join(Item, Item.id == ItemUnit.item_id)
        .join(Pokja, Pokja.id == Item.pokja_id)
        .join(Location, Location.id == ItemUnit.location_id)
        .order_by(Pokja.code.asc(), ItemUnit.unit_code.asc())
    )

    if current_user.role == UserRole.POKJA_ADMIN and current_user.pokja_id:
        query = query.filter(Item.pokja_id == current_user.pokja_id)
    elif pokja_code:
        query = query.filter(Pokja.code == pokja_code.strip().upper())

    if location_id:
        query = query.filter(ItemUnit.location_id == location_id)
    if effective_condition:
        query = query.filter(ItemUnit.condition_status == effective_condition)
    if lifecycle_status:
        query = query.filter(ItemUnit.lifecycle_status == lifecycle_status)

    if search and search.strip():
        s = f"%{search.strip().lower()}%"
        query = query.filter(
            or_(
                func.lower(ItemUnit.unit_code).like(s),
                func.lower(Item.name).like(s),
                func.lower(Item.brand_model).like(s),
                func.lower(Item.category).like(s),
                func.lower(Pokja.code).like(s),
                func.lower(Pokja.name).like(s),
                func.lower(Location.name).like(s),
            )
        )

    units = query.all()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Rekap Inventaris"

    header_fill = PatternFill(start_color="141413", end_color="141413", fill_type="solid")
    header_font = Font(name="Arial", size=10, bold=True, color="FFFFFF")
    data_font = Font(name="Arial", size=9)
    thin_border = Border(
        left=Side(style='thin', color='D6D3C9'),
        right=Side(style='thin', color='D6D3C9'),
        top=Side(style='thin', color='D6D3C9'),
        bottom=Side(style='thin', color='D6D3C9')
    )

    # Kop Header
    ws.merge_cells("A1:J1")
    ws["A1"] = "GREJA KRISTEN JAWI WETAN (GKJW) JEMAAT SUKUN"
    ws["A1"].font = Font(name="Arial", size=13, bold=True, color="C84B31")
    ws["A1"].alignment = Alignment(horizontal="center")

    ws.merge_cells("A2:J2")
    ws["A2"] = f"Laporan Rekapitulasi Fisik Inventaris & Aset — {datetime.now().strftime('%d %B %Y')}"
    ws["A2"].font = Font(name="Arial", size=10, italic=True)
    ws["A2"].alignment = Alignment(horizontal="center")

    headers = [
        "No", "ID Stiker", "POKJA / Komisi", "Nama Barang", "Merk / Model",
        "Lokasi Ruangan", "Kondisi Fisik", "Status", "Foto / Bukti Fisik", "Catatan"
    ]
    ws.append([])
    ws.append(headers)

    for col_num in range(1, len(headers) + 1):
        cell = ws.cell(row=4, column=col_num)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    for idx, u in enumerate(units, 1):
        photo = u.unit_photo_path or u.item.default_photo_path or "Belum ada foto"
        row_data = [
            idx,
            u.unit_code,
            f"{u.item.pokja.code} - {u.item.pokja.name}",
            u.item.name,
            u.item.brand_model or "-",
            u.location.name,
            u.condition_status.value,
            u.lifecycle_status.value,
            photo,
            u.notes or "-"
        ]
        ws.append(row_data)
        curr_row = ws.max_row
        for col_num in range(1, len(row_data) + 1):
            cell = ws.cell(row=curr_row, column=col_num)
            cell.font = data_font
            cell.border = thin_border
            if col_num in (1, 2, 7, 8):
                cell.alignment = Alignment(horizontal="center")

    for col_idx, col in enumerate(ws.columns, 1):
        max_len = max(len(str(cell.value or '')) for cell in col if cell.row > 2)
        col_letter = get_column_letter(col_idx)
        ws.column_dimensions[col_letter].width = min(max(max_len + 3, 10), 45)

    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)

    filename = f"Inventaris_GKJW_Sukun_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


def _format_unit_response(u: ItemUnit) -> ItemUnitResponse:
    return ItemUnitResponse(
        unit_code=u.unit_code,
        item_id=u.item_id,
        item_name=u.item.name,
        brand_model=u.item.brand_model,
        pokja_code=u.item.pokja.code,
        pokja_name=u.item.pokja.name,
        location_id=u.location_id,
        location_name=u.location.name,
        condition_status=u.condition_status,
        lifecycle_status=u.lifecycle_status,
        unit_photo_path=u.unit_photo_path or u.item.default_photo_path,
        acquisition_date=u.acquisition_date,
        notes=u.notes,
        decommissioned_at=u.decommissioned_at,
        decommission_reason=u.decommission_reason,
        created_at=u.created_at,
        updated_at=u.updated_at
    )
