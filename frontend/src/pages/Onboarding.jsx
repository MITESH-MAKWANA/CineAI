import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { toast } from 'react-hot-toast'
import api from '../api/axiosInstance'
import { FiArrowRight, FiArrowLeft, FiCheck, FiHeart, FiSlash } from 'react-icons/fi'

const ALL_GENRES = [
  'Action','Adventure','Animation','Comedy','Crime','Documentary',
  'Drama','Family','Fantasy','History','Horror','Music','Mystery',
  'Romance','Science Fiction','Thriller','TV Movie','War','Western',
]

const STEPS = [
  { id: 1, title: 'Genres You Love',  icon: '\u2764\uFE0F', sub: 'Pick at least one genre you enjoy watching' },
  { id: 2, title: 'Genres to Skip',   icon: '\uD83D\uDEAB', sub: "Select genres you'd like to avoid (optional)" },
  { id: 3, title: "You're All Set!",  icon: '\uD83C\uDF89', sub: 'Your preferences have been saved' },
]

export default function Onboarding({ onComplete }) {
  const { logout, updateUserGenres } = useAuth()
  const navigate = useNavigate()

  const [step, setStep]     = useState(1)
  const [loved, setLoved]   = useState([])
  const [skip, setSkip]     = useState([])
  const [saving, setSaving] = useState(false)

  const toggleGenre = (list, setList, genre) =>
    setList(prev => prev.includes(genre) ? prev.filter(g => g !== genre) : [...prev, genre])

  /* ── Save & navigate to login ───────────────────────────── */
  const saveAndFinish = async () => {
    setSaving(true)
    try {
      const token = localStorage.getItem('cineai_token')
      if (token) {
        await api.put('/auth/profile', {
          loved_genres: loved,
          skipped_genres: skip,
          onboarding_done: true,
        }, { headers: { Authorization: `Bearer ${token}` } })
        if (loved.length > 0) updateUserGenres(loved)
        toast.success('Preferences saved! Please sign in to continue 🎬')
      }
    } catch {
      toast('Preferences noted. Please log in to continue.', { icon: '🎬' })
    } finally {
      setSaving(false)
    }
    if (onComplete) { onComplete(); return }
    // Persist all preferences in auth state & localStorage
    updateUserGenres(loved, skip)
    // Logout and redirect to login so the user formally signs in
    logout()
    navigate('/login', { replace: true })
  }

  const skipAll = () => {
    logout()
    navigate('/login', { replace: true })
  }

  /* ── Genre chip ─────────────────────────────────────────── */
  const Chip = ({ genre, selected, onToggle, color = 'var(--accent-primary)' }) => (
    <button
      type="button"
      onClick={() => onToggle(genre)}
      className={`genre-chip${selected ? ' genre-chip-selected' : ''}`}
      style={selected ? { borderColor: color, background: `${color}20`, color } : {}}
    >
      {selected && <FiCheck size={13} style={{ flexShrink: 0 }} />}
      {genre}
    </button>
  )

  /* ── Progress bar ───────────────────────────────────────── */
  const Progress = () => (
    <div className="ob-progress">
      {STEPS.map((s) => (
        <div key={s.id} className="ob-step-dot-wrap">
          <div className={`ob-step-dot${step >= s.id ? ' ob-dot-active' : ''}${step > s.id ? ' ob-dot-done' : ''}`}>
            {step > s.id ? <FiCheck size={12} /> : s.id}
          </div>
          <span className="ob-dot-label">{s.id === 3 ? 'Done' : s.title.split(' ')[0]}</span>
          {s.id < STEPS.length && <div className={`ob-connector${step > s.id ? ' ob-conn-active' : ''}`} />}
        </div>
      ))}
    </div>
  )

  return (
    <div className="ob-page">
      <div className="ob-card">

        {/* Header */}
        <div className="ob-header">
          <div className="ob-logo">🎬 Cine<span style={{ color: 'var(--accent-primary)' }}>AI</span></div>
          <Progress />
        </div>

        {/* ── Step 1: Genre Love ─────────────────────────────── */}
        {step === 1 && (
          <div className="ob-content">
            <div className="ob-icon-wrap ob-icon-love">{STEPS[0].icon}</div>
            <h2 className="ob-title">{STEPS[0].title}</h2>
            <p className="ob-sub">{STEPS[0].sub}</p>

            <div className="genre-grid">
              {ALL_GENRES.map(g => (
                <Chip key={g} genre={g} selected={loved.includes(g)}
                  onToggle={(g) => toggleGenre(loved, setLoved, g)}
                  color="#10b981" />
              ))}
            </div>

            <div className="ob-footer">
              <button className="btn btn-ghost ob-skip" onClick={skipAll}>
                Skip All Setup
              </button>
              <button
                className="btn btn-primary"
                disabled={loved.length === 0}
                onClick={() => setStep(2)}
              >
                Continue <FiArrowRight size={16} />
              </button>
            </div>
          </div>
        )}

        {/* ── Step 2: Skip Genres ────────────────────────────── */}
        {step === 2 && (
          <div className="ob-content">
            <div className="ob-icon-wrap ob-icon-skip">{STEPS[1].icon}</div>
            <h2 className="ob-title">{STEPS[1].title}</h2>
            <p className="ob-sub">{STEPS[1].sub}</p>

            <div className="genre-grid">
              {ALL_GENRES.filter(g => !loved.includes(g)).map(g => (
                <Chip key={g} genre={g} selected={skip.includes(g)}
                  onToggle={(g) => toggleGenre(skip, setSkip, g)}
                  color="#e50914" />
              ))}
            </div>

            <div className="ob-footer">
              <button className="btn btn-ghost ob-skip" onClick={() => setStep(1)}>
                <FiArrowLeft size={15} /> Back
              </button>
              <button className="btn btn-primary" onClick={() => setStep(3)}>
                Continue <FiArrowRight size={16} />
              </button>
            </div>
          </div>
        )}

        {/* ── Step 3: You're All Set ─────────────────────────── */}
        {step === 3 && (
          <div className="ob-content ob-allset">
            <div className="ob-confetti">🎊</div>
            <div className="ob-icon-wrap ob-icon-done">{STEPS[2].icon}</div>
            <h2 className="ob-title">You're All Set!</h2>
            <p className="ob-sub">Your preferences are saved. Sign in to start discovering movies made for you.</p>

            <div className="ob-summary">
              <div className="ob-summary-row">
                <span className="ob-summary-label"><FiHeart size={14} color="#10b981" /> Loved genres</span>
                <div className="ob-summary-chips">
                  {loved.length > 0 ? loved.map(g => (
                    <span key={g} className="ob-summary-chip ob-chip-love">{g}</span>
                  )) : <span className="ob-none">None selected</span>}
                </div>
              </div>
              {skip.length > 0 && (
                <div className="ob-summary-row">
                  <span className="ob-summary-label"><FiSlash size={14} color="#e50914" /> Skipping</span>
                  <div className="ob-summary-chips">
                    {skip.map(g => (
                      <span key={g} className="ob-summary-chip ob-chip-skip">{g}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="ob-footer">
              <button className="btn btn-ghost ob-skip" onClick={() => setStep(2)}>
                <FiArrowLeft size={15} /> Back
              </button>
              <button className="btn btn-primary ob-start-btn" onClick={saveAndFinish} disabled={saving}>
                {saving ? <span className="btn-spinner" /> : <>Start Exploring <FiArrowRight size={16} /></>}
              </button>
            </div>
          </div>
        )}
      </div>

      <style>{`
        .ob-page {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: calc(var(--navbar-height) + 1.5rem) 1rem 3rem;
          background: radial-gradient(ellipse at 20% 20%, rgba(229,9,20,0.07) 0%, transparent 60%),
                      radial-gradient(ellipse at 80% 80%, rgba(124,58,237,0.06) 0%, transparent 50%);
        }
        .ob-card {
          background: var(--bg-card);
          border: 1px solid var(--border-medium);
          border-radius: var(--radius-xl);
          padding: 2rem 2.25rem 2.5rem;
          width: 100%;
          max-width: 600px;
          box-shadow: var(--shadow-lg);
          animation: fadeIn 0.4s ease;
        }
        .ob-header { text-align: center; margin-bottom: 2rem; }
        .ob-logo {
          font-family: var(--font-display);
          font-size: 1.35rem;
          font-weight: 800;
          margin-bottom: 1.5rem;
        }

        /* Progress */
        .ob-progress { display: flex; align-items: center; justify-content: center; gap: 0; }
        .ob-step-dot-wrap { display: flex; align-items: center; gap: 0; position: relative; }
        .ob-dot-label { position: absolute; top: 32px; left: 50%; transform: translateX(-50%); font-size: 0.62rem; color: var(--text-muted); font-weight: 600; white-space: nowrap; }
        .ob-step-dot {
          width: 30px; height: 30px;
          border-radius: 50%;
          border: 2px solid var(--border-medium);
          display: flex; align-items: center; justify-content: center;
          font-size: 0.75rem; font-weight: 700;
          color: var(--text-muted);
          background: var(--bg-secondary);
          transition: all 0.35s;
          z-index: 1;
          position: relative;
        }
        .ob-dot-active { border-color: var(--accent-primary); color: var(--accent-primary); background: rgba(229,9,20,0.12); }
        .ob-dot-done { border-color: #10b981; color: white; background: #10b981; }
        .ob-connector { width: 60px; height: 2px; background: var(--border-medium); transition: background 0.35s; }
        .ob-conn-active { background: #10b981; }

        /* Content */
        .ob-content { display: flex; flex-direction: column; align-items: center; text-align: center; }
        .ob-icon-wrap {
          width: 72px; height: 72px;
          border-radius: 50%;
          display: flex; align-items: center; justify-content: center;
          font-size: 2rem; margin-bottom: 1rem;
        }
        .ob-icon-love { background: rgba(16,185,129,0.14); }
        .ob-icon-skip { background: rgba(229,9,20,0.12); }
        .ob-icon-done { background: rgba(245,197,24,0.18); }
        .ob-title { font-size: 1.5rem; font-weight: 800; margin-bottom: 0.4rem; }
        .ob-sub { color: var(--text-muted); font-size: 0.875rem; margin-bottom: 1.5rem; max-width: 420px; }

        /* Genre chips */
        .genre-grid {
          display: flex; flex-wrap: wrap; gap: 8px;
          justify-content: center;
          max-height: 240px;
          overflow-y: auto;
          width: 100%;
          padding: 4px 2px;
          margin-bottom: 1.5rem;
          scrollbar-width: thin;
        }
        .genre-chip {
          padding: 6px 14px;
          border-radius: var(--radius-full);
          border: 1.5px solid var(--border-medium);
          background: var(--bg-secondary);
          color: var(--text-secondary);
          font-size: 0.82rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
          display: flex; align-items: center; gap: 5px;
        }
        .genre-chip:hover { border-color: var(--text-muted); color: var(--text-primary); }
        .genre-chip-selected { font-weight: 700; }

        /* Summary */
        .ob-allset { }
        .ob-confetti { font-size: 2.5rem; margin-bottom: -0.5rem; }
        .ob-summary {
          width: 100%;
          background: var(--bg-secondary);
          border: 1px solid var(--border-subtle);
          border-radius: var(--radius-lg);
          padding: 1.25rem;
          margin-bottom: 1.5rem;
          text-align: left;
          display: flex; flex-direction: column; gap: 1rem;
        }
        .ob-summary-row { display: flex; flex-direction: column; gap: 6px; }
        .ob-summary-label { font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); display: flex; align-items: center; gap: 6px; }
        .ob-summary-chips { display: flex; flex-wrap: wrap; gap: 6px; }
        .ob-summary-chip { padding: 3px 10px; border-radius: var(--radius-full); font-size: 0.75rem; font-weight: 600; }
        .ob-chip-love { background: rgba(16,185,129,0.15); color: #10b981; }
        .ob-chip-skip { background: rgba(229,9,20,0.12); color: #e50914; }
        .ob-none { color: var(--text-muted); font-size: 0.8rem; font-style: italic; }

        /* Footer */
        .ob-footer { display: flex; align-items: center; justify-content: space-between; width: 100%; gap: 12px; }
        .ob-skip { color: var(--text-muted); font-size: 0.85rem; padding: 8px 14px; }
        .ob-skip:hover { color: var(--text-primary); }
        .ob-start-btn { min-width: 180px; justify-content: center; }

        .btn-spinner {
          width: 18px; height: 18px;
          border: 2px solid rgba(255,255,255,0.3);
          border-top-color: white;
          border-radius: 50%;
          animation: spinAnim 0.7s linear infinite;
        }

        @media (max-width: 560px) {
          .ob-card { padding: 1.75rem 1.25rem 2rem; }
          .ob-connector { width: 32px; }
        }
      `}</style>
    </div>
  )
}
