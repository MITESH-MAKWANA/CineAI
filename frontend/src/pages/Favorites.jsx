import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'react-hot-toast'
import { FiHeart, FiTrash2, FiStar } from 'react-icons/fi'
import { getFavorites, removeFromFavorites, getPosterUrl } from '../api/movies'
import LoadingSpinner from '../components/LoadingSpinner'
import { useAuth } from '../context/AuthContext'

export default function Favorites() {
  const navigate = useNavigate()
  const { isAuthenticated } = useAuth()
  const [favorites, setFavorites] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!isAuthenticated) { navigate('/login'); return }
    getFavorites()
      .then(r => setFavorites(Array.isArray(r.data) ? r.data : []))
      .catch(err => {
        console.error('Favorites load error:', err)
        toast.error('Failed to load favorites')
      })
      .finally(() => setLoading(false))
  }, [isAuthenticated])


  const handleRemove = async (movieId, movieTitle) => {
    try {
      await removeFromFavorites(movieId)
      setFavorites(prev => prev.filter(m => m.movie_id !== movieId))
      toast.success(`Removed "${movieTitle}" from Favorites`)
    } catch {
      toast.error('Failed to remove')
    }
  }

  return (
    <div className="list-page page-wrapper">
      <div className="container">
        <div className="list-page-header">
          <div className="list-page-icon" style={{ background: 'rgba(229,9,20,0.15)', color: 'var(--accent-primary)' }}>
            <FiHeart size={28} fill="currentColor" />
          </div>
          <div>
            <h1 className="list-page-title">My Favorites</h1>
            <p className="list-page-subtitle">{favorites.length} movie{favorites.length !== 1 ? 's' : ''} you love</p>
          </div>
        </div>

        {loading ? (
          <LoadingSpinner text="Loading favorites..." />
        ) : favorites.length === 0 ? (
          <div className="list-empty">
            <span style={{ fontSize: '4rem' }}>❤️</span>
            <h2>No favorites yet</h2>
            <p>Movies you favorite will appear here.</p>
            <button className="btn btn-primary" onClick={() => navigate('/explore')}>Explore Movies</button>
          </div>
        ) : (
          <div className="list-grid">
            {favorites.map(item => (
              <div key={item.id} className="list-card card" onClick={() => navigate(`/movie/${item.movie_id}`)}>
                <div className="list-card-poster-wrap">
                  <img
                    src={getPosterUrl(item.poster_path, 'w342')}
                    alt={item.movie_title}
                    className="list-card-poster"
                    onError={e => { e.target.src = ''; e.target.style.display = 'none' }}
                  />
                  <div className="list-card-overlay">
                    <button className="btn btn-primary btn-sm" onClick={e => { e.stopPropagation(); navigate(`/movie/${item.movie_id}`) }}>
                      View Details
                    </button>
                  </div>
                </div>
                <div className="list-card-info">
                  <h3 className="list-card-title">{item.movie_title}</h3>
                  <div className="list-card-meta">
                    {item.vote_average && (
                      <span className="list-rating"><FiStar size={12} fill="var(--accent-gold)" /> {parseFloat(item.vote_average).toFixed(1)}</span>
                    )}
                    <span className="list-date">Added {item.added_at?.split('T')[0]}</span>
                  </div>
                  <button
                    className="list-remove-btn"
                    onClick={e => { e.stopPropagation(); handleRemove(item.movie_id, item.movie_title) }}
                    title="Remove from favorites"
                  >
                    <FiTrash2 size={14} /> Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      <ListPageStyles />
    </div>
  )
}

function ListPageStyles() {
  return <style>{`
    .list-page { padding-top: calc(var(--navbar-height, 64px) + 1.5rem); padding-bottom: 4rem; }
    .list-page-header {
      display: flex; align-items: center; gap: 1.25rem;
      padding: 2rem 0 1.75rem;
      border-bottom: 1px solid var(--border-subtle);
      margin-bottom: 2rem;
    }
    .list-page-icon {
      width: 64px; height: 64px;
      border-radius: var(--radius-lg);
      display: flex; align-items: center; justify-content: center;
      flex-shrink: 0;
    }
    .list-page-title { font-size: 1.75rem; font-weight: 800; margin-bottom: 0.25rem; }
    .list-page-subtitle { color: var(--text-muted); font-size: 0.875rem; }
    .list-empty {
      text-align: center; padding: 5rem 2rem;
      display: flex; flex-direction: column; align-items: center; gap: 1rem;
    }
    .list-empty h2 { font-size: 1.5rem; }
    .list-empty p { color: var(--text-muted); }
    .list-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 1.25rem;
    }
    .list-card { cursor: pointer; overflow: hidden; border-radius: var(--radius-lg); }
    .list-card:hover { transform: translateY(-4px); box-shadow: var(--shadow-lg); }
    .list-card-poster-wrap { position: relative; aspect-ratio: 2/3; background: var(--bg-secondary); overflow: hidden; }
    .list-card-poster { width: 100%; height: 100%; object-fit: cover; transition: transform 0.4s; }
    .list-card:hover .list-card-poster { transform: scale(1.06); }
    .list-card-overlay {
      position: absolute; inset: 0;
      background: rgba(10,10,15,0.75);
      display: flex; align-items: center; justify-content: center;
      opacity: 0; transition: opacity 0.3s;
    }
    .list-card:hover .list-card-overlay { opacity: 1; }
    .list-card-info { padding: 12px; }
    .list-card-title { font-size: 0.875rem; font-weight: 700; margin-bottom: 6px; line-height: 1.3; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
    .list-card-meta { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; flex-wrap: wrap; }
    .list-rating { display: flex; align-items: center; gap: 4px; font-size: 0.8rem; color: var(--accent-gold); font-weight: 600; }
    .list-date { font-size: 0.72rem; color: var(--text-muted); }
    .list-remove-btn {
      display: flex; align-items: center; gap: 5px;
      width: 100%; padding: 7px 10px;
      background: rgba(255,255,255,0.04);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-sm);
      color: var(--text-muted); font-size: 0.75rem;
      cursor: pointer; transition: var(--transition);
    }
    .list-remove-btn:hover { background: rgba(229,9,20,0.1); border-color: rgba(229,9,20,0.3); color: var(--accent-secondary); }
    @media (max-width: 480px) {
      .list-grid { grid-template-columns: repeat(2, 1fr); gap: 10px; }
    }
  `}</style>
}
