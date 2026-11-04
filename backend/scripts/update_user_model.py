import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.database import engine
from sqlalchemy import text

def update_schema():
    with engine.connect() as conn:
        res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'users'")).fetchall()
        cols = [r[0] for r in res]
        print("Columns in users:", cols)
        if "username" not in cols:
            print("Adding username column...")
            conn.execute(text("ALTER TABLE users ADD COLUMN username VARCHAR(50) UNIQUE;"))
            conn.commit()
            print("username column added!")
        else:
            print("username column already exists.")

if __name__ == "__main__":
    update_schema()

