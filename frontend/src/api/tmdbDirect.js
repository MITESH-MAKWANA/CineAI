/**
 * tmdbDirect.js
 * Calls TMDB API directly from the browser (bypasses backend proxy).
 * Used because the backend server may not have external internet access.
 */
import axios from 'axios'

const TMDB_KEY = import.meta.env.VITE_TMDB_API_KEY || '15f372e27ab9be14aeed119bcce5657f'
const TMDB_BASE = import.meta.env.VITE_TMDB_BASE_URL || 'https://api.themoviedb.org/3'

const tmdb = axios.create({ baseURL: TMDB_BASE })

const get = (url, params = {}) =>
  tmdb.get(url, { params: { api_key: TMDB_KEY, ...params } })

// ── Core endpoints ────────────────────────────────────────────────────────────
export const tmdbTrending  = (page = 1) => get('/trending/movie/week', { page })
export const tmdbTopRated  = (page = 1) => get('/movie/top_rated', { page })
export const tmdbPopular   = (page = 1) => get('/movie/popular', { page })
export const tmdbUpcoming  = (page = 1) => get('/movie/upcoming', { page })
export const tmdbNowPlaying = (page = 1) => get('/movie/now_playing', { page })

// ── By genre ID ───────────────────────────────────────────────────────────────
export const tmdbByGenre = (genreId, page = 1) =>
  get('/discover/movie', { with_genres: genreId, sort_by: 'popularity.desc', page })

// ── Search ───────────────────────────────────────────────────────────────────
export const tmdbSearch = (query, page = 1) =>
  get('/search/movie', { query, page })

// ── Movie detail (with videos, credits, similar) ───────────────────────────
export const tmdbMovieDetail = (id) =>
  get(`/movie/${id}`, { append_to_response: 'videos,credits,similar,reviews' })

// ── Genre IDs map ─────────────────────────────────────────────────────────────
export const GENRE_IDS = {
  Action:           28,
  Adventure:        12,
  Animation:        16,
  Comedy:           35,
  Crime:            80,
  Documentary:      99,
  Drama:            18,
  Family:           10751,
  Fantasy:          14,
  History:          36,
  Horror:           27,
  Music:            10402,
  Mystery:          9648,
  Romance:          10749,
  'Science Fiction':878,
  Thriller:         53,
  War:              10752,
  Western:          37,
}

// ── Image helpers ─────────────────────────────────────────────────────────────
const IMG_BASE = import.meta.env.VITE_TMDB_IMAGE_BASE || 'https://image.tmdb.org/t/p'
export const posterUrl   = (path, size = 'w342') => path ? `${IMG_BASE}/${size}${path}` : null
export const backdropUrl = (path, size = 'w1280') => path ? `${IMG_BASE}/${size}${path}` : null
