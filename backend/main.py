"""
CineAI - FastAPI Main Application Entry Point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from config import APP_NAME
from database import create_all_tables
from routes import auth, movies, recommendations, sentiment, watchlist, favorites
from routes import csv_movies
import os

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
ADMIN_SECRET    = os.getenv("ADMIN_SECRET", "cineai-admin-2024")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"[START] {APP_NAME} API starting up...")
    create_all_tables()
    try:
        from ml.sentiment_engine import SentimentEngine
        app.state.sentiment = SentimentEngine()
        print("[OK] Sentiment engine ready.")
    except Exception as e:
        print(f"[WARN] Sentiment engine startup: {e}")
    try:
        from ml.recommender_engine import RecommenderEngine
        app.state.recommender = RecommenderEngine()
        print("[OK] Recommender engine ready.")
    except Exception as e:
        print(f"[WARN] Recommender engine startup: {e}")
    yield
    print(f"[STOP] {APP_NAME} shutting down.")


app = FastAPI(
    title=f"{APP_NAME} API",
    description="AI-powered Movie Recommendation & Sentiment Analysis Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(movies.router)
app.include_router(recommendations.router)
app.include_router(sentiment.router)
app.include_router(watchlist.router)
app.include_router(favorites.router)
app.include_router(csv_movies.router)


@app.get("/", tags=["Health"])
def root():
    return {"app": APP_NAME, "status": "running", "version": "1.0.0", "docs": "/docs"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy", "app": APP_NAME}


# ── Admin Login page HTML ──────────────────────────────────────────────────────
def _login_page(msg=""):
    return HTMLResponse(f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>CineAI Admin</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Segoe UI',sans-serif;background:#0f0f1a;color:#e2e8f0;
     display:flex;align-items:center;justify-content:center;min-height:100vh}}
.card{{background:#1e1e3a;border:1px solid #2d2d50;border-radius:16px;padding:48px 40px;
      text-align:center;width:380px;box-shadow:0 20px 60px rgba(0,0,0,.5)}}
.logo{{font-size:44px;margin-bottom:12px}}
h1{{font-size:22px;font-weight:700;margin-bottom:6px}}
.sub{{color:#94a3b8;font-size:13px;margin-bottom:28px;min-height:20px}}
.err{{color:#f87171;font-size:13px}}
input{{width:100%;padding:13px 16px;background:#0f0f1a;border:1px solid #4c1d95;
      border-radius:10px;color:#e2e8f0;font-size:15px;margin-bottom:16px;outline:none;
      letter-spacing:2px}}
input:focus{{border-color:#a78bfa;box-shadow:0 0 0 3px rgba(167,139,250,.15)}}
button{{width:100%;padding:13px;background:linear-gradient(135deg,#6c3ef4,#e040fb);
       color:#fff;border:none;border-radius:10px;font-size:15px;font-weight:600;
       cursor:pointer;transition:.2s}}
button:hover{{opacity:.88;transform:translateY(-1px)}}
</style></head><body>
<div class="card">
  <div class="logo">🎬</div>
  <h1>CineAI Admin Panel</h1>
  <p class="sub">{msg if msg else 'Live database viewer &mdash; restricted access'}</p>
  <form onsubmit="go(event)">
    <input type="password" id="k" placeholder="Enter admin key..." autofocus/>
    <button type="submit">🔓 Open Dashboard</button>
  </form>
</div>
<script>
function go(e){{e.preventDefault();
  var k=document.getElementById('k').value.trim();
  if(k) window.location.href='/admin?key='+encodeURIComponent(k);
}}
</script></body></html>""")


# ── Admin Dashboard ────────────────────────────────────────────────────────────
@app.get("/admin", response_class=HTMLResponse, tags=["Admin"])
def admin_dashboard(key: str = Query(default="")):
    if not key:
        return _login_page()
    if key != ADMIN_SECRET:
        return _login_page('<span class="err">❌ Wrong key — try again</span>')

    from sqlalchemy.orm import Session
    from database import SessionLocal
    from models.user import User
    from models.watchlist import WatchlistItem, FavoriteItem
    from models.review import Review

    db: Session = SessionLocal()
    try:
        users     = db.query(User).order_by(User.id).all()
        watchlist = db.query(WatchlistItem).order_by(WatchlistItem.id).all()
        favorites = db.query(FavoriteItem).order_by(FavoriteItem.id).all()
        reviews   = db.query(Review).order_by(Review.id).all()
    finally:
        db.close()

    def make_rows(data_rows):
        if not data_rows:
            return '<tr><td colspan="10" class="empty">No records yet</td></tr>'
        return "".join(
            "<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>"
            for r in data_rows
        )

    def make_panel(tid, headers, data_rows, search_hint):
        head = "".join(f"<th>{h}</th>" for h in headers)
        body = make_rows(data_rows)
        n    = len(data_rows)
        cols = list(range(len(headers)))   # search all columns
        return f"""
<div class="panel" id="panel-{tid}">
  <div class="toolbar">
    <div class="search-wrap">
      <span class="search-icon">🔍</span>
      <input class="search-box" id="srch-{tid}" type="text"
             placeholder="Search by {search_hint}..."
             oninput="doFilter('{tid}',{cols})"/>
    </div>
    <span class="rec-count" id="cnt-{tid}">{n} record{'s' if n!=1 else ''}</span>
  </div>
  <div class="tbl-wrap">
    <table>
      <thead><tr>{head}</tr></thead>
      <tbody id="body-{tid}">{body}</tbody>
    </table>
  </div>
</div>"""

    u_panel = make_panel("users",
        ["ID","Username","Email","Age","Gender","Genres"],
        [(u.id, u.username, u.email, u.age or "—", u.gender or "—",
          u.favorite_genres or "—") for u in users],
        "username, email, age, gender, genres")

    w_panel = make_panel("watchlist",
        ["ID","User ID","Movie ID","Movie Title"],
        [(w.id, w.user_id, w.movie_id, w.movie_title) for w in watchlist],
        "movie title")

    f_panel = make_panel("favorites",
        ["ID","User ID","Movie ID","Movie Title"],
        [(f.id, f.user_id, f.movie_id, f.movie_title) for f in favorites],
        "movie title")

    r_panel = make_panel("reviews",
        ["ID","User ID","Movie Title","Review","Sentiment"],
        [(r.id, r.user_id, r.movie_title,
          (r.review_text[:60]+"…") if len(r.review_text) > 60 else r.review_text,
          f'<span class="sent {r.sentiment}">{r.sentiment or "—"}</span>')
         for r in reviews],
        "movie title, sentiment")

    return HTMLResponse(f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CineAI Admin Dashboard</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Segoe UI',system-ui,sans-serif;background:#0d0d1a;color:#e2e8f0;min-height:100vh}}
/* Header */
header{{background:linear-gradient(120deg,#4c1d95,#6d28d9,#7e22ce);
        padding:16px 28px;display:flex;align-items:center;
        justify-content:space-between;box-shadow:0 4px 24px rgba(0,0,0,.5)}}
.h-title{{font-size:20px;font-weight:700;display:flex;align-items:center;gap:10px}}
.h-sub{{font-size:12px;opacity:.7;margin-top:3px}}
.h-actions{{display:flex;gap:10px;align-items:center}}
.pill{{background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.2);
       border-radius:30px;padding:5px 14px;font-size:12px;font-weight:600}}
.btn{{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.18);
      color:#fff;padding:7px 14px;border-radius:8px;text-decoration:none;
      font-size:13px;transition:.15s;cursor:pointer}}
.btn:hover{{background:rgba(255,255,255,.2)}}
/* Stat cards */
.stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;padding:20px 28px}}
.stat{{background:#13132a;border:1px solid #252545;border-radius:14px;
       padding:18px 20px;text-align:center;cursor:pointer;transition:.2s;
       position:relative;overflow:hidden}}
.stat::after{{content:'';position:absolute;bottom:0;left:0;right:0;height:3px;
              background:linear-gradient(90deg,#7c3aed,#db2777);opacity:0}}
.stat.active,.stat:hover{{border-color:#7c3aed;background:#18183a}}
.stat.active::after,.stat:hover::after{{opacity:1}}
.stat .num{{font-size:36px;font-weight:800;color:#a78bfa;line-height:1}}
.stat .lbl{{font-size:12px;color:#64748b;margin-top:6px;font-weight:500;text-transform:uppercase;letter-spacing:.5px}}
/* Tabs */
.tabs{{display:flex;padding:0 28px;border-bottom:1px solid #1e1e3f;gap:4px}}
.tab{{padding:12px 20px;font-size:14px;font-weight:500;color:#64748b;
      border-bottom:2px solid transparent;cursor:pointer;transition:.15s;
      border-radius:4px 4px 0 0;user-select:none}}
.tab:hover{{color:#c4b5fd;background:#ffffff08}}
.tab.active{{color:#c4b5fd;border-bottom-color:#7c3aed;background:#ffffff05}}
/* Panel */
.panel{{display:none;padding:20px 28px 36px}}
.panel.active{{display:block}}
/* Toolbar */
.toolbar{{display:flex;align-items:center;gap:12px;margin-bottom:16px}}
.search-wrap{{position:relative;flex:1;max-width:480px}}
.search-icon{{position:absolute;left:13px;top:50%;transform:translateY(-50%);
              font-size:14px;pointer-events:none}}
.search-box{{width:100%;padding:10px 14px 10px 38px;background:#13132a;
             border:1px solid #252545;border-radius:10px;color:#e2e8f0;
             font-size:14px;outline:none;transition:.2s}}
.search-box:focus{{border-color:#7c3aed;background:#18183a;
                   box-shadow:0 0 0 3px rgba(124,58,237,.2)}}
.rec-count{{font-size:13px;color:#475569;margin-left:auto;white-space:nowrap}}
/* Table */
.tbl-wrap{{overflow-x:auto;border-radius:12px;border:1px solid #1e1e3f}}
table{{width:100%;border-collapse:collapse;font-size:13.5px}}
thead{{background:#0d0d20}}
th{{padding:12px 16px;text-align:left;color:#7c3aed;font-weight:600;
    font-size:11px;text-transform:uppercase;letter-spacing:.6px;
    white-space:nowrap;position:sticky;top:0;background:#0d0d20}}
td{{padding:11px 16px;border-top:1px solid #1a1a35;color:#cbd5e1;
    white-space:nowrap;max-width:280px;overflow:hidden;text-overflow:ellipsis}}
tr:hover td{{background:#16163a}}
tr.hidden{{display:none}}
.empty{{text-align:center;color:#374151;padding:40px;font-size:14px}}
/* Sentiment */
.sent{{border-radius:20px;padding:3px 10px;font-size:11px;font-weight:700;
       text-transform:uppercase;letter-spacing:.4px}}
.sent.positive{{background:rgba(16,185,129,.12);color:#34d399;border:1px solid rgba(16,185,129,.2)}}
.sent.negative{{background:rgba(239,68,68,.12);color:#f87171;border:1px solid rgba(239,68,68,.2)}}
.sent.neutral{{background:rgba(148,163,184,.1);color:#94a3b8;border:1px solid rgba(148,163,184,.15)}}
footer{{text-align:center;padding:20px;color:#1e293b;font-size:12px;
        border-top:1px solid #131325;margin-top:8px}}
@media(max-width:640px){{
  .stats{{grid-template-columns:repeat(2,1fr)}}
  .toolbar{{flex-wrap:wrap}}
}}
</style></head><body>

<header>
  <div>
    <div class="h-title">🎬 CineAI Admin Dashboard</div>
    <div class="h-sub">Live PostgreSQL viewer — admin only</div>
  </div>
  <div class="h-actions">
    <span class="pill">🔒 Admin</span>
    <a class="btn" href="/admin?key={key}">🔄 Refresh</a>
  </div>
</header>

<div class="stats">
  <div class="stat active" id="st-users"     onclick="sw('users')">
    <div class="num">{len(users)}</div><div class="lbl">👤 Users</div>
  </div>
  <div class="stat" id="st-watchlist"  onclick="sw('watchlist')">
    <div class="num">{len(watchlist)}</div><div class="lbl">📋 Watchlist</div>
  </div>
  <div class="stat" id="st-favorites"  onclick="sw('favorites')">
    <div class="num">{len(favorites)}</div><div class="lbl">❤️ Favorites</div>
  </div>
  <div class="stat" id="st-reviews"    onclick="sw('reviews')">
    <div class="num">{len(reviews)}</div><div class="lbl">💬 Reviews</div>
  </div>
</div>

<div class="tabs">
  <div class="tab active" id="tb-users"     onclick="sw('users')">👤 Users</div>
  <div class="tab"        id="tb-watchlist" onclick="sw('watchlist')">📋 Watchlist</div>
  <div class="tab"        id="tb-favorites" onclick="sw('favorites')">❤️ Favorites</div>
  <div class="tab"        id="tb-reviews"   onclick="sw('reviews')">💬 Reviews</div>
</div>

{u_panel}
{w_panel}
{f_panel}
{r_panel}

<footer>CineAI Admin &bull; PostgreSQL &bull; 🔒 Admin Only</footer>

<script>
var TABS=['users','watchlist','favorites','reviews'];
function sw(name){{
  TABS.forEach(function(t){{
    ['panel-','tb-','st-'].forEach(function(p){{
      var el=document.getElementById(p+t);
      if(el) el.classList.toggle('active',t===name);
    }});
  }});
}}
function doFilter(tid,cols){{
  var q=document.getElementById('srch-'+tid).value.toLowerCase().trim();
  var rows=document.querySelectorAll('#body-'+tid+' tr');
  var vis=0;
  rows.forEach(function(r){{
    var tds=r.querySelectorAll('td');
    var ok=!q||cols.some(function(c){{
      return tds[c]&&tds[c].textContent.toLowerCase().includes(q);
    }});
    r.classList.toggle('hidden',!ok);
    if(ok)vis++;
  }});
  var el=document.getElementById('cnt-'+tid);
  if(el)el.textContent=(q?vis+' of '+rows.length:rows.length)+' record'+(rows.length!==1?'s':'');
}}
</script>
</body></html>""")
