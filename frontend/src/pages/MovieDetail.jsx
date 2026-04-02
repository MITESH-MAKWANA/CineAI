import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { toast } from 'react-hot-toast'
import {
  FiStar, FiHeart, FiBookmark, FiArrowLeft, FiCalendar,
  FiGlobe, FiClock, FiPlay, FiMessageSquare, FiTrendingUp, FiX
} from 'react-icons/fi'
import api from '../api/axiosInstance'
import LoadingSpinner from '../components/LoadingSpinner'
import { useAuth } from '../context/AuthContext'

const IMG_W500 = 'https://image.tmdb.org/t/p/w500'
const IMG_W1280 = 'https://image.tmdb.org/t/p/w1280'
const getPoster   = (p) => p ? `${IMG_W500}${p.startsWith('/') ? '' : '/'}${p}` : null
const getBackdrop = (p) => p ? `${IMG_W1280}${p.startsWith('/') ? '' : '/'}${p}` : null

// Try to fetch a YouTube trailer via TMDB direct from browser
async function fetchTrailerKey(movieId, imdbId) {
  const TMDB_KEY = import.meta.env.VITE_TMDB_API_KEY || ''
  if (!TMDB_KEY) return null
  try {
    const res = await fetch(
      `https://api.themoviedb.org/3/movie/${movieId}/videos?api_key=${TMDB_KEY}`,
      { signal: AbortSignal.timeout(5000) }
    )
    if (!res.ok) return null
    const data = await res.json()
    const vids = data.results || []
    const trailer = vids.find(v => v.type === 'Trailer' && v.site === 'YouTube')
      || vids.find(v => v.site === 'YouTube')
    return trailer?.key || null
  } catch {
    return null
  }
}

const rc = (r) => parseFloat(r) >= 7.5 ? '#10b981' : parseFloat(r) >= 6 ? '#f5c518' : '#e50914'

export default function MovieDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { isAuthenticated } = useAuth()

  const [movie, setMovie]               = useState(null)
  const [trailerKey, setTrailerKey]     = useState(null)
  const [showTrailer, setShowTrailer]   = useState(false)
  const [loading, setLoading]           = useState(true)
  const [inWatchlist, setInWatchlist]   = useState(false)
  const [inFavorite, setInFavorite]     = useState(false)
  const [togglingWL, setTogglingWL]     = useState(false)
  const [togglingFav, setTogglingFav]   = useState(false)
  const [reviewText, setReviewText]     = useState('')
  const [reviewLoading, setReviewLoading] = useState(false)
  const [sentimentResult, setSentimentResult] = useState(null)
  const [submittedReview, setSubmittedReview] = useState('')
  const [movieReviews, setMovieReviews] = useState(null)
  const [similar, setSimilar]           = useState([])

  useEffect(() => {
    window.scrollTo(0, 0)
    loadMovie()
  // eslint-disable-next-line
  }, [id])

  const loadMovie = async () => {
    setLoading(true)
    setMovie(null); setTrailerKey(null); setSentimentResult(null)
    try {
      // Load from CSV backend
      const { data } = await api.get(`/csv/movies/${id}`)
      setMovie(data)

      // Try to get trailer from TMDB (browser-side, may fail on some networks)
      fetchTrailerKey(id).then(key => { if (key) setTrailerKey(key) })

      // Try to get similar movies from CSV
      const genres = data.genres || []
      if (genres.length > 0) {
        const simRes = await api.get(`/csv/movies/by-genre`, { params: { genre: genres[0], per_page: 20 } })
        setSimilar((simRes.data?.results || []).filter(m => m.id !== parseInt(id)).slice(0, 15))
      }

      // Check watchlist / favorites
      if (isAuthenticated) {
        try {
          const [wl, fav] = await Promise.all([
            api.get(`/watchlist/check/${id}`),
            api.get(`/favorites/check/${id}`)
          ])
          setInWatchlist(wl.data?.in_watchlist || false)
          setInFavorite(fav.data?.in_favorites || false)
        } catch { /* not critical */ }
      }

      // Load reviews
      try {
        const rev = await api.get(`/sentiment/reviews/${id}`)
        setMovieReviews(rev.data)
      } catch { /* ok */ }

    } catch (err) {
      toast.error('Movie not found')
      navigate(-1)
    } finally {
      setLoading(false)
    }
  }

  const handleWatchlist = async () => {
    if (!isAuthenticated) {
      toast.error('Please sign in to add to Watchlist')
      return navigate('/login')
    }
    setTogglingWL(true)
    try {
      if (inWatchlist) {
        await api.delete(`/watchlist/remove/${movie.id}`, { _skipSessionExpiry: true })
        setInWatchlist(false)
        toast.success('Removed from Watchlist')
      } else {
        await api.post('/watchlist/add', {
          movie_id:     movie.id,
          movie_title:  movie.title,
          poster_path:  movie.poster_path || '',
          vote_average: parseFloat(movie.vote_average) || 0,
          genre_ids:    []
        }, { _skipSessionExpiry: true })
        setInWatchlist(true)
        toast.success('Added to Watchlist 📌')
      }
    } catch (err) {
      const msg = err.response?.data?.detail || 'Something went wrong'
      if (err.response?.status === 401) {
        toast.error('Session expired — please sign in again')
      } else if (msg.toLowerCase().includes('already')) {
        setInWatchlist(true)
        toast('Already in your Watchlist', { icon: '📌' })
      } else {
        toast.error(msg)
      }
    } finally { setTogglingWL(false) }
  }

  const handleFavorite = async () => {
    if (!isAuthenticated) {
      toast.error('Please sign in to add to Favorites')
      return navigate('/login')
    }
    setTogglingFav(true)
    try {
      if (inFavorite) {
        await api.delete(`/favorites/remove/${movie.id}`, { _skipSessionExpiry: true })
        setInFavorite(false)
        toast.success('Removed from Favorites')
      } else {
        await api.post('/favorites/add', {
          movie_id:     movie.id,
          movie_title:  movie.title,
          poster_path:  movie.poster_path || '',
          vote_average: parseFloat(movie.vote_average) || 0,
          genre_ids:    []
        }, { _skipSessionExpiry: true })
        setInFavorite(true)
        toast.success('Added to Favorites ❤️')
      }
    } catch (err) {
      const msg = err.response?.data?.detail || 'Something went wrong'
      if (err.response?.status === 401) {
        toast.error('Session expired — please sign in again')
      } else if (msg.toLowerCase().includes('already')) {
        setInFavorite(true)
        toast('Already in your Favorites', { icon: '❤️' })
      } else {
        toast.error(msg)
      }
    } finally { setTogglingFav(false) }
  }

  const handleAnalyze = async () => {
    if (!reviewText.trim()) return toast.error('Please write a review first')
    const textToAnalyze = reviewText.trim()
    setReviewLoading(true)
    setSentimentResult(null)
    setSubmittedReview('')
    try {
      // Step 1: Always analyze first using the public endpoint — result shows immediately
      const { data } = await api.post('/sentiment/analyze', { text: textToAnalyze })
      const result = {
        sentiment:  data.sentiment  || 'neutral',
        score:      typeof data.score      === 'number' ? data.score      : 0.5,
        confidence: typeof data.confidence === 'number' ? data.confidence : 0.6,
      }
      setSentimentResult(result)
      setSubmittedReview(textToAnalyze)

      // Step 2: If logged in, silently try to persist the review
      // _skipSessionExpiry = true → a 401 here will NOT trigger auto-logout
      if (isAuthenticated) {
        try {
          await api.post(
            '/sentiment/review',
            { movie_id: movie.id, movie_title: movie.title, review_text: textToAnalyze },
            { _skipSessionExpiry: true }
          )
          toast.success(`Review saved! Sentiment: ${result.sentiment.toUpperCase()} 🎬`)
          setReviewText('')
          // Refresh community reviews list
          try {
            const rev = await api.get(`/sentiment/reviews/${id}`)
            setMovieReviews(rev.data)
          } catch { /* non-critical */ }
        } catch {
          // Save failed (expired session) but result is already shown — don't log out
          toast('Analysis complete! Sign in again to save your review.', { icon: '⚠️' })
          setReviewText('')
        }
      } else {
        toast('Sign in to save your review to the community', { icon: '💡' })
      }
    } catch (err) {
      console.error('Sentiment analysis error:', err)
      toast.error(err.response?.data?.detail || err.message || 'Analysis failed. Please try again.')
    } finally {
      setReviewLoading(false)
    }
  }


  if (loading) return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <LoadingSpinner size={50} text="Loading movie details..." />
    </div>
  )
  if (!movie) return null

  const backdrop = getBackdrop(movie.backdrop_path)
  const poster   = getPoster(movie.poster_path)
  const rating   = movie.vote_average ? parseFloat(movie.vote_average).toFixed(1) : 'N/A'
  const year     = movie.year || movie.release_date?.split('-')?.pop() || ''
  const genres   = movie.genres || []
  const runtime  = movie.runtime > 0 ? `${Math.floor(movie.runtime / 60)}h ${movie.runtime % 60}m` : null
  const country  = (movie.production_countries || [])[0] || ''
  const ratingColor = rc(rating)

  const sentimentColors = { positive: '#10b981', negative: '#e50914', neutral: '#f5c518' }
  const sentimentEmoji  = { positive: '😊', negative: '😞', neutral: '😐' }

  return (
    <div className="detail-page">

      {/* ── Hero / Backdrop ─────────────────────────────────────────────────── */}
      <div className="detail-hero" style={{ backgroundImage: backdrop ? `url(${backdrop})` : 'none' }}>
        <div className="detail-hero-overlay" />
        <div className="container detail-hero-content">
          <button className="back-btn" onClick={() => navigate(-1)}>
            <FiArrowLeft size={18} /> Back
          </button>

          <div className="detail-main">
            {/* Poster */}
            <div className="detail-poster-wrap">
              {poster
                ? <img src={poster} alt={movie.title} className="detail-poster" onError={e => { e.target.style.display='none' }} />
                : <div className="detail-no-poster">🎬</div>
              }
              {trailerKey && (
                <button className="detail-play-overlay" onClick={() => setShowTrailer(true)}>
                  <div className="detail-play-icon"><FiPlay size={24} fill="white" /></div>
                  <span>Watch Trailer</span>
                </button>
              )}
            </div>

            {/* Info panel */}
            <div className="detail-info">
              {/* Genre pills */}
              <div className="detail-genres">
                {genres.slice(0, 5).map(g => <span key={g} className="badge badge-red">{g}</span>)}
              </div>

              <h1 className="detail-title">{movie.title}</h1>
              {movie.tagline && <p className="detail-tagline">"{movie.tagline}"</p>}

              {/* Meta row */}
              <div className="detail-meta-row">
                <div className="detail-meta-item" style={{ color: ratingColor }}>
                  <FiStar size={16} fill={ratingColor} />
                  <span className="meta-value">{rating}</span>
                  <span className="meta-label">/10</span>
                </div>
                {year && (
                  <div className="detail-meta-item">
                    <FiCalendar size={15} /> <span>{year}</span>
                  </div>
                )}
                {runtime && (
                  <div className="detail-meta-item">
                    <FiClock size={15} /> <span>{runtime}</span>
                  </div>
                )}
                {country && (
                  <div className="detail-meta-item">
                    <FiGlobe size={15} /> <span>{country}</span>
                  </div>
                )}
              </div>

              {movie.vote_count > 0 && (
                <p className="vote-count">{movie.vote_count.toLocaleString()} ratings</p>
              )}

              {/* Overview */}
              {movie.overview && (
                <div className="detail-overview">
                  <h3 className="overview-label">Overview</h3>
                  <p className="overview-text">{movie.overview}</p>
                </div>
              )}

              {/* Action buttons */}
              <div className="detail-actions">
                {trailerKey && (
                  <button className="btn btn-primary btn-lg" onClick={() => setShowTrailer(true)} id="watch-trailer-btn">
                    <FiPlay size={18} fill="white" /> Watch Trailer
                  </button>
                )}
                <button
                  className={`detail-action-btn${inWatchlist ? ' active-watchlist' : ''}`}
                  onClick={handleWatchlist} disabled={togglingWL} id="add-watchlist-btn">
                  <FiBookmark size={20} fill={inWatchlist ? 'white' : 'none'} />
                  {togglingWL ? '...' : inWatchlist ? 'In Watchlist' : 'Add to Watchlist'}
                </button>
                <button
                  className={`detail-action-btn${inFavorite ? ' active-favorite' : ''}`}
                  onClick={handleFavorite} disabled={togglingFav} id="add-favorite-btn">
                  <FiHeart size={20} fill={inFavorite ? 'white' : 'none'} />
                  {togglingFav ? '...' : inFavorite ? 'Favorited' : 'Add to Favorites'}
                </button>
              </div>

              {/* ── Full Metadata Panel ─────────────────────────────── */}
              <div className="detail-meta-panel">
                <div className="dmp-grid">
                  {[
                    { label: 'Status',            value: movie.status },
                    { label: 'Release Date',       value: movie.release_date },
                    { label: 'Original Language',  value: movie.original_language?.toUpperCase() },
                    { label: 'Original Title',     value: movie.original_title && movie.original_title !== movie.title ? movie.original_title : null },
                    { label: 'Popularity',         value: movie.popularity ? `${parseFloat(movie.popularity).toFixed(1)} pts` : null },
                    { label: 'Budget',             value: movie.budget > 0 ? `$${(movie.budget/1e6).toFixed(1)}M` : null },
                    { label: 'Revenue',            value: movie.revenue > 0 ? `$${(movie.revenue/1e6).toFixed(1)}M` : null },
                    { label: 'Runtime',            value: runtime },
                  ].filter(r => r.value).map(({ label, value }) => (
                    <div key={label} className="dmp-item">
                      <div className="dmp-label">{label}</div>
                      <div className="dmp-value">{value}</div>
                    </div>
                  ))}
                </div>

                {(movie.production_companies || []).length > 0 && (
                  <div className="dmp-list-row">
                    <div className="dmp-list-label">🏢 Production Companies</div>
                    <div className="dmp-pills">
                      {movie.production_companies.slice(0, 6).map(c => <span key={c} className="dmp-pill dmp-pill-blue">{c}</span>)}
                    </div>
                  </div>
                )}

                {(movie.production_countries || []).length > 0 && (
                  <div className="dmp-list-row">
                    <div className="dmp-list-label">🌍 Production Countries</div>
                    <div className="dmp-pills">
                      {movie.production_countries.map(c => <span key={c} className="dmp-pill dmp-pill-green">{c}</span>)}
                    </div>
                  </div>
                )}

                {(movie.spoken_languages || []).length > 0 && (
                  <div className="dmp-list-row">
                    <div className="dmp-list-label">🗣️ Spoken Languages</div>
                    <div className="dmp-pills">
                      {movie.spoken_languages.map(l => <span key={l} className="dmp-pill dmp-pill-purple">{l}</span>)}
                    </div>
                  </div>
                )}

                {movie.keywords && (
                  <div className="dmp-list-row">
                    <div className="dmp-list-label">🏷️ Keywords</div>
                    <div className="dmp-pills">
                      {movie.keywords.split(',').slice(0, 12).map(k => k.trim()).filter(Boolean).map(k => (
                        <span key={k} className="dmp-pill dmp-pill-grey">{k}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ── Trailer Modal ──────────────────────────────────────────────────── */}
      {showTrailer && trailerKey && (
        <div className="trailer-modal" onClick={() => setShowTrailer(false)}>
          <div className="trailer-modal-inner" onClick={e => e.stopPropagation()}>
            <button className="trailer-close" onClick={() => setShowTrailer(false)}><FiX size={18} /></button>
            <div className="trailer-embed">
              <iframe
                src={`https://www.youtube.com/embed/${trailerKey}?autoplay=1`}
                title="Movie Trailer"
                allow="autoplay; encrypted-media"
                allowFullScreen
              />
            </div>
          </div>
        </div>
      )}

      {/* ── Body ──────────────────────────────────────────────────────────── */}
      <div className="container detail-body">

        {/* AI Review Section */}
        <section className="review-section card">
          <div className="review-section-header">
            <h2 className="section-title"><FiMessageSquare /> AI Sentiment Analysis</h2>
            {!isAuthenticated && (
              <p className="review-guest-note">
                <span>💡</span> <a href="/login" style={{ color:'var(--accent-secondary)', textDecoration:'underline' }}>Sign in</a> to save reviews to the community
              </p>
            )}
          </div>

          {/* Review input */}
          <textarea className="review-input"
            placeholder={isAuthenticated
              ? 'Write your review here — we\'ll analyze the sentiment and save it...'
              : 'Write a review to see AI sentiment analysis...'}
            value={reviewText} onChange={e => setReviewText(e.target.value)}
            rows={4} id="review-textarea" />

          <div className="review-btns">
            <button className="btn btn-primary btn-analyze" onClick={handleAnalyze}
              disabled={reviewLoading || !reviewText.trim()} id="analyze-sentiment-btn">
              <FiTrendingUp size={16} />
              {reviewLoading ? 'Analyzing...' : isAuthenticated ? 'Analyze & Save Review' : 'Analyze Sentiment'}
            </button>
          </div>

          {reviewLoading && <LoadingSpinner size={30} text="Analyzing sentiment..." />}

          {/* Result card — shows BELOW the button with the review text */}
          {sentimentResult && !reviewLoading && (
            <div className="sa-result-card" style={{ borderColor: sentimentColors[sentimentResult.sentiment] }}>
              <div className="sa-result-badge" style={{ background: `${sentimentColors[sentimentResult.sentiment]}18`, borderColor: sentimentColors[sentimentResult.sentiment] }}>
                <span className="sa-result-emoji">{sentimentEmoji[sentimentResult.sentiment]}</span>
                <div className="sa-result-meta">
                  <span className="sa-result-label" style={{ color: sentimentColors[sentimentResult.sentiment] }}>
                    {sentimentResult.sentiment?.toUpperCase()} SENTIMENT
                  </span>
                  <span className="sa-result-score">
                    Score: {(sentimentResult.score * 100).toFixed(0)}%
                    {sentimentResult.confidence ? ` · Confidence: ${(sentimentResult.confidence * 100).toFixed(0)}%` : ''}
                  </span>
                </div>
                {isAuthenticated && (
                  <span className="sa-saved-tag">✓ Saved</span>
                )}
              </div>
              {submittedReview && (
                <div className="sa-result-review">
                  <span className="sa-result-review-label">Your review:</span>
                  <p className="sa-result-review-text">"{submittedReview}"</p>
                </div>
              )}
            </div>
          )}

          {/* Community reviews list */}
          {movieReviews?.reviews?.length > 0 && (
            <div className="recent-reviews">
              <h3 className="review-sub-title">Community Reviews ({movieReviews.total})</h3>
              {movieReviews.reviews.slice(0, 5).map(r => (
                <div key={r.id} className="review-item">
                  <div className="review-item-header">
                    <span className={`review-badge review-${r.sentiment}`}>
                      {sentimentEmoji[r.sentiment]} {r.sentiment}
                    </span>
                    <span className="review-date">{r.created_at?.split('T')[0]}</span>
                  </div>
                  <p className="review-text-preview">{r.review_text.slice(0, 200)}{r.review_text.length > 200 ? '...' : ''}</p>
                </div>
              ))}
            </div>
          )}
        </section>



        {/* Similar Movies */}
        {similar.length > 0 && (
          <section className="similar-section">
            <h2 className="section-title" style={{ marginBottom: '1rem' }}>🎬 More Like This</h2>
            <div className="similar-grid">
              {similar.map(m => {
                const sp = getPoster(m.poster_path)
                const sr = m.vote_average ? parseFloat(m.vote_average).toFixed(1) : null
                return (
                  <div key={m.id} className="similar-card" onClick={() => { navigate(`/movie/${m.id}`); window.scrollTo(0,0) }}>
                    {sp
                      ? <img src={sp} alt={m.title} className="similar-poster" onError={e => e.target.style.display='none'} />
                      : <div className="similar-no-poster">🎬</div>
                    }
                    <div className="similar-info">
                      <p className="similar-title">{m.title}</p>
                      {sr && <p className="similar-rating" style={{ color: rc(sr) }}>★ {sr}</p>}
                    </div>
                  </div>
                )
              })}
            </div>
          </section>
        )}
      </div>

      <style>{`
        .detail-page { min-height: 100vh; }

        /* Hero */
        .detail-hero { position: relative; min-height: 80vh; background-size: cover; background-position: center; display: flex; align-items: flex-end; padding-bottom: 3rem; }
        .detail-hero-overlay { position: absolute; inset: 0; background: linear-gradient(to right, rgba(10,10,15,0.97) 40%, rgba(10,10,15,0.6) 100%), linear-gradient(to top, rgba(10,10,15,1) 0%, transparent 60%); }
        .detail-hero-content { position: relative; z-index: 2; padding-top: calc(var(--navbar-height) + 1.5rem); }
        .back-btn { display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px; background: rgba(255,255,255,0.08); border: 1px solid var(--border-medium); border-radius: var(--radius-md); color: var(--text-secondary); font-size: 0.875rem; cursor: pointer; transition: var(--transition); margin-bottom: 1.5rem; }
        .back-btn:hover { color: var(--text-primary); background: rgba(255,255,255,0.14); }

        .detail-main { display: flex; gap: 2.5rem; align-items: flex-start; }
        .detail-poster-wrap { flex-shrink: 0; width: 220px; border-radius: var(--radius-lg); overflow: hidden; box-shadow: 0 30px 60px rgba(0,0,0,0.7); position: relative; background: var(--bg-secondary); min-height: 320px; }
        .detail-poster { width: 100%; display: block; }
        .detail-no-poster { width: 100%; height: 320px; display: flex; align-items: center; justify-content: center; font-size: 3rem; }
        .detail-play-overlay { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; background: rgba(10,10,15,0.65); color: white; font-size: 0.85rem; font-weight: 600; opacity: 0; transition: opacity 0.3s; cursor: pointer; border: none; }
        .detail-poster-wrap:hover .detail-play-overlay { opacity: 1; }
        .detail-play-icon { width: 56px; height: 56px; border-radius: 50%; background: rgba(229,9,20,0.9); display: flex; align-items: center; justify-content: center; border: 2px solid rgba(255,255,255,0.3); }

        .detail-info { flex: 1; }
        .detail-genres { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 1rem; }
        .detail-title { font-size: clamp(1.75rem, 4vw, 3rem); font-weight: 900; margin-bottom: 0.4rem; line-height: 1.1; }
        .detail-tagline { color: var(--text-muted); font-style: italic; margin-bottom: 1rem; font-size: 0.95rem; }
        .detail-meta-row { display: flex; flex-wrap: wrap; gap: 16px; margin-bottom: 0.75rem; }
        .detail-meta-item { display: flex; align-items: center; gap: 6px; color: var(--text-secondary); font-size: 0.9rem; }
        .meta-value { font-size: 1.1rem; font-weight: 700; }
        .meta-label { font-size: 0.8rem; color: var(--text-muted); }
        .vote-count { color: var(--text-muted); font-size: 0.8rem; margin-bottom: 1.25rem; }
        .detail-overview { margin-bottom: 1.75rem; }
        .overview-label { font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-muted); margin-bottom: 0.5rem; }
        .overview-text { color: var(--text-secondary); line-height: 1.75; font-size: 0.95rem; }
        .detail-actions { display: flex; flex-wrap: wrap; gap: 10px; }
        .detail-action-btn { display: flex; align-items: center; gap: 8px; padding: 11px 20px; border-radius: var(--radius-md); background: rgba(255,255,255,0.08); border: 1px solid var(--border-medium); color: var(--text-secondary); font-size: 0.875rem; font-weight: 600; cursor: pointer; transition: var(--transition); }
        .detail-action-btn:hover { background: rgba(255,255,255,0.15); color: var(--text-primary); }
        .active-watchlist { background: rgba(79,195,247,0.2) !important; border-color: rgba(79,195,247,0.5) !important; color: #4fc3f7 !important; }
        .active-favorite { background: rgba(229,9,20,0.2) !important; border-color: rgba(229,9,20,0.4) !important; color: var(--accent-secondary) !important; }

        /* Metadata Panel */
        .detail-meta-panel { margin-top: 1.75rem; background: rgba(255,255,255,0.03); border: 1px solid var(--border-subtle); border-radius: var(--radius-lg); padding: 1.25rem; }
        .dmp-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px,1fr)); gap: 0.85rem; margin-bottom: 1.1rem; }
        .dmp-item { display: flex; flex-direction: column; gap: 3px; }
        .dmp-label { font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.07em; color: var(--text-muted); }
        .dmp-value { font-size: 0.875rem; font-weight: 600; color: var(--text-primary); }
        .dmp-list-row { margin-top: 0.85rem; padding-top: 0.85rem; border-top: 1px solid var(--border-subtle); }
        .dmp-list-label { font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); margin-bottom: 0.5rem; }
        .dmp-pills { display: flex; flex-wrap: wrap; gap: 5px; }
        .dmp-pill { padding: 3px 10px; border-radius: var(--radius-full); font-size: 0.72rem; font-weight: 600; white-space: nowrap; }
        .dmp-pill-blue   { background: rgba(79,195,247,0.12); color: #4fc3f7; }
        .dmp-pill-green  { background: rgba(16,185,129,0.12); color: #10b981; }
        .dmp-pill-purple { background: rgba(124,58,237,0.12); color: #a78bfa; }
        .dmp-pill-grey   { background: rgba(255,255,255,0.06); color: var(--text-muted); }

        /* Trailer Modal */
        .trailer-modal { position: fixed; inset: 0; z-index: 9999; background: rgba(0,0,0,0.92); display: flex; align-items: center; justify-content: center; padding: 1rem; animation: fadeIn 0.3s ease; }
        .trailer-modal-inner { position: relative; width: 100%; max-width: 900px; background: var(--bg-card); border-radius: var(--radius-xl); overflow: hidden; box-shadow: var(--shadow-lg); }
        .trailer-close { position: absolute; top: 10px; right: 10px; z-index: 10; width: 36px; height: 36px; border-radius: 50%; background: rgba(0,0,0,0.7); border: none; color: white; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: var(--transition); }
        .trailer-close:hover { background: var(--accent-primary); }
        .trailer-embed { position: relative; padding-bottom: 56.25%; height: 0; }
        .trailer-embed iframe { position: absolute; inset: 0; width: 100%; height: 100%; border: none; }

        /* Body */
        .detail-body { padding: 2.5rem 0 4rem; display: flex; flex-direction: column; gap: 2rem; }

        .review-section { padding: 1.75rem; border-radius: var(--radius-xl); }
        .review-section-header { display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px; margin-bottom: 1.25rem; }
        .review-guest-note { font-size: 0.8rem; color: var(--text-muted); display: flex; align-items: center; gap: 5px; margin: 0; }

        .review-input { width: 100%; background: var(--bg-secondary); border: 1px solid var(--border-medium); border-radius: var(--radius-md); padding: 14px; color: var(--text-primary); font-size: 0.9rem; resize: vertical; min-height: 110px; font-family: inherit; transition: var(--transition); margin-bottom: 1rem; box-sizing: border-box; }
        .review-input:focus { border-color: var(--accent-primary); outline: none; box-shadow: 0 0 0 3px rgba(229,9,20,0.12); }
        .review-input::placeholder { color: var(--text-muted); }
        .review-btns { display: flex; gap: 10px; margin-bottom: 1.25rem; flex-wrap: wrap; }
        .btn-analyze { gap: 8px; }

        /* Sentiment result card */
        .sa-result-card { border: 1px solid; border-radius: var(--radius-lg); overflow: hidden; margin-top: 0.5rem; animation: slideUp 0.35s ease; }
        @keyframes slideUp { from { opacity:0; transform: translateY(12px); } to { opacity:1; transform: translateY(0); } }
        .sa-result-badge { display: flex; align-items: center; gap: 14px; padding: 16px 20px; border-bottom: 1px solid rgba(255,255,255,0.06); }
        .sa-result-emoji { font-size: 2.2rem; flex-shrink: 0; }
        .sa-result-meta { flex: 1; display: flex; flex-direction: column; gap: 3px; }
        .sa-result-label { font-weight: 800; font-size: 1rem; letter-spacing: 0.03em; }
        .sa-result-score { font-size: 0.8rem; color: var(--text-muted); }
        .sa-saved-tag { font-size: 0.72rem; font-weight: 700; color: #10b981; background: rgba(16,185,129,0.12); border: 1px solid rgba(16,185,129,0.25); border-radius: var(--radius-full); padding: 3px 10px; flex-shrink: 0; }
        .sa-result-review { padding: 14px 20px; background: rgba(255,255,255,0.02); }
        .sa-result-review-label { font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); display: block; margin-bottom: 6px; }
        .sa-result-review-text { font-size: 0.9rem; color: var(--text-secondary); line-height: 1.6; font-style: italic; margin: 0; }

        .recent-reviews { margin-top: 1.75rem; padding-top: 1.25rem; border-top: 1px solid var(--border-subtle); }
        .review-sub-title { font-size: 0.9rem; font-weight: 700; margin-bottom: 0.875rem; color: var(--text-secondary); }
        .review-item { padding: 12px 14px; background: var(--bg-secondary); border-radius: var(--radius-md); margin-bottom: 8px; }
        .review-item-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
        .review-badge { padding: 2px 10px; border-radius: var(--radius-full); font-size: 0.72rem; font-weight: 700; text-transform: capitalize; }
        .review-positive { background: rgba(16,185,129,0.15); color: #10b981; }
        .review-negative { background: rgba(229,9,20,0.15); color: var(--accent-secondary); }
        .review-neutral { background: rgba(245,197,24,0.15); color: #f5c518; }
        .review-date { color: var(--text-muted); font-size: 0.72rem; }
        .review-text-preview { font-size: 0.85rem; color: var(--text-secondary); line-height: 1.5; margin: 0; }

        /* Similar */
        .similar-section { }
        .similar-grid { display: flex; gap: 12px; overflow-x: auto; padding-bottom: 1rem; scrollbar-width: none; }
        .similar-grid::-webkit-scrollbar { display: none; }
        .similar-card { flex-shrink: 0; width: 130px; cursor: pointer; transition: var(--transition); border-radius: var(--radius-md); overflow: hidden; background: var(--bg-card); }
        .similar-card:hover { transform: scale(1.05); }
        .similar-poster { width: 100%; aspect-ratio: 2/3; object-fit: cover; display: block; }
        .similar-no-poster { width: 100%; aspect-ratio: 2/3; background: var(--bg-secondary); display: flex; align-items: center; justify-content: center; font-size: 2rem; }
        .similar-info { padding: 6px 8px 8px; }
        .similar-title { font-size: 0.72rem; font-weight: 600; color: var(--text-primary); overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; margin: 0 0 3px; }
        .similar-rating { font-size: 0.68rem; font-weight: 700; margin: 0; }

        @media (max-width: 700px) {
          .detail-main { flex-direction: column; }
          .detail-poster-wrap { width: 160px; }
          .detail-hero { min-height: auto; padding-bottom: 2rem; }
        }
      `}</style>
    </div>
  )
}
