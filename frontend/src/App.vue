<template>
  <div class="min-h-screen flex flex-col bg-paper-canvas text-ink-primary">
    <!-- Header / Navbar -->
    <header class="bg-paper-surface border-b-[1.5px] border-ink-primary px-4 lg:px-8 py-3 sticky top-0 z-40 flex items-center justify-between">
      <!-- Church Brand -->
      <router-link to="/" class="flex items-center gap-2.5 sm:gap-3 group">
        <div class="w-9 h-9 sm:w-10 sm:h-10 rounded-md bg-paper-canvas flex items-center justify-center p-1 border-[1.5px] border-ink-primary shadow-tactile group-hover:bg-paper-subtle transition-colors overflow-hidden">
          <img src="/Logo Gkjw Hitam.png" alt="Logo GKJW" class="w-full h-full object-contain" />
        </div>
        <div>
          <h1 class="text-xs sm:text-sm font-extrabold tracking-tight uppercase leading-none">
            GKJW SUKUN
          </h1>
          <p class="text-[9px] sm:text-xs text-ink-secondary font-medium tracking-wide mt-0.5">
            Inventaris & Arsip v2.0
          </p>
        </div>
      </router-link>

      <!-- Navigation Links -->
      <nav class="hidden md:flex items-center gap-1 font-medium text-xs sm:text-sm">
        <!-- Public Navigation (When not authenticated) -->
        <template v-if="!authStore.isAuthenticated">
          <button
            @click="navigateTo('hero')"
            class="px-3 py-1.5 rounded-md border-[1.5px] border-transparent hover:border-ink-primary hover:bg-paper-subtle transition-all duration-100 font-semibold cursor-pointer"
            :class="{ '!border-ink-primary bg-paper-subtle shadow-tactile': isCurrentSection('hero') }"
          >
            Beranda
          </button>
          <button
            @click="navigateTo('guide')"
            class="px-3 py-1.5 rounded-md border-[1.5px] border-transparent hover:border-ink-primary hover:bg-paper-subtle transition-all duration-100 font-semibold cursor-pointer"
            :class="{ '!border-ink-primary bg-paper-subtle shadow-tactile': isCurrentSection('guide') }"
          >
            Panduan Alur
          </button>
          <button
            @click="navigateTo('pokja')"
            class="px-3 py-1.5 rounded-md border-[1.5px] border-transparent hover:border-ink-primary hover:bg-paper-subtle transition-all duration-100 font-semibold cursor-pointer"
            :class="{ '!border-ink-primary bg-paper-subtle shadow-tactile': isCurrentSection('pokja') }"
          >
            24 POKJA
          </button>
        </template>

        <!-- Officer / Admin Navigation (When authenticated) -->
        <template v-else>
          <router-link
            to="/dashboard"
            class="px-3 py-1.5 rounded-md border-[1.5px] border-transparent hover:border-ink-primary transition-all duration-100"
            active-class="!border-ink-primary bg-paper-subtle font-bold shadow-tactile"
          >
            Ringkasan
          </router-link>
          <router-link
            to="/inventory"
            class="px-3 py-1.5 rounded-md border-[1.5px] border-transparent hover:border-ink-primary transition-all duration-100"
            active-class="!border-ink-primary bg-paper-subtle font-bold shadow-tactile"
          >
            Daftar Barang &amp; Stiker
          </router-link>
          <router-link
            v-if="authStore.canManage"
            to="/documents"
            class="px-3 py-1.5 rounded-md border-[1.5px] border-transparent hover:border-ink-primary transition-all duration-100"
            active-class="!border-ink-primary bg-paper-subtle font-bold shadow-tactile"
          >
            Berkas &amp; Dokumen
          </router-link>
        </template>
      </nav>

      <!-- User Info & Auth Action -->
      <div class="flex items-center gap-2">
        <template v-if="!authStore.isAuthenticated">
          <span class="hidden sm:inline-block text-[10px] font-mono px-2 py-1 bg-paper-subtle border border-paper-border rounded">
            WARGA &amp; JEMAAT
          </span>
          <button @click="isLoginOpen = true" class="btn-primary text-xs py-1.5 px-3">
            Masuk Pengurus &rarr;
          </button>
        </template>

        <template v-else>
          <!-- User Chip -->
          <div class="hidden sm:flex items-center gap-2 pl-2 pr-3 py-1 bg-paper-subtle border border-ink-primary rounded">
            <span class="w-2 h-2 rounded-full bg-status-good-ink"></span>
            <div class="text-left font-mono">
              <span class="block text-[11px] font-bold leading-tight">{{ authStore.user?.name }}</span>
              <span class="block text-[9px] text-ink-secondary">{{ authStore.userRoleLabel }}</span>
            </div>
          </div>

          <button @click="handleLogout" class="btn-secondary text-xs py-1.5 px-3">
            Keluar
          </button>
        </template>
      </div>
    </header>

    <!-- Main View Outlet -->
    <main class="flex-1 w-full mx-auto">
      <router-view />
    </main>

    <!-- Footer Archival Minimalist with Developer Watermark -->
    <footer class="border-t-[1.5px] border-ink-primary bg-paper-subtle text-xs text-ink-secondary py-5 px-4 text-center font-mono">
      <div class="max-w-4xl mx-auto space-y-2">
        <p class="font-bold text-ink-primary tracking-wide text-xs sm:text-sm">
          GREJA KRISTEN JAWI WETAN (GKJW) JEMAAT SUKUN &bull; MALANG
        </p>
        <p class="text-[11px] text-ink-secondary">
          Pengawasan Perbendaharaan Jemaat (PBJ) &bull; 24 Komisi / POKJA &bull; Standalone Web System v2.0
        </p>
        
        <!-- Elegant Developer Watermark (Task 6) -->
        <div class="pt-3 mt-3 border-t border-paper-border/80 text-[10px] sm:text-[11px] text-ink-secondary flex items-center justify-center gap-1.5 flex-wrap">
          <span class="inline-block w-1.5 h-1.5 rounded-full bg-church-terracotta"></span>
          <span>Designed &amp; Engineered with precision by</span>
          <strong class="text-ink-primary font-bold">Yosia Graceheo Boimau (Theology26)</strong>
          <span>&bull;</span>
          <span class="text-ink-muted">GKJW Jemaat Sukun Inventory v2.0</span>
        </div>
      </div>
    </footer>

    <!-- Global Login Modal -->
    <LoginModal
      :is-open="isLoginOpen"
      @close="isLoginOpen = false"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from './stores/auth'
import LoginModal from './components/auth/LoginModal.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const isLoginOpen = ref(false)

function isCurrentSection(sectionId) {
  if (route.path !== '/') return false
  if (sectionId === 'hero' && (!route.hash || route.hash === '#hero')) return true
  return route.hash === `#${sectionId}`
}

function navigateTo(sectionId) {
  if (route.path !== '/') {
    router.push({ path: '/', hash: `#${sectionId}` })
  } else {
    if (sectionId === 'hero') {
      window.scrollTo({ top: 0, behavior: 'smooth' })
      history.replaceState(null, null, ' ')
    } else {
      const el = document.getElementById(sectionId)
      if (el) {
        const headerOffset = 70
        const elementPosition = el.getBoundingClientRect().top
        const offsetPosition = elementPosition + window.pageYOffset - headerOffset
        window.scrollTo({
          top: offsetPosition,
          behavior: 'smooth'
        })
        history.replaceState(null, null, `#${sectionId}`)
      }
    }
  }
}

function handleLogout() {
  authStore.logout()
  router.push('/')
}
</script>
