import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { toast } from 'react-hot-toast'
import { FiUser, FiMail, FiLock, FiEye, FiEyeOff, FiArrowRight } from 'react-icons/fi'

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ username: '', email: '', password: '', confirm: '' })
  const [showPass, setShowPass] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => setForm(p => ({ ...p, [e.target.name]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.username || !form.email || !form.password) return toast.error('Please fill all fields')
    if (form.password !== form.confirm) return toast.error('Passwords do not match')
    if (form.password.length < 8)              return toast.error('Password must be at least 8 characters')
    if (!/[A-Z]/.test(form.password))          return toast.error('Password needs an uppercase letter')
    if (!/[a-z]/.test(form.password))          return toast.error('Password needs a lowercase letter')
    if (!/[0-9]/.test(form.password))          return toast.error('Password needs at least one number')
    if (!/[^A-Za-z0-9]/.test(form.password))   return toast.error('Password needs a special character')
    setLoading(true)
    try {
      await register(form.username, form.email, form.password)
      toast.success('Account created! Let\'s personalise your experience 🎬')
      navigate('/onboarding', { replace: true })
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Registration failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const strength = form.password.length === 0 ? 0 : form.password.length < 6 ? 1 : form.password.length < 10 ? 2 : 3
  const strengthLabel = ['', 'Weak', 'Good', 'Strong'][strength]
  const strengthColor = ['', '#e50914', '#f5c518', '#10b981'][strength]

  return (
    <div className="auth-page">
      <div className="auth-bg-orbs">
        <div className="auth-orb auth-orb-1" />
        <div className="auth-orb auth-orb-2" />
      </div>

      <div className="auth-card">
        <div className="auth-logo">
          <Link to="/">🎬 Cine<span style={{color:'var(--accent-primary)'}}>AI</span></Link>
        </div>

        <div className="auth-header">
          <h1 className="auth-title">Create Account</h1>
          <p className="auth-subtitle">Join CineAI and discover movies made for you</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form" id="register-form">
          <div className="form-group">
            <label className="form-label" htmlFor="reg-username">Username</label>
            <div className="input-wrap">
              <FiUser className="input-icon" size={17} />
              <input id="reg-username" type="text" name="username" value={form.username}
                onChange={handleChange} placeholder="coolmovielover" className="form-input input-with-icon" required />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="reg-email">Email Address</label>
            <div className="input-wrap">
              <FiMail className="input-icon" size={17} />
              <input id="reg-email" type="email" name="email" value={form.email}
                onChange={handleChange} placeholder="you@example.com" className="form-input input-with-icon" required />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="reg-password">Password</label>
            <div className="input-wrap">
              <FiLock className="input-icon" size={17} />
              <input id="reg-password" type={showPass ? 'text' : 'password'} name="password" value={form.password}
                onChange={handleChange} placeholder="Min 8 chars, uppercase, number, symbol" className="form-input input-with-icon" required />
              <button type="button" className="input-toggle" onClick={() => setShowPass(!showPass)}>
                {showPass ? <FiEyeOff size={16} /> : <FiEye size={16} />}
              </button>
            </div>
            {form.password && (
              <div className="strength-wrap">
                <div className="strength-bar">
                  {[1,2,3].map(level => (
                    <div key={level} className="strength-seg" style={{ background: strength >= level ? strengthColor : 'var(--border-medium)' }} />
                  ))}
                </div>
                <span style={{ fontSize: '0.72rem', color: strengthColor }}>{strengthLabel}</span>
              </div>
            )}
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="reg-confirm">Confirm Password</label>
            <div className="input-wrap">
              <FiLock className="input-icon" size={17} />
              <input id="reg-confirm" type="password" name="confirm" value={form.confirm}
                onChange={handleChange} placeholder="Repeat password" className="form-input input-with-icon" required />
            </div>
          </div>

          <button type="submit" className="btn btn-primary btn-login" id="register-submit-btn" disabled={loading}>
            {loading ? <span className="btn-spinner" /> : <><span>Create Account</span><FiArrowRight size={17}/></>}
          </button>
        </form>

        <p className="auth-switch">
          Already have an account? <Link to="/login" className="auth-link">Login</Link>
        </p>
      </div>

      <style>{`
        .auth-page {
          min-height: 100vh;
          display: flex; align-items: center; justify-content: center;
          padding: calc(var(--navbar-height) + 2rem) 1rem 3rem;
          position: relative; overflow: hidden;
        }
        .auth-bg-orbs { position: absolute; inset: 0; pointer-events: none; overflow: hidden; }
        .auth-orb { position: absolute; border-radius: 50%; filter: blur(80px); animation: gradientShift 10s ease infinite; }
        .auth-orb-1 { width: 350px; height: 350px; top: -10%; left: -10%; background: rgba(229,9,20,0.1); }
        .auth-orb-2 { width: 250px; height: 250px; bottom: 0; right: 0; background: rgba(124,58,237,0.08); animation-delay: 3s; }
        .auth-card {
          position: relative; width: 100%; max-width: 440px;
          background: var(--bg-card); border: 1px solid var(--border-medium);
          border-radius: var(--radius-xl); padding: 2.5rem 2rem;
          box-shadow: var(--shadow-lg); animation: fadeIn 0.5s ease;
        }
        .auth-logo { text-align: center; font-family: var(--font-display); font-size: 1.4rem; font-weight: 800; margin-bottom: 1.75rem; }
        .auth-logo a { text-decoration: none; color: var(--text-primary); }
        .auth-header { text-align: center; margin-bottom: 1.75rem; }
        .auth-title { font-size: 1.6rem; font-weight: 800; margin-bottom: 0.35rem; }
        .auth-subtitle { color: var(--text-muted); font-size: 0.9rem; }
        .auth-form { display: flex; flex-direction: column; gap: 1rem; margin-bottom: 1.25rem; }
        .input-wrap { position: relative; }
        .input-icon { position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: var(--text-muted); pointer-events: none; }
        .input-with-icon { padding-left: 42px !important; }
        .input-toggle { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); background: none; border: none; color: var(--text-muted); cursor: pointer; padding: 4px; transition: var(--transition); }
        .input-toggle:hover { color: var(--text-primary); }
        .strength-wrap { display: flex; align-items: center; gap: 8px; margin-top: 6px; }
        .strength-bar { display: flex; gap: 4px; flex: 1; }
        .strength-seg { height: 4px; flex: 1; border-radius: 2px; transition: background 0.3s; }
        .btn-login { width: 100%; justify-content: center; margin-top: 0.25rem; padding: 14px; font-size: 1rem; }
        .btn-spinner { width: 20px; height: 20px; border: 2px solid rgba(255,255,255,0.3); border-top-color: white; border-radius: 50%; animation: spinAnim 0.7s linear infinite; }
        .auth-switch { text-align: center; color: var(--text-muted); font-size: 0.875rem; }
        .auth-link { color: var(--accent-secondary); font-weight: 600; transition: var(--transition); }
        .auth-link:hover { color: var(--text-primary); }
        .auth-divider { display: flex; align-items: center; gap: 12px; color: var(--text-muted); font-size: 0.78rem; margin: 0.5rem 0; }
        .auth-divider::before, .auth-divider::after { content: ''; flex: 1; height: 1px; background: var(--border-medium); }
        .btn-google { width: 100%; display: flex; align-items: center; justify-content: center; gap: 10px; padding: 12px; background: white; border: 1px solid #ddd; border-radius: var(--radius-md); color: #333; font-size: 0.9rem; font-weight: 600; cursor: pointer; transition: box-shadow 0.2s; margin-bottom: 1rem; }
        .btn-google:hover { box-shadow: 0 2px 10px rgba(0,0,0,0.3); }
      `}</style>
    </div>
  )
}
