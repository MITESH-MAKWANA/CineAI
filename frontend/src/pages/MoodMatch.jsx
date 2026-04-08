import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { FiZap, FiArrowRight, FiRefreshCw, FiFilm, FiSliders } from 'react-icons/fi'
import api from '../api/axiosInstance'

export const VIBES = [
  { id: 'happy',       emoji: '😄', label: 'Happy',      color: '#f5c518', desc: 'Joyful & Upbeat' },
  { id: 'excited',     emoji: '🤩', label: 'Excited',    color: '#f97316', desc: 'Thrilled & Pumped' },
  { id: 'romantic',    emoji: '🥰', label: 'Romantic',   color: '#ec4899', desc: 'Warm & Loving' },
  { id: 'melancholy',  emoji: '😢', label: 'Melancholy', color: '#4fc3f7', desc: 'Reflective & Sad' },
  { id: 'dark',        emoji: '🖤', label: 'Dark',       color: '#8b5cf6', desc: 'Intense & Gritty' },
  { id: 'adventurous', emoji: '🌍', label: 'Adventure',  color: '#10b981', desc: 'Bold & Daring' },
  { id: 'scared',      emoji: '😱', label: 'Thrilled',   color: '#e50914', desc: 'Edge-of-Seat' },
  { id: 'curious',     emoji: '🤔', label: 'Curious',    color: '#a78bfa', desc: 'Thoughtful & Deep' },
  { id: 'nostalgic',   emoji: '🕰️', label: 'Nostalgic',  color: '#fbbf24', desc: 'Sentimental & Retro' },
  { id: 'inspired',    emoji: '✨', label: 'Inspired',   color: '#34d399', desc: 'Motivated & Uplifted' },
]

export const VIBE_TO_GENRES = {
  happy:       ['Comedy', 'Animation', 'Family'],
  excited:     ['Action', 'Adventure', 'Science Fiction'],
  romantic:    ['Romance', 'Drama'],
  melancholy:  ['Drama', 'Music'],
  dark:        ['Crime', 'Mystery', 'Thriller'],
  adventurous: ['Adventure', 'Action', 'Western'],
  scared:      ['Horror', 'Thriller'],
  curious:     ['Documentary', 'Mystery', 'Science Fiction'],
  nostalgic:   ['History', 'Drama', 'War'],
  inspired:    ['Documentary', 'Drama', 'Music'],
}

const ALL_GENRES = [
  'Action','Adventure','Animation','Comedy','Crime','Documentary',
  'Drama','Family','Fantasy','History','Horror','Music',
  'Mystery','Romance','Science Fiction','Thriller','War','Western',
]

const getPoster = (path) => {
  if (!path) return null
  if (path.startsWith('http')) return path
  return `https://image.tmdb.org/t/p/w300${path.startsWith('/') ? '' : '/'}${path}`
}

// ─── Shared movie fetching logic ──────────────────────────────────────
export async function fetchMoodMovies(currentVibe, targetVibe, selectedGenres = [], limit = 1000) {
  const vibeGenres1 = VIBE_TO_GENRES[currentVibe]  || []
  const vibeGenres2 = VIBE_TO_GENRES[targetVibe]   || []
  const merged      = [...new Set([...vibeGenres1, ...vibeGenres2])]

  // If user selected specific genres, use those; otherwise use vibe-mapped genres
  const genresToUse = selectedGenres.length > 0 ? selectedGenres : merged
  const results = []

  for (const genre of genresToUse.slice(0, 6)) {
    try {
      const { data } = await api.get('/csv/movies/by-genre', { params: { genre, page: 1, per_page: 500 } })
      const list = data?.results || data?.movies || (Array.isArray(data) ? data : [])
      results.push(...list)
    } catch { /* skip */ }
  }

  // Deduplicate by id, sort by popularity
  const seen = new Set()
  const unique = results.filter(m => { if (seen.has(m.id)) return false; seen.add(m.id); return true })
  unique.sort((a, b) => (b.popularity || 0) - (a.popularity || 0))
  return unique.slice(0, limit)
}

// ─── Main Page ────────────────────────────────────────────────────────
export default function MoodMatch() {
  const navigate  = useNavigate()
  const canvasRef = useRef(null)

  const [currentVibe, setCurrentVibe]     = useState(null)
  const [targetVibe, setTargetVibe]       = useState(null)
  const [selectedGenres, setSelectedGenres] = useState([])
  const [step, setStep]                   = useState(1) // 1=current 2=target 3=genres 4=results
  const [movies, setMovies]               = useState([])
  const [loading, setLoading]             = useState(false)

  /* ── Animated wave canvas ──────────────────────────────────────── */
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    let raf = null, t = 0

    const draw = () => {
      canvas.width  = canvas.offsetWidth
      canvas.height = canvas.offsetHeight
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      const { width: w, height: h } = canvas
      const midY = h / 2
      const c1 = VIBES.find(v => v.id === currentVibe)?.color || '#333'
      const c2 = VIBES.find(v => v.id === targetVibe)?.color  || '#333'
      ;[
        { amp:18, freq:0.022, phase:0,   alpha:0.8 },
        { amp:12, freq:0.028, phase:1.2, alpha:0.55 },
        { amp: 8, freq:0.018, phase:2.3, alpha:0.35 },
      ].forEach(({ amp, freq, phase, alpha }, idx) => {
        const grad = ctx.createLinearGradient(0, 0, w, 0)
        grad.addColorStop(0,   c1); grad.addColorStop(0.5, '#ffffff20'); grad.addColorStop(1, c2)
        ctx.beginPath(); ctx.moveTo(0, midY)
        for (let x = 0; x <= w; x++) {
          ctx.lineTo(x, midY + Math.sin(x * freq + t + phase) * amp * Math.sin((x / w) * Math.PI))
        }
        ctx.strokeStyle = grad; ctx.lineWidth = 2.5 - idx * 0.7
        ctx.globalAlpha = alpha; ctx.stroke(); ctx.globalAlpha = 1
      })
      t += 0.04
      raf = requestAnimationFrame(draw)
    }
    draw()
    return () => cancelAnimationFrame(raf)
  }, [currentVibe, targetVibe])

  /* ── Toggle genre filter ───────────────────────────────────────── */
  const toggleGenre = (g) => setSelectedGenres(prev =>
    prev.includes(g) ? prev.filter(x => x !== g) : [...prev, g]
  )

  /* ── Find movies ───────────────────────────────────────────────── */
  const findMovies = async () => {
    setLoading(true)
    setStep(4)
    try {
      const results = await fetchMoodMovies(currentVibe, targetVibe, selectedGenres, 1000)
      setMovies(results)
    } catch { setMovies([]) }
    finally { setLoading(false) }
  }

  const reset = () => {
    setCurrentVibe(null); setTargetVibe(null); setSelectedGenres([])
    setMovies([]); setStep(1)
  }

  const currentVibeObj = VIBES.find(v => v.id === currentVibe)
  const targetVibeObj  = VIBES.find(v => v.id === targetVibe)

  return (
    <div className="mm-page">

      {/* ── Header ───────────────────────────────────────────────── */}
      <div className="mm-hero">
        <div className="mm-badge"><FiZap size={13} /> Vibe Cinema Engine</div>
        <h1 className="mm-h1">Find movies that <span className="mm-gradient-text">shift your mood</span></h1>
        <p className="mm-sub">
          Tell us how you feel now and how you want to feel. We'll bridge the emotional gap with the perfect movie.
        </p>
      </div>

      {/* ── Wave canvas ──────────────────────────────────────────── */}
      <div className="mm-wave-container">
        <canvas ref={canvasRef} className="mm-canvas" />
        <div className="mm-wave-labels">
          <span className="mm-wave-tag" style={{ color: currentVibeObj?.color || 'var(--text-muted)' }}>
            {currentVibeObj ? `${currentVibeObj.emoji} ${currentVibeObj.label}` : 'How you feel now'}
          </span>
          <span className="mm-wave-center">→ EMOTIONAL JOURNEY →</span>
          <span className="mm-wave-tag" style={{ color: targetVibeObj?.color || 'var(--text-muted)' }}>
            {targetVibeObj ? `${targetVibeObj.emoji} ${targetVibeObj.label}` : 'How you want to feel'}
          </span>
        </div>
      </div>

      {/* ── Step progress ────────────────────────────────────────── */}
      {step < 4 && (
        <div className="mm-progress">
          {['Current Mood','Target Mood','Genre Filter'].map((label, i) => (
            <div key={i} className={`mm-prog-item ${step === i+1 ? 'active' : step > i+1 ? 'done' : ''}`}>
              <div className="mm-prog-dot">{step > i+1 ? '✓' : i+1}</div>
              <span className="mm-prog-label">{label}</span>
            </div>
          ))}
        </div>
      )}

      {/* ── Steps ────────────────────────────────────────────────── */}
      {step < 4 && (
        <div className="mm-steps-container">

          {/* Step 1 — Current Vibe */}
          <div className={`mm-panel${step === 1 ? ' mm-panel-active' : ''}`}>
            <div className="mm-panel-header">
              <div className="mm-step-num" style={{
                background: step > 1 ? 'rgba(16,185,129,0.15)' : 'rgba(229,9,20,0.15)',
                color: step > 1 ? '#10b981' : '#e50914'
              }}>{step > 1 ? '✓' : '1'}</div>
              <div>
                <div className="mm-panel-title">How do you feel right now?</div>
                <div className="mm-panel-sub">Pick the vibe that matches your current mood</div>
              </div>
              {currentVibeObj && (
                <span className="mm-selected-chip" style={{ background:`${currentVibeObj.color}20`, color:currentVibeObj.color }}>
                  {currentVibeObj.emoji} {currentVibeObj.label}
                </span>
              )}
            </div>
            {step === 1 && (
              <div className="mm-vibe-grid">
                {VIBES.map(v => (
                  <button key={v.id}
                    className={`mm-vibe-btn${currentVibe === v.id ? ' mm-vibe-selected' : ''}`}
                    style={currentVibe === v.id ? { borderColor:v.color, background:`${v.color}18` } : {}}
                    onClick={() => { setCurrentVibe(v.id); setStep(2) }}>
                    <span className="mm-vibe-emoji">{v.emoji}</span>
                    <span className="mm-vibe-label">{v.label}</span>
                    <span className="mm-vibe-desc">{v.desc}</span>
                    {currentVibe === v.id && <div className="mm-vibe-dot" style={{ background:v.color }} />}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Step 2 — Target Vibe */}
          <div className={`mm-panel${step === 2 ? ' mm-panel-active' : ''}`}>
            <div className="mm-panel-header">
              <div className="mm-step-num" style={{
                background: step > 2 ? 'rgba(16,185,129,0.15)' : step === 2 ? 'rgba(229,9,20,0.15)' : 'rgba(255,255,255,0.05)',
                color: step > 2 ? '#10b981' : step === 2 ? '#e50914' : 'var(--text-muted)'
              }}>{step > 2 ? '✓' : '2'}</div>
              <div>
                <div className="mm-panel-title">How do you want to feel?</div>
                <div className="mm-panel-sub">Choose your emotional destination</div>
              </div>
              {targetVibeObj && (
                <span className="mm-selected-chip" style={{ background:`${targetVibeObj.color}20`, color:targetVibeObj.color }}>
                  {targetVibeObj.emoji} {targetVibeObj.label}
                </span>
              )}
            </div>
            {step === 2 && (
              <>
                <div className="mm-vibe-grid">
                  {VIBES.filter(v => v.id !== currentVibe).map(v => (
                    <button key={v.id}
                      className={`mm-vibe-btn${targetVibe === v.id ? ' mm-vibe-selected' : ''}`}
                      style={targetVibe === v.id ? { borderColor:v.color, background:`${v.color}18` } : {}}
                      onClick={() => setTargetVibe(v.id)}>
                      <span className="mm-vibe-emoji">{v.emoji}</span>
                      <span className="mm-vibe-label">{v.label}</span>
                      <span className="mm-vibe-desc">{v.desc}</span>
                      {targetVibe === v.id && <div className="mm-vibe-dot" style={{ background:v.color }} />}
                    </button>
                  ))}
                </div>
                <div className="mm-cta-row">
                  <button className="btn btn-ghost mm-back-btn" onClick={() => { setStep(1); setTargetVibe(null) }}>← Back</button>
                  <button className="btn mm-find-btn" disabled={!targetVibe} onClick={() => setStep(3)}>
                    Next: Genre Filter <FiArrowRight size={16} />
                  </button>
                </div>
              </>
            )}
          </div>

          {/* Step 3 — Genre Filter (Optional) */}
          <div className={`mm-panel${step === 3 ? ' mm-panel-active' : ''}`}>
            <div className="mm-panel-header">
              <div className="mm-step-num" style={{
                background: step === 3 ? 'rgba(249,115,22,0.15)' : 'rgba(255,255,255,0.05)',
                color: step === 3 ? '#f97316' : 'var(--text-muted)'
              }}>3</div>
              <div>
                <div className="mm-panel-title">
                  <FiSliders size={14} style={{ marginRight:6, verticalAlign:'middle' }} />
                  Filter by Genre
                  <span className="mm-optional-tag">optional</span>
                </div>
                <div className="mm-panel-sub">Narrow results to specific genres, or skip for a broader match</div>
              </div>
              {selectedGenres.length > 0 && (
                <span className="mm-selected-chip" style={{ background:'rgba(249,115,22,0.15)', color:'#f97316' }}>
                  {selectedGenres.length} genre{selectedGenres.length > 1 ? 's' : ''} selected
                </span>
              )}
            </div>
            {step === 3 && (
              <>
                <div className="mm-genre-grid">
                  {ALL_GENRES.map(g => {
                    const isSelected = selectedGenres.includes(g)
                    return (
                      <button key={g}
                        className={`mm-genre-btn${isSelected ? ' mm-genre-selected' : ''}`}
                        onClick={() => toggleGenre(g)}>
                        {isSelected && <span className="mm-genre-check">✓</span>}
                        {g}
                      </button>
                    )
                  })}
                </div>
                {selectedGenres.length > 0 && (
                  <div className="mm-genre-selected-pills">
                    <span className="mm-genre-clear-label">Selected:</span>
                    {selectedGenres.map(g => (
                      <span key={g} className="mm-genre-pill" onClick={() => toggleGenre(g)}>
                        {g} ✕
                      </span>
                    ))}
                    <button className="mm-clear-genres" onClick={() => setSelectedGenres([])}>Clear all</button>
                  </div>
                )}
                <div className="mm-cta-row">
                  <button className="btn btn-ghost mm-back-btn" onClick={() => setStep(2)}>← Back</button>
                  <div className="mm-cta-right">
                    <button className="btn btn-ghost mm-skip-btn" onClick={findMovies}>
                      Skip & Find Movies
                    </button>
                    <button className="btn mm-find-btn" onClick={findMovies}>
                      <FiFilm size={18} /> Find My Movies <FiArrowRight size={16} />
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* ── Results ──────────────────────────────────────────────── */}
      {step === 4 && (
        <div className="mm-results">
          <div className="mm-results-header">
            <div>
              <h2 className="mm-results-title">
                <span style={{ color:currentVibeObj?.color }}>{currentVibeObj?.emoji} {currentVibeObj?.label}</span>
                &nbsp;→&nbsp;
                <span style={{ color:targetVibeObj?.color }}>{targetVibeObj?.emoji} {targetVibeObj?.label}</span>
              </h2>
              <p className="mm-results-sub">
                {selectedGenres.length > 0
                  ? `Filtered by: ${selectedGenres.join(', ')}`
                  : 'Showing best mood-matched picks'}
              </p>
            </div>
            <button className="btn btn-ghost mm-reset-btn" onClick={reset}>
              <FiRefreshCw size={15} /> Try Again
            </button>
          </div>

          {loading ? (
            <div className="mm-loading">
              <div className="mm-loading-dots"><span /><span /><span /></div>
              <p>Finding your perfect mood match...</p>
            </div>
          ) : movies.length === 0 ? (
            <div className="mm-empty">
              <div style={{ fontSize:'3rem', marginBottom:'1rem' }}>🎬</div>
              <p>No movies found for this combination. Try different genres or vibes!</p>
              <button className="btn btn-primary" style={{ marginTop:'1rem' }} onClick={reset}>Start Over</button>
            </div>
          ) : (
            <div className="mm-movies-grid">
              {movies.map((m, i) => {
                const poster = getPoster(m.poster_path)
                const rating = m.vote_average ? parseFloat(m.vote_average).toFixed(1) : null
                return (
                  <div key={m.id || i} className="mm-movie-card" onClick={() => navigate(`/movie/${m.id}`)}>
                    <div className="mm-poster-wrap">
                      {poster
                        ? <img src={poster} alt={m.title} className="mm-poster" onError={e => e.target.style.display='none'} />
                        : <div className="mm-no-poster">🎬</div>}
                      <div className="mm-card-overlay">
                        <span className="mm-card-cta">View Details →</span>
                      </div>
                    </div>
                    <div className="mm-card-info">
                      <p className="mm-card-title">{m.title}</p>
                      {rating && <p className="mm-card-rating">★ {rating}</p>}
                      {m.genres?.length > 0 && (
                        <p className="mm-card-genre">{m.genres.slice(0,2).join(' · ')}</p>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      )}

      <style>{`
        .mm-page {
          min-height: 100vh;
          padding: calc(var(--navbar-height) + 2rem) 1.5rem 5rem;
          max-width: 1100px; margin: 0 auto;
        }

        .mm-hero { text-align: center; margin-bottom: 1.75rem; }
        .mm-badge { display: inline-flex; align-items: center; gap: 6px; background: rgba(229,9,20,0.12); border: 1px solid rgba(229,9,20,0.25); color: var(--accent-secondary); font-size: 0.72rem; font-weight: 700; padding: 5px 14px; border-radius: var(--radius-full); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 1.25rem; }
        .mm-h1 { font-size: clamp(1.75rem, 4.5vw, 2.8rem); font-weight: 900; margin-bottom: 0.85rem; line-height: 1.15; }
        .mm-gradient-text { background: linear-gradient(135deg, #e50914, #f97316, #7c3aed); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
        .mm-sub { color: var(--text-secondary); font-size: 1rem; max-width: 560px; margin: 0 auto; line-height: 1.65; }

        .mm-wave-container { background: var(--bg-card); border: 1px solid var(--border-medium); border-radius: var(--radius-xl); padding: 1.25rem 2rem 0.75rem; margin-bottom: 1.5rem; }
        .mm-canvas { width: 100%; height: 80px; display: block; }
        .mm-wave-labels { display: flex; justify-content: space-between; align-items: center; font-size: 0.82rem; font-weight: 700; padding-top: 0.25rem; }
        .mm-wave-tag { transition: color 0.35s; }
        .mm-wave-center { color: var(--text-muted); font-size: 0.68rem; letter-spacing: 0.07em; text-transform: uppercase; }

        /* Progress */
        .mm-progress { display: flex; align-items: center; gap: 0; margin-bottom: 1.5rem; justify-content: center; }
        .mm-prog-item { display: flex; align-items: center; gap: 8px; }
        .mm-prog-item:not(:last-child)::after { content: '—'; margin: 0 12px; color: var(--border-medium); font-size: 0.8rem; }
        .mm-prog-dot { width: 28px; height: 28px; border-radius: 50%; border: 2px solid var(--border-medium); display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: 700; color: var(--text-muted); background: var(--bg-card); transition: all 0.3s; }
        .mm-prog-label { font-size: 0.78rem; font-weight: 600; color: var(--text-muted); transition: color 0.3s; }
        .mm-prog-item.active .mm-prog-dot { border-color: #e50914; color: #e50914; background: rgba(229,9,20,0.1); }
        .mm-prog-item.active .mm-prog-label { color: var(--text-primary); }
        .mm-prog-item.done .mm-prog-dot { border-color: #10b981; color: #10b981; background: rgba(16,185,129,0.1); }
        .mm-prog-item.done .mm-prog-label { color: #10b981; }

        .mm-steps-container { display: flex; flex-direction: column; gap: 1rem; }
        .mm-panel { background: var(--bg-card); border: 1px solid var(--border-medium); border-radius: var(--radius-xl); overflow: hidden; transition: border-color 0.3s; }
        .mm-panel-active { border-color: rgba(229,9,20,0.3); }
        .mm-panel-header { display: flex; align-items: center; gap: 1rem; padding: 1.25rem 1.5rem; flex-wrap: wrap; }
        .mm-step-num { width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.85rem; flex-shrink: 0; transition: all 0.3s; }
        .mm-panel-title { font-weight: 800; font-size: 0.95rem; margin-bottom: 2px; }
        .mm-panel-sub { font-size: 0.78rem; color: var(--text-muted); }
        .mm-optional-tag { font-size: 0.65rem; font-weight: 700; background: rgba(249,115,22,0.15); color: #f97316; border-radius: var(--radius-full); padding: 2px 8px; margin-left: 8px; text-transform: uppercase; letter-spacing: 0.05em; vertical-align: middle; }
        .mm-selected-chip { margin-left: auto; padding: 4px 12px; border-radius: var(--radius-full); font-size: 0.8rem; font-weight: 700; }

        .mm-vibe-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 8px; padding: 0 1.5rem 1.5rem; }
        .mm-vibe-btn { display: flex; flex-direction: column; align-items: center; gap: 4px; padding: 14px 10px; border: 1.5px solid var(--border-medium); border-radius: var(--radius-lg); background: var(--bg-secondary); cursor: pointer; transition: all 0.2s; position: relative; }
        .mm-vibe-btn:hover { border-color: var(--text-muted); transform: translateY(-2px); background: rgba(255,255,255,0.05); }
        .mm-vibe-selected { transform: translateY(-3px) !important; box-shadow: 0 8px 24px rgba(0,0,0,0.3); }
        .mm-vibe-emoji { font-size: 1.6rem; line-height: 1; }
        .mm-vibe-label { font-size: 0.8rem; font-weight: 700; color: var(--text-primary); }
        .mm-vibe-desc  { font-size: 0.66rem; color: var(--text-muted); text-align: center; line-height: 1.3; }
        .mm-vibe-dot { position: absolute; top: 8px; right: 8px; width: 7px; height: 7px; border-radius: 50%; }

        /* Genre filter */
        .mm-genre-grid { display: flex; flex-wrap: wrap; gap: 8px; padding: 0 1.5rem 1rem; }
        .mm-genre-btn { padding: 7px 16px; border: 1.5px solid var(--border-medium); border-radius: var(--radius-full); background: var(--bg-secondary); color: var(--text-secondary); font-size: 0.82rem; font-weight: 600; cursor: pointer; transition: all 0.2s; position: relative; }
        .mm-genre-btn:hover { border-color: #f97316; color: #f97316; background: rgba(249,115,22,0.08); }
        .mm-genre-selected { border-color: #f97316 !important; background: rgba(249,115,22,0.15) !important; color: #f97316 !important; }
        .mm-genre-check { margin-right: 5px; font-size: 0.75rem; }
        .mm-genre-selected-pills { display: flex; align-items: center; flex-wrap: wrap; gap: 6px; padding: 0 1.5rem 1rem; }
        .mm-genre-clear-label { font-size: 0.72rem; color: var(--text-muted); font-weight: 600; }
        .mm-genre-pill { background: rgba(249,115,22,0.15); color: #f97316; font-size: 0.72rem; font-weight: 700; padding: 3px 10px; border-radius: var(--radius-full); cursor: pointer; transition: background 0.2s; }
        .mm-genre-pill:hover { background: rgba(229,9,20,0.2); }
        .mm-clear-genres { font-size: 0.72rem; color: var(--text-muted); cursor: pointer; background: none; border: none; text-decoration: underline; }

        /* CTA row */
        .mm-cta-row { display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 0.5rem 1.5rem 1.25rem; flex-wrap: wrap; }
        .mm-cta-right { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
        .mm-back-btn { color: var(--text-muted); font-size: 0.875rem; }
        .mm-skip-btn { color: var(--text-secondary); font-size: 0.875rem; text-decoration: underline; }
        .mm-find-btn { background: linear-gradient(135deg, #e50914, #b91c1c); color: white; border: none; padding: 12px 24px; border-radius: var(--radius-lg); font-size: 0.95rem; font-weight: 700; display: inline-flex; align-items: center; gap: 10px; cursor: pointer; transition: all 0.25s; box-shadow: 0 8px 24px rgba(229,9,20,0.35); }
        .mm-find-btn:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 12px 32px rgba(229,9,20,0.5); }
        .mm-find-btn:disabled { opacity: 0.4; cursor: not-allowed; }

        /* Results */
        .mm-results { animation: fadeIn 0.4s ease; }
        .mm-results-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.75rem; }
        .mm-results-title { font-size: 1.3rem; font-weight: 800; margin-bottom: 0.25rem; }
        .mm-results-sub { color: var(--text-muted); font-size: 0.875rem; }
        .mm-reset-btn { color: var(--text-muted); white-space: nowrap; }
        .mm-empty { text-align: center; padding: 4rem 2rem; color: var(--text-secondary); }
        .mm-loading { text-align: center; padding: 4rem; color: var(--text-muted); }
        .mm-loading-dots { display: flex; justify-content: center; gap: 8px; margin-bottom: 1rem; }
        .mm-loading-dots span { width: 10px; height: 10px; border-radius: 50%; background: var(--accent-primary); animation: mmBounce 0.9s ease infinite; }
        .mm-loading-dots span:nth-child(2) { animation-delay: 0.15s; background: #f97316; }
        .mm-loading-dots span:nth-child(3) { animation-delay: 0.3s;  background: #7c3aed; }

        .mm-movies-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(155px, 1fr)); gap: 1rem; }
        .mm-movie-card { cursor: pointer; border-radius: var(--radius-lg); overflow: hidden; background: var(--bg-card); border: 1px solid var(--border-subtle); transition: var(--transition); }
        .mm-movie-card:hover { transform: translateY(-5px); box-shadow: 0 16px 40px rgba(0,0,0,0.5); border-color: rgba(229,9,20,0.3); }
        .mm-poster-wrap { position: relative; aspect-ratio: 2/3; background: var(--bg-secondary); overflow: hidden; }
        .mm-poster { width: 100%; height: 100%; object-fit: cover; display: block; transition: transform 0.3s; }
        .mm-movie-card:hover .mm-poster { transform: scale(1.04); }
        .mm-no-poster { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 2.5rem; }
        .mm-card-overlay { position: absolute; inset: 0; background: linear-gradient(to top, rgba(10,10,15,0.85) 0%, transparent 50%); display: flex; align-items: flex-end; justify-content: center; padding-bottom: 12px; opacity: 0; transition: opacity 0.3s; }
        .mm-movie-card:hover .mm-card-overlay { opacity: 1; }
        .mm-card-cta { font-size: 0.72rem; font-weight: 700; color: white; background: rgba(229,9,20,0.85); padding: 4px 12px; border-radius: var(--radius-full); }
        .mm-card-info { padding: 8px 10px 10px; }
        .mm-card-title { font-size: 0.78rem; font-weight: 700; color: var(--text-primary); overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; margin: 0 0 3px; }
        .mm-card-rating { font-size: 0.72rem; font-weight: 700; color: #f5c518; margin: 0 0 2px; }
        .mm-card-genre { font-size: 0.65rem; color: var(--text-muted); margin: 0; }

        @keyframes mmBounce { 0%,100% { transform:translateY(0); opacity:0.5 } 50% { transform:translateY(-8px); opacity:1 } }
        @media (max-width:600px) {
          .mm-vibe-grid { grid-template-columns: repeat(auto-fill, minmax(110px,1fr)); }
          .mm-movies-grid { grid-template-columns: repeat(auto-fill, minmax(130px,1fr)); }
          .mm-progress { display: none; }
        }
      `}</style>
    </div>
  )
}
