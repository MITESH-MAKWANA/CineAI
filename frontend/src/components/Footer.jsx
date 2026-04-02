import { Link } from 'react-router-dom'
import { FiGithub, FiMail, FiHeart } from 'react-icons/fi'

export default function Footer() {
  return (
    <footer className="footer">
      <div className="footer-inner container">
        <div className="footer-brand">
          <Link to="/" className="footer-logo">
            <span>🎬</span>
            <span>Cine<span style={{color:'var(--accent-primary)'}}>AI</span></span>
          </Link>
          <p className="footer-tagline">Smart recommendations. Better entertainment.</p>
          <div className="footer-social">
            <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="social-icon-link" aria-label="GitHub">
              <FiGithub size={18} />
            </a>
            <a href="mailto:contact@cineai.com" className="social-icon-link" aria-label="Email">
              <FiMail size={18} />
            </a>
          </div>
        </div>

        <div className="footer-col">
          <h4 className="footer-heading">Explore</h4>
          <ul className="footer-links">
            <li><Link to="/explore">Trending Movies</Link></li>
            <li><Link to="/explore?filter=top_rated">Top Rated</Link></li>
            <li><Link to="/explore">Genres</Link></li>
          </ul>
        </div>

        <div className="footer-col">
          <h4 className="footer-heading">Features</h4>
          <ul className="footer-links">
            <li><Link to="/explore">AI Recommendations</Link></li>
            <li><Link to="/explore">Smart Search</Link></li>
            <li><Link to="/about">Sentiment Insights</Link></li>
          </ul>
        </div>

        <div className="footer-col">
          <h4 className="footer-heading">Support</h4>
          <ul className="footer-links">
            <li><Link to="/contact">Contact</Link></li>
            <li><Link to="/about">About</Link></li>
          </ul>
        </div>
      </div>

      <div className="footer-bottom">
        <p>© 2026 CineAI • Powered by AI &amp; Machine Learning</p>
        <p>Made with <FiHeart size={12} style={{color:'var(--accent-primary)', display:'inline', margin:'0 3px'}} /> using FastAPI &amp; React</p>
      </div>

      <style>{`
        .footer {
          background: var(--bg-secondary);
          border-top: 1px solid var(--border-subtle);
          padding: 3rem 0 0;
          margin-top: 4rem;
        }
        .footer-inner {
          display: grid;
          grid-template-columns: 2fr 1fr 1fr 1fr;
          gap: 2.5rem;
          padding-bottom: 2.5rem;
        }
        .footer-logo {
          display: flex;
          align-items: center;
          gap: 8px;
          font-family: var(--font-display);
          font-size: 1.3rem;
          font-weight: 800;
          color: var(--text-primary);
          text-decoration: none;
          margin-bottom: 0.5rem;
        }
        .footer-tagline {
          color: var(--text-muted);
          font-size: 0.875rem;
          margin-bottom: 1rem;
          line-height: 1.5;
        }
        .footer-social { display: flex; gap: 10px; }
        .social-icon-link {
          width: 36px; height: 36px;
          display: flex; align-items: center; justify-content: center;
          background: rgba(255,255,255,0.07);
          border-radius: var(--radius-md);
          color: var(--text-secondary);
          transition: var(--transition);
          text-decoration: none;
        }
        .social-icon-link:hover {
          background: rgba(229,9,20,0.2);
          color: var(--accent-secondary);
        }
        .footer-heading {
          font-size: 0.8rem;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 0.08em;
          color: var(--text-muted);
          margin-bottom: 1rem;
        }
        .footer-links { display: flex; flex-direction: column; gap: 8px; }
        .footer-links li a {
          color: var(--text-secondary);
          font-size: 0.875rem;
          text-decoration: none;
          transition: var(--transition);
        }
        .footer-links li a:hover { color: var(--text-primary); padding-left: 4px; }
        .footer-bottom {
          border-top: 1px solid var(--border-subtle);
          padding: 1.25rem clamp(1rem, 3vw, 2rem);
          display: flex;
          justify-content: space-between;
          align-items: center;
          flex-wrap: wrap;
          gap: 8px;
          max-width: 1400px;
          margin: 0 auto;
        }
        .footer-bottom p { font-size: 0.8rem; color: var(--text-muted); }
        @media (max-width: 768px) {
          .footer-inner { grid-template-columns: 1fr 1fr; }
          .footer-brand { grid-column: 1 / -1; }
          .footer-bottom { flex-direction: column; text-align: center; }
        }
        @media (max-width: 480px) {
          .footer-inner { grid-template-columns: 1fr; }
        }
      `}</style>
    </footer>
  )
}
