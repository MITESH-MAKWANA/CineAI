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
from routes import csv_movies, contact, admin_actions
import os

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
ADMIN_SECRET    = os.getenv("ADMIN_SECRET", "cineai-admin-2024")
TMDB_IMG        = "https://image.tmdb.org/t/p/w92"


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
    # Recommender loads lazily on first request to avoid startup timeout
    print("[INFO] Recommender will load on first request.")
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
app.include_router(contact.router)
app.include_router(admin_actions.router)


@app.get("/", tags=["Health"])
def root():
    return {"app": APP_NAME, "status": "running", "version": "1.0.0", "docs": "/docs"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy", "app": APP_NAME}


# ── Admin Dashboard ────────────────────────────────────────────────────────────
@app.get("/admin", response_class=HTMLResponse, tags=["Admin"])
def admin_dashboard(key: str = Query(default="")):

    # ── Login form ────────────────────────────────────────────────────────────
    if not key:
        return HTMLResponse("""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>CineAI Admin</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',sans-serif;background:#0a0a14;color:#e2e8f0;
     display:flex;align-items:center;justify-content:center;min-height:100vh}
.card{background:#111128;border:1px solid #1e1e3f;border-radius:18px;
      padding:52px 44px;text-align:center;width:400px;
      box-shadow:0 24px 64px rgba(0,0,0,.6)}
.logo{font-size:48px;margin-bottom:14px}
h1{font-size:24px;font-weight:800;margin-bottom:6px}
p{color:#64748b;font-size:13px;margin-bottom:30px}
input{width:100%;padding:14px 16px;background:#0a0a14;border:1px solid #2d2d5e;
      border-radius:10px;color:#e2e8f0;font-size:15px;margin-bottom:16px;
      outline:none;letter-spacing:2px}
input:focus{border-color:#7c3aed;box-shadow:0 0 0 3px rgba(124,58,237,.2)}
button{width:100%;padding:14px;background:linear-gradient(135deg,#6c3ef4,#e040fb);
       color:#fff;border:none;border-radius:10px;font-size:15px;
       font-weight:700;cursor:pointer;letter-spacing:.5px}
button:hover{opacity:.9;transform:translateY(-1px)}
</style></head><body>
<div class="card">
  <div class="logo">🎬</div>
  <h1>CineAI Admin Panel</h1>
  <p>Live database viewer — admin only</p>
  <form onsubmit="go(event)">
    <input type="password" id="k" placeholder="Enter admin key..." autofocus/>
    <button type="submit">🔓 Open Dashboard</button>
  </form>
</div>
<script>function go(e){e.preventDefault();var k=document.getElementById('k').value.trim();if(k)window.location.href='/admin?key='+encodeURIComponent(k);}</script>
</body></html>""")

    # ── Wrong key ─────────────────────────────────────────────────────────────
    if key != ADMIN_SECRET:
        return HTMLResponse("""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Access Denied</title>
<style>body{font-family:'Segoe UI',sans-serif;background:#0a0a14;color:#e2e8f0;display:flex;align-items:center;justify-content:center;min-height:100vh}
.card{background:#111128;border:1px solid #2d1414;border-radius:18px;padding:52px 44px;text-align:center;width:400px}
h1{color:#f87171;font-size:22px;margin-bottom:12px}p{color:#64748b;margin-bottom:24px}
input{width:100%;padding:14px;background:#0a0a14;border:1px solid #7c3aed;border-radius:10px;color:#e2e8f0;font-size:15px;margin-bottom:16px;outline:none;letter-spacing:2px}
button{width:100%;padding:14px;background:linear-gradient(135deg,#6c3ef4,#e040fb);color:#fff;border:none;border-radius:10px;font-size:15px;font-weight:700;cursor:pointer}
</style></head><body>
<div class="card"><div style="font-size:48px;margin-bottom:14px">❌</div>
<h1>Wrong Key</h1><p>Please try the correct admin key</p>
<form onsubmit="go(event)"><input type="password" id="k" placeholder="Enter admin key..." autofocus/><button>🔓 Try Again</button></form>
</div>
<script>function go(e){e.preventDefault();var k=document.getElementById('k').value.trim();if(k)window.location.href='/admin?key='+encodeURIComponent(k);}</script>
</body></html>""", status_code=403)

    # ── Load data ─────────────────────────────────────────────────────────────
    from sqlalchemy.orm import Session
    from database import SessionLocal
    from models.user import User
    from models.watchlist import WatchlistItem, FavoriteItem
    from models.review import Review
    from models.contact import ContactMessage
    from sqlalchemy import func as sqlfunc

    db: Session = SessionLocal()
    try:
        users     = db.query(User).order_by(User.id).all()
        watchlist = db.query(WatchlistItem).order_by(WatchlistItem.id).all()
        favorites = db.query(FavoriteItem).order_by(FavoriteItem.id).all()
        reviews   = db.query(Review).order_by(Review.id.desc()).all()
        messages  = db.query(ContactMessage).order_by(ContactMessage.created_at.desc()).all()

        # Analytics
        pos_count  = db.query(Review).filter(Review.sentiment == "positive").count()
        neg_count  = db.query(Review).filter(Review.sentiment == "negative").count()
        neu_count  = db.query(Review).filter(Review.sentiment == "neutral").count()
        unread_msgs = db.query(ContactMessage).filter(ContactMessage.is_read == False).count()
        banned_count = db.query(User).filter(User.is_banned == True).count()
    finally:
        db.close()

    def esc(v):
        return str(v or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"','&quot;')

    def poster_thumb(path):
        if not path or path.strip() == "":
            return '<span class="no-poster">🎬</span>'
        src = f"{TMDB_IMG}{path if path.startswith('/') else '/' + path}"
        return f'<img src="{src}" class="poster-thumb" onerror="this.style.display=\'none\'" loading="lazy"/>'

    # ── Build Users table rows ─────────────────────────────────────────────────
    user_rows = ""
    for u in users:
        banned_cls = " row-banned" if u.is_banned else ""
        ban_btn = (
            f'<button class="btn-act btn-unban" onclick="adminAction(\'POST\',\'/admin/users/{u.id}/unban\',this,\'unban\')">Unban</button>'
            if u.is_banned else
            f'<button class="btn-act btn-ban" onclick="adminAction(\'POST\',\'/admin/users/{u.id}/ban\',this,\'ban\')">Ban</button>'
        )
        joined = str(u.created_at)[:10] if u.created_at else "—"
        user_rows += f"""<tr class="data-row{banned_cls}" data-search="{esc(u.username)} {esc(u.email)} {u.id}">
  <td>{u.id}</td>
  <td><span class="username-link" onclick="showUserModal({u.id})">{esc(u.username)}</span></td>
  <td>{esc(u.email)}</td>
  <td>{u.age or '—'}</td>
  <td>{esc(u.gender or '—')}</td>
  <td class="genres-cell">{esc(u.favorite_genres or '—')}</td>
  <td>{joined}</td>
  <td>{'🔴 Banned' if u.is_banned else '🟢 Active'}</td>
  <td class="action-cell">{ban_btn}
    <button class="btn-act btn-delete" onclick="adminAction('DELETE','/admin/users/{u.id}',this,'delete_user',{u.id})">Delete</button>
  </td>
</tr>"""

    # ── Build Watchlist rows ───────────────────────────────────────────────────
    wl_rows = ""
    for w in watchlist:
        wl_rows += f"""<tr class="data-row" data-search="{esc(w.movie_title)} {w.user_id} {w.id}">
  <td>{w.id}</td><td>{w.user_id}</td><td>{w.movie_id}</td>
  <td>{poster_thumb(getattr(w,'poster_path',''))}{esc(w.movie_title)}</td>
</tr>"""

    # ── Build Favorites rows ───────────────────────────────────────────────────
    fav_rows = ""
    for f in favorites:
        fav_rows += f"""<tr class="data-row" data-search="{esc(f.movie_title)} {f.user_id} {f.id}">
  <td>{f.id}</td><td>{f.user_id}</td><td>{f.movie_id}</td>
  <td>{poster_thumb(getattr(f,'poster_path',''))}{esc(f.movie_title)}</td>
</tr>"""

    # ── Build Reviews rows ─────────────────────────────────────────────────────
    rev_rows = ""
    for r in reviews:
        sent_cls = r.sentiment or "neutral"
        rev_text_esc = esc(r.review_text)
        preview = esc(r.review_text[:80] + ("…" if len(r.review_text) > 80 else ""))
        rev_rows += f"""<tr class="data-row" data-sentiment="{r.sentiment or ''}" data-search="{esc(r.movie_title)} {r.user_id} {r.id} {esc(r.review_text[:50])}">
  <td>{r.id}</td><td>{r.user_id}</td>
  <td>{esc(r.movie_title)}</td>
  <td class="review-text-cell" title="{rev_text_esc}">{preview}</td>
  <td><span class="sent-badge {sent_cls}">{r.sentiment or '—'}</span></td>
  <td class="action-cell">
    <button class="btn-act btn-edit" onclick="editReview({r.id},`{rev_text_esc}`)">Edit</button>
    <button class="btn-act btn-delete" onclick="adminAction('DELETE','/admin/reviews/{r.id}',this,'delete_review',{r.id})">Del</button>
  </td>
</tr>"""

    # ── Build Messages rows ────────────────────────────────────────────────────
    msg_rows = ""
    for m in messages:
        read_cls = "" if m.is_read else " row-unread"
        date_str = str(m.created_at)[:16] if m.created_at else "—"
        msg_rows += f"""<tr class="data-row{read_cls}" data-search="{esc(m.name)} {esc(m.email)} {esc(m.subject)}">
  <td>{m.id}</td>
  <td>{esc(m.name)}</td>
  <td>{esc(m.email)}</td>
  <td>{esc(m.subject)}</td>
  <td class="review-text-cell" title="{esc(m.message)}">{esc(m.message[:100])}{"…" if len(m.message)>100 else ""}</td>
  <td>{date_str}</td>
  <td>{'✅ Read' if m.is_read else '🔵 New'}</td>
  <td class="action-cell">
    {'<button class="btn-act btn-edit" onclick="adminAction(\'POST\',\'/admin/messages/' + str(m.id) + '/read\',this,\'read_msg\',' + str(m.id) + ')">Mark Read</button>' if not m.is_read else ''}
    <button class="btn-act btn-delete" onclick="adminAction('DELETE','/admin/messages/{m.id}',this,'delete_msg',{m.id})">Del</button>
  </td>
</tr>"""

    # ── Build user modal data (JSON-safe) ─────────────────────────────────────
    user_data_js = "{"
    for u in users:
        u_reviews = [r for r in reviews if r.user_id == u.id]
        u_wl = [w for w in watchlist if w.user_id == u.id]
        u_fav = [f for f in favorites if f.user_id == u.id]
        pos = sum(1 for r in u_reviews if r.sentiment == "positive")
        neg = sum(1 for r in u_reviews if r.sentiment == "negative")
        neu = sum(1 for r in u_reviews if r.sentiment == "neutral")
        wl_titles = [esc(w.movie_title) for w in u_wl[:8]]
        fav_titles = [esc(f.movie_title) for f in u_fav[:8]]
        rev_list = [{"text": esc(r.review_text[:80]), "sent": r.sentiment or "", "movie": esc(r.movie_title)} for r in u_reviews[:8]]

        user_data_js += f"""
  {u.id}: {{
    id:{u.id}, username:"{esc(u.username)}", email:"{esc(u.email)}",
    age:{u.age or 'null'}, gender:"{esc(u.gender or '')}",
    genres:"{esc(u.favorite_genres or '')}",
    banned:{str(u.is_banned).lower()},
    joined:"{str(u.created_at)[:10] if u.created_at else ''}",
    reviews:{len(u_reviews)}, watchlist:{len(u_wl)}, favorites:{len(u_fav)},
    pos:{pos}, neg:{neg}, neu:{neu},
    wl_titles:{str(wl_titles).replace("'",'"')},
    fav_titles:{str(fav_titles).replace("'",'"')},
    rev_list:{str(rev_list).replace("'",'"')}
  }},"""
    user_data_js += "\n}"

    html = f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CineAI Admin Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Segoe UI',system-ui,sans-serif;background:#080812;color:#e2e8f0;min-height:100vh}}
:root{{--accent:#7c3aed;--accent2:#e50914;--bg-card:#0f0f22;--bg-sec:#13132a;--border:#1a1a35;--muted:#475569}}

/* Header */
header{{background:linear-gradient(120deg,#3b1f8c,#6d28d9,#7e22ce);padding:16px 28px;
        display:flex;align-items:center;justify-content:space-between;
        box-shadow:0 4px 24px rgba(0,0,0,.5)}}
.ht{{font-size:20px;font-weight:800}}.hs{{font-size:11px;opacity:.7;margin-top:3px}}
.hbtns{{display:flex;gap:8px;align-items:center}}
.pill{{background:rgba(255,255,255,.13);border:1px solid rgba(255,255,255,.22);
       border-radius:30px;padding:5px 13px;font-size:12px;font-weight:600}}
.header-btn{{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.2);
             color:#fff;border-radius:8px;padding:7px 14px;font-size:12px;
             font-weight:600;cursor:pointer}}
.header-btn:hover{{background:rgba(255,255,255,.2)}}

/* Stat cards */
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));
        gap:10px;padding:16px 24px}}
.card{{background:var(--bg-card);border:1px solid var(--border);border-radius:12px;
       padding:16px;text-align:center;cursor:pointer;transition:.2s}}
.card:hover,.card.active{{border-color:var(--accent);background:#18183a}}
.card .n{{font-size:28px;font-weight:800;color:#a78bfa}}
.card .l{{font-size:11px;color:#64748b;margin-top:3px;text-transform:uppercase;letter-spacing:.4px}}
.card .sub{{font-size:10px;color:#334155;margin-top:2px}}

/* Tabs */
.tabs{{display:flex;padding:0 24px;border-bottom:1px solid var(--border);overflow-x:auto}}
.tab{{padding:11px 16px;font-size:13px;font-weight:500;color:#64748b;
      border-bottom:2px solid transparent;cursor:pointer;transition:.15s;white-space:nowrap}}
.tab:hover{{color:#c4b5fd}}.tab.active{{color:#c4b5fd;border-bottom-color:var(--accent)}}
.badge{{background:#e50914;color:#fff;border-radius:10px;padding:1px 6px;
        font-size:10px;font-weight:800;margin-left:5px}}

/* Panel */
.panel{{display:none;padding:16px 24px 40px}}.panel.active{{display:block}}

/* Toolbar */
.toolbar{{display:flex;align-items:center;gap:10px;margin-bottom:12px;flex-wrap:wrap}}
.sw{{position:relative;flex:1;min-width:200px;max-width:380px}}
.si{{position:absolute;left:11px;top:50%;transform:translateY(-50%);font-size:13px;pointer-events:none}}
.sbox{{width:100%;padding:9px 12px 9px 32px;background:var(--bg-card);
       border:1px solid var(--border);border-radius:8px;color:#e2e8f0;
       font-size:13px;outline:none;transition:.2s}}
.sbox:focus{{border-color:var(--accent);box-shadow:0 0 0 3px rgba(124,58,237,.18)}}
.rc{{font-size:12px;color:var(--muted);margin-left:auto}}
.filter-sel{{padding:8px 10px;background:var(--bg-card);border:1px solid var(--border);
             border-radius:8px;color:#e2e8f0;font-size:13px;cursor:pointer;outline:none}}
.export-btn{{background:rgba(16,185,129,.15);border:1px solid rgba(16,185,129,.3);
             color:#34d399;border-radius:8px;padding:8px 14px;font-size:12px;
             font-weight:600;cursor:pointer}}
.export-btn:hover{{background:rgba(16,185,129,.25)}}

/* Table */
.tw{{overflow-x:auto;border-radius:10px;border:1px solid var(--border)}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
thead{{background:#0a0a1a}}
th{{padding:10px 13px;text-align:left;color:var(--accent);font-weight:600;
    font-size:11px;text-transform:uppercase;letter-spacing:.5px;white-space:nowrap}}
td{{padding:9px 13px;border-top:1px solid #0f0f2a;color:#cbd5e1;
    white-space:nowrap;max-width:220px;overflow:hidden;text-overflow:ellipsis}}
tr.data-row:hover td{{background:#12122e}}
tr.hidden{{display:none}}
tr.row-banned td{{opacity:.6;background:rgba(239,68,68,.04)}}
tr.row-unread td{{background:rgba(99,102,241,.05)}}
.empty{{text-align:center;color:#334155;padding:36px;font-size:14px}}

/* Sentiment badges */
.sent-badge{{border-radius:20px;padding:2px 9px;font-size:11px;font-weight:700;
             text-transform:uppercase;white-space:nowrap}}
.sent-badge.positive{{background:rgba(16,185,129,.12);color:#34d399}}
.sent-badge.negative{{background:rgba(239,68,68,.12);color:#f87171}}
.sent-badge.neutral{{background:rgba(148,163,184,.1);color:#94a3b8}}

/* Action buttons */
.action-cell{{white-space:nowrap}}
.btn-act{{border:none;border-radius:6px;padding:4px 9px;font-size:11px;
           font-weight:700;cursor:pointer;margin-right:4px;transition:.15s}}
.btn-ban{{background:rgba(251,191,36,.12);color:#fbbf24}}
.btn-ban:hover{{background:rgba(251,191,36,.25)}}
.btn-unban{{background:rgba(16,185,129,.12);color:#34d399}}
.btn-unban:hover{{background:rgba(16,185,129,.25)}}
.btn-delete{{background:rgba(239,68,68,.12);color:#f87171}}
.btn-delete:hover{{background:rgba(239,68,68,.25)}}
.btn-edit{{background:rgba(99,102,241,.12);color:#818cf8}}
.btn-edit:hover{{background:rgba(99,102,241,.25)}}

/* Username link */
.username-link{{color:#a78bfa;cursor:pointer;font-weight:700;text-decoration:underline;
                text-underline-offset:3px}}
.username-link:hover{{color:#c4b5fd}}

/* Poster */
.poster-thumb{{width:32px;height:48px;border-radius:4px;object-fit:cover;
               margin-right:8px;vertical-align:middle;border:1px solid var(--border)}}
.no-poster{{font-size:20px;margin-right:8px;vertical-align:middle}}

/* Pagination */
.pagination{{display:flex;align-items:center;justify-content:center;gap:6px;
             margin-top:14px;flex-wrap:wrap}}
.page-btn{{background:var(--bg-card);border:1px solid var(--border);
           color:#94a3b8;border-radius:6px;padding:5px 11px;
           font-size:12px;cursor:pointer;transition:.15s}}
.page-btn:hover,.page-btn.active{{background:var(--accent);color:#fff;border-color:var(--accent)}}
.page-info{{color:var(--muted);font-size:12px;padding:0 8px}}

/* Analytics */
.analytics-grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:20px}}
.analytics-card{{background:var(--bg-card);border:1px solid var(--border);
                 border-radius:12px;padding:20px}}
.analytics-title{{font-size:13px;font-weight:700;color:#94a3b8;margin-bottom:16px;
                  text-transform:uppercase;letter-spacing:.5px}}
.stat-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}}
.stat-item{{background:var(--bg-sec);border-radius:8px;padding:14px;text-align:center}}
.stat-num{{font-size:26px;font-weight:800;color:#a78bfa}}
.stat-label{{font-size:10px;color:#64748b;margin-top:4px;text-transform:uppercase}}

/* User modal */
.modal-overlay{{position:fixed;inset:0;background:rgba(0,0,0,.8);backdrop-filter:blur(4px);
                z-index:1000;display:none;align-items:center;justify-content:center}}
.modal-overlay.open{{display:flex}}
.modal{{background:#0f0f22;border:1px solid #1e1e3f;border-radius:16px;padding:28px;
        width:min(700px,95vw);max-height:90vh;overflow-y:auto;position:relative}}
.modal-close{{position:absolute;top:16px;right:16px;background:rgba(255,255,255,.08);
              border:none;color:#94a3b8;width:30px;height:30px;border-radius:50%;
              font-size:16px;cursor:pointer;display:flex;align-items:center;justify-content:center}}
.modal-close:hover{{background:rgba(239,68,68,.2);color:#f87171}}
.modal-username{{font-size:22px;font-weight:800;margin-bottom:4px}}
.modal-email{{color:#64748b;font-size:13px;margin-bottom:18px}}
.modal-grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:18px}}
.modal-stat{{background:var(--bg-sec);border-radius:8px;padding:12px;text-align:center}}
.modal-stat .n{{font-size:22px;font-weight:800;color:#a78bfa}}
.modal-stat .l{{font-size:10px;color:#64748b;margin-top:3px;text-transform:uppercase}}
.modal-section{{margin-bottom:14px}}
.modal-section-title{{font-size:12px;font-weight:700;color:#7c3aed;
                       text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px}}
.modal-pills{{display:flex;flex-wrap:wrap;gap:6px}}
.modal-pill{{background:var(--bg-sec);border:1px solid var(--border);border-radius:20px;
             padding:3px 10px;font-size:12px;color:#cbd5e1}}
.modal-rev{{background:var(--bg-sec);border-radius:8px;padding:10px;margin-bottom:6px}}
.modal-rev-text{{font-size:12px;color:#94a3b8;line-height:1.4}}
.modal-act-row{{display:flex;gap:8px;margin-top:18px;padding-top:16px;border-top:1px solid var(--border)}}

/* Edit modal */
.edit-modal{{background:#0f0f22;border:1px solid #1e1e3f;border-radius:14px;
             padding:24px;width:min(540px,95vw);position:relative}}
.edit-modal textarea{{width:100%;background:#080812;border:1px solid var(--border);
                       border-radius:8px;color:#e2e8f0;padding:12px;font-size:13px;
                       resize:vertical;min-height:100px;outline:none;margin:12px 0}}
.edit-modal textarea:focus{{border-color:var(--accent)}}
.edit-modal-btns{{display:flex;gap:10px;justify-content:flex-end}}
.btn-save{{background:linear-gradient(135deg,var(--accent),#e040fb);
           color:#fff;border:none;border-radius:8px;padding:9px 20px;
           font-size:13px;font-weight:700;cursor:pointer}}
.btn-cancel{{background:var(--bg-sec);border:1px solid var(--border);
             color:#94a3b8;border-radius:8px;padding:9px 16px;font-size:13px;cursor:pointer}}

/* Toast */
.toast{{position:fixed;bottom:24px;right:24px;padding:12px 20px;border-radius:10px;
        font-size:13px;font-weight:600;z-index:2000;animation:fadeIn .2s ease;
        pointer-events:none}}
.toast.ok{{background:#065f46;color:#34d399;border:1px solid rgba(52,211,153,.3)}}
.toast.err{{background:#7f1d1d;color:#f87171;border:1px solid rgba(248,113,113,.3)}}
@keyframes fadeIn{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:none}}}}

.genres-cell{{max-width:180px;overflow:hidden;text-overflow:ellipsis}}
.review-text-cell{{max-width:260px;overflow:hidden;text-overflow:ellipsis;cursor:help}}

footer{{text-align:center;padding:16px;color:#1e293b;font-size:12px;border-top:1px solid #0a0a20;margin-top:8px}}

@media(max-width:640px){{
  .analytics-grid{{grid-template-columns:1fr}}
  .modal-grid{{grid-template-columns:1fr 1fr}}
  .cards{{grid-template-columns:repeat(3,1fr)}}
}}
</style></head><body>

<!-- Header -->
<header>
  <div>
    <div class="ht">🎬 CineAI Admin Dashboard</div>
    <div class="hs">Live PostgreSQL database viewer</div>
  </div>
  <div class="hbtns">
    <button class="header-btn" onclick="location.reload()">🔄 Refresh</button>
    <span class="pill">🔒 Admin</span>
  </div>
</header>

<!-- Stat cards -->
<div class="cards">
  <div class="card active" id="c-analytics" onclick="sw('analytics')">
    <div class="n">{len(users)}</div><div class="l">👤 Users</div>
    <div class="sub">{banned_count} banned</div>
  </div>
  <div class="card" id="c-watchlist" onclick="sw('watchlist')">
    <div class="n">{len(watchlist)}</div><div class="l">📋 Watchlist</div>
  </div>
  <div class="card" id="c-favorites" onclick="sw('favorites')">
    <div class="n">{len(favorites)}</div><div class="l">❤️ Favorites</div>
  </div>
  <div class="card" id="c-reviews" onclick="sw('reviews')">
    <div class="n">{len(reviews)}</div><div class="l">💬 Reviews</div>
  </div>
  <div class="card" id="c-messages" onclick="sw('messages')">
    <div class="n">{len(messages)}</div><div class="l">📩 Messages</div>
    <div class="sub" style="color:#e50914">{unread_msgs} unread</div>
  </div>
</div>

<!-- Tabs -->
<div class="tabs">
  <div class="tab active" id="tb-analytics" onclick="sw('analytics')">📊 Analytics</div>
  <div class="tab" id="tb-users"     onclick="sw('users')">👤 Users ({len(users)})</div>
  <div class="tab" id="tb-watchlist" onclick="sw('watchlist')">📋 Watchlist</div>
  <div class="tab" id="tb-favorites" onclick="sw('favorites')">❤️ Favorites</div>
  <div class="tab" id="tb-reviews"   onclick="sw('reviews')">💬 Reviews</div>
  <div class="tab" id="tb-messages"  onclick="sw('messages')">📩 Messages{f'<span class="badge">{unread_msgs}</span>' if unread_msgs > 0 else ''}</div>
</div>

<!-- ── ANALYTICS PANEL ── -->
<div class="panel active" id="panel-analytics">
  <div class="analytics-grid">
    <div class="analytics-card">
      <div class="analytics-title">📊 Platform Overview</div>
      <div class="stat-grid">
        <div class="stat-item"><div class="stat-num">{len(users)}</div><div class="stat-label">Users</div></div>
        <div class="stat-item"><div class="stat-num">{len(reviews)}</div><div class="stat-label">Reviews</div></div>
        <div class="stat-item"><div class="stat-num">{len(watchlist)}</div><div class="stat-label">Watchlist</div></div>
        <div class="stat-item"><div class="stat-num">{len(favorites)}</div><div class="stat-label">Favorites</div></div>
        <div class="stat-item"><div class="stat-num">{banned_count}</div><div class="stat-label" style="color:#f87171">Banned</div></div>
        <div class="stat-item"><div class="stat-num">{unread_msgs}</div><div class="stat-label" style="color:#818cf8">Unread Msgs</div></div>
      </div>
    </div>
    <div class="analytics-card">
      <div class="analytics-title">😊 Sentiment Distribution</div>
      <canvas id="sentChart" height="160"></canvas>
    </div>
  </div>
  <div class="analytics-card" style="margin-bottom:16px">
    <div class="analytics-title">👤 Quick User Actions</div>
    <p style="color:#64748b;font-size:13px">Click the <strong style="color:#a78bfa">Users</strong> tab to manage users — ban, delete, or view full profile details.</p>
    <div style="margin-top:12px;display:flex;gap:10px;flex-wrap:wrap">
      <button class="export-btn" onclick="exportCSV('users')">📥 Export Users CSV</button>
      <button class="export-btn" onclick="exportCSV('reviews')">📥 Export Reviews CSV</button>
      <button class="export-btn" onclick="exportCSV('messages')">📥 Export Messages CSV</button>
    </div>
  </div>
</div>

<!-- ── USERS PANEL ── -->
<div class="panel" id="panel-users">
  <div class="toolbar">
    <div class="sw"><span class="si">🔍</span>
      <input class="sbox" id="srch-users" type="text" placeholder="Search by username, email, ID…" oninput="doFilter('users')"/>
    </div>
    <select class="filter-sel" id="filter-banned" onchange="doFilter('users')">
      <option value="">All Users</option>
      <option value="active">🟢 Active only</option>
      <option value="banned">🔴 Banned only</option>
    </select>
    <span class="rc" id="cnt-users">{len(users)} records</span>
    <button class="export-btn" onclick="exportCSV('users')">📥 CSV</button>
  </div>
  <div class="tw">
    <table id="tbl-users">
      <thead><tr><th>ID</th><th>Username</th><th>Email</th><th>Age</th><th>Gender</th><th>Genres</th><th>Joined</th><th>Status</th><th>Actions</th></tr></thead>
      <tbody id="body-users">{user_rows if user_rows else '<tr><td colspan="9" class="empty">No users yet</td></tr>'}</tbody>
    </table>
  </div>
  <div class="pagination" id="pg-users"></div>
</div>

<!-- ── WATCHLIST PANEL ── -->
<div class="panel" id="panel-watchlist">
  <div class="toolbar">
    <div class="sw"><span class="si">🔍</span>
      <input class="sbox" id="srch-watchlist" type="text" placeholder="Search movie title, user ID…" oninput="doFilter('watchlist')"/>
    </div>
    <span class="rc" id="cnt-watchlist">{len(watchlist)} records</span>
    <button class="export-btn" onclick="exportCSV('watchlist')">📥 CSV</button>
  </div>
  <div class="tw">
    <table id="tbl-watchlist">
      <thead><tr><th>ID</th><th>User ID</th><th>Movie ID</th><th>Movie Title</th></tr></thead>
      <tbody id="body-watchlist">{wl_rows if wl_rows else '<tr><td colspan="4" class="empty">No watchlist items yet</td></tr>'}</tbody>
    </table>
  </div>
  <div class="pagination" id="pg-watchlist"></div>
</div>

<!-- ── FAVORITES PANEL ── -->
<div class="panel" id="panel-favorites">
  <div class="toolbar">
    <div class="sw"><span class="si">🔍</span>
      <input class="sbox" id="srch-favorites" type="text" placeholder="Search movie title, user ID…" oninput="doFilter('favorites')"/>
    </div>
    <span class="rc" id="cnt-favorites">{len(favorites)} records</span>
    <button class="export-btn" onclick="exportCSV('favorites')">📥 CSV</button>
  </div>
  <div class="tw">
    <table id="tbl-favorites">
      <thead><tr><th>ID</th><th>User ID</th><th>Movie ID</th><th>Movie Title</th></tr></thead>
      <tbody id="body-favorites">{fav_rows if fav_rows else '<tr><td colspan="4" class="empty">No favorites yet</td></tr>'}</tbody>
    </table>
  </div>
  <div class="pagination" id="pg-favorites"></div>
</div>

<!-- ── REVIEWS PANEL ── -->
<div class="panel" id="panel-reviews">
  <div class="toolbar">
    <div class="sw"><span class="si">🔍</span>
      <input class="sbox" id="srch-reviews" type="text" placeholder="Search movie, user ID, review text…" oninput="doFilter('reviews')"/>
    </div>
    <select class="filter-sel" id="filter-sentiment" onchange="doFilter('reviews')">
      <option value="">All Sentiments</option>
      <option value="positive">😊 Positive</option>
      <option value="negative">😞 Negative</option>
      <option value="neutral">😐 Neutral</option>
    </select>
    <span class="rc" id="cnt-reviews">{len(reviews)} records</span>
    <button class="export-btn" onclick="exportCSV('reviews')">📥 CSV</button>
  </div>
  <div class="tw">
    <table id="tbl-reviews">
      <thead><tr><th>ID</th><th>User ID</th><th>Movie</th><th>Review</th><th>Sentiment</th><th>Actions</th></tr></thead>
      <tbody id="body-reviews">{rev_rows if rev_rows else '<tr><td colspan="6" class="empty">No reviews yet</td></tr>'}</tbody>
    </table>
  </div>
  <div class="pagination" id="pg-reviews"></div>
</div>

<!-- ── MESSAGES PANEL ── -->
<div class="panel" id="panel-messages">
  <div class="toolbar">
    <div class="sw"><span class="si">🔍</span>
      <input class="sbox" id="srch-messages" type="text" placeholder="Search name, email, subject…" oninput="doFilter('messages')"/>
    </div>
    <span class="rc" id="cnt-messages">{len(messages)} records</span>
    <button class="export-btn" onclick="exportCSV('messages')">📥 CSV</button>
  </div>
  <div class="tw">
    <table id="tbl-messages">
      <thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Subject</th><th>Message</th><th>Date</th><th>Status</th><th>Actions</th></tr></thead>
      <tbody id="body-messages">{msg_rows if msg_rows else '<tr><td colspan="8" class="empty">No messages yet</td></tr>'}</tbody>
    </table>
  </div>
  <div class="pagination" id="pg-messages"></div>
</div>

<!-- User Profile Modal -->
<div class="modal-overlay" id="userModal" onclick="if(event.target===this)closeModal()">
  <div class="modal">
    <button class="modal-close" onclick="closeModal()">✕</button>
    <div id="modal-content"></div>
  </div>
</div>

<!-- Edit Review Modal -->
<div class="modal-overlay" id="editModal" onclick="if(event.target===this)closeEditModal()">
  <div class="edit-modal">
    <button class="modal-close" onclick="closeEditModal()">✕</button>
    <h3 style="margin-bottom:8px;font-size:16px">✏️ Edit Review</h3>
    <p style="color:#64748b;font-size:12px">Edit the review text below</p>
    <textarea id="edit-textarea" rows="5"></textarea>
    <div class="edit-modal-btns">
      <button class="btn-cancel" onclick="closeEditModal()">Cancel</button>
      <button class="btn-save" onclick="saveReview()">💾 Save</button>
    </div>
  </div>
</div>

<!-- Toast -->
<div class="toast" id="toast" style="display:none"></div>

<footer>CineAI Admin Dashboard &bull; PostgreSQL &bull; 🔒 Admin Only</footer>

<script>
const KEY = '{key}';
const TABS = ['analytics','users','watchlist','favorites','reviews','messages'];
const PER_PAGE = 25;
const PAGE_STATE = {{}};
const USER_DATA = {user_data_js};

// ── Tab switch ───────────────────────────────────────────────────────
function sw(name) {{
  TABS.forEach(t => {{
    document.getElementById('panel-'+t)?.classList.toggle('active', t===name);
    document.getElementById('tb-'+t)?.classList.toggle('active', t===name);
    document.getElementById('c-'+t)?.classList.toggle('active', t===name);
  }});
  if (name !== 'analytics' && !PAGE_STATE[name]) {{
    PAGE_STATE[name] = 1;
    renderPage(name);
  }}
}}

// ── Pagination ───────────────────────────────────────────────────────
function renderPage(tid) {{
  const tbody = document.getElementById('body-'+tid);
  if (!tbody) return;
  const rows = Array.from(tbody.querySelectorAll('tr.data-row:not(.hidden)'));
  const page = PAGE_STATE[tid] || 1;
  const total = rows.length;
  const pages = Math.ceil(total / PER_PAGE) || 1;
  rows.forEach((r, i) => r.style.display = (i >= (page-1)*PER_PAGE && i < page*PER_PAGE) ? '' : 'none');
  const pg = document.getElementById('pg-'+tid);
  if (!pg) return;
  let html = '';
  if (pages > 1) {{
    html += `<button class="page-btn" onclick="goPage('${{tid}}',${{Math.max(1,page-1)}})">‹</button>`;
    for (let p=Math.max(1,page-2); p<=Math.min(pages,page+2); p++)
      html += `<button class="page-btn${{p===page?' active':''}}" onclick="goPage('${{tid}}',${{p}})">${{p}}</button>`;
    html += `<button class="page-btn" onclick="goPage('${{tid}}',${{Math.min(pages,page+1)}})">›</button>`;
    html += `<span class="page-info">Page ${{page}} of ${{pages}} (${{total}} records)</span>`;
  }}
  pg.innerHTML = html;
}}

function goPage(tid, p) {{ PAGE_STATE[tid]=p; renderPage(tid); }}

// ── Filter / Search ──────────────────────────────────────────────────
function doFilter(tid) {{
  const q = (document.getElementById('srch-'+tid)?.value||'').toLowerCase().trim();
  const sentFilter = document.getElementById('filter-sentiment')?.value || '';
  const banFilter  = document.getElementById('filter-banned')?.value || '';
  const rows = document.querySelectorAll('#body-'+tid+' tr.data-row');
  let vis=0;
  rows.forEach(r => {{
    const txt = (r.dataset.search||'').toLowerCase();
    const sent = r.dataset.sentiment || '';
    const banned = r.classList.contains('row-banned');
    let ok = !q || txt.includes(q);
    if (sentFilter) ok = ok && sent === sentFilter;
    if (banFilter === 'active') ok = ok && !banned;
    if (banFilter === 'banned') ok = ok && banned;
    r.classList.toggle('hidden', !ok);
    if (ok) vis++;
  }});
  const el = document.getElementById('cnt-'+tid);
  if (el) el.textContent = (q||sentFilter||banFilter ? vis+' of '+rows.length : rows.length)+' records';
  PAGE_STATE[tid]=1; renderPage(tid);
}}

// ── Admin actions ────────────────────────────────────────────────────
async function adminAction(method, endpoint, btn, action, id) {{
  if (action==='delete_user'||action==='delete_review'||action==='delete_msg') {{
    if (!confirm('Are you sure you want to delete this? This cannot be undone.')) return;
  }}
  btn.disabled = true; btn.textContent = '…';
  try {{
    const r = await fetch(endpoint+'?key='+KEY, {{ method }});
    const data = await r.json();
    if (!r.ok) throw new Error(data.detail || 'Error');
    showToast('✅ Done!', 'ok');
    setTimeout(() => location.reload(), 800);
  }} catch(e) {{
    showToast('❌ '+e.message, 'err');
    btn.disabled=false; btn.textContent=btn.textContent.replace('…','Retry');
  }}
}}

// ── User profile modal ───────────────────────────────────────────────
function showUserModal(uid) {{
  const u = USER_DATA[uid];
  if (!u) return;
  const sentColor = u.pos>u.neg ? '#34d399' : u.neg>u.pos ? '#f87171' : '#94a3b8';
  const wlPills = u.wl_titles.map(t=>`<span class="modal-pill">${{t}}</span>`).join('');
  const favPills = u.fav_titles.map(t=>`<span class="modal-pill">${{t}}</span>`).join('');
  const revList = u.rev_list.map(r=>`
    <div class="modal-rev">
      <span class="sent-badge ${{r.sent}}">${{r.sent||'—'}}</span>
      <span style="font-size:11px;color:#64748b;margin-left:6px">${{r.movie}}</span>
      <div class="modal-rev-text" style="margin-top:5px">${{r.text}}</div>
    </div>`).join('');
  document.getElementById('modal-content').innerHTML = `
    <div class="modal-username">${{u.banned?'🔴 ':''}}${{u.username}}</div>
    <div class="modal-email">${{u.email}}</div>
    <div class="modal-grid">
      <div class="modal-stat"><div class="n">${{u.reviews}}</div><div class="l">Reviews</div></div>
      <div class="modal-stat"><div class="n">${{u.watchlist}}</div><div class="l">Watchlist</div></div>
      <div class="modal-stat"><div class="n">${{u.favorites}}</div><div class="l">Favorites</div></div>
      <div class="modal-stat"><div class="n" style="color:${{sentColor}}">${{u.pos>u.neg?'😊 Positive':u.neg>u.pos?'😞 Negative':'😐 Neutral'}}</div><div class="l">Mood</div></div>
    </div>
    <div class="modal-section">
      <div class="modal-section-title">ℹ️ Info</div>
      <p style="font-size:13px;color:#94a3b8">Age: ${{u.age||'—'}} &bull; Gender: ${{u.gender||'—'}} &bull; Joined: ${{u.joined}} &bull; ID: #${{u.id}}</p>
    </div>
    ${{u.genres?`<div class="modal-section"><div class="modal-section-title">🎬 Favourite Genres</div><p style="font-size:13px;color:#cbd5e1">${{u.genres}}</p></div>`:''}}
    ${{wlPills?`<div class="modal-section"><div class="modal-section-title">📋 Watchlist (top 8)</div><div class="modal-pills">${{wlPills}}</div></div>`:''}}
    ${{favPills?`<div class="modal-section"><div class="modal-section-title">❤️ Favorites (top 8)</div><div class="modal-pills">${{favPills}}</div></div>`:''}}
    ${{revList?`<div class="modal-section"><div class="modal-section-title">💬 Recent Reviews (top 8)</div>${{revList}}</div>`:''}}
    <div class="modal-act-row">
      ${{u.banned
        ? `<button class="btn-act btn-unban" style="padding:8px 16px;font-size:13px" onclick="adminAction('POST','/admin/users/${{u.id}}/unban',this,'unban')">✅ Unban User</button>`
        : `<button class="btn-act btn-ban"  style="padding:8px 16px;font-size:13px" onclick="adminAction('POST','/admin/users/${{u.id}}/ban',this,'ban')">🚫 Ban User</button>`
      }}
      <button class="btn-act btn-delete" style="padding:8px 16px;font-size:13px" onclick="adminAction('DELETE','/admin/users/${{u.id}}',this,'delete_user',${{u.id}})">🗑️ Delete User</button>
    </div>`;
  document.getElementById('userModal').classList.add('open');
}}
function closeModal() {{ document.getElementById('userModal').classList.remove('open'); }}

// ── Edit review modal ────────────────────────────────────────────────
let _editId = null;
function editReview(id, text) {{
  _editId = id;
  document.getElementById('edit-textarea').value = text.replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&amp;/g,'&');
  document.getElementById('editModal').classList.add('open');
}}
function closeEditModal() {{ document.getElementById('editModal').classList.remove('open'); _editId=null; }}
async function saveReview() {{
  if (!_editId) return;
  const text = document.getElementById('edit-textarea').value.trim();
  if (!text) return showToast('Review text is empty','err');
  try {{
    const r = await fetch('/admin/reviews/'+_editId+'?key='+KEY, {{
      method:'PUT', headers:{{'Content-Type':'application/json'}},
      body: JSON.stringify({{review_text: text}})
    }});
    if (!r.ok) throw new Error('Failed');
    showToast('✅ Review updated','ok');
    closeEditModal();
    setTimeout(() => location.reload(), 800);
  }} catch(e) {{ showToast('❌ '+e.message,'err'); }}
}}

// ── CSV Export ───────────────────────────────────────────────────────
function exportCSV(tid) {{
  const tbl = document.getElementById('tbl-'+tid);
  if (!tbl) return;
  const rows = Array.from(tbl.querySelectorAll('tr')).filter(r=>!r.classList.contains('hidden'));
  const csv = rows.map(r=>Array.from(r.querySelectorAll('th,td')).slice(0,-1)
    .map(c=>'"'+c.textContent.trim().replace(/"/g,'""')+'"').join(',')).join('\\n');
  const a=document.createElement('a');
  a.href='data:text/csv;charset=utf-8,'+encodeURIComponent(csv);
  a.download='cineai_'+tid+'_'+new Date().toISOString().slice(0,10)+'.csv';
  a.click();
}}

// ── Toast ─────────────────────────────────────────────────────────────
function showToast(msg, type='ok') {{
  const t=document.getElementById('toast');
  t.textContent=msg; t.className='toast '+type; t.style.display='block';
  setTimeout(()=>{{t.style.display='none';}}, 2800);
}}

// ── Chart.js Sentiment Pie ────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {{
  const ctx = document.getElementById('sentChart');
  if (!ctx) return;
  new Chart(ctx, {{
    type:'doughnut',
    data:{{
      labels:['Positive','Negative','Neutral'],
      datasets:[{{
        data:[{pos_count},{neg_count},{neu_count}],
        backgroundColor:['rgba(16,185,129,.7)','rgba(239,68,68,.7)','rgba(148,163,184,.5)'],
        borderColor:['#10b981','#ef4444','#94a3b8'],
        borderWidth:1.5, hoverOffset:6
      }}]
    }},
    options:{{
      responsive:true, maintainAspectRatio:true,
      plugins:{{
        legend:{{position:'bottom',labels:{{color:'#94a3b8',font:{{size:12}},padding:16}}}},
        tooltip:{{callbacks:{{label:ctx=>` ${{ctx.label}}: ${{ctx.parsed}} reviews`}}}}
      }}
    }}
  }});

  // Init pagination for all panels
  ['users','watchlist','favorites','reviews','messages'].forEach(t => {{
    PAGE_STATE[t]=1; renderPage(t);
  }});
}});
</script>
</body></html>"""

    return HTMLResponse(html)
