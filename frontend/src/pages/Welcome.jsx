import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { FiArrowRight, FiArrowLeft, FiStar } from 'react-icons/fi'

export default function Welcome() {
  const navigate = useNavigate()
  const { user } = useAuth()

  return (
    <div className="welcome-page">
      {/* Background orbs */}
      <div className="welcome-orbs">
        <div className="w-orb w-orb-1" />
        <div className="w-orb w-orb-2" />
        <div className="w-orb w-orb-3" />
      </div>

      <div className="welcome-card">
        {/* Animated check */}
        <div className="welcome-icon-wrap">
          <div className="welcome-icon-ring">
            <span className="welcome-icon-emoji">🎬</span>
          </div>
          <div className="welcome-sparkles">
            <FiStar className="sparkle s1" size={14} />
            <FiStar className="sparkle s2" size={10} />
            <FiStar className="sparkle s3" size={12} />
          </div>
        </div>

        <h1 className="welcome-title">
          You're all set{user?.username ? `, ${user.username}` : ''}!
        </h1>
        <p className="welcome-body">
          Your personalized movie experience is ready.<br />
          Discover trending films, AI recommendations, and more — all curated just for you.
        </p>

        {/* Feature highlights */}
        <div className="welcome-features">
          {[
            { emoji: '🔥', label: 'Trending Movies' },
            { emoji: '🤖', label: 'AI Picks for You' },
            { emoji: '❤️', label: 'Save Favorites' },
            { emoji: '📋', label: 'Your Watchlist' },
          ].map((f, i) => (
            <div key={i} className="welcome-feature-tag">
              <span>{f.emoji}</span>
              <span>{f.label}</span>
            </div>
          ))}
        </div>

        {/* Action buttons */}
        <div className="welcome-actions">
          <button
            className="btn btn-ghost welcome-back-btn"
            id="welcome-back-btn"
            onClick={() => navigate('/genre-skip')}
          >
            <FiArrowLeft size={16} /> Back
          </button>
          <button
            className="btn btn-primary btn-lg welcome-explore-btn"
            id="welcome-start-btn"
            onClick={() => navigate('/explore', { replace: true })}
          >
            Start Exploring <FiArrowRight size={20} />
          </button>
        </div>
      </div>

      <style>{`
        .welcome-page {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: calc(var(--navbar-height) + 1rem) 1rem 3rem;
          position: relative;
          overflow: hidden;
        }
        .welcome-orbs {
          position: absolute;
          inset: 0;
          pointer-events: none;
          overflow: hidden;
        }
        .w-orb {
          position: absolute;
          border-radius: 50%;
          filter: blur(90px);
          animation: gradientShift 8s ease infinite;
        }
        .w-orb-1 { width: 500px; height: 500px; top: -20%; left: -15%; background: rgba(229,9,20,0.12); }
        .w-orb-2 { width: 350px; height: 350px; bottom: -10%; right: -10%; background: rgba(124,58,237,0.1); animation-delay: 3s; }
        .w-orb-3 { width: 250px; height: 250px; top: 50%; left: 50%; background: rgba(79,195,247,0.06); animation-delay: 5s; }

        .welcome-card {
          position: relative;
          width: 100%;
          max-width: 520px;
          background: var(--bg-card);
          border: 1px solid var(--border-medium);
          border-radius: var(--radius-xl);
          padding: 3rem 2.5rem;
          box-shadow: var(--shadow-lg), 0 0 60px rgba(229,9,20,0.08);
          text-align: center;
          animation: fadeIn 0.6s ease;
        }

        .welcome-icon-wrap {
          position: relative;
          display: inline-block;
          margin-bottom: 1.75rem;
        }
        .welcome-icon-ring {
          width: 88px;
          height: 88px;
          border-radius: 50%;
          background: linear-gradient(135deg, rgba(229,9,20,0.2), rgba(124,58,237,0.15));
          border: 2px solid rgba(229,9,20,0.4);
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 2.5rem;
          animation: pulse 2s ease infinite;
          margin: 0 auto;
        }
        @keyframes pulse {
          0%, 100% { box-shadow: 0 0 0 0 rgba(229,9,20,0.3); }
          50% { box-shadow: 0 0 0 12px rgba(229,9,20,0); }
        }
        .welcome-sparkles {
          position: absolute;
          inset: 0;
          pointer-events: none;
        }
        .sparkle {
          position: absolute;
          color: var(--accent-primary);
          animation: sparkleAnim 2s ease infinite;
        }
        .s1 { top: 0; right: -4px; animation-delay: 0s; }
        .s2 { bottom: 4px; right: -8px; animation-delay: 0.5s; }
        .s3 { top: 10px; left: -10px; animation-delay: 1s; }
        @keyframes sparkleAnim {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.4; transform: scale(0.7); }
        }

        .welcome-title {
          font-size: clamp(1.5rem, 4vw, 2.2rem);
          font-weight: 900;
          margin-bottom: 0.75rem;
          background: linear-gradient(135deg, #fff, #e50914);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }
        .welcome-body {
          color: var(--text-secondary);
          font-size: 0.95rem;
          line-height: 1.7;
          margin-bottom: 1.75rem;
        }

        .welcome-features {
          display: flex;
          flex-wrap: wrap;
          gap: 10px;
          justify-content: center;
          margin-bottom: 2rem;
        }
        .welcome-feature-tag {
          display: flex;
          align-items: center;
          gap: 7px;
          padding: 8px 16px;
          background: rgba(255,255,255,0.04);
          border: 1px solid var(--border-subtle);
          border-radius: var(--radius-full);
          font-size: 0.82rem;
          font-weight: 600;
          color: var(--text-secondary);
          transition: var(--transition);
        }
        .welcome-feature-tag:hover {
          border-color: var(--border-medium);
          color: var(--text-primary);
          background: rgba(255,255,255,0.07);
        }

        .welcome-actions {
          display: flex;
          flex-direction: column;
          gap: 12px;
          align-items: center;
        }
        .welcome-explore-btn {
          width: 100%;
          justify-content: center;
          padding: 16px;
          font-size: 1.05rem;
          font-weight: 700;
          gap: 10px;
          background: linear-gradient(135deg, #e50914, #c00811);
          box-shadow: 0 4px 20px rgba(229,9,20,0.35);
          transition: var(--transition);
        }
        .welcome-explore-btn:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 30px rgba(229,9,20,0.5);
        }
        .welcome-back-btn {
          color: var(--text-muted);
          font-size: 0.875rem;
          gap: 8px;
        }
        .welcome-back-btn:hover { color: var(--text-primary); }
        .welcome-genre-like-btn {
          color: var(--text-muted);
          font-size: 0.8rem;
          opacity: 0.7;
        }
        .welcome-genre-like-btn:hover { color: #a78bfa; opacity: 1; }

        @media (max-width: 480px) {
          .welcome-card { padding: 2rem 1.25rem; }
        }
      `}</style>
    </div>
  )
}
