from typing import List, Optional
from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.api.deps import get_db, get_current_user, require_admin
from app.core.media import compress_and_save_image
from app.models.location import Location
from app.models.item_unit import ItemUnit
from app.models.user import User
from app.schemas.location import LocationResponse

router = APIRouter(prefix="/locations", tags=["Master Lokasi"])


@router.get("", response_model=List[LocationResponse])
def get_locations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mengambil daftar seluruh master ruangan / lokasi penyimpanan GKJW Sukun.
    """
    locations = db.query(Location).order_by(Location.name.asc()).all()
    results = []
    for loc in locations:
        count = db.query(func.count(ItemUnit.unit_code)).filter(ItemUnit.location_id == loc.id).scalar() or 0
        results.append(
            LocationResponse(
                id=loc.id,
                name=loc.name,
                building_zone=loc.building_zone,
                room_photo_path=loc.room_photo_path,
                description=loc.description,
                total_units=count,
                created_at=loc.created_at
            )
        )
    return results


@router.post("", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
def create_location(
    name: str = Form(..., min_length=2, max_length=100),
    building_zone: Optional[str] = Form(None, max_length=100),
    description: Optional[str] = Form(None),
    photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Menambahkan lokasi/ruangan baru beserta foto sudut ruangan (otomatis dikompresi ke .webp).
    """
    clean_name = name.strip()
    existing = db.query(Location).filter(Location.name == clean_name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Lokasi dengan nama '{clean_name}' sudah ada."
        )

    photo_path = None
    if photo and photo.filename:
        photo_path = compress_and_save_image(photo, subfolder="photos/locations")

    new_loc = Location(
        name=clean_name,
        building_zone=building_zone.strip() if building_zone else None,
        description=description.strip() if description else None,
        room_photo_path=photo_path
    )
    db.add(new_loc)
    db.commit()
    db.refresh(new_loc)

    return LocationResponse(
        id=new_loc.id,
        name=new_loc.name,
        building_zone=new_loc.building_zone,
        room_photo_path=new_loc.room_photo_path,
        description=new_loc.description,
        total_units=0,
        created_at=new_loc.created_at
    )

