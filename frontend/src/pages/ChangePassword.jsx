import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { toast } from 'react-hot-toast'
import { FiLock, FiEye, FiEyeOff, FiArrowLeft, FiCheck } from 'react-icons/fi'
import api from '../api/axiosInstance'

export default function ChangePassword() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ current_password: '', new_password: '', confirm_password: '' })
  const [show, setShow] = useState({ current: false, new: false, confirm: false })
  const [loading, setLoading] = useState(false)

  const toggle = (field) => setShow(p => ({ ...p, [field]: !p[field] }))
  const handleChange = (e) => setForm(p => ({ ...p, [e.target.name]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.current_password || !form.new_password || !form.confirm_password)
      return toast.error('Please fill all fields')
    if (form.new_password.length < 6)
      return toast.error('New password must be at least 6 characters')
    if (form.new_password !== form.confirm_password)
      return toast.error('New passwords do not match')
    if (form.current_password === form.new_password)
      return toast.error('New password must be different from current password')

    setLoading(true)
    try {
      await api.put('/auth/change-password', {
        current_password: form.current_password,
        new_password:     form.new_password,
      }, { _skipSessionExpiry: true })
      toast.success('Password changed successfully! 🔑')
      setTimeout(() => navigate('/profile'), 1500)
    } catch (err) {
      if (err.response?.status === 401) {
        toast.error('Session expired — please log in again to change your password.')
      } else {
        toast.error(err.response?.data?.detail || 'Failed to change password')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-bg-orbs">
        <div className="auth-orb auth-orb-1" />
        <div className="auth-orb auth-orb-2" />
      </div>

      <div className="auth-card" style={{ maxWidth: '460px' }}>
        <div className="auth-logo">
          <Link to="/">🎬 Cine<span style={{ color: 'var(--accent-primary)' }}>AI</span></Link>
        </div>

        <div className="auth-header">
          <h1 className="auth-title">Change Password</h1>
          <p className="auth-subtitle">Update your account password below</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form" id="change-password-form">

          {/* Current Password */}
          <div className="form-group">
            <label className="form-label" htmlFor="cp-current">Current Password</label>
            <div className="input-wrap">
              <FiLock className="input-icon" size={17} />
              <input
                id="cp-current"
                type={show.current ? 'text' : 'password'}
                name="current_password"
                value={form.current_password}
                onChange={handleChange}
                placeholder="Your current password"
                className="form-input input-with-icon"
                autoComplete="current-password"
              />
              <button type="button" className="input-toggle" onClick={() => toggle('current')}>
                {show.current ? <FiEyeOff size={16} /> : <FiEye size={16} />}
              </button>
            </div>
          </div>

          {/* New Password */}
          <div className="form-group">
            <label className="form-label" htmlFor="cp-new">New Password</label>
            <div className="input-wrap">
              <FiLock className="input-icon" size={17} />
              <input
                id="cp-new"
                type={show.new ? 'text' : 'password'}
                name="new_password"
                value={form.new_password}
                onChange={handleChange}
                placeholder="Min. 6 characters"
                className="form-input input-with-icon"
                autoComplete="new-password"
              />
              <button type="button" className="input-toggle" onClick={() => toggle('new')}>
                {show.new ? <FiEyeOff size={16} /> : <FiEye size={16} />}
              </button>
            </div>
          </div>

          {/* Confirm New Password */}
          <div className="form-group">
            <label className="form-label" htmlFor="cp-confirm">Confirm New Password</label>
            <div className="input-wrap">
              <FiLock className="input-icon" size={17} />
              <input
                id="cp-confirm"
                type={show.confirm ? 'text' : 'password'}
                name="confirm_password"
                value={form.confirm_password}
                onChange={handleChange}
                placeholder="Repeat new password"
                className="form-input input-with-icon"
                autoComplete="new-password"
              />
              <button type="button" className="input-toggle" onClick={() => toggle('confirm')}>
                {show.confirm ? <FiEyeOff size={16} /> : <FiEye size={16} />}
              </button>
            </div>
            {/* Match indicator */}
            {form.confirm_password && (
              <p style={{
                fontSize: '0.78rem',
                marginTop: '5px',
                color: form.new_password === form.confirm_password ? '#10b981' : '#e50914'
              }}>
                {form.new_password === form.confirm_password ? '✓ Passwords match' : '✗ Passwords do not match'}
              </p>
            )}
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-login"
            id="change-password-submit"
            disabled={loading}
          >
            {loading
              ? <span className="btn-spinner" />
              : <><FiCheck size={17} /><span>Update Password</span></>
            }
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '0.75rem' }}>
          <button
            className="forgot-back-link"
            onClick={() => navigate(-1)}
            style={{ background: 'none', border: 'none', cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: 6 }}
          >
            <FiArrowLeft size={14} /> Go Back
          </button>
        </div>
      </div>

      <style>{`
        .auth-page {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: calc(var(--navbar-height) + 2rem) 1rem 3rem;
          position: relative;
          overflow: hidden;
        }
        .auth-bg-orbs { position: absolute; inset: 0; pointer-events: none; overflow: hidden; }
        .auth-orb { position: absolute; border-radius: 50%; filter: blur(80px); animation: gradientShift 10s ease infinite; }
        .auth-orb-1 { width: 350px; height: 350px; top: -10%; left: -10%; background: rgba(124,58,237,0.1); }
        .auth-orb-2 { width: 250px; height: 250px; bottom: 0; right: 0; background: rgba(229,9,20,0.08); animation-delay: 3s; }
        .auth-card {
          position: relative;
          width: 100%;
          background: var(--bg-card);
          border: 1px solid var(--border-medium);
          border-radius: var(--radius-xl);
          padding: 2.5rem 2rem;
          box-shadow: var(--shadow-lg);
          animation: fadeIn 0.5s ease;
        }
        .auth-logo { text-align: center; font-family: var(--font-display); font-size: 1.4rem; font-weight: 800; margin-bottom: 1.75rem; }
        .auth-logo a { text-decoration: none; color: var(--text-primary); }
        .auth-header { text-align: center; margin-bottom: 1.75rem; }
        .auth-title { font-size: 1.6rem; font-weight: 800; margin-bottom: 0.35rem; }
        .auth-subtitle { color: var(--text-muted); font-size: 0.9rem; }
        .auth-form { display: flex; flex-direction: column; gap: 1.1rem; margin-bottom: 1rem; }
        .input-wrap { position: relative; }
        .input-icon { position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: var(--text-muted); pointer-events: none; }
        .input-with-icon { padding-left: 42px !important; }
        .input-toggle { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); background: none; border: none; color: var(--text-muted); cursor: pointer; padding: 4px; transition: var(--transition); }
        .input-toggle:hover { color: var(--text-primary); }
        .btn-login { width: 100%; justify-content: center; padding: 14px; font-size: 1rem; gap: 10px; }
        .btn-spinner { width: 20px; height: 20px; border: 2px solid rgba(255,255,255,0.3); border-top-color: white; border-radius: 50%; animation: spinAnim 0.7s linear infinite; }
        .forgot-back-link { color: var(--text-muted); font-size: 0.875rem; transition: var(--transition); text-decoration: none; }
        .forgot-back-link:hover { color: var(--accent-secondary); }
      `}</style>
    </div>
  )
}
