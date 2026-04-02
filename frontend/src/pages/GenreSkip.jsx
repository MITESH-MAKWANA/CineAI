import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { updateGenres } from '../api/auth'
import { toast } from 'react-hot-toast'
import { FiArrowRight, FiArrowLeft, FiSkipForward, FiCheck } from 'react-icons/fi'

const SKIP_GENRES = [
  { id: 'Horror', emoji: '👻', desc: 'Spine-chilling scares' },
  { id: 'War', emoji: '⚔️', desc: 'War & military stories' },
  { id: 'Western', emoji: '🤠', desc: 'Cowboys & frontiers' },
  { id: 'History', emoji: '📜', desc: 'Historical epics' },
  { id: 'Music', emoji: '🎵', desc: 'Music & performance films' },
  { id: 'Documentary', emoji: '🎥', desc: 'Real-world stories' },
  { id: 'Animation', emoji: '🎨', desc: 'Animated masterpieces' },
  { id: 'Family', emoji: '👨‍👩‍👧', desc: 'For the whole family' },
  { id: 'Mystery', emoji: '🕵️', desc: 'Whodunit & suspense' },
  { id: 'Romance', emoji: '❤️', desc: 'Love & relationships' },
  { id: 'Fantasy', emoji: '🧙', desc: 'Magical worlds & myths' },
  { id: 'Science Fiction', emoji: '🚀', desc: 'Futuristic worlds' },
]

export default function GenreSkip() {
  const navigate = useNavigate()
  const [skipped, setSkipped] = useState([])
  const [loading, setLoading] = useState(false)

  const toggle = (genre) => {
    setSkipped(prev =>
      prev.includes(genre) ? prev.filter(g => g !== genre) : [...prev, genre]
    )
  }

  const handleContinue = async () => {
    setLoading(true)
    try {
      if (skipped.length > 0) {
        toast.success(`Noted! We'll skip ${skipped.length} genre${skipped.length > 1 ? 's' : ''} for you.`)
      }
      navigate('/welcome', { replace: true })
    } catch {
      navigate('/welcome', { replace: true })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="genre-skip-page">
      <div className="genre-header">
        <div className="genre-logo">🎬 Cine<span>AI</span></div>
        <div className="genre-step-badge">Step 2 of 2 · Genre Skip</div>
        <h1 className="genre-title">Anything you'd rather skip?</h1>
        <p className="genre-subtitle">
          Select genres you <strong>don't</strong> want to see in your recommendations.<br />
          This helps us avoid content you're not interested in.
        </p>
        {skipped.length > 0 && (
          <div className="genre-skip-count">
            <FiSkipForward size={14} /> {skipped.length} genre{skipped.length > 1 ? 's' : ''} skipped
          </div>
        )}
      </div>

      <div className="genre-grid">
        {SKIP_GENRES.map(({ id, emoji, desc }) => {
          const isSkipped = skipped.includes(id)
          return (
            <button
              key={id}
              className={`genre-card skip-card${isSkipped ? ' skipped' : ''}`}
              onClick={() => toggle(id)}
              id={`skip-${id.toLowerCase().replace(/\s+/g, '-')}`}
            >
              <span className="genre-emoji">{emoji}</span>
              <span className="genre-name">{id}</span>
              <span className="genre-desc">{desc}</span>
              {isSkipped && (
                <div className="genre-check skip-check">
                  <FiSkipForward size={14} />
                </div>
              )}
            </button>
          )
        })}
      </div>

      <div className="genre-actions">
        <button
          className="btn btn-primary btn-lg"
          onClick={handleContinue}
          disabled={loading}
          id="genre-skip-continue-btn"
        >
          {loading ? <span className="btn-spinner" /> : <><span>Continue to You're All Set</span><FiArrowRight size={18} /></>}
        </button>

        <button
          className="btn btn-ghost"
          onClick={() => navigate('/genre-select', { replace: true })}
          id="genre-skip-back-btn"
        >
          <FiArrowLeft size={16} /> Back to Genre Likes
        </button>

        <div className="genre-skip-divider">or</div>

        <button
          className="btn btn-outline-muted"
          onClick={() => navigate('/welcome', { replace: true })}
          id="genre-skip-all-btn"
        >
          <FiSkipForward size={15} /> Skip all genre settings
        </button>
      </div>

      <style>{`
        .genre-skip-page {
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
          background: rgba(124,58,237,0.12);
          border: 1px solid rgba(124,58,237,0.25);
          border-radius: var(--radius-full);
          color: #a78bfa;
          font-size: 0.75rem;
          font-weight: 600;
          letter-spacing: 0.05em;
          margin-bottom: 1.25rem;
        }
        .genre-title { font-size: clamp(1.5rem, 4vw, 2.5rem); font-weight: 800; margin-bottom: 0.75rem; }
        .genre-subtitle { color: var(--text-secondary); font-size: 0.95rem; line-height: 1.6; margin-bottom: 1rem; }
        .genre-subtitle strong { color: var(--text-primary); }
        .genre-skip-count {
          display: inline-flex; align-items: center; gap: 6px;
          padding: 6px 16px;
          background: rgba(124,58,237,0.12);
          border: 1px solid rgba(124,58,237,0.25);
          border-radius: var(--radius-full);
          color: #a78bfa;
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
          border-color: rgba(124,58,237,0.4);
          background: rgba(124,58,237,0.05);
          transform: translateY(-4px);
          box-shadow: var(--shadow-md);
        }
        .genre-card.skipped {
          border-color: rgba(124,58,237,0.6);
          background: rgba(124,58,237,0.1);
          box-shadow: 0 0 20px rgba(124,58,237,0.15);
          opacity: 0.75;
        }
        .genre-emoji { font-size: 2rem; line-height: 1; }
        .genre-name { font-size: 0.9rem; font-weight: 700; color: var(--text-primary); }
        .genre-desc { font-size: 0.72rem; color: var(--text-muted); line-height: 1.4; }
        .genre-check {
          position: absolute;
          top: 10px; right: 10px;
          width: 22px; height: 22px;
          border-radius: 50%;
          display: flex; align-items: center; justify-content: center;
          color: white;
          animation: scaleIn 0.2s ease;
        }
        .skip-check { background: #7c3aed; }
        .genre-actions {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 12px;
        }
        .genre-actions .btn-primary { min-width: 280px; justify-content: center; }
        .genre-skip-divider {
          color: var(--text-muted);
          font-size: 0.8rem;
          position: relative;
          width: 200px;
          text-align: center;
        }
        .genre-skip-divider::before,
        .genre-skip-divider::after {
          content: '';
          position: absolute;
          top: 50%;
          width: 40%;
          height: 1px;
          background: var(--border-subtle);
        }
        .genre-skip-divider::before { left: 0; }
        .genre-skip-divider::after { right: 0; }
        .btn-outline-muted {
          background: transparent;
          border: 1px solid var(--border-medium);
          color: var(--text-muted);
          padding: 10px 20px;
          border-radius: var(--radius-md);
          font-size: 0.875rem;
          cursor: pointer;
          display: flex; align-items: center; gap: 8px;
          transition: var(--transition);
        }
        .btn-outline-muted:hover { color: var(--text-primary); border-color: var(--border-light); }
        .btn-spinner { width: 20px; height: 20px; border: 2px solid rgba(255,255,255,0.3); border-top-color: white; border-radius: 50%; animation: spinAnim 0.7s linear infinite; }
        @media (max-width: 480px) {
          .genre-grid { grid-template-columns: repeat(2, 1fr); }
          .genre-actions .btn-primary { min-width: unset; width: 100%; }
        }
      `}</style>
    </div>
  )
}
