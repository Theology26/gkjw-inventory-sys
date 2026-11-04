<template>
  <div class="max-w-7xl mx-auto p-3 sm:p-4 lg:p-6 space-y-4 sm:space-y-6">
    <!-- Top Action & View Switcher Bar -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-paper-surface p-4 border-[1.5px] border-ink-primary rounded-md shadow-tactile">
      <div>
        <h2 class="text-lg sm:text-xl font-bold tracking-tight">Daftar Inventaris &amp; Barang Gereja</h2>
        <p class="text-xs text-ink-secondary mt-0.5">
          Setiap macam barang dikelompokkan dengan rapi agar mudah dicari dan tidak membingungkan.
        </p>
      </div>

      <div class="flex flex-wrap items-center gap-2">
        <!-- Segmented Mode Toggle -->
        <div class="inline-flex border-[1.5px] border-ink-primary rounded-md p-0.5 bg-paper-subtle w-full sm:w-auto">
          <button
            @click="activeMode = 'catalog'"
            :class="[
              'flex-1 sm:flex-initial px-3 py-1.5 text-xs font-semibold rounded transition-all',
              activeMode === 'catalog'
                ? 'bg-paper-surface border-[1.5px] border-ink-primary text-ink-primary shadow-tactile'
                : 'text-ink-secondary hover:text-ink-primary'
            ]"
          >
            Kelompok per Jenis Barang
          </button>
          <button
            @click="activeMode = 'units'"
            :class="[
              'flex-1 sm:flex-initial px-3 py-1.5 text-xs font-semibold rounded transition-all',
              activeMode === 'units'
                ? 'bg-paper-surface border-[1.5px] border-ink-primary text-ink-primary shadow-tactile'
                : 'text-ink-secondary hover:text-ink-primary'
            ]"
          >
            Daftar Seluruh Nomor Stiker
          </button>
        </div>

        <!-- Export & Print Actions -->
        <button
          @click="handleExportBackendExcel"
          :disabled="isExporting"
          class="btn-secondary text-xs py-2 px-3 flex items-center gap-2 font-mono"
          title="Unduh laporan daftar barang ke format Microsoft Excel (.xlsx)"
        >
          <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="8" y1="13" x2="16" y2="13"/>
            <line x1="8" y1="17" x2="16" y2="17"/>
          </svg>
          <span>{{ isExporting ? 'Mengunduh...' : 'Unduh Excel (.xlsx)' }}</span>
        </button>

        <button
          @click="handlePrintBA"
          class="btn-secondary text-xs py-2 px-3 flex items-center gap-2 font-mono"
          title="Cetak lembar Berita Acara / Laporan Resmi"
        >
          <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="6 9 6 2 18 2 18 9"/>
            <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/>
            <rect x="6" y="14" width="12" height="8"/>
          </svg>
          <span>Cetak Berita Acara</span>
        </button>

        <button
          v-if="authStore.canManage"
          @click="showCreateModal = true"
          class="btn-primary text-xs py-2 px-3.5 w-full sm:w-auto"
        >
          + Tambah Barang Baru
        </button>
      </div>
    </div>

    <!-- Filter Bar (Swiss Archival Tactile) -->
    <div class="bg-paper-surface p-3.5 sm:p-4 border-[1.5px] border-ink-primary rounded-md shadow-tactile space-y-3">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5 sm:gap-3">
        <!-- 1. Search Bar -->
        <div>
          <label class="block text-xs font-bold uppercase text-ink-secondary mb-1">
            Cari Barang / ID Stiker
          </label>
          <div class="relative">
            <input
              v-model="searchQuery"
              @input="handleSearchInput"
              type="text"
              placeholder="Contoh: Mic, Mixer, MAU-001..."
              class="input-tactile text-xs h-9 pr-7 w-full"
            />
            <button
              v-if="searchQuery"
              @click="clearSearch"
              type="button"
              class="absolute right-2 top-1/2 -translate-y-1/2 text-ink-muted hover:text-church-terracotta text-xs font-mono font-bold"
              title="Hapus pencarian"
            >
              ✕
            </button>
          </div>
        </div>

        <!-- 2. POKJA Selector -->
        <div>
          <label class="block text-xs font-bold uppercase text-ink-secondary mb-1">
            Komisi / POKJA ({{ pokjas.length }})
          </label>
          <select v-model="selectedPokja" @change="fetchData" class="input-tactile text-xs h-9 w-full">
            <option value="">Semua Komisi / POKJA</option>
            <option v-for="p in pokjas" :key="p.code" :value="p.code">
              {{ p.code }} — {{ p.name }}
            </option>
          </select>
        </div>

        <!-- 3. Location Selector (Sorted Alphabetically) -->
        <div>
          <label class="block text-xs font-bold uppercase text-ink-secondary mb-1">
            Lokasi Ruangan ({{ locations.length }})
          </label>
          <select v-model="selectedLocation" @change="fetchData" class="input-tactile text-xs h-9 w-full">
            <option value="">Semua Lokasi Ruangan</option>
            <option v-for="loc in sortedLocations" :key="loc.id" :value="loc.id">
              {{ loc.name }}
            </option>
          </select>
        </div>

        <!-- 4. Condition Selector -->
        <div>
          <label class="block text-xs font-bold uppercase text-ink-secondary mb-1">
            Kondisi Fisik Barang
          </label>
          <select v-model="selectedCondition" @change="fetchData" class="input-tactile text-xs h-9 w-full">
            <option value="">Semua Kondisi</option>
            <option value="BAIK">Baik (Siap Pakai)</option>
            <option value="KURANG_BAIK">Kurang Baik (Perlu Servis)</option>
            <option value="RUSAK_BERAT">Rusak Berat (Tidak Berfungsi)</option>
          </select>
        </div>
      </div>

      <!-- Active Filter Badges & Reset Strip -->
      <div
        v-if="hasActiveFilters"
        class="pt-2.5 border-t border-paper-border flex flex-wrap items-center justify-between gap-2 text-xs font-mono"
      >
        <div class="flex items-center gap-1.5 flex-wrap">
          <span class="text-ink-secondary uppercase font-bold text-[11px]">Filter Aktif ({{ activeFilterCount }}):</span>

          <span
            v-if="searchQuery"
            class="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-paper-canvas border border-ink-primary text-ink-primary font-bold text-[11px]"
          >
            Cari: "{{ searchQuery }}"
            <button @click="clearSearch" class="hover:text-church-terracotta ml-0.5 font-bold">✕</button>
          </span>

          <span
            v-if="selectedPokja"
            class="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-paper-canvas border border-ink-primary text-ink-primary font-bold text-[11px]"
          >
            POKJA: {{ selectedPokja }}
            <button @click="clearPokja" class="hover:text-church-terracotta ml-0.5 font-bold">✕</button>
          </span>

          <span
            v-if="selectedLocation"
            class="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-paper-canvas border border-ink-primary text-ink-primary font-bold text-[11px]"
          >
            Lokasi: {{ selectedLocationName }}
            <button @click="clearLocation" class="hover:text-church-terracotta ml-0.5 font-bold">✕</button>
          </span>

          <span
            v-if="selectedCondition"
            class="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-paper-canvas border border-ink-primary text-ink-primary font-bold text-[11px]"
          >
            Kondisi: {{ selectedConditionLabel }}
            <button @click="clearCondition" class="hover:text-church-terracotta ml-0.5 font-bold">✕</button>
          </span>
        </div>

        <button
          @click="resetFilters"
          type="button"
          class="text-church-terracotta hover:underline font-bold text-xs flex items-center gap-1 ml-auto"
        >
          <span>✕</span>
          <span>Bersihkan Semua Filter</span>
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="p-12 text-center bg-paper-surface border-[1.5px] border-ink-primary rounded-md font-mono text-xs sm:text-sm">
      Memuat data inventaris GKJW Sukun...
    </div>

    <!-- MODE 1: KATALOG TERKELOMPOK (MASTER-DETAIL ACCORDION) -->
    <div v-else-if="activeMode === 'catalog'" class="bg-paper-surface border-[1.5px] border-ink-primary rounded-md shadow-tactile overflow-hidden">
      <div class="p-3.5 border-b border-paper-border bg-paper-subtle flex items-center justify-between">
        <span class="text-xs font-mono font-bold uppercase text-ink-secondary">
          Daftar Master Katalog Terdaftar (Anti-Redundansi)
        </span>
        <span class="text-xs font-mono px-2 py-0.5 bg-paper-surface border border-ink-primary rounded font-bold">
          Total: {{ catalogs.length }} Master Barang
        </span>
      </div>

      <div v-if="!catalogs.length" class="p-12 text-center text-ink-secondary font-mono text-xs">
        <svg class="w-8 h-8 mx-auto mb-2.5 text-ink-secondary" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="3" width="18" height="18" rx="1"/>
          <line x1="3" y1="9" x2="21" y2="9"/>
          <line x1="9" y1="21" x2="9" y2="9"/>
        </svg>
        <p class="font-bold text-sm text-ink-primary mb-1">Tidak ada macam barang yang cocok dengan filter</p>
        <p class="text-xs text-ink-secondary mb-3 max-w-md mx-auto">
          Tidak ditemukan barang pada lokasi atau kondisi yang dipilih. Silakan periksa kembali atau bersihkan filter di atas.
        </p>
        <button
          v-if="hasActiveFilters"
          @click="resetFilters"
          class="btn-secondary text-xs py-1.5 px-3 inline-flex items-center gap-1 font-mono"
        >
          <span>✕</span>
          <span>Kembalikan Semua Barang</span>
        </button>
      </div>

      <div v-else class="divide-y divide-paper-border">
        <div v-for="cat in catalogs" :key="cat.id" class="transition-colors hover:bg-paper-subtle/40">
          <!-- Master Item Row -->
          <div
            @click="toggleExpand(cat.id)"
            class="p-3 sm:p-4 flex flex-col md:flex-row md:items-center justify-between gap-3 cursor-pointer select-none"
          >
            <div class="flex items-start sm:items-center gap-3">
              <span class="w-5 text-center text-xs font-mono font-bold text-church-terracotta mt-0.5 sm:mt-0">
                {{ expandedItems[cat.id] ? '▼' : '►' }}
              </span>

              <!-- Foto Thumbnail Barang jika ada -->
              <a
                v-if="cat.default_photo_path"
                :href="`/uploads/${cat.default_photo_path}`"
                target="_blank"
                @click.stop
                class="block w-11 h-11 rounded border-[1.5px] border-ink-primary overflow-hidden shrink-0 hover:opacity-85 shadow-[1px_1px_0px_#141413]"
                title="Lihat foto barang"
              >
                <img :src="`/uploads/${cat.default_photo_path}`" alt="Foto" class="w-full h-full object-cover" />
              </a>

              <div>
                <div class="flex items-center gap-2 flex-wrap">
                  <span class="text-xs font-mono font-bold px-2 py-0.5 bg-paper-subtle border border-ink-primary rounded text-church-forest">
                    {{ cat.pokja_code }}
                  </span>
                  <h3 class="font-bold text-sm text-ink-primary">{{ cat.name }}</h3>
                </div>
                <p class="text-xs text-ink-secondary mt-0.5 font-mono">
                  Merk / Tipe: <span class="font-semibold text-ink-primary">{{ cat.brand_model || '-' }}</span>
                  <span v-if="cat.category" class="ml-2 px-1.5 py-0.5 bg-paper-canvas border border-paper-border rounded text-[10px]">
                    {{ cat.category }}
                  </span>
                </p>
              </div>
            </div>

            <!-- Aggregated Quantity & Condition Pills -->
            <div class="flex items-center gap-2 sm:gap-3 flex-wrap pl-8 sm:pl-0">
              <span class="font-mono text-xs font-bold px-2.5 py-1 bg-paper-canvas border border-ink-primary rounded">
                {{ cat.total_units }} Unit
              </span>

              <div class="flex items-center gap-1.5 text-[11px] font-mono flex-wrap">
                <span v-if="cat.baik_count > 0" class="px-2 py-0.5 rounded bg-status-good-bg text-status-good-ink border border-status-good-ink font-semibold">
                  {{ cat.baik_count }} Baik
                </span>
                <span v-if="cat.kurang_baik_count > 0" class="px-2 py-0.5 rounded bg-status-warn-bg text-status-warn-ink border border-status-warn-ink font-semibold">
                  {{ cat.kurang_baik_count }} Krg Baik
                </span>
                <span v-if="cat.rusak_berat_count > 0" class="px-2 py-0.5 rounded bg-status-bad-bg text-status-bad-ink border border-status-bad-ink font-semibold">
                  {{ cat.rusak_berat_count }} Rusak
                </span>
              </div>
            </div>
          </div>

          <!-- Expanded Accordion: Sub-Table Unit Fisik Berstiker -->
          <div v-if="expandedItems[cat.id]" class="bg-paper-canvas border-t border-b border-ink-primary p-3 sm:p-4 sm:pl-8">
            <div class="text-xs font-mono font-bold uppercase text-ink-secondary mb-2 flex items-center justify-between">
              <span>Rincian Stiker Fisik Berlabel ({{ cat.name }})</span>
              <span class="text-[10px] sm:text-[11px] text-church-terracotta hidden sm:inline">
                Immutable Stiker ID &bull; Soft Delete Archive
              </span>
            </div>

            <div v-if="loadingUnits[cat.id]" class="text-xs font-mono text-ink-secondary py-3">
              Memuat daftar unit fisik...
            </div>

            <div v-else-if="!unitsByCatalog[cat.id]?.length" class="text-xs font-mono text-ink-secondary py-3">
              Tidak ada unit fisik aktif.
            </div>

            <div v-else class="overflow-x-auto">
              <table class="w-full text-left border-collapse text-xs min-w-[500px]">
                <thead>
                  <tr class="border-b-[1.5px] border-ink-primary bg-paper-subtle">
                    <th class="py-2 px-3 font-mono">ID Stiker</th>
                    <th class="py-2 px-3">Kondisi Fisik</th>
                    <th class="py-2 px-3">Lokasi Penempatan</th>
                    <th class="py-2 px-3">Foto Fisik</th>
                    <th class="py-2 px-3 text-right">Aksi Unit</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-paper-border font-mono">
                  <tr v-for="unit in unitsByCatalog[cat.id]" :key="unit.unit_code" class="hover:bg-paper-surface">
                    <td class="py-2 px-3 font-bold text-church-terracotta">{{ unit.unit_code }}</td>
                    <td class="py-2 px-3">
                      <span :class="conditionBadgeClass(unit.condition_status)">
                        {{ unit.condition_status }}
                      </span>
                    </td>
                    <td class="py-2 px-3">{{ unit.location_name }}</td>
                    <td class="py-2 px-3">
                      <a
                        v-if="unit.unit_photo_path"
                        :href="`/uploads/${unit.unit_photo_path}`"
                        target="_blank"
                        class="text-church-terracotta hover:underline font-bold text-[11px]"
                      >
                        [Lihat Foto]
                      </a>
                      <span v-else class="text-ink-muted text-[11px]">-</span>
                    </td>
                    <td class="py-2 px-3 text-right space-x-1">
                      <button
                        v-if="authStore.canManage"
                        @click="openEditModal(unit)"
                        class="px-2 py-0.5 rounded border border-ink-primary bg-paper-surface hover:bg-paper-subtle text-[11px]"
                      >
                        Edit
                      </button>
                      <button
                        v-if="authStore.isSuperAdmin"
                        @click="openDecommissionModal(unit)"
                        class="px-2 py-0.5 rounded border border-status-bad-ink bg-status-bad-bg text-status-bad-ink hover:bg-status-bad-bg/80 text-[11px]"
                      >
                        Arsipkan
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- MODE 2: FLAT LIST SEMUA STIKER FISIK -->
    <div v-else class="bg-paper-surface border-[1.5px] border-ink-primary rounded-md shadow-tactile overflow-hidden">
      <div class="p-3.5 border-b border-paper-border bg-paper-subtle flex items-center justify-between">
        <span class="text-xs font-mono font-bold uppercase text-ink-secondary">
          Daftar Seluruh Stiker Fisik di Lapangan
        </span>
        <span class="text-xs font-mono px-2 py-0.5 bg-paper-surface border border-ink-primary rounded font-bold">
          Total: {{ flatUnits.length }} Stiker Fisik
        </span>
      </div>

      <div v-if="!flatUnits.length" class="p-12 text-center text-ink-secondary font-mono text-xs">
        <svg class="w-8 h-8 mx-auto mb-2.5 text-ink-secondary" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
          <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/>
          <line x1="7" y1="7" x2="7.01" y2="7"/>
        </svg>
        <p class="font-bold text-sm text-ink-primary mb-1">Tidak ada nomor stiker fisik yang cocok</p>
        <p class="text-xs text-ink-secondary mb-3 max-w-md mx-auto">
          Tidak ditemukan stiker fisik pada lokasi atau kondisi yang dipilih. Silakan periksa kembali atau bersihkan filter di atas.
        </p>
        <button
          v-if="hasActiveFilters"
          @click="resetFilters"
          class="btn-secondary text-xs py-1.5 px-3 inline-flex items-center gap-1 font-mono"
        >
          <span>✕</span>
          <span>Kembalikan Semua Barang</span>
        </button>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full text-left border-collapse text-xs min-w-[650px]">
          <thead>
            <tr class="border-b-[1.5px] border-ink-primary bg-paper-subtle font-mono text-[11px] uppercase text-ink-secondary">
              <th class="py-2.5 px-3">ID Stiker</th>
              <th class="py-2.5 px-3">POKJA</th>
              <th class="py-2.5 px-3">Nama & Merk Barang</th>
              <th class="py-2.5 px-3">Lokasi Ruangan</th>
              <th class="py-2.5 px-3">Kondisi</th>
              <th class="py-2.5 px-3">Foto Fisik</th>
              <th class="py-2.5 px-3 text-right">Aksi</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-paper-border font-mono text-xs">
            <tr v-for="unit in flatUnits" :key="unit.unit_code" class="hover:bg-paper-subtle/40">
              <td class="py-2.5 px-3 font-bold text-church-terracotta">{{ unit.unit_code }}</td>
              <td class="py-2.5 px-3 font-semibold">{{ unit.pokja_code }}</td>
              <td class="py-2.5 px-3 font-sans">
                <span class="font-bold text-ink-primary">{{ unit.item_name }}</span>
                <span class="text-ink-secondary block text-[11px] font-mono">{{ unit.brand_model }}</span>
              </td>
              <td class="py-2.5 px-3 font-sans">{{ unit.location_name }}</td>
              <td class="py-2.5 px-3">
                <span :class="conditionBadgeClass(unit.condition_status)">
                  {{ unit.condition_status }}
                </span>
              </td>
              <td class="py-2.5 px-3">
                <a
                  v-if="unit.unit_photo_path"
                  :href="`/uploads/${unit.unit_photo_path}`"
                  target="_blank"
                  class="text-church-terracotta hover:underline font-bold text-[11px]"
                >
                  [Foto]
                </a>
                <span v-else class="text-ink-muted text-[11px]">-</span>
              </td>
              <td class="py-2.5 px-3 text-right space-x-1">
                <button
                  v-if="authStore.canManage"
                  @click="openEditModal(unit)"
                  class="px-2 py-0.5 rounded border border-ink-primary bg-paper-surface hover:bg-paper-subtle text-[11px]"
                >
                  Edit
                </button>
                <button
                  v-if="authStore.isSuperAdmin"
                  @click="openDecommissionModal(unit)"
                  class="px-2 py-0.5 rounded border border-status-bad-ink bg-status-bad-bg text-status-bad-ink text-[11px]"
                >
                  Arsipkan
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ======================================================================= -->
    <!-- MODAL: TAMBAH INVENTARIS BARU DENGAN CONDITION SPLITTER                 -->
    <!-- ======================================================================= -->
    <div v-if="showCreateModal" class="fixed inset-0 z-50 bg-ink-primary/60 backdrop-blur-[2px] flex items-center justify-center p-3 sm:p-4">
      <div class="max-w-xl w-full bg-paper-surface border-[2px] border-ink-primary rounded-md p-5 sm:p-6 shadow-tactile-lg max-h-[92vh] overflow-y-auto">
        <!-- Archival Ledger Modal Header -->
        <div class="flex items-center justify-between border-b-[1.5px] border-ink-primary pb-3 mb-4">
          <div>
            <span class="text-[10px] font-mono font-bold uppercase tracking-wider text-church-terracotta block">
              Sistem Inventaris &bull; Registrasi Aset
            </span>
            <h3 class="text-base font-bold tracking-tight text-ink-primary mt-0.5">
              Tambah Inventaris Baru
            </h3>
          </div>
          <button
            @click="showCreateModal = false"
            class="w-7 h-7 flex items-center justify-center border border-ink-primary bg-paper-surface hover:bg-paper-subtle font-mono text-xs font-bold transition-colors"
            title="Tutup (Esc)"
          >
            ✕
          </button>
        </div>

        <form @submit.prevent="handleCreateSubmit" class="space-y-4 text-xs">
          <!-- POKJA Selector -->
          <div>
            <label class="block font-bold uppercase text-ink-secondary mb-1">Komisi / POKJA *</label>
            <select v-model="createForm.pokja_code" required class="input-tactile text-xs">
              <option value="">Pilih POKJA...</option>
              <option v-for="p in pokjas" :key="p.code" :value="p.code">
                {{ p.code }} — {{ p.name }} (Stiker terakhir: {{ p.last_sequence }})
              </option>
            </select>
          </div>

          <!-- Nama & Merk -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block font-bold uppercase text-ink-secondary mb-1">Nama Barang *</label>
              <input v-model="createForm.name" type="text" placeholder="Contoh: Mic Wireless" required class="input-tactile text-xs" />
            </div>
            <div>
              <label class="block font-bold uppercase text-ink-secondary mb-1">Merk / Tipe / Seri *</label>
              <input v-model="createForm.brand_model" type="text" placeholder="Contoh: KREZT KRU-4810A" required class="input-tactile text-xs" />
            </div>
          </div>

          <!-- Jumlah Unit & Lokasi -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block font-bold uppercase text-ink-secondary mb-1">Jumlah Unit Fisik *</label>
              <input v-model.number="createForm.quantity" type="number" min="1" max="200" required class="input-tactile text-xs font-mono font-bold" />
            </div>
            <div>
              <label class="block font-bold uppercase text-ink-secondary mb-1">Lokasi Ruangan *</label>
              <select v-model.number="createForm.location_id" required class="input-tactile text-xs">
                <option v-for="loc in sortedLocations" :key="loc.id" :value="loc.id">{{ loc.name }}</option>
              </select>
            </div>
          </div>

          <!-- CONDITION SPLITTER SUB-FORM (Swiss Archival Segmented Control) -->
          <div class="p-3.5 bg-paper-canvas border-[1.5px] border-ink-primary rounded space-y-2.5">
            <div class="flex items-center justify-between flex-wrap gap-2">
              <span class="font-bold uppercase text-ink-primary text-xs">
                Distribusi Kondisi Fisik
              </span>
              <div class="inline-flex border border-ink-primary bg-paper-surface text-[11px] font-mono">
                <button
                  type="button"
                  @click="useConditionSplit = false"
                  :class="[!useConditionSplit ? 'bg-ink-primary text-white font-bold' : 'text-ink-secondary hover:text-ink-primary', 'px-2.5 py-1 transition-colors']"
                >
                  Kondisi Seragam
                </button>
                <button
                  type="button"
                  @click="enableConditionSplit"
                  :class="[useConditionSplit ? 'bg-ink-primary text-white font-bold' : 'text-ink-secondary hover:text-ink-primary', 'px-2.5 py-1 border-l border-ink-primary transition-colors']"
                >
                  Pecah Porsi Kondisi
                </button>
              </div>
            </div>

            <!-- Single Condition Mode -->
            <div v-if="!useConditionSplit">
              <label class="block text-[11px] font-medium text-ink-secondary mb-1 font-mono">
                Seluruh {{ createForm.quantity }} unit dalam kondisi:
              </label>
              <select v-model="createForm.condition_status" class="input-tactile text-xs">
                <option value="BAIK">Baik (Siap Pakai)</option>
                <option value="KURANG_BAIK">Kurang Baik (Perlu Servis)</option>
                <option value="RUSAK_BERAT">Rusak Berat (Tidak Berfungsi)</option>
              </select>
            </div>

            <!-- Split Condition Mode (Sub-Form 3 Porsi) -->
            <div v-else class="space-y-2 pt-1">
              <p class="text-[11px] text-ink-secondary font-mono">
                Tentukan jumlah unit untuk setiap kondisi (total: {{ createForm.quantity }} unit):
              </p>
              <div class="grid grid-cols-3 gap-2 font-mono">
                <div>
                  <label class="block text-[10px] font-bold text-status-good-ink uppercase">Baik</label>
                  <input
                    v-model.number="conditionSplit.baik"
                    type="number"
                    min="0"
                    :max="createForm.quantity"
                    class="input-tactile text-xs font-bold text-status-good-ink text-center"
                  />
                </div>
                <div>
                  <label class="block text-[10px] font-bold text-status-warn-ink uppercase">Kurang Baik</label>
                  <input
                    v-model.number="conditionSplit.kurang_baik"
                    type="number"
                    min="0"
                    :max="createForm.quantity"
                    class="input-tactile text-xs font-bold text-status-warn-ink text-center"
                  />
                </div>
                <div>
                  <label class="block text-[10px] font-bold text-status-bad-ink uppercase">Rusak Berat</label>
                  <input
                    v-model.number="conditionSplit.rusak_berat"
                    type="number"
                    min="0"
                    :max="createForm.quantity"
                    class="input-tactile text-xs font-bold text-status-bad-ink text-center"
                  />
                </div>
              </div>

              <!-- Realtime Validation Text -->
              <div class="text-[11px] font-mono flex items-center justify-between pt-1">
                <span class="text-ink-secondary">Terbagi: {{ splitTotal }} / {{ createForm.quantity }} Unit</span>
                <span v-if="splitTotal === createForm.quantity" class="text-status-good-ink font-bold">
                  Jumlah Pas
                </span>
                <span v-else-if="splitTotal < createForm.quantity" class="text-status-warn-ink font-bold">
                  Kurang {{ createForm.quantity - splitTotal }} unit
                </span>
                <span v-else class="text-status-bad-ink font-bold">
                  Kelebihan {{ splitTotal - createForm.quantity }} unit
                </span>
              </div>
            </div>
          </div>

          <!-- Catatan Tambahan -->
          <div>
            <label class="block font-bold uppercase text-ink-secondary mb-1">Catatan Tambahan (Opsional)</label>
            <textarea v-model="createForm.notes" rows="2" placeholder="Keterangan pengadaan, nomor nota, atau spesifikasi khusus..." class="input-tactile text-xs h-14 py-2"></textarea>
          </div>

          <!-- PHOTO UPLOAD & CAMERA CAPTURE (Archival Tactile Trigger) -->
          <div class="p-3.5 bg-paper-canvas border-[1.5px] border-ink-primary rounded space-y-2">
            <div class="flex items-center justify-between">
              <span class="font-bold uppercase text-ink-primary text-xs">
                Dokumentasi Foto Fisik
              </span>
              <span class="text-[10px] font-mono text-ink-secondary">
                Format WebP Otomatis
              </span>
            </div>

            <p class="text-[11px] text-ink-secondary">
              Ambil foto fisik barang langsung via kamera HP atau pilih berkas gambar:
            </p>

            <div class="flex items-center gap-2 flex-wrap">
              <input
                ref="createFileInput"
                type="file"
                accept="image/*"
                capture="environment"
                @change="handleCreatePhotoSelect"
                class="hidden"
              />
              <button
                type="button"
                @click="$refs.createFileInput.click()"
                class="btn-secondary text-xs py-1.5 px-3 flex items-center gap-1.5 font-mono"
              >
                <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
                  <circle cx="12" cy="13" r="4"/>
                </svg>
                <span>{{ createPhotoFile ? 'Ganti Berkas Foto' : 'Pilih Berkas / Potret Foto' }}</span>
              </button>

              <button
                v-if="createPhotoFile"
                @click="clearCreatePhoto"
                type="button"
                class="text-xs font-mono text-church-terracotta hover:underline"
              >
                Hapus
              </button>

              <span v-if="!createPhotoFile" class="text-[11px] font-mono text-ink-muted">
                Belum ada foto dipilih
              </span>
            </div>

            <!-- Preview Foto jika sudah dipilih -->
            <div v-if="createPhotoPreview" class="pt-2 flex items-center gap-3">
              <div class="w-14 h-14 rounded border border-ink-primary overflow-hidden bg-paper-subtle shrink-0 shadow-[1px_1px_0px_#141413]">
                <img :src="createPhotoPreview" alt="Pratinjau Foto" class="w-full h-full object-cover" />
              </div>
              <div class="text-[11px] font-mono text-ink-secondary">
                <span class="text-status-good-ink font-bold block">Foto siap diunggah &amp; dikompresi</span>
                <span class="text-ink-primary font-semibold truncate max-w-[200px] block">{{ createPhotoFile.name }}</span>
                <span class="text-[10px] text-ink-muted">({{ (createPhotoFile.size / 1024).toFixed(1) }} KB)</span>
              </div>
            </div>
          </div>

          <!-- PRATINJAU KODE STIKER FISIK (Archival Ledger Grid) -->
          <div class="border-[1.5px] border-ink-primary bg-paper-subtle p-3 rounded space-y-1.5">
            <div class="flex items-center justify-between text-[10px] font-mono font-bold uppercase text-ink-secondary">
              <span>Pratinjau Label Fisik yang Diterbitkan</span>
              <span>{{ createForm.quantity }} Unit</span>
            </div>
            <div class="flex flex-wrap gap-1.5 max-h-32 overflow-y-auto pt-1 font-mono text-xs">
              <div
                v-for="item in previewStickerList"
                :key="item.code"
                class="px-2 py-0.5 border border-ink-primary bg-paper-surface flex items-center gap-2 rounded-none"
              >
                <span class="font-bold text-church-terracotta">{{ item.code }}</span>
                <span class="text-[10px] text-ink-secondary border-l border-paper-border pl-1.5">
                  {{ item.condition }}
                </span>
              </div>
            </div>
          </div>

          <div class="pt-3 flex justify-end gap-2 border-t border-paper-border">
            <button type="button" @click="showCreateModal = false" class="btn-secondary text-xs py-2 px-3">Batal</button>
            <button
              type="submit"
              :disabled="isSubmitting || (useConditionSplit && splitTotal !== createForm.quantity)"
              class="btn-primary text-xs py-2 px-4 disabled:opacity-50 disabled:cursor-not-allowed font-mono font-bold"
            >
              {{ isSubmitting ? 'Menyimpan...' : 'Daftarkan Inventaris' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- ======================================================================= -->
    <!-- MODAL: EDIT KONDISI, LOKASI, & UPLOAD FOTO DARI KAMERA HP               -->
    <!-- ======================================================================= -->
    <div v-if="editingUnit" class="fixed inset-0 z-50 bg-ink-primary/60 backdrop-blur-[2px] flex items-center justify-center p-3 sm:p-4">
      <div class="max-w-md w-full bg-paper-surface border-[2px] border-ink-primary rounded-md p-5 sm:p-6 shadow-tactile-lg max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between border-b-[1.5px] border-ink-primary pb-3 mb-4">
          <div>
            <span class="text-[10px] font-mono font-bold uppercase tracking-wider text-church-terracotta block">
              Pembaruan Status Aset
            </span>
            <h3 class="text-sm font-bold tracking-tight text-ink-primary mt-0.5">
              Edit Unit: <span class="font-mono text-church-terracotta">{{ editingUnit.unit_code }}</span>
            </h3>
          </div>
          <button
            @click="editingUnit = null"
            class="w-6 h-6 flex items-center justify-center border border-ink-primary bg-paper-surface hover:bg-paper-subtle font-mono text-xs font-bold transition-colors"
          >
            ✕
          </button>
        </div>

        <form @submit.prevent="handleEditSubmit" class="space-y-3.5 text-xs">
          <div>
            <label class="block font-bold uppercase text-ink-secondary mb-1">Kondisi Fisik Saat Ini</label>
            <select v-model="editForm.condition_status" class="input-tactile text-xs">
              <option value="BAIK">Baik (Siap Pakai)</option>
              <option value="KURANG_BAIK">Kurang Baik (Perlu Servis)</option>
              <option value="RUSAK_BERAT">Rusak Berat (Tidak Berfungsi)</option>
            </select>
          </div>

          <div>
            <label class="block font-bold uppercase text-ink-secondary mb-1">Lokasi Ruangan Penempatan</label>
            <select v-model.number="editForm.location_id" class="input-tactile text-xs">
              <option v-for="loc in sortedLocations" :key="loc.id" :value="loc.id">{{ loc.name }}</option>
            </select>
          </div>

          <div>
            <label class="block font-bold uppercase text-ink-secondary mb-1">Catatan Tambahan</label>
            <textarea v-model="editForm.notes" rows="2" class="input-tactile text-xs h-14 py-1.5"></textarea>
          </div>

          <div>
            <label class="block font-bold uppercase text-ink-secondary mb-1">Keterangan Mutasi / Riwayat</label>
            <input v-model="editForm.remarks" type="text" placeholder="Misal: Dipindahkan dari Ruang Audio ke Gedung Gereja" class="input-tactile text-xs" />
          </div>

          <!-- PHOTO UPLOAD & DIRECT CAMERA INPUT (ARCHIVAL TRIGGER) -->
          <div class="p-3 bg-paper-canvas border border-ink-primary rounded space-y-2">
            <span class="block text-[11px] font-bold uppercase text-ink-secondary">
              Dokumentasi Foto Fisik
            </span>
            <div v-if="editingUnit.unit_photo_path" class="text-[11px] font-mono text-status-good-ink">
              Foto tersimpan: <a :href="`/uploads/${editingUnit.unit_photo_path}`" target="_blank" class="underline font-bold">[Lihat Foto]</a>
            </div>

            <div class="flex items-center gap-2 flex-wrap">
              <input
                ref="editFileInput"
                type="file"
                accept="image/*"
                capture="environment"
                @change="handleCameraPhotoSelect"
                class="hidden"
              />
              <button
                type="button"
                @click="$refs.editFileInput.click()"
                class="btn-secondary text-xs py-1.5 px-3 flex items-center gap-1.5 font-mono"
              >
                <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
                  <circle cx="12" cy="13" r="4"/>
                </svg>
                <span>{{ selectedPhotoFile ? 'Ganti Foto' : 'Ambil Foto / Pilih Berkas' }}</span>
              </button>

              <span v-if="selectedPhotoFile" class="text-[11px] font-mono text-ink-primary font-semibold">
                {{ selectedPhotoFile.name }}
              </span>
              <span v-else class="text-[11px] font-mono text-ink-muted">
                {{ editingUnit.unit_photo_path ? 'Pertahankan foto lama' : 'Belum ada foto' }}
              </span>
            </div>
          </div>

          <div class="pt-2 flex justify-end gap-2 border-t border-paper-border">
            <button type="button" @click="editingUnit = null" class="btn-secondary text-xs py-1.5 px-3">Batal</button>
            <button type="submit" :disabled="isSavingEdit" class="btn-primary text-xs py-1.5 px-4 font-mono font-bold">
              {{ isSavingEdit ? 'Menyimpan...' : 'Simpan Perubahan' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- ======================================================================= -->
    <!-- MODAL: ARSIAPKAN BARANG                                                 -->
    <!-- ======================================================================= -->
    <div v-if="decommissioningUnit" class="fixed inset-0 z-50 bg-ink-primary/60 backdrop-blur-[2px] flex items-center justify-center p-3 sm:p-4">
      <div class="max-w-md w-full bg-paper-surface border-[2px] border-status-bad-ink rounded-md p-5 sm:p-6 shadow-tactile-lg">
        <h3 class="text-sm font-bold uppercase text-status-bad-ink mb-1">
          Arsipkan Barang: {{ decommissioningUnit.unit_code }}
        </h3>
        <p class="text-xs text-ink-secondary mb-3 leading-relaxed">
          Data barang ini <strong>akan disimpan dalam arsip</strong> dan nomor stikernya tidak akan dipakai ulang agar pembukuan gereja tetap rapi.
        </p>

        <form @submit.prevent="handleDecommissionSubmit" class="space-y-3 text-xs">
          <div>
            <label class="block font-bold uppercase text-ink-secondary mb-1">Alasan / Catatan Berita Acara Majelis *</label>
            <textarea
              v-model="decommissionReason"
              required
              rows="3"
              placeholder="Contoh: Rusak total dan tidak dapat diservis, disetujui dalam rapat Majelis pada..."
              class="input-tactile text-xs h-20 py-2"
            ></textarea>
          </div>

          <div class="flex justify-end gap-2 pt-2">
            <button type="button" @click="decommissioningUnit = null" class="btn-secondary text-xs py-1.5 px-3">Batal</button>
            <button type="submit" class="btn-primary text-xs py-1.5 px-3 bg-status-bad-ink">Simpan ke Arsip</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api'
import { useAuthStore } from '../stores/auth'
import { printBeritaAcaraStockOpname } from '../utils/export'

const authStore = useAuthStore()

const activeMode = ref('catalog')
const isLoading = ref(true)
const isSubmitting = ref(false)
const isSavingEdit = ref(false)
const isExporting = ref(false)

const catalogs = ref([])
const flatUnits = ref([])
const pokjas = ref([])
const locations = ref([])

// Filter state
const searchQuery = ref('')
const selectedPokja = ref('')
const selectedLocation = ref('')
const selectedCondition = ref('')

// Computed properties for filter UX
const sortedLocations = computed(() => {
  return [...locations.value].sort((a, b) => a.name.localeCompare(b.name, 'id'))
})

const hasActiveFilters = computed(() => {
  return !!(searchQuery.value.trim() || selectedPokja.value || selectedLocation.value || selectedCondition.value)
})

const activeFilterCount = computed(() => {
  let count = 0
  if (searchQuery.value.trim()) count++
  if (selectedPokja.value) count++
  if (selectedLocation.value) count++
  if (selectedCondition.value) count++
  return count
})

const selectedLocationName = computed(() => {
  if (!selectedLocation.value) return ''
  const found = locations.value.find((l) => l.id === Number(selectedLocation.value))
  return found ? found.name : `Lokasi #${selectedLocation.value}`
})

const selectedConditionLabel = computed(() => {
  if (selectedCondition.value === 'BAIK') return 'Baik (Siap Pakai)'
  if (selectedCondition.value === 'KURANG_BAIK') return 'Kurang Baik'
  if (selectedCondition.value === 'RUSAK_BERAT') return 'Rusak Berat'
  return selectedCondition.value
})

let searchDebounceTimer = null
function handleSearchInput() {
  clearTimeout(searchDebounceTimer)
  searchDebounceTimer = setTimeout(() => {
    fetchData()
  }, 300)
}

function clearSearch() {
  searchQuery.value = ''
  fetchData()
}

function clearPokja() {
  selectedPokja.value = ''
  fetchData()
}

function clearLocation() {
  selectedLocation.value = ''
  fetchData()
}

function clearCondition() {
  selectedCondition.value = ''
  fetchData()
}

function resetFilters() {
  searchQuery.value = ''
  selectedPokja.value = ''
  selectedLocation.value = ''
  selectedCondition.value = ''
  fetchData()
}

// Accordion expanded state for catalog mode
const expandedItems = ref({})
const unitsByCatalog = ref({})
const loadingUnits = ref({})

// Modals
const showCreateModal = ref(false)
const useConditionSplit = ref(false)
const conditionSplit = ref({
  baik: 1,
  kurang_baik: 0,
  rusak_berat: 0
})

const createPhotoFile = ref(null)
const createPhotoPreview = ref('')

function handleCreatePhotoSelect(e) {
  const file = e.target.files[0]
  if (file) {
    createPhotoFile.value = file
    createPhotoPreview.value = URL.createObjectURL(file)
  }
}

function clearCreatePhoto() {
  createPhotoFile.value = null
  if (createPhotoPreview.value) {
    URL.revokeObjectURL(createPhotoPreview.value)
    createPhotoPreview.value = ''
  }
}

const createForm = ref({
  pokja_code: 'MAU',
  name: '',
  brand_model: '',
  quantity: 1,
  condition_status: 'BAIK',
  location_id: 1,
  notes: ''
})

const editingUnit = ref(null)
const selectedPhotoFile = ref(null)
const editForm = ref({
  condition_status: 'BAIK',
  location_id: 1,
  notes: '',
  remarks: ''
})

const decommissioningUnit = ref(null)
const decommissionReason = ref('')

onMounted(async () => {
  await Promise.all([fetchPokjas(), fetchLocations()])
  await fetchData()
})

async function fetchPokjas() {
  try {
    const res = await api.get('/pokja')
    pokjas.value = res.data
  } catch (err) {
    console.error(err)
  }
}

async function fetchLocations() {
  try {
    const res = await api.get('/locations')
    locations.value = res.data
    if (locations.value.length) {
      createForm.value.location_id = locations.value[0].id
    }
  } catch (err) {
    console.error(err)
  }
}

async function fetchData() {
  isLoading.value = true
  try {
    const params = {}
    if (selectedPokja.value) params.pokja_code = selectedPokja.value
    if (searchQuery.value.trim()) params.search = searchQuery.value.trim()
    if (selectedCondition.value) params.condition_status = selectedCondition.value
    if (selectedLocation.value) params.location_id = selectedLocation.value

    const [catRes, unitRes] = await Promise.all([
      api.get('/inventory/catalog', { params }),
      api.get('/inventory/units', { params })
    ])

    catalogs.value = catRes.data
    flatUnits.value = unitRes.data

    // Clear unit cache so re-expanded accordions reflect active filters
    unitsByCatalog.value = {}
  } catch (err) {
    console.error('Gagal mengambil data inventaris:', err)
  } finally {
    isLoading.value = false
  }
}

async function toggleExpand(itemId) {
  expandedItems.value[itemId] = !expandedItems.value[itemId]
  if (expandedItems.value[itemId] && !unitsByCatalog.value[itemId]) {
    loadingUnits.value[itemId] = true
    try {
      const params = {}
      if (selectedLocation.value) params.location_id = selectedLocation.value
      if (selectedCondition.value) params.condition_status = selectedCondition.value
      if (searchQuery.value.trim()) params.search = searchQuery.value.trim()

      const res = await api.get(`/inventory/catalog/${itemId}/units`, { params })
      unitsByCatalog.value[itemId] = res.data
    } catch (err) {
      console.error('Gagal memuat rincian unit:', err)
    } finally {
      loadingUnits.value[itemId] = false
    }
  }
}

function enableConditionSplit() {
  useConditionSplit.value = true
  conditionSplit.value.baik = createForm.value.quantity
  conditionSplit.value.kurang_baik = 0
  conditionSplit.value.rusak_berat = 0
}

const splitTotal = computed(() => {
  return (conditionSplit.value.baik || 0) + (conditionSplit.value.kurang_baik || 0) + (conditionSplit.value.rusak_berat || 0)
})

// Live sticker ID & condition preview (TASK 2)
const previewStickerList = computed(() => {
  if (!createForm.value.pokja_code || createForm.value.quantity <= 0) return []
  const selectedP = pokjas.value.find((p) => p.code === createForm.value.pokja_code)
  const currentSeq = selectedP ? selectedP.last_sequence : 0

  const conditions = []
  if (useConditionSplit.value) {
    for (let i = 0; i < (conditionSplit.value.baik || 0); i++) conditions.push('BAIK')
    for (let i = 0; i < (conditionSplit.value.kurang_baik || 0); i++) conditions.push('KURANG_BAIK')
    for (let i = 0; i < (conditionSplit.value.rusak_berat || 0); i++) conditions.push('RUSAK_BERAT')
  } else {
    for (let i = 0; i < createForm.value.quantity; i++) conditions.push(createForm.value.condition_status)
  }

  const list = []
  const maxPreview = Math.min(createForm.value.quantity, 15)
  for (let i = 1; i <= maxPreview; i++) {
    const seq = currentSeq + i
    const cond = conditions[i - 1] || 'BAIK'
    list.push({
      code: `${createForm.value.pokja_code}-${String(seq).padStart(3, '0')}`,
      condition: cond
    })
  }
  return list
})

async function handleCreateSubmit() {
  isSubmitting.value = true
  try {
    const payload = {
      ...createForm.value
    }
    if (useConditionSplit.value) {
      payload.condition_split = {
        baik: conditionSplit.value.baik || 0,
        kurang_baik: conditionSplit.value.kurang_baik || 0,
        rusak_berat: conditionSplit.value.rusak_berat || 0
      }
    }

    // 1. Simpan registrasi barang baru & unit-unitnya
    const res = await api.post('/inventory/bulk-create', payload)
    const newItemId = res.data?.data?.item_id

    // 2. Jika ada foto fisik yang dipotret / dipilih, unggah & kompresi ke WebP
    if (createPhotoFile.value && newItemId) {
      const formData = new FormData()
      formData.append('file', createPhotoFile.value)
      await api.post(`/inventory/catalog/${newItemId}/photo`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    }

    showCreateModal.value = false
    createForm.value.name = ''
    createForm.value.brand_model = ''
    createForm.value.notes = ''
    createForm.value.quantity = 1
    useConditionSplit.value = false
    clearCreatePhoto()
    await fetchPokjas()
    await fetchData()
    alert('Berhasil mendaftarkan inventaris baru beserta dokumentasi fotonya!')
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal menyimpan barang.')
  } finally {
    isSubmitting.value = false
  }
}

function openEditModal(unit) {
  editingUnit.value = unit
  editForm.value.condition_status = unit.condition_status
  editForm.value.location_id = unit.location_id
  editForm.value.notes = unit.notes || ''
  editForm.value.remarks = ''
  selectedPhotoFile.value = null
}

function handleCameraPhotoSelect(e) {
  selectedPhotoFile.value = e.target.files[0]
}

async function handleEditSubmit() {
  isSavingEdit.value = true
  try {
    // 1. Simpan perubahan atribut
    await api.patch(`/inventory/units/${editingUnit.value.unit_code}`, editForm.value)

    // 2. Jika ada foto baru dari kamera ponsel, unggah dan kompresi
    if (selectedPhotoFile.value) {
      const formData = new FormData()
      formData.append('file', selectedPhotoFile.value)
      await api.post(`/inventory/units/${editingUnit.value.unit_code}/photo`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    }

    editingUnit.value = null
    selectedPhotoFile.value = null
    await fetchData()
    alert('Data unit berhasil diperbarui!')
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal mengubah unit.')
  } finally {
    isSavingEdit.value = false
  }
}

function openDecommissionModal(unit) {
  decommissioningUnit.value = unit
  decommissionReason.value = ''
}

async function handleDecommissionSubmit() {
  try {
    await api.post(`/inventory/units/${decommissioningUnit.value.unit_code}/decommission`, {
      reason: decommissionReason.value
    })
    decommissioningUnit.value = null
    await fetchData()
    alert('Unit berhasil diarsipkan (Decommissioned)!')
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal mengarsipkan unit.')
  }
}

// Download Excel .xlsx dari Backend (TASK 5)
async function handleExportBackendExcel() {
  isExporting.value = true
  try {
    const params = {}
    if (selectedPokja.value) params.pokja_code = selectedPokja.value
    if (selectedCondition.value) params.condition_status = selectedCondition.value
    if (selectedLocation.value) params.location_id = selectedLocation.value
    if (searchQuery.value.trim()) params.search = searchQuery.value.trim()

    const response = await api.get('/inventory/export/excel', {
      params,
      responseType: 'blob'
    })

    const blob = new Blob([response.data], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    const dateStr = new Date().toISOString().split('T')[0]
    link.setAttribute('download', `Rekap_Inventaris_GKJW_Sukun_${dateStr}.xlsx`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (err) {
    alert('Gagal mengunduh berkas Excel.')
  } finally {
    isExporting.value = false
  }
}

function handlePrintBA() {
  const pokjaObj = pokjas.value.find((p) => p.code === selectedPokja.value)
  printBeritaAcaraStockOpname({
    pokjaName: pokjaObj ? `${pokjaObj.code} - ${pokjaObj.name}` : 'Semua Komisi',
    items: flatUnits.value,
    officerName: authStore.user?.name || 'Petugas Inventaris'
  })
}

function conditionBadgeClass(status) {
  if (status === 'BAIK') {
    return 'px-2 py-0.5 rounded bg-status-good-bg text-status-good-ink border border-status-good-ink font-semibold'
  }
  if (status === 'KURANG_BAIK') {
    return 'px-2 py-0.5 rounded bg-status-warn-bg text-status-warn-ink border border-status-warn-ink font-semibold'
  }
  return 'px-2 py-0.5 rounded bg-status-bad-bg text-status-bad-ink border border-status-bad-ink font-semibold'
}
</script>
