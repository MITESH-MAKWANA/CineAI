import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { updateGenres } from '../api/auth'
import { toast } from 'react-hot-toast'
import { FiCheck, FiArrowRight, FiSkipForward } from 'react-icons/fi'

const GENRES = [
  { id: 'Action', emoji: '💥', desc: 'Explosive action & adventure' },
  { id: 'Drama', emoji: '🎭', desc: 'Emotional storytelling' },
  { id: 'Comedy', emoji: '😂', desc: 'Laugh out loud films' },
  { id: 'Thriller', emoji: '😨', desc: 'Edge-of-seat suspense' },
  { id: 'Science Fiction', emoji: '🚀', desc: 'Futuristic worlds' },
  { id: 'Horror', emoji: '👻', desc: 'Spine-chilling scares' },
  { id: 'Romance', emoji: '❤️', desc: 'Love & relationships' },
  { id: 'Animation', emoji: '🎨', desc: 'Animated masterpieces' },
  { id: 'Fantasy', emoji: '🧙', desc: 'Magical worlds & myths' },
  { id: 'Crime', emoji: '🔍', desc: 'Mystery & crime thrillers' },
  { id: 'War', emoji: '⚔️', desc: 'War & military stories' },
  { id: 'Music', emoji: '🎵', desc: 'Music & performance films' },
  { id: 'Family', emoji: '👨‍👩‍👧', desc: 'For the whole family' },
  { id: 'History', emoji: '📜', desc: 'Historical epics' },
  { id: 'Mystery', emoji: '🕵️', desc: 'Whodunit & suspense' },
  { id: 'Western', emoji: '🤠', desc: 'Cowboys & frontiers' },
]

export default function GenreSelect() {
  const { updateUserGenres } = useAuth()
  const navigate = useNavigate()
  const [selected, setSelected] = useState([])
  const [loading, setLoading] = useState(false)

  const toggle = (genre) => {
    setSelected(prev =>
      prev.includes(genre) ? prev.filter(g => g !== genre) : [...prev, genre]
    )
  }

  const handleSave = async () => {
    if (selected.length === 0) return toast.error('Please select at least one genre')
    setLoading(true)
    try {
      await updateGenres(selected)
      updateUserGenres(selected)
      toast.success('Genres saved!')
    } catch (err) {
      toast.error('Could not save genres, but you can continue.')
    } finally {
      setLoading(false)
      navigate('/genre-skip', { replace: true })
    }
  }

  return (
    <div className="genre-page">
      <div className="genre-header">
        <div className="genre-logo">🎬 Cine<span>AI</span></div>
        <div className="genre-step-badge">Pick Your Favourite Genres</div>
        <h1 className="genre-title">What do you love watching?</h1>
        <p className="genre-subtitle">
          Select your favorite genres — we'll personalize your recommendations.
          <br />You can always change this later.
        </p>
        {selected.length > 0 && (
          <div className="genre-selected-count">
            <FiCheck size={14} /> {selected.length} genre{selected.length > 1 ? 's' : ''} selected
          </div>
        )}
      </div>

      <div className="genre-grid">
        {GENRES.map(({ id, emoji, desc }) => {
          const isSelected = selected.includes(id)
          return (
            <button
              key={id}
              className={`genre-card${isSelected ? ' selected' : ''}`}
              onClick={() => toggle(id)}
              id={`genre-${id.toLowerCase().replace(/\s+/g, '-')}`}
            >
              <span className="genre-emoji">{emoji}</span>
              <span className="genre-name">{id}</span>
              <span className="genre-desc">{desc}</span>
              {isSelected && (
                <div className="genre-check">
                  <FiCheck size={14} />
                </div>
              )}
            </button>
          )
        })}
      </div>

      <div className="genre-actions">
        <button className="btn btn-primary btn-lg" onClick={handleSave} disabled={loading || selected.length === 0} id="genre-save-btn">
          {loading ? <span className="btn-spinner" /> : <><span>Continue with {selected.length} Genre{selected.length !== 1 ? 's' : ''}</span><FiArrowRight size={18}/></>}
        </button>
        <button className="btn btn-ghost" onClick={() => navigate('/genre-skip', { replace: true })} id="genre-skip-btn">
          <FiSkipForward size={16} /> Skip for now
        </button>
      </div>

      <style>{`
        .genre-page {
          min-height: 100vh;
          padding: calc(var(--navbar-height) + 2rem) clamp(1rem, 5vw, 3rem) 4rem;
          max-width: 900px;
          margin: 0 auto;
        }
        .genre-header { text-align: center; margin-bottom: 2.5rem; }
        .genre-logo {
          font-family: var(--font-display);
          font-size: 1.3rem;
          font-weight: 800;
          margin-bottom: 0.75rem;
          color: var(--text-primary);
        }
        .genre-logo span { color: var(--accent-primary); }
        .genre-step-badge {
          display: inline-block;
          padding: 4px 14px;
          background: rgba(229,9,20,0.1);
          border: 1px solid rgba(229,9,20,0.2);
          border-radius: var(--radius-full);
          color: var(--accent-secondary);
          font-size: 0.75rem;
          font-weight: 600;
          letter-spacing: 0.05em;
          margin-bottom: 1.25rem;
        }
        .genre-title { font-size: clamp(1.5rem, 4vw, 2.5rem); font-weight: 800; margin-bottom: 0.75rem; }
        .genre-subtitle { color: var(--text-secondary); font-size: 0.95rem; line-height: 1.6; margin-bottom: 1rem; }
        .genre-selected-count {
          display: inline-flex; align-items: center; gap: 6px;
          padding: 6px 16px;
          background: rgba(229,9,20,0.15);
          border: 1px solid rgba(229,9,20,0.3);
          border-radius: var(--radius-full);
          color: var(--accent-secondary);
          font-size: 0.8rem;
          font-weight: 600;
          margin-top: 0.5rem;
        }
        .genre-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
          gap: 14px;
          margin-bottom: 2.5rem;
        }
        .genre-card {
          position: relative;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 6px;
          padding: 1.5rem 1rem;
          background: var(--bg-card);
          border: 2px solid var(--border-subtle);
          border-radius: var(--radius-lg);
          cursor: pointer;
          transition: var(--transition);
          text-align: center;
        }
        .genre-card:hover {
          border-color: var(--border-medium);
          background: var(--bg-card-hover);
          transform: translateY(-4px);
          box-shadow: var(--shadow-md);
        }
        .genre-card.selected {
          border-color: var(--accent-primary);
          background: rgba(229,9,20,0.08);
          box-shadow: 0 0 20px rgba(229,9,20,0.2);
        }
        .genre-emoji { font-size: 2rem; line-height: 1; }
        .genre-name { font-size: 0.9rem; font-weight: 700; color: var(--text-primary); }
        .genre-desc { font-size: 0.72rem; color: var(--text-muted); line-height: 1.4; }
        .genre-check {
          position: absolute;
          top: 10px; right: 10px;
          width: 22px; height: 22px;
          background: var(--accent-primary);
          border-radius: 50%;
          display: flex; align-items: center; justify-content: center;
          color: white;
          animation: scaleIn 0.2s ease;
        }
        .genre-actions {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 12px;
        }
        .genre-actions .btn-primary { min-width: 280px; justify-content: center; }
        .btn-spinner { width: 20px; height: 20px; border: 2px solid rgba(255,255,255,0.3); border-top-color: white; border-radius: 50%; animation: spinAnim 0.7s linear infinite; }
        @media (max-width: 480px) {
          .genre-grid { grid-template-columns: repeat(2, 1fr); }
          .genre-actions .btn-primary { min-width: unset; width: 100%; }
        }
      `}</style>
    </div>
  )
}
