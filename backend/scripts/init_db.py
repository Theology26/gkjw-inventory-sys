"""
SISTEM INFORMASI INVENTARIS & ARSIP GKJW SUKUN v2.0
Inisialisasi Skema & Master Seeding Database Resmi
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.reset_and_seed_all import reset_and_seed

if __name__ == "__main__":
    reset_and_seed()
