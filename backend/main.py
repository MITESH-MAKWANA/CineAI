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
    try:
        create_all_tables()
    except Exception as e:
        print(f"[WARN] DB init: {e}")
    try:
        from ml.sentiment_engine import SentimentEngine
        app.state.sentiment = SentimentEngine()
        print("[OK] Sentiment engine ready.")
    except Exception as e:
        print(f"[WARN] Sentiment engine startup: {e}")
    # Recommender loads lazily on first request to avoid startup timeout
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


# ??&#128274; Admin Dashboard 
@app.get("/admin", response_class=HTMLResponse, tags=["Admin"])
def admin_dashboard(key: str = Query(default="")):

    # No key: show login page 
    if not key:
        return HTMLResponse("""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>CineAI Admin</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',sans-serif;background:#0d0d1a;color:#e2e8f0;
     display:flex;align-items:center;justify-content:center;min-height:100vh}
.card{background:#13132a;border:1px solid #252545;border-radius:16px;
      padding:48px 40px;text-align:center;width:380px}
.logo{font-size:44px;margin-bottom:12px}
h1{font-size:22px;font-weight:700;margin-bottom:6px}
p{color:#94a3b8;font-size:13px;margin-bottom:28px}
input{width:100%;padding:13px 16px;background:#0d0d1a;border:1px solid #4c1d95;
      border-radius:10px;color:#e2e8f0;font-size:15px;margin-bottom:16px;
      outline:none;letter-spacing:2px}
input:focus{border-color:#a78bfa}
button{width:100%;padding:13px;background:linear-gradient(135deg,#6c3ef4,#e040fb);
       color:#fff;border:none;border-radius:10px;font-size:15px;
       font-weight:600;cursor:pointer}
</style></head><body>
<div class="card">
  <div class="logo"></div>
  <h1>CineAI Admin Panel</h1>
  <p>Live database viewer &mdash; admin only</p>
  <form onsubmit="go(event)">
    <input type="password" id="k" placeholder="Enter admin key..." autofocus/>
    <button type="submit">&#128275; Open Dashboard</button>
  </form>
</div>
<script>
function go(e){e.preventDefault();
  var k=document.getElementById('k').value.trim();
  if(k) window.location.href='/admin?key='+encodeURIComponent(k);
}
</script></body></html>""")

    # Wrong key 
    if key != ADMIN_SECRET:
        return HTMLResponse("""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>CineAI Admin</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',sans-serif;background:#0d0d1a;color:#e2e8f0;
     display:flex;align-items:center;justify-content:center;min-height:100vh}
.card{background:#13132a;border:1px solid #252545;border-radius:16px;
      padding:48px 40px;text-align:center;width:380px}
.logo{font-size:44px;margin-bottom:12px}
h1{font-size:22px;font-weight:700;margin-bottom:6px;color:#f87171}
p{color:#94a3b8;font-size:13px;margin-bottom:28px}
input{width:100%;padding:13px 16px;background:#0d0d1a;border:1px solid #4c1d95;
      border-radius:10px;color:#e2e8f0;font-size:15px;margin-bottom:16px;
      outline:none;letter-spacing:2px}
input:focus{border-color:#a78bfa}
button{width:100%;padding:13px;background:linear-gradient(135deg,#6c3ef4,#e040fb);
       color:#fff;border:none;border-radius:10px;font-size:15px;
       font-weight:600;cursor:pointer}
</style></head><body>
<div class="card">
  <div class="logo"></div>
  <h1> Wrong Key</h1>
  <p>Please try again with the correct admin key</p>
  <form onsubmit="go(event)">
    <input type="password" id="k" placeholder="Enter admin key..." autofocus/>
    <button type="submit">&#128275; Try Again</button>
  </form>
</div>
<script>
function go(e){e.preventDefault();
  var k=document.getElementById('k').value.trim();
  if(k) window.location.href='/admin?key='+encodeURIComponent(k);
}
</script></body></html>""", status_code=403)

    # Load data 
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

    def esc(v):
        return str(v).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

    def make_table(tid, headers, rows):
        head = "".join(f"<th>{h}</th>" for h in headers)
        if rows:
            body = "".join(
                "<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>"
                for r in rows
            )
        else:
            body = f'<tr><td colspan="{len(headers)}" class="empty">No data yet</td></tr>'
        return f"""
<div class="panel" id="panel-{tid}">
  <div class="toolbar">
    <div class="sw"><span class="si"></span>
      <input class="sbox" id="srch-{tid}" type="text"
             placeholder="Search..." oninput="doFilter('{tid}')"/>
    </div>
    <span class="rc" id="cnt-{tid}">{len(rows)} records</span>
  </div>
  <div class="tw">
    <table id="tbl-{tid}">
      <thead><tr>{head}</tr></thead>
      <tbody id="body-{tid}">{body}</tbody>
    </table>
  </div>
</div>"""

    u_tbl = make_table("users",
        ["ID", "Username", "Email", "Age", "Gender", "Favorite Genres"],
        [(u.id, esc(u.username), esc(u.email),
          u.age or "", esc(u.gender or ""),
          esc(u.favorite_genres or "")) for u in users])

    w_tbl = make_table("watchlist",
        ["ID", "User ID", "Movie ID", "Movie Title"],
        [(w.id, w.user_id, w.movie_id, esc(w.movie_title)) for w in watchlist])

    f_tbl = make_table("favorites",
        ["ID", "User ID", "Movie ID", "Movie Title"],
        [(f.id, f.user_id, f.movie_id, esc(f.movie_title)) for f in favorites])

    r_tbl = make_table("reviews",
        ["ID", "User ID", "Movie Title", "Review", "Sentiment"],
        [(r.id, r.user_id, esc(r.movie_title),
          esc(r.review_text[:70]+"" if len(r.review_text)>70 else r.review_text),
          f'<span class="sent {r.sentiment}">{r.sentiment or ""}</span>')
         for r in reviews])

    return HTMLResponse(f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>&#127921; CineAI Admin Dashboard</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Segoe UI',system-ui,sans-serif;background:#0d0d1a;
     color:#e2e8f0;min-height:100vh}}
header{{background:linear-gradient(120deg,#4c1d95,#6d28d9,#7e22ce);
        padding:16px 28px;display:flex;align-items:center;
        justify-content:space-between;box-shadow:0 4px 24px rgba(0,0,0,.5)}}
.ht{{font-size:20px;font-weight:700}}
.hs{{font-size:11px;opacity:.7;margin-top:3px}}
.pill{{background:rgba(255,255,255,.13);border:1px solid rgba(255,255,255,.22);
       border-radius:30px;padding:5px 13px;font-size:12px;font-weight:600}}
/* Stat cards */
.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;padding:18px 28px}}
.card{{background:#13132a;border:1px solid #1e1e3f;border-radius:12px;
       padding:16px;text-align:center;cursor:pointer;transition:.2s}}
.card:hover,.card.active{{border-color:#7c3aed;background:#18183a}}
.card .n{{font-size:32px;font-weight:800;color:#a78bfa}}
.card .l{{font-size:11px;color:#64748b;margin-top:4px;
          text-transform:uppercase;letter-spacing:.4px}}
/* Tabs */
.tabs{{display:flex;padding:0 28px;border-bottom:1px solid #1a1a35}}
.tab{{padding:11px 18px;font-size:13.5px;font-weight:500;color:#64748b;
      border-bottom:2px solid transparent;cursor:pointer;transition:.15s}}
.tab:hover{{color:#c4b5fd}}
.tab.active{{color:#c4b5fd;border-bottom-color:#7c3aed}}
/* Panel */
.panel{{display:none;padding:18px 28px 36px}}
.panel.active{{display:block}}
/* Toolbar */
.toolbar{{display:flex;align-items:center;gap:12px;margin-bottom:14px}}
.sw{{position:relative;flex:1;max-width:400px}}
.si{{position:absolute;left:12px;top:50%;transform:translateY(-50%);
     font-size:13px;pointer-events:none}}
.sbox{{width:100%;padding:9px 12px 9px 34px;background:#13132a;
       border:1px solid #1e1e3f;border-radius:9px;color:#e2e8f0;
       font-size:13.5px;outline:none;transition:.2s}}
.sbox:focus{{border-color:#7c3aed;box-shadow:0 0 0 3px rgba(124,58,237,.18)}}
.rc{{font-size:12px;color:#475569;margin-left:auto}}
/* Table */
.tw{{overflow-x:auto;border-radius:11px;border:1px solid #1a1a35}}
table{{width:100%;border-collapse:collapse;font-size:13.5px}}
thead{{background:#0d0d20}}
th{{padding:11px 14px;text-align:left;color:#7c3aed;font-weight:600;
    font-size:11px;text-transform:uppercase;letter-spacing:.5px;
    white-space:nowrap}}
td{{padding:10px 14px;border-top:1px solid #131330;color:#cbd5e1;
    white-space:nowrap;max-width:260px;overflow:hidden;text-overflow:ellipsis}}
tr:hover td{{background:#15153a}}
tr.hidden{{display:none}}
.empty{{text-align:center;color:#334155;padding:36px;font-size:14px}}
.sent{{border-radius:20px;padding:2px 9px;font-size:11px;font-weight:700;text-transform:uppercase}}
.sent.positive{{background:rgba(16,185,129,.12);color:#34d399}}
.sent.negative{{background:rgba(239,68,68,.12);color:#f87171}}
.sent.neutral{{background:rgba(148,163,184,.1);color:#94a3b8}}
footer{{text-align:center;padding:18px;color:#1e293b;font-size:12px;
        border-top:1px solid #0f0f25;margin-top:8px}}
</style></head><body>

<header>
  <div>
    <div class="ht">&#127921; &#127921; CineAI Admin Dashboard</div>
    <div class="hs">Live PostgreSQL database viewer &mdash; admin only</div>
  </div>
  <span class="pill">&#128274; Admin</span>
</header>

<div class="cards">
  <div class="card active" id="c-users"     onclick="sw('users')">
    <div class="n">{len(users)}</div><div class="l">&#128100; Users</div>
  </div>
  <div class="card" id="c-watchlist" onclick="sw('watchlist')">
    <div class="n">{len(watchlist)}</div><div class="l">&#128203; Watchlist</div>
  </div>
  <div class="card" id="c-favorites" onclick="sw('favorites')">
    <div class="n">{len(favorites)}</div><div class="l">&#10084; Favorites</div>
  </div>
  <div class="card" id="c-reviews"   onclick="sw('reviews')">
    <div class="n">{len(reviews)}</div><div class="l">&#128172; Reviews</div>
  </div>
</div>

<div class="tabs">
  <div class="tab active" id="tb-users"     onclick="sw('users')">&#128100; Users</div>
  <div class="tab"        id="tb-watchlist" onclick="sw('watchlist')">&#128203; Watchlist</div>
  <div class="tab"        id="tb-favorites" onclick="sw('favorites')">&#10084; Favorites</div>
  <div class="tab"        id="tb-reviews"   onclick="sw('reviews')">&#128172; Reviews</div>
</div>

{u_tbl}
{w_tbl}
{f_tbl}
{r_tbl}

<footer>&#127921; CineAI Admin Dashboard &bull; PostgreSQL &bull; &#128274; Admin Only</footer>

<script>
var TABS=['users','watchlist','favorites','reviews'];
function sw(name){{
  TABS.forEach(function(t){{
    var p=document.getElementById('panel-'+t);
    var tb=document.getElementById('tb-'+t);
    var c=document.getElementById('c-'+t);
    if(p) p.classList.toggle('active',t===name);
    if(tb) tb.classList.toggle('active',t===name);
    if(c) c.classList.toggle('active',t===name);
  }});
}}
function doFilter(tid){{
  var q=(document.getElementById('srch-'+tid).value||'').toLowerCase().trim();
  var rows=document.querySelectorAll('#body-'+tid+' tr');
  var vis=0;
  rows.forEach(function(r){{
    var ok=!q||Array.from(r.querySelectorAll('td')).some(function(td){{
      return td.textContent.toLowerCase().includes(q);
    }});
    r.classList.toggle('hidden',!ok);
    if(ok) vis++;
  }});
  var el=document.getElementById('cnt-'+tid);
  if(el) el.textContent=(q?vis+' of '+rows.length:rows.length)+' records';
}}
</script>
</body></html>""")
