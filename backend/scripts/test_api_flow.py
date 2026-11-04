import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine, SessionLocal
from scripts.init_db import init_database

# Ensure test DB is initialized
init_database()

client = TestClient(app)

print("\n--- [TEST 1] Root & Health Check ---")
r_root = client.get("/")
assert r_root.status_code == 200, r_root.text
print("Root OK:", r_root.json())

r_health = client.get("/health")
assert r_health.status_code == 200, r_health.text
print("Health OK:", r_health.json())

print("\n--- [TEST 2] Authentication (Login) ---")
r_login = client.post("/api/v1/auth/login", json={
    "email": "admin@gkjwsukun.org",
    "password": "AdminGKJW2025!"
})
assert r_login.status_code == 200, r_login.text
auth_data = r_login.json()
token = auth_data["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print(f"Login OK: {auth_data['name']} ({auth_data['role']})")

print("\n--- [TEST 3] Get 24 POKJA ---")
r_pokja = client.get("/api/v1/pokja", headers=headers)
assert r_pokja.status_code == 200, r_pokja.text
pokjas = r_pokja.json()
assert len(pokjas) == 24, f"Expected 24 POKJA, got {len(pokjas)}"
print(f"POKJA OK: {len(pokjas)} POKJA loaded.")

print("\n--- [TEST 4] Get Locations ---")
r_loc = client.get("/api/v1/locations", headers=headers)
assert r_loc.status_code == 200, r_loc.text
locations = r_loc.json()
assert len(locations) >= 11, f"Expected at least 11 locations, got {len(locations)}"
print(f"Locations OK: {len(locations)} locations loaded.")

print("\n--- [TEST 5] Bulk Create Physical Units (Atomic Sequence) ---")
bulk_payload = {
    "pokja_code": "MAU",
    "name": "Mic Wireless",
    "brand_model": "KREZT KRU-4810A",
    "category": "Elektronik",
    "quantity": 4,
    "condition_status": "BAIK",
    "location_id": locations[0]["id"],
    "notes": "Pengadaan unit ibadah raya"
}
r_bulk = client.post("/api/v1/inventory/bulk-create", json=bulk_payload, headers=headers)
assert r_bulk.status_code == 201, r_bulk.text
bulk_res = r_bulk.json()
print("Bulk Create OK:", bulk_res["message"])
print("Generated Codes:", bulk_res["data"]["generated_unit_codes"])
assert bulk_res["data"]["generated_unit_codes"] == ["MAU-001", "MAU-002", "MAU-003", "MAU-004"]

print("\n--- [TEST 6] Inventory Catalog Grouped View ---")
r_cat = client.get("/api/v1/inventory/catalog", headers=headers)
assert r_cat.status_code == 200, r_cat.text
catalogs = r_cat.json()
assert len(catalogs) == 1
assert catalogs[0]["total_units"] == 4
assert catalogs[0]["baik_count"] == 4
print(f"Catalog OK: {catalogs[0]['name']} - Total: {catalogs[0]['total_units']} Baik: {catalogs[0]['baik_count']}")

print("\n--- [TEST 7] Update Condition of Unit MAU-002 ---")
r_update = client.patch(
    "/api/v1/inventory/units/MAU-002",
    json={"condition_status": "KURANG_BAIK", "remarks": "Kabel mic kresek-kresek"},
    headers=headers
)
assert r_update.status_code == 200, r_update.text
print("Unit MAU-002 updated to:", r_update.json()["condition_status"])

print("\n--- [TEST 8] Decommission Unit MAU-003 (Soft Delete) ---")
r_decom = client.post(
    "/api/v1/inventory/units/MAU-003/decommission",
    json={"reason": "Jatuh dan patah modul receiver, disetujui Majelis"},
    headers=headers
)
assert r_decom.status_code == 200, r_decom.text
assert r_decom.json()["lifecycle_status"] == "DECOMMISSIONED"
print("Unit MAU-003 decommissioned successfully.")

print("\n--- [TEST 9] Audit History Log for MAU-002 ---")
r_hist = client.get("/api/v1/inventory/units/MAU-002/history", headers=headers)
assert r_hist.status_code == 200, r_hist.text
history = r_hist.json()
assert len(history) == 2  # CREATED and CONDITION_CHANGED
print(f"Audit Trail OK: {len(history)} log entries found for MAU-002.")
for h in history:
    print(f"  - [{h['action_type']}] {h['old_value']} -> {h['new_value']} ({h['remarks']})")

print("\n========================================================")
print("ALL SYSTEM ARCHITECTURE & LOGIC TESTS PASSED 100%!")
print("========================================================")
