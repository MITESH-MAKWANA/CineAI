import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { FiStar, FiHeart, FiBookmark, FiPlay, FiCalendar } from 'react-icons/fi'
import { getPosterUrl } from '../api/movies'

const GENRE_MAP = {
  28: 'Action', 12: 'Adventure', 16: 'Animation', 35: 'Comedy',
  80: 'Crime', 99: 'Documentary', 18: 'Drama', 10751: 'Family',
  14: 'Fantasy', 36: 'History', 27: 'Horror', 10402: 'Music',
  9648: 'Mystery', 10749: 'Romance', 878: 'Sci-Fi', 53: 'Thriller',
  10752: 'War', 37: 'Western'
}

export default function MovieCard({ movie, onWatchlist, onFavorite, inWatchlist, inFavorite, size = 'md' }) {
  const navigate = useNavigate()
  const [imgError, setImgError] = useState(false)
  const [hovered, setHovered] = useState(false)

  const posterUrl = !imgError ? getPosterUrl(movie.poster_path, 'w342') : null
  const rawRating = parseFloat(movie.vote_average)
  const rating = rawRating ? rawRating.toFixed(1) : null
  const year = movie.release_date?.split('-')[0] || movie.release_year || null

  // Genre: from genre_ids array or genres array
  const genres = (movie.genre_ids || [])
    .slice(0, 2)
    .map(id => GENRE_MAP[id])
    .filter(Boolean)

  // If genres array provided directly (from some API shapes)
  const genreNames = genres.length
    ? genres
    : (movie.genres || []).slice(0, 2).map(g => g.name || g).filter(Boolean)

  const ratingColor = rawRating >= 7.5 ? '#10b981' : rawRating >= 6 ? '#f5c518' : '#e50914'

  return (
    <div
      className={`mc mc-${size}${hovered ? ' mc-hovered' : ''}`}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      onClick={() => navigate(`/movie/${movie.id}`)}
    >
      {/* ── Poster ── */}
      <div className="mc-poster-wrap">
        {posterUrl ? (
          <img
            src={posterUrl}
            alt={movie.title}
            className="mc-poster-img"
            onError={() => setImgError(true)}
            loading="lazy"
          />
        ) : (
          <div className="mc-poster-placeholder">
            <span style={{ fontSize: '2.5rem' }}>🎬</span>
            <p>{movie.title}</p>
          </div>
        )}

        {/* Hover overlay */}
        <div className="mc-overlay">
          <button
            className="mc-play-btn"
            onClick={e => { e.stopPropagation(); navigate(`/movie/${movie.id}`) }}
            aria-label="View details"
          >
            <FiPlay size={22} fill="white" />
          </button>
          <div className="mc-action-btns">
            {onWatchlist && (
              <button
                className={`mc-action-btn${inWatchlist ? ' mc-btn-active-bm' : ''}`}
                onClick={e => { e.stopPropagation(); onWatchlist(movie) }}
                title={inWatchlist ? 'Remove from Watchlist' : 'Add to Watchlist'}
              >
                <FiBookmark size={15} fill={inWatchlist ? 'white' : 'none'} />
              </button>
            )}
            {onFavorite && (
              <button
                className={`mc-action-btn${inFavorite ? ' mc-btn-active-hrt' : ''}`}
                onClick={e => { e.stopPropagation(); onFavorite(movie) }}
                title={inFavorite ? 'Remove from Favorites' : 'Add to Favorites'}
              >
                <FiHeart size={15} fill={inFavorite ? 'white' : 'none'} />
              </button>
            )}
          </div>
        </div>

        {/* Rating badge — always visible */}
        {rating && (
          <div className="mc-rating-badge" style={{ borderColor: ratingColor + '55' }}>
            <FiStar size={10} fill={ratingColor} color={ratingColor} />
            <span style={{ color: ratingColor }}>{rating}</span>
          </div>
        )}
      </div>

      {/* ── Info Section (always visible) ── */}
      <div className="mc-info">
        {/* Title */}
        <h3 className="mc-title">{movie.title}</h3>

        {/* Rating bar + Year row */}
        <div className="mc-meta-row">
          {rating && (
            <div className="mc-star-row">
              <FiStar size={11} fill={ratingColor} color={ratingColor} />
              <span className="mc-rating-text" style={{ color: ratingColor }}>{rating}</span>
            </div>
          )}
          {year && (
            <div className="mc-year-row">
              <FiCalendar size={10} />
              <span>{year}</span>
            </div>
          )}
        </div>

        {/* Genre tags */}
        {genreNames.length > 0 && (
          <div className="mc-genres">
            {genreNames.map(g => (
              <span key={g} className="mc-genre-pill">{g}</span>
            ))}
          </div>
        )}
      </div>

      <style>{`
        .mc {
          position: relative;
          border-radius: var(--radius-md);
          overflow: hidden;
          background: var(--bg-card);
          border: 1px solid var(--border-subtle);
          transition: var(--transition);
          flex-shrink: 0;
          cursor: pointer;
          display: flex;
          flex-direction: column;
        }
        .mc-sm  { width: 140px; }
        .mc-md  { width: 185px; }
        .mc-lg  { width: 220px; }

        .mc-hovered {
          transform: scale(1.04) translateY(-5px);
          box-shadow: 0 20px 50px rgba(0,0,0,0.7), 0 0 20px rgba(229,9,20,0.15);
          border-color: rgba(229,9,20,0.3);
          z-index: 5;
        }

        /* ── Poster ── */
        .mc-poster-wrap {
          position: relative;
          aspect-ratio: 2/3;
          overflow: hidden;
          background: var(--bg-secondary);
          flex-shrink: 0;
        }
        .mc-poster-img {
          width: 100%; height: 100%;
          object-fit: cover;
          transition: transform 0.4s ease;
          display: block;
        }
        .mc-hovered .mc-poster-img { transform: scale(1.07); }
        .mc-poster-placeholder {
          width: 100%; height: 100%;
          display: flex; flex-direction: column;
          align-items: center; justify-content: center;
          gap: 8px; padding: 1rem;
          color: var(--text-muted);
          font-size: 0.7rem; text-align: center;
        }

        /* ── Overlay ── */
        .mc-overlay {
          position: absolute; inset: 0;
          background: linear-gradient(to top, rgba(5,5,10,0.92) 0%, transparent 55%);
          display: flex; flex-direction: column;
          align-items: center; justify-content: center;
          opacity: 0;
          transition: opacity 0.3s ease;
        }
        .mc-hovered .mc-overlay { opacity: 1; }
        .mc-play-btn {
          width: 52px; height: 52px;
          border-radius: 50%;
          background: rgba(229,9,20,0.9);
          border: 2px solid rgba(255,255,255,0.4);
          display: flex; align-items: center; justify-content: center;
          color: white;
          transition: var(--transition);
          margin-bottom: auto;
          margin-top: auto;
          backdrop-filter: blur(4px);
        }
        .mc-play-btn:hover { background: #e50914; transform: scale(1.12); }
        .mc-action-btns {
          display: flex; gap: 6px;
          padding: 0 8px 8px;
          align-self: flex-end;
        }
        .mc-action-btn {
          width: 30px; height: 30px;
          border-radius: 50%;
          background: rgba(255,255,255,0.15);
          backdrop-filter: blur(8px);
          border: 1px solid rgba(255,255,255,0.25);
          display: flex; align-items: center; justify-content: center;
          color: white;
          transition: var(--transition);
        }
        .mc-action-btn:hover { background: rgba(255,255,255,0.3); transform: scale(1.1); }
        .mc-btn-active-hrt { background: rgba(229,9,20,0.75) !important; }
        .mc-btn-active-bm  { background: rgba(79,195,247,0.65) !important; }

        /* ── Rating Badge (top right) ── */
        .mc-rating-badge {
          position: absolute; top: 7px; right: 7px;
          display: flex; align-items: center; gap: 3px;
          background: rgba(5,5,10,0.82);
          backdrop-filter: blur(6px);
          padding: 3px 7px;
          border-radius: var(--radius-full);
          font-size: 0.7rem;
          font-weight: 700;
          border: 1px solid;
        }

        /* ── Info Section ── */
        .mc-info {
          padding: 10px 10px 12px;
          display: flex;
          flex-direction: column;
          gap: 5px;
          flex: 1;
        }
        .mc-title {
          font-size: 0.82rem;
          font-weight: 700;
          color: var(--text-primary);
          line-height: 1.35;
          overflow: hidden;
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          margin: 0;
        }
        .mc-meta-row {
          display: flex;
          align-items: center;
          gap: 8px;
          flex-wrap: wrap;
        }
        .mc-star-row {
          display: flex; align-items: center; gap: 3px;
          font-size: 0.72rem; font-weight: 700;
        }
        .mc-rating-text { font-weight: 700; }
        .mc-year-row {
          display: flex; align-items: center; gap: 3px;
          font-size: 0.7rem;
          color: var(--text-muted);
        }
        .mc-genres {
          display: flex;
          flex-wrap: wrap;
          gap: 4px;
          margin-top: 2px;
        }
        .mc-genre-pill {
          font-size: 0.62rem;
          padding: 2px 7px;
          background: rgba(255,255,255,0.06);
          border: 1px solid rgba(255,255,255,0.12);
          border-radius: var(--radius-full);
          color: var(--text-secondary);
          font-weight: 500;
          letter-spacing: 0.02em;
          white-space: nowrap;
        }

        @media (max-width: 480px) {
          .mc-md { width: 150px; }
          .mc-sm { width: 125px; }
        }
      `}</style>
    </div>
  )
}
