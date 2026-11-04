import csv
import sys
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.database import SessionLocal
from app.models.pokja import Pokja
from app.models.location import Location
from app.models.item import Item
from app.models.item_unit import ItemUnit, ConditionStatus, LifecycleStatus
from app.models.history_log import UnitHistoryLog, HistoryActionType
from app.models.user import User

def import_csv_data():
    csv_path = Path(__file__).resolve().parents[1] / "data" / "legacy_inventory.csv"
    if not csv_path.exists():
        print(f"[!] File {csv_path} tidak ditemukan.")
        return

    db = SessionLocal()
    try:
        # Get admin user for changer_id
        admin = db.query(User).filter(User.username == "admin_sukun").first()
        admin_id = admin.id if admin else 1

        # Cache Pokjas
        pokja_map = {p.code: p for p in db.query(Pokja).all()}
        
        # Cache Locations
        locations = db.query(Location).all()
        loc_map = {l.id: l for l in locations}
        
        # Fallback locations by pokja
        pokja_default_loc = {
            "MVI": 4,   # Ruang Multimedia Visual
            "MAU": 3,   # Ruang Multimedia Audio
            "MSG": 1,   # Gedung Gereja Utama
            "URT": 11,  # Gudang URTG
        }

        # Item cache: (pokja_id, brand_or_name) -> Item
        item_cache = {}
        for itm in db.query(Item).all():
            item_cache[(itm.pokja_id, (itm.name or "").strip().lower(), (itm.brand_model or "").strip().lower())] = itm

        condition_map = {
            "baik": ConditionStatus.BAIK,
            "kurang baik": ConditionStatus.KURANG_BAIK,
            "rusak": ConditionStatus.RUSAK_BERAT,
        }

        pokja_max_seq = {}
        imported_count = 0
        skipped_count = 0

        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                unit_code = row["ID BARANG"].strip()
                if not unit_code or "-" not in unit_code:
                    continue

                pokja_code, seq_str = unit_code.split("-", 1)
                try:
                    seq_num = int(seq_str)
                except ValueError:
                    continue

                pokja = pokja_map.get(pokja_code)
                if not pokja:
                    print(f"[!] POKJA '{pokja_code}' tidak terdaftar di sistem. Lewati {unit_code}.")
                    continue

                # Track max sequence
                pokja_max_seq[pokja_code] = max(pokja_max_seq.get(pokja_code, 0), seq_num)

                # Check if unit already exists
                existing_unit = db.query(ItemUnit).filter(ItemUnit.unit_code == unit_code).first()
                if existing_unit:
                    skipped_count += 1
                    continue

                # Parse timestamp
                raw_time = row.get("TIMESTAMP", "").strip()
                created_dt = datetime.utcnow()
                if raw_time:
                    try:
                        created_dt = datetime.strptime(raw_time, "%d/%m/%Y %H:%M:%S")
                    except ValueError:
                        pass

                raw_model = (row.get("MERK/MODEL") or "").strip()
                if not raw_model or raw_model == "-":
                    jenis_id = row.get("JENIS_ID", "").strip()
                    item_name = f"Perlengkapan {pokja_code} #{jenis_id}" if jenis_id else f"Inventaris {pokja_code}"
                    brand_model = "-"
                else:
                    item_name = raw_model
                    brand_model = raw_model

                # Find or create master catalog Item
                cache_key = (pokja.id, item_name.lower(), brand_model.lower())
                item = item_cache.get(cache_key)
                if not item:
                    item = Item(
                        pokja_id=pokja.id,
                        name=item_name,
                        brand_model=brand_model,
                        category="Umum",
                        created_at=created_dt
                    )
                    db.add(item)
                    db.flush()
                    item_cache[cache_key] = item

                # Map condition
                raw_cond = (row.get("KEADAAN") or "Baik").strip().lower()
                condition = condition_map.get(raw_cond, ConditionStatus.BAIK)

                # Location resolution
                raw_loc_id = row.get("LOKASI_ID", "").strip()
                location_id = None
                if raw_loc_id.isdigit():
                    cand_id = int(raw_loc_id)
                    if cand_id in loc_map:
                        location_id = cand_id

                if not location_id:
                    location_id = pokja_default_loc.get(pokja_code, 1)

                # Create ItemUnit
                unit = ItemUnit(
                    unit_code=unit_code,
                    item_id=item.id,
                    location_id=location_id,
                    condition_status=condition,
                    lifecycle_status=LifecycleStatus.ACTIVE,
                    notes=f"Migrasi data gereja. Lokasi lama #{raw_loc_id}",
                    created_by=admin_id,
                    created_at=created_dt
                )
                db.add(unit)

                # Add history log
                log = UnitHistoryLog(
                    unit_code=unit_code,
                    action_type=HistoryActionType.CREATED,
                    old_value=None,
                    new_value=f"Kondisi: {condition.value}",
                    remarks="Migrasi inventaris gereja awal",
                    changed_by=admin_id,
                    created_at=created_dt
                )
                db.add(log)
                imported_count += 1

        # Update POKJA sequences
        for code, max_seq in pokja_max_seq.items():
            pokja = pokja_map.get(code)
            if pokja:
                if (pokja.last_sequence or 0) < max_seq:
                    pokja.last_sequence = max_seq
                    print(f"[+] POKJA {code}: Sequence diperbarui ke {max_seq}")

        db.commit()
        print(f"\n==========================================")
        print(f"MIGRASI DATA SELESAI:")
        print(f"Total Unit Berhasil Diimpor: {imported_count}")
        print(f"Total Unit Dilewati (Sudah Ada): {skipped_count}")
        print(f"Total Unit Saat Ini di DB: {db.query(ItemUnit).count()}")
        print(f"Total Master Item Saat Ini di DB: {db.query(Item).count()}")
        print(f"==========================================")

    except Exception as e:
        db.rollback()
        print(f"[!] Error saat impor CSV: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    import_csv_data()
