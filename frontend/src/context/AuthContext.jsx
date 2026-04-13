import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { loginUser, registerUser, getMe, logoutUser as apiLogout } from '../api/auth'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('cineai_token'))
  const [loading, setLoading] = useState(true)

  const saveAuth = (tokenValue, userData) => {
    localStorage.setItem('cineai_token', tokenValue)
    localStorage.setItem('cineai_user', JSON.stringify(userData))
    setToken(tokenValue)
    setUser(userData)
  }

  const clearAuth = () => {
    localStorage.removeItem('cineai_token')
    localStorage.removeItem('cineai_user')
    setToken(null)
    setUser(null)
  }

  // Load user from token on mount
  useEffect(() => {
    const storedToken = localStorage.getItem('cineai_token')
    if (storedToken) {
      getMe()
        .then(({ data }) => {
          setUser(data)
          // Keep localStorage in sync with latest server data
          localStorage.setItem('cineai_user', JSON.stringify(data))
        })
        .catch((err) => {
          if (err.response?.status === 401) {
            // Token is definitively invalid — clear session
            clearAuth()
          } else {
            // Network error or backend down — restore from cache so user stays logged in
            const cached = localStorage.getItem('cineai_user')
            if (cached) {
              try { setUser(JSON.parse(cached)) }
              catch { clearAuth() }
            } else {
              clearAuth()
            }
          }
        })
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  // Listen for 401 session-expiry events from axiosInstance
  useEffect(() => {
    const handler = () => {
      // Best-effort: tell backend this session is gone
      apiLogout()
      setToken(null)
      setUser(null)
    }
    window.addEventListener('cineai:session-expired', handler)
    return () => window.removeEventListener('cineai:session-expired', handler)
  }, [])

  const login = useCallback(async (email, password) => {
    const { data } = await loginUser(email, password)
    saveAuth(data.access_token, data.user)
    return data
  }, [])

  const register = useCallback(async (username, email, password) => {
    const { data } = await registerUser(username, email, password)
    saveAuth(data.access_token, data.user)
    return data
  }, [])

  const logout = useCallback(() => {
    apiLogout() // fire-and-forget — sets is_online=false on server
    clearAuth()
  }, [])

  const updateUserGenres = useCallback((genres, skippedGenres) => {
    setUser(prev => {
      const updated = {
        ...prev,
        favorite_genres: Array.isArray(genres) ? genres.join(',') : (genres || ''),
        skipped_genres: Array.isArray(skippedGenres) ? skippedGenres.join(',') : (skippedGenres || prev?.skipped_genres || ''),
        onboarding_done: true,
      }
      localStorage.setItem('cineai_user', JSON.stringify(updated))
      return updated
    })
  }, [])

  const updateUser = useCallback((patch) => {
    setUser(prev => {
      const updated = { ...prev, ...patch }
      localStorage.setItem('cineai_user', JSON.stringify(updated))
      return updated
    })
  }, [])

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout, updateUserGenres, updateUser, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
