import csv
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.pokja import Pokja
from app.models.user import User, UserRole

def seed_pokja_users():
    """
    Skrip AMAN & NON-DESTRUKTIF untuk mendaftarkan 25 akun resmi GKJW Sukun:
    - 1 Akun Super Admin: 'admin_sukun'
    - 24 Akun Petugas Komisi: 'petugas_<kode>' (e.g. petugas_mvi, petugas_mau, petugas_msg, dll.)
    - 1 Akun Alias Pengujian: 'petugas_pokja'

    CATATAN KEAMANAN:
    Skrip ini TIDAK MENGHAPUS tabel atau data inventaris yang sudah ada di database produksi.
    """
    print("=" * 70)
    print("SISTEM INFORMASI INVENTARIS & ARSIP GKJW SUKUN v2.0")
    print("Pembaruan 25 Akun Resmi Pengurus (Aman untuk Server Produksi)")
    print("=" * 70)

    db = SessionLocal()
    try:
        # 1. Pastikan Super Admin Ada
        admin = db.query(User).filter(User.username == "admin_sukun").first()
        if not admin:
            admin = User(
                username="admin_sukun",
                name="Super Admin Inventaris",
                email="multimedia.gkjwsukun@gmail.com",
                password_hash=get_password_hash("AdminGKJW2025!"),
                role=UserRole.SUPER_ADMIN,
                pokja_id=None,
                is_active=True
            )
            db.add(admin)
            print(" [+] Akun Super Admin 'admin_sukun' berhasil dibuat.")
        else:
            print(" [i] Akun Super Admin 'admin_sukun' sudah aktif.")

        # 2. Ambil seluruh 24 POKJA dari database
        all_pokjas = db.query(Pokja).order_by(Pokja.id.asc()).all()
        if not all_pokjas:
            print(" [!] PERINGATAN: Tabel pokja masih kosong. Membaca master_pokja.csv...")
            data_dir = Path(__file__).resolve().parents[1] / "data"
            pokja_file = data_dir / "master_pokja.csv"
            with open(pokja_file, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    p = Pokja(
                        id=int(row["ID"]),
                        name=row["Nama"].strip(),
                        code=row["Extra"].strip().upper(),
                        last_sequence=0
                    )
                    db.add(p)
            db.commit()
            all_pokjas = db.query(Pokja).order_by(Pokja.id.asc()).all()

        print(f"\n[i] Memproses 24 Akun Petugas Komisi / POKJA...")
        created_count = 0
        updated_count = 0

        default_petugas_hash = get_password_hash("PetugasGKJW2025!")

        for p in all_pokjas:
            username = f"petugas_{p.code.lower()}"
            name = f"Petugas {p.name}"

            user = db.query(User).filter(User.username == username).first()
            if not user:
                user = User(
                    username=username,
                    name=name,
                    email="multimedia.gkjwsukun@gmail.com",
                    password_hash=default_petugas_hash,
                    role=UserRole.POKJA_ADMIN,
                    pokja_id=p.id,
                    is_active=True
                )
                db.add(user)
                created_count += 1
                print(f" [+] Dibuat: {username:<15} -> {p.code} ({p.name})")
            else:
                user.name = name
                user.role = UserRole.POKJA_ADMIN
                user.pokja_id = p.id
                user.is_active = True
                updated_count += 1
                print(f" [✓] Sinkron: {username:<15} -> {p.code} ({p.name})")

        # 3. Akun Alias 'petugas_pokja' untuk kompatibilitas
        alias_user = db.query(User).filter(User.username == "petugas_pokja").first()
        if not alias_user:
            alias_user = User(
                username="petugas_pokja",
                name="Petugas POKJA (MVI)",
                email="multimedia.gkjwsukun@gmail.com",
                password_hash=default_petugas_hash,
                role=UserRole.POKJA_ADMIN,
                pokja_id=1,
                is_active=True
            )
            db.add(alias_user)
            print(" [+] Akun alias 'petugas_pokja' (MVI) berhasil dibuat.")
        else:
            alias_user.role = UserRole.POKJA_ADMIN
            alias_user.pokja_id = 1
            alias_user.is_active = True

        db.commit()

        total_users = db.query(User).count()
        print("\n" + "=" * 70)
        print("SINKRONISASI AKUN BERHASIL 100%!")
        print(f"• Total Akun di Database   : {total_users} Akun")
        print(f"• Akun Baru Didaftarkan    : {created_count} Akun")
        print(f"• Akun Diperbarui/Disinkron: {updated_count} Akun")
        print("=" * 70)

    except Exception as e:
        db.rollback()
        print(f"\n[!] TERJADI KESALAHAN: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_pokja_users()
