import csv
import sys
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.database import engine, Base, SessionLocal
from app.core.security import get_password_hash
from app.models.pokja import Pokja
from app.models.user import User, UserRole
from app.models.location import Location
from app.models.item import Item
from app.models.item_unit import ItemUnit, ConditionStatus, LifecycleStatus
from app.models.history_log import UnitHistoryLog, HistoryActionType
from app.models.document import ChurchDocument

def reset_and_seed():
    print("=" * 70)
    print("SISTEM INFORMASI INVENTARIS & ARSIP GKJW SUKUN v2.0")
    print("Reset Basis Data Total & Seed Master Data Riil Gereja...")
    print("=" * 70)

    # 1. DROP ALL AND CREATE ALL TABLES
    print("[1/6] Menghapus dan membuat ulang seluruh tabel...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("      -> Skema 7 tabel relasional 3NF berhasil dibuat bersih!")

    db = SessionLocal()
    try:
        data_dir = Path(__file__).resolve().parents[1] / "data"

        # 2. SEED 24 MASTER POKJA
        print("[2/6] Memasukkan Master 24 Komisi / POKJA GKJW Sukun...")
        pokja_file = data_dir / "master_pokja.csv"
        pokja_map = {}
        with open(pokja_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                p_id = int(row["ID"])
                p_name = row["Nama"].strip()
                p_code = row["Extra"].strip().upper()
                pokja = Pokja(
                    id=p_id,
                    code=p_code,
                    name=p_name,
                    last_sequence=0
                )
                db.add(pokja)
                pokja_map[p_id] = pokja
                pokja_map[p_code] = pokja
        db.commit()
        print(f"      -> {len(pokja_map) // 2} Komisi resmi berhasil didaftarkan.")

        # 3. SEED 44 MASTER LOKASI
        print("[3/6] Memasukkan Master 44 Ruangan / Lokasi GKJW Sukun...")
        lokasi_file = data_dir / "master_lokasi.csv"
        lokasi_map = {}
        with open(lokasi_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                l_id = int(row["ID"])
                l_name = row["Nama"].strip()
                l_extra = row.get("Extra", "").strip() or None
                loc = Location(
                    id=l_id,
                    name=l_name,
                    building_zone="Kompleks GKJW Sukun",
                    extra=l_extra
                )
                db.add(loc)
                lokasi_map[l_id] = loc
        db.commit()
        print(f"      -> {len(lokasi_map)} Titik lokasi / ruangan berhasil didaftarkan.")

        # 4. SEED USER ACCOUNTS (Super Admin & 24 Petugas POKJA)
        print("[4/6] Menyiapkan 25 Akun Pengurus Resmi (Super Admin & 24 Petugas Komisi)...")
        admin = User(
            username="admin_sukun",
            name="Super Admin Inventaris",
            email="multimedia.gkjwsukun@gmail.com",
            password_hash=get_password_hash("AdminGKJW2025!"),
            role=UserRole.SUPER_ADMIN,
            is_active=True
        )
        db.add(admin)

        default_petugas_hash = get_password_hash("PetugasGKJW2025!")
        all_pokjas_list = db.query(Pokja).order_by(Pokja.id.asc()).all()
        for p in all_pokjas_list:
            petugas_user = User(
                username=f"petugas_{p.code.lower()}",
                name=f"Petugas {p.name}",
                email="multimedia.gkjwsukun@gmail.com",
                password_hash=default_petugas_hash,
                role=UserRole.POKJA_ADMIN,
                pokja_id=p.id,
                is_active=True
            )
            db.add(petugas_user)

        alias_petugas = User(
            username="petugas_pokja",
            name="Petugas POKJA (MVI)",
            email="multimedia.gkjwsukun@gmail.com",
            password_hash=default_petugas_hash,
            role=UserRole.POKJA_ADMIN,
            pokja_id=1,
            is_active=True
        )
        db.add(alias_petugas)

        db.commit()
        db.refresh(admin)
        print(f"      -> 25 Akun Resmi ('admin_sukun' + 24 Petugas Komisi) siap digunakan.")

        # 5. LOAD MASTER JENIS BARANG (Kategori & Nama Barang)
        print("[5/6] Membaca Master Jenis Barang...")
        jenis_file = data_dir / "master_jenis.csv"
        jenis_map = {}
        with open(jenis_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                j_id = int(row["ID"])
                j_name = row["Nama"].strip()
                jenis_map[j_id] = j_name
        print(f"      -> {len(jenis_map)} Jenis barang termuat dalam kamus master.")

        # 6. IMPORT 279 INVENTARIS FISIK DENGAN NORMALISASI RELASIONAL (3NF)
        print("[6/6] Melakukan migrasi 279 unit inventaris riil...")
        inv_file = data_dir / "legacy_inventory.csv"
        
        condition_lookup = {
            "baik": ConditionStatus.BAIK,
            "kurang baik": ConditionStatus.KURANG_BAIK,
            "rusak": ConditionStatus.RUSAK_BERAT,
        }

        # Cache master items: (pokja_id, item_name, brand_model) -> Item
        item_cache = {}
        pokja_max_seq = {}
        total_units_imported = 0

        with open(inv_file, mode="r", encoding="utf-8") as f:
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

                raw_pokja_id = row.get("POKJA_ID", "").strip()
                pokja_id = int(raw_pokja_id) if raw_pokja_id.isdigit() else pokja_map[pokja_code].id

                # Track sequence per pokja
                pokja_max_seq[pokja_code] = max(pokja_max_seq.get(pokja_code, 0), seq_num)

                # Determine Item Name & Brand/Model from JENIS_ID and MERK/MODEL
                raw_jenis_id = row.get("JENIS_ID", "").strip()
                jenis_name = "Barang Inventaris"
                if raw_jenis_id.isdigit():
                    j_id = int(raw_jenis_id)
                    jenis_name = jenis_map.get(j_id, f"Barang #{j_id}")

                raw_model = (row.get("MERK/MODEL") or "").strip()
                if not raw_model or raw_model == "-":
                    item_name = jenis_name
                    brand_model = "-"
                else:
                    item_name = jenis_name
                    brand_model = raw_model

                # Get or Create Master Catalog Item (Level 1 Normalization)
                cache_key = (pokja_id, item_name, brand_model)
                item = item_cache.get(cache_key)
                if not item:
                    item = Item(
                        pokja_id=pokja_id,
                        name=item_name,
                        brand_model=brand_model,
                        category="Inventaris Gereja"
                    )
                    db.add(item)
                    db.flush()
                    item_cache[cache_key] = item

                # Map Condition
                raw_cond = (row.get("KEADAAN") or "Baik").strip().lower()
                condition = condition_lookup.get(raw_cond, ConditionStatus.BAIK)

                # Map Location ID
                raw_loc_id = row.get("LOKASI_ID", "").strip()
                loc_id = int(raw_loc_id) if raw_loc_id.isdigit() and int(raw_loc_id) in lokasi_map else 30

                # Parse Timestamp
                raw_time = row.get("TIMESTAMP", "").strip()
                created_dt = datetime.now()
                if raw_time:
                    try:
                        created_dt = datetime.strptime(raw_time, "%d/%m/%Y %H:%M:%S")
                    except ValueError:
                        pass

                # Create Physical Labeled Unit (Level 2 Normalization)
                unit = ItemUnit(
                    unit_code=unit_code,
                    item_id=item.id,
                    location_id=loc_id,
                    condition_status=condition,
                    lifecycle_status=LifecycleStatus.ACTIVE,
                    notes=f"Data migrasi resmi GKJW Sukun",
                    created_by=admin.id,
                    created_at=created_dt
                )
                db.add(unit)

                # Log initial history trail
                log = UnitHistoryLog(
                    unit_code=unit_code,
                    action_type=HistoryActionType.CREATED,
                    old_value=None,
                    new_value=f"Kondisi: {condition.value}",
                    remarks="Migrasi inventaris awal dari spreadsheet master",
                    changed_by=admin.id,
                    created_at=created_dt
                )
                db.add(log)
                total_units_imported += 1

        # Synchronize Atomic Sequences on Pokja
        for p_code, max_seq in pokja_max_seq.items():
            p = pokja_map.get(p_code)
            if p:
                p.last_sequence = max_seq
                print(f"      -> POKJA {p_code}: Sequence dikunci pada nomor {max_seq}")

        db.commit()
        print("\n" + "=" * 70)
        print("MIGRASI DAN INISIALISASI DATABASE MASTER SUKSES 100%!")
        print(f"• Total Master POKJA    : {db.query(Pokja).count()} Komisi")
        print(f"• Total Master Lokasi   : {db.query(Location).count()} Ruangan")
        print(f"• Total Master Katalog  : {db.query(Item).count()} Tipe Barang (Terkelompok)")
        print(f"• Total Unit Fisik      : {db.query(ItemUnit).count()} Unit Berstiker")
        print(f"• Total Riwayat Mutasi  : {db.query(UnitHistoryLog).count()} Log Audit Trail")
        print("=" * 70)

    except Exception as e:
        db.rollback()
        print(f"\n[!] TERJADI KESALAHAN: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    reset_and_seed()
