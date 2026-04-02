import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('cineai_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// 401 handling rules:
//  • GET requests           → never auto-logout (silent background checks)
//  • _skipSessionExpiry     → caller opted out (e.g. sentiment save attempt)
//  • /auth/login            → let the login page show its own error
//  • Everything else (POST/PUT/DELETE with a real token) → clear stale session
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      const method           = (err.config?.method || 'get').toLowerCase()
      const isWrite          = ['post', 'put', 'delete', 'patch'].includes(method)
      const isLoginEndpoint  = err.config?.url?.includes('/auth/login')
      const skipExpiry       = !!err.config?._skipSessionExpiry
      const hadToken         = !!localStorage.getItem('cineai_token')

      if (isWrite && !isLoginEndpoint && !skipExpiry && hadToken) {
        localStorage.removeItem('cineai_token')
        localStorage.removeItem('cineai_user')
        window.dispatchEvent(new Event('cineai:session-expired'))
      }
    }
    return Promise.reject(err)
  }
)

export default api
