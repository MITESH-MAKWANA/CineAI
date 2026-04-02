import { Link } from 'react-router-dom'
import {
  FiTarget, FiEye, FiInfo, FiLayers, FiCpu, FiCode,
  FiShield, FiFileText, FiMail, FiGlobe, FiBarChart2,
  FiDatabase, FiArrowRight, FiCheck
} from 'react-icons/fi'

const NAV_ITEMS = ['About','Mission','Vision','Project','Services','ML Models','Architecture','Terms','Privacy','Contact']

const SERVICES = [
  { icon:<FiCpu size={22}/>,       title:'AI Recommendations',   desc:'Personalized movie picks powered by collaborative and content-based machine learning models.' },
  { icon:<FiBarChart2 size={22}/>, title:'Sentiment Analysis',    desc:'NLP-powered real-time classification of user reviews into positive, negative, or neutral sentiment.' },
  { icon:<FiGlobe size={22}/>,     title:'Global Movie Catalogue',desc:'Access to 10,000+ movies from the TMDB dataset across all genres, languages, and eras.' },
  { icon:<FiShield size={22}/>,    title:'Watchlist & Favorites', desc:'Personal movie management — save, bookmark and organize your discoveries.' },
  { icon:<FiDatabase size={22}/>,  title:'Review Analytics',      desc:'Visual sentiment charts and community review statistics on each movie detail page.' },
  { icon:<FiCode size={22}/>,      title:'REST API',              desc:'FastAPI-powered backend with full JWT authentication and documented endpoints.' },
]

const ML_MODELS = [
  { name:'Collaborative Filtering',       acc:'—',    type:'Recommendation', color:'#e50914', desc:'Users with similar viewing histories get matched movie recommendations.' },
  { name:'TF-IDF + Logistic Regression',  acc:'89%',  type:'Sentiment NLP',  color:'#7c3aed', desc:'Review text is vectorized with TF-IDF and classified with logistic regression.' },
  { name:'VADER Sentiment Analysis',      acc:'85%',  type:'Rule-Based NLP', color:'#10b981', desc:'Dictionary-based valence-aware sentiment reasoning for real-time use.' },
  { name:'Content-Based Filtering',       acc:'—',    type:'Recommendation', color:'#4fc3f7', desc:'Genre, cast, director, and keywords are compared to find similar films.' },
]

const ARCH_LAYERS = [
  { layer:'Frontend',  tech:'React 18 + Vite + CSS Modules', color:'#4fc3f7', desc:'SPA with React Router, real-time search, responsive design.' },
  { layer:'Backend',   tech:'Python + FastAPI + Uvicorn',     color:'#10b981', desc:'REST API with JWT auth, SQLAlchemy ORM, background ML inference.' },
  { layer:'ML Engine', tech:'scikit-learn + NLTK + VADER',    color:'#7c3aed', desc:'Trained models persisted with joblib; real-time inference on review submission.' },
  { layer:'Database',  tech:'SQLite + SQLAlchemy',            color:'#f59e0b', desc:'Relational schema for users, reviews, watchlist, and favorites.' },
  { layer:'Data',      tech:'TMDB Dataset (tmdbmovies.csv)',  color:'#e50914', desc:'10,000+ movies with genres, overviews, ratings, posters.' },
]

export default function About() {
  const scrollTo = (id) => {
    const el = document.getElementById(id)
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  return (
    <div className="about-page">

      {/* Sticky side nav */}
      <nav className="about-sidenav">
        {NAV_ITEMS.map(n => (
          <button key={n} className="sidenav-btn" onClick={() => scrollTo(`section-${n.toLowerCase()}`)}>{n}</button>
        ))}
      </nav>

      <div className="about-main">

        {/* ── About ── */}
        <section id="section-about" className="about-section">
          <div className="section-eyebrow"><FiInfo size={14}/> About</div>
          <h1 className="about-h1">🎬 About CineAI</h1>
          <p className="about-lead">
            CineAI is an <strong>AI-powered movie discovery platform</strong> designed to transform
            how people find and experience films. Built as an academic capstone project, it combines
            modern web technologies with real machine learning to deliver personalized, intelligent
            movie recommendations.
          </p>
          <p className="about-p">
            The platform serves movie enthusiasts who want more than just a simple search engine.
            CineAI understands your taste, analyses audience sentiment, and curates content from a
            global database of over 10,000 films — automatically adapting to your preferences over time.
          </p>
          <div className="about-highlight-row">
            {[['10,000+','Movies in Database'],['89%','Sentiment Accuracy'],['4','ML Models'],['20+','Genre Categories']].map(([v,l],i) => (
              <div key={i} className="about-highlight">
                <div className="highlight-val">{v}</div>
                <div className="highlight-lbl">{l}</div>
              </div>
            ))}
          </div>
        </section>

        {/* ── Mission ── */}
        <section id="section-mission" className="about-section">
          <div className="section-eyebrow"><FiTarget size={14}/> Our Mission</div>
          <h2 className="about-h2">Our Mission</h2>
          <div className="mission-card">
            <div className="mission-icon">🎯</div>
            <div>
              <p className="about-lead" style={{marginBottom:'1rem'}}>
                "To make intelligent movie discovery accessible to everyone — turning data into
                personal cinematic experiences through the power of artificial intelligence."
              </p>
              <p className="about-p">
                We believe great films deserve to be found. CineAI's mission is to bridge the gap
                between a user's taste and the world's vast film library, using ML recommendation
                pipelines, NLP sentiment analysis, and an intuitive interface.
              </p>
            </div>
          </div>
        </section>

        {/* ── Vision ── */}
        <section id="section-vision" className="about-section">
          <div className="section-eyebrow"><FiEye size={14}/> Our Vision</div>
          <h2 className="about-h2">Our Vision</h2>
          <p className="about-p">
            We envision a future where discovering your next favourite film is as natural as having
            a conversation. CineAI aims to evolve from a recommendation engine into a full
            AI-driven cinematic companion — one that understands context, mood, and nuance.
          </p>
          <div className="vision-pillars">
            {[
              { icon:'🌐', title:'Global Reach',     desc:'Breaking language barriers to make world cinema discoverable.' },
              { icon:'🤖', title:'Smarter AI',        desc:'Continuously improving models that learn from user interactions.' },
              { icon:'🎭', title:'Deeper Insights',   desc:'Moving beyond ratings to emotional, contextual film understanding.' },
              { icon:'🔓', title:'Open & Accessible', desc:'Free, fast, and privacy-respecting for every movie lover.' },
            ].map((p,i) => (
              <div key={i} className="vision-pillar">
                <div className="vpillar-icon">{p.icon}</div>
                <h4 className="vpillar-title">{p.title}</h4>
                <p className="vpillar-desc">{p.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* ── Project Info ── */}
        <section id="section-project" className="about-section">
          <div className="section-eyebrow"><FiFileText size={14}/> Project Information</div>
          <h2 className="about-h2">Project Information</h2>
          <div className="info-table">
            {[
              ['Project Name',  'CineAI — AI-Powered Movie Discovery Platform'],
              ['Type',          'Full-Stack Web Application with Machine Learning'],
              ['Domain',        'Entertainment Technology / AI & Data Science'],
              ['Dataset',       'TMDB Movie Dataset (tmdbmovies.csv) — 10,000+ films'],
              ['Tech Stack',    'React, FastAPI, Python, SQLite, scikit-learn, NLTK'],
              ['ML Tasks',      'Recommendation, Sentiment Classification, NLP'],
              ['Auth',          'JWT Token-based Authentication'],
              ['API Standard',  'RESTful API with OpenAPI/Swagger documentation'],
            ].map(([k,v],i) => (
              <div key={i} className="info-row">
                <div className="info-key">{k}</div>
                <div className="info-val">{v}</div>
              </div>
            ))}
          </div>
        </section>

        {/* ── Services ── */}
        <section id="section-services" className="about-section">
          <div className="section-eyebrow"><FiLayers size={14}/> Services</div>
          <h2 className="about-h2">What CineAI Offers</h2>
          <div className="services-grid">
            {SERVICES.map((s,i) => (
              <div key={i} className="service-card">
                <div className="service-icon">{s.icon}</div>
                <h3 className="service-title">{s.title}</h3>
                <p className="service-desc">{s.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* ── ML Models ── */}
        <section id="section-ml" className="about-section">
          <div className="section-eyebrow"><FiCpu size={14}/> Machine Learning Models</div>
          <h2 className="about-h2">ML Models Used</h2>
          <p className="about-p" style={{marginBottom:'1.5rem'}}>
            CineAI uses four distinct ML models working in concert to deliver recommendations and sentiment intelligence:
          </p>
          <div className="ml-cards">
            {ML_MODELS.map((m,i) => (
              <div key={i} className="ml-about-card" style={{'--mc': m.color}}>
                <div className="ml-header">
                  <div className="ml-type-badge" style={{ background:`${m.color}20`, color:m.color }}>{m.type}</div>
                  {m.acc !== '—' && <div className="ml-acc" style={{ color:m.color }}>Accuracy: {m.acc}</div>}
                </div>
                <h3 className="ml-about-name">{m.name}</h3>
                <p className="ml-about-desc">{m.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* ── Architecture ── */}
        <section id="section-architecture" className="about-section">
          <div className="section-eyebrow"><FiCode size={14}/> Architecture</div>
          <h2 className="about-h2">System Architecture</h2>
          <p className="about-p" style={{marginBottom:'1.5rem'}}>
            CineAI follows a modern three-tier architecture: a React SPA frontend, a FastAPI REST API,
            and a SQLite database — all connected via JWT-authenticated HTTP calls.
          </p>
          <div className="arch-layers">
            {ARCH_LAYERS.map((l,i) => (
              <div key={i} className="arch-layer" style={{'--lc': l.color}}>
                <div className="arch-dot" style={{ background:l.color }} />
                <div className="arch-layer-content">
                  <div className="arch-layer-header">
                    <span className="arch-layer-name" style={{ color:l.color }}>{l.layer}</span>
                    <span className="arch-tech">{l.tech}</span>
                  </div>
                  <p className="arch-desc">{l.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* ── Terms ── */}
        <section id="section-terms" className="about-section">
          <div className="section-eyebrow"><FiFileText size={14}/> Terms</div>
          <h2 className="about-h2">Terms of Use</h2>
          <div className="terms-content">
            <p className="about-p">By using CineAI, you agree to the following terms:</p>
            <ul className="terms-list">
              <li>CineAI is an academic project for educational and demonstration purposes only.</li>
              <li>Movie data is sourced from TMDB and is subject to their respective licensing terms.</li>
              <li>User accounts and data are stored locally and used only to provide recommendations.</li>
              <li>You agree not to misuse the platform, including submitting harmful or false content.</li>
              <li>CineAI does not stream or provide access to any copyrighted film content.</li>
              <li>Accounts and all associated data may be deleted at any time for platform maintenance.</li>
              <li>Trailers are embedded via YouTube's standard embed API; we do not host any media.</li>
            </ul>
          </div>
        </section>

        {/* ── Privacy ── */}
        <section id="section-privacy" className="about-section">
          <div className="section-eyebrow"><FiShield size={14}/> Privacy</div>
          <h2 className="about-h2">Privacy Policy</h2>
          <div className="terms-content">
            <p className="about-p">We take your privacy seriously. Here is what we collect and why:</p>
            <div className="privacy-blocks">
              {[
                { title:'Data We Collect',   body:'Username, email address, hashed password, genre preferences, watchlist entries, and review submissions.' },
                { title:'How It\'s Used',    body:'Your data is used exclusively to provide personalized movie recommendations and sentiment feedback. We never sell data.' },
                { title:'Data Storage',      body:'All data is stored locally in a SQLite database. We use bcrypt hashing for passwords and JWT tokens for sessions.' },
                { title:'Third Parties',     body:'Poster images are loaded from TMDB\'s CDN. Trailers are embedded via YouTube. No tracking cookies are used.' },
                { title:'Your Rights',       body:'You may request deletion of your account and all associated data by contacting us via the Contact page.' },
              ].map((b,i) => (
                <div key={i} className="privacy-block">
                  <h4 className="privacy-title">{b.title}</h4>
                  <p className="privacy-body">{b.body}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── Contact ── */}
        <section id="section-contact" className="about-section">
          <div className="section-eyebrow"><FiMail size={14}/> Contact</div>
          <h2 className="about-h2">Get In Touch</h2>
          <p className="about-p" style={{marginBottom:'1.5rem'}}>
            Have questions, feedback, or want to contribute to CineAI? Reach out through any of the channels below.
          </p>
          <div className="contact-options">
            <div className="contact-card">
              <div className="contact-icon"><FiMail size={24} color="var(--accent-primary)"/></div>
              <h3 className="contact-title">Email</h3>
              <p className="contact-body">For general questions and feedback</p>
              <a href="mailto:contact@cineai.dev" className="contact-link">contact@cineai.dev</a>
            </div>
            <div className="contact-card">
              <div className="contact-icon">🌐</div>
              <h3 className="contact-title">Contact Form</h3>
              <p className="contact-body">Use our dedicated contact page</p>
              <Link to="/contact" className="btn btn-primary" style={{marginTop:'0.5rem', display:'inline-flex', gap:8, alignItems:'center'}}>
                Go to Contact <FiArrowRight size={15}/>
              </Link>
            </div>
          </div>
        </section>

      </div>

      <style>{`
        .about-page { display: flex; gap: 2rem; min-height: 100vh; padding-top: calc(var(--navbar-height) + 2rem); max-width: 1200px; margin: 0 auto; padding-left: 1rem; padding-right: 1rem; padding-bottom: 5rem; }

        /* Side nav */
        .about-sidenav { position: sticky; top: calc(var(--navbar-height) + 1.5rem); align-self: flex-start; width: 160px; flex-shrink: 0; display: flex; flex-direction: column; gap: 4px; }
        .sidenav-btn { background: none; border: none; text-align: left; padding: 7px 10px; border-radius: var(--radius-sm); color: var(--text-muted); font-size: 0.8rem; cursor: pointer; transition: var(--transition); white-space: nowrap; }
        .sidenav-btn:hover { background: rgba(255,255,255,0.06); color: var(--text-primary); }

        /* Main */
        .about-main { flex: 1; display: flex; flex-direction: column; gap: 0; }
        .about-section { padding: 3rem 0; border-bottom: 1px solid var(--border-subtle); }
        .about-section:last-child { border-bottom: none; }
        .section-eyebrow { display: inline-flex; align-items: center; gap: 6px; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: var(--accent-primary); margin-bottom: 0.5rem; }
        .about-h1 { font-size: clamp(1.75rem, 4vw, 2.5rem); font-weight: 900; margin-bottom: 1rem; }
        .about-h2 { font-size: clamp(1.35rem, 3vw, 1.9rem); font-weight: 800; margin-bottom: 1rem; }
        .about-lead { font-size: 1.05rem; color: var(--text-primary); line-height: 1.7; margin-bottom: 0.75rem; }
        .about-lead strong { color: var(--accent-secondary); }
        .about-p { font-size: 0.92rem; color: var(--text-secondary); line-height: 1.75; margin-bottom: 0.5rem; }

        /* Highlights */
        .about-highlight-row { display: flex; gap: 1.5rem; flex-wrap: wrap; margin-top: 1.75rem; }
        .about-highlight { background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: var(--radius-lg); padding: 1rem 1.5rem; text-align: center; min-width: 110px; }
        .highlight-val { font-size: 1.5rem; font-weight: 900; color: var(--accent-primary); }
        .highlight-lbl { font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.06em; margin-top: 2px; }

        /* Mission */
        .mission-card { display: flex; gap: 1.5rem; align-items: flex-start; background: var(--bg-card); border: 1px solid var(--border-medium); border-radius: var(--radius-xl); padding: 2rem; }
        .mission-icon { font-size: 2.5rem; flex-shrink: 0; }

        /* Vision */
        .vision-pillars { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px,1fr)); gap: 1rem; margin-top: 1.5rem; }
        .vision-pillar { background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: var(--radius-lg); padding: 1.5rem; text-align: center; transition: var(--transition); }
        .vision-pillar:hover { transform: translateY(-4px); border-color: rgba(229,9,20,0.3); }
        .vpillar-icon { font-size: 1.75rem; margin-bottom: 0.5rem; }
        .vpillar-title { font-size: 0.9rem; font-weight: 700; margin-bottom: 0.35rem; }
        .vpillar-desc { font-size: 0.78rem; color: var(--text-secondary); line-height: 1.5; }

        /* Info table */
        .info-table { border: 1px solid var(--border-medium); border-radius: var(--radius-lg); overflow: hidden; }
        .info-row { display: grid; grid-template-columns: 160px 1fr; gap: 1rem; padding: 0.875rem 1.25rem; border-bottom: 1px solid var(--border-subtle); }
        .info-row:last-child { border-bottom: none; }
        .info-row:nth-child(even) { background: rgba(255,255,255,0.02); }
        .info-key { font-size: 0.78rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.04em; }
        .info-val { font-size: 0.875rem; color: var(--text-primary); }

        /* Services */
        .services-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px,1fr)); gap: 1.1rem; }
        .service-card { background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: var(--radius-lg); padding: 1.5rem; transition: var(--transition); }
        .service-card:hover { border-color: rgba(229,9,20,0.3); transform: translateY(-4px); box-shadow: 0 12px 30px rgba(0,0,0,0.25); }
        .service-icon { color: var(--accent-primary); margin-bottom: 0.75rem; }
        .service-title { font-size: 0.95rem; font-weight: 700; margin-bottom: 0.35rem; }
        .service-desc { font-size: 0.82rem; color: var(--text-secondary); line-height: 1.55; }

        /* ML models */
        .ml-cards { display: flex; flex-direction: column; gap: 1rem; }
        .ml-about-card { background: var(--bg-card); border: 1px solid var(--border-subtle); border-left: 3px solid var(--mc); border-radius: var(--radius-lg); padding: 1.25rem 1.5rem; transition: var(--transition); }
        .ml-about-card:hover { box-shadow: 0 8px 25px rgba(0,0,0,0.2); }
        .ml-header { display: flex; align-items: center; gap: 12px; margin-bottom: 0.5rem; }
        .ml-type-badge { font-size: 0.68rem; font-weight: 700; padding: 3px 10px; border-radius: var(--radius-full); text-transform: uppercase; letter-spacing: 0.05em; }
        .ml-acc { font-size: 0.75rem; font-weight: 700; }
        .ml-about-name { font-size: 1rem; font-weight: 700; margin-bottom: 0.3rem; }
        .ml-about-desc { font-size: 0.85rem; color: var(--text-secondary); line-height: 1.55; }

        /* Architecture */
        .arch-layers { display: flex; flex-direction: column; gap: 0; }
        .arch-layer { display: flex; gap: 1.25rem; align-items: flex-start; padding: 1.25rem; border-radius: var(--radius-md); transition: var(--transition); position: relative; }
        .arch-layer::before { content: ''; position: absolute; left: 20px; top: 50px; width: 2px; height: calc(100% - 20px); background: linear-gradient(var(--lc, #888), transparent); opacity: 0.3; }
        .arch-layer:last-child::before { display: none; }
        .arch-layer:hover { background: rgba(255,255,255,0.02); }
        .arch-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; margin-top: 5px; box-shadow: 0 0 10px currentColor; }
        .arch-layer-content { flex: 1; }
        .arch-layer-header { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 0.3rem; }
        .arch-layer-name { font-weight: 800; font-size: 0.9rem; }
        .arch-tech { font-size: 0.78rem; color: var(--text-muted); background: var(--bg-secondary); padding: 2px 10px; border-radius: var(--radius-full); }
        .arch-desc { font-size: 0.82rem; color: var(--text-secondary); line-height: 1.5; }

        /* Terms */
        .terms-content { background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: var(--radius-lg); padding: 1.5rem; }
        .terms-list { list-style: none; display: flex; flex-direction: column; gap: 10px; margin-top: 0.75rem; }
        .terms-list li { display: flex; align-items: flex-start; gap: 10px; font-size: 0.875rem; color: var(--text-secondary); line-height: 1.55; }
        .terms-list li::before { content: '✓'; color: var(--accent-primary); font-weight: 700; flex-shrink: 0; margin-top: 2px; }

        /* Privacy */
        .privacy-blocks { display: flex; flex-direction: column; gap: 1rem; margin-top: 0.75rem; }
        .privacy-block { background: var(--bg-secondary); border-radius: var(--radius-md); padding: 1rem 1.25rem; }
        .privacy-title { font-size: 0.875rem; font-weight: 700; margin-bottom: 0.35rem; color: var(--text-primary); }
        .privacy-body { font-size: 0.825rem; color: var(--text-secondary); line-height: 1.55; }

        /* Contact */
        .contact-options { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px,1fr)); gap: 1.25rem; }
        .contact-card { background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: var(--radius-xl); padding: 1.75rem; text-align: center; transition: var(--transition); }
        .contact-card:hover { border-color: rgba(229,9,20,0.3); transform: translateY(-4px); box-shadow: 0 15px 35px rgba(0,0,0,0.25); }
        .contact-icon { font-size: 1.75rem; margin-bottom: 0.75rem; display: flex; justify-content: center; }
        .contact-title { font-size: 1rem; font-weight: 700; margin-bottom: 0.25rem; }
        .contact-body { font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.75rem; }
        .contact-link { color: var(--accent-secondary); font-size: 0.85rem; font-weight: 600; text-decoration: underline; text-underline-offset: 3px; }

        @media (max-width: 768px) {
          .about-sidenav { display: none; }
          .about-page { flex-direction: column; }
          .mission-card { flex-direction: column; }
          .info-row { grid-template-columns: 1fr; gap: 2px; }
          .info-key { color: var(--accent-primary); }
        }
      `}</style>
    </div>
  )
}
