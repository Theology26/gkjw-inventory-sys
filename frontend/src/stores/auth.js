import { defineStore } from 'pinia'
import api from '../api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    isLoading: false,
    error: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    isSuperAdmin: (state) => state.user?.role === 'SUPER_ADMIN',
    isPokjaAdmin: (state) => state.user?.role === 'POKJA_ADMIN',
    canManage: (state) => ['SUPER_ADMIN', 'POKJA_ADMIN'].includes(state.user?.role),
    userRoleLabel: (state) => {
      if (!state.user) return 'Tamu'
      if (state.user.role === 'SUPER_ADMIN') return 'Super Admin'
      if (state.user.role === 'POKJA_ADMIN') return 'Admin POKJA'
      return 'Viewer'
    }
  },

  actions: {
    async login(identifier, password) {
      this.isLoading = true
      this.error = null
      try {
        const response = await api.post('/auth/login', {
          identifier,
          username: identifier,
          email: identifier,
          password
        })
        const data = response.data

        this.token = data.access_token
        this.user = {
          id: data.user_id,
          username: data.username,
          name: data.name,
          email: data.email,
          role: data.role,
          pokja_id: data.pokja_id
        }

        localStorage.setItem('token', this.token)
        localStorage.setItem('user', JSON.stringify(this.user))
        return { success: true }
      } catch (err) {
        this.error = err.response?.data?.detail || 'Gagal masuk. Periksa kembali nama pengguna dan kata sandi.'
        return { success: false, error: this.error }
      } finally {
        this.isLoading = false
      }
    },

    async fetchProfile() {
      if (!this.token) return
      try {
        const response = await api.get('/auth/me')
        this.user = response.data
        localStorage.setItem('user', JSON.stringify(this.user))
      } catch (err) {
        this.logout()
      }
    },

    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  }
})

