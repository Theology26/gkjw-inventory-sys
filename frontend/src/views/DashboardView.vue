<template>
  <div class="max-w-7xl mx-auto p-3 sm:p-4 lg:p-6 space-y-4 sm:space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-paper-surface p-4 border-[1.5px] border-ink-primary rounded-md shadow-tactile">
      <div>
        <h2 class="text-lg sm:text-xl font-bold tracking-tight">Ringkasan Inventaris &amp; Dokumen Gereja</h2>
        <p class="text-xs text-ink-secondary mt-0.5">
          Informasi aset barang milik 24 Komisi / POKJA GKJW Sukun untuk Majelis dan Pengawas Perbendaharaan (PBJ).
        </p>
      </div>

      <div class="flex items-center gap-2">
        <router-link to="/inventory" class="btn-primary text-xs py-2 px-3.5 w-full sm:w-auto text-center">
          Buka Daftar Barang &rarr;
        </router-link>
      </div>
    </div>

    <!-- 4 KPI Metrics Grid -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
      <div class="bg-paper-surface p-3.5 sm:p-5 border-[1.5px] border-ink-primary rounded-md shadow-tactile">
        <span class="text-[10px] sm:text-xs font-mono font-bold uppercase text-ink-secondary">Total Unit Barang</span>
        <div class="text-2xl sm:text-3xl font-mono font-extrabold mt-1 sm:mt-2 text-ink-primary">
          {{ totalActiveUnits }}
        </div>
        <span class="text-[10px] sm:text-[11px] text-ink-muted mt-0.5 block">Sudah Diberi Stiker</span>
      </div>

      <div class="bg-paper-surface p-3.5 sm:p-5 border-[1.5px] border-ink-primary rounded-md shadow-tactile">
        <span class="text-[10px] sm:text-xs font-mono font-bold uppercase text-status-good-ink">Kondisi Baik</span>
        <div class="text-2xl sm:text-3xl font-mono font-extrabold mt-1 sm:mt-2 text-status-good-ink">
          {{ totalGoodUnits }}
        </div>
        <span class="text-[10px] sm:text-[11px] text-ink-muted mt-0.5 block">Siap Digunakan Ibadah</span>
      </div>

      <div class="bg-paper-surface p-3.5 sm:p-5 border-[1.5px] border-ink-primary rounded-md shadow-tactile">
        <span class="text-[10px] sm:text-xs font-mono font-bold uppercase text-status-bad-ink">Perlu Perbaikan</span>
        <div class="text-2xl sm:text-3xl font-mono font-extrabold mt-1 sm:mt-2 text-status-bad-ink">
          {{ totalDamagedUnits }}
        </div>
        <span class="text-[10px] sm:text-[11px] text-ink-muted mt-0.5 block">Kurang Baik &amp; Rusak</span>
      </div>

      <div class="bg-paper-surface p-3.5 sm:p-5 border-[1.5px] border-ink-primary rounded-md shadow-tactile">
        <span class="text-[10px] sm:text-xs font-mono font-bold uppercase text-church-terracotta">24 Komisi / POKJA</span>
        <div class="text-2xl sm:text-3xl font-mono font-extrabold mt-1 sm:mt-2 text-church-terracotta">
          {{ pokjas.length || 24 }}
        </div>
        <span class="text-[10px] sm:text-[11px] text-ink-muted mt-0.5 block">Seluruh Komisi Aktif</span>
      </div>
    </div>

    <!-- POKJA Distribution & Sequence Tracker Table -->
    <div class="bg-paper-surface border-[1.5px] border-ink-primary rounded-md shadow-tactile overflow-hidden">
      <div class="p-3.5 border-b border-paper-border bg-paper-subtle flex items-center justify-between">
        <span class="text-xs font-mono font-bold uppercase text-ink-secondary">
          Daftar Barang per Komisi &amp; Nomor Stiker Terakhir
        </span>
        <span class="text-xs font-mono font-bold px-2 py-0.5 bg-paper-surface border border-ink-primary rounded">
          Nomor Stiker Otomatis
        </span>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse text-xs min-w-[500px]">
          <thead>
            <tr class="border-b-[1.5px] border-ink-primary bg-paper-subtle font-mono text-[11px] uppercase text-ink-secondary">
              <th class="py-2 px-3">Kode</th>
              <th class="py-2 px-3">Nama Komisi / POKJA</th>
              <th class="py-2 px-3 text-center">Nomor Urut Terakhir</th>
              <th class="py-2 px-3 text-center">Macam Barang</th>
              <th class="py-2 px-3 text-center">Total Unit Barang</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-paper-border font-mono text-xs">
            <tr v-for="p in pokjas" :key="p.code" class="hover:bg-paper-subtle/30">
              <td class="py-2 px-3 font-bold text-church-terracotta">{{ p.code }}</td>
              <td class="py-2 px-3 font-sans font-medium text-ink-primary">{{ p.name }}</td>
              <td class="py-2 px-3 text-center font-bold">
                <span class="px-2 py-0.5 bg-paper-canvas border border-paper-border rounded">
                  {{ p.code }}-{{ String(p.last_sequence).padStart(3, '0') }}
                </span>
              </td>
              <td class="py-2 px-3 text-center">{{ p.total_items }}</td>
              <td class="py-2 px-3 text-center font-bold">{{ p.total_units }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../api'

const pokjas = ref([])
const units = ref([])
const isLoading = ref(true)

onMounted(async () => {
  try {
    const [pokjaRes, unitRes] = await Promise.all([
      api.get('/pokja'),
      api.get('/inventory/units')
    ])
    pokjas.value = pokjaRes.data
    units.value = unitRes.data
  } catch (err) {
    console.error('Gagal mengambil ringkasan:', err)
  } finally {
    isLoading.value = false
  }
})

const totalActiveUnits = computed(() => {
  return units.value.filter((u) => u.lifecycle_status === 'ACTIVE').length
})

const totalGoodUnits = computed(() => {
  return units.value.filter((u) => u.condition_status === 'BAIK' && u.lifecycle_status === 'ACTIVE').length
})

const totalDamagedUnits = computed(() => {
  return units.value.filter((u) => u.condition_status !== 'BAIK' && u.lifecycle_status === 'ACTIVE').length
})
</script>
