import { useRef } from 'react'
import { FiChevronLeft, FiChevronRight } from 'react-icons/fi'
import MovieCard from './MovieCard'

export default function MovieRow({ title, movies = [], loading, onWatchlist, onFavorite, watchlistIds = [], favoriteIds = [] }) {
  const scrollRef = useRef(null)

  const scroll = (dir) => {
    const el = scrollRef.current
    if (el) el.scrollBy({ left: dir * 600, behavior: 'smooth' })
  }

  return (
    <section className="movie-row">
      <div className="movie-row-header">
        <h2 className="section-title">{title}</h2>
        <div className="row-scroll-btns">
          <button className="row-scroll-btn" onClick={() => scroll(-1)} aria-label="Scroll left">
            <FiChevronLeft size={20} />
          </button>
          <button className="row-scroll-btn" onClick={() => scroll(1)} aria-label="Scroll right">
            <FiChevronRight size={20} />
          </button>
        </div>
      </div>

      <div className="movie-row-scroll" ref={scrollRef}>
        {loading
          ? Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="movie-card-skeleton">
                <div className="skeleton skeleton-poster" />
                <div className="skeleton skeleton-title" />
                <div className="skeleton skeleton-meta" />
              </div>
            ))
          : movies.map((movie) => (
              <MovieCard
                key={movie.id}
                movie={movie}
                onWatchlist={onWatchlist}
                onFavorite={onFavorite}
                inWatchlist={watchlistIds.includes(movie.id)}
                inFavorite={favoriteIds.includes(movie.id)}
              />
            ))
        }
      </div>

      <style>{`
        .movie-row { margin-bottom: 2.5rem; }
        .movie-row-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 1rem;
        }
        .row-scroll-btns { display: flex; gap: 6px; }
        .row-scroll-btn {
          width: 32px; height: 32px;
          border-radius: var(--radius-full);
          background: rgba(255,255,255,0.08);
          border: 1px solid var(--border-medium);
          color: var(--text-secondary);
          display: flex; align-items: center; justify-content: center;
          transition: var(--transition);
        }
        .row-scroll-btn:hover {
          background: var(--accent-primary);
          color: white;
          border-color: transparent;
        }
        .movie-row-scroll {
          display: flex;
          gap: 14px;
          overflow-x: auto;
          padding: 8px 4px 16px;
          scrollbar-width: none;
          -ms-overflow-style: none;
          scroll-snap-type: x mandatory;
        }
        .movie-row-scroll::-webkit-scrollbar { display: none; }
        .movie-row-scroll > * { scroll-snap-align: start; }

        /* Skeleton */
        .movie-card-skeleton { flex-shrink: 0; width: 185px; }
        .skeleton-poster {
          width: 100%;
          aspect-ratio: 2/3;
          border-radius: var(--radius-md);
          margin-bottom: 8px;
        }
        .skeleton-title {
          height: 14px;
          border-radius: 4px;
          margin-bottom: 6px;
          width: 80%;
        }
        .skeleton-meta {
          height: 10px;
          border-radius: 4px;
          width: 50%;
        }
      `}</style>
    </section>
  )
}
