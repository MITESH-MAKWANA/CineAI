import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import {
  FiArrowRight, FiCpu, FiSearch, FiGlobe, FiMessageSquare,
  FiDatabase, FiShield, FiCheck, FiBarChart2, FiActivity, FiLayers, FiUser
} from 'react-icons/fi'

const FEATURES = [
  {
    icon: '🤖',
    svgColor: '#e50914',
    title: 'AI Recommendations',
    desc: 'Personalized movie picks powered by collaborative and content-based machine learning models that learn your taste over time.',
  },
  {
    icon: '🔍',
    svgColor: '#4fc3f7',
    title: 'Smart Search & Filters',
    desc: 'Find movies by title, genre, release year, rating, and language. Instantly search across 10,000+ films from our TMDB dataset.',
  },
  {
    icon: '💬',
    svgColor: '#7c3aed',
    title: 'Sentiment Analysis',
    desc: 'NLP-driven emotion analysis classifies your reviews as Positive, Negative, or Neutral using VADER and TF-IDF + Logistic Regression.',
  },
  {
    icon: '🌍',
    svgColor: '#10b981',
    title: 'Global Film Catalogue',
    desc: 'Explore Hollywood, Bollywood, anime, K-drama, European and world cinema — all indexed in CineAI\'s intelligent database.',
  },
  {
    icon: '📊',
    svgColor: '#f59e0b',
    title: 'Review Analytics',
    desc: 'Visual sentiment charts (bar + donut) show real community opinion distribution for every single film on the platform.',
  },
  {
    icon: '🔖',
    svgColor: '#ec4899',
    title: 'Watchlist & Favorites',
    desc: 'Save movies to your personal watchlist and mark favourites with one click. Access them anytime from your profile.',
  },
]

const ML_MODELS = [
  {
    emoji: '🧠',
    name: 'Collaborative Filtering',
    type: 'Recommendation',
    color: '#e50914',
    desc: 'Matches users with similar viewing preferences. If two people loved the same 10 movies, they\'ll likely enjoy each other\'s picks.',
  },
  {
    emoji: '📊',
    name: 'TF-IDF + Logistic Regression',
    type: 'Sentiment NLP',
    color: '#7c3aed',
    desc: 'Vectorizes review text using Term Frequency-Inverse Document Frequency, then classifies it. Achieves 89% accuracy on the test set.',
  },
  {
    emoji: '🎭',
    name: 'VADER Sentiment Engine',
    type: 'Rule-Based NLP',
    color: '#10b981',
    desc: 'Valence Aware Dictionary and sEntiment Reasoner — a dictionary-based model optimised for real-time social-media style text.',
  },
  {
    emoji: '🔮',
    name: 'Content-Based Filtering',
    type: 'Recommendation',
    color: '#4fc3f7',
    desc: 'Compares genres, cast, director, and keyword metadata to surface films with high similarity scores to ones you already love.',
  },
]

const TECH_STACK = [
  { bg:'#61dafb22', color:'#61dafb', emoji:'⚛️',  name:'React 18 + Vite',     label:'Frontend' },
  { bg:'#059669220', color:'#10b981', emoji:'🐍', name:'FastAPI + Python',     label:'Backend' },
  { bg:'#f5c51822', color:'#f5c518', emoji:'🗄️',  name:'SQLite + SQLAlchemy', label:'Database' },
  { bg:'#f59e0b22', color:'#f59e0b', emoji:'🤖',  name:'scikit-learn + NLTK', label:'ML / NLP' },
  { bg:'#e5091422', color:'#e50914', emoji:'🎬',  name:'TMDB Movie Dataset',  label:'Data Source' },
  { bg:'#7c3aed22', color:'#a78bfa', emoji:'🔐',  name:'JWT + bcrypt',       label:'Security' },
]

const STATS = [
  { value:'10,000+', label:'Movies in Dataset', emoji:'🎬' },
  { value:'89%',     label:'Sentiment Accuracy', emoji:'🧠' },
  { value:'4',       label:'ML Models',          emoji:'🤖' },
  { value:'20+',     label:'Genre Categories',   emoji:'🎭' },
]

const MODEL_PIE_DATA = [
  { label: 'Sentiment Accuracy',     pct: 89, color: '#10b981' },
  { label: 'Dataset Coverage',        pct: 95, color: '#4fc3f7' },
  { label: 'Recommendation Hit Rate', pct: 82, color: '#7c3aed' },
  { label: 'Genre Classification',    pct: 91, color: '#f59e0b' },
]

function ModelPieChart() {
  const cx = 80, cy = 80, r = 60, inner = 36
  const total = MODEL_PIE_DATA.reduce((s, d) => s + d.pct, 0)
  let cumulative = 0
  const slices = MODEL_PIE_DATA.map(d => {
    const start = cumulative / total * 2 * Math.PI - Math.PI / 2
    cumulative += d.pct
    const end = cumulative / total * 2 * Math.PI - Math.PI / 2
    const x1 = cx + r * Math.cos(start), y1 = cy + r * Math.sin(start)
    const x2 = cx + r * Math.cos(end),   y2 = cy + r * Math.sin(end)
    const ix1= cx + inner * Math.cos(start), iy1 = cy + inner * Math.sin(start)
    const ix2= cx + inner * Math.cos(end),   iy2 = cy + inner * Math.sin(end)
    const large = (end - start) > Math.PI ? 1 : 0
    return { ...d, path: `M${x1},${y1} A${r},${r} 0 ${large} 1 ${x2},${y2} L${ix2},${iy2} A${inner},${inner} 0 ${large} 0 ${ix1},${iy1} Z` }
  })
  return (
    <div className="pie-wrap">
      <svg width="160" height="160" viewBox="0 0 160 160" className="pie-svg-c">
        {slices.map((s,i) => (
          <path key={i} d={s.path} fill={s.color} opacity="0.92">
            <animate attributeName="opacity" from="0" to="0.92" dur="0.6s" begin={`${i*0.15}s`} fill="freeze"/>
          </path>
        ))}
        <circle cx={cx} cy={cy} r={inner-2} fill="var(--bg-card)"/>
        <text x={cx} y={cy-6} textAnchor="middle" fill="var(--text-primary)" fontSize="13" fontWeight="800">89%</text>
        <text x={cx} y={cy+10} textAnchor="middle" fill="var(--text-muted)" fontSize="9">Accuracy</text>
      </svg>
      <div className="pie-legend">
        {MODEL_PIE_DATA.map((d,i) => (
          <div key={i} className="pie-leg-row">
            <div className="pie-leg-dot" style={{ background: d.color }}/>
            <span className="pie-leg-lbl">{d.label}</span>
            <span className="pie-leg-pct" style={{ color: d.color }}>{d.pct}%</span>
          </div>
        ))}
      </div>
    </div>
  )
}


export default function Home() {
  const { isAuthenticated } = useAuth()
  const navigate = useNavigate()

  const handleGetStarted = () => navigate(isAuthenticated ? '/explore' : '/register')

  return (
    <div className="home">

      {/* ── Hero ── */}
      <section className="hero">
        <div className="hero-orbs">
          <div className="horb h1"/><div className="horb h2"/><div className="horb h3"/>
        </div>
        <div className="hero-inner container">
          <div className="hero-badge">
            <FiCpu size={13}/> AI-Powered Movie Discovery
          </div>

          <h1 className="hero-h1">
            🎬 Smart Movie<br/>
            <span className="hero-grad">Discovery</span> Starts Here
          </h1>

          <p className="hero-sub">
            Find films that match your taste with AI recommendations, sentiment analysis,
            and a global catalogue of 10,000+ movies — all in one place.
          </p>

          <div className="hero-ctas">
            <button className="btn btn-primary btn-lg" id="hero-get-started" onClick={handleGetStarted}>
              Get Started Free <FiArrowRight size={18}/>
            </button>
            <Link to="/login" className="btn btn-secondary btn-lg" id="hero-sign-in">Sign In</Link>
          </div>

          <div className="hero-explore-hint">
            <Link to="/explore" className="hint-link">Or browse without an account → Explore Movies</Link>
          </div>

          <div className="stats-row">
            {STATS.map((s,i) => (
              <div key={i} className="stat-box">
                <div className="stat-em">{s.emoji}</div>
                <div className="stat-val">{s.value}</div>
                <div className="stat-lbl">{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Core Features ── */}
      <section className="section-block container">
        <div className="sec-eyebrow">Core Features</div>
        <h2 className="sec-h2">Everything you need to<br/><span className="red-text">love movies more</span></h2>
        <p className="sec-lead">Six powerful tools working together to personalise your cinematic experience.</p>

        <div className="features-grid-2col">
          {FEATURES.map((f,i) => (
            <div key={i} className="feat-card" style={{'--fc': f.svgColor}}>
              <div className="feat-icon-wrap" style={{ background:`${f.svgColor}18`, borderColor:`${f.svgColor}30` }}>
                <span className="feat-emoji">{f.icon}</span>
              </div>
              <h3 className="feat-title">{f.title}</h3>
              <p className="feat-desc">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── ML Models ── */}
      <section className="section-band">
        <div className="container">
          <div className="sec-eyebrow">Machine Learning Models Used</div>
          <h2 className="sec-h2">Powered by Cutting-Edge AI</h2>
          <p className="sec-lead">Four distinct ML models working in concert to deliver recommendations and sentiment intelligence.</p>

          <div className="ml-grid">
            {ML_MODELS.map((m,i) => (
              <div key={i} className="ml-card" style={{'--mc': m.color}}>
                <div className="ml-top">
                  <div className="ml-emoji-wrap" style={{ background:`${m.color}15` }}>
                    <span className="ml-emoji">{m.emoji}</span>
                  </div>
                  <div>
                    <span className="ml-type-tag" style={{ background:`${m.color}18`, color:m.color }}>{m.type}</span>
                  </div>
                </div>
                <h3 className="ml-name">{m.name}</h3>
                <p className="ml-desc">{m.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Data Intelligence ── */}
      <section className="section-block container">
        <div className="data-split">
          <div className="data-left">
            <div className="sec-eyebrow">Data Intelligence</div>
            <h2 className="sec-h2">Global Movie Dataset<br/>+ Sentiment Intelligence</h2>
            <p className="data-body">
              CineAI is powered by the <strong>TMDB Global Movie Dataset</strong> — one of the most
              comprehensive film databases in the world, spanning 10,000+ movies across all genres,
              languages, and decades. Our NLP sentiment engine achieves <strong>89% accuracy</strong> on
              independent test sets.
            </p>
            <ul className="data-list">
              {[
                '10,000+ movies from TMDB global dataset',
                '89% sentiment classification accuracy (TF-IDF + Logistic Regression)',
                'VADER rule-based real-time review analysis',
                'Multi-genre filtering: 20+ curated categories',
                'Collaborative + content-based hybrid recommendations',
              ].map((b,i) => (
                <li key={i}><FiCheck size={14} color="#10b981" style={{flexShrink:0}}/> {b}</li>
              ))}
            </ul>
          </div>
          <div className="data-right">
            <div className="data-visual-card">
              <div className="dvc-header">📊 Model Performance</div>
              <ModelPieChart />
              <div className="dvc-footer">🎓 Academic Research Project — TMDB Dataset</div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Platform / Tech Stack ── */}
      <section className="section-band">
        <div className="container">
          <div className="sec-eyebrow" style={{textAlign:'center',display:'block'}}>Platform</div>
          <h2 className="sec-h2" style={{textAlign:'center'}}>Built with Modern Technologies</h2>
          <p className="sec-lead" style={{textAlign:'center',maxWidth:560,margin:'0 auto 2.5rem'}}>
            CineAI combines a blazing-fast React frontend, a Python FastAPI backend, and
            production-grade machine learning models into one seamless experience.
          </p>
          <div className="tech-grid-2col">
            {TECH_STACK.map((t,i) => (
              <div key={i} className="tech-card" style={{'--tc': t.color}}>
                <div className="tech-icon-wrap" style={{ background:t.bg, borderColor:`${t.color}40` }}>
                  <span className="tech-emoji">{t.emoji}</span>
                </div>
                <div className="tech-name">{t.name}</div>
                <div className="tech-label" style={{ color:t.color }}>{t.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── How It Works ── */}
      <section className="section-block container">
        <div className="sec-eyebrow" style={{textAlign:'center',display:'block'}}>How It Works</div>
        <h2 className="sec-h2" style={{textAlign:'center'}}>Your AI Movie Journey in 3 Steps</h2>
        <div className="steps-row">
          {[
            { num:'01', emoji:'👤', title:'Create an Account', desc:'Register free in seconds. Set your age, gender, and favourite genre preferences during onboarding.' },
            { num:'02', emoji:'🤖', title:'AI Learns Your Taste', desc:'Our recommendation engine analyses your genre preferences and viewing patterns to surface films you\'ll love.' },
            { num:'03', emoji:'🎬', title:'Discover & Review', desc:'Explore AI-curated picks, add films to your watchlist, and get instant NLP sentiment analysis on your reviews.' },
          ].map((s,i) => (
            <div key={i} className="step-card">
              <div className="step-num">{s.num}</div>
              <div className="step-emoji">{s.emoji}</div>
              <h3 className="step-title">{s.title}</h3>
              <p className="step-desc">{s.desc}</p>
              {i < 2 && <div className="step-connector"/>}
            </div>
          ))}
        </div>
      </section>

      {/* ── Final CTA ── */}
      <section className="cta-section container">
        <div className="cta-inner">
          <div className="cta-orb"/>
          <h2 className="cta-title">Ready to find your next favourite movie?</h2>
          <p className="cta-sub">Join thousands of movie lovers discovering great content with AI.</p>
          <button className="btn btn-primary btn-lg" onClick={handleGetStarted}>
            Start Exploring Free <FiArrowRight size={18}/>
          </button>
        </div>
      </section>

      <style>{`
        .home { overflow-x: hidden; }

        /* Hero */
        .hero { position:relative; min-height:100vh; display:flex; align-items:center; padding:calc(var(--navbar-height) + 2rem) 0 4rem; overflow:hidden; }
        .hero-orbs { position:absolute; inset:0; overflow:hidden; pointer-events:none; }
        .horb { position:absolute; border-radius:50%; filter:blur(80px); animation:gradientShift 10s ease infinite; }
        .h1 { width:450px;height:450px;top:-10%;left:-5%;background:rgba(229,9,20,0.1); }
        .h2 { width:320px;height:320px;top:40%;right:5%;background:rgba(124,58,237,0.08);animation-delay:2s; }
        .h3 { width:260px;height:260px;bottom:5%;left:35%;background:rgba(79,195,247,0.07);animation-delay:4s; }
        .hero-inner { position:relative; z-index:2; }
        .hero-badge { display:inline-flex; align-items:center; gap:8px; padding:6px 16px; border-radius:var(--radius-full); background:rgba(229,9,20,0.12); border:1px solid rgba(229,9,20,0.3); color:var(--accent-secondary); font-size:0.78rem; font-weight:700; letter-spacing:0.05em; margin-bottom:1.5rem; }
        .hero-h1 { font-family:var(--font-display); font-size:clamp(2.5rem,6vw,5rem); font-weight:900; line-height:1.05; margin-bottom:1.25rem; letter-spacing:-0.02em; }
        .hero-grad { background:linear-gradient(135deg,#e50914,#ff6b6b,#ff9a3c); background-size:200% auto; -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; animation:gradientShift 4s ease infinite; }
        .hero-sub { font-size:clamp(1rem,2vw,1.15rem); color:var(--text-secondary); line-height:1.7; margin-bottom:2rem; max-width:600px; }
        .hero-ctas { display:flex; gap:14px; flex-wrap:wrap; margin-bottom:1.25rem; }
        .hint-link { color:var(--text-muted); font-size:0.875rem; text-decoration:underline; text-underline-offset:3px; transition:var(--transition); }
        .hint-link:hover { color:var(--accent-secondary); }

        /* Stats */
        .stats-row { display:flex; gap:2rem; flex-wrap:wrap; margin-top:2.5rem; }
        .stat-box { text-align:center; }
        .stat-em { font-size:1.3rem; margin-bottom:2px; }
        .stat-val { font-size:1.4rem; font-weight:900; }
        .stat-lbl { font-size:0.68rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.06em; font-weight:600; }

        /* Section helpers */
        .section-block { padding:5rem 0; }
        .section-band { background:var(--bg-secondary); padding:5rem 0; margin:0; }
        .sec-eyebrow { display:inline-block; font-size:0.7rem; font-weight:800; text-transform:uppercase; letter-spacing:0.14em; color:var(--accent-primary); margin-bottom:0.6rem; }
        .sec-h2 { font-size:clamp(1.5rem,3vw,2.4rem); font-weight:800; margin-bottom:0.75rem; line-height:1.2; }
        .sec-lead { color:var(--text-secondary); font-size:0.95rem; line-height:1.7; margin-bottom:2.5rem; max-width:640px; }
        .red-text { color:var(--accent-primary); }

        /* ── FEATURES ── */
        .features-grid-2col { display:grid; grid-template-columns:1fr 1fr; gap:1.5rem; }
        .feat-card { background:var(--bg-card); border:1px solid var(--border-subtle); border-radius:var(--radius-xl); padding:2rem 1.75rem; transition:var(--transition); position:relative; overflow:hidden; }
        .feat-card::before { content:''; position:absolute; inset:0; border-radius:inherit; border:1px solid transparent; transition:border-color 0.3s; }
        .feat-card:hover { transform:translateY(-8px); box-shadow:0 24px 50px rgba(0,0,0,0.35); }
        .feat-card:hover::before { border-color:var(--fc,var(--accent-primary)); }
        .feat-icon-wrap { width:72px; height:72px; border-radius:20px; border:1px solid transparent; display:flex; align-items:center; justify-content:center; margin-bottom:1.25rem; }
        .feat-emoji { font-size:2rem; line-height:1; }
        .feat-title { font-size:1.05rem; font-weight:800; margin-bottom:0.6rem; color:var(--text-primary); }
        .feat-desc { color:var(--text-secondary); font-size:0.86rem; line-height:1.65; }

        /* ── ML MODELS ── */
        .ml-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:1.25rem; }
        .ml-card { background:var(--bg-card); border:1px solid var(--border-subtle); border-left:3px solid var(--mc); border-radius:var(--radius-xl); padding:1.75rem; transition:var(--transition); }
        .ml-card:hover { transform:translateY(-5px); box-shadow:0 20px 40px rgba(0,0,0,0.3); border-color:var(--mc); }
        .ml-top { display:flex; align-items:center; gap:12px; margin-bottom:1rem; }
        .ml-emoji-wrap { width:52px; height:52px; border-radius:14px; display:flex; align-items:center; justify-content:center; font-size:1.6rem; flex-shrink:0; }
        .ml-emoji { line-height:1; }
        .ml-type-tag { font-size:0.68rem; font-weight:800; padding:3px 10px; border-radius:var(--radius-full); text-transform:uppercase; letter-spacing:0.06em; }
        .ml-name { font-size:1rem; font-weight:800; margin-bottom:0.5rem; }
        .ml-desc { font-size:0.85rem; color:var(--text-secondary); line-height:1.65; }

        /* ── DATA INTELLIGENCE ── */
        .data-split { display:grid; grid-template-columns:1fr 1fr; gap:4rem; align-items:center; }
        .data-body { color:var(--text-secondary); line-height:1.75; margin-bottom:1.25rem; font-size:0.92rem; }
        .data-body strong { color:var(--text-primary); }
        .data-list { list-style:none; display:flex; flex-direction:column; gap:10px; }
        .data-list li { display:flex; align-items:center; gap:10px; font-size:0.875rem; color:var(--text-secondary); }
        .data-visual-card { background:var(--bg-card); border:1px solid var(--border-medium); border-radius:var(--radius-xl); padding:1.75rem; }
        .dvc-header { font-size:0.9rem; font-weight:800; margin-bottom:1.25rem; }
        .dvc-row { margin-bottom:1rem; }
        .dvc-label { font-size:0.75rem; color:var(--text-muted); font-weight:600; margin-bottom:5px; }
        .dvc-bar-wrap { height:7px; background:rgba(255,255,255,0.07); border-radius:4px; overflow:hidden; margin-bottom:3px; }
        .dvc-bar { height:100%; border-radius:4px; transition:width 1.2s ease; }
        .dvc-pct { font-size:0.72rem; font-weight:800; text-align:right; }
        .dvc-footer { font-size:0.7rem; color:var(--text-muted); margin-top:1rem; text-align:center; }

        /* ── TECH STACK ── */
        .tech-grid-2col { display:grid; grid-template-columns:1fr 1fr; gap:1.25rem; }
        .tech-card { background:var(--bg-card); border:1px solid var(--border-subtle); border-radius:var(--radius-xl); padding:1.75rem 1.25rem; display:flex; align-items:center; gap:1rem; transition:var(--transition); cursor:default; text-align:left; }
        .tech-card:hover { transform:translateY(-4px); border-color:var(--tc,var(--accent-primary)); box-shadow:0 16px 40px rgba(0,0,0,0.3); }
        .tech-icon-wrap { width:54px; height:54px; border-radius:14px; border:1px solid; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
        .tech-emoji { font-size:1.6rem; line-height:1; }
        .tech-name { font-size:0.88rem; font-weight:800; color:var(--text-primary); margin-bottom:3px; }
        .tech-label { font-size:0.66rem; font-weight:800; text-transform:uppercase; letter-spacing:0.08em; }

        /* ── HOW IT WORKS ── */
        .steps-row { display:flex; gap:1.5rem; margin-top:0.5rem; position:relative; }
        .step-card { flex:1; text-align:center; background:var(--bg-card); border:1px solid var(--border-subtle); border-radius:var(--radius-xl); padding:2.25rem 1.5rem; position:relative; transition:var(--transition); }
        .step-card:hover { transform:translateY(-5px); box-shadow:0 20px 45px rgba(0,0,0,0.25); }
        .step-num { font-family:var(--font-display); font-size:3.5rem; font-weight:900; color:rgba(229,9,20,0.12); line-height:1; margin-bottom:0.4rem; }
        .step-emoji { font-size:2rem; margin-bottom:0.75rem; }
        .step-title { font-size:1.05rem; font-weight:800; margin-bottom:0.5rem; }
        .step-desc { color:var(--text-secondary); font-size:0.86rem; line-height:1.65; }
        .step-connector { position:absolute; top:45%; right:-1rem; width:2rem; height:2px; background:linear-gradient(to right,var(--accent-primary),transparent); }

        /* ── CTA ── */
        .cta-section { padding:4rem 0 6rem; }
        .cta-inner { position:relative; text-align:center; padding:4rem 2rem; border-radius:var(--radius-xl); overflow:hidden; background:linear-gradient(135deg,rgba(229,9,20,0.07),rgba(124,58,237,0.05)); border:1px solid rgba(229,9,20,0.18); }
        .cta-orb { position:absolute; width:350px; height:350px; border-radius:50%; background:radial-gradient(circle,rgba(229,9,20,0.13) 0%,transparent 70%); top:-50%; left:50%; transform:translateX(-50%); pointer-events:none; }
        .cta-title { font-size:clamp(1.5rem,3vw,2.5rem); font-weight:900; margin-bottom:1rem; position:relative; }
        .cta-sub { color:var(--text-secondary); margin-bottom:2rem; font-size:1rem; position:relative; }

        /* ── PIE CHART ── */
        .pie-wrap { display:flex; align-items:center; gap:1.5rem; margin-bottom:0.5rem; flex-wrap:wrap; }
        .pie-svg-c { flex-shrink:0; filter:drop-shadow(0 4px 16px rgba(0,0,0,0.5)); }
        .pie-legend { display:flex; flex-direction:column; gap:0.6rem; flex:1; min-width:150px; }
        .pie-leg-row { display:flex; align-items:center; gap:8px; }
        .pie-leg-dot { width:10px; height:10px; border-radius:50%; flex-shrink:0; }
        .pie-leg-lbl { font-size:0.75rem; color:var(--text-secondary); flex:1; }
        .pie-leg-pct { font-size:0.78rem; font-weight:800; }

        @media (max-width:960px) { .data-split { grid-template-columns:1fr; } }
        @media (max-width:700px) {
          .hero-ctas { flex-direction:column; }
          .hero-ctas .btn { width:100%; justify-content:center; }
          .stats-row { gap:1rem; }
          .steps-row { flex-direction:column; }
          .step-connector { display:none; }
          .features-grid-2col { grid-template-columns:1fr; }
          .tech-grid-2col { grid-template-columns:1fr; }
        }
      `}</style>
    </div>
  )
}
