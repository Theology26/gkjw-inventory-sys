-- ==============================================================================
-- SISTEM INFORMASI INVENTARIS & ARSIP DOKUMEN GKJW SUKUN (v2.0 Standalone Web)
-- File: database/schema_postgres.sql
-- Engine Target: PostgreSQL 14+ / 16
-- ==============================================================================

-- Drop existing tables if reinitializing
DROP TABLE IF EXISTS church_documents CASCADE;
DROP TABLE IF EXISTS unit_history_logs CASCADE;
DROP TABLE IF EXISTS item_units CASCADE;
DROP TABLE IF EXISTS items CASCADE;
DROP TABLE IF EXISTS locations CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS pokja CASCADE;

-- Custom ENUM Types
DROP TYPE IF EXISTS user_role;
DROP TYPE IF EXISTS condition_status_enum;
DROP TYPE IF EXISTS lifecycle_status_enum;
DROP TYPE IF EXISTS history_action_type;

CREATE TYPE user_role AS ENUM ('SUPER_ADMIN', 'POKJA_ADMIN', 'VIEWER');
CREATE TYPE condition_status_enum AS ENUM ('BAIK', 'KURANG_BAIK', 'RUSAK_BERAT');
CREATE TYPE lifecycle_status_enum AS ENUM ('ACTIVE', 'BORROWED', 'MAINTENANCE', 'DECOMMISSIONED');
CREATE TYPE history_action_type AS ENUM ('CREATED', 'CONDITION_CHANGED', 'LOCATION_MOVED', 'DECOMMISSIONED', 'RESTORED');

-- 1. POKJA
CREATE TABLE pokja (
    id SERIAL PRIMARY KEY,
    code VARCHAR(3) NOT NULL UNIQUE,
    name VARCHAR(120) NOT NULL UNIQUE,
    last_sequence INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. USERS
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'VIEWER',
    pokja_id INT NULL REFERENCES pokja(id) ON DELETE SET NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. LOCATIONS
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    building_zone VARCHAR(100) NULL,
    room_photo_path VARCHAR(255) NULL,
    description TEXT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. ITEMS (Master Katalog)
CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    pokja_id INT NOT NULL REFERENCES pokja(id) ON DELETE RESTRICT,
    name VARCHAR(150) NOT NULL,
    brand_model VARCHAR(150) NOT NULL DEFAULT '-',
    category VARCHAR(80) NULL,
    default_photo_path VARCHAR(255) NULL,
    description TEXT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_pokja_item_brand UNIQUE (pokja_id, name, brand_model)
);

CREATE INDEX idx_items_pokja ON items(pokja_id);
CREATE INDEX idx_items_category ON items(category);

-- 5. ITEM_UNITS (Unit Fisik Berlabel)
CREATE TABLE item_units (
    unit_code VARCHAR(15) PRIMARY KEY,
    item_id INT NOT NULL REFERENCES items(id) ON DELETE RESTRICT,
    location_id INT NOT NULL REFERENCES locations(id) ON DELETE RESTRICT,
    condition_status condition_status_enum NOT NULL DEFAULT 'BAIK',
    lifecycle_status lifecycle_status_enum NOT NULL DEFAULT 'ACTIVE',
    unit_photo_path VARCHAR(255) NULL,
    acquisition_date DATE NULL,
    notes TEXT NULL,
    decommissioned_at TIMESTAMP WITH TIME ZONE NULL,
    decommission_reason TEXT NULL,
    created_by INT NULL REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_units_item ON item_units(item_id);
CREATE INDEX idx_units_location ON item_units(location_id);
CREATE INDEX idx_units_condition ON item_units(condition_status);
CREATE INDEX idx_units_lifecycle ON item_units(lifecycle_status);

-- 6. UNIT_HISTORY_LOGS (Audit Trail)
CREATE TABLE unit_history_logs (
    id BIGSERIAL PRIMARY KEY,
    unit_code VARCHAR(15) NOT NULL REFERENCES item_units(unit_code) ON DELETE RESTRICT,
    changed_by INT NULL REFERENCES users(id) ON DELETE SET NULL,
    action_type history_action_type NOT NULL,
    old_value VARCHAR(255) NULL,
    new_value VARCHAR(255) NULL,
    remarks TEXT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_logs_unit ON unit_history_logs(unit_code);
CREATE INDEX idx_logs_created_at ON unit_history_logs(created_at);

-- 7. CHURCH_DOCUMENTS (Arsip Berkas)
CREATE TABLE church_documents (
    id SERIAL PRIMARY KEY,
    doc_number VARCHAR(100) NULL,
    title VARCHAR(200) NOT NULL,
    pokja_id INT NULL REFERENCES pokja(id) ON DELETE SET NULL,
    related_item_id INT NULL REFERENCES items(id) ON DELETE SET NULL,
    file_path VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size_bytes BIGINT NOT NULL DEFAULT 0,
    physical_storage_loc VARCHAR(150) NULL,
    uploaded_by INT NULL REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_docs_pokja ON church_documents(pokja_id);
CREATE INDEX idx_docs_item ON church_documents(related_item_id);

-- SEED 24 POKJA
INSERT INTO pokja (code, name, last_sequence) VALUES
('KTP', 'Katekisasi & Perkawinan', 0),
('MSG', 'Musik Gerejawi', 0),
('MVI', 'Multimedia Visual', 0),
('MAU', 'Multimedia Audio', 0),
('PAN', 'Pelayanan Anak', 0),
('PRE', 'Pelayanan Remaja', 0),
('PPM', 'Pembinaan Pemuda dan Mahasiswa', 0),
('ARP', 'Perlindungan & Pendampingan Anak Remaja Pemuda', 0),
('PWW', 'Pembinaan Peranan Wanita', 0),
('ADY', 'Pembinaan Peranan Warga Adiyuswa', 0),
('KPT', 'Pembinaan Teologi', 0),
('GKS', 'Pelayanan Tenaga Kesehatan (GAKES)', 0),
('GRU', 'Pelayanan Tenaga Guru (GARU)', 0),
('HJU', 'Gereja Hijau', 0),
('TBN', 'Pelayanan Tanggul Bencana', 0),
('WRA', 'Pelayanan Kewirausahaan', 0),
('DUK', 'Pelayanan Duka', 0),
('INV', 'Inventaris & Perpustakaan', 0),
('URT', 'Pelayanan URTG', 0),
('KMN', 'Keamanan', 0),
('PBG', 'Pembangunan', 0),
('LIT', 'Perencanaan Penelitian & Pengembangan', 0),
('PBJ', 'Pengawasan Perbendaharaan Jemaat', 0),
('UUM', 'Antar Umat Beragama', 0)
ON CONFLICT (code) DO NOTHING;

-- SEED MASTER LOKASI
INSERT INTO locations (name, building_zone, description) VALUES
('Gedung Gereja Utama', 'Gedung Utama', 'Ruang ibadah raya utama'),
('Balkon Gereja', 'Gedung Utama', 'Lantai 2 balkon ruang ibadah'),
('Ruang Multimedia Audio', 'Gedung Utama', 'Ruang operator audio & sound system'),
('Ruang Multimedia Visual', 'Gedung Utama', 'Ruang siaran streaming & operator visual'),
('Konsistori', 'Gedung Utama', 'Ruang persiapan majelis dan pelayan ibadah'),
('Balepamitran', 'Gedung Timur', 'Gedung serbaguna GKJW Sukun'),
('Ruang Anak (KPAR)', 'Gedung Timur', 'Ruang kelas pelayanan anak'),
('Ruang Remaja (KPR)', 'Gedung Timur', 'Ruang persekutuan remaja'),
('Ruang Pemuda (KPPM)', 'Gedung Timur', 'Ruang persekutuan pemuda'),
('Kantor Majelis Jemaat', 'Gedung Utama Lt 1', 'Ruang sekretariat dan tata usaha kantor gereja'),
('Gudang URTG', 'Gedung Belakang', 'Gudang penyimpanan perlengkapan umum & kebersihan')
ON CONFLICT (name) DO NOTHING;

-- SEED SUPER ADMIN
INSERT INTO users (name, email, password_hash, role, pokja_id, is_active) VALUES
('Super Admin Inventaris', 'admin@gkjwsukun.org', '$2b$12$e8Y6eYq/t2qQYqI5b5XkCeym1M6Vz8l9oR1jQvYpM0zX7fX9tM9uS', 'SUPER_ADMIN', NULL, TRUE)
ON CONFLICT (email) DO NOTHING;

