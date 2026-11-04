-- ==============================================================================
-- SISTEM INFORMASI INVENTARIS & ARSIP DOKUMEN GKJW SUKUN (v2.0 Standalone Web)
-- File: database/schema.sql
-- Engine Target: MySQL 8.0+ / MariaDB 10.5+
-- Karakteristik: 3NF Relational, Anti-Redundansi, Immutable Unit IDs, Audit Trail
-- ==============================================================================

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS church_documents;
DROP TABLE IF EXISTS unit_history_logs;
DROP TABLE IF EXISTS item_units;
DROP TABLE IF EXISTS items;
DROP TABLE IF EXISTS locations;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS pokja;

SET FOREIGN_KEY_CHECKS = 1;

-- ------------------------------------------------------------------------------
-- 1. TABEL POKJA / KOMISI (24 POKJA + Atomic Sequence Tracker)
-- ------------------------------------------------------------------------------
-- Kolom `last_sequence` bertindak sebagai pencatat nomor urut stiker fisik tertinggi.
-- Pada saat transaksi penambahan barang (Bulk Create), row POKJA dikunci dengan:
-- `SELECT last_sequence, code FROM pokja WHERE id = :id FOR UPDATE;`
-- Nomor urut TIDAK PERNAH mundur saat barang dihapus / decommission.
CREATE TABLE pokja (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code CHAR(3) NOT NULL UNIQUE COMMENT 'Kode 3 huruf POKJA: MAU, MVI, KTP, dll.',
    name VARCHAR(120) NOT NULL UNIQUE COMMENT 'Nama resmi komisi / POKJA',
    last_sequence INT NOT NULL DEFAULT 0 COMMENT 'Counter nomor urut stiker terakhir (Anti-Reset)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 2. TABEL PENGGUNA (Users & RBAC)
-- ------------------------------------------------------------------------------
-- Role terbagi menjadi:
-- - SUPER_ADMIN : Hak akses penuh (Majelis / Tim Inventaris)
-- - POKJA_ADMIN : Mengelola barang di POKJA yang ditugaskan (pokja_id)
-- - VIEWER      : Hanya melihat katalog, riwayat, dan mengunduh laporan
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('SUPER_ADMIN', 'POKJA_ADMIN', 'VIEWER') NOT NULL DEFAULT 'VIEWER',
    pokja_id INT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_users_pokja FOREIGN KEY (pokja_id) REFERENCES pokja(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 3. TABEL MASTER LOKASI / RUANGAN (Locations)
-- ------------------------------------------------------------------------------
-- Menghilangkan inkonsistensi input lokasi (mencegah typo: R. Mulmed vs Ruang Audio).
CREATE TABLE locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE COMMENT 'Contoh: Gedung Gereja, Ruang Mulmed Audio, Balepamitran',
    building_zone VARCHAR(100) NULL COMMENT 'Contoh: Gedung Utama, Gedung Timur, Pastori',
    room_photo_path VARCHAR(255) NULL COMMENT 'Relative path foto sudut lemari/ruangan',
    description TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 4. TABEL KATALOG MASTER BARANG (Items - Level 1 Normalisasi)
-- ------------------------------------------------------------------------------
-- Mengeliminasi duplikasi ribuan baris pada Google Sheets lama.
-- Satu Master Item mewakili jenis barang (misal: "Mic Wireless - KREZT KRU-4810A").
-- Unit fisik berlabel disimpan terpisah di tabel `item_units`.
CREATE TABLE items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pokja_id INT NOT NULL COMMENT 'POKJA penanggung jawab katalog barang',
    name VARCHAR(150) NOT NULL COMMENT 'Nama umum: Mic Wireless, Kursi Lipat, dsb.',
    brand_model VARCHAR(150) NOT NULL DEFAULT '-' COMMENT 'Merk / Model: KREZT KRU-4810A, Chitose, dsb.',
    category VARCHAR(80) NULL COMMENT 'Kategori: Elektronik, Furniture, Alat Musik, Kabel, dsb.',
    default_photo_path VARCHAR(255) NULL COMMENT 'Relative path foto katalog (storage/uploads/photos/items/)',
    description TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_items_pokja FOREIGN KEY (pokja_id) REFERENCES pokja(id) ON DELETE RESTRICT,
    UNIQUE KEY uq_pokja_item_brand (pokja_id, name, brand_model),
    INDEX idx_items_pokja (pokja_id),
    INDEX idx_items_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 5. TABEL UNIT FISIK BERLABEL (Item Units - Level 2 Normalisasi)
-- ------------------------------------------------------------------------------
-- 1 Baris = 1 Stiker Fisik Berlabel di GKJW Sukun (`MAU-001`, `MVI-062`, dst.)
-- DILARANG MENGGUNAKAN HARD DELETE (`DELETE FROM item_units`).
-- Barang rusak total / musnah diubah ke `lifecycle_status = 'DECOMMISSIONED'`.
CREATE TABLE item_units (
    unit_code VARCHAR(15) NOT NULL PRIMARY KEY COMMENT 'Contoh: MAU-001 (Immutable Primary Key)',
    item_id INT NOT NULL COMMENT 'Relasi ke master katalog items.id',
    location_id INT NOT NULL COMMENT 'Lokasi fisik unit saat ini',
    condition_status ENUM('BAIK', 'KURANG_BAIK', 'RUSAK_BERAT') NOT NULL DEFAULT 'BAIK',
    lifecycle_status ENUM('ACTIVE', 'BORROWED', 'MAINTENANCE', 'DECOMMISSIONED') NOT NULL DEFAULT 'ACTIVE',
    unit_photo_path VARCHAR(255) NULL COMMENT 'Foto khusus kondisi unit jika berbeda dari foto katalog',
    acquisition_date DATE NULL COMMENT 'Tanggal perolehan / pembelian',
    notes TEXT NULL COMMENT 'Catatan fisik khusus (misal: tombol mic agak goyang)',
    decommissioned_at TIMESTAMP NULL COMMENT 'Waktu penonaktifan jika rusak total/dimusnahkan',
    decommission_reason TEXT NULL COMMENT 'Alasan penonaktifan & nomor Berita Acara Majelis',
    created_by INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_units_item FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE RESTRICT,
    CONSTRAINT fk_units_location FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE RESTRICT,
    CONSTRAINT fk_units_creator FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_units_item (item_id),
    INDEX idx_units_location (location_id),
    INDEX idx_units_condition (condition_status),
    INDEX idx_units_lifecycle (lifecycle_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 6. TABEL RIWAYAT MUTASI & AUDIT TRAIL (Unit History Logs)
-- ------------------------------------------------------------------------------
-- Mencatat otomatis setiap perubahan status kondisi, perpindahan lokasi, dan arsip.
CREATE TABLE unit_history_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    unit_code VARCHAR(15) NOT NULL,
    changed_by INT NULL,
    action_type ENUM('CREATED', 'CONDITION_CHANGED', 'LOCATION_MOVED', 'DECOMMISSIONED', 'RESTORED') NOT NULL,
    old_value VARCHAR(255) NULL,
    new_value VARCHAR(255) NULL,
    remarks TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_logs_unit FOREIGN KEY (unit_code) REFERENCES item_units(unit_code) ON DELETE RESTRICT,
    CONSTRAINT fk_logs_user FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_logs_unit (unit_code),
    INDEX idx_logs_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 7. TABEL ARSIP DOKUMEN GEREJA (Church Documents)
-- ------------------------------------------------------------------------------
-- Menyimpan berkas legal, nota pembelian, kartu garansi, manual book, sertifikat, & SK.
CREATE TABLE church_documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    doc_number VARCHAR(100) NULL COMMENT 'Nomor surat / nomor nota',
    title VARCHAR(200) NOT NULL COMMENT 'Judul dokumen / berkas arsip',
    pokja_id INT NULL,
    related_item_id INT NULL COMMENT 'Tautan opsional ke katalog barang',
    file_path VARCHAR(255) NOT NULL COMMENT 'Path file di storage/uploads/documents/{pokja_code}/',
    file_type VARCHAR(50) NOT NULL COMMENT 'Ekstensi mime: pdf, jpg, png, webp, docx',
    file_size_bytes BIGINT NOT NULL DEFAULT 0,
    physical_storage_loc VARCHAR(150) NULL COMMENT 'Lokasi map arsip fisik (misal: Lemari Arsip Kantor Lt 1)',
    uploaded_by INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_docs_pokja FOREIGN KEY (pokja_id) REFERENCES pokja(id) ON DELETE SET NULL,
    CONSTRAINT fk_docs_item FOREIGN KEY (related_item_id) REFERENCES items(id) ON DELETE SET NULL,
    CONSTRAINT fk_docs_uploader FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_docs_pokja (pokja_id),
    INDEX idx_docs_item (related_item_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==============================================================================
-- SEED DATA AWAL: 24 POKJA / KOMISI GKJW SUKUN
-- ==============================================================================
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
ON DUPLICATE KEY UPDATE name = VALUES(name);

-- ==============================================================================
-- SEED DATA AWAL: MASTER LOKASI STANDAR GKJW SUKUN
-- ==============================================================================
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
ON DUPLICATE KEY UPDATE building_zone = VALUES(building_zone);

-- ==============================================================================
-- SEED DATA AWAL: PENGGUNA DEFAULT (SUPER ADMIN)
-- Password default: 'AdminGKJW2025!' (Hash bcrypt pre-calculated)
-- ==============================================================================
INSERT INTO users (name, email, password_hash, role, pokja_id, is_active) VALUES
('Super Admin Inventaris', 'admin@gkjwsukun.org', '$2b$12$e8Y6eYq/t2qQYqI5b5XkCeym1M6Vz8l9oR1jQvYpM0zX7fX9tM9uS', 'SUPER_ADMIN', NULL, TRUE)
ON DUPLICATE KEY UPDATE name = VALUES(name);

