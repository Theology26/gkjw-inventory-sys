from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.api.deps import get_db, get_current_user
from app.models.pokja import Pokja
from app.models.item import Item
from app.models.item_unit import ItemUnit
from app.models.user import User
from app.schemas.pokja import PokjaResponse

router = APIRouter(prefix="/pokja", tags=["Master POKJA"])


@router.get("", response_model=List[PokjaResponse])
def get_all_pokja(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mengambil daftar seluruh 24 POKJA GKJW Sukun beserta nilai sequence stiker terakhir
    dan agregasi total master item & unit fisik.
    """
    pokja_list = db.query(Pokja).order_by(Pokja.code.asc()).all()

    # Hitung total items dan units per pokja
    results = []
    for p in pokja_list:
        total_items = db.query(func.count(Item.id)).filter(Item.pokja_id == p.id).scalar() or 0
        total_units = (
            db.query(func.count(ItemUnit.unit_code))
            .join(Item, Item.id == ItemUnit.item_id)
            .filter(Item.pokja_id == p.id)
            .scalar() or 0
        )
        results.append(
            PokjaResponse(
                id=p.id,
                code=p.code,
                name=p.name,
                last_sequence=p.last_sequence,
                total_items=total_items,
                total_units=total_units,
                created_at=p.created_at
            )
        )

    return results

