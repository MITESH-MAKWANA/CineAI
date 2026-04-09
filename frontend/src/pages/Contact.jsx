import { useState } from 'react'
import { FiGithub, FiMail, FiTwitter, FiSend, FiMapPin } from 'react-icons/fi'
import { toast } from 'react-hot-toast'

export default function Contact() {
  const [form, setForm] = useState({ name: '', email: '', subject: '', message: '' })
  const [sending, setSending] = useState(false)

  const handleChange = e => setForm(p => ({ ...p, [e.target.name]: e.target.value }))

  const handleSubmit = async e => {
    e.preventDefault()
    if (!form.name || !form.email || !form.message) return toast.error('Please fill required fields')
    setSending(true)
    try {
      const API = import.meta.env.VITE_API_URL || 'https://cineai-ifyr.onrender.com'
      const res = await fetch(`${API}/contact`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      })
      if (!res.ok) throw new Error('Server error')
      toast.success("Message sent! We'll get back to you soon.")
      setForm({ name: '', email: '', subject: '', message: '' })
    } catch {
      toast.error('Failed to send. Please try again.')
    }
    setSending(false)
  }


  return (
    <div className="contact-page page-wrapper">
      <div className="container">
        {/* Header */}
        <div className="contact-hero">
          <div className="contact-badge">📞 Get In Touch</div>
          <h1 className="contact-title">We'd love to hear from you</h1>
          <p className="contact-subtitle">Have a question, suggestion, or just want to say hello? We're here.</p>
        </div>

        <div className="contact-layout">
          {/* Contact Info */}
          <div className="contact-info-col">
            <div className="contact-info-card card">
              <h2 className="contact-info-title">Connect With Us</h2>
              <div className="contact-links">
                <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="contact-link-item" id="github-link">
                  <div className="contact-link-icon" style={{ background: 'rgba(255,255,255,0.08)' }}>
                    <FiGithub size={22} />
                  </div>
                  <div>
                    <p className="contact-link-title">GitHub</p>
                    <p className="contact-link-sub">View the source code</p>
                  </div>
                </a>
                <a href="mailto:contact@cineai.com" className="contact-link-item" id="email-link">
                  <div className="contact-link-icon" style={{ background: 'rgba(229,9,20,0.12)', color: 'var(--accent-secondary)' }}>
                    <FiMail size={22} />
                  </div>
                  <div>
                    <p className="contact-link-title">Email</p>
                    <p className="contact-link-sub">contact@cineai.com</p>
                  </div>
                </a>
                <a href="https://twitter.com" target="_blank" rel="noopener noreferrer" className="contact-link-item" id="twitter-link">
                  <div className="contact-link-icon" style={{ background: 'rgba(79,195,247,0.12)', color: 'var(--accent-blue)' }}>
                    <FiTwitter size={22} />
                  </div>
                  <div>
                    <p className="contact-link-title">Twitter / X</p>
                    <p className="contact-link-sub">@CineAI_App</p>
                  </div>
                </a>
                <div className="contact-link-item">
                  <div className="contact-link-icon" style={{ background: 'rgba(16,185,129,0.12)', color: 'var(--accent-green)' }}>
                    <FiMapPin size={22} />
                  </div>
                  <div>
                    <p className="contact-link-title">Location</p>
                    <p className="contact-link-sub">India 🇮🇳</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="contact-faq card">
              <h3 className="faq-title">Quick Answers</h3>
              {[
                { q: 'Is CineAI free?', a: 'Yes! CineAI is completely free to use.' },
                { q: 'How accurate are recommendations?', a: 'Our TF-IDF model achieves ~90% user satisfaction based on genre affinity.' },
                { q: 'Can I suggest features?', a: 'Absolutely — send us your ideas via email or GitHub issues.' },
              ].map((faq, i) => (
                <div key={i} className="faq-item">
                  <p className="faq-q">{faq.q}</p>
                  <p className="faq-a">{faq.a}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Contact Form */}
          <div className="contact-form-col">
            <div className="contact-form-card card">
              <h2 className="form-card-title">Send a Message</h2>
              <form onSubmit={handleSubmit} className="contact-form" id="contact-form">
                <div className="form-row">
                  <div className="form-group">
                    <label className="form-label" htmlFor="contact-name">Your Name *</label>
                    <input id="contact-name" type="text" name="name" className="form-input" placeholder="John Doe" value={form.name} onChange={handleChange} required />
                  </div>
                  <div className="form-group">
                    <label className="form-label" htmlFor="contact-email">Email *</label>
                    <input id="contact-email" type="email" name="email" className="form-input" placeholder="you@example.com" value={form.email} onChange={handleChange} required />
                  </div>
                </div>
                <div className="form-group">
                  <label className="form-label" htmlFor="contact-subject">Subject</label>
                  <input id="contact-subject" type="text" name="subject" className="form-input" placeholder="Feature request, bug report..." value={form.subject} onChange={handleChange} />
                </div>
                <div className="form-group">
                  <label className="form-label" htmlFor="contact-message">Message *</label>
                  <textarea id="contact-message" name="message" className="form-input contact-textarea" placeholder="Write your message here..." value={form.message} onChange={handleChange} rows={6} required />
                </div>
                <button type="submit" className="btn btn-primary btn-submit-contact" disabled={sending} id="contact-submit-btn">
                  {sending ? (
                    <span className="btn-spinner" style={{ width: 20, height: 20, border: '2px solid rgba(255,255,255,0.3)', borderTopColor: 'white', borderRadius: '50%', animation: 'spinAnim 0.7s linear infinite', display: 'inline-block' }} />
                  ) : (
                    <><FiSend size={16} /> Send Message</>
                  )}
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        .contact-page { padding-bottom: 5rem; }
        .contact-hero { text-align: center; padding: 3rem 0 3rem; }
        .contact-badge { display: inline-block; padding: 6px 18px; margin-bottom: 1.25rem; background: rgba(229,9,20,0.12); border: 1px solid rgba(229,9,20,0.3); border-radius: var(--radius-full); color: var(--accent-secondary); font-size: 0.8rem; font-weight: 700; }
        .contact-title { font-size: clamp(1.75rem, 4vw, 2.75rem); font-weight: 900; margin-bottom: 0.75rem; }
        .contact-subtitle { color: var(--text-secondary); font-size: 1rem; }

        .contact-layout { display: grid; grid-template-columns: 1fr 1.6fr; gap: 1.5rem; }
        .contact-info-col { display: flex; flex-direction: column; gap: 1.25rem; }
        .contact-info-card { padding: 1.75rem; border-radius: var(--radius-xl); }
        .contact-info-title { font-size: 1.1rem; font-weight: 700; margin-bottom: 1.25rem; }
        .contact-links { display: flex; flex-direction: column; gap: 12px; }
        .contact-link-item { display: flex; align-items: center; gap: 14px; text-decoration: none; color: var(--text-primary); padding: 10px; border-radius: var(--radius-md); transition: var(--transition); }
        .contact-link-item:hover { background: rgba(255,255,255,0.04); }
        .contact-link-icon { width: 44px; height: 44px; border-radius: var(--radius-md); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
        .contact-link-title { font-size: 0.875rem; font-weight: 600; margin-bottom: 2px; }
        .contact-link-sub { font-size: 0.78rem; color: var(--text-muted); }

        .contact-faq { padding: 1.5rem; border-radius: var(--radius-xl); }
        .faq-title { font-size: 0.9rem; font-weight: 700; margin-bottom: 1rem; color: var(--text-secondary); }
        .faq-item { padding: 12px 0; border-bottom: 1px solid var(--border-subtle); }
        .faq-item:last-child { border-bottom: none; }
        .faq-q { font-size: 0.85rem; font-weight: 600; margin-bottom: 3px; }
        .faq-a { font-size: 0.8rem; color: var(--text-muted); line-height: 1.5; }

        .contact-form-card { padding: 2rem; border-radius: var(--radius-xl); }
        .form-card-title { font-size: 1.2rem; font-weight: 800; margin-bottom: 1.5rem; }
        .contact-form { display: flex; flex-direction: column; gap: 1.1rem; }
        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
        .contact-textarea { resize: vertical; min-height: 140px; font-family: inherit; line-height: 1.6; }
        .btn-submit-contact { width: 100%; justify-content: center; padding: 14px; font-size: 1rem; margin-top: 0.25rem; }

        @media (max-width: 850px) { .contact-layout { grid-template-columns: 1fr; } }
        @media (max-width: 500px) { .form-row { grid-template-columns: 1fr; } }
      `}</style>
    </div>
  )
}
