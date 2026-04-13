import api from './axiosInstance'

export const registerUser = (username, email, password) =>
  api.post('/auth/register', { username, email, password })

export const loginUser = (email, password) =>
  api.post('/auth/login', { email, password })

export const getMe = () => api.get('/auth/me')

export const updateGenres = (genres) =>
  api.put('/auth/genres', { genres })

// Tells the backend to set is_online=false before the token is cleared
export const logoutUser = () =>
  api.post('/auth/logout').catch(() => {}) // fire-and-forget — never block logout
