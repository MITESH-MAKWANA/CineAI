import { useState, useEffect, useCallback } from 'react'
import { useNavigate, useLocation, useSearchParams } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { FiSearch, FiX, FiStar, FiCalendar, FiFilter, FiChevronLeft, FiChevronRight, FiChevronDown } from 'react-icons/fi'
import api from '../api/axiosInstance'

const IMG = 'https://image.tmdb.org/t/p/w342'
const getPoster = (path) => path ? `${IMG}${path.startsWith('/') ? '' : '/'}${path}` : null

const GENRE_MAP_INV = {
  28:'Action', 12:'Adventure', 16:'Animation', 35:'Comedy', 80:'Crime',
  18:'Drama', 10751:'Family', 14:'Fantasy', 27:'Horror', 9648:'Mystery',
  10749:'Romance', 878:'Sci-Fi', 53:'Thriller', 10752:'War', 37:'Western'
}

const rColor = (r) => parseFloat(r) >= 7.5 ? '#10b981' : parseFloat(r) >= 6 ? '#f5c518' : '#e50914'

// ── Movie Card ────────────────────────────────────────────────────────────────
function MovieCard({ movie, onClick }) {
  const [err, setErr] = useState(false)
  const [hov, setHov] = useState(false)
  const poster = !err ? getPoster(movie.poster_path) : null
  const rating = movie.vote_average ? parseFloat(movie.vote_average).toFixed(1) : null
  // Support both genres array (CSV) and genre_ids (TMDB)
  const genres = movie.genres?.length
    ? movie.genres.slice(0, 2)
    : (movie.genre_ids || []).slice(0, 2).map(id => GENRE_MAP_INV[id]).filter(Boolean)
  const year = movie.year || movie.release_date?.split('-')?.[0] || movie.release_date?.split('-')?.[2] || ''
  const rc = rating ? rColor(rating) : '#888'

  return (
    <div className={`ec-card${hov ? ' ec-hov' : ''}`}
      onMouseEnter={() => setHov(true)} onMouseLeave={() => setHov(false)}
      onClick={() => onClick(movie.id)}>
      <div className="ec-poster-wrap">
        {poster
          ? <img src={poster} alt={movie.title} className="ec-poster" onError={() => setErr(true)} loading="lazy" />
          : <div className="ec-no-poster">🎬</div>
        }
        <div className="ec-overlay"><div className="ec-play">▶</div></div>
        {rating && (
          <div className="ec-rating-badge" style={{ color: rc, borderColor: rc + '55' }}>
            ★ {rating}
          </div>
        )}
      </div>
      <div className="ec-info">
        <h3 className="ec-title">{movie.title}</h3>
        <div className="ec-meta">
          {rating && <span className="ec-stars" style={{ color: rc }}>★ {rating}</span>}
          {year && <span className="ec-year">📅 {year}</span>}
        </div>
        {genres.length > 0 && (
          <div className="ec-genres">
            {genres.map(g => <span key={g} className="ec-genre-pill">{g}</span>)}
          </div>
        )}
      </div>
    </div>
  )
}

// ── Movie Row ─────────────────────────────────────────────────────────────────
function MovieRow({ title, movies, onMovie }) {
  if (!movies?.length) return null
  const scroll = (dir) => {
    const el = document.getElementById(`row-${title.replace(/[^a-z]/gi, '')}`)
    if (el) el.scrollBy({ left: dir * 700, behavior: 'smooth' })
  }
  return (
    <section className="ec-row">
      <div className="ec-row-header">
        <h2 className="ec-row-title">{title}</h2>
        <div className="ec-row-btns">
          <button className="ec-scroll-btn" onClick={() => scroll(-1)}><FiChevronLeft size={18} /></button>
          <button className="ec-scroll-btn" onClick={() => scroll(1)}><FiChevronRight size={18} /></button>
        </div>
      </div>
      <div className="ec-row-scroll" id={`row-${title.replace(/[^a-z]/gi, '')}`}>
        {movies.map(m => <MovieCard key={m.id} movie={m} onClick={onMovie} />)}
      </div>
    </section>
  )
}

// ── Helpers ────────────────────────────────────────────────────────────────────
const csvGet = (path, params = {}) => api.get(`/csv${path}`, { params })

// ── Explore Page ──────────────────────────────────────────────────────────────
export default function Explore() {
  const navigate      = useNavigate()
  const location      = useLocation()
  const [searchParams] = useSearchParams()
  const { user }      = useAuth()

  // Preferred genres passed from Profile "Start Exploring" button
  const stateGenres = location.state?.genres || user?.favorite_genres || ''
  const preferredGenres = stateGenres.split(',').map(g => g.trim()).filter(Boolean)

  // Search & filter state — initialised from URL so browser back restores them
  const [query, setQuery]             = useState(searchParams.get('q')      || '')
  const [filterGenre, setFilterGenre] = useState(searchParams.get('genre')  || '')
  const [filterYear, setFilterYear]   = useState(searchParams.get('year')   || '')
  const [minRating, setMinRating]     = useState(searchParams.get('rating') || '')
  const [filtersOpen, setFiltersOpen] = useState(false)

  // Data state
  const [rows, setRows]               = useState({})
  const [userRows, setUserRows]       = useState([])  // personalized genre rows
  const [searchResults, setSearchResults] = useState(null)
  const [searching, setSearching]     = useState(false)
  const [allGenres, setAllGenres]     = useState([])
  const [allYears, setAllYears]       = useState([])
  const [loading, setLoading]         = useState(true)

  // ── Load genres, years, all rows ──────────────────────────────────────────
  useEffect(() => {
    Promise.allSettled([
      csvGet('/movies/genres'),
      csvGet('/movies/years'),
      csvGet('/movies/trending?per_page=20'),
      csvGet('/movies/top-rated?per_page=20'),
      csvGet('/movies/by-genre?genre=Action&per_page=20'),
      csvGet('/movies/by-genre?genre=Comedy&per_page=20'),
      csvGet('/movies/by-genre?genre=Drama&per_page=20'),
      csvGet('/movies/by-genre?genre=Horror&per_page=20'),
      csvGet('/movies/by-genre?genre=Thriller&per_page=20'),
      csvGet('/movies/by-genre?genre=Romance&per_page=20'),
      csvGet('/movies/by-genre?genre=Science+Fiction&per_page=20'),
      csvGet('/movies/by-genre?genre=Animation&per_page=20'),
      csvGet('/movies/by-genre?genre=Fantasy&per_page=20'),
      csvGet('/movies/by-genre?genre=Crime&per_page=20'),
      csvGet('/movies/by-genre?genre=Family&per_page=20'),
      csvGet('/movies/by-genre?genre=Adventure&per_page=20'),
    ]).then(([genres, years, trending, topRated, action, comedy, drama, horror,
      thriller, romance, scifi, animation, fantasy, crime, family, adventure]) => {
      if (genres.status === 'fulfilled') setAllGenres(genres.value?.data || [])
      if (years.status === 'fulfilled') setAllYears(years.value?.data || [])
      const get = r => r.status === 'fulfilled' ? (r.value?.data?.results || []) : []
      setRows({
        trending: get(trending), topRated: get(topRated),
        action: get(action), comedy: get(comedy), drama: get(drama),
        horror: get(horror), thriller: get(thriller), romance: get(romance),
        scifi: get(scifi), animation: get(animation), fantasy: get(fantasy),
        crime: get(crime), family: get(family), adventure: get(adventure)
      })
      setLoading(false)
    })
  }, [])

  // ── Load personalized genre rows (runs when user has preferred genres) ─────
  useEffect(() => {
    if (!preferredGenres.length) return
    Promise.allSettled(
      preferredGenres.slice(0, 5).map(g =>
        csvGet(`/movies/by-genre?genre=${encodeURIComponent(g)}&per_page=20`)
      )
    ).then(results => {
      const built = results
        .map((r, i) => ({
          genre: preferredGenres[i],
          movies: r.status === 'fulfilled' ? (r.value?.data?.results || []) : []
        }))
        .filter(r => r.movies.length > 0)
      setUserRows(built)
    })
  }, [stateGenres])

  // ── React to URL search param changes (browser Back button) ──────────────
  useEffect(() => {
    const q      = searchParams.get('q')      || ''
    const genre  = searchParams.get('genre')  || ''
    const year   = searchParams.get('year')   || ''
    const rating = searchParams.get('rating') || ''

    // Sync input fields with URL
    setQuery(q)
    setFilterGenre(genre)
    setFilterYear(year)
    setMinRating(rating)

    if (!q && !genre && !year && !rating) {
      // No search params — back to normal rows
      setSearchResults(null)
      return
    }

    // Re-run the search (triggered by back-button URL change too)
    setSearching(true)
    setSearchResults(null)
    const apiParams = { per_page: 1000 }
    if (q)      apiParams.query    = q
    if (genre)  apiParams.genre    = genre
    if (year)   { apiParams.year_from = parseInt(year); apiParams.year_to = parseInt(year) }
    if (rating) apiParams.min_rating = parseFloat(rating)
    csvGet('/movies/search', apiParams)
      .then(({ data }) => setSearchResults(data.results || []))
      .catch(() => setSearchResults([]))
      .finally(() => setSearching(false))
  }, [searchParams])

  // ── Search ──────────────────────────────────────────────────────────────
  const handleSearch = async (e) => {
    e?.preventDefault()
    if (!query.trim() && !filterGenre && !filterYear && !minRating) return
    // Push search state into URL history — back button will clear it and stay on Explore
    const p = new URLSearchParams()
    if (query.trim()) p.set('q', query.trim())
    if (filterGenre)  p.set('genre', filterGenre)
    if (filterYear)   p.set('year', filterYear)
    if (minRating)    p.set('rating', minRating)
    navigate(`/explore?${p.toString()}`)
    // Actual search is triggered by the searchParams useEffect above
  }

  const clearSearch = () => {
    setFiltersOpen(false)
    navigate('/explore', { replace: true })  // clear URL params, stay on Explore
  }

  const goToMovie = (id) => navigate(`/movie/${id}`)

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div className="ec-page page-wrapper">
      <div className="container">

        <div className="ec-header">
          <h1 className="ec-page-title">🎬 Explore Movies</h1>
          <p className="ec-page-sub">Discover from 13,150 movies in our catalogue</p>
        </div>

        {/* Search bar */}
        <form onSubmit={handleSearch} className="ec-search-form">
          <div className="ec-search-bar">
            <FiSearch className="ec-search-icon" size={18} />
            <input type="text" className="ec-search-input"
              placeholder="Search movies by title, genre, overview..."
              value={query} onChange={e => setQuery(e.target.value)}
              id="explore-search-input" />
            {(query || filterGenre || filterYear || minRating) && (
              <button type="button" className="ec-clear-btn" onClick={clearSearch}><FiX size={15} /></button>
            )}
          </div>
          <button type="submit" className="btn btn-primary" id="explore-search-btn">Search</button>
          <button type="button"
            className={`btn btn-secondary${filtersOpen ? ' ec-filter-active' : ''}`}
            onClick={() => setFiltersOpen(v => !v)}>
            <FiFilter size={14} /> Filters
            <FiChevronDown size={13} style={{ transform: filtersOpen ? 'rotate(180deg)' : 'none', transition: '0.2s' }} />
          </button>
        </form>

        {/* Active filter chips */}
        {(filterGenre || filterYear || minRating) && (
          <div className="ec-active-filters">
            {filterGenre && <span className="ec-active-chip">{filterGenre} <button onClick={() => setFilterGenre('')}>×</button></span>}
            {filterYear && <span className="ec-active-chip">Year: {filterYear} <button onClick={() => setFilterYear('')}>×</button></span>}
            {minRating && <span className="ec-active-chip">Rating ≥ {minRating} <button onClick={() => setMinRating('')}>×</button></span>}
          </div>
        )}

        {/* Filter panel */}
        {filtersOpen && (
          <div className="ec-filter-panel">
            <div className="ec-filter-row">
              <div className="ec-filter-field">
                <label className="ec-filter-label">Genre</label>
                <select className="filter-select" value={filterGenre} onChange={e => setFilterGenre(e.target.value)}>
                  <option value="">All Genres</option>
                  {allGenres.map(g => <option key={g} value={g}>{g}</option>)}
                </select>
              </div>
              <div className="ec-filter-field">
                <label className="ec-filter-label">Year</label>
                <select className="filter-select" value={filterYear} onChange={e => setFilterYear(e.target.value)}>
                  <option value="">Any Year</option>
                  {allYears.slice(0, 50).map(y => <option key={y} value={y}>{y}</option>)}
                </select>
              </div>
              <div className="ec-filter-field">
                <label className="ec-filter-label">Min Rating</label>
                <select className="filter-select" value={minRating} onChange={e => setMinRating(e.target.value)}>
                  <option value="">Any Rating</option>
                  {['9', '8', '7.5', '7', '6.5', '6', '5'].map(r => (
                    <option key={r} value={r}>★ {r}+</option>
                  ))}
                </select>
              </div>
            </div>
            <div style={{ display: 'flex', gap: 10, marginTop: 14 }}>
              <button className="btn btn-primary btn-sm" onClick={handleSearch}>Apply Filters</button>
              <button className="btn btn-ghost btn-sm" onClick={clearSearch}>Clear All</button>
            </div>
          </div>
        )}

        {/* Search Results */}
        {searchResults !== null && (
          <div className="ec-search-results">
            {searching ? (
              <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🔍</div>
                Searching...
              </div>
            ) : (
              <>
                <div className="ec-results-header">
                  <h2>{searchResults.length} Result{searchResults.length !== 1 ? 's' : ''}
                    {query ? ` for "${query}"` : ''}
                    {filterGenre ? ` in ${filterGenre}` : ''}
                  </h2>
                  <button className="btn btn-ghost btn-sm" onClick={clearSearch}><FiX size={13} /> Clear</button>
                </div>
                {searchResults.length === 0
                  ? <p className="ec-no-results">No movies found. Try different terms or fewer filters.</p>
                  : <div className="ec-grid">{searchResults.map(m => <MovieCard key={m.id} movie={m} onClick={goToMovie} />)}</div>
                }
              </>
            )}
          </div>
        )}

        {/* Movie Rows */}
        {searchResults === null && (
          loading ? (
            <div style={{ padding: '4rem 0', textAlign: 'center', color: 'var(--text-muted)' }}>
              <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>🎬</div>
              Loading movies...
            </div>
          ) : (
            <>
              {/* ✨ Personalized section — shown when user has preferred genres */}
              {userRows.length > 0 && (
                <div className="ec-personalized">
                  <div className="ec-personalized-header">
                    <span className="ec-personalized-badge">✨ Picked For You</span>
                    <span className="ec-personalized-sub">
                      Based on your preferred genres: {preferredGenres.slice(0,5).join(' · ')}
                    </span>
                  </div>
                  {userRows.map(({ genre, movies }) => (
                    <MovieRow
                      key={genre}
                      title={`🎯 ${genre}`}
                      movies={movies}
                      onMovie={goToMovie}
                    />
                  ))}
                  <div className="ec-personalized-divider" />
                </div>
              )}

              <MovieRow title="🔥 Trending & Popular"    movies={rows.trending}   onMovie={goToMovie} />
              <MovieRow title="⭐ Top Rated"              movies={rows.topRated}   onMovie={goToMovie} />
              <MovieRow title="💥 Action & Adventure"    movies={rows.action}     onMovie={goToMovie} />
              <MovieRow title="🎭 Drama"                 movies={rows.drama}      onMovie={goToMovie} />
              <MovieRow title="😂 Comedy"                movies={rows.comedy}     onMovie={goToMovie} />
              <MovieRow title="😱 Horror"                movies={rows.horror}     onMovie={goToMovie} />
              <MovieRow title="🕵️ Thriller"              movies={rows.thriller}   onMovie={goToMovie} />
              <MovieRow title="❤️ Romance"               movies={rows.romance}    onMovie={goToMovie} />
              <MovieRow title="🚀 Science Fiction"       movies={rows.scifi}      onMovie={goToMovie} />
              <MovieRow title="🎨 Animation"             movies={rows.animation}  onMovie={goToMovie} />
              <MovieRow title="🧙 Fantasy"               movies={rows.fantasy}    onMovie={goToMovie} />
              <MovieRow title="🔍 Crime & Mystery"       movies={rows.crime}      onMovie={goToMovie} />
              <MovieRow title="👨‍👩‍👧 Family"               movies={rows.family}     onMovie={goToMovie} />
              <MovieRow title="🌍 Adventure"             movies={rows.adventure}  onMovie={goToMovie} />
            </>
          )
        )}

      </div>

      <style>{`
        .ec-page { padding-top: calc(var(--navbar-height, 64px) + 1.5rem); padding-bottom: 5rem; }
        .ec-header { padding: 2rem 0 1.5rem; }
        .ec-page-title { font-size: clamp(1.75rem,4vw,2.5rem); font-weight: 900; margin-bottom: 0.25rem; }
        .ec-page-sub { color: var(--text-muted); font-size: 0.9rem; }

        /* Search */
        .ec-search-form { display: flex; gap: 10px; margin-bottom: 0.75rem; flex-wrap: wrap; }
        .ec-search-bar { position: relative; flex: 1; min-width: 220px; }
        .ec-search-icon { position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: var(--text-muted); pointer-events: none; }
        .ec-search-input { width: 100%; background: var(--bg-card); border: 1px solid var(--border-medium); border-radius: var(--radius-lg); padding: 12px 40px 12px 44px; color: var(--text-primary); font-size: 0.95rem; transition: var(--transition); box-sizing: border-box; }
        .ec-search-input:focus { border-color: var(--accent-primary); outline: none; }
        .ec-clear-btn { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); background: none; border: none; color: var(--text-muted); cursor: pointer; padding: 4px; }
        .ec-filter-active { border-color: var(--accent-primary) !important; color: var(--accent-secondary) !important; }

        /* Active filter chips */
        .ec-active-filters { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 0.75rem; }
        .ec-active-chip { display: inline-flex; align-items: center; gap: 5px; padding: 3px 10px 3px 12px; background: rgba(229,9,20,0.12); border: 1px solid rgba(229,9,20,0.3); border-radius: var(--radius-full); font-size: 0.76rem; color: var(--accent-secondary); font-weight: 600; }
        .ec-active-chip button { background: none; border: none; color: var(--accent-secondary); cursor: pointer; font-size: 1rem; line-height: 1; padding: 0; }

        /* Filter Panel */
        .ec-filter-panel { background: var(--bg-card); border: 1px solid var(--border-medium); border-radius: var(--radius-lg); padding: 1.25rem; margin-bottom: 1.5rem; animation: fadeIn 0.2s ease; }
        .ec-filter-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px,1fr)); gap: 1rem; }
        .ec-filter-field {}
        .ec-filter-label { display: block; font-size: 0.72rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px; }
        .filter-select { width: 100%; background: var(--bg-secondary); border: 1px solid var(--border-medium); border-radius: var(--radius-md); padding: 9px 12px; color: var(--text-primary); font-size: 0.875rem; cursor: pointer; }
        .filter-select:focus { border-color: var(--accent-primary); outline: none; }

        /* Search results */
        .ec-search-results { padding: 0.5rem 0 2rem; }
        .ec-results-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem; }
        .ec-results-header h2 { font-size: 1.05rem; font-weight: 700; }
        .ec-no-results { text-align: center; color: var(--text-muted); padding: 3rem 0; }
        .ec-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(155px,1fr)); gap: 1rem; }

        /* Movie Row */
        .ec-row { margin-bottom: 2.75rem; }
        .ec-row-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; }
        .ec-row-title { font-size: 1.1rem; font-weight: 800; }
        .ec-row-btns { display: flex; gap: 6px; }
        .ec-scroll-btn { width: 32px; height: 32px; border-radius: 50%; background: rgba(255,255,255,0.07); border: 1px solid var(--border-medium); color: var(--text-secondary); display: flex; align-items: center; justify-content: center; transition: var(--transition); cursor: pointer; }
        .ec-scroll-btn:hover { background: var(--accent-primary); color: white; border-color: transparent; }
        .ec-row-scroll { display: flex; gap: 14px; overflow-x: auto; padding: 6px 2px 18px; scrollbar-width: none; }
        .ec-row-scroll::-webkit-scrollbar { display: none; }

        /* Movie Card */
        .ec-card { flex-shrink: 0; width: 170px; border-radius: var(--radius-md); overflow: hidden; background: var(--bg-card); border: 1px solid var(--border-subtle); transition: var(--transition); cursor: pointer; display: flex; flex-direction: column; }
        .ec-card.ec-hov { transform: scale(1.04) translateY(-5px); box-shadow: 0 20px 45px rgba(0,0,0,0.7), 0 0 20px rgba(229,9,20,0.12); border-color: rgba(229,9,20,0.3); }
        .ec-poster-wrap { position: relative; aspect-ratio: 2/3; overflow: hidden; background: var(--bg-secondary); flex-shrink: 0; }
        .ec-poster { width: 100%; height: 100%; object-fit: cover; display: block; transition: transform 0.4s ease; }
        .ec-card.ec-hov .ec-poster { transform: scale(1.06); }
        .ec-no-poster { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 2.5rem; color: var(--text-muted); }
        .ec-overlay { position: absolute; inset: 0; background: linear-gradient(to top, rgba(5,5,12,0.88) 0%, transparent 55%); opacity: 0; transition: opacity 0.3s; display: flex; align-items: center; justify-content: center; }
        .ec-card.ec-hov .ec-overlay { opacity: 1; }
        .ec-play { width: 48px; height: 48px; border-radius: 50%; background: rgba(229,9,20,0.9); border: 2px solid rgba(255,255,255,0.3); display: flex; align-items: center; justify-content: center; color: white; font-size: 1.1rem; margin-top: -20px; }
        .ec-rating-badge { position: absolute; top: 7px; right: 7px; background: rgba(5,5,12,0.85); backdrop-filter: blur(6px); padding: 2px 8px; border-radius: var(--radius-full); font-size: 0.68rem; font-weight: 700; border: 1px solid; }
        .ec-info { padding: 10px 10px 12px; display: flex; flex-direction: column; gap: 5px; flex: 1; }
        .ec-title { font-size: 0.82rem; font-weight: 700; color: var(--text-primary); line-height: 1.3; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; margin: 0; }
        .ec-meta { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
        .ec-stars { font-size: 0.72rem; font-weight: 700; }
        .ec-year { font-size: 0.68rem; color: var(--text-muted); }
        .ec-genres { display: flex; flex-wrap: wrap; gap: 4px; }
        .ec-genre-pill { font-size: 0.6rem; padding: 2px 7px; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1); border-radius: var(--radius-full); color: var(--text-secondary); font-weight: 500; white-space: nowrap; }

        /* Personalized section */
        .ec-personalized { margin-bottom: 1rem; }
        .ec-personalized-header { display: flex; align-items: center; gap: 1rem; flex-wrap: wrap; padding: 1rem 1.25rem; background: linear-gradient(135deg, rgba(124,58,237,0.1), rgba(229,9,20,0.08)); border: 1px solid rgba(124,58,237,0.25); border-radius: var(--radius-lg); margin-bottom: 1.5rem; }
        .ec-personalized-badge { display: inline-flex; align-items: center; gap: 6px; padding: 5px 14px; background: linear-gradient(135deg, #7c3aed, #e50914); border-radius: var(--radius-full); color: white; font-size: 0.8rem; font-weight: 800; letter-spacing: 0.03em; white-space: nowrap; }
        .ec-personalized-sub { color: var(--text-muted); font-size: 0.8rem; }
        .ec-personalized-divider { height: 1px; background: var(--border-subtle); margin: 0.5rem 0 2rem; }

        @media (max-width: 600px) {
          .ec-search-form { flex-direction: column; }
          .ec-card { width: 148px; }
          .ec-grid { grid-template-columns: repeat(auto-fill, minmax(140px,1fr)); }
          .ec-filter-row { grid-template-columns: 1fr 1fr; }
        }
      `}</style>
    </div>
  )
}
