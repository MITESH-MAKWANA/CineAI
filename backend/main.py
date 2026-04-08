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


# ── Login page ─────────────────────────────────────────────────────────────────
def _login_page(msg=""):
    return HTMLResponse(f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>CineAI Admin</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Segoe UI',sans-serif;background:#0d0d1a;color:#e2e8f0;
     display:flex;align-items:center;justify-content:center;min-height:100vh}}
.card{{background:#13132a;border:1px solid #252545;border-radius:18px;padding:48px 40px;
      text-align:center;width:390px;box-shadow:0 24px 64px rgba(0,0,0,.6)}}
.logo{{font-size:48px;margin-bottom:14px}}
h1{{font-size:22px;font-weight:700;margin-bottom:6px}}
.sub{{color:#94a3b8;font-size:13px;margin-bottom:28px;min-height:20px}}
.err{{color:#f87171}}
input{{width:100%;padding:13px 16px;background:#0d0d1a;border:1px solid #4c1d95;
      border-radius:10px;color:#e2e8f0;font-size:15px;margin-bottom:16px;outline:none;
      letter-spacing:3px}}
input:focus{{border-color:#a78bfa;box-shadow:0 0 0 3px rgba(167,139,250,.15)}}
button{{width:100%;padding:13px;background:linear-gradient(135deg,#6c3ef4,#e040fb);
       color:#fff;border:none;border-radius:10px;font-size:15px;font-weight:600;
       cursor:pointer;transition:.2s}}
button:hover{{opacity:.88;transform:translateY(-1px)}}
</style></head><body>
<div class="card">
  <div class="logo">🎬</div>
  <h1>CineAI Admin Panel</h1>
  <p class="sub">{msg if msg else 'Live database viewer &mdash; admin only'}</p>
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


# ── Admin Dashboard ─────────────────────────────────────────────────────────
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
    import json

    db: Session = SessionLocal()
    try:
        users     = db.query(User).order_by(User.id).all()
        watchlist = db.query(WatchlistItem).order_by(WatchlistItem.id).all()
        favorites = db.query(FavoriteItem).order_by(FavoriteItem.id).all()
        reviews   = db.query(Review).order_by(Review.id).all()
    finally:
        db.close()

    # Build user detail lookup for modal
    user_detail = {}
    for u in users:
        uid = u.id
        user_detail[uid] = {
            "id": uid,
            "username": u.username,
            "email": u.email,
            "age": u.age or "—",
            "gender": u.gender or "—",
            "genres": u.favorite_genres or "—",
            "watchlist": [{"movie_id": w.movie_id, "title": w.movie_title}
                          for w in watchlist if w.user_id == uid],
            "favorites": [{"movie_id": f.movie_id, "title": f.movie_title}
                          for f in favorites if f.user_id == uid],
            "reviews": [{"title": r.movie_title, "text": r.review_text[:80],
                         "sentiment": r.sentiment}
                        for r in reviews if r.user_id == uid],
        }
    detail_js = json.dumps(user_detail)

    # Stats
    with_genres    = sum(1 for u in users if u.favorite_genres)
    without_genres = len(users) - with_genres
    pos_rev = sum(1 for r in reviews if r.sentiment == "positive")
    neg_rev = sum(1 for r in reviews if r.sentiment == "negative")
    neu_rev = sum(1 for r in reviews if r.sentiment == "neutral")

    def esc(v):
        return str(v).replace("<","&lt;").replace(">","&gt;").replace('"','&quot;')

    def make_rows(data):
        if not data:
            return '<tr><td colspan="10" class="empty">No records yet</td></tr>'
        return "".join(
            "<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>"
            for r in data
        )

    def make_panel(tid, headers, data, search_hint, extra_btn=""):
        head = "".join(f'<th onclick="sortTbl(\'{tid}\',{i})" title="Sort">{h} <span class="sort-icon">↕</span></th>'
                       for i, h in enumerate(headers))
        body = make_rows(data)
        n    = len(data)
        return f"""
<div class="panel" id="panel-{tid}">
  <div class="toolbar">
    <div class="search-wrap">
      <span class="si">🔍</span>
      <input class="sbox" id="srch-{tid}" type="text"
             placeholder="Search {search_hint}..."
             oninput="doFilter('{tid}')"/>
    </div>
    <div class="toolbar-right">
      <select class="pg-sel" id="pgsize-{tid}" onchange="changePg('{tid}')">
        <option value="10">10 / page</option>
        <option value="25">25 / page</option>
        <option value="50">50 / page</option>
        <option value="9999">All</option>
      </select>
      <button class="btn-csv" onclick="exportCSV('{tid}')">📥 Export CSV</button>
      {extra_btn}
    </div>
  </div>
  <div class="tbl-wrap">
    <table id="tbl-{tid}">
      <thead><tr>{head}</tr></thead>
      <tbody id="body-{tid}">{body}</tbody>
    </table>
  </div>
  <div class="pagination" id="pg-{tid}"></div>
  <div class="rec-info" id="cnt-{tid}">{n} total record{'s' if n!=1 else ''}</div>
</div>"""

    u_rows = [(
        f'<span class="uid">{u.id}</span>',
        f'<span class="clickable" onclick="showUser({u.id})">{esc(u.username)}</span>',
        esc(u.email),
        u.age or "—",
        esc(u.gender or "—"),
        esc(u.favorite_genres or "—")
    ) for u in users]

    w_rows = [(w.id, w.user_id, w.movie_id, esc(w.movie_title)) for w in watchlist]
    f_rows = [(f.id, f.user_id, f.movie_id, esc(f.movie_title)) for f in favorites]
    r_rows = [(r.id, r.user_id, esc(r.movie_title),
               esc((r.review_text[:60]+"…") if len(r.review_text)>60 else r.review_text),
               f'<span class="sent {r.sentiment}">{r.sentiment or "—"}</span>')
              for r in reviews]

    u_panel = make_panel("users",
        ["ID","Username","Email","Age","Gender","Genres"],
        u_rows, "username / email / age / gender / genres",
        '<button class="btn-csv" style="background:#1e3a5f" onclick="showAllUsers()">👁 View All</button>')
    w_panel = make_panel("watchlist", ["ID","User ID","Movie ID","Movie Title"], w_rows, "movie title")
    f_panel = make_panel("favorites", ["ID","User ID","Movie ID","Movie Title"], f_rows, "movie title")
    r_panel = make_panel("reviews",   ["ID","User ID","Movie Title","Review","Sentiment"], r_rows, "movie / sentiment")

    return HTMLResponse(f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CineAI Admin Dashboard</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Segoe UI',system-ui,sans-serif;background:#0d0d1a;color:#e2e8f0;min-height:100vh}}
/* Header */
header{{background:linear-gradient(120deg,#4c1d95,#6d28d9,#7e22ce);padding:15px 28px;
        display:flex;align-items:center;justify-content:space-between;
        box-shadow:0 4px 30px rgba(0,0,0,.5)}}
.h-title{{font-size:19px;font-weight:700}}
.h-sub{{font-size:11px;opacity:.7;margin-top:3px}}
.h-actions{{display:flex;gap:8px;align-items:center}}
.pill{{background:rgba(255,255,255,.13);border:1px solid rgba(255,255,255,.22);
       border-radius:30px;padding:5px 13px;font-size:12px;font-weight:600}}
.btn{{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.18);
      color:#fff;padding:6px 13px;border-radius:8px;text-decoration:none;
      font-size:13px;transition:.15s;cursor:pointer}}
.btn:hover{{background:rgba(255,255,255,.22)}}
/* Summary stats */
.summary{{display:grid;grid-template-columns:repeat(7,1fr);gap:10px;padding:16px 28px;
          background:#0a0a16;border-bottom:1px solid #151530}}
.sm{{background:#13132a;border:1px solid #1e1e3f;border-radius:10px;
     padding:11px 14px;text-align:center}}
.sm .n{{font-size:22px;font-weight:800;color:#a78bfa}}
.sm .l{{font-size:10px;color:#475569;margin-top:3px;text-transform:uppercase;letter-spacing:.4px}}
/* Stat cards */
.stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;padding:16px 28px}}
.stat{{background:#13132a;border:1px solid #1e1e3f;border-radius:12px;
       padding:16px 18px;text-align:center;cursor:pointer;transition:.2s;position:relative;overflow:hidden}}
.stat::after{{content:'';position:absolute;bottom:0;left:0;right:0;height:3px;
              background:linear-gradient(90deg,#7c3aed,#db2777);opacity:0;transition:.2s}}
.stat.active,.stat:hover{{border-color:#7c3aed;background:#18183a}}
.stat.active::after,.stat:hover::after{{opacity:1}}
.stat .num{{font-size:32px;font-weight:800;color:#a78bfa;line-height:1}}
.stat .lbl{{font-size:11px;color:#64748b;margin-top:5px;text-transform:uppercase;letter-spacing:.5px}}
/* Tabs */
.tabs{{display:flex;padding:0 28px;border-bottom:1px solid #1a1a35;gap:2px}}
.tab{{padding:11px 18px;font-size:13.5px;font-weight:500;color:#64748b;
      border-bottom:2px solid transparent;cursor:pointer;transition:.15s;border-radius:4px 4px 0 0}}
.tab:hover{{color:#c4b5fd;background:#ffffff06}}
.tab.active{{color:#c4b5fd;border-bottom-color:#7c3aed}}
/* Panel */
.panel{{display:none;padding:18px 28px 32px}}
.panel.active{{display:block}}
/* Toolbar */
.toolbar{{display:flex;align-items:center;gap:10px;margin-bottom:14px;flex-wrap:wrap}}
.search-wrap{{position:relative;flex:1;min-width:220px;max-width:420px}}
.si{{position:absolute;left:12px;top:50%;transform:translateY(-50%);font-size:13px;pointer-events:none}}
.sbox{{width:100%;padding:9px 12px 9px 34px;background:#13132a;border:1px solid #1e1e3f;
       border-radius:9px;color:#e2e8f0;font-size:13.5px;outline:none;transition:.2s}}
.sbox:focus{{border-color:#7c3aed;background:#18183a;box-shadow:0 0 0 3px rgba(124,58,237,.18)}}
.toolbar-right{{display:flex;gap:8px;align-items:center;margin-left:auto;flex-wrap:wrap}}
.pg-sel{{padding:8px 10px;background:#13132a;border:1px solid #1e1e3f;border-radius:8px;
         color:#e2e8f0;font-size:13px;outline:none;cursor:pointer}}
.btn-csv{{padding:8px 13px;background:#2d1b69;border:1px solid #4c1d95;
          color:#c4b5fd;border-radius:8px;font-size:13px;cursor:pointer;transition:.15s;font-weight:500}}
.btn-csv:hover{{background:#3b1fa8;border-color:#7c3aed}}
/* Table */
.tbl-wrap{{overflow-x:auto;border-radius:11px;border:1px solid #1a1a35}}
table{{width:100%;border-collapse:collapse;font-size:13.5px}}
thead{{background:#0d0d20}}
th{{padding:11px 14px;text-align:left;color:#7c3aed;font-weight:600;font-size:11px;
    text-transform:uppercase;letter-spacing:.5px;white-space:nowrap;cursor:pointer;
    user-select:none;position:sticky;top:0;background:#0d0d20;transition:.15s}}
th:hover{{color:#a78bfa;background:#13132a}}
.sort-icon{{opacity:.4;font-size:10px}}
th.asc .sort-icon::after{{content:'▲';opacity:1}}
th.desc .sort-icon::after{{content:'▼';opacity:1}}
th.asc .sort-icon,th.desc .sort-icon{{opacity:1;color:#a78bfa}}
td{{padding:10px 14px;border-top:1px solid #131330;color:#cbd5e1;
    white-space:nowrap;max-width:260px;overflow:hidden;text-overflow:ellipsis}}
tr:hover td{{background:#15153a}}
tr.hidden{{display:none}}
.empty{{text-align:center;color:#334155;padding:36px;font-size:14px}}
.uid{{background:#1e1e3f;border-radius:4px;padding:2px 7px;font-size:12px;color:#7c3aed;font-weight:600}}
.clickable{{color:#a78bfa;cursor:pointer;text-decoration:underline;text-underline-offset:2px}}
.clickable:hover{{color:#c4b5fd}}
/* Sentiment */
.sent{{border-radius:20px;padding:2px 9px;font-size:11px;font-weight:700;text-transform:uppercase}}
.sent.positive{{background:rgba(16,185,129,.12);color:#34d399;border:1px solid rgba(16,185,129,.2)}}
.sent.negative{{background:rgba(239,68,68,.12);color:#f87171;border:1px solid rgba(239,68,68,.2)}}
.sent.neutral{{background:rgba(148,163,184,.1);color:#94a3b8;border:1px solid rgba(148,163,184,.15)}}
/* Pagination */
.pagination{{display:flex;gap:6px;margin-top:14px;flex-wrap:wrap;align-items:center}}
.pg-btn{{padding:6px 11px;background:#13132a;border:1px solid #1e1e3f;border-radius:7px;
         color:#94a3b8;font-size:13px;cursor:pointer;transition:.15s}}
.pg-btn:hover,.pg-btn.active{{background:#2d1b69;border-color:#7c3aed;color:#c4b5fd}}
.rec-info{{font-size:12px;color:#374151;margin-top:8px}}
/* Modal */
.overlay{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.75);z-index:100;
          align-items:center;justify-content:center;padding:20px}}
.overlay.open{{display:flex}}
.modal{{background:#13132a;border:1px solid #252550;border-radius:16px;
        width:100%;max-width:680px;max-height:90vh;overflow-y:auto;
        box-shadow:0 32px 80px rgba(0,0,0,.7)}}
.modal-header{{padding:20px 24px 16px;border-bottom:1px solid #1e1e3f;
               display:flex;align-items:center;justify-content:space-between}}
.modal-header h2{{font-size:18px;font-weight:700}}
.close-btn{{background:none;border:none;color:#64748b;font-size:22px;cursor:pointer;
            padding:0 4px;line-height:1;transition:.15s}}
.close-btn:hover{{color:#f87171}}
.modal-body{{padding:20px 24px}}
.m-section{{margin-bottom:20px}}
.m-section h3{{font-size:13px;text-transform:uppercase;letter-spacing:.5px;color:#7c3aed;
               font-weight:600;margin-bottom:10px;display:flex;align-items:center;gap:8px}}
.m-badge{{background:#1e1e3f;border-radius:20px;padding:2px 8px;font-size:12px;color:#94a3b8}}
.info-grid{{display:grid;grid-template-columns:1fr 1fr;gap:10px}}
.info-item{{background:#0d0d1a;border:1px solid #1a1a35;border-radius:8px;padding:10px 14px}}
.info-item .k{{font-size:11px;color:#475569;text-transform:uppercase;letter-spacing:.4px}}
.info-item .v{{font-size:14px;color:#e2e8f0;margin-top:3px;font-weight:500}}
.m-list{{display:flex;flex-direction:column;gap:6px}}
.m-list-item{{background:#0d0d1a;border:1px solid #1a1a35;border-radius:8px;
              padding:9px 14px;font-size:13px;color:#cbd5e1;display:flex;
              align-items:center;justify-content:space-between}}
.no-data{{color:#374151;font-size:13px;padding:10px 0}}
footer{{text-align:center;padding:18px;color:#1e293b;font-size:12px;border-top:1px solid #0f0f25}}
@media(max-width:700px){{
  .stats{{grid-template-columns:repeat(2,1fr)}}
  .summary{{grid-template-columns:repeat(4,1fr)}}
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

<!-- Summary Stats Bar -->
<div class="summary">
  <div class="sm"><div class="n">{len(users)}</div><div class="l">Total Users</div></div>
  <div class="sm"><div class="n">{with_genres}</div><div class="l">With Genres</div></div>
  <div class="sm"><div class="n">{without_genres}</div><div class="l">No Genres</div></div>
  <div class="sm"><div class="n">{len(watchlist)}</div><div class="l">Watchlist</div></div>
  <div class="sm"><div class="n">{len(favorites)}</div><div class="l">Favorites</div></div>
  <div class="sm"><div class="n" style="color:#34d399">{pos_rev}</div><div class="l">Positive Rev</div></div>
  <div class="sm"><div class="n" style="color:#f87171">{neg_rev}</div><div class="l">Negative Rev</div></div>
</div>

<!-- Stat Cards -->
<div class="stats">
  <div class="stat active" id="st-users"     onclick="sw('users')">
    <div class="num">{len(users)}</div><div class="lbl">👤 Users</div>
  </div>
  <div class="stat" id="st-watchlist" onclick="sw('watchlist')">
    <div class="num">{len(watchlist)}</div><div class="lbl">📋 Watchlist</div>
  </div>
  <div class="stat" id="st-favorites" onclick="sw('favorites')">
    <div class="num">{len(favorites)}</div><div class="lbl">❤️ Favorites</div>
  </div>
  <div class="stat" id="st-reviews"   onclick="sw('reviews')">
    <div class="num">{len(reviews)}</div><div class="lbl">💬 Reviews</div>
  </div>
</div>

<!-- Tabs -->
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

<!-- User Detail Modal -->
<div class="overlay" id="modal-overlay" onclick="closeModal(event)">
  <div class="modal" id="modal-box">
    <div class="modal-header">
      <h2 id="modal-title">User Details</h2>
      <button class="close-btn" onclick="closeModal()">✕</button>
    </div>
    <div class="modal-body" id="modal-body"></div>
  </div>
</div>

<footer>CineAI Admin Dashboard &bull; PostgreSQL &bull; 🔒 Admin Only</footer>

<script>
var TABS = ['users','watchlist','favorites','reviews'];
var USER_DATA = {detail_js};
var sortState = {{}};
var filterState = {{}};
var pgState = {{}};
var pgSize = {{}};

// Init pagination for all tabs
TABS.forEach(function(t) {{
  pgState[t] = 1;
  pgSize[t] = 10;
  renderPage(t);
}});

function sw(name) {{
  TABS.forEach(function(t) {{
    ['panel-','tb-','st-'].forEach(function(p) {{
      var el = document.getElementById(p+t);
      if (el) el.classList.toggle('active', t===name);
    }});
  }});
}}

// ── Filter ─────────────────────────────────────────────────────────────────
function doFilter(tid) {{
  pgState[tid] = 1;
  renderPage(tid);
}}

function getVisibleRows(tid) {{
  var q = (document.getElementById('srch-'+tid)||{{}}).value||'';
  q = q.toLowerCase().trim();
  var rows = Array.from(document.querySelectorAll('#body-'+tid+' tr'));
  return rows.filter(function(r) {{
    if (!q) return true;
    return Array.from(r.querySelectorAll('td')).some(function(td) {{
      return td.textContent.toLowerCase().includes(q);
    }});
  }});
}}

function renderPage(tid) {{
  var allRows = Array.from(document.querySelectorAll('#body-'+tid+' tr'));
  var visible = getVisibleRows(tid);
  var pg = pgState[tid] || 1;
  var ps = pgSize[tid] || 10;
  var total = visible.length;
  var pages = Math.max(1, Math.ceil(total / ps));
  if (pg > pages) pg = pages;
  pgState[tid] = pg;

  allRows.forEach(function(r) {{ r.classList.add('hidden'); }});
  visible.forEach(function(r, i) {{
    var show = i >= (pg-1)*ps && i < pg*ps;
    r.classList.toggle('hidden', !show);
  }});

  // Pagination buttons
  var pgDiv = document.getElementById('pg-'+tid);
  var html = '';
  if (pages > 1) {{
    html += '<span class="pg-btn'+(pg===1?' active':'')+'" onclick="goPage(\''+tid+'\',1)">«</span>';
    for (var i=1; i<=pages; i++) {{
      if (pages<=7 || i===1 || i===pages || Math.abs(i-pg)<=1)
        html += '<span class="pg-btn'+(i===pg?' active':'')+'" onclick="goPage(\''+tid+'\','+i+')">'+i+'</span>';
      else if (Math.abs(i-pg)===2)
        html += '<span style="color:#374151;padding:6px 4px">…</span>';
    }}
    html += '<span class="pg-btn'+(pg===pages?' active':'')+'" onclick="goPage(\''+tid+'\','+pages+')">»</span>';
  }}
  if (pgDiv) pgDiv.innerHTML = html;

  var cnt = document.getElementById('cnt-'+tid);
  if (cnt) {{
    var showing = Math.min(ps, total-(pg-1)*ps);
    cnt.textContent = total + ' record'+(total!==1?'s':'')+
      (total > ps ? ' — showing '+(((pg-1)*ps)+1)+'–'+Math.min(pg*ps,total) : '');
  }}
}}

function goPage(tid, pg) {{ pgState[tid]=pg; renderPage(tid); }}

function changePg(tid) {{
  pgSize[tid] = parseInt(document.getElementById('pgsize-'+tid).value);
  pgState[tid] = 1;
  renderPage(tid);
}}

// ── Sort ───────────────────────────────────────────────────────────────────
function sortTbl(tid, col) {{
  var tbody = document.getElementById('body-'+tid);
  var rows  = Array.from(tbody.querySelectorAll('tr'));
  var key   = tid+'_'+col;
  var asc   = sortState[key] !== true;
  sortState[key] = asc;

  // Update header icons
  var ths = document.querySelectorAll('#tbl-'+tid+' thead th');
  ths.forEach(function(th,i) {{
    th.classList.remove('asc','desc');
    if (i===col) th.classList.add(asc?'asc':'desc');
  }});

  rows.sort(function(a,b) {{
    var av = (a.querySelectorAll('td')[col]||{{}}).textContent||'';
    var bv = (b.querySelectorAll('td')[col]||{{}}).textContent||'';
    var ai = parseFloat(av), bi = parseFloat(bv);
    if (!isNaN(ai)&&!isNaN(bi)) return asc?ai-bi:bi-ai;
    return asc ? av.localeCompare(bv) : bv.localeCompare(av);
  }});
  rows.forEach(function(r) {{ tbody.appendChild(r); }});
  renderPage(tid);
}}

// ── Export CSV ─────────────────────────────────────────────────────────────
function exportCSV(tid) {{
  var table = document.getElementById('tbl-'+tid);
  var rows  = Array.from(table.querySelectorAll('tr'));
  var csv   = rows.map(function(r) {{
    return Array.from(r.querySelectorAll('th,td')).map(function(c) {{
      return '"'+c.textContent.trim().replace(/"/g,'""')+'"';
    }}).join(',');
  }}).join('\\n');
  var a = document.createElement('a');
  a.href = 'data:text/csv;charset=utf-8,'+encodeURIComponent(csv);
  a.download = 'cineai_'+tid+'_'+new Date().toISOString().slice(0,10)+'.csv';
  a.click();
}}

// ── User Detail Modal ──────────────────────────────────────────────────────
function showUser(uid) {{
  var u = USER_DATA[uid];
  if (!u) return;
  document.getElementById('modal-title').textContent = '👤 '+u.username;
  var html = '<div class="m-section">';
  html += '<h3>Account Info</h3>';
  html += '<div class="info-grid">';
  html += '<div class="info-item"><div class="k">ID</div><div class="v">#'+u.id+'</div></div>';
  html += '<div class="info-item"><div class="k">Username</div><div class="v">'+u.username+'</div></div>';
  html += '<div class="info-item"><div class="k">Email</div><div class="v">'+u.email+'</div></div>';
  html += '<div class="info-item"><div class="k">Age</div><div class="v">'+u.age+'</div></div>';
  html += '<div class="info-item"><div class="k">Gender</div><div class="v">'+u.gender+'</div></div>';
  html += '<div class="info-item"><div class="k">Genres</div><div class="v">'+u.genres+'</div></div>';
  html += '</div></div>';

  html += '<div class="m-section"><h3>📋 Watchlist <span class="m-badge">'+u.watchlist.length+'</span></h3>';
  if (u.watchlist.length) {{
    html += '<div class="m-list">';
    u.watchlist.forEach(function(w) {{
      html += '<div class="m-list-item"><span>🎬 '+w.title+'</span><span style="color:#475569;font-size:12px">ID:'+w.movie_id+'</span></div>';
    }});
    html += '</div>';
  }} else html += '<p class="no-data">No watchlist entries</p>';
  html += '</div>';

  html += '<div class="m-section"><h3>❤️ Favorites <span class="m-badge">'+u.favorites.length+'</span></h3>';
  if (u.favorites.length) {{
    html += '<div class="m-list">';
    u.favorites.forEach(function(f) {{
      html += '<div class="m-list-item"><span>🎬 '+f.title+'</span><span style="color:#475569;font-size:12px">ID:'+f.movie_id+'</span></div>';
    }});
    html += '</div>';
  }} else html += '<p class="no-data">No favorites yet</p>';
  html += '</div>';

  html += '<div class="m-section"><h3>💬 Reviews <span class="m-badge">'+u.reviews.length+'</span></h3>';
  if (u.reviews.length) {{
    html += '<div class="m-list">';
    u.reviews.forEach(function(r) {{
      var cls = r.sentiment||'neutral';
      html += '<div class="m-list-item" style="flex-direction:column;align-items:flex-start;gap:4px">';
      html += '<div style="display:flex;justify-content:space-between;width:100%"><b>'+r.title+'</b><span class="sent '+cls+'">'+cls+'</span></div>';
      html += '<div style="color:#94a3b8;font-size:12px">'+r.text+'</div>';
      html += '</div>';
    }});
    html += '</div>';
  }} else html += '<p class="no-data">No reviews yet</p>';
  html += '</div>';

  document.getElementById('modal-body').innerHTML = html;
  document.getElementById('modal-overlay').classList.add('open');
}}

function closeModal(e) {{
  if (!e || e.target===document.getElementById('modal-overlay'))
    document.getElementById('modal-overlay').classList.remove('open');
}}
document.addEventListener('keydown',function(e){{if(e.key==='Escape')closeModal();}});
</script>
</body></html>""")
