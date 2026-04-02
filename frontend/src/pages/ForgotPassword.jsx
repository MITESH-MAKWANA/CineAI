import { useState } from 'react'
import { Link } from 'react-router-dom'
import { toast } from 'react-hot-toast'
import { FiMail, FiArrowLeft, FiSend, FiCheckCircle } from 'react-icons/fi'
import api from '../api/axiosInstance'

export default function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [sent, setSent] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!email.trim()) return toast.error('Please enter your email')
    setLoading(true)
    try {
      await api.post('/auth/forgot-password', { email: email.trim() })
      setSent(true)
    } catch {
      // Still show success to prevent email enumeration
      setSent(true)
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

      <div className="auth-card">
        <div className="auth-logo">
          <Link to="/">🎬 Cine<span style={{ color: 'var(--accent-primary)' }}>AI</span></Link>
        </div>

        {!sent ? (
          <>
            <div className="auth-header">
              <h1 className="auth-title">Forgot Password?</h1>
              <p className="auth-subtitle">
                Enter your email and we'll send you a reset link.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="auth-form" id="forgot-password-form">
              <div className="form-group">
                <label className="form-label" htmlFor="forgot-email">Email Address</label>
                <div className="input-wrap">
                  <FiMail className="input-icon" size={17} />
                  <input
                    id="forgot-email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@example.com"
                    className="form-input input-with-icon"
                    autoComplete="email"
                    required
                  />
                </div>
              </div>

              <button type="submit" className="btn btn-primary btn-login" id="forgot-submit-btn" disabled={loading}>
                {loading
                  ? <span className="btn-spinner" />
                  : <><FiSend size={16} /><span>Send Reset Link</span></>
                }
              </button>
            </form>
          </>
        ) : (
          <div className="forgot-success">
            <div className="forgot-success-icon">
              <FiCheckCircle size={52} />
            </div>
            <h2 className="forgot-success-title">Check your email!</h2>
            <p className="forgot-success-body">
              If <strong>{email}</strong> is registered with CineAI, you will receive
              a password reset link shortly.
            </p>
            <p className="forgot-success-note">
              Didn't receive it? Check your spam folder.
            </p>
          </div>
        )}

        <div style={{ marginTop: '1.5rem', textAlign: 'center' }}>
          <Link to="/login" className="forgot-back-link">
            <FiArrowLeft size={14} /> Back to Login
          </Link>
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
        .auth-orb-1 { width: 350px; height: 350px; top: -10%; left: -10%; background: rgba(229,9,20,0.1); }
        .auth-orb-2 { width: 250px; height: 250px; bottom: 0; right: 0; background: rgba(124,58,237,0.08); animation-delay: 3s; }
        .auth-card {
          position: relative;
          width: 100%;
          max-width: 440px;
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
        .auth-subtitle { color: var(--text-muted); font-size: 0.9rem; line-height: 1.6; }
        .auth-form { display: flex; flex-direction: column; gap: 1.1rem; margin-bottom: 1.25rem; }
        .input-wrap { position: relative; }
        .input-icon { position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: var(--text-muted); pointer-events: none; }
        .input-with-icon { padding-left: 42px !important; }
        .btn-login { width: 100%; justify-content: center; padding: 14px; font-size: 1rem; gap: 10px; }
        .btn-spinner { width: 20px; height: 20px; border: 2px solid rgba(255,255,255,0.3); border-top-color: white; border-radius: 50%; animation: spinAnim 0.7s linear infinite; }

        .forgot-success { text-align: center; padding: 1rem 0; }
        .forgot-success-icon {
          color: #10b981;
          margin-bottom: 1.25rem;
          animation: scaleIn 0.4s ease;
        }
        .forgot-success-title { font-size: 1.4rem; font-weight: 800; margin-bottom: 0.75rem; }
        .forgot-success-body { color: var(--text-secondary); font-size: 0.9rem; line-height: 1.7; margin-bottom: 0.5rem; }
        .forgot-success-body strong { color: var(--text-primary); }
        .forgot-success-note { color: var(--text-muted); font-size: 0.8rem; }

        .forgot-back-link {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          color: var(--text-muted);
          font-size: 0.875rem;
          transition: var(--transition);
          text-decoration: none;
        }
        .forgot-back-link:hover { color: var(--accent-secondary); }
      `}</style>
    </div>
  )
}
