# Admin dashboard — server-side data injection
# Data is embedded as JSON in the page — NO async fetch for initial load
# 30s polling only for live-update notifications

import json
import os
from sqlalchemy import text
from database import SessionLocal

ADMIN_SECRET = os.getenv("ADMIN_SECRET", "cineai-admin-2024")


def _fmt(dt):
    return str(dt)[:16].replace("T", " ") if dt else "-"


def _get_data():
    """Fetch all dashboard data from PostgreSQL. Returns dict."""
    db = SessionLocal()
    user_list, wl_list, fav_list, rev_list, msg_list, popular = [], [], [], [], [], []
    try:
        rows = db.execute(text("""
            SELECT u.id, u.username, u.email, u.age, u.gender,
                   u.favorite_genres, COALESCE(u.is_banned,false),
                   u.created_at, u.last_login,
                   COUNT(DISTINCT w.id), COUNT(DISTINCT f.id), COUNT(DISTINCT r.id)
            FROM users u
            LEFT JOIN watchlist w ON w.user_id=u.id
            LEFT JOIN favorites f ON f.user_id=u.id
            LEFT JOIN reviews r   ON r.user_id=u.id
            GROUP BY u.id ORDER BY u.id
        """)).fetchall()
        for row in rows:
            user_list.append({
                "id": row[0], "username": row[1] or "", "email": row[2] or "",
                "age": row[3], "gender": row[4] or "",
                "favorite_genres": row[5] or "", "is_banned": bool(row[6]),
                "created_at": _fmt(row[7]), "last_login": _fmt(row[8]),
                "wl_count": int(row[9] or 0), "fav_count": int(row[10] or 0),
                "rev_count": int(row[11] or 0),
            })
    except Exception as e:
        db.rollback()
        print(f"[ADMIN] users query error: {e}")
        try:
            rows = db.execute(text(
                "SELECT id,username,email,age,gender,favorite_genres,created_at FROM users ORDER BY id"
            )).fetchall()
            for row in rows:
                user_list.append({
                    "id": row[0], "username": row[1] or "", "email": row[2] or "",
                    "age": row[3], "gender": row[4] or "", "favorite_genres": row[5] or "",
                    "is_banned": False, "created_at": _fmt(row[6]), "last_login": "-",
                    "wl_count": 0, "fav_count": 0, "rev_count": 0,
                })
        except Exception:
            db.rollback()

    try:
        for row in db.execute(text(
            "SELECT id,user_id,movie_id,movie_title,COALESCE(poster_path,''),added_at FROM watchlist ORDER BY id"
        )).fetchall():
            wl_list.append({"id": row[0], "user_id": row[1], "movie_id": row[2],
                            "movie_title": row[3] or "", "poster_path": row[4] or "",
                            "added_at": _fmt(row[5])})
    except Exception:
        db.rollback()

    try:
        for row in db.execute(text(
            "SELECT id,user_id,movie_id,movie_title,COALESCE(poster_path,''),added_at FROM favorites ORDER BY id"
        )).fetchall():
            fav_list.append({"id": row[0], "user_id": row[1], "movie_id": row[2],
                             "movie_title": row[3] or "", "poster_path": row[4] or "",
                             "added_at": _fmt(row[5])})
    except Exception:
        db.rollback()

    try:
        for row in db.execute(text(
            "SELECT id,user_id,movie_id,movie_title,review_text,sentiment,created_at FROM reviews ORDER BY id DESC"
        )).fetchall():
            rev_list.append({"id": row[0], "user_id": row[1], "movie_id": row[2],
                             "movie_title": row[3] or "", "review_text": row[4] or "",
                             "sentiment": row[5] or "", "created_at": _fmt(row[6])})
    except Exception:
        db.rollback()

    try:
        for row in db.execute(text(
            "SELECT id,name,email,subject,message,is_read,created_at FROM contact_messages ORDER BY created_at DESC"
        )).fetchall():
            msg_list.append({"id": row[0], "name": row[1] or "", "email": row[2] or "",
                             "subject": row[3] or "", "message": row[4] or "",
                             "is_read": bool(row[5]), "created_at": _fmt(row[6])})
    except Exception:
        db.rollback()

    try:
        rows = db.execute(text("""
            SELECT movie_title, COUNT(*) cnt FROM (
                SELECT movie_title FROM watchlist UNION ALL SELECT movie_title FROM favorites
            ) t WHERE movie_title IS NOT NULL AND movie_title!='' GROUP BY movie_title ORDER BY cnt DESC LIMIT 10
        """)).fetchall()
        popular = [{"title": r[0], "count": int(r[1])} for r in rows]
    except Exception:
        db.rollback()

    db.close()

    pos = sum(1 for r in rev_list if r["sentiment"] == "positive")
    neg = sum(1 for r in rev_list if r["sentiment"] == "negative")
    neu = sum(1 for r in rev_list if r["sentiment"] == "neutral")
    banned = sum(1 for u in user_list if u["is_banned"])
    unread = sum(1 for m in msg_list if not m["is_read"])
    active = sum(1 for u in user_list if u["rev_count"] + u["wl_count"] + u["fav_count"] > 0)
    top_users = sorted(user_list,
                       key=lambda u: u["rev_count"] + u["wl_count"] + u["fav_count"],
                       reverse=True)[:5]

    return {
        "stats": {
            "users": len(user_list), "watchlist": len(wl_list),
            "favorites": len(fav_list), "reviews": len(rev_list),
            "messages": len(msg_list), "banned": banned,
            "unread_msgs": unread, "active": active,
            "pos": pos, "neg": neg, "neu": neu,
        },
        "users": user_list, "watchlist": wl_list, "favorites": fav_list,
        "reviews": rev_list, "messages": msg_list,
        "popular": popular, "top_users": top_users,
    }


def get_dashboard(key: str) -> str:
    """Return complete dashboard HTML with data embedded as JSON."""
    data = _get_data()
    # CRITICAL: escape </ in JSON to prevent </script> from terminating the <script> tag early
    data_json = json.dumps(data, ensure_ascii=True, separators=(',', ':'))
    data_json = data_json.replace('</', '<\\/')   # "</script>" → "<\/script>" (valid JSON, safe HTML)
    safe_key  = key.replace("'", "\\'").replace("\\", "\\\\")
    return _DASHBOARD_TEMPLATE.replace("__DATA_JSON__", data_json).replace("__KEY__", safe_key)


# ─── Login / Wrong-key pages ───────────────────────────────────────────────────

LOGIN_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>CineAI Admin</title>
<style>*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',sans-serif;background:#080812;color:#e2e8f0;display:flex;align-items:center;justify-content:center;min-height:100vh}
.card{background:#0f0f22;border:1px solid #252545;border-radius:18px;padding:52px 44px;text-align:center;width:400px;box-shadow:0 24px 64px rgba(0,0,0,.7)}
h1{font-size:26px;font-weight:800;margin-bottom:8px}p{color:#64748b;font-size:13px;margin-bottom:32px}
input{width:100%;padding:14px 16px;background:#080812;border:1px solid #2d2d5e;border-radius:10px;color:#e2e8f0;font-size:15px;margin-bottom:16px;outline:none;letter-spacing:2px}
input:focus{border-color:#7c3aed;box-shadow:0 0 0 3px rgba(124,58,237,.2)}
button{width:100%;padding:14px;background:linear-gradient(135deg,#6c3ef4,#e040fb);color:#fff;border:none;border-radius:10px;font-size:15px;font-weight:700;cursor:pointer;transition:.2s}
button:hover{opacity:.9;transform:translateY(-1px)}</style></head><body>
<div class="card"><div style="font-size:52px;margin-bottom:16px">&#128274;</div>
<h1>CineAI Admin Panel</h1><p>Live PostgreSQL database viewer &mdash; admin only</p>
<form onsubmit="go(event)">
<input type="password" id="k" placeholder="Enter admin key..." autofocus/>
<button type="submit">&#128275; Open Dashboard</button>
</form></div>
<script>function go(e){e.preventDefault();var k=document.getElementById('k').value.trim();if(k)window.location.href='/admin?key='+encodeURIComponent(k);}</script>
</body></html>"""

WRONG_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>CineAI Admin - Wrong Key</title>
<style>*{box-sizing:border-box;margin:0;padding:0}body{font-family:'Segoe UI',sans-serif;background:#080812;color:#e2e8f0;display:flex;align-items:center;justify-content:center;min-height:100vh}.card{background:#0f0f22;border:1px solid #252545;border-radius:18px;padding:52px 44px;text-align:center;width:400px}h1{font-size:22px;font-weight:800;margin-bottom:8px;color:#f87171}p{color:#64748b;font-size:13px;margin-bottom:28px}input{width:100%;padding:14px;background:#080812;border:1px solid #7c3aed;border-radius:10px;color:#e2e8f0;font-size:15px;margin-bottom:16px;outline:none;letter-spacing:2px}button{width:100%;padding:14px;background:linear-gradient(135deg,#6c3ef4,#e040fb);color:#fff;border:none;border-radius:10px;font-size:15px;font-weight:700;cursor:pointer}</style></head><body>
<div class="card"><div style="font-size:48px;margin-bottom:16px">&#10060;</div>
<h1>Wrong Key</h1><p>Please try the correct admin key</p>
<form onsubmit="go(event)"><input type="password" id="k" placeholder="Enter admin key..." autofocus/><button>&#128275; Try Again</button></form></div>
<script>function go(e){e.preventDefault();var k=document.getElementById('k').value.trim();if(k)window.location.href='/admin?key='+encodeURIComponent(k);}</script>
</body></html>"""

# ─── Dashboard template (data injected server-side) ───────────────────────────

_DASHBOARD_TEMPLATE = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CineAI Admin Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js" onerror="window._noChart=true"></script>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',system-ui,sans-serif;background:#080812;color:#e2e8f0;min-height:100vh}
header{background:linear-gradient(120deg,#3b1f8c,#6d28d9);padding:14px 22px;display:flex;align-items:center;justify-content:space-between;box-shadow:0 4px 24px rgba(0,0,0,.5);position:sticky;top:0;z-index:100}
.ht{font-size:18px;font-weight:800}.hs{font-size:11px;opacity:.7;margin-top:2px}
.hbtns{display:flex;gap:8px;align-items:center}
.pill{background:rgba(255,255,255,.13);border:1px solid rgba(255,255,255,.22);border-radius:30px;padding:5px 13px;font-size:12px;font-weight:600}
.hbtn{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.2);color:#fff;border-radius:8px;padding:6px 12px;font-size:12px;font-weight:600;cursor:pointer}
.hbtn:hover{background:rgba(255,255,255,.2)}
.live{display:flex;align-items:center;gap:6px;font-size:11px;color:#34d399}
.livdot{width:8px;height:8px;background:#34d399;border-radius:50%;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.6;transform:scale(1.3)}}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(110px,1fr));gap:10px;padding:12px 22px}
.card{background:#0f0f22;border:1px solid #1a1a35;border-radius:12px;padding:14px;text-align:center;cursor:pointer;transition:.2s}
.card:hover,.card.active{border-color:#7c3aed;background:#18183a;transform:translateY(-2px)}
.card .n{font-size:26px;font-weight:800;color:#a78bfa}
.card .l{font-size:10px;color:#64748b;margin-top:3px;text-transform:uppercase;letter-spacing:.4px}
.card .s{font-size:10px;color:#334155;margin-top:2px}
.tabs{display:flex;padding:0 22px;border-bottom:1px solid #1a1a35;overflow-x:auto;gap:2px}
.tab{padding:10px 14px;font-size:13px;font-weight:500;color:#64748b;border-bottom:2px solid transparent;cursor:pointer;transition:.15s;white-space:nowrap}
.tab:hover{color:#c4b5fd}.tab.active{color:#c4b5fd;border-bottom-color:#7c3aed}
.badge{background:#e50914;color:#fff;border-radius:10px;padding:1px 6px;font-size:10px;font-weight:800;margin-left:4px}
.panel{display:none;padding:14px 22px 40px}.panel.active{display:block}
.toolbar{display:flex;align-items:center;gap:8px;margin-bottom:12px;flex-wrap:wrap}
.sw{position:relative;flex:1;min-width:180px;max-width:320px}
.si{position:absolute;left:10px;top:50%;transform:translateY(-50%);font-size:12px;pointer-events:none;color:#64748b}
.sbox{width:100%;padding:8px 10px 8px 30px;background:#0f0f22;border:1px solid #1a1a35;border-radius:8px;color:#e2e8f0;font-size:13px;outline:none;transition:.2s}
.sbox:focus{border-color:#7c3aed;box-shadow:0 0 0 3px rgba(124,58,237,.15)}
.fsel{padding:7px 10px;background:#0f0f22;border:1px solid #1a1a35;border-radius:8px;color:#e2e8f0;font-size:12px;cursor:pointer;outline:none}
.rc{font-size:12px;color:#64748b;margin-left:auto;white-space:nowrap}
.ebtn{background:rgba(16,185,129,.12);border:1px solid rgba(16,185,129,.25);color:#34d399;border-radius:8px;padding:6px 12px;font-size:12px;font-weight:600;cursor:pointer}
.ebtn:hover{background:rgba(16,185,129,.22)}
.tw{overflow-x:auto;border-radius:10px;border:1px solid #1a1a35;max-height:62vh;overflow-y:auto}
table{width:100%;border-collapse:collapse;font-size:13px}
thead th{padding:9px 12px;text-align:left;color:#7c3aed;font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:.5px;white-space:nowrap;background:#080818;position:sticky;top:0;z-index:2;cursor:pointer;user-select:none}
thead th:hover{color:#c4b5fd}
td{padding:8px 12px;border-top:1px solid #0d0d20;color:#cbd5e1;max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
tr.dr:hover td{background:#0f0f28}
tr.hidden{display:none}
tr.banned td{opacity:.55;background:rgba(239,68,68,.03)}
tr.unread td{background:rgba(99,102,241,.04)}
.empty{text-align:center;color:#334155;padding:32px;font-size:14px}
.sb{border-radius:20px;padding:2px 9px;font-size:11px;font-weight:700;text-transform:uppercase;white-space:nowrap}
.sb.positive{background:rgba(16,185,129,.12);color:#34d399}
.sb.negative{background:rgba(239,68,68,.12);color:#f87171}
.sb.neutral{background:rgba(148,163,184,.1);color:#94a3b8}
.sb.banned{background:rgba(239,68,68,.1);color:#f87171}
.sb.active{background:rgba(16,185,129,.1);color:#34d399}
.ba{border:none;border-radius:6px;padding:3px 8px;font-size:11px;font-weight:700;cursor:pointer;transition:.15s;margin-right:2px}
.ban-btn{background:rgba(251,191,36,.1);color:#fbbf24}.ban-btn:hover{background:rgba(251,191,36,.22)}
.unb-btn{background:rgba(16,185,129,.1);color:#34d399}.unb-btn:hover{background:rgba(16,185,129,.22)}
.del-btn{background:rgba(239,68,68,.1);color:#f87171}.del-btn:hover{background:rgba(239,68,68,.22)}
.rd-btn{background:rgba(99,102,241,.12);color:#818cf8}.rd-btn:hover{background:rgba(99,102,241,.25)}
.ulink{color:#a78bfa;cursor:pointer;font-weight:700;text-decoration:underline;text-underline-offset:3px}
.ulink:hover{color:#c4b5fd}
.pthumb{width:28px;height:40px;border-radius:3px;object-fit:cover;margin-right:6px;vertical-align:middle;border:1px solid #1a1a35}
.pg{display:flex;align-items:center;justify-content:center;gap:4px;margin-top:10px;flex-wrap:wrap}
.pb{background:#0f0f22;border:1px solid #1a1a35;color:#94a3b8;border-radius:6px;padding:4px 9px;font-size:12px;cursor:pointer;transition:.15s}
.pb:hover,.pb.active{background:#7c3aed;color:#fff;border-color:#7c3aed}
.pi{color:#475569;font-size:12px;padding:0 5px}
.pr-sel{padding:5px 8px;background:#0f0f22;border:1px solid #1a1a35;border-radius:6px;color:#94a3b8;font-size:12px;cursor:pointer;outline:none}
.ag{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:14px}
.ac2{background:#0f0f22;border:1px solid #1a1a35;border-radius:12px;padding:18px}
.at{font-size:11px;font-weight:700;color:#64748b;margin-bottom:14px;text-transform:uppercase;letter-spacing:.5px}
.sg{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.si2{background:#080818;border-radius:8px;padding:12px;text-align:center}
.si2 .n{font-size:20px;font-weight:800;color:#a78bfa}.si2 .l{font-size:10px;color:#64748b;margin-top:3px;text-transform:uppercase}
.ins-row{display:flex;align-items:center;justify-content:space-between;padding:8px 0;border-bottom:1px solid #0d0d20;font-size:13px}
.ins-row:last-child{border:none}
.ins-name{color:#e2e8f0;font-weight:600}.ins-val{color:#a78bfa;font-weight:700;font-size:12px}
.mo{position:fixed;inset:0;background:rgba(0,0,0,.85);backdrop-filter:blur(6px);z-index:1000;display:none;align-items:flex-start;justify-content:center;padding:40px 16px;overflow-y:auto}
.mo.open{display:flex}
.mbox{background:#0f0f22;border:1px solid #1e1e3f;border-radius:16px;padding:26px;width:min(720px,100%);position:relative;margin:auto}
.mcl{position:absolute;top:12px;right:12px;background:rgba(255,255,255,.08);border:none;color:#94a3b8;width:28px;height:28px;border-radius:50%;font-size:14px;cursor:pointer}
.mcl:hover{background:rgba(239,68,68,.2);color:#f87171}
.mun{font-size:20px;font-weight:800;margin-bottom:4px}
.mem{color:#64748b;font-size:13px;margin-bottom:14px}
.mgr{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:14px}
.ms{background:#080818;border-radius:8px;padding:10px;text-align:center}
.ms .n{font-size:18px;font-weight:800;color:#a78bfa}.ms .l{font-size:10px;color:#64748b;margin-top:2px;text-transform:uppercase}
.mst{font-size:11px;font-weight:700;color:#7c3aed;text-transform:uppercase;letter-spacing:.5px;margin:12px 0 6px}
.mph{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:10px}
.mpl{background:#080818;border:1px solid #1a1a35;border-radius:20px;padding:3px 9px;font-size:11px;color:#cbd5e1}
.mra{display:flex;gap:8px;margin-top:14px;padding-top:12px;border-top:1px solid #1a1a35;flex-wrap:wrap}
.toast{position:fixed;bottom:20px;right:20px;padding:11px 16px;border-radius:9px;font-size:13px;font-weight:600;z-index:3000;pointer-events:none;display:none;max-width:280px}
.tok{background:#065f46;color:#34d399;border:1px solid rgba(52,211,153,.3)}
.ter{background:#7f1d1d;color:#f87171;border:1px solid rgba(248,113,113,.3)}
.nbanner{background:linear-gradient(135deg,#1e1b4b,#312e81);border:1px solid #4c1d95;border-radius:10px;padding:10px 14px;display:none;align-items:center;gap:10px;margin:8px 22px;font-size:13px}
.nbanner.show{display:flex}
footer{text-align:center;padding:14px;color:#1e293b;font-size:12px;border-top:1px solid #0a0a20;margin-top:8px}
@media(max-width:640px){.ag{grid-template-columns:1fr}.mgr{grid-template-columns:repeat(2,1fr)}}
</style></head><body>

<header>
<div><div class="ht">&#128274; CineAI Admin Dashboard</div>
<div class="hs">Live PostgreSQL &mdash; data loaded at page load</div></div>
<div class="hbtns">
<div class="live"><span class="livdot"></span><span id="live-txt">Ready</span></div>
<span id="last-upd" style="font-size:11px;color:#475569;margin-left:4px"></span>
<button class="hbtn" onclick="window.location.reload()">&#128260; Refresh</button>
<span class="pill">&#128274; Admin</span>
</div></header>

<div class="nbanner" id="nbanner">
<span>&#128276;</span><span id="ntext">New activity detected</span>
<button style="margin-left:auto;background:none;border:none;color:#818cf8;cursor:pointer;font-size:12px" onclick="this.parentElement.classList.remove('show')">Dismiss</button>
</div>

<div class="cards" id="stat-cards"></div>
<div class="tabs" id="tab-bar"></div>
<div id="panels-container"></div>

<div class="mo" id="userModal" onclick="if(event.target===this)closeModal()">
<div class="mbox"><button class="mcl" onclick="closeModal()">&#10005;</button><div id="modal-content"></div></div>
</div>
<div class="toast" id="toast"></div>
<footer>CineAI Admin Dashboard &bull; PostgreSQL &bull; &#128274; Admin Only</footer>

<script>
// ── Server-injected data (NO async fetch needed for initial load) ────────────
var D = __DATA_JSON__;
var KEY = '__KEY__';
var TMDB = 'https://image.tmdb.org/t/p/w92';
var PER_PAGE = {users:25,watchlist:25,favorites:25,reviews:25,messages:25};
var PAGES = {};
var sentChart = null, popChart = null;
var pollTimer = null, prevStats = null;

// ── Helpers ──────────────────────────────────────────────────────────────────
function q(id){return document.getElementById(id);}
function esc(v){return String(v==null?'':v).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
function toast(msg,cls){var t=q('toast');t.textContent=msg;t.className='toast '+cls;t.style.display='block';setTimeout(function(){t.style.display='none';},2800);}
function notify(msg){q('ntext').textContent=msg;q('nbanner').classList.add('show');setTimeout(function(){q('nbanner').classList.remove('show');},8000);}
function sw(name){
  var tabs=['analytics','users','watchlist','favorites','reviews','messages','insights'];
  tabs.forEach(function(t){
    var p=q('panel-'+t),tb=q('tb-'+t),c=q('c-'+t);
    if(p)p.classList.toggle('active',t===name);
    if(tb)tb.classList.toggle('active',t===name);
    if(c)c.classList.toggle('active',t===name);
  });
}

// ── Build stat cards ─────────────────────────────────────────────────────────
function buildCards(){
  var s=D.stats;
  var cards=[
    {id:'analytics',label:'Analytics',n:'&#128202;',sub:''},
    {id:'users',label:'Users',n:s.users,sub:s.active+' active'},
    {id:'watchlist',label:'Watchlist',n:s.watchlist,sub:''},
    {id:'favorites',label:'Favorites',n:s.favorites,sub:''},
    {id:'reviews',label:'Reviews',n:s.reviews,sub:''},
    {id:'messages',label:'Messages',n:s.messages,sub:s.unread_msgs>0?s.unread_msgs+' unread':''},
    {id:'insights',label:'Insights',n:'&#128200;',sub:''},
  ];
  q('stat-cards').innerHTML=cards.map(function(c){
    return '<div class="card'+(c.id==='analytics'?' active':'')+'" id="c-'+c.id+'" onclick="sw(\''+c.id+'\')">'
      +'<div class="n">'+c.n+'</div><div class="l">'+c.label+'</div>'
      +(c.sub?'<div class="s" style="color:'+(c.id==='messages'&&D.stats.unread_msgs>0?'#e50914':'#64748b')+'">'+c.sub+'</div>':'')
      +'</div>';
  }).join('');
}

// ── Build tab bar ────────────────────────────────────────────────────────────
function buildTabs(){
  var s=D.stats;
  var unread=s.unread_msgs>0?'<span class="badge">'+s.unread_msgs+'</span>':'';
  q('tab-bar').innerHTML=
    '<div class="tab active" id="tb-analytics" onclick="sw(\'analytics\')">&#128202; Analytics</div>'
    +'<div class="tab" id="tb-users" onclick="sw(\'users\')">&#128100; Users ('+s.users+')</div>'
    +'<div class="tab" id="tb-watchlist" onclick="sw(\'watchlist\')">&#128203; Watchlist</div>'
    +'<div class="tab" id="tb-favorites" onclick="sw(\'favorites\')">&#10084; Favorites</div>'
    +'<div class="tab" id="tb-reviews" onclick="sw(\'reviews\')">&#128172; Reviews ('+s.reviews+')</div>'
    +'<div class="tab" id="tb-messages" onclick="sw(\'messages\')">&#128233; Messages'+unread+'</div>'
    +'<div class="tab" id="tb-insights" onclick="sw(\'insights\')">&#128200; Insights</div>';
}

// ── Build panels ─────────────────────────────────────────────────────────────
function buildPanels(){
  var c=q('panels-container');
  c.innerHTML=
    analyticsPanel()+usersPanel()+wlPanel('watchlist')+wlPanel('favorites')+reviewsPanel()+messagesPanel()+insightsPanel();
}

// Analytics
function analyticsPanel(){
  var s=D.stats;
  var chartHtml='<canvas id="sentChart"></canvas>';
  var popHtml='<canvas id="popChart" height="100"></canvas>';
  return '<div class="panel active" id="panel-analytics">'
    +'<div class="ag">'
    +'<div class="ac2"><div class="at">Platform Overview</div><div class="sg">'
    +mini('Total Users',s.users,'')
    +mini('Active Users',s.active,'color:#34d399')
    +mini('Banned',s.banned,'color:#f87171')
    +mini('Reviews',s.reviews,'')
    +mini('Watchlist',s.watchlist,'')
    +mini('Messages',s.messages,'')
    +'</div></div>'
    +'<div class="ac2"><div class="at">Sentiment Distribution</div>'+chartHtml+'</div>'
    +'</div>'
    +'<div class="ac2" style="margin-bottom:14px"><div class="at">Most Popular Movies (Top 10)</div>'+popHtml+'</div>'
    +'<div class="ac2"><div class="at">Quick Exports</div>'
    +'<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px">'
    +['users','watchlist','favorites','reviews','messages'].map(function(t){
      return '<button class="ebtn" onclick="exportCSV(\''+t+'\')">&#128229; '+t.charAt(0).toUpperCase()+t.slice(1)+' CSV</button>';
    }).join('')
    +'</div></div>'
    +'</div>';
}
function mini(label,val,style){
  return '<div class="si2"><div class="n"'+(style?' style="'+style+'"':'')+'>'+val+'</div><div class="l">'+label+'</div></div>';
}

// Users
function usersPanel(){
  var rows=D.users;
  var tbody=rows.length?rows.map(function(u){
    var bn=u.is_banned, act=u.rev_count+u.wl_count+u.fav_count>0;
    return '<tr class="dr'+(bn?' banned':'')+'" data-s="'+esc(u.username)+' '+esc(u.email)+' '+u.id+'"'
      +' data-status="'+(bn?'banned':act?'active':'inactive')+'"'
      +' data-rev="'+u.rev_count+'" data-wl="'+u.wl_count+'" data-id="'+u.id+'">'
      +'<td>'+u.id+'</td>'
      +'<td><span class="ulink" onclick="showUser('+u.id+')">'+esc(u.username)+'</span></td>'
      +'<td>'+esc(u.email)+'</td>'
      +'<td>'+(u.age||'-')+'</td>'
      +'<td>'+esc(u.gender||'-')+'</td>'
      +'<td title="'+esc(u.favorite_genres)+'">'+esc((u.favorite_genres||'').slice(0,22)||'-')+'</td>'
      +'<td style="text-align:center">'+u.rev_count+'</td>'
      +'<td style="text-align:center">'+u.wl_count+'</td>'
      +'<td>'+u.created_at+'</td>'
      +'<td>'+u.last_login+'</td>'
      +'<td><span class="sb '+(bn?'banned':act?'active':'neutral')+'">'+(bn?'Banned':act?'Active':'Inactive')+'</span></td>'
      +'<td style="white-space:nowrap">'
      +(bn?'<button class="ba unb-btn" onclick="act(\'POST\',\'/admin/users/'+u.id+'/unban\',this)">Unban</button>'
         :'<button class="ba ban-btn" onclick="act(\'POST\',\'/admin/users/'+u.id+'/ban\',this)">Ban</button>')
      +'<button class="ba del-btn" onclick="act(\'DELETE\',\'/admin/users/'+u.id+'\',this,true)">Del</button>'
      +'</td></tr>';
  }).join('') : '<tr><td colspan="12" class="empty">No users yet</td></tr>';
  return '<div class="panel" id="panel-users">'
    +'<div class="toolbar">'
    +'<div class="sw"><span class="si">&#128269;</span><input class="sbox" id="srch-users" placeholder="Search name, email, ID..." oninput="filt(\'users\')"/></div>'
    +'<select class="fsel" id="f-status" onchange="filt(\'users\')"><option value="">All Users</option><option value="active">Active</option><option value="inactive">Inactive</option><option value="banned">Banned</option></select>'
    +'<select class="fsel" id="f-sort" onchange="filt(\'users\')"><option value="id">Latest First</option><option value="oldest">Oldest First</option><option value="reviews">Most Reviews</option><option value="watchlist">Most Watchlist</option></select>'
    +'<span class="rc" id="cnt-users">'+rows.length+' records</span>'
    +'<button class="ebtn" onclick="exportCSV(\'users\')">&#128229; CSV</button>'
    +'</div>'
    +'<div class="tw"><table id="tbl-users"><thead><tr>'
    +'<th>ID</th><th>Username</th><th>Email</th><th>Age</th><th>Gender</th><th>Genres</th>'
    +'<th>Reviews</th><th>Watchlist</th><th>Registered</th><th>Last Login</th><th>Status</th><th>Actions</th>'
    +'</tr></thead><tbody id="body-users">'+tbody+'</tbody></table></div>'
    +'<div class="pg" id="pg-users"></div></div>';
}

// Watchlist / Favorites
function wlPanel(tid){
  var rows=D[tid];
  var tbody=rows.length?rows.map(function(w){
    var img=w.poster_path?'<img src="'+TMDB+(w.poster_path[0]==='/'?'':'/')+w.poster_path+'" class="pthumb" onerror="this.style.display=\'none\'" loading="lazy"/>':'';
    return '<tr class="dr" data-s="'+esc(w.movie_title)+' '+w.user_id+'">'
      +'<td>'+w.id+'</td><td>'+w.user_id+'</td><td>'+w.movie_id+'</td>'
      +'<td>'+img+esc(w.movie_title)+'</td><td>'+w.added_at+'</td></tr>';
  }).join('') : '<tr><td colspan="5" class="empty">No '+tid+' yet</td></tr>';
  var label=tid.charAt(0).toUpperCase()+tid.slice(1);
  return '<div class="panel" id="panel-'+tid+'">'
    +'<div class="toolbar">'
    +'<div class="sw"><span class="si">&#128269;</span><input class="sbox" id="srch-'+tid+'" placeholder="Search movie title, user ID..." oninput="filt(\''+tid+'\')"/></div>'
    +'<span class="rc" id="cnt-'+tid+'">'+rows.length+' records</span>'
    +'<button class="ebtn" onclick="exportCSV(\''+tid+'\')">&#128229; CSV</button>'
    +'</div>'
    +'<div class="tw"><table id="tbl-'+tid+'"><thead><tr><th>ID</th><th>User ID</th><th>Movie ID</th><th>Movie Title</th><th>Added At</th></tr></thead>'
    +'<tbody id="body-'+tid+'">'+tbody+'</tbody></table></div>'
    +'<div class="pg" id="pg-'+tid+'"></div></div>';
}

// Reviews
function reviewsPanel(){
  var rows=D.reviews;
  var tbody=rows.length?rows.map(function(r){
    var prev=esc(r.review_text.length>80?r.review_text.slice(0,80)+'...':r.review_text);
    return '<tr class="dr" data-s="'+esc(r.movie_title)+' '+r.user_id+' '+esc(r.review_text.slice(0,30))+'" data-sent="'+r.sentiment+'">'
      +'<td>'+r.id+'</td><td>'+r.user_id+'</td><td>'+esc(r.movie_title)+'</td>'
      +'<td title="'+esc(r.review_text)+'">'+prev+'</td>'
      +'<td><span class="sb '+r.sentiment+'">'+r.sentiment+'</span></td>'
      +'<td>'+r.created_at+'</td></tr>';
  }).join('') : '<tr><td colspan="6" class="empty">No reviews yet</td></tr>';
  return '<div class="panel" id="panel-reviews">'
    +'<div class="toolbar">'
    +'<div class="sw"><span class="si">&#128269;</span><input class="sbox" id="srch-reviews" placeholder="Search movie, review text..." oninput="filt(\'reviews\')"/></div>'
    +'<select class="fsel" id="f-sent" onchange="filt(\'reviews\')"><option value="">All Sentiments</option><option value="positive">Positive</option><option value="negative">Negative</option><option value="neutral">Neutral</option></select>'
    +'<span class="rc" id="cnt-reviews">'+rows.length+' records</span>'
    +'<button class="ebtn" onclick="exportCSV(\'reviews\')">&#128229; CSV</button>'
    +'</div>'
    +'<div class="tw"><table id="tbl-reviews"><thead><tr><th>ID</th><th>User ID</th><th>Movie</th><th>Review</th><th>Sentiment</th><th>Date</th></tr></thead>'
    +'<tbody id="body-reviews">'+tbody+'</tbody></table></div>'
    +'<div class="pg" id="pg-reviews"></div></div>';
}

// Messages
function messagesPanel(){
  var rows=D.messages;
  var tbody=rows.length?rows.map(function(m){
    var prev=esc(m.message.length>80?m.message.slice(0,80)+'...':m.message);
    return '<tr class="dr'+(m.is_read?'':' unread')+'" data-s="'+esc(m.name)+' '+esc(m.email)+' '+esc(m.subject)+'" data-read="'+(m.is_read?'read':'unread')+'">'
      +'<td>'+m.id+'</td><td>'+esc(m.name)+'</td><td>'+esc(m.email)+'</td>'
      +'<td>'+esc(m.subject)+'</td><td title="'+esc(m.message)+'">'+prev+'</td>'
      +'<td>'+m.created_at+'</td>'
      +'<td>'+(m.is_read?'&#9989; Read':'&#128308; New')+'</td>'
      +'<td style="white-space:nowrap">'
      +(!m.is_read?'<button class="ba rd-btn" onclick="act(\'POST\',\'/admin/messages/'+m.id+'/read\',this)">Mark Read</button>':'')
      +'<button class="ba del-btn" onclick="act(\'DELETE\',\'/admin/messages/'+m.id+'\',this,true)">Del</button>'
      +'</td></tr>';
  }).join('') : '<tr><td colspan="8" class="empty">No messages yet</td></tr>';
  return '<div class="panel" id="panel-messages">'
    +'<div class="toolbar">'
    +'<div class="sw"><span class="si">&#128269;</span><input class="sbox" id="srch-messages" placeholder="Search name, email, subject..." oninput="filt(\'messages\')"/></div>'
    +'<select class="fsel" id="f-read" onchange="filt(\'messages\')"><option value="">All Messages</option><option value="unread">Unread Only</option><option value="read">Read Only</option></select>'
    +'<span class="rc" id="cnt-messages">'+rows.length+' records</span>'
    +'<button class="ebtn" onclick="exportCSV(\'messages\')">&#128229; CSV</button>'
    +'</div>'
    +'<div class="tw"><table id="tbl-messages"><thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Subject</th><th>Message</th><th>Sent At</th><th>Status</th><th>Actions</th></tr></thead>'
    +'<tbody id="body-messages">'+tbody+'</tbody></table></div>'
    +'<div class="pg" id="pg-messages"></div></div>';
}

// Insights
function insightsPanel(){
  var s=D.stats, n=s.users||1, total=s.reviews||1;
  var topUsers=D.top_users||[];
  var pop=D.popular||[];
  var tuHtml=topUsers.length?topUsers.map(function(u,i){
    return '<div class="ins-row"><span class="ins-name">'+(i+1)+'. '+esc(u.username)+'</span><span class="ins-val">'+u.rev_count+'R / '+u.wl_count+'W / '+u.fav_count+'F</span></div>';
  }).join(''):'<div class="empty">No data</div>';
  var popHtml=pop.length?pop.map(function(p,i){
    return '<div class="ins-row"><span class="ins-name">'+(i+1)+'. '+esc(p.title)+'</span><span class="ins-val">'+p.count+' adds</span></div>';
  }).join(''):'<div class="empty">No data</div>';
  return '<div class="panel" id="panel-insights">'
    +'<div class="ag">'
    +'<div class="ac2"><div class="at">&#127942; Top 5 Most Active Users</div>'+tuHtml+'</div>'
    +'<div class="ac2"><div class="at">&#127909; Top 10 Popular Movies</div>'+popHtml+'</div>'
    +'</div>'
    +'<div class="ac2" style="margin-bottom:14px"><div class="at">Sentiment Breakdown</div>'
    +'<div style="display:flex;gap:12px;margin-top:10px;flex-wrap:wrap">'
    +'<div class="si2" style="flex:1"><div class="n" style="color:#34d399">'+Math.round(s.pos/total*100)+'%</div><div class="l">Positive</div></div>'
    +'<div class="si2" style="flex:1"><div class="n" style="color:#f87171">'+Math.round(s.neg/total*100)+'%</div><div class="l">Negative</div></div>'
    +'<div class="si2" style="flex:1"><div class="n" style="color:#94a3b8">'+Math.round(s.neu/total*100)+'%</div><div class="l">Neutral</div></div>'
    +'</div></div>'
    +'<div class="ac2"><div class="at">User Behavior Summary</div>'
    +'<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px">'
    +mini('Avg Reviews/User',(s.reviews/n).toFixed(1),'font-size:16px')
    +mini('Avg Watchlist/User',(s.watchlist/n).toFixed(1),'font-size:16px')
    +mini('Avg Favorites/User',(s.favorites/n).toFixed(1),'font-size:16px')
    +mini('Active Rate',Math.round(s.active/n*100)+'%','font-size:16px;color:#34d399')
    +'</div></div></div>';
}

// ── Pagination ────────────────────────────────────────────────────────────────
function initPaging(){
  ['users','watchlist','favorites','reviews','messages'].forEach(function(tid){
    PAGES[tid]=1; renderPage(tid);
  });
}
function renderPage(tid){
  var PER=PER_PAGE[tid]||25;
  var rows=Array.from(document.querySelectorAll('#body-'+tid+' tr.dr:not(.hidden)'));
  var pg=PAGES[tid]||1, total=rows.length, pages=Math.max(1,Math.ceil(total/PER));
  if(pg>pages)pg=pages;
  rows.forEach(function(r,i){r.style.display=(i>=(pg-1)*PER&&i<pg*PER)?'':'none';});
  var el=q('pg-'+tid); if(!el)return;
  var h='<select class="pr-sel" onchange="PER_PAGE[\''+tid+'\']=+this.value;PAGES[\''+tid+'\']=1;renderPage(\''+tid+'\')">'
    +[10,25,50].map(function(n){return '<option value="'+n+'"'+(PER===n?' selected':'')+'>'+n+'/page</option>';}).join('')+'</select>';
  if(pages>1){
    h+='<button class="pb" onclick="gp(\''+tid+'\','+(Math.max(1,pg-1))+')">&#8249;</button>';
    var s2=Math.max(1,pg-2),e2=Math.min(pages,pg+2);
    for(var p=s2;p<=e2;p++)h+='<button class="pb'+(p===pg?' active':'')+'" onclick="gp(\''+tid+'\','+p+')">'+p+'</button>';
    h+='<button class="pb" onclick="gp(\''+tid+'\','+(Math.min(pages,pg+1))+')">&#8250;</button>';
  }
  h+='<span class="pi">'+total+' total</span>';
  el.innerHTML=h;
}
function gp(tid,p){PAGES[tid]=p;renderPage(tid);}

// ── Filter ────────────────────────────────────────────────────────────────────
function filt(tid){
  var sq=(q('srch-'+tid)||{value:''}).value.toLowerCase().trim();
  var sent=(q('f-sent')||{value:''}).value;
  var status=(q('f-status')||{value:''}).value;
  var readF=(q('f-read')||{value:''}).value;
  var rows=Array.from(document.querySelectorAll('#body-'+tid+' tr.dr'));
  var vis=0;
  rows.forEach(function(r){
    var s=(r.dataset.s||'').toLowerCase();
    var ok=!sq||s.includes(sq);
    if(sent)ok=ok&&r.dataset.sent===sent;
    if(status)ok=ok&&r.dataset.status===status;
    if(readF)ok=ok&&r.dataset.read===readF;
    r.classList.toggle('hidden',!ok); if(ok)vis++;
  });
  if(tid==='users'){
    var sortV=(q('f-sort')||{value:'id'}).value;
    var body=q('body-users');
    var sr=Array.from(body.querySelectorAll('tr.dr')).sort(function(a,b){
      if(sortV==='oldest')return +a.dataset.id - +b.dataset.id;
      if(sortV==='reviews')return +b.dataset.rev - +a.dataset.rev;
      if(sortV==='watchlist')return +b.dataset.wl - +a.dataset.wl;
      return +b.dataset.id - +a.dataset.id;
    });
    sr.forEach(function(r){body.appendChild(r);});
  }
  var ce=q('cnt-'+tid);
  if(ce)ce.textContent=(sq||sent||status||readF?vis+' of '+rows.length:rows.length)+' records';
  PAGES[tid]=1; renderPage(tid);
}

// ── Charts (optional — safe to skip if Chart.js unavailable) ─────────────────
function drawCharts(){
  if(window._noChart||typeof Chart==='undefined')return;
  try{
    var ctx=q('sentChart'); if(!ctx)return;
    var s=D.stats;
    if(sentChart)sentChart.destroy();
    sentChart=new Chart(ctx,{type:'doughnut',data:{
      labels:['Positive','Negative','Neutral'],
      datasets:[{data:[s.pos,s.neg,s.neu],
        backgroundColor:['rgba(16,185,129,.7)','rgba(239,68,68,.7)','rgba(148,163,184,.5)'],
        borderColor:['#10b981','#ef4444','#94a3b8'],borderWidth:1.5,hoverOffset:5}]
    },options:{responsive:true,plugins:{legend:{position:'bottom',labels:{color:'#94a3b8',font:{size:11},padding:12}}}}});
  }catch(e){console.warn('sentChart:',e);}
  try{
    var pop=D.popular||[]; if(!pop.length)return;
    var ctx2=q('popChart'); if(!ctx2)return;
    if(popChart)popChart.destroy();
    popChart=new Chart(ctx2,{type:'bar',data:{
      labels:pop.map(function(p){return p.title.length>20?p.title.slice(0,20)+'...':p.title;}),
      datasets:[{data:pop.map(function(p){return p.count;}),
        backgroundColor:'rgba(124,58,237,.6)',borderColor:'#7c3aed',borderWidth:1,borderRadius:4}]
    },options:{responsive:true,indexAxis:'y',plugins:{legend:{display:false}},
      scales:{x:{ticks:{color:'#64748b',font:{size:10}},grid:{color:'rgba(255,255,255,.04)'}},
              y:{ticks:{color:'#94a3b8',font:{size:10}},grid:{display:false}}}}});
  }catch(e){console.warn('popChart:',e);}
}

// ── Admin actions ─────────────────────────────────────────────────────────────
function act(method,url,btn,confirm_it){
  if(confirm_it&&!confirm('Are you sure? This cannot be undone.'))return;
  btn.disabled=true; var orig=btn.textContent; btn.textContent='...';
  fetch(url+'?key='+encodeURIComponent(KEY),{method:method})
    .then(function(r){return r.json().then(function(d){if(!r.ok)throw new Error(d.detail||'Error '+r.status);return d;});})
    .then(function(){toast('Done! Refreshing...','tok'); setTimeout(function(){window.location.reload();},800);})
    .catch(function(e){toast('Error: '+e.message,'ter'); btn.disabled=false; btn.textContent=orig;});
}

// ── User detail modal ─────────────────────────────────────────────────────────
function showUser(uid){
  var u=D.users.find(function(x){return x.id===uid;}); if(!u)return;
  var revs=D.reviews.filter(function(r){return r.user_id===uid;});
  var wl=D.watchlist.filter(function(w){return w.user_id===uid;});
  var fav=D.favorites.filter(function(f){return f.user_id===uid;});
  var msgs=D.messages.filter(function(m){return m.email&&m.email.toLowerCase()===u.email.toLowerCase();});
  var pos=revs.filter(function(r){return r.sentiment==='positive';}).length;
  var neg=revs.filter(function(r){return r.sentiment==='negative';}).length;
  var mood=pos>neg?'Positive':neg>pos?'Negative':'Neutral';
  var mc=pos>neg?'#34d399':neg>pos?'#f87171':'#94a3b8';
  var html=
    '<div class="mun">'+esc(u.username)+(u.is_banned?' <span class="sb banned">Banned</span>':'')+'</div>'
    +'<div class="mem">'+esc(u.email)+' &bull; '+(u.age||'?')+' yrs &bull; '+esc(u.gender||'Unknown')+'</div>'
    +'<div style="font-size:12px;color:#64748b;margin-bottom:12px">Joined: '+u.created_at+' &bull; Last login: '+u.last_login+'</div>'
    +(u.favorite_genres?'<div style="font-size:12px;color:#a78bfa;margin-bottom:12px">Genres: '+esc(u.favorite_genres)+'</div>':'')
    +'<div class="mgr">'
    +'<div class="ms"><div class="n">'+revs.length+'</div><div class="l">Reviews</div></div>'
    +'<div class="ms"><div class="n">'+wl.length+'</div><div class="l">Watchlist</div></div>'
    +'<div class="ms"><div class="n">'+fav.length+'</div><div class="l">Favorites</div></div>'
    +'<div class="ms"><div class="n" style="color:'+mc+'">'+mood+'</div><div class="l">Mood</div></div>'
    +'</div>'
    +(wl.length?'<div class="mst">Watchlist</div><div class="mph">'+wl.slice(0,10).map(function(w){return '<span class="mpl">'+esc(w.movie_title)+' <small style="color:#475569">'+w.added_at+'</small></span>';}).join('')+'</div>':'')
    +(fav.length?'<div class="mst">Favorites</div><div class="mph">'+fav.slice(0,10).map(function(f){return '<span class="mpl">'+esc(f.movie_title)+' <small style="color:#475569">'+f.added_at+'</small></span>';}).join('')+'</div>':'')
    +(revs.length?'<div class="mst">Reviews</div>'+revs.slice(0,5).map(function(r){
      return '<div style="background:#080818;border-radius:7px;padding:8px;margin-bottom:5px">'
        +'<span class="sb '+r.sentiment+'">'+r.sentiment+'</span>'
        +' <span style="font-size:11px;color:#64748b;margin-left:5px">'+esc(r.movie_title)+' &bull; '+r.created_at+'</span>'
        +'<div style="font-size:12px;color:#94a3b8;margin-top:3px">'+esc(r.review_text.slice(0,100))+'</div></div>';
    }).join(''):'')
    +(msgs.length?'<div class="mst">Contact Messages</div>'+msgs.slice(0,3).map(function(m){
      return '<div style="background:#080818;border-radius:7px;padding:8px;margin-bottom:5px">'
        +'<div style="font-size:12px;font-weight:600">'+esc(m.subject)+'</div>'
        +'<div style="font-size:12px;color:#94a3b8;margin-top:2px">'+esc(m.message.slice(0,80))+'</div>'
        +'<div style="font-size:11px;color:#475569;margin-top:2px">'+m.created_at+'</div></div>';
    }).join(''):'')
    +'<div class="mra">'
    +(u.is_banned
      ?'<button class="ba unb-btn" style="padding:6px 14px;font-size:13px" onclick="act(\'POST\',\'/admin/users/'+u.id+'/unban\',this)">&#9989; Unban</button>'
      :'<button class="ba ban-btn" style="padding:6px 14px;font-size:13px" onclick="act(\'POST\',\'/admin/users/'+u.id+'/ban\',this)">&#128683; Ban</button>')
    +'<button class="ba del-btn" style="padding:6px 14px;font-size:13px" onclick="act(\'DELETE\',\'/admin/users/'+u.id+'\',this,true)">&#128465; Delete</button>'
    +'</div>';
  q('modal-content').innerHTML=html;
  q('userModal').classList.add('open');
}
function closeModal(){q('userModal').classList.remove('open');}

// ── CSV Export ─────────────────────────────────────────────────────────────────
function exportCSV(tid){
  var tbl=q('tbl-'+tid); if(!tbl)return;
  var rows=Array.from(tbl.querySelectorAll('tr')).filter(function(r){return !r.classList.contains('hidden');});
  var csv=rows.map(function(r){
    return Array.from(r.querySelectorAll('th,td')).slice(0,-1).map(function(c){
      return '"'+c.textContent.trim().replace(/"/g,'""')+'"';
    }).join(',');
  }).join('\\n');
  var a=document.createElement('a');
  a.href='data:text/csv;charset=utf-8,'+encodeURIComponent(csv);
  a.download='cineai_'+tid+'_'+new Date().toISOString().slice(0,10)+'.csv';
  a.click();
}

// ── 30s polling for live notifications ───────────────────────────────────────
function startPolling(){
  prevStats={users:D.stats.users,reviews:D.stats.reviews,messages:D.stats.messages};
  pollTimer=setInterval(function(){
    fetch('/admin/api/stats?key='+encodeURIComponent(KEY))
      .then(function(r){return r.ok?r.json():null;})
      .then(function(s){
        if(!s||!prevStats)return;
        var msgs=[];
        if(s.users>prevStats.users)msgs.push('New user registered!');
        if(s.reviews>prevStats.reviews)msgs.push('New review submitted!');
        if(s.messages>prevStats.messages)msgs.push('New message received!');
        if(msgs.length){notify(msgs.join(' | ')); window.location.reload();}
        prevStats=s;
        q('last-upd').textContent='Checked '+new Date().toLocaleTimeString();
      }).catch(function(){});
  },30000);
}

// ── Init ──────────────────────────────────────────────────────────────────────
(function init(){
  buildCards();
  buildTabs();
  buildPanels();
  initPaging();
  q('live-txt').textContent='Live';
  q('last-upd').textContent='Loaded '+new Date().toLocaleTimeString();
  setTimeout(drawCharts, 100);
  startPolling();
})();
</script></body></html>"""
