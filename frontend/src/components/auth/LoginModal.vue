<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 bg-ink-primary/60 backdrop-blur-[2px] flex items-center justify-center p-4">
    <div
      class="max-w-md w-full bg-paper-surface p-6 sm:p-8 border-[2px] border-ink-primary rounded-md shadow-tactile-lg relative overflow-hidden animate-in fade-in zoom-in-95 duration-150"
    >
      <!-- Top Church Terracotta Line Accent -->
      <div class="absolute top-0 left-0 right-0 h-1.5 bg-church-terracotta"></div>

      <!-- Close Button -->
      <button
        @click="close"
        class="absolute top-4 right-4 w-7 h-7 rounded border border-ink-primary bg-paper-subtle hover:bg-paper-border flex items-center justify-center text-xs font-mono font-bold"
        title="Tutup (Esc)"
      >
        ✕
      </button>

      <!-- Header -->
      <div class="text-center mb-6">
        <div class="w-12 h-12 mx-auto rounded-md bg-paper-canvas flex items-center justify-center p-1.5 border-[1.5px] border-ink-primary shadow-tactile mb-3">
          <img src="/Logo Gkjw Hitam.png" alt="Logo GKJW" class="w-full h-full object-contain" />
        </div>
        <h2 class="text-lg font-extrabold uppercase tracking-tight">Masuk Akun Pengurus</h2>
        <p class="text-xs text-ink-secondary mt-1 font-medium">
          Untuk Majelis, Pengawas Perbendaharaan (PBJ), dan Pengurus 24 Komisi
        </p>
      </div>

      <!-- Error Alert Banner -->
      <div
        v-if="errorMessage"
        class="mb-4 p-3 rounded border-[1.5px] border-status-bad-ink bg-status-bad-bg text-status-bad-ink text-xs font-mono flex items-start gap-2"
      >
        <span class="font-bold">[!]</span>
        <span>{{ errorMessage }}</span>
      </div>

      <!-- Login Form -->
      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-xs font-bold uppercase text-ink-secondary mb-1">
            Nama Pengguna (Username)
          </label>
          <input
            v-model="username"
            type="text"
            placeholder="admin_sukun"
            class="input-tactile text-sm font-mono"
            autocomplete="username"
            required
          />
        </div>

        <div>
          <label class="block text-xs font-bold uppercase text-ink-secondary mb-1">
            Kata Sandi
          </label>
          <input
            v-model="password"
            type="password"
            placeholder="••••••••"
            class="input-tactile text-sm"
            autocomplete="current-password"
            required
          />
        </div>

        <div class="pt-2">
          <button
            type="submit"
            :disabled="isLoading"
            class="btn-primary w-full py-2.5 text-xs font-bold uppercase tracking-wider"
          >
            <span v-if="isLoading">Memeriksa kata sandi...</span>
            <span v-else>Masuk ke Sistem Inventaris &rarr;</span>
          </button>
        </div>
      </form>

      <div class="mt-4 pt-3 border-t border-paper-border text-center">
        <span class="text-[11px] font-mono text-ink-muted">
          Akun Contoh Pengurus: <code class="text-ink-primary font-bold">admin_sukun</code>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'login-success'])

const router = useRouter()
const authStore = useAuthStore()

const username = ref('admin_sukun')
const password = ref('')
const errorMessage = ref('')
const isLoading = ref(false)

function close() {
  errorMessage.value = ''
  emit('close')
}

async function handleLogin() {
  errorMessage.value = ''
  isLoading.value = true

  const result = await authStore.login(username.value, password.value)
  isLoading.value = false

  if (result.success) {
    emit('login-success')
    close()
    router.push('/dashboard')
  } else {
    errorMessage.value = result.error
  }
}

function handleKeydown(e) {
  if (e.key === 'Escape' && props.isOpen) {
    close()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

