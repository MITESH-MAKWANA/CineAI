# Admin dashboard HTML — all data loaded via JS fetch from /admin/api/data
# No f-strings, no emoji literals — uses HTML entities for all icons

LOGIN_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>CineAI Admin</title>
<style>*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',sans-serif;background:#080812;color:#e2e8f0;display:flex;align-items:center;justify-content:center;min-height:100vh}
.card{background:#0f0f22;border:1px solid #252545;border-radius:18px;padding:52px 44px;text-align:center;width:400px;box-shadow:0 24px 64px rgba(0,0,0,.7)}
h1{font-size:26px;font-weight:800;margin-bottom:8px}p{color:#64748b;font-size:13px;margin-bottom:32px}
input{width:100%;padding:14px 16px;background:#080812;border:1px solid #2d2d5e;border-radius:10px;color:#e2e8f0;font-size:15px;margin-bottom:16px;outline:none;letter-spacing:2px}
input:focus{border-color:#7c3aed;box-shadow:0 0 0 3px rgba(124,58,237,.2)}
button{width:100%;padding:14px;background:linear-gradient(135deg,#6c3ef4,#e040fb);color:#fff;border:none;border-radius:10px;font-size:15px;font-weight:700;cursor:pointer;transition:.2s}
button:hover{opacity:.9;transform:translateY(-1px)}
.err{color:#f87171;font-size:13px;margin-top:8px;display:none}
</style></head><body>
<div class="card">
<div style="font-size:52px;margin-bottom:16px">&#128274;</div>
<h1>CineAI Admin Panel</h1><p>Live PostgreSQL database viewer &mdash; admin only</p>
<form onsubmit="go(event)">
<input type="password" id="k" placeholder="Enter admin key..." autofocus/>
<p class="err" id="err">Wrong key. Please try again.</p>
<button type="submit">&#128275; Open Dashboard</button>
</form></div>
<script>
var p=new URLSearchParams(window.location.search);
if(p.get('wrong')==='1'){var e=document.getElementById('err');e.style.display='block';}
function go(e){e.preventDefault();var k=document.getElementById('k').value.trim();if(k)window.location.href='/admin?key='+encodeURIComponent(k);}
</script></body></html>"""

WRONG_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>CineAI Admin</title>
<style>*{box-sizing:border-box;margin:0;padding:0}body{font-family:'Segoe UI',sans-serif;background:#080812;color:#e2e8f0;display:flex;align-items:center;justify-content:center;min-height:100vh}.card{background:#0f0f22;border:1px solid #252545;border-radius:18px;padding:52px 44px;text-align:center;width:400px}h1{font-size:22px;font-weight:800;margin-bottom:8px;color:#f87171}p{color:#64748b;font-size:13px;margin-bottom:28px}input{width:100%;padding:14px;background:#080812;border:1px solid #7c3aed;border-radius:10px;color:#e2e8f0;font-size:15px;margin-bottom:16px;outline:none;letter-spacing:2px}button{width:100%;padding:14px;background:linear-gradient(135deg,#6c3ef4,#e040fb);color:#fff;border:none;border-radius:10px;font-size:15px;font-weight:700;cursor:pointer}</style></head><body>
<div class="card"><div style="font-size:48px;margin-bottom:16px">&#10060;</div>
<h1>Wrong Key</h1><p>Please try the correct admin key</p>
<form onsubmit="go(event)"><input type="password" id="k" placeholder="Enter admin key..." autofocus/><button>&#128275; Try Again</button></form></div>
<script>function go(e){e.preventDefault();var k=document.getElementById('k').value.trim();if(k)window.location.href='/admin?key='+encodeURIComponent(k);}</script>
</body></html>"""

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CineAI Admin Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js" onerror="window._chartFailed=true"></script>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',system-ui,sans-serif;background:#080812;color:#e2e8f0;min-height:100vh}
/* Header */
header{background:linear-gradient(120deg,#3b1f8c,#6d28d9);padding:14px 22px;display:flex;align-items:center;justify-content:space-between;box-shadow:0 4px 24px rgba(0,0,0,.5);position:sticky;top:0;z-index:100}
.ht{font-size:18px;font-weight:800}.hs{font-size:11px;opacity:.7;margin-top:2px}
.hbtns{display:flex;gap:8px;align-items:center}
.pill{background:rgba(255,255,255,.13);border:1px solid rgba(255,255,255,.22);border-radius:30px;padding:5px 13px;font-size:12px;font-weight:600}
.hbtn{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.2);color:#fff;border-radius:8px;padding:6px 12px;font-size:12px;font-weight:600;cursor:pointer}
.hbtn:hover{background:rgba(255,255,255,.2)}
/* Live indicator */
.live{display:flex;align-items:center;gap:6px;font-size:11px;color:#34d399}
.livdot{width:8px;height:8px;background:#34d399;border-radius:50%;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.6;transform:scale(1.3)}}
/* Stat cards */
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(110px,1fr));gap:10px;padding:12px 22px}
.card{background:#0f0f22;border:1px solid #1a1a35;border-radius:12px;padding:14px;text-align:center;cursor:pointer;transition:.2s}
.card:hover,.card.active{border-color:#7c3aed;background:#18183a;transform:translateY(-2px)}
.card .n{font-size:26px;font-weight:800;color:#a78bfa}
.card .l{font-size:10px;color:#64748b;margin-top:3px;text-transform:uppercase;letter-spacing:.4px}
.card .s{font-size:10px;color:#334155;margin-top:2px}
/* Tabs */
.tabs{display:flex;padding:0 22px;border-bottom:1px solid #1a1a35;overflow-x:auto;gap:2px}
.tab{padding:10px 14px;font-size:13px;font-weight:500;color:#64748b;border-bottom:2px solid transparent;cursor:pointer;transition:.15s;white-space:nowrap;position:relative}
.tab:hover{color:#c4b5fd}.tab.active{color:#c4b5fd;border-bottom-color:#7c3aed}
.badge{background:#e50914;color:#fff;border-radius:10px;padding:1px 6px;font-size:10px;font-weight:800;margin-left:4px}
/* Panels */
.panel{display:none;padding:14px 22px 40px}.panel.active{display:block}
/* Toolbar */
.toolbar{display:flex;align-items:center;gap:8px;margin-bottom:12px;flex-wrap:wrap}
.sw{position:relative;flex:1;min-width:180px;max-width:320px}
.si{position:absolute;left:10px;top:50%;transform:translateY(-50%);font-size:12px;pointer-events:none;color:#64748b}
.sbox{width:100%;padding:8px 10px 8px 30px;background:#0f0f22;border:1px solid #1a1a35;border-radius:8px;color:#e2e8f0;font-size:13px;outline:none;transition:.2s}
.sbox:focus{border-color:#7c3aed;box-shadow:0 0 0 3px rgba(124,58,237,.15)}
.fsel{padding:7px 10px;background:#0f0f22;border:1px solid #1a1a35;border-radius:8px;color:#e2e8f0;font-size:12px;cursor:pointer;outline:none}
.rc{font-size:12px;color:#64748b;margin-left:auto;white-space:nowrap}
.ebtn{background:rgba(16,185,129,.12);border:1px solid rgba(16,185,129,.25);color:#34d399;border-radius:8px;padding:6px 12px;font-size:12px;font-weight:600;cursor:pointer}
.ebtn:hover{background:rgba(16,185,129,.22)}
/* Table */
.tw{overflow-x:auto;border-radius:10px;border:1px solid #1a1a35;max-height:62vh;overflow-y:auto}
table{width:100%;border-collapse:collapse;font-size:13px}
thead th{padding:9px 12px;text-align:left;color:#7c3aed;font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:.5px;white-space:nowrap;background:#080818;position:sticky;top:0;z-index:2;cursor:pointer;user-select:none}
thead th:hover{color:#c4b5fd}
thead th::after{content:' \\2195';opacity:.3;font-size:9px}
thead th.sort-asc::after{content:' \\2191';opacity:1}
thead th.sort-desc::after{content:' \\2193';opacity:1}
td{padding:8px 12px;border-top:1px solid #0d0d20;color:#cbd5e1;max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
tr.dr:hover td{background:#0f0f28}
tr.hidden{display:none}
tr.banned td{opacity:.55;background:rgba(239,68,68,.03)}
tr.unread td{background:rgba(99,102,241,.04)}
.empty{text-align:center;color:#334155;padding:32px;font-size:14px}
/* Badges */
.sb{border-radius:20px;padding:2px 9px;font-size:11px;font-weight:700;text-transform:uppercase;white-space:nowrap}
.sb.positive{background:rgba(16,185,129,.12);color:#34d399}
.sb.negative{background:rgba(239,68,68,.12);color:#f87171}
.sb.neutral{background:rgba(148,163,184,.1);color:#94a3b8}
.sb.banned{background:rgba(239,68,68,.1);color:#f87171}
.sb.active{background:rgba(16,185,129,.1);color:#34d399}
/* Action buttons */
.ba{border:none;border-radius:6px;padding:3px 8px;font-size:11px;font-weight:700;cursor:pointer;transition:.15s;margin-right:2px}
.rd-btn{background:rgba(99,102,241,.12);color:#818cf8}.rd-btn:hover{background:rgba(99,102,241,.25)}
.rs-btn{background:rgba(16,185,129,.12);color:#34d399}.rs-btn:hover{background:rgba(16,185,129,.25)}
.del-btn{background:rgba(239,68,68,.1);color:#f87171}.del-btn:hover{background:rgba(239,68,68,.22)}
.ban-btn{background:rgba(251,191,36,.1);color:#fbbf24}.ban-btn:hover{background:rgba(251,191,36,.22)}
.unb-btn{background:rgba(16,185,129,.1);color:#34d399}.unb-btn:hover{background:rgba(16,185,129,.22)}
/* User link */
.ulink{color:#a78bfa;cursor:pointer;font-weight:700;text-decoration:underline;text-underline-offset:3px}
.ulink:hover{color:#c4b5fd}
/* Poster */
.pthumb{width:28px;height:42px;border-radius:3px;object-fit:cover;margin-right:6px;vertical-align:middle;border:1px solid #1a1a35}
/* Pagination */
.pg{display:flex;align-items:center;justify-content:center;gap:4px;margin-top:10px;flex-wrap:wrap}
.pb{background:#0f0f22;border:1px solid #1a1a35;color:#94a3b8;border-radius:6px;padding:4px 9px;font-size:12px;cursor:pointer;transition:.15s}
.pb:hover,.pb.active{background:#7c3aed;color:#fff;border-color:#7c3aed}
.pi{color:#475569;font-size:12px;padding:0 5px}
.pr-sel{padding:5px 8px;background:#0f0f22;border:1px solid #1a1a35;border-radius:6px;color:#94a3b8;font-size:12px;cursor:pointer;outline:none}
/* Analytics */
.ag{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:14px}
.ac2{background:#0f0f22;border:1px solid #1a1a35;border-radius:12px;padding:18px}
.at{font-size:11px;font-weight:700;color:#64748b;margin-bottom:14px;text-transform:uppercase;letter-spacing:.5px}
.sg{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.si2{background:#080818;border-radius:8px;padding:12px;text-align:center}
.si2 .n{font-size:20px;font-weight:800;color:#a78bfa}.si2 .l{font-size:10px;color:#64748b;margin-top:3px;text-transform:uppercase}
.ins-row{display:flex;align-items:center;justify-content:space-between;padding:8px 0;border-bottom:1px solid #0d0d20;font-size:13px}
.ins-row:last-child{border:none}
.ins-name{color:#e2e8f0;font-weight:600}
.ins-val{color:#a78bfa;font-weight:700;font-size:12px}
/* Modals */
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
.mph{display:flex;flex-wrap:wrap;gap:4px}
.mpl{background:#080818;border:1px solid #1a1a35;border-radius:20px;padding:3px 9px;font-size:11px;color:#cbd5e1}
.mra{display:flex;gap:8px;margin-top:14px;padding-top:12px;border-top:1px solid #1a1a35;flex-wrap:wrap}
/* Toast */
.toast{position:fixed;bottom:20px;right:20px;padding:11px 16px;border-radius:9px;font-size:13px;font-weight:600;z-index:3000;pointer-events:none;display:none;max-width:280px}
.tok{background:#065f46;color:#34d399;border:1px solid rgba(52,211,153,.3)}
.ter{background:#7f1d1d;color:#f87171;border:1px solid rgba(248,113,113,.3)}
.tin{background:#1e1b4b;color:#818cf8;border:1px solid rgba(129,140,248,.3)}
/* Notif banner */
.nbanner{background:linear-gradient(135deg,#1e1b4b,#312e81);border:1px solid #4c1d95;border-radius:10px;padding:10px 14px;display:none;align-items:center;gap:10px;margin-bottom:12px;font-size:13px}
.nbanner.show{display:flex}
footer{text-align:center;padding:14px;color:#1e293b;font-size:12px;border-top:1px solid #0a0a20;margin-top:8px}
@media(max-width:640px){.ag{grid-template-columns:1fr}.mgr{grid-template-columns:repeat(2,1fr)}}
</style></head><body>

<header>
<div><div class="ht">&#128274; CineAI Admin Dashboard</div>
<div class="hs">Live PostgreSQL &mdash; auto-refreshes every 30s</div></div>
<div class="hbtns">
<div class="live"><span class="livdot"></span><span id="live-txt">Live</span></div>
<span id="last-upd" style="font-size:11px;color:#475569;margin-left:4px"></span>
<button class="hbtn" onclick="loadData()">&#128260; Refresh</button>
<span class="pill">&#128274; Admin</span>
</div></header>

<!-- Notification banner -->
<div class="nbanner" id="nbanner">
<span>&#128276;</span><span id="ntext">New activity detected</span>
<button style="margin-left:auto;background:none;border:none;color:#818cf8;cursor:pointer;font-size:12px" onclick="this.parentElement.classList.remove('show')">Dismiss</button>
</div>

<!-- Stat cards -->
<div class="cards">
<div class="card active" id="c-analytics" onclick="sw('analytics')"><div class="n" id="st-users">-</div><div class="l">Users</div><div class="s" id="st-active"></div></div>
<div class="card" id="c-watchlist" onclick="sw('watchlist')"><div class="n" id="st-wl">-</div><div class="l">Watchlist</div></div>
<div class="card" id="c-favorites" onclick="sw('favorites')"><div class="n" id="st-fav">-</div><div class="l">Favorites</div></div>
<div class="card" id="c-reviews" onclick="sw('reviews')"><div class="n" id="st-rev">-</div><div class="l">Reviews</div></div>
<div class="card" id="c-messages" onclick="sw('messages')"><div class="n" id="st-msg">-</div><div class="l">Messages</div><div class="s" id="st-unread"></div></div>
<div class="card" id="c-insights" onclick="sw('insights')"><div class="n">&#128200;</div><div class="l">Insights</div></div>
</div>

<!-- Tabs -->
<div class="tabs">
<div class="tab active" id="tb-analytics" onclick="sw('analytics')">&#128202; Analytics</div>
<div class="tab" id="tb-users" onclick="sw('users')">&#128100; Users</div>
<div class="tab" id="tb-watchlist" onclick="sw('watchlist')">&#128203; Watchlist</div>
<div class="tab" id="tb-favorites" onclick="sw('favorites')">&#10084; Favorites</div>
<div class="tab" id="tb-reviews" onclick="sw('reviews')">&#128172; Reviews</div>
<div class="tab" id="tb-messages" onclick="sw('messages')">&#128233; Messages<span class="badge" id="unread-badge" style="display:none"></span></div>
<div class="tab" id="tb-insights" onclick="sw('insights')">&#128200; Insights</div>
</div>

<!-- ANALYTICS -->
<div class="panel active" id="panel-analytics">
<div class="ag">
<div class="ac2"><div class="at">Platform Overview</div>
<div class="sg">
<div class="si2"><div class="n" id="an-users">-</div><div class="l">Total Users</div></div>
<div class="si2"><div class="n" id="an-active" style="color:#34d399">-</div><div class="l">Active Users</div></div>
<div class="si2"><div class="n" id="an-banned" style="color:#f87171">-</div><div class="l">Banned</div></div>
<div class="si2"><div class="n" id="an-rev">-</div><div class="l">Reviews</div></div>
<div class="si2"><div class="n" id="an-wl">-</div><div class="l">Watchlist</div></div>
<div class="si2"><div class="n" id="an-msg">-</div><div class="l">Messages</div></div>
</div></div>
<div class="ac2"><div class="at">Sentiment Distribution</div><canvas id="sentChart"></canvas></div>
</div>
<div class="ac2" style="margin-bottom:14px"><div class="at">Most Popular Movies (Top 10)</div><canvas id="popChart" height="90"></canvas></div>
<div class="ac2"><div class="at">Quick Exports</div>
<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px">
<button class="ebtn" onclick="exportCSV('users')">&#128229; Users CSV</button>
<button class="ebtn" onclick="exportCSV('watchlist')">&#128229; Watchlist CSV</button>
<button class="ebtn" onclick="exportCSV('favorites')">&#128229; Favorites CSV</button>
<button class="ebtn" onclick="exportCSV('reviews')">&#128229; Reviews CSV</button>
<button class="ebtn" onclick="exportCSV('messages')">&#128229; Messages CSV</button>
</div></div>
</div>

<!-- USERS -->
<div class="panel" id="panel-users">
<div class="toolbar">
<div class="sw"><span class="si">&#128269;</span><input class="sbox" id="srch-users" placeholder="Search name, email, ID..." oninput="filt('users')"/></div>
<select class="fsel" id="f-status" onchange="filt('users')">
<option value="">All Users</option><option value="active">Active Only</option><option value="inactive">Inactive</option><option value="banned">Banned</option>
</select>
<select class="fsel" id="f-sort" onchange="filt('users')">
<option value="id">Latest First</option><option value="oldest">Oldest First</option><option value="reviews">Most Reviews</option><option value="watchlist">Most Watchlist</option>
</select>
<span class="rc" id="cnt-users">-</span>
<button class="ebtn" onclick="exportCSV('users')">&#128229; CSV</button>
</div>
<div class="tw"><table id="tbl-users">
<thead><tr>
<th onclick="sortTbl('users',0)">ID</th>
<th onclick="sortTbl('users',1)">Username</th>
<th onclick="sortTbl('users',2)">Email</th>
<th onclick="sortTbl('users',3)">Age</th>
<th onclick="sortTbl('users',4)">Gender</th>
<th onclick="sortTbl('users',5)">Genres</th>
<th onclick="sortTbl('users',6)">Reviews</th>
<th onclick="sortTbl('users',7)">Watchlist</th>
<th onclick="sortTbl('users',8)">Registered</th>
<th onclick="sortTbl('users',9)">Last Login</th>
<th>Status</th><th>Actions</th>
</tr></thead>
<tbody id="body-users"><tr><td colspan="12" class="empty">Loading...</td></tr></tbody></table></div>
<div class="pg" id="pg-users"></div>
</div>

<!-- WATCHLIST -->
<div class="panel" id="panel-watchlist">
<div class="toolbar">
<div class="sw"><span class="si">&#128269;</span><input class="sbox" id="srch-watchlist" placeholder="Search movie title, user ID..." oninput="filt('watchlist')"/></div>
<span class="rc" id="cnt-watchlist">-</span><button class="ebtn" onclick="exportCSV('watchlist')">&#128229; CSV</button>
</div>
<div class="tw"><table id="tbl-watchlist">
<thead><tr><th>ID</th><th>User ID</th><th>Movie ID</th><th>Movie Title</th><th>Added At</th></tr></thead>
<tbody id="body-watchlist"><tr><td colspan="5" class="empty">Loading...</td></tr></tbody></table></div>
<div class="pg" id="pg-watchlist"></div>
</div>

<!-- FAVORITES -->
<div class="panel" id="panel-favorites">
<div class="toolbar">
<div class="sw"><span class="si">&#128269;</span><input class="sbox" id="srch-favorites" placeholder="Search movie title, user ID..." oninput="filt('favorites')"/></div>
<span class="rc" id="cnt-favorites">-</span><button class="ebtn" onclick="exportCSV('favorites')">&#128229; CSV</button>
</div>
<div class="tw"><table id="tbl-favorites">
<thead><tr><th>ID</th><th>User ID</th><th>Movie ID</th><th>Movie Title</th><th>Added At</th></tr></thead>
<tbody id="body-favorites"><tr><td colspan="5" class="empty">Loading...</td></tr></tbody></table></div>
<div class="pg" id="pg-favorites"></div>
</div>

<!-- REVIEWS -->
<div class="panel" id="panel-reviews">
<div class="toolbar">
<div class="sw"><span class="si">&#128269;</span><input class="sbox" id="srch-reviews" placeholder="Search movie, review text..." oninput="filt('reviews')"/></div>
<select class="fsel" id="f-sent" onchange="filt('reviews')">
<option value="">All Sentiments</option><option value="positive">Positive</option><option value="negative">Negative</option><option value="neutral">Neutral</option>
</select>
<span class="rc" id="cnt-reviews">-</span><button class="ebtn" onclick="exportCSV('reviews')">&#128229; CSV</button>
</div>
<div class="tw"><table id="tbl-reviews">
<thead><tr><th>ID</th><th>User ID</th><th>Movie</th><th>Review</th><th>Sentiment</th><th>Date</th></tr></thead>
<tbody id="body-reviews"><tr><td colspan="6" class="empty">Loading...</td></tr></tbody></table></div>
<div class="pg" id="pg-reviews"></div>
</div>

<!-- MESSAGES -->
<div class="panel" id="panel-messages">
<div class="toolbar">
<div class="sw"><span class="si">&#128269;</span><input class="sbox" id="srch-messages" placeholder="Search name, email, subject..." oninput="filt('messages')"/></div>
<select class="fsel" id="f-read" onchange="filt('messages')">
<option value="">All Messages</option><option value="unread">Unread Only</option><option value="read">Read Only</option>
</select>
<span class="rc" id="cnt-messages">-</span><button class="ebtn" onclick="exportCSV('messages')">&#128229; CSV</button>
</div>
<div class="tw"><table id="tbl-messages">
<thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Subject</th><th>Message</th><th>Sent At</th><th>Status</th><th>Actions</th></tr></thead>
<tbody id="body-messages"><tr><td colspan="8" class="empty">Loading...</td></tr></tbody></table></div>
<div class="pg" id="pg-messages"></div>
</div>

<!-- INSIGHTS -->
<div class="panel" id="panel-insights">
<div class="ag">
<div class="ac2"><div class="at">&#127942; Top 5 Most Active Users</div><div id="top-users-list"><div class="empty">Loading...</div></div></div>
<div class="ac2"><div class="at">&#127909; Top 10 Popular Movies</div><div id="popular-list"><div class="empty">Loading...</div></div></div>
</div>
<div class="ac2" style="margin-bottom:14px">
<div class="at">Sentiment Breakdown</div>
<div style="display:flex;gap:12px;margin-top:10px;flex-wrap:wrap">
<div class="si2" style="flex:1"><div class="n" id="pct-pos" style="color:#34d399">-</div><div class="l">Positive</div></div>
<div class="si2" style="flex:1"><div class="n" id="pct-neg" style="color:#f87171">-</div><div class="l">Negative</div></div>
<div class="si2" style="flex:1"><div class="n" id="pct-neu" style="color:#94a3b8">-</div><div class="l">Neutral</div></div>
</div></div>
<div class="ac2"><div class="at">User Behavior Summary</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px">
<div class="si2"><div class="n" id="avg-rev" style="font-size:16px">-</div><div class="l">Avg Reviews/User</div></div>
<div class="si2"><div class="n" id="avg-wl" style="font-size:16px">-</div><div class="l">Avg Watchlist/User</div></div>
<div class="si2"><div class="n" id="avg-fav" style="font-size:16px">-</div><div class="l">Avg Favorites/User</div></div>
<div class="si2"><div class="n" id="engagement" style="font-size:16px;color:#34d399">-</div><div class="l">Active Rate</div></div>
</div></div>
</div>

<!-- User Detail Modal -->
<div class="mo" id="userModal" onclick="if(event.target===this)closeModal()">
<div class="mbox"><button class="mcl" onclick="closeModal()">&#10005;</button><div id="modal-content"></div></div>
</div>

<div class="toast" id="toast"></div>
<footer>CineAI Admin Dashboard &bull; PostgreSQL &bull; &#128274; Admin Only</footer>

<script>
var KEY=new URLSearchParams(window.location.search).get('key')||'';
var TMDB='https://image.tmdb.org/t/p/w92';
var PER_PAGE={users:25,watchlist:25,favorites:25,reviews:25,messages:25};
var PAGES={},D=null,prevStats=null,pollTimer=null;
var sentChart=null,popChart=null;

// ── Helpers ────────────────────────────────────────────────────────────
function q(id){return document.getElementById(id);}
function esc(v){return String(v==null?'':v).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
function toast(msg,cls){var t=q('toast');t.textContent=msg;t.className='toast '+cls;t.style.display='block';setTimeout(()=>t.style.display='none',2800);}
function notify(msg){q('ntext').textContent=msg;q('nbanner').classList.add('show');setTimeout(()=>q('nbanner').classList.remove('show'),8000);}

// ── Load full data ─────────────────────────────────────────────────────
async function loadData(){
  q('live-txt').textContent='Refreshing...';
  try{
    var r=await fetch('/admin/api/data?key='+encodeURIComponent(KEY));
    if(!r.ok){toast('Error '+r.status+': Check admin key','ter');return;}
    D=await r.json();
    renderAll();
    prevStats=Object.assign({},D.stats);
    q('last-upd').textContent='Updated '+new Date().toLocaleTimeString();
    q('live-txt').textContent='Live';
    startPolling();
  }catch(e){toast('Load failed: '+e.message,'ter');q('live-txt').textContent='Error';}
}

// ── 30s polling for live updates ───────────────────────────────────────
function startPolling(){
  if(pollTimer)clearInterval(pollTimer);
  pollTimer=setInterval(async()=>{
    try{
      var r=await fetch('/admin/api/stats?key='+encodeURIComponent(KEY));
      if(!r.ok)return;
      var s=await r.json();
      if(prevStats){
        var msgs=[];
        if(s.users>prevStats.users)msgs.push('New user registered!');
        if(s.reviews>prevStats.reviews)msgs.push('New review submitted!');
        if(s.messages>prevStats.messages)msgs.push('New message received!');
        if(msgs.length){notify(msgs.join(' | '));loadData();}
        else{
          q('st-unread').textContent=s.unread>0?s.unread+' unread':'';
          var b=q('unread-badge');b.textContent=s.unread;b.style.display=s.unread>0?'inline':'none';
        }
      }
      prevStats=s;
      q('last-upd').textContent='Updated '+new Date().toLocaleTimeString();
    }catch(e){}
  },30000);
}

// ── Render all tabs ────────────────────────────────────────────────────
function renderAll(){
  try {
    var s=D.stats;
    // Cards
    q('st-users').textContent=s.users;
    q('st-active').textContent=s.active+' active';
    q('st-wl').textContent=s.watchlist;
    q('st-fav').textContent=s.favorites;
    q('st-rev').textContent=s.reviews;
    q('st-msg').textContent=s.messages;
    q('st-unread').textContent=s.unread_msgs>0?s.unread_msgs+' unread':'';
    q('st-unread').style.color=s.unread_msgs>0?'#e50914':'#334155';
    var b=q('unread-badge');
    if(b){b.textContent=s.unread_msgs;b.style.display=s.unread_msgs>0?'inline':'none';}
    // Analytics panel numbers
    q('an-users').textContent=s.users;q('an-active').textContent=s.active;
    q('an-banned').textContent=s.banned;q('an-rev').textContent=s.reviews;
    q('an-wl').textContent=s.watchlist;q('an-msg').textContent=s.messages;
    // --- BUILD TABLES FIRST (critical — must run before charts) ---
    buildUsers();
    buildWL('watchlist');
    buildWL('favorites');
    buildReviews();
    buildMessages();
    buildInsights();
    q('live-txt').textContent='Live';
    // --- CHARTS LAST — safe to fail without affecting tables ---
    try{ renderSentChart(s.pos,s.neg,s.neu); }catch(ce){ console.warn('Sentiment chart skipped:',ce.message); }
    try{ renderPopChart(D.popular||[]); }catch(ce){ console.warn('Popular chart skipped:',ce.message); }
  } catch(e) {
    console.error('renderAll error:',e);
    toast('Render error: '+e.message,'ter');
  }
}


// ── Charts ─────────────────────────────────────────────────────────────
function renderSentChart(pos,neg,neu){
  if(sentChart)sentChart.destroy();
  var ctx=q('sentChart');if(!ctx)return;
  sentChart=new Chart(ctx,{type:'doughnut',data:{
    labels:['Positive','Negative','Neutral'],
    datasets:[{data:[pos,neg,neu],backgroundColor:['rgba(16,185,129,.7)','rgba(239,68,68,.7)','rgba(148,163,184,.5)'],borderColor:['#10b981','#ef4444','#94a3b8'],borderWidth:1.5,hoverOffset:5}]
  },options:{responsive:true,plugins:{legend:{position:'bottom',labels:{color:'#94a3b8',font:{size:11},padding:12}},tooltip:{callbacks:{label:c=>' '+c.label+': '+c.parsed}}}}});
}

function renderPopChart(pop){
  if(popChart)popChart.destroy();
  var ctx=q('popChart');if(!ctx||!pop.length)return;
  popChart=new Chart(ctx,{type:'bar',data:{
    labels:pop.map(p=>p.title.length>20?p.title.slice(0,20)+'...':p.title),
    datasets:[{data:pop.map(p=>p.count),backgroundColor:'rgba(124,58,237,.6)',borderColor:'#7c3aed',borderWidth:1,borderRadius:4}]
  },options:{responsive:true,indexAxis:'y',plugins:{legend:{display:false}},scales:{x:{ticks:{color:'#64748b',font:{size:10}},grid:{color:'rgba(255,255,255,.04)'}},y:{ticks:{color:'#94a3b8',font:{size:10}},grid:{display:false}}}}});
}

// ── Build tables ───────────────────────────────────────────────────────
function buildUsers(){
  var b=q('body-users');if(!b)return;
  if(!D.users.length){b.innerHTML='<tr><td colspan="12" class="empty">No users yet</td></tr>';return;}
  b.innerHTML=D.users.map(u=>{
    var bn=u.is_banned;
    return '<tr class="dr'+(bn?' banned':'')+'" '
      +'data-s="'+esc(u.username)+' '+esc(u.email)+' '+u.id+'" '
      +'data-status="'+(bn?'banned':u.rev_count+u.wl_count+u.fav_count>0?'active':'inactive')+'" '
      +'data-rev="'+u.rev_count+'" data-wl="'+u.wl_count+'" data-id="'+u.id+'">'
      +'<td>'+u.id+'</td>'
      +'<td><span class="ulink" onclick="showUser('+u.id+')">'+esc(u.username)+'</span></td>'
      +'<td>'+esc(u.email)+'</td>'
      +'<td>'+(u.age||'-')+'</td>'
      +'<td>'+esc(u.gender||'-')+'</td>'
      +'<td title="'+esc(u.favorite_genres)+'">'+esc((u.favorite_genres||'').slice(0,25)||'-')+'</td>'
      +'<td style="text-align:center">'+u.rev_count+'</td>'
      +'<td style="text-align:center">'+u.wl_count+'</td>'
      +'<td>'+u.created_at+'</td>'
      +'<td>'+u.last_login+'</td>'
      +'<td><span class="sb '+(bn?'banned':u.rev_count+u.wl_count+u.fav_count>0?'active':'neutral')+'">'+(bn?'Banned':u.rev_count+u.wl_count+u.fav_count>0?'Active':'Inactive')+'</span></td>'
      +'<td style="white-space:nowrap">'
      +(bn?'<button class="ba unb-btn" onclick="act(\'POST\',\'/admin/users/'+u.id+'/unban\',this)">Unban</button>'
         :'<button class="ba ban-btn" onclick="act(\'POST\',\'/admin/users/'+u.id+'/ban\',this)">Ban</button>')
      +'<button class="ba del-btn" onclick="act(\'DELETE\',\'/admin/users/'+u.id+'\',this,true)">Del</button>'
      +'</td></tr>';
  }).join('');
  initPage('users');
}

function buildWL(tid){
  var data=D[tid],b=q('body-'+tid);if(!b)return;
  if(!data.length){b.innerHTML='<tr><td colspan="5" class="empty">No '+tid+' yet</td></tr>';return;}
  b.innerHTML=data.map(w=>{
    var img=w.poster_path?'<img src="'+TMDB+(w.poster_path.startsWith('/')?'':'/')+w.poster_path+'" class="pthumb" onerror="this.style.display=\'none\'" loading="lazy"/>':'';
    return '<tr class="dr" data-s="'+esc(w.movie_title)+' '+w.user_id+'">'
      +'<td>'+w.id+'</td><td>'+w.user_id+'</td><td>'+w.movie_id+'</td>'
      +'<td>'+img+esc(w.movie_title)+'</td>'
      +'<td>'+w.added_at+'</td></tr>';
  }).join('');
  initPage(tid);
}

function buildReviews(){
  var b=q('body-reviews');if(!b)return;
  if(!D.reviews.length){b.innerHTML='<tr><td colspan="6" class="empty">No reviews yet</td></tr>';return;}
  b.innerHTML=D.reviews.map(r=>{
    var prev=esc(r.review_text.length>80?r.review_text.slice(0,80)+'...':r.review_text);
    return '<tr class="dr" data-s="'+esc(r.movie_title)+' '+r.user_id+' '+esc(r.review_text.slice(0,30))+'" data-sent="'+r.sentiment+'">'
      +'<td>'+r.id+'</td><td>'+r.user_id+'</td><td>'+esc(r.movie_title)+'</td>'
      +'<td title="'+esc(r.review_text)+'">'+prev+'</td>'
      +'<td><span class="sb '+r.sentiment+'">'+r.sentiment+'</span></td>'
      +'<td>'+r.created_at+'</td></tr>';
  }).join('');
  initPage('reviews');
}

function buildMessages(){
  var b=q('body-messages');if(!b)return;
  if(!D.messages.length){b.innerHTML='<tr><td colspan="8" class="empty">No messages yet</td></tr>';return;}
  b.innerHTML=D.messages.map(m=>{
    var prev=esc(m.message.length>80?m.message.slice(0,80)+'...':m.message);
    return '<tr class="dr'+(m.is_read?'':' unread')+'" data-s="'+esc(m.name)+' '+esc(m.email)+' '+esc(m.subject)+'" data-read="'+(m.is_read?'read':'unread')+'">'
      +'<td>'+m.id+'</td><td>'+esc(m.name)+'</td><td>'+esc(m.email)+'</td>'
      +'<td>'+esc(m.subject)+'</td>'
      +'<td title="'+esc(m.message)+'">'+prev+'</td>'
      +'<td>'+m.created_at+'</td>'
      +'<td>'+(m.is_read?'&#9989; Read':'&#128308; New')+'</td>'
      +'<td style="white-space:nowrap">'
      +(!m.is_read?'<button class="ba rd-btn" onclick="act(\'POST\',\'/admin/messages/'+m.id+'/read\',this)">Mark Read</button>':'')
      +'<button class="ba del-btn" onclick="act(\'DELETE\',\'/admin/messages/'+m.id+'\',this,true)">Del</button>'
      +'</td></tr>';
  }).join('');
  initPage('messages');
}

function buildInsights(){
  // Top users
  var tu=q('top-users-list');
  if(D.top_users&&D.top_users.length){
    tu.innerHTML=D.top_users.map((u,i)=>'<div class="ins-row"><span class="ins-name">'+(i+1)+'. '+esc(u.username)+'</span><span class="ins-val">'+u.rev_count+'R / '+u.wl_count+'W / '+u.fav_count+'F</span></div>').join('');
  }else{tu.innerHTML='<div class="empty">No data</div>';}
  // Popular movies
  var pm=q('popular-list');
  if(D.popular&&D.popular.length){
    pm.innerHTML=D.popular.map((p,i)=>'<div class="ins-row"><span class="ins-name">'+(i+1)+'. '+esc(p.title)+'</span><span class="ins-val">'+p.count+' adds</span></div>').join('');
  }else{pm.innerHTML='<div class="empty">No data</div>';}
  // Sentiment pct
  var s=D.stats, total=s.reviews||1;
  q('pct-pos').textContent=Math.round(s.pos/total*100)+'%';
  q('pct-neg').textContent=Math.round(s.neg/total*100)+'%';
  q('pct-neu').textContent=Math.round(s.neu/total*100)+'%';
  // Averages
  var n=s.users||1;
  q('avg-rev').textContent=(s.reviews/n).toFixed(1);
  q('avg-wl').textContent=(s.watchlist/n).toFixed(1);
  q('avg-fav').textContent=(s.favorites/n).toFixed(1);
  q('engagement').textContent=Math.round(s.active/n*100)+'%';
}

// ── Pagination ─────────────────────────────────────────────────────────
function initPage(tid){PAGES[tid]=1;filt(tid);}

function renderPage(tid){
  var PER=PER_PAGE[tid]||25;
  var rows=Array.from(document.querySelectorAll('#body-'+tid+' tr.dr:not(.hidden)'));
  var pg=PAGES[tid]||1,total=rows.length,pages=Math.ceil(total/PER)||1;
  if(pg>pages)pg=pages;
  rows.forEach((r,i)=>r.style.display=(i>=(pg-1)*PER&&i<pg*PER)?'':'none');
  var el=q('pg-'+tid);if(!el)return;
  var h='<select class="pr-sel" onchange="PER_PAGE[\''+tid+'\']=+this.value;PAGES[\''+tid+'\']=1;renderPage(\''+tid+'\')">'
    +[10,25,50].map(n=>'<option value="'+n+'"'+(PER===n?' selected':'')+'>'+n+'/page</option>').join('')+'</select>';
  if(pages>1){
    h+=' <button class="pb" onclick="gp(\''+tid+'\','+Math.max(1,pg-1)+')">&#8249;</button>';
    var start=Math.max(1,pg-2),end=Math.min(pages,pg+2);
    for(var p=start;p<=end;p++)h+='<button class="pb'+(p===pg?' active':'')+'" onclick="gp(\''+tid+'\','+p+')">'+p+'</button>';
    h+='<button class="pb" onclick="gp(\''+tid+'\','+Math.min(pages,pg+1)+')">&#8250;</button>';
  }
  h+='<span class="pi">'+total+' total</span>';
  el.innerHTML=h;
}
function gp(tid,p){PAGES[tid]=p;renderPage(tid);}

// ── Filter + sort ──────────────────────────────────────────────────────
function filt(tid){
  var sq=(q('srch-'+tid)||{}).value||'';sq=sq.toLowerCase().trim();
  var sent=(q('f-sent')||{}).value||'';
  var status=(q('f-status')||{}).value||'';
  var readF=(q('f-read')||{}).value||'';
  var rows=Array.from(document.querySelectorAll('#body-'+tid+' tr.dr'));
  var vis=0;
  rows.forEach(r=>{
    var s=(r.dataset.s||'').toLowerCase();
    var ok=!sq||s.includes(sq);
    if(sent)ok=ok&&r.dataset.sent===sent;
    if(status)ok=ok&&r.dataset.status===status;
    if(readF)ok=ok&&r.dataset.read===readF;
    r.classList.toggle('hidden',!ok);if(ok)vis++;
  });
  // Sort (users only)
  if(tid==='users'){
    var sortV=(q('f-sort')||{}).value||'id';
    var body=q('body-'+tid);
    var sortedRows=Array.from(body.querySelectorAll('tr.dr')).sort((a,b)=>{
      if(sortV==='oldest')return +a.dataset.id - +b.dataset.id;
      if(sortV==='reviews')return +b.dataset.rev - +a.dataset.rev;
      if(sortV==='watchlist')return +b.dataset.wl - +a.dataset.wl;
      return +b.dataset.id - +a.dataset.id; // latest first
    });
    sortedRows.forEach(r=>body.appendChild(r));
  }
  var ce=q('cnt-'+tid);
  if(ce)ce.textContent=(sq||sent||status||readF?vis+' of '+rows.length:rows.length)+' records';
  PAGES[tid]=1;renderPage(tid);
}

// ── Column sort ────────────────────────────────────────────────────────
var _sortState={};
function sortTbl(tid,col){
  var body=q('body-'+tid);if(!body)return;
  var key=tid+col;
  _sortState[key]=_sortState[key]==='asc'?'desc':'asc';
  var asc=_sortState[key]==='asc';
  var rows=Array.from(body.querySelectorAll('tr.dr'));
  rows.sort((a,b)=>{
    var av=(a.querySelectorAll('td')[col]||{}).textContent||'';
    var bv=(b.querySelectorAll('td')[col]||{}).textContent||'';
    var n=av-bv;return isNaN(n)?(asc?av.localeCompare(bv):bv.localeCompare(av)):(asc?n:-n);
  });
  rows.forEach(r=>body.appendChild(r));
  // Update header arrows
  var ths=document.querySelectorAll('#tbl-'+tid+' thead th');
  ths.forEach((th,i)=>{th.className=i===col?('sort-'+_sortState[key]):'';});
  renderPage(tid);
}

// ── Tab switch ─────────────────────────────────────────────────────────
var TABS=['analytics','users','watchlist','favorites','reviews','messages','insights'];
function sw(name){TABS.forEach(t=>{['panel-','tb-','c-'].forEach(p=>{var el=q(p+t);if(el)el.classList.toggle('active',t===name);});});}

// ── Admin actions ──────────────────────────────────────────────────────
async function act(method,url,btn,confirm_it){
  if(confirm_it&&!confirm('Are you sure? This cannot be undone.'))return;
  btn.disabled=true;var orig=btn.textContent;btn.textContent='...';
  try{
    var r=await fetch(url+'?key='+encodeURIComponent(KEY),{method});
    var d=await r.json();if(!r.ok)throw new Error(d.detail||'Error '+r.status);
    toast('Done!','tok');setTimeout(()=>loadData(),600);
  }catch(e){toast('Error: '+e.message,'ter');btn.disabled=false;btn.textContent=orig;}
}

// ── User detail modal ──────────────────────────────────────────────────
function showUser(uid){
  if(!D)return;var u=D.users.find(x=>x.id===uid);if(!u)return;
  var revs=D.reviews.filter(r=>r.user_id===uid);
  var wl=D.watchlist.filter(w=>w.user_id===uid);
  var fav=D.favorites.filter(f=>f.user_id===uid);
  var msgs=D.messages.filter(m=>m.email&&m.email.toLowerCase()===u.email.toLowerCase());
  var pos=revs.filter(r=>r.sentiment==='positive').length;
  var neg=revs.filter(r=>r.sentiment==='negative').length;
  var mood=pos>neg?'Positive':neg>pos?'Negative':'Neutral';
  var mc=pos>neg?'#34d399':neg>pos?'#f87171':'#94a3b8';
  q('modal-content').innerHTML=
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
    +(wl.length?'<div class="mst">Watchlist</div><div class="mph" style="margin-bottom:10px">'+wl.slice(0,10).map(w=>'<span class="mpl">'+esc(w.movie_title)+' <small style="color:#475569">'+w.added_at+'</small></span>').join('')+'</div>':'')
    +(fav.length?'<div class="mst">Favorites</div><div class="mph" style="margin-bottom:10px">'+fav.slice(0,10).map(f=>'<span class="mpl">'+esc(f.movie_title)+' <small style="color:#475569">'+f.added_at+'</small></span>').join('')+'</div>':'')
    +(revs.length?'<div class="mst">Reviews</div>'+revs.slice(0,5).map(r=>'<div style="background:#080818;border-radius:7px;padding:8px;margin-bottom:5px"><span class="sb '+r.sentiment+'">'+r.sentiment+'</span> <span style="font-size:11px;color:#64748b;margin-left:5px">'+esc(r.movie_title)+' &bull; '+r.created_at+'</span><div style="font-size:12px;color:#94a3b8;margin-top:3px">'+esc(r.review_text.slice(0,100))+'</div></div>').join(''):'')
    +(msgs.length?'<div class="mst">Contact Messages</div>'+msgs.slice(0,3).map(m=>'<div style="background:#080818;border-radius:7px;padding:8px;margin-bottom:5px"><div style="font-size:12px;font-weight:600">'+esc(m.subject)+'</div><div style="font-size:12px;color:#94a3b8;margin-top:2px">'+esc(m.message.slice(0,80))+'</div><div style="font-size:11px;color:#475569;margin-top:2px">'+m.created_at+'</div></div>').join(''):'')
    +'<div class="mra">'
    +(u.is_banned
      ?'<button class="ba unb-btn" style="padding:6px 14px;font-size:13px" onclick="act(\'POST\',\'/admin/users/'+u.id+'/unban\',this)">&#9989; Unban</button>'
      :'<button class="ba ban-btn" style="padding:6px 14px;font-size:13px" onclick="act(\'POST\',\'/admin/users/'+u.id+'/ban\',this)">&#128683; Ban</button>')
    +'<button class="ba del-btn" style="padding:6px 14px;font-size:13px" onclick="act(\'DELETE\',\'/admin/users/'+u.id+'\',this,true)">&#128465; Delete</button>'
    +'</div>';
  q('userModal').classList.add('open');
}
function closeModal(){q('userModal').classList.remove('open');}

// ── CSV Export ─────────────────────────────────────────────────────────
function exportCSV(tid){
  var tbl=q('tbl-'+tid);if(!tbl)return;
  var rows=Array.from(tbl.querySelectorAll('tr')).filter(r=>!r.classList.contains('hidden'));
  var csv=rows.map(r=>Array.from(r.querySelectorAll('th,td')).slice(0,-1).map(c=>'"'+c.textContent.trim().replace(/"/g,'""')+'"').join(',')).join('\\n');
  var a=document.createElement('a');
  a.href='data:text/csv;charset=utf-8,'+encodeURIComponent(csv);
  a.download='cineai_'+tid+'_'+new Date().toISOString().slice(0,10)+'.csv';a.click();
}

// ── Init ───────────────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded',loadData);
</script></body></html>"""
