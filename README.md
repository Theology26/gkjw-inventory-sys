# GKJW Sukun Inventory & Document Archive System (v2.0)
### Greja Kristen Jawi Wetan Jemaat Sukun &bull; Malang, Jawa Timur

```
========================================================================================
+ 00.00        SWISS ARCHIVAL & BRUTALIST CRAFT &bull; STANDALONE WEB SYSTEM       + REV.2.0
+ 24.POKJA     GREJA KRISTEN JAWI WETAN &bull; JEMAAT SUKUN &bull; MALANG           + PBJ.SKN
========================================================================================
```

[![System Version](https://img.shields.io/badge/Version-2.0.0--Standalone-141413?style=flat-square&labelColor=F6F5F0)](https://github.com/)
[![Architecture](https://img.shields.io/badge/Architecture-Monorepo%20(FastAPI%20%2B%20Vue%203)-C84B31?style=flat-square&labelColor=141413)](https://github.com/)
[![Database](https://img.shields.io/badge/Database-PostgreSQL%2018%20(3NF)-2D4059?style=flat-square&labelColor=F6F5F0)](https://github.com/)
[![UI Design](https://img.shields.io/badge/Design-Swiss%20Archival%20%2F%20Brutalist%20Craft-2B580C?style=flat-square&labelColor=F6F5F0)](https://github.com/)
[![Zero AI Slop](https://img.shields.io/badge/Zero%20AI%20Slop-Guaranteed-C84B31?style=flat-square&labelColor=141413)](https://github.com/)

---

## 🇬🇧 English Documentation

### 1. Project Overview & Institutional Context
The **GKJW Sukun Inventory & Document Archive System (v2.0)** is an enterprise-grade, standalone web application engineered specifically for **Greja Kristen Jawi Wetan (GKJW) Jemaat Sukun**, Malang, East Java. 

The system transitions the church from legacy flat spreadsheets into a centralized, audited relational repository governed by the **Pengawasan Perbendaharaan Jemaat (PBJ)** across all **24 church commissions (POKJA)**. It guarantees physical accountability by binding every tangible item to an immutable, sequential physical sticker code (e.g., `MVI-012`, `MAU-005`), managing multi-condition bulk acquisitions, compressing field documentation into lightweight WebP media, and locking sensitive church assemblies and financial archives behind strict Role-Based Access Control (RBAC).

---

### 2. Design Philosophy: Swiss Archival & Brutalist Craft
Adhering to strict **Anti-AI-Slop** guardrails, the user interface rejects neon gradients, blurry floating cards, and gratuitous decorations in favor of utilitarian dignity:
* **Palette:** Warm canvas background (`#F6F5F0`), solid tactile ink borders (`1.5px solid #141413`), subtle archival paper surfaces (`#FFFFFF` / `#EEECE1`), and stately church terracotta accents (`#C84B31`).
* **Typography:** Clean architectural sans-serif for UI chrome paired with high-contrast monospace (`JetBrains Mono`) for all physical sticker IDs, sequence counters, timestamps, and currency ledgers.
* **Tactile Affordances:** Hard offset drop shadows (`shadow-[2px_2px_0px_#141413]`), physical button depressions (`translate-x-0.5 translate-y-0.5`), and functional data density.

---

### 3. Monorepo Architecture & Directory Structure

```
c:\Inventaris GKJW SUKUN\
├── backend/                         # FastAPI High-Performance Lightweight Engine
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py             # Database session & JWT Auth dependencies
│   │   │   └── v1/
│   │   │       ├── auth.py         # Login, token issuance & identity resolution
│   │   │       ├── inventory.py    # Bulk create, condition splitter, WebP upload, Excel
│   │   │       ├── documents.py    # Private church archive CRUD & file streaming
│   │   │       └── pokja.py        # 24 Commission sequences & public overview
│   │   ├── core/
│   │   │   ├── config.py           # Environment settings & directory resolver
│   │   │   ├── database.py         # SQLAlchemy engine & session pool
│   │   │   └── security.py         # Bcrypt password hasher & JWT HS256 tokens
│   │   ├── models/                 # SQLAlchemy 3NF Relational ORM Entities
│   │   │   ├── pokja.py            # 24 Commissions with atomic sequence counters
│   │   │   ├── user.py             # User accounts with roles (SUPER_ADMIN, POKJA_ADMIN)
│   │   │   ├── location.py         # Church room mapping
│   │   │   ├── item.py             # Master Item Catalog (anti-redundancy grouping)
│   │   │   ├── item_unit.py        # Physical labeled units with lifecycle status
│   │   │   ├── history_log.py      # Immutable mutation audit trail
│   │   │   └── document.py         # Private church documents & receipts
│   │   ├── schemas/                # Pydantic v2 strict serialization contracts
│   │   └── main.py                 # FastAPI application entrypoint
│   ├── data/
│   │   └── legacy_inventory.csv    # 279 Church legacy inventory records
│   ├── scripts/
│   │   ├── init_db.py              # DDL schema initialization & initial seed
│   │   └── import_church_csv.py    # Automated legacy migration pipeline
│   ├── storage/uploads/            # WebP photos & encrypted document vault
│   ├── requirements.txt            # Python dependencies (FastAPI, SQLAlchemy, Pillow, openpyxl)
│   └── .env.example                # Backend environment configuration template
│
├── frontend/                        # Vue 3 Single Page Application (Vite + Tailwind CSS)
│   ├── public/
│   │   └── Logo Gkjw Hitam.png     # Official church heraldry emblem
│   ├── src/
│   │   ├── api/index.js            # Axios client with automatic Bearer token interceptor
│   │   ├── components/
│   │   │   └── auth/LoginModal.vue # Archival login modal with Esc listener & demo hints
│   │   ├── router/index.js         # Navigation guards (Auth guard for /dashboard & /documents)
│   │   ├── stores/auth.js          # Pinia state management for user session & permissions
│   │   ├── views/
│   │   │   ├── LandingView.vue     # Welcoming animation, SOP cards, 24 POKJA, Scrollspy
│   │   │   ├── DashboardView.vue   # Executive asset summary & atomic sequence tracker
│   │   │   ├── InventoryView.vue   # Catalog accordion, Condition Splitter, Excel & PDF
│   │   │   ├── DocumentsView.vue   # Confidential document archive with mobile upload
│   │   │   └── LoginView.vue       # Standalone login route fallback
│   │   ├── App.vue                 # Dynamic navbar with scrollspy & developer watermark
│   │   └── main.js                 # Application bootstrap
│   ├── package.json                # Frontend packages & scripts
│   ├── tailwind.config.js          # Custom Swiss Archival tokens & typography
│   └── vite.config.js              # Production build optimizations & proxy rules
│
├── .gitignore                       # Strict Git leak-prevention rules
├── .env.example                     # Root environment configuration template
├── MASTER_BLUEPRINT.md              # Software Requirements Specification (SRS) & PRD
├── AGENTS.md                        # AI coding guardrails & database normalization rules
└── README.md                        # Bilingual Documentation (English & Indonesian)
```

---

### 4. Technology Stack

| Layer | Technologies & Libraries | Architectural Purpose |
| :--- | :--- | :--- |
| **Backend** | Python 3.14 / 3.12, FastAPI, SQLAlchemy 2.0, Pydantic v2 | High-throughput async REST API with sub-millisecond execution times. |
| **Database** | PostgreSQL 18 / PostgreSQL 16 | ACID-compliant relational storage in Third Normal Form ($3\text{NF}$). |
| **Image Pipeline** | Pillow (PIL) | Automatic conversion to `.webp` (LANCZOS, max 1280px, quality 80%, $<150\text{ KB}$). |
| **Report Engine** | OpenPyXL & Native Print CSS | Styled `.xlsx` spreadsheet streaming and official Berita Acara PDF layouts. |
| **Frontend** | Vue 3 (Composition API), Vite 5, Pinia | Lightning-fast reactive interface ($< 100\text{ KB}$ initial gzipped bundle). |
| **Styling** | Tailwind CSS v3, PostCSS, JetBrains Mono | Custom Swiss Archival design tokens, tactile borders, zero layout shifts. |

---

### 5. Key System Capabilities

#### A. Two-Tier Relational Normalization (3NF)
Unlike legacy spreadsheets where 20 identical wireless microphones produce 20 duplicated rows with redundant brand and specification text, the system cleanly separates the **Master Item Catalog** (`items`) from **Physical Labeled Units** (`item_units`). 20 identical microphones appear as one clean master row with an expandable accordion detailing individual serials, conditions, and room placements.

#### B. Multi-Condition Form Input (*Condition Splitter*)
When commissioning bulk acquisitions (e.g., 10 microphone units), church officers can split quantities across conditions in a single modal submission (e.g., 4 Good, 3 Minor Damage, 3 Major Damage). The backend locks the commission sequence, creates 10 sequential sticker IDs (e.g., `MAU-001` through `MAU-010`), maps each physical unit to its designated condition, and registers an initial creation record in `unit_history_logs`.

#### C. Strict Role-Based Access Control (RBAC)
* **Public / Warga Jemaat (Read-Only):** The root page (`/`) serves as a public repository showcasing church commission overviews and live aggregated metrics. Add, edit, and delete operations are completely stripped from the UI and protected on the API.
* **Confidential Church Documents (`/documents`):** Sensitive acquisition invoices, purchase receipts, warranties, and Church Assembly Official Reports (*Berita Acara Majelis*) are completely invisible to unauthenticated visitors and guarded by JWT Bearer authorization.

#### D. Mobile-First Field Inspection & WebP Pipeline
Church officers conducting stock opnames across sanctuaries and storage rooms can access the web application on smartphones. All photo upload fields carry `capture="environment"`, automatically prompting the rear camera for instant field photography. Uploaded photos are compressed into lightweight `.webp` files before writing to disk, preserving laptop storage while delivering instant loads over church Wi-Fi.

#### E. Decommissioning & Immutable Audit Trail
Physical sticker IDs are **never deleted or recycled**. If an item is permanently broken or lost, it is marked as `DECOMMISSIONED` accompanied by the official Church Assembly resolution number. The sequence number remains reserved forever, guaranteeing physical ledger integrity.

---

### 6. Local Installation & Setup Guide

#### Prerequisites
* **Python 3.12+** or **Python 3.14**
* **Node.js v20+** or **v24** and **npm**
* **PostgreSQL 16+** or **PostgreSQL 18** running locally on port `5432`

#### Step 1: Database Setup
1. Launch pgAdmin or PostgreSQL shell:
```sql
CREATE DATABASE gkjw_sukun_inventory;
```

#### Step 2: Backend Configuration & Initialization
1. Navigate to the backend directory:
```bash
cd "c:\Inventaris GKJW SUKUN"
```
2. Copy the environment template:
```bash
cp .env.example .env
cp backend/.env.example backend/.env
```
3. Open `backend/.env` and update the database connection string with your local PostgreSQL password:
```ini
DATABASE_URL=postgresql://postgres:your_password@127.0.0.1:5432/gkjw_sukun_inventory
```
4. Install Python dependencies:
```bash
pip install -r backend/requirements.txt
```
5. Initialize the database schema and 24 POKJAs:
```bash
# Windows PowerShell:
$env:PYTHONPATH="backend"
python backend/scripts/init_db.py

# Windows Command Prompt (CMD):
set PYTHONPATH=backend
python backend\scripts\init_db.py
```
6. Import the church's legacy inventory records (279 units):
```bash
python backend/scripts/import_church_csv.py
```
7. Start the FastAPI development server:
```bash
python backend/app/main.py
```
* API Documentation: `http://localhost:8000/docs`
* Health Check: `http://localhost:8000/health`

#### Step 3: Frontend Setup
1. Open a new terminal in the `frontend` folder:
```bash
cd "c:\Inventaris GKJW SUKUN\frontend"
```
2. Install frontend dependencies:
```bash
npm install
```
3. Start the Vite development server:
```bash
npm run dev
```
4. Open your browser at `http://localhost:5173`.

---

```
========================================================================================
Designed & Engineered with precision by Yosia Graceheo Boimau (Theology26)
GKJW Jemaat Sukun Inventory & Document Archive System v2.0
========================================================================================
```

<br />

---
---

## 🇮🇩 Dokumentasi Bahasa Indonesia

### 1. Ikhtisar Sistem & Konteks Kelembagaan
**Sistem Informasi Inventaris & Arsip Dokumen GKJW Sukun (v2.0)** adalah aplikasi web mandiri (*standalone web application*) yang dirancang dan dibangun khusus untuk **Greja Kristen Jawi Wetan (GKJW) Jemaat Sukun**, Malang, Jawa Timur.

Sistem ini memodernisasi tata kelola aset gereja dari pencatatan *spreadsheet* terpisah menuju satu basis data relasional terpadu di bawah pengawasan **Pengawasan Perbendaharaan Jemaat (PBJ)** lintas **24 Komisi / POKJA**. Setiap barang fisik dijamin akuntabilitasnya dengan nomor stiker unik permanen yang tidak pernah didaur ulang (contoh: `MVI-012`, `MAU-005`), pencatatan barang massal multi-kondisi, kompresi otomatis foto lapangan ke format WebP, serta perlindungan berkas rahasia gereja melalui sistem hak akses terotorisasi (*Role-Based Access Control*).

---

### 2. Filosofi Desain: Swiss Archival & Brutalist Craft
Mengikuti standar visual **Anti-AI-Slop**, antarmuka menolak penggunaan gradien neon ungu-biru, kartu mengambang buram (*glassmorphism*), dan ikon dekoratif tanpa fungsi:
* **Palet Warna:** Kanvas hangat menyerupai kertas arsip fisik (`#F6F5F0`), garis tepi tinta hitam tegas (`1.5px solid #141413`), permukaan kertas bersih (`#FFFFFF` / `#EEECE1`), dan aksen merah terakota gereja (`#C84B31`).
* **Tipografi:** Sans-serif bersih untuk navigasi sistem dipadukan dengan huruf *monospace* tegas (`JetBrains Mono`) untuk seluruh kode stiker fisik, nomor urut sequence, waktu pencatatan, dan kuantitas unit.
* **Sentuhan Taktil:** Bayangan tegas berjarak presisi (`shadow-[2px_2px_0px_#141413]`), tombol fisik yang memberikan umpan balik nyata saat ditekan, serta kepadatan data yang rapi dan mudah dibaca oleh warga jemaat maupun pengurus non-IT.

---

### 3. Struktur Direktori Proyek (Monorepo)

```
c:\Inventaris GKJW SUKUN\
├── backend/                         # Mesin Backend FastAPI (Ringan & Cepat)
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py             # Dependensi sesi database & otorisasi JWT
│   │   │   └── v1/
│   │   │       ├── auth.py         # Login pengguna & penerbitan token JWT
│   │   │       ├── inventory.py    # Input barang, condition splitter, foto WebP, Excel
│   │   │       ├── documents.py    # Kelola arsip dokumen & kuitansi privat
│   │   │       └── pokja.py        # Ringkasan 24 komisi & nomor urut stiker
│   │   ├── core/
│   │   │   ├── config.py           # Konfigurasi aplikasi & pelacak path .env
│   │   │   ├── database.py         # Koneksi engine & sesi database SQLAlchemy
│   │   │   └── security.py         # Hashing kata sandi Bcrypt & token JWT
│   │   ├── models/                 # Model Data Relasional 3NF (PostgreSQL)
│   │   │   ├── pokja.py            # 24 Komisi dengan atomic sequence counter
│   │   │   ├── user.py             # Akun pengguna (Super Admin, Petugas POKJA)
│   │   │   ├── location.py         # Daftar ruangan gereja
│   │   │   ├── item.py             # Master Katalog Barang (Cegah duplikasi)
│   │   │   ├── item_unit.py        # Unit fisik berlabel stiker
│   │   │   ├── history_log.py      # Jejak rekam perubahan kondisi & mutasi
│   │   │   └── document.py         # Dokumen kuitansi, sertifikat & berita acara
│   │   ├── schemas/                # Kontrak validasi input Pydantic v2
│   │   └── main.py                 # File utama penjalur API FastAPI
│   ├── data/
│   │   └── legacy_inventory.csv    # 279 Data inventaris riil GKJW Sukun
│   ├── scripts/
│   │   ├── init_db.py              # Inisialisasi tabel SQL & data awal 24 POKJA
│   │   └── import_church_csv.py    # Skrip impor otomatis 279 barang gereja
│   ├── storage/uploads/            # Tempat penyimpanan foto WebP & dokumen
│   ├── requirements.txt            # Daftar pustaka Python backend
│   └── .env.example                # Salinan contoh konfigurasi backend
│
├── frontend/                        # Antarmuka Pengguna Vue 3 (Vite + Tailwind CSS)
│   ├── public/
│   │   └── Logo Gkjw Hitam.png     # Logo resmi GKJW Sukun
│   ├── src/
│   │   ├── api/index.js            # Penghubung API dengan penyimpan token otomatis
│   │   ├── components/
│   │   │   └── auth/LoginModal.vue # Jendela pop-up masuk akun pengurus
│   │   ├── router/index.js         # Pengatur rute halaman & proteksi login
│   │   ├── stores/auth.js          # Pengelola sesi login pengguna (Pinia)
│   │   ├── views/
│   │   │   ├── LandingView.vue     # Animasi pembuka, panduan alur, 24 komisi, scrollspy
│   │   │   ├── DashboardView.vue   # Ringkasan eksekutif aset & pemantau stiker
│   │   │   ├── InventoryView.vue   # Katalog akordeon, pembagi kondisi, ekspor Excel & PDF
│   │   │   ├── DocumentsView.vue   # Arsip kuitansi privat & foto kamera ponsel
│   │   │   └── LoginView.vue       # Halaman login mandiri
│   │   ├── App.vue                 # Bilah menu atas, scrollspy otomatis & watermark
│   │   └── main.js                 # Bootstrapping aplikasi frontend
│   ├── package.json                # Daftar paket frontend & skrip npm
│   ├── tailwind.config.js          # Token visual Swiss Archival & font monospace
│   └── vite.config.js              # Konfigurasi build produksi Vite
│
├── .gitignore                       # Aturan keamanan ketat pencegah kebocoran data
├── .env.example                     # Salinan contoh konfigurasi root
├── MASTER_BLUEPRINT.md              # Dokumen SRS, PRD, dan Arsitektur Lengkap
├── AGENTS.md                        # Pedoman AI & aturan integritas stiker fisik
└── README.md                        # Dokumentasi Lengkap Dwibahasa
```

---

### 4. Tumpukan Teknologi (*Tech Stack*)

| Lapisan Sistem | Teknologi / Pustaka | Peran Teknis & Keunggulan |
| :--- | :--- | :--- |
| **Backend** | Python 3.14 / 3.12, FastAPI, SQLAlchemy 2.0, Pydantic v2 | RESTful API berkecepatan tinggi, hemat memori RAM laptop, dan validasi data ketat. |
| **Basis Data** | PostgreSQL 18 / PostgreSQL 16 | Basis data relasional standar ACID bentuk normal ketiga ($3\text{NF}$). |
| **Pemrosesan Foto** | Pillow (PIL) | Kompresi foto otomatis ke format modern `.webp` (LANCZOS, lebar maks 1280px, kualitas 80%, ukuran $<150\text{ KB}$). |
| **Ekspor Laporan** | OpenPyXL & Cetak Browser Asli | Pembuatan spreadsheet Excel `.xlsx` rapi dan lembar Berita Acara siap cetak PDF. |
| **Frontend** | Vue 3 (Composition API), Vite 5, Pinia | Antarmuka reaktif ringan dengan ukuran awal sangat kecil ($< 100\text{ KB}$ gzipped). |
| **Desain Antarmuka** | Tailwind CSS v3, PostCSS, JetBrains Mono | Gaya Swiss Archival tanpa dependensi berat, stabil, dan ramah pengguna non-IT. |

---

### 5. Fitur Unggulan Sistem

#### A. Normalisasi Data 2 Tingkat (Bentuk Normal Ketiga - 3NF)
Berbeda dari *Google Sheets* lama di mana 20 mikrofon nirkabel yang sama ditulis berulang-ulang hingga 20 baris, sistem ini memisahkan **Master Katalog** (`items`) dan **Unit Fisik Berstiker** (`item_units`). 20 mikrofon tersebut hanya tampil sebagai 1 baris induk yang dapat dibuka (*accordion*), menghemat ruang layar dan mempermudah pencarian.

#### B. Pembagian Kondisi Barang Sekaligus (*Condition Splitter*)
Saat pengurus komisi mendaftarkan barang dalam jumlah banyak (misal: 10 unit), sistem menyediakan formulir pembagi kondisi dalam sekali simpan (contoh: 4 Baik, 3 Kurang Baik, 3 Rusak Berat). Backend secara otomatis membuatkan 10 kode stiker berurutan (misal: `MAU-001` s/d `MAU-010`) dan memetakan status kondisi masing-masing unit ke database beserta riwayat log awalnya.

#### C. Pembatasan Hak Akses Ketat (RBAC)
* **Halaman Publik / Warga Jemaat (Hanya Lihat):** Halaman awal (`/`) dapat diakses secara bebas oleh warga jemaat untuk melihat transparansi daftar 24 komisi dan ringkasan statistik. Seluruh tombol tambah, edit, atau hapus ditiadakan untuk umum.
* **Arsip Dokumen Rahasia Gereja (`/documents`):** Kuitansi pembelian, nota belanja, sertifikat, dan Berita Acara Majelis disembunyikan total dari pengunjung umum dan hanya bisa dibuka setelah masuk akun pengurus resmi via token JWT.

#### D. Desain Ramah Ponsel & Pemotretan Kamera Langsung
Pengurus yang melakukan *stock opname* keliling ruangan gereja dapat membuka web ini langsung dari ponsel pintar. Bagian unggah foto dilengkapi atribut `capture="environment"`, sehingga saat diklik akan otomatis membuka kamera belakang HP untuk memotret fisik barang di tempat. Foto langsung dikompresi menjadi file `.webp` hemat memori sebelum disimpan ke server.

#### E. Keamanan Nomor Stiker & Catatan Riwayat Mutasi (*Audit Trail*)
Nomor stiker barang yang sudah ditempel pada fisik **tidak akan pernah dihapus permanen atau didaur ulang**. Jika ada barang yang rusak total atau dibuang, barang tersebut diberi status **Diarsipkan (*Decommissioned*)** beserta nomor Berita Acara Majelis. Setiap perubahan ruangan dan kondisi tercatat rapi pada tabel log riwayat.

---

### 6. Panduan Instalasi & Menjalankan di Komputer Lokal

#### Persyaratan Sistem
* **Python 3.12+** atau **Python 3.14**
* **Node.js v20+** atau **v24** dan **npm**
* **PostgreSQL 16+** atau **PostgreSQL 18** yang aktif di port `5432`

#### Langkah 1: Persiapan Basis Data PostgreSQL
Buka aplikasi pgAdmin atau terminal PostgreSQL (psql), lalu jalankan perintah:
```sql
CREATE DATABASE gkjw_sukun_inventory;
```

#### Langkah 2: Pemasangan & Penyiapan Backend
1. Buka Command Prompt (CMD) atau PowerShell di folder repositori:
```bash
cd "c:\Inventaris GKJW SUKUN"
```
2. Salin template konfigurasi `.env`:
```bash
copy .env.example .env
copy backend\.env.example backend\.env
```
3. Buka file `backend/.env`, lalu sesuaikan password PostgreSQL Anda:
```ini
DATABASE_URL=postgresql://postgres:password_postgres_anda@127.0.0.1:5432/gkjw_sukun_inventory
```
4. Pasang modul-modul Python yang dibutuhkan:
```bash
pip install -r backend/requirements.txt
```
5. Buat struktur tabel database dan seed awal 24 POKJA:
```cmd
set PYTHONPATH=backend
python backend\scripts\init_db.py
```
*(Bila menggunakan PowerShell: `$env:PYTHONPATH="backend"`; lalu jalankan `python backend\scripts\init_db.py`)*

6. Masukkan 279 data barang riil GKJW Sukun dari file CSV:
```cmd
python backend\scripts\import_church_csv.py
```
7. Jalankan server backend FastAPI:
```cmd
python backend\app\main.py
```
* Layanan API akan aktif di: `http://localhost:8000`
* Halaman Dokumentasi Interaktif (Swagger): `http://localhost:8000/docs`

#### Langkah 3: Pemasangan & Menjalankan Frontend
1. Buka jendela terminal baru di folder `frontend`:
```bash
cd "c:\Inventaris GKJW SUKUN\frontend"
```
2. Pasang paket dependensi JavaScript:
```bash
npm install
```
3. Jalankan server pengembang Vite:
```bash
npm run dev
```
4. Buka peramban (*browser*) Anda di alamat: `http://localhost:5173`.

---

```
========================================================================================
Designed & Engineered with precision by Yosia Graceheo Boimau (Theology26)
GKJW Jemaat Sukun Inventory & Document Archive System v2.0
========================================================================================
```

