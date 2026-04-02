import api from './axiosInstance'

export const getTrending = (page = 1) => api.get(`/movies/trending?page=${page}`)
export const getTopRated = (page = 1) => api.get(`/movies/top-rated?page=${page}`)
export const getPopular = (page = 1) => api.get(`/movies/popular?page=${page}`)
export const getUpcoming = (page = 1) => api.get(`/movies/upcoming?page=${page}`)
export const getByGenre = (genre, page = 1) => api.get(`/movies/by-genre?genre=${encodeURIComponent(genre)}&page=${page}`)
export const getMovieDetail = (id) => api.get(`/movies/${id}`)
export const getMovieVideos = (id) => api.get(`/movies/${id}/videos`)
export const searchMovies = (params) => api.get('/movies/search', { params })

// Recommendations
export const getSimilarMovies = (movieId, limit = 12) =>
  api.get(`/recommendations/for-movie/${movieId}?limit=${limit}`)
export const getPersonalized = (page = 1) =>
  api.get(`/recommendations/personalized?page=${page}`)
export const getAITrending = () => api.get('/recommendations/trending-ai')

// Watchlist
export const getWatchlist       = () => api.get('/watchlist/')
export const addToWatchlist     = (data) => api.post('/watchlist/add', data, { _skipSessionExpiry: true })
export const removeFromWatchlist= (movieId) => api.delete(`/watchlist/remove/${movieId}`, { _skipSessionExpiry: true })
export const checkWatchlist     = (movieId) => api.get(`/watchlist/check/${movieId}`)

// Favorites
export const getFavorites       = () => api.get('/favorites/')
export const addToFavorites     = (data) => api.post('/favorites/add', data, { _skipSessionExpiry: true })
export const removeFromFavorites= (movieId) => api.delete(`/favorites/remove/${movieId}`, { _skipSessionExpiry: true })
export const checkFavorite      = (movieId) => api.get(`/favorites/check/${movieId}`)

// Sentiment
export const analyzeText = (text) => api.post('/sentiment/analyze', { text })
export const submitReview = (data) => api.post('/sentiment/review', data)
export const getMovieReviews = (movieId) => api.get(`/sentiment/reviews/${movieId}`)

// Image helper
export const getPosterUrl = (path, size = 'w500') => {
  if (!path) return '/placeholder-poster.jpg'
  const base = import.meta.env.VITE_TMDB_IMAGE_BASE || 'https://image.tmdb.org/t/p'
  return `${base}/${size}${path}`
}

export const getBackdropUrl = (path, size = 'original') => {
  if (!path) return ''
  const base = import.meta.env.VITE_TMDB_IMAGE_BASE || 'https://image.tmdb.org/t/p'
  return `${base}/${size}${path}`
}
