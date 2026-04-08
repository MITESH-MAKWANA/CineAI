import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../context/AuthContext'
import { toast } from 'react-hot-toast'
import { useNavigate } from 'react-router-dom'
import api from '../api/axiosInstance'
import { VIBES, fetchMoodMovies } from './MoodMatch'
import {
  FiKey, FiLogOut, FiCheck, FiZap
} from 'react-icons/fi'

const ALL_GENRES = [
  'Action','Adventure','Animation','Comedy','Crime','Documentary',
  'Drama','Family','Fantasy','History','Horror','Music','Mystery',
  'Romance','Science Fiction','Thriller','TV Movie','War','Western',
]

function PreferencesPanel({ user, onSaved }) {
  const { updateUserGenres } = useAuth()
  const [loved, setLoved]   = useState(() => (user.favorite_genres || '').split(',').filter(Boolean))
  const [skip, setSkip]     = useState(() => (user.skipped_genres  || '').split(',').filter(Boolean))
  const [saving, setSaving] = useState(false)

  const toggle = (list, setList, genre) =>
    setList(prev => prev.includes(genre) ? prev.filter(g => g !== genre) : [...prev, genre])

  const save = async () => {
    setSaving(true)
    try {
      await api.put('/auth/profile', {
        loved_genres:    loved,
        skipped_genres:  skip,
        onboarding_done: true,
      }, { _skipSessionExpiry: true })
      updateUserGenres(loved, skip)
      onSaved()
    } catch (err) {
      if (err.response?.status === 401) {
        toast.error('Session expired — please sign in again to save preferences.')
      } else {
        toast.error(err.response?.data?.detail || 'Failed to save preferences')
      }
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="prof-card">
      <h2 className="prof-section-title">Genre Preferences</h2>
      <p style={{color:'var(--text-muted)',fontSize:'0.875rem',marginBottom:'1.5rem'}}>
        Select genres to personalise your recommendations. Changes save instantly.
      </p>

      <div className="pref-section">
        <div className="pref-section-label">❤️ Genres You Love</div>
        <div className="pref-chips">
          {ALL_GENRES.map(g => (
            <button key={g}
              className={`pref-chip${loved.includes(g) ? ' pref-chip-love' : ''}`}
              onClick={() => toggle(loved, setLoved, g)}>
              {loved.includes(g) && <FiCheck size={12} />} {g}
            </button>
          ))}
        </div>
      </div>

      <div className="pref-section" style={{marginTop:'1.5rem'}}>
        <div className="pref-section-label">🚫 Genres to Skip <span style={{fontWeight:400,color:'var(--text-muted)'}}>(optional)</span></div>
        <div className="pref-chips">
          {ALL_GENRES.map(g => (
            <button key={g}
              className={`pref-chip${skip.includes(g) ? ' pref-chip-skip' : ''}`}
              onClick={() => toggle(skip, setSkip, g)}>
              {skip.includes(g) && <FiCheck size={12} />} {g}
            </button>
          ))}
        </div>
      </div>

      <div style={{marginTop:'1.75rem',display:'flex',gap:10,flexWrap:'wrap'}}>
        <button className="btn btn-primary" onClick={save} disabled={saving}>
          {saving ? 'Saving...' : '💾 Save Preferences'}
        </button>
        <button className="btn btn-secondary" onClick={() => { setLoved([]); setSkip([]) }}>
          Clear All
        </button>
      </div>

      <style>{`
        .pref-section-label { font-size:0.8rem; font-weight:700; text-transform:uppercase; letter-spacing:0.06em; color:var(--text-muted); margin-bottom:0.75rem; }
        .pref-chips { display:flex; flex-wrap:wrap; gap:7px; }
        .pref-chip { display:inline-flex; align-items:center; gap:5px; padding:5px 13px; border-radius:var(--radius-full); font-size:0.78rem; font-weight:600; border:1.5px solid var(--border-medium); background:var(--bg-secondary); color:var(--text-muted); cursor:pointer; transition:all 0.15s; }
        .pref-chip:hover { border-color:var(--text-secondary); color:var(--text-primary); }
        .pref-chip-love { background:rgba(229,9,20,0.12); border-color:rgba(229,9,20,0.4); color:var(--accent-secondary); }
        .pref-chip-skip { background:rgba(124,58,237,0.12); border-color:rgba(124,58,237,0.4); color:#a78bfa; }
      `}</style>
    </div>
  )
}

const TABS = [
  { id:'profile',   label:'Profile',    icon:'👤' },
  { id:'moodmatch', label:'Mood Match', icon:'⚡' },
  { id:'security',  label:'Security',   icon:'🔑' },
]

export default function Profile() {
  const { user, logout, updateUser } = useAuth()
  const navigate         = useNavigate()
  const [tab, setTab]    = useState('profile')
  const [ageVal, setAgeVal]     = useState('')
  const [genderVal, setGenderVal] = useState('')
  const [profileSaving, setProfileSaving] = useState(false)
  const [profileSaved, setProfileSaved]   = useState(false)

  // Mood Match state
  const [selectedMood, setSelectedMood]   = useState(null)
  const [moodMovies, setMoodMovies]       = useState([])
  const [moodLoading, setMoodLoading]     = useState(false)
  const [moodSearched, setMoodSearched]   = useState(false)

  if (!user) { navigate('/login'); return null }

  const lovedGenres   = (user.favorite_genres || '').split(',').filter(Boolean)
  const skippedGenres = (user.skipped_genres  || '').split(',').filter(Boolean)

  const saveProfileInfo = async () => {
    if (!ageVal) return toast.error('Please enter your age')
    if (!genderVal) return toast.error('Please select your gender')
    if (isNaN(ageVal) || +ageVal < 1 || +ageVal > 120)
      return toast.error('Please enter a valid age (1–120)')
    setProfileSaving(true)
    setProfileSaved(false)
    try {
      const payload = { age: parseInt(ageVal), gender: genderVal, onboarding_done: true }
      await api.put('/auth/profile', payload, { _skipSessionExpiry: true })
      updateUser({
        age:             parseInt(ageVal),
        gender:          genderVal,
        onboarding_done: true,
      })
      setProfileSaved(true)
      setAgeVal('')
      setGenderVal('')
      toast.success('Profile saved! Age and gender are now locked. 🔒')
    } catch (err) {
      if (err.response?.status === 401) {
        toast.error('Session expired — please sign in again to save your profile.')
      } else {
        toast.error(err.response?.data?.detail || 'Failed to save profile. Please try again.')
      }
    } finally {
      setProfileSaving(false)
    }
  }

  const findMoodMovies = async (vibeId) => {
    setSelectedMood(vibeId)
    setMoodLoading(true)
    setMoodSearched(false)
    try {
      const results = await fetchMoodMovies(vibeId, vibeId, [], 300)
      setMoodMovies(results)
      setMoodSearched(true)
    } catch { setMoodMovies([]) }
    finally { setMoodLoading(false); setMoodSearched(true) }
  }

  return (
    <div className="profile-page container">
      <div className="profile-layout">

        {/* ── Sidebar ── */}
        <aside className="profile-sidebar">
          <div className="profile-avatar-wrap">
            <div className="profile-avatar">
              {user.username?.[0]?.toUpperCase() || '?'}
            </div>
            <div className="profile-name">{user.username}</div>
            <div className="profile-email">{user.email}</div>
            {user.onboarding_done
              ? <div className="prof-badge green">✅ Setup Complete</div>
              : <div className="prof-badge red">⚠️ Setup Incomplete</div>
            }
          </div>

          <nav className="profile-nav">
            {TABS.map(t => (
              <button key={t.id} onClick={() => setTab(t.id)}
                className={`profile-nav-btn ${tab === t.id ? 'pnav-active' : ''}`}>
                <span>{t.icon}</span> {t.label}
              </button>
            ))}
            <div className="pnav-divider" />
            <button className="profile-nav-btn pnav-danger"
              onClick={() => { logout(); navigate('/') }}>
              <FiLogOut size={15}/> Sign Out
            </button>
          </nav>
        </aside>

        {/* ── Main ── */}
        <main className="profile-main">

          {/* ── Profile Tab ── */}
          {tab === 'profile' && (
            <div className="prof-card">
              <h2 className="prof-section-title">Profile Overview</h2>

              <div className="pinfo-grid">
                {[
                  ['👤','Username', user.username],
                  ['📧','Email',    user.email],
                  ['🎂','Age',      user.age || 'Not set'],
                  ['🏷️','Gender',   user.gender || 'Not set'],
                ].map(([em,label,val]) => (
                  <div key={label} className="pinfo-item">
                    <div className="pinfo-em">{em}</div>
                    <div>
                      <div className="pinfo-lbl">{label}</div>
                      <div className="pinfo-val">{val}</div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Age & Gender — one-time only */}
              {(user.age && user.gender) ? (
                // Already saved — locked permanently
                <div className="pinfo-locked">
                  <div style={{fontSize:'1.5rem'}}>🔒</div>
                  <div>
                    <div className="pinfo-lock-title">Profile information is locked</div>
                    <div className="pinfo-lock-sub">Age and gender can only be set once and cannot be changed.</div>
                  </div>
                </div>
              ) : (
                // Not yet set — show the one-time form
                <div className="pinfo-form">
                  <h3 className="pinfo-form-title">
                    ✏️ Update Profile
                    <span style={{fontSize:'0.72rem',color:'var(--text-muted)',fontWeight:400,marginLeft:8}}>(can only be set once)</span>
                  </h3>
                  <div className="pinfo-fields">
                    <div className="pinfo-field">
                      <label className="pinfo-field-label">🎂 Age</label>
                      <input
                        type="number" min="1" max="120"
                        className="pinfo-field-input"
                        placeholder="Enter your age"
                        value={ageVal}
                        onChange={e => { setAgeVal(e.target.value); setProfileSaved(false) }}
                      />
                    </div>
                    <div className="pinfo-field">
                      <label className="pinfo-field-label">🏷️ Gender</label>
                      <select
                        className="pinfo-field-input"
                        value={genderVal}
                        onChange={e => { setGenderVal(e.target.value); setProfileSaved(false) }}
                      >
                        <option value="">— Select gender —</option>
                        <option value="Male">Male</option>
                        <option value="Female">Female</option>
                        <option value="Non-binary">Non-binary</option>
                        <option value="Prefer not to say">Prefer not to say</option>
                      </select>
                    </div>
                  </div>
                  <button className="btn btn-primary" style={{marginTop:'1rem'}} onClick={saveProfileInfo} disabled={profileSaving}>
                    {profileSaving ? 'Saving...' : '💾 Save Changes'}
                  </button>
                  {profileSaved && (
                    <div className="pinfo-success-block">
                      <div className="pinfo-setup-done">✅ Profile locked and saved</div>
                    </div>
                  )}
                </div>
              )}

              {/* Genre Preferences — always editable */}
              <div style={{marginTop:'1.75rem'}}>
                <PreferencesPanel
                  user={user}
                  onSaved={() => toast.success('Genre preferences saved! 🎥')}
                />
              </div>

              {/* Start Exploring button */}
              <div style={{marginTop:'1.5rem', paddingTop:'1.5rem', borderTop:'1px solid var(--border-subtle)', textAlign:'center'}}>
                <p style={{color:'var(--text-muted)',fontSize:'0.8rem',marginBottom:'0.75rem'}}>
                  {user.favorite_genres ? '🎯 Your preferred genres will be highlighted on the Explore page.' : 'Select genres above to get personalised recommendations.'}
                </p>
                <button
                  className="btn btn-primary"
                  style={{padding:'13px 40px', fontSize:'1rem', letterSpacing:'0.02em'}}
                  onClick={() => navigate('/explore', { state: { genres: user.favorite_genres || '' } })}
                >
                  🎬 Start Exploring
                </button>
              </div>
            </div>
          )}

          {/* ── Mood Match Tab ── */}
          {tab === 'moodmatch' && (
            <div className="prof-card">
              <h2 className="prof-section-title"><FiZap size={18} color="#f97316" style={{verticalAlign:'middle',marginRight:8}}/>Mood Match</h2>
              <p style={{color:'var(--text-muted)',fontSize:'0.875rem',marginBottom:'1.5rem'}}>
                Select your current mood and we'll instantly recommend movies that match how you feel.
              </p>

              {/* Vibe picker */}
              <div className="pm-vibe-grid">
                {VIBES.map(v => (
                  <button key={v.id}
                    className={`pm-vibe-btn${selectedMood === v.id ? ' pm-vibe-active' : ''}`}
                    style={selectedMood === v.id ? { borderColor:v.color, background:`${v.color}15`, color:v.color } : {}}
                    onClick={() => findMoodMovies(v.id)}>
                    <span className="pm-vibe-emoji">{v.emoji}</span>
                    <span className="pm-vibe-label">{v.label}</span>
                  </button>
                ))}
              </div>

              {/* Loading */}
              {moodLoading && (
                <div className="pm-mm-loading">
                  <div className="pm-dots"><span /><span /><span /></div>
                  <p>Finding movies for your mood...</p>
                </div>
              )}

              {/* Results */}
              {!moodLoading && moodSearched && (
                <>
                  {moodMovies.length === 0 ? (
                    <div className="pm-mm-empty">No movies found for this mood. Try another!</div>
                  ) : (
                    <>
                      <div className="pm-mm-header">
                        <span style={{color: VIBES.find(v=>v.id===selectedMood)?.color, fontWeight:700}}>
                          {VIBES.find(v=>v.id===selectedMood)?.emoji} {VIBES.find(v=>v.id===selectedMood)?.label} Picks
                        </span>
                        <span style={{color:'var(--text-muted)',fontSize:'0.78rem'}}>{moodMovies.length} movies</span>
                      </div>
                      <div className="pm-movies-grid">
                        {moodMovies.map((m, i) => {
                          const poster = m.poster_path
                            ? `https://image.tmdb.org/t/p/w200${m.poster_path.startsWith('/')? '':'/'}${m.poster_path}`
                            : null
                          return (
                            <div key={m.id||i} className="pm-movie-card" onClick={() => navigate(`/movie/${m.id}`)}>
                              <div className="pm-poster-wrap">
                                {poster
                                  ? <img src={poster} alt={m.title} className="pm-poster" onError={e=>e.target.style.display='none'}/>
                                  : <div className="pm-no-poster">🎬</div>}
                                <div className="pm-card-hover">View →</div>
                              </div>
                              <p className="pm-card-title">{m.title}</p>
                              {m.vote_average > 0 && <p className="pm-card-rating">★ {parseFloat(m.vote_average).toFixed(1)}</p>}
                            </div>
                          )
                        })}
                      </div>
                    </>
                  )}
                </>
              )}

              <style>{`
                .pm-vibe-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(100px,1fr)); gap:8px; margin-bottom:1.5rem; }
                .pm-vibe-btn { display:flex; flex-direction:column; align-items:center; gap:4px; padding:12px 8px; border:1.5px solid var(--border-medium); border-radius:var(--radius-lg); background:var(--bg-secondary); cursor:pointer; transition:all 0.2s; color:var(--text-secondary); }
                .pm-vibe-btn:hover { border-color:var(--text-muted); transform:translateY(-2px); }
                .pm-vibe-active { transform:translateY(-3px) !important; box-shadow:0 6px 20px rgba(0,0,0,0.3); }
                .pm-vibe-emoji { font-size:1.5rem; line-height:1; }
                .pm-vibe-label { font-size:0.72rem; font-weight:700; }
                .pm-mm-loading { text-align:center; padding:2rem; color:var(--text-muted); }
                .pm-dots { display:flex; justify-content:center; gap:6px; margin-bottom:0.75rem; }
                .pm-dots span { width:8px; height:8px; border-radius:50%; background:var(--accent-primary); animation:mmBounce 0.9s ease infinite; }
                .pm-dots span:nth-child(2){animation-delay:0.15s;background:#f97316}
                .pm-dots span:nth-child(3){animation-delay:0.3s;background:#7c3aed}
                .pm-mm-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem; font-size:0.9rem; }
                .pm-mm-empty { text-align:center; padding:2rem; color:var(--text-muted); font-size:0.875rem; }
                .pm-movies-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(120px,1fr)); gap:0.85rem; }
                .pm-movie-card { cursor:pointer; border-radius:var(--radius-md); overflow:hidden; background:var(--bg-secondary); border:1px solid var(--border-subtle); transition:var(--transition); }
                .pm-movie-card:hover { transform:translateY(-4px); box-shadow:0 10px 28px rgba(0,0,0,0.4); border-color:rgba(229,9,20,0.3); }
                .pm-poster-wrap { position:relative; aspect-ratio:2/3; background:var(--bg-card); overflow:hidden; }
                .pm-poster { width:100%; height:100%; object-fit:cover; display:block; transition:transform 0.3s; }
                .pm-movie-card:hover .pm-poster { transform:scale(1.05); }
                .pm-no-poster { width:100%; height:100%; display:flex; align-items:center; justify-content:center; font-size:2rem; }
                .pm-card-hover { position:absolute; inset:0; background:rgba(10,10,15,0.7); display:flex; align-items:center; justify-content:center; font-size:0.75rem; font-weight:700; color:white; opacity:0; transition:opacity 0.3s; }
                .pm-movie-card:hover .pm-card-hover { opacity:1; }
                .pm-card-title { font-size:0.72rem; font-weight:700; padding:6px 7px 2px; overflow:hidden; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; color:var(--text-primary); }
                .pm-card-rating { font-size:0.65rem; font-weight:700; color:#f5c518; padding:0 7px 6px; }
              `}</style>
            </div>
          )}

          {/* ── Security Tab ── */}
          {tab === 'security' && (
            <div className="prof-card">
              <h2 className="prof-section-title">Security</h2>
              <div className="security-list">
                <div className="sec-item" onClick={() => navigate('/change-password')}>
                  <FiKey size={22} color="var(--accent-primary)"/>
                  <div>
                    <div className="sec-title">Change Password</div>
                    <div className="sec-sub">Update your current account password</div>
                  </div>
                  <span className="sec-arr">›</span>
                </div>
                <div className="sec-item sec-danger" onClick={() => { logout(); navigate('/') }}>
                  <FiLogOut size={22} color="#e50914"/>
                  <div>
                    <div className="sec-title">Sign Out</div>
                    <div className="sec-sub">Log out of your CineAI account</div>
                  </div>
                  <span className="sec-arr">›</span>
                </div>
              </div>
            </div>
          )}

        </main>
      </div>

      <style>{`
        .profile-page { padding-top: calc(var(--navbar-height) + 2rem); padding-bottom: 5rem; }
        .profile-layout { display: grid; grid-template-columns: 230px 1fr; gap: 1.75rem; align-items: flex-start; }

        /* Sidebar */
        .profile-sidebar { background: var(--bg-card); border: 1px solid var(--border-medium); border-radius: var(--radius-xl); padding: 1.5rem; position: sticky; top: calc(var(--navbar-height) + 1rem); }
        .profile-avatar-wrap { text-align: center; padding-bottom: 1.25rem; border-bottom: 1px solid var(--border-subtle); margin-bottom: 1rem; }
        .profile-avatar { width: 76px; height: 76px; border-radius: 50%; background: linear-gradient(135deg,#e50914,#7c3aed); display:flex; align-items:center; justify-content:center; font-size:2rem; font-weight:800; color:white; margin:0 auto 0.75rem; box-shadow:0 8px 24px rgba(229,9,20,0.3); }
        .profile-name { font-weight:800; font-size:1rem; margin-bottom:3px; }
        .profile-email { font-size:0.72rem; color:var(--text-muted); word-break:break-all; margin-bottom:6px; }
        .prof-badge { font-size:0.68rem; font-weight:700; }
        .prof-badge.green { color:#10b981; }
        .prof-badge.red   { color:#f59e0b; }

        .profile-nav { display:flex; flex-direction:column; gap:3px; }
        .profile-nav-btn { display:flex; align-items:center; gap:10px; padding:9px 12px; border:none; border-radius:var(--radius-md); background:none; color:var(--text-secondary); font-size:0.875rem; font-weight:600; cursor:pointer; transition:var(--transition); text-align:left; }
        .profile-nav-btn:hover { background:rgba(255,255,255,0.06); color:var(--text-primary); }
        .pnav-active { background:rgba(229,9,20,0.1) !important; color:var(--accent-secondary) !important; }
        .pnav-divider { height:1px; background:var(--border-subtle); margin:8px 0; }
        .pnav-danger { color:#e50914 !important; }
        .pnav-danger:hover { background:rgba(229,9,20,0.08) !important; }

        /* Main */
        .profile-main { min-width:0; }
        .prof-card { background:var(--bg-card); border:1px solid var(--border-medium); border-radius:var(--radius-xl); padding:2rem; animation:fadeIn 0.3s ease; }
        .prof-section-title { font-size:1.2rem; font-weight:800; margin-bottom:1.25rem; }

        /* Info grid */
        .pinfo-grid { display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-bottom:1.5rem; }
        .pinfo-item { display:flex; gap:12px; align-items:center; background:var(--bg-secondary); border-radius:var(--radius-lg); padding:1rem; }
        .pinfo-em { font-size:1.4rem; flex-shrink:0; }
        .pinfo-lbl { font-size:0.68rem; text-transform:uppercase; letter-spacing:0.06em; color:var(--text-muted); font-weight:700; }
        .pinfo-val { font-size:0.9rem; font-weight:600; color:var(--text-primary); margin-top:2px; }

        /* Genre pills */
        .pgenre-block { margin-bottom:1rem; }
        .pgenre-title { font-size:0.83rem; font-weight:700; color:var(--text-secondary); margin-bottom:7px; }
        .gpills { display:flex; flex-wrap:wrap; gap:6px; }
        .gpill { padding:4px 12px; border-radius:var(--radius-full); font-size:0.73rem; font-weight:600; }
        .gpill.love { background:rgba(229,9,20,0.12); color:var(--accent-secondary); }
        .gpill.skip { background:rgba(124,58,237,0.12); color:#a78bfa; }

        /* Setup prompt */
        .psetup-prompt { display:flex; align-items:center; gap:1rem; margin-top:1.5rem; background:rgba(229,9,20,0.06); border:1px solid rgba(229,9,20,0.2); border-radius:var(--radius-lg); padding:1.25rem; flex-wrap:wrap; }
        .psetup-title { font-weight:700; margin-bottom:3px; }
        .psetup-body { font-size:0.8rem; color:var(--text-muted); }

        /* Security */
        .security-list { display:flex; flex-direction:column; gap:8px; }
        .sec-item { display:flex; align-items:center; gap:1rem; padding:1.1rem 1.25rem; background:var(--bg-secondary); border-radius:var(--radius-lg); cursor:pointer; transition:var(--transition); }
        .sec-item:hover { transform:translateX(4px); }
        .sec-danger:hover { background:rgba(229,9,20,0.07); }
        .sec-title { font-weight:700; font-size:0.875rem; }
        .sec-sub { font-size:0.75rem; color:var(--text-muted); }
        .sec-arr { margin-left:auto; font-size:1.25rem; color:var(--text-muted); }

        /* Age/Gender form */
        .pinfo-form { margin-top:1.5rem; background:var(--bg-secondary); border-radius:var(--radius-lg); padding:1.25rem; border:1px solid var(--border-subtle); }
        .pinfo-form-title { font-size:0.88rem; font-weight:700; margin-bottom:1rem; color:var(--text-primary); }
        .pinfo-fields { display:grid; grid-template-columns:1fr 1fr; gap:0.85rem; }
        .pinfo-field { display:flex; flex-direction:column; gap:5px; }
        .pinfo-field-label { font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; color:var(--text-muted); }
        .pinfo-field-input { background:var(--bg-card); border:1.5px solid var(--border-medium); border-radius:var(--radius-md); padding:9px 13px; color:var(--text-primary); font-size:0.875rem; outline:none; transition:border-color 0.2s; width:100%; }
        .pinfo-field-input:focus { border-color:var(--accent-primary); }
        .pinfo-setup-done { display:inline-flex; align-items:center; gap:7px; padding:8px 16px; background:rgba(16,185,129,0.12); border:1px solid rgba(16,185,129,0.3); border-radius:var(--radius-full); color:#10b981; font-size:0.82rem; font-weight:700; animation:fadeIn 0.3s ease; }
        .pinfo-success-block { display:flex; flex-direction:column; align-items:flex-start; gap:0.5rem; margin-top:0.75rem; }
        .pinfo-locked { display:flex; align-items:center; gap:1rem; margin-top:1.5rem; background:rgba(16,185,129,0.06); border:1px solid rgba(16,185,129,0.2); border-radius:var(--radius-lg); padding:1rem 1.25rem; }
        .pinfo-lock-title { font-size:0.875rem; font-weight:700; color:#10b981; margin-bottom:2px; }
        .pinfo-lock-sub { font-size:0.75rem; color:var(--text-muted); }

        @media (max-width:768px) {
          .profile-layout { grid-template-columns:1fr; }
          .profile-sidebar { position:static; }
          .pinfo-grid { grid-template-columns:1fr; }
          .pinfo-fields { grid-template-columns:1fr; }
        }
      `}</style>
    </div>
  )
}
