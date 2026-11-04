<template>
  <div class="min-h-screen bg-paper-canvas text-ink-primary relative overflow-x-hidden">
    <!-- ========================================================================= -->
    <!-- 1. FULLSCREEN IMMERSIVE WELCOMING ANIMATION (Architectural Church Style)  -->
    <!-- ========================================================================= -->
    <transition name="curtain-fade">
      <div
        v-if="showWelcoming"
        class="fixed inset-0 z-50 bg-paper-canvas flex flex-col justify-between p-6 sm:p-12 select-none overflow-hidden"
      >
        <!-- Architectural Drafting Corner Marks (+) -->
        <div class="absolute top-4 left-4 font-mono text-xs text-ink-muted select-none">+ 00.00</div>
        <div class="absolute top-4 right-4 font-mono text-xs text-ink-muted select-none">+ 24.POKJA</div>
        <div class="absolute bottom-4 left-4 font-mono text-xs text-ink-muted select-none">+ PBJ.SKN</div>
        <div class="absolute bottom-4 right-4 font-mono text-xs text-ink-muted select-none">+ REV.2.0</div>

        <!-- Top Status Bar -->
        <div class="flex items-center justify-between border-b-[1.5px] border-ink-primary pb-3 max-w-5xl w-full mx-auto animate-fade-down">
          <div class="flex items-center gap-2">
            <span class="w-2.5 h-2.5 rounded-full bg-church-terracotta animate-pulse"></span>
            <span class="text-xs font-mono font-bold tracking-widest uppercase">
              MENYIAPKAN SISTEM INVENTARIS GEREJA
            </span>
          </div>
          <span class="text-xs font-mono text-ink-secondary">
            MALANG, JAWA TIMUR
          </span>
        </div>

        <!-- Center Architectural Emblem & Reveal Sequence -->
        <div class="max-w-xl w-full mx-auto text-center py-6 sm:py-8 my-auto relative">
          <!-- Subtle Cross / Church Line Art Grid -->
          <div class="w-24 h-24 sm:w-28 sm:h-28 mx-auto mb-6 p-3 bg-paper-surface rounded-md border-[2px] border-ink-primary shadow-tactile-lg relative group">
            <img src="/Logo Gkjw Hitam.png" alt="Logo GKJW Sukun" class="w-full h-full object-contain filter drop-shadow" />
            <div class="absolute -bottom-2 -right-2 px-1.5 py-0.5 bg-church-terracotta text-white font-mono text-[9px] font-bold border border-ink-primary rounded">
              EST. SUKUN
            </div>
          </div>

          <!-- Stately Typography -->
          <span class="inline-block px-3 py-1 mb-2 text-[11px] font-mono font-bold uppercase tracking-wider bg-paper-subtle border border-ink-primary rounded shadow-tactile">
            Sistem Informasi Inventaris & Arsip Terpadu v2.0
          </span>

          <h1 class="text-2xl sm:text-3xl lg:text-4xl font-extrabold tracking-tight uppercase leading-tight mt-2 text-ink-primary">
            GREJA KRISTEN JAWI WETAN<br />
            <span class="text-church-terracotta">JEMAAT SUKUN</span>
          </h1>

          <p class="text-xs sm:text-sm text-ink-secondary mt-3 max-w-md mx-auto font-medium">
            Pencatatan tertib barang inventaris, pemberian nomor stiker unik, dan penyimpanan dokumen penting untuk 24 Komisi / POKJA.
          </p>

          <!-- Loading Progress Bar & Sequence Checklist -->
          <div class="mt-8 max-w-md mx-auto space-y-3">
            <div class="w-full bg-paper-subtle h-2.5 rounded border border-ink-primary overflow-hidden p-0.5">
              <div
                class="bg-church-terracotta h-full rounded transition-all duration-300"
                :style="{ width: `${animationProgress}%` }"
              ></div>
            </div>

            <div class="flex items-center justify-between text-[11px] font-mono text-ink-secondary">
              <span>{{ currentStatusText }}</span>
              <span class="font-bold text-ink-primary">{{ animationProgress }}%</span>
            </div>
          </div>
        </div>

        <!-- Bottom Actions (Instant Enter or Direct Officer Login) -->
        <div class="max-w-5xl w-full mx-auto pt-4 border-t-[1.5px] border-ink-primary flex flex-col sm:flex-row items-center justify-between gap-3">
          <span class="text-[11px] font-mono text-ink-muted order-2 sm:order-1">
            Tekan <kbd class="px-1.5 py-0.5 bg-paper-surface border border-ink-primary rounded font-bold">Space</kbd> atau <kbd class="px-1.5 py-0.5 bg-paper-surface border border-ink-primary rounded font-bold">Enter</kbd> untuk melewati
          </span>

          <div class="flex items-center gap-2 order-1 sm:order-2 w-full sm:w-auto">
            <button
              @click="dismissWelcoming"
              class="btn-secondary text-xs py-2 px-4 flex-1 sm:flex-initial"
            >
              Buka Halaman Utama &rarr;
            </button>
            <button
              @click="openLoginFromWelcoming"
              class="btn-primary text-xs py-2 px-4 flex-1 sm:flex-initial"
            >
              Masuk Pengurus &rarr;
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- ========================================================================= -->
    <!-- 2. MAIN PUBLIC LANDING PAGE CONTENT                                       -->
    <!-- ========================================================================= -->
    <div>
      <!-- HERO SECTION (#hero) -->
      <section id="hero" class="scroll-mt-24 max-w-7xl mx-auto px-4 lg:px-8 pt-8 pb-12 sm:pb-16">
        <div class="bg-paper-surface border-[2px] border-ink-primary rounded-lg p-6 sm:p-10 lg:p-12 shadow-tactile-lg relative overflow-hidden">
          <div class="max-w-3xl">
            <div class="inline-flex items-center gap-2 px-3 py-1 bg-paper-subtle border border-ink-primary rounded text-xs font-mono font-semibold mb-4">
              <span class="w-2 h-2 rounded-full bg-status-good-ink animate-pulse"></span>
              HALAMAN INFORMASI &bull; TERBUKA UNTUK WARGA JEMAAT
            </div>

            <h2 class="text-2xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight leading-[1.15]">
              Pengelolaan & Pencatatan Barang Gereja Lintas 24 Komisi.
            </h2>

            <p class="text-sm sm:text-base text-ink-secondary mt-4 leading-relaxed font-medium">
              Sistem resmi GKJW Jemaat Sukun untuk memudahkan pengurus komisi mencatat barang inventaris gereja, 
              menempelkan nomor stiker unik agar tidak tertukar, serta menyimpan kuitansi dan dokumen penting secara aman dan rapi.
            </p>

            <!-- Real Live Public Stats -->
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-6 pt-6 border-t border-paper-border">
              <div class="p-3 bg-paper-canvas border border-ink-primary rounded">
                <span class="text-[10px] font-mono font-bold uppercase text-ink-secondary block">Komisi Gereja</span>
                <span class="text-2xl font-mono font-extrabold text-ink-primary">{{ publicStats.total_pokja }}</span>
                <span class="text-[10px] text-ink-muted block mt-0.5">Komisi Aktif</span>
              </div>
              <div class="p-3 bg-paper-canvas border border-ink-primary rounded">
                <span class="text-[10px] font-mono font-bold uppercase text-ink-secondary block">Jenis Barang</span>
                <span class="text-2xl font-mono font-extrabold text-church-terracotta">{{ publicStats.total_items }}</span>
                <span class="text-[10px] text-ink-muted block mt-0.5">Macam Barang</span>
              </div>
              <div class="p-3 bg-paper-canvas border border-ink-primary rounded">
                <span class="text-[10px] font-mono font-bold uppercase text-ink-secondary block">Total Unit Barang</span>
                <span class="text-2xl font-mono font-extrabold text-ink-primary">{{ publicStats.total_units }}</span>
                <span class="text-[10px] text-ink-muted block mt-0.5">Ada Stikernya</span>
              </div>
              <div class="p-3 bg-paper-canvas border border-ink-primary rounded">
                <span class="text-[10px] font-mono font-bold uppercase text-status-good-ink block">Kondisi Baik</span>
                <span class="text-2xl font-mono font-extrabold text-status-good-ink">{{ publicStats.total_good }}</span>
                <span class="text-[10px] text-ink-muted block mt-0.5">Siap Dipakai</span>
              </div>
            </div>

            <!-- Main CTA Buttons -->
            <div class="flex flex-wrap items-center gap-3 mt-8">
              <button
                @click="openLoginModal"
                class="btn-primary text-xs sm:text-sm py-3 px-5 shadow-tactile"
              >
                Masuk Akun Pengurus / Petugas &rarr;
              </button>
              
              <button
                @click="scrollTo('guide')"
                class="btn-secondary text-xs sm:text-sm py-3 px-5 shadow-tactile"
              >
                Tata Cara Penggunaan
              </button>

              <button
                @click="scrollTo('pokja')"
                class="btn-secondary text-xs sm:text-sm py-3 px-5 shadow-tactile"
              >
                Daftar 24 Komisi
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- 4 VALUE PROPOSITION CARDS -->
      <section class="max-w-7xl mx-auto px-4 lg:px-8 pb-12 sm:pb-16">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="bg-paper-surface border-[1.5px] border-ink-primary p-5 rounded-md shadow-tactile">
            <div class="text-xs font-mono font-bold uppercase text-church-terracotta">Pencatatan Rapi</div>
            <h3 class="text-base font-bold mt-1">Kelompokkan Barang Sejenis</h3>
            <p class="text-xs text-ink-secondary mt-2 leading-relaxed">
              Mencatat 20 mikrofon atau 50 kursi yang sama cukup dalam satu kelompok nama barang. Daftar inventaris tetap ringkas dan tidak berantakan.
            </p>
          </div>

          <div class="bg-paper-surface border-[1.5px] border-ink-primary p-5 rounded-md shadow-tactile">
            <div class="text-xs font-mono font-bold uppercase text-church-terracotta">Stiker Fisik</div>
            <h3 class="text-base font-bold mt-1">Nomor Stiker Tidak Tertukar</h3>
            <p class="text-xs text-ink-secondary mt-2 leading-relaxed">
              Setiap barang mendapatkan kode unik (contoh: <span class="font-mono font-semibold">MAU-001</span>) yang tidak akan pernah hilang atau dipakai barang lain.
            </p>
          </div>

          <div class="bg-paper-surface border-[1.5px] border-ink-primary p-5 rounded-md shadow-tactile">
            <div class="text-xs font-mono font-bold uppercase text-church-terracotta">Keamanan Berkas</div>
            <h3 class="text-base font-bold mt-1">Dokumen Penting Terlindungi</h3>
            <p class="text-xs text-ink-secondary mt-2 leading-relaxed">
              Nota kuitansi pembelian, kartu garansi, dan surat keputusan tersimpan aman. Hanya majelis dan pengurus yang dapat membukanya.
            </p>
          </div>

          <div class="bg-paper-surface border-[1.5px] border-ink-primary p-5 rounded-md shadow-tactile">
            <div class="text-xs font-mono font-bold uppercase text-church-terracotta">Laporan Mudah</div>
            <h3 class="text-base font-bold mt-1">Cetak Laporan Sekali Klik</h3>
            <p class="text-xs text-ink-secondary mt-2 leading-relaxed">
              Tinggal klik untuk mengunduh daftar barang ke file Excel atau mencetak lembar Berita Acara yang siap ditandatangani saat rapat majelis.
            </p>
          </div>
        </div>
      </section>

      <!-- TUTORIAL & ALUR PENGGUNAAN (#guide) -->
      <section id="guide" class="scroll-mt-28 max-w-7xl mx-auto px-4 lg:px-8 pb-12 sm:pb-16">
        <div class="bg-paper-surface border-[2px] border-ink-primary rounded-lg p-6 sm:p-10 shadow-tactile-lg">
          <div class="border-b-[1.5px] border-ink-primary pb-4 mb-8 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <span class="text-xs font-mono font-bold uppercase text-church-terracotta">Panduan Praktis Pengurus</span>
              <h3 class="text-xl sm:text-2xl font-bold tracking-tight mt-1">
                Tata Cara Mudah Pengelolaan Barang &amp; Inventaris
              </h3>
            </div>
            <span class="text-xs font-mono px-2.5 py-1 bg-paper-subtle border border-ink-primary rounded self-start sm:self-auto">
              Panduan Resmi v2.0
            </span>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <!-- Step 1 -->
            <div class="space-y-2.5 p-4 bg-paper-canvas border border-ink-primary rounded">
              <div class="w-8 h-8 rounded bg-ink-primary text-white font-mono font-bold flex items-center justify-center text-sm shadow-tactile">
                01
              </div>
              <h4 class="font-bold text-sm text-ink-primary">Catat Barang Sekaligus</h4>
              <p class="text-xs text-ink-secondary leading-relaxed">
                Pengurus memilih komisi, nama barang, merk, dan jumlahnya. Jika kondisinya campur (misal: 7 baik, 3 rusak ringan), bisa langsung dibagi dalam satu kali simpan tanpa mengetik berulang.
              </p>
            </div>

            <!-- Step 2 -->
            <div class="space-y-2.5 p-4 bg-paper-canvas border border-ink-primary rounded">
              <div class="w-8 h-8 rounded bg-ink-primary text-white font-mono font-bold flex items-center justify-center text-sm shadow-tactile">
                02
              </div>
              <h4 class="font-bold text-sm text-ink-primary">Tempelkan Nomor Stiker</h4>
              <p class="text-xs text-ink-secondary leading-relaxed">
                Sistem otomatis membuatkan nomor kode stiker berurutan (contoh: <span class="font-mono font-bold text-church-terracotta">MVI-012</span>). Tulis atau tempelkan pada badan barang sebelum disimpan di ruangan.
              </p>
            </div>

            <!-- Step 3 -->
            <div class="space-y-2.5 p-4 bg-paper-canvas border border-ink-primary rounded">
              <div class="w-8 h-8 rounded bg-ink-primary text-white font-mono font-bold flex items-center justify-center text-sm shadow-tactile">
                03
              </div>
              <h4 class="font-bold text-sm text-ink-primary">Perbarui Kondisi &amp; Foto Barang</h4>
              <p class="text-xs text-ink-secondary leading-relaxed">
                Bila ada satu barang yang rusak atau berpindah ruangan, cukup ubah data barang tersebut. Anda juga bisa langsung memotret barangnya lewat kamera HP sebagai bukti.
              </p>
            </div>

            <!-- Step 4 -->
            <div class="space-y-2.5 p-4 bg-paper-canvas border border-ink-primary rounded">
              <div class="w-8 h-8 rounded bg-ink-primary text-white font-mono font-bold flex items-center justify-center text-sm shadow-tactile">
                04
              </div>
              <h4 class="font-bold text-sm text-ink-primary">Penyimpanan Arsip Barang</h4>
              <p class="text-xs text-ink-secondary leading-relaxed">
                Barang yang rusak total atau sudah tidak terpakai tetap disimpan datanya sebagai arsip bersama Berita Acara Majelis, agar riwayat pembukuan gereja tetap lengkap dan jelas.
              </p>
            </div>
          </div>
        </div>
      </section>

      <!-- 24 POKJA REFERENCE GRID (#pokja) -->
      <section id="pokja" class="scroll-mt-24 max-w-7xl mx-auto px-4 lg:px-8 pb-16">
        <div class="bg-paper-surface border-[2px] border-ink-primary rounded-lg p-6 sm:p-8 shadow-tactile-lg">
          <div class="flex items-center justify-between border-b-[1.5px] border-ink-primary pb-3 mb-6">
            <div>
              <span class="text-xs font-mono font-bold uppercase text-church-terracotta">Struktur Kelembagaan</span>
              <h3 class="text-lg sm:text-xl font-bold">24 Komisi / POKJA GKJW Sukun</h3>
            </div>
            <span class="text-xs font-mono font-bold px-2.5 py-1 bg-paper-subtle border border-ink-primary rounded">
              24 Komisi Terdaftar
            </span>
          </div>

          <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
            <div
              v-for="p in pokjaList"
              :key="p.code"
              class="p-3 bg-paper-canvas border border-ink-primary rounded flex flex-col justify-between hover:bg-paper-subtle transition-all shadow-[1px_1px_0px_#141413]"
            >
              <span class="font-mono font-extrabold text-sm text-church-terracotta tracking-wider">
                {{ p.code }}
              </span>
              <span class="text-[11px] font-medium leading-tight text-ink-primary mt-1">
                {{ p.name }}
              </span>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- Replay Welcoming Animation Button & Footer Info -->
    <div class="max-w-7xl mx-auto px-4 lg:px-8 pb-6 flex items-center justify-between text-xs font-mono text-ink-muted">
      <span>Portal Informasi GKJW Sukun</span>
      <button
        @click="replayWelcoming"
        class="hover:text-church-terracotta underline cursor-pointer"
      >
        ↺ Putar Ulang Animasi Pembuka
      </button>
    </div>

    <!-- Login Modal Component -->
    <LoginModal
      :is-open="isLoginModalOpen"
      @close="isLoginModalOpen = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import LoginModal from '../components/auth/LoginModal.vue'
import api from '../api'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// State welcoming animation
const showWelcoming = ref(false)
const animationProgress = ref(0)
const currentStatusText = ref('Menghubungkan basis data...')
let animationInterval = null

// Login Modal
const isLoginModalOpen = ref(false)

// Public Live Stats
const publicStats = ref({
  total_pokja: 24,
  total_items: 0,
  total_units: 0,
  total_good: 0
})

onMounted(async () => {
  // Ambil ringkasan publik dari backend
  try {
    const res = await api.get('/inventory/public/summary')
    publicStats.value = res.data
  } catch (err) {
    // Gunakan fallback default jika backend sedang offline
  }

  // Cek apakah sudah pernah melihat welcoming animation di sesi ini
  const hasSeen = sessionStorage.getItem('hasSeenWelcoming_v2')
  if (!hasSeen) {
    startWelcomingAnimation()
  }

  // Handle hash scrolling jika datang dengan #guide atau #pokja
  if (route.hash) {
    setTimeout(() => {
      scrollTo(route.hash.replace('#', ''))
    }, 200)
  }

  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  if (animationInterval) clearInterval(animationInterval)
  window.removeEventListener('keydown', handleKeydown)
})

function startWelcomingAnimation() {
  showWelcoming.value = true
  animationProgress.value = 10
  currentStatusText.value = 'Menyiapkan data 24 Komisi / POKJA...'

  let progress = 10
  animationInterval = setInterval(() => {
    progress += 15
    if (progress >= 40 && progress < 70) {
      currentStatusText.value = 'Menyiapkan nomor stiker barang otomatis...'
    } else if (progress >= 70 && progress < 95) {
      currentStatusText.value = 'Memeriksa kelengkapan catatan perbendaharaan...'
    } else if (progress >= 100) {
      progress = 100
      currentStatusText.value = 'Selesai, sistem siap digunakan.'
      clearInterval(animationInterval)
      // Otomatis selesai setelah selesai progress
      setTimeout(() => {
        dismissWelcoming()
      }, 700)
    }
    animationProgress.value = Math.min(progress, 100)
  }, 220)
}

function dismissWelcoming() {
  if (animationInterval) clearInterval(animationInterval)
  showWelcoming.value = false
  sessionStorage.setItem('hasSeenWelcoming_v2', 'true')
}

function replayWelcoming() {
  sessionStorage.removeItem('hasSeenWelcoming_v2')
  startWelcomingAnimation()
}

function openLoginFromWelcoming() {
  dismissWelcoming()
  openLoginModal()
}

function openLoginModal() {
  if (authStore.isAuthenticated) {
    router.push('/dashboard')
  } else {
    isLoginModalOpen.value = true
  }
}

// Precision Smooth Scroll dengan kompensasi Sticky Navbar Header (70px)
function scrollTo(sectionId) {
  if (sectionId === 'hero') {
    window.scrollTo({ top: 0, behavior: 'smooth' })
    return
  }
  const el = document.getElementById(sectionId)
  if (el) {
    const headerOffset = 70
    const elementPosition = el.getBoundingClientRect().top
    const offsetPosition = elementPosition + window.pageYOffset - headerOffset
    window.scrollTo({
      top: offsetPosition,
      behavior: 'smooth'
    })
  }
}

function handleKeydown(e) {
  if (showWelcoming.value && (e.key === ' ' || e.key === 'Enter' || e.key === 'Escape')) {
    e.preventDefault()
    dismissWelcoming()
  }
}

// 24 POKJA Resmi GKJW Sukun
const pokjaList = [
  { code: 'KTP', name: 'Katekisasi & Perkawinan' },
  { code: 'MSG', name: 'Musik Gerejawi' },
  { code: 'MVI', name: 'Multimedia Visual' },
  { code: 'MAU', name: 'Multimedia Audio' },
  { code: 'PAN', name: 'Pelayanan Anak' },
  { code: 'PRE', name: 'Pelayanan Remaja' },
  { code: 'PPM', name: 'Pembinaan Pemuda & Mahasiswa' },
  { code: 'ARP', name: 'Perlindungan & Pendampingan ARP' },
  { code: 'PWW', name: 'Pembinaan Peranan Wanita' },
  { code: 'ADY', name: 'Pembinaan Peranan Adiyuswa' },
  { code: 'KPT', name: 'Pembinaan Teologi' },
  { code: 'GKS', name: 'Pelayanan Kesehatan (GAKES)' },
  { code: 'GRU', name: 'Pelayanan Guru (GARU)' },
  { code: 'HJU', name: 'Gereja Hijau' },
  { code: 'TBN', name: 'Pelayanan Tanggul Bencana' },
  { code: 'WRA', name: 'Pelayanan Kewirausahaan' },
  { code: 'DUK', name: 'Pelayanan Duka' },
  { code: 'INV', name: 'Inventaris & Perpustakaan' },
  { code: 'URT', name: 'Pelayanan URTG' },
  { code: 'KMN', name: 'Keamanan' },
  { code: 'PBG', name: 'Pembangunan' },
  { code: 'LIT', name: 'Litbang & Perencanaan' },
  { code: 'PBJ', name: 'Pengawasan Perbendaharaan' },
  { code: 'UUM', name: 'Antar Umat Beragama' },
]
</script>

<style scoped>
.curtain-fade-enter-active,
.curtain-fade-leave-active {
  transition: all 400ms cubic-bezier(0.16, 1, 0.3, 1);
}
.curtain-fade-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}
.curtain-fade-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

@keyframes fadeDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.animate-fade-down {
  animation: fadeDown 0.4s ease-out;
}
</style>
