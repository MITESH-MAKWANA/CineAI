import { useState, useEffect, useRef } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { FiMenu, FiX, FiLogOut, FiHeart, FiBookmark, FiHome, FiCompass, FiKey, FiSettings, FiUser } from 'react-icons/fi'
import './Navbar.css'

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuth()
  const navigate = useNavigate()
  const [menuOpen, setMenuOpen] = useState(false)
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)
  const dropRef = useRef(null)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 60)
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  useEffect(() => {
    const handler = (e) => {
      if (dropRef.current && !dropRef.current.contains(e.target)) setDropdownOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const handleLogout = () => {
    logout()
    setDropdownOpen(false)
    navigate('/')
  }

  return (
    <nav className={`navbar${scrolled ? ' navbar-scrolled' : ''}`}>
      <div className="navbar-inner">
        {/* Logo */}
        <Link to="/" className="navbar-logo">
          <span className="logo-icon">🎬</span>
          <span className="logo-text">Cine<span className="logo-ai">AI</span></span>
        </Link>

        {/* Desktop Nav Links */}
        <div className="navbar-links">
          <NavLink to="/" end className={({isActive}) => `nav-link${isActive?' active':''}`}>Home</NavLink>
          <NavLink to="/explore" className={({isActive}) => `nav-link${isActive?' active':''}`}>Explore</NavLink>
          <NavLink to="/mood" className={({isActive}) => `nav-link nav-link-mood${isActive?' active':''}`}>⚡ Mood Match</NavLink>
          {isAuthenticated && (
            <>
              <NavLink to="/watchlist" className={({isActive}) => `nav-link${isActive?' active':''}`}>Watchlist</NavLink>
              <NavLink to="/favorites" className={({isActive}) => `nav-link${isActive?' active':''}`}>Favorites</NavLink>
            </>
          )}
          <NavLink to="/about" className={({isActive}) => `nav-link${isActive?' active':''}`}>About</NavLink>
          <NavLink to="/contact" className={({isActive}) => `nav-link${isActive?' active':''}`}>Contact</NavLink>
        </div>

        {/* Right Controls */}
        <div className="navbar-right">
          {isAuthenticated ? (
            <div className="user-menu" ref={dropRef}>
              <button className="user-avatar-btn" onClick={() => setDropdownOpen(!dropdownOpen)}>
                <span className="avatar-circle">{user?.username?.[0]?.toUpperCase() || 'U'}</span>
                <span className="user-name-text">{user?.username}</span>
              </button>
              {dropdownOpen && (
                <div className="user-dropdown">
                  <div className="dropdown-header">
                    <span className="avatar-circle avatar-lg">{user?.username?.[0]?.toUpperCase()}</span>
                    <div>
                      <p className="dropdown-name">{user?.username}</p>
                      <p className="dropdown-email">{user?.email}</p>
                    </div>
                  </div>
                  <div className="dropdown-divider" />
                  <Link to="/" className="dropdown-item" onClick={() => setDropdownOpen(false)}>
                    <FiHome size={15} /> Home
                  </Link>
                  <Link to="/explore" className="dropdown-item" onClick={() => setDropdownOpen(false)}>
                    <FiCompass size={15} /> Explore
                  </Link>
                  <Link to="/favorites" className="dropdown-item" onClick={() => setDropdownOpen(false)}>
                    <FiHeart size={15} /> Favorites
                  </Link>
                  <Link to="/watchlist" className="dropdown-item" onClick={() => setDropdownOpen(false)}>
                    <FiBookmark size={15} /> Watchlist
                  </Link>
                  <Link to="/profile" className="dropdown-item" onClick={() => setDropdownOpen(false)}>
                    <FiUser size={15} /> My Profile
                  </Link>
                  <Link to="/change-password" className="dropdown-item" onClick={() => setDropdownOpen(false)}>
                    <FiKey size={15} /> Change Password
                  </Link>
                  <div className="dropdown-divider" />
                  <button className="dropdown-item dropdown-logout" onClick={handleLogout}>
                    <FiLogOut size={15} /> Log Out
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="auth-buttons">
              <Link to="/" className="btn btn-ghost btn-sm nav-home-btn">
                <FiHome size={15} /> Home
              </Link>
              <Link to="/login" className="btn btn-ghost btn-sm">Login</Link>
              <Link to="/register" className="btn btn-primary btn-sm">Get Started</Link>
            </div>
          )}

          {/* Hamburger */}
          <button className="navbar-hamburger btn-ghost btn-icon" onClick={() => setMenuOpen(!menuOpen)}>
            {menuOpen ? <FiX size={22} /> : <FiMenu size={22} />}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {menuOpen && (
        <div className="mobile-menu">
          <NavLink to="/" end className="mobile-link" onClick={() => setMenuOpen(false)}>Home</NavLink>
          <NavLink to="/explore" className="mobile-link" onClick={() => setMenuOpen(false)}>Explore</NavLink>
          {isAuthenticated && (
            <>
              <NavLink to="/watchlist" className="mobile-link" onClick={() => setMenuOpen(false)}>Watchlist</NavLink>
              <NavLink to="/favorites" className="mobile-link" onClick={() => setMenuOpen(false)}>Favorites</NavLink>
              <NavLink to="/profile"   className="mobile-link" onClick={() => setMenuOpen(false)}>My Profile</NavLink>
            </>
          )}
          <NavLink to="/about" className="mobile-link" onClick={() => setMenuOpen(false)}>About</NavLink>
          <NavLink to="/contact" className="mobile-link" onClick={() => setMenuOpen(false)}>Contact</NavLink>
          {!isAuthenticated && (
            <div className="mobile-auth">
              <Link to="/login" className="btn btn-secondary" onClick={() => setMenuOpen(false)}>Login</Link>
              <Link to="/register" className="btn btn-primary" onClick={() => setMenuOpen(false)}>Get Started</Link>
            </div>
          )}
          {isAuthenticated && (
            <button className="btn btn-ghost mobile-link" style={{color:'var(--accent-secondary)'}} onClick={handleLogout}>
              <FiLogOut size={16} /> Log Out
            </button>
          )}
        </div>
      )}
    </nav>
  )
}
