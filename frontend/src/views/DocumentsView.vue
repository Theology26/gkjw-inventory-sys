<template>
  <div class="max-w-7xl mx-auto p-3 sm:p-4 lg:p-6 space-y-4 sm:space-y-6">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-paper-surface p-4 border-[1.5px] border-ink-primary rounded-md shadow-tactile">
      <div>
        <div class="flex items-center gap-2 mb-1">
          <span class="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-status-good-bg text-status-good-ink border border-status-good-ink">
            BERKAS RESMI &bull; KHUSUS PENGURUS &amp; MAJELIS
          </span>
        </div>
        <h2 class="text-lg sm:text-xl font-bold tracking-tight">Arsip Dokumen &amp; Kuitansi Gereja</h2>
        <p class="text-xs text-ink-secondary mt-0.5">
          Tempat menyimpan kuitansi belanja, kartu garansi, surat perjanjian, dan Berita Acara Majelis secara aman.
        </p>
      </div>

      <div class="flex items-center gap-2">
        <button
          @click="showUploadModal = true"
          class="btn-primary text-xs py-2 px-3.5 w-full sm:w-auto"
        >
          + Simpan Dokumen / Kuitansi
        </button>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 bg-paper-surface p-3.5 border-[1.5px] border-ink-primary rounded-md">
      <div>
        <label class="block text-xs font-bold uppercase text-ink-secondary mb-1">Cari Dokumen / Kuitansi</label>
        <input
          v-model="searchQuery"
          @input="fetchDocuments"
          type="text"
          placeholder="Ketik judul, nomor surat, nomor nota..."
          class="input-tactile text-xs h-9"
        />
      </div>

      <div>
        <label class="block text-xs font-bold uppercase text-ink-secondary mb-1">Pilih Komisi / POKJA</label>
        <select v-model="selectedPokjaId" @change="fetchDocuments" class="input-tactile text-xs h-9">
          <option value="">Semua Komisi</option>
          <option v-for="p in pokjas" :key="p.id" :value="p.id">
            {{ p.code }} — {{ p.name }}
          </option>
        </select>
      </div>
    </div>

    <!-- Documents Table -->
    <div class="bg-paper-surface border-[1.5px] border-ink-primary rounded-md shadow-tactile overflow-hidden">
      <div class="p-3.5 border-b border-paper-border bg-paper-subtle flex items-center justify-between">
        <span class="text-xs font-mono font-bold uppercase text-ink-secondary">
          Daftar Berkas yang Tersimpan Aman
        </span>
        <span class="text-xs font-mono font-bold px-2 py-0.5 bg-paper-surface border border-ink-primary rounded">
          Total: {{ documents.length }} Berkas
        </span>
      </div>

      <div v-if="isLoading" class="p-12 text-center text-ink-secondary font-mono text-xs">
        Memuat arsip berkas gereja...
      </div>

      <div v-else-if="!documents.length" class="p-12 text-center text-ink-secondary font-mono text-xs">
        Belum ada berkas arsip yang diunggah.
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full text-left border-collapse text-xs min-w-[650px]">
          <thead>
            <tr class="border-b-[1.5px] border-ink-primary bg-paper-subtle font-mono text-[11px] uppercase text-ink-secondary">
              <th class="py-2.5 px-3">Nomor Surat / Nota</th>
              <th class="py-2.5 px-3">Judul Berkas</th>
              <th class="py-2.5 px-3">POKJA</th>
              <th class="py-2.5 px-3">Lokasi Fisik Map</th>
              <th class="py-2.5 px-3">Tipe / Ukuran</th>
              <th class="py-2.5 px-3">Pengunggah</th>
              <th class="py-2.5 px-3 text-right">Aksi</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-paper-border font-mono text-xs">
            <tr v-for="doc in documents" :key="doc.id" class="hover:bg-paper-subtle/30">
              <td class="py-2.5 px-3 font-bold text-church-terracotta">
                {{ doc.doc_number || '-' }}
              </td>
              <td class="py-2.5 px-3 font-sans font-bold text-ink-primary">
                {{ doc.title }}
              </td>
              <td class="py-2.5 px-3">
                <span class="px-2 py-0.5 bg-paper-canvas border border-ink-primary rounded text-[11px] font-bold">
                  {{ doc.pokja_code || 'Umum' }}
                </span>
              </td>
              <td class="py-2.5 px-3 font-sans text-ink-secondary">
                {{ doc.physical_storage_loc || 'Brankas Kantor Gereja' }}
              </td>
              <td class="py-2.5 px-3 text-[11px] uppercase">
                {{ doc.file_type }} ({{ formatBytes(doc.file_size_bytes) }})
              </td>
              <td class="py-2.5 px-3 font-sans text-ink-secondary">
                {{ doc.uploaded_by_name || 'Admin' }}
              </td>
              <td class="py-2.5 px-3 text-right">
                <a
                  :href="`/uploads/${doc.file_path}`"
                  target="_blank"
                  class="btn-secondary text-[11px] py-1 px-2.5 inline-flex items-center gap-1"
                >
                  Buka Berkas &rarr;
                </a>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- MODAL: UPLOAD DOKUMEN -->
    <div v-if="showUploadModal" class="fixed inset-0 z-50 bg-ink-primary/60 backdrop-blur-[2px] flex items-center justify-center p-3 sm:p-4">
      <div class="max-w-md w-full bg-paper-surface border-[2px] border-ink-primary rounded-md p-5 sm:p-6 shadow-tactile-lg max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between border-b-[1.5px] border-ink-primary pb-3 mb-4">
          <h3 class="text-sm font-bold uppercase">Unggah Dokumen Arsip Gereja</h3>
          <button @click="showUploadModal = false" class="font-mono font-bold p-1">✕</button>
        </div>

        <form @submit.prevent="handleUploadSubmit" class="space-y-3.5 text-xs">
          <div>
            <label class="block font-bold uppercase text-ink-secondary mb-1">Judul Dokumen *</label>
            <input v-model="uploadForm.title" type="text" placeholder="Contoh: Nota Pengadaan Mic KREZT" required class="input-tactile text-xs" />
          </div>

          <div>
            <label class="block font-bold uppercase text-ink-secondary mb-1">Nomor Surat / Nota (Opsional)</label>
            <input v-model="uploadForm.doc_number" type="text" placeholder="Contoh: 142/GKJW-SKN/VII/2025" class="input-tactile text-xs" />
          </div>

          <div>
            <label class="block font-bold uppercase text-ink-secondary mb-1">Komisi / POKJA Terkait</label>
            <select v-model="uploadForm.pokja_id" class="input-tactile text-xs">
              <option value="">Umum / Majelis Jemaat</option>
              <option v-for="p in pokjas" :key="p.id" :value="p.id">{{ p.code }} — {{ p.name }}</option>
            </select>
          </div>

          <div>
            <label class="block font-bold uppercase text-ink-secondary mb-1">Lokasi Penyimpanan Map Fisik *</label>
            <input v-model="uploadForm.physical_storage_loc" type="text" placeholder="Misal: Lemari Arsip Kantor Lt 1 / Brankas PBJ" required class="input-tactile text-xs" />
          </div>

          <div>
            <label class="block font-bold uppercase text-ink-secondary mb-1">Pilih File (PDF, Foto Nota, DOCX) *</label>
            <input
              @change="handleFileChange"
              type="file"
              accept=".pdf,image/*,.docx"
              capture="environment"
              required
              class="text-xs file:mr-3 file:py-1.5 file:px-3 file:rounded file:border file:border-ink-primary file:bg-paper-canvas file:font-semibold cursor-pointer"
            />
          </div>

          <div class="pt-3 flex justify-end gap-2 border-t border-paper-border">
            <button type="button" @click="showUploadModal = false" class="btn-secondary text-xs py-1.5 px-3">Batal</button>
            <button type="submit" :disabled="isUploading" class="btn-primary text-xs py-1.5 px-3">
              {{ isUploading ? 'Mengunggah...' : 'Unggah Sekarang' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const documents = ref([])
const pokjas = ref([])
const isLoading = ref(true)
const isUploading = ref(false)

const searchQuery = ref('')
const selectedPokjaId = ref('')

const showUploadModal = ref(false)
const uploadForm = ref({
  title: '',
  doc_number: '',
  pokja_id: '',
  physical_storage_loc: 'Lemari Arsip Kantor Gereja'
})
const selectedFile = ref(null)

onMounted(async () => {
  try {
    const pRes = await api.get('/pokja')
    pokjas.value = pRes.data
    await fetchDocuments()
  } catch (err) {
    console.error(err)
  }
})

async function fetchDocuments() {
  isLoading.value = true
  try {
    const params = {}
    if (selectedPokjaId.value) params.pokja_id = selectedPokjaId.value
    if (searchQuery.value) params.search = searchQuery.value

    const res = await api.get('/documents', { params })
    documents.value = res.data
  } catch (err) {
    console.error('Gagal mengambil dokumen:', err)
  } finally {
    isLoading.value = false
  }
}

function handleFileChange(e) {
  selectedFile.value = e.target.files[0]
}

async function handleUploadSubmit() {
  if (!selectedFile.value) {
    alert('Pilih file terlebih dahulu.')
    return
  }

  isUploading.value = true
  try {
    const formData = new FormData()
    formData.append('title', uploadForm.value.title)
    if (uploadForm.value.doc_number) formData.append('doc_number', uploadForm.value.doc_number)
    if (uploadForm.value.pokja_id) formData.append('pokja_id', uploadForm.value.pokja_id)
    formData.append('physical_storage_loc', uploadForm.value.physical_storage_loc)
    formData.append('file', selectedFile.value)

    await api.post('/documents', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    showUploadModal.value = false
    uploadForm.value.title = ''
    uploadForm.value.doc_number = ''
    selectedFile.value = null
    await fetchDocuments()
    alert('Dokumen berhasil diunggah ke arsip gereja!')
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal mengunggah dokumen.')
  } finally {
    isUploading.value = false
  }
}

function formatBytes(bytes) {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}
</script>
