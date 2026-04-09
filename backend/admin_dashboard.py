# Admin dashboard HTML strings - kept separate to avoid f-string/encoding issues in main.py

LOGIN_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>CineAI Admin</title>
<style>*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',sans-serif;background:#0d0d1a;color:#e2e8f0;display:flex;align-items:center;justify-content:center;min-height:100vh}
.card{background:#13132a;border:1px solid #252545;border-radius:18px;padding:52px 44px;text-align:center;width:400px;box-shadow:0 24px 64px rgba(0,0,0,.6)}
h1{font-size:26px;font-weight:800;margin-bottom:8px}p{color:#64748b;font-size:13px;margin-bottom:32px}
input{width:100%;padding:14px 16px;background:#0a0a14;border:1px solid #2d2d5e;border-radius:10px;color:#e2e8f0;font-size:15px;margin-bottom:16px;outline:none;letter-spacing:2px}
input:focus{border-color:#7c3aed}
button{width:100%;padding:14px;background:linear-gradient(135deg,#6c3ef4,#e040fb);color:#fff;border:none;border-radius:10px;font-size:15px;font-weight:700;cursor:pointer}
</style></head><body>
<div class="card">
<div style="font-size:52px;margin-bottom:16px">&#127921;</div>
<h1>CineAI Admin Panel</h1><p>Live database viewer &mdash; admin only</p>
<form onsubmit="go(event)">
<input type="password" id="k" placeholder="Enter admin key..." autofocus/>
<button type="submit">&#128275; Open Dashboard</button>
</form></div>
<script>function go(e){e.preventDefault();var k=document.getElementById('k').value.trim();if(k)window.location.href='/admin?key='+encodeURIComponent(k);}</script>
</body></html>"""

WRONG_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>CineAI Admin</title>
<style>*{box-sizing:border-box;margin:0;padding:0}body{font-family:'Segoe UI',sans-serif;background:#0d0d1a;color:#e2e8f0;display:flex;align-items:center;justify-content:center;min-height:100vh}.card{background:#13132a;border:1px solid #252545;border-radius:18px;padding:52px 44px;text-align:center;width:400px}h1{font-size:22px;font-weight:800;margin-bottom:8px;color:#f87171}p{color:#64748b;font-size:13px;margin-bottom:28px}input{width:100%;padding:14px;background:#0a0a14;border:1px solid #7c3aed;border-radius:10px;color:#e2e8f0;font-size:15px;margin-bottom:16px;outline:none;letter-spacing:2px}button{width:100%;padding:14px;background:linear-gradient(135deg,#6c3ef4,#e040fb);color:#fff;border:none;border-radius:10px;font-size:15px;font-weight:700;cursor:pointer}</style></head><body>
<div class="card"><div style="font-size:48px;margin-bottom:16px">&#10060;</div>
<h1>Wrong Key</h1><p>Please try the correct admin key</p>
<form onsubmit="go(event)"><input type="password" id="k" placeholder="Enter admin key..." autofocus/><button>&#128275; Try Again</button></form></div>
<script>function go(e){e.preventDefault();var k=document.getElementById('k').value.trim();if(k)window.location.href='/admin?key='+encodeURIComponent(k);}</script>
</body></html>"""

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CineAI Admin Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',system-ui,sans-serif;background:#080812;color:#e2e8f0;min-height:100vh}
header{background:linear-gradient(120deg,#3b1f8c,#6d28d9);padding:16px 24px;display:flex;align-items:center;justify-content:space-between;box-shadow:0 4px 24px rgba(0,0,0,.5)}
.ht{font-size:20px;font-weight:800}.hs{font-size:11px;opacity:.7;margin-top:2px}
.hbtns{display:flex;gap:8px;align-items:center}
.pill{background:rgba(255,255,255,.13);border:1px solid rgba(255,255,255,.22);border-radius:30px;padding:5px 13px;font-size:12px;font-weight:600}
.hbtn{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.2);color:#fff;border-radius:8px;padding:7px 14px;font-size:12px;font-weight:600;cursor:pointer}
.hbtn:hover{background:rgba(255,255,255,.2)}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:10px;padding:14px 22px}
.card{background:#0f0f22;border:1px solid #1a1a35;border-radius:12px;padding:14px;text-align:center;cursor:pointer;transition:.2s}
.card:hover,.card.active{border-color:#7c3aed;background:#18183a}
.card .n{font-size:28px;font-weight:800;color:#a78bfa}
.card .l{font-size:11px;color:#64748b;margin-top:3px;text-transform:uppercase;letter-spacing:.4px}
.card .s{font-size:10px;color:#334155;margin-top:2px}
.tabs{display:flex;padding:0 22px;border-bottom:1px solid #1a1a35;overflow-x:auto}
.tab{padding:10px 14px;font-size:13px;font-weight:500;color:#64748b;border-bottom:2px solid transparent;cursor:pointer;transition:.15s;white-space:nowrap}
.tab:hover{color:#c4b5fd}.tab.active{color:#c4b5fd;border-bottom-color:#7c3aed}
.badge{background:#e50914;color:#fff;border-radius:10px;padding:1px 6px;font-size:10px;font-weight:800;margin-left:4px}
.panel{display:none;padding:14px 22px 40px}.panel.active{display:block}
.toolbar{display:flex;align-items:center;gap:10px;margin-bottom:12px;flex-wrap:wrap}
.sw{position:relative;flex:1;min-width:180px;max-width:360px}
.si{position:absolute;left:11px;top:50%;transform:translateY(-50%);font-size:13px;pointer-events:none}
.sbox{width:100%;padding:9px 12px 9px 32px;background:#0f0f22;border:1px solid #1a1a35;border-radius:8px;color:#e2e8f0;font-size:13px;outline:none;transition:.2s}
.sbox:focus{border-color:#7c3aed;box-shadow:0 0 0 3px rgba(124,58,237,.18)}
.rc{font-size:12px;color:#475569;margin-left:auto}
.fsel{padding:8px 10px;background:#0f0f22;border:1px solid #1a1a35;border-radius:8px;color:#e2e8f0;font-size:13px;cursor:pointer;outline:none}
.ebtn{background:rgba(16,185,129,.15);border:1px solid rgba(16,185,129,.3);color:#34d399;border-radius:8px;padding:7px 13px;font-size:12px;font-weight:600;cursor:pointer}
.ebtn:hover{background:rgba(16,185,129,.25)}
.tw{overflow-x:auto;border-radius:10px;border:1px solid #1a1a35}
table{width:100%;border-collapse:collapse;font-size:13px}
thead{background:#0a0a1a}
th{padding:9px 12px;text-align:left;color:#7c3aed;font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:.5px;white-space:nowrap}
td{padding:8px 12px;border-top:1px solid #0f0f2a;color:#cbd5e1;white-space:nowrap;max-width:220px;overflow:hidden;text-overflow:ellipsis}
tr.dr:hover td{background:#12122e}
tr.hidden{display:none}
tr.banned td{opacity:.6;background:rgba(239,68,68,.04)}
tr.unread td{background:rgba(99,102,241,.05)}
.empty{text-align:center;color:#334155;padding:32px;font-size:14px}
.sb{border-radius:20px;padding:2px 9px;font-size:11px;font-weight:700;text-transform:uppercase}
.sb.positive{background:rgba(16,185,129,.12);color:#34d399}
.sb.negative{background:rgba(239,68,68,.12);color:#f87171}
.sb.neutral{background:rgba(148,163,184,.1);color:#94a3b8}
.ac{white-space:nowrap}
.ba{border:none;border-radius:6px;padding:4px 8px;font-size:11px;font-weight:700;cursor:pointer;margin-right:3px;transition:.15s}
.ban-btn{background:rgba(251,191,36,.12);color:#fbbf24}.ban-btn:hover{background:rgba(251,191,36,.25)}
.unb-btn{background:rgba(16,185,129,.12);color:#34d399}.unb-btn:hover{background:rgba(16,185,129,.25)}
.del-btn{background:rgba(239,68,68,.12);color:#f87171}.del-btn:hover{background:rgba(239,68,68,.25)}
.edt-btn{background:rgba(99,102,241,.12);color:#818cf8}.edt-btn:hover{background:rgba(99,102,241,.25)}
.ulink{color:#a78bfa;cursor:pointer;font-weight:700;text-decoration:underline;text-underline-offset:3px}
.ulink:hover{color:#c4b5fd}
.pthumb{width:30px;height:44px;border-radius:3px;object-fit:cover;margin-right:7px;vertical-align:middle;border:1px solid #1a1a35}
.pg{display:flex;align-items:center;justify-content:center;gap:5px;margin-top:12px;flex-wrap:wrap}
.pb{background:#0f0f22;border:1px solid #1a1a35;color:#94a3b8;border-radius:6px;padding:4px 10px;font-size:12px;cursor:pointer;transition:.15s}
.pb:hover,.pb.active{background:#7c3aed;color:#fff;border-color:#7c3aed}
.pi{color:#475569;font-size:12px;padding:0 6px}
.ag{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:16px}
.ac2{background:#0f0f22;border:1px solid #1a1a35;border-radius:12px;padding:18px}
.at{font-size:12px;font-weight:700;color:#94a3b8;margin-bottom:14px;text-transform:uppercase;letter-spacing:.5px}
.sg{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.si2{background:#13132a;border-radius:8px;padding:12px;text-align:center}
.si2 .n{font-size:22px;font-weight:800;color:#a78bfa}.si2 .l{font-size:10px;color:#64748b;margin-top:3px;text-transform:uppercase}
.mo{position:fixed;inset:0;background:rgba(0,0,0,.8);backdrop-filter:blur(4px);z-index:1000;display:none;align-items:center;justify-content:center}
.mo.open{display:flex}
.mbox{background:#0f0f22;border:1px solid #1e1e3f;border-radius:16px;padding:26px;width:min(680px,95vw);max-height:90vh;overflow-y:auto;position:relative}
.mcl{position:absolute;top:14px;right:14px;background:rgba(255,255,255,.08);border:none;color:#94a3b8;width:28px;height:28px;border-radius:50%;font-size:15px;cursor:pointer;display:flex;align-items:center;justify-content:center}
.mcl:hover{background:rgba(239,68,68,.2);color:#f87171}
.mun{font-size:20px;font-weight:800;margin-bottom:4px}
.mem{color:#64748b;font-size:13px;margin-bottom:16px}
.mgr{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:14px}
.ms{background:#13132a;border-radius:8px;padding:10px;text-align:center}
.ms .n{font-size:20px;font-weight:800;color:#a78bfa}.ms .l{font-size:10px;color:#64748b;margin-top:2px;text-transform:uppercase}
.mst{font-size:12px;font-weight:700;color:#7c3aed;text-transform:uppercase;letter-spacing:.5px;margin-bottom:7px}
.mph{display:flex;flex-wrap:wrap;gap:5px}
.mpl{background:#13132a;border:1px solid #1a1a35;border-radius:20px;padding:3px 9px;font-size:12px;color:#cbd5e1}
.mra{display:flex;gap:8px;margin-top:16px;padding-top:14px;border-top:1px solid #1a1a35}
textarea{width:100%;background:#080812;border:1px solid #1a1a35;border-radius:8px;color:#e2e8f0;padding:10px;font-size:13px;resize:vertical;min-height:90px;outline:none;margin:10px 0}
textarea:focus{border-color:#7c3aed}
.sav{background:linear-gradient(135deg,#7c3aed,#e040fb);color:#fff;border:none;border-radius:8px;padding:8px 18px;font-size:13px;font-weight:700;cursor:pointer}
.cnc{background:#13132a;border:1px solid #1a1a35;color:#94a3b8;border-radius:8px;padding:8px 14px;font-size:13px;cursor:pointer}
.toast{position:fixed;bottom:22px;right:22px;padding:11px 18px;border-radius:9px;font-size:13px;font-weight:600;z-index:2000;pointer-events:none;display:none}
.tok{background:#065f46;color:#34d399;border:1px solid rgba(52,211,153,.3)}
.ter{background:#7f1d1d;color:#f87171;border:1px solid rgba(248,113,113,.3)}
footer{text-align:center;padding:14px;color:#1e293b;font-size:12px;border-top:1px solid #0a0a20;margin-top:8px}
@media(max-width:640px){.ag{grid-template-columns:1fr}.mgr{grid-template-columns:repeat(2,1fr)}.cards{grid-template-columns:repeat(3,1fr)}}
</style></head><body>

<header>
<div><div class="ht">&#127921; CineAI Admin Dashboard</div>
<div class="hs">Live PostgreSQL database viewer</div></div>
<div class="hbtns">
<button class="hbtn" onclick="loadData()">&#128260; Refresh</button>
<span class="pill">&#128274; Admin</span>
</div></header>

<div class="cards">
<div class="card active" id="c-analytics" onclick="sw('analytics')"><div class="n" id="st-users">-</div><div class="l">&#128100; Users</div><div class="s" id="st-banned"></div></div>
<div class="card" id="c-watchlist" onclick="sw('watchlist')"><div class="n" id="st-wl">-</div><div class="l">&#128203; Watchlist</div></div>
<div class="card" id="c-favorites" onclick="sw('favorites')"><div class="n" id="st-fav">-</div><div class="l">&#10084; Favorites</div></div>
<div class="card" id="c-reviews" onclick="sw('reviews')"><div class="n" id="st-rev">-</div><div class="l">&#128172; Reviews</div></div>
<div class="card" id="c-messages" onclick="sw('messages')"><div class="n" id="st-msg">-</div><div class="l">&#128233; Messages</div><div class="s" id="st-unread"></div></div>
</div>

<div class="tabs">
<div class="tab active" id="tb-analytics" onclick="sw('analytics')">&#128202; Analytics</div>
<div class="tab" id="tb-users" onclick="sw('users')">&#128100; Users</div>
<div class="tab" id="tb-watchlist" onclick="sw('watchlist')">&#128203; Watchlist</div>
<div class="tab" id="tb-favorites" onclick="sw('favorites')">&#10084; Favorites</div>
<div class="tab" id="tb-reviews" onclick="sw('reviews')">&#128172; Reviews</div>
<div class="tab" id="tb-messages" onclick="sw('messages')">&#128233; Messages <span class="badge" id="unread-badge" style="display:none"></span></div>
</div>

<div class="panel active" id="panel-analytics">
<div class="ag">
<div class="ac2"><div class="at">&#128202; Platform Overview</div>
<div class="sg">
<div class="si2"><div class="n" id="an-users">-</div><div class="l">Users</div></div>
<div class="si2"><div class="n" id="an-rev">-</div><div class="l">Reviews</div></div>
<div class="si2"><div class="n" id="an-wl">-</div><div class="l">Watchlist</div></div>
<div class="si2"><div class="n" id="an-fav">-</div><div class="l">Favorites</div></div>
<div class="si2"><div class="n" id="an-ban" style="color:#f87171">-</div><div class="l" style="color:#f87171">Banned</div></div>
<div class="si2"><div class="n" id="an-msg" style="color:#818cf8">-</div><div class="l">Messages</div></div>
</div></div>
<div class="ac2"><div class="at">&#128578; Sentiment Distribution</div>
<canvas id="sentChart" height="160"></canvas>
</div></div>
<div class="ac2" style="margin-bottom:14px">
<div class="at">&#128229; Quick Exports</div>
<div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:10px">
<button class="ebtn" onclick="exportCSV('users')">&#128229; Users CSV</button>
<button class="ebtn" onclick="exportCSV('reviews')">&#128229; Reviews CSV</button>
<button class="ebtn" onclick="exportCSV('messages')">&#128229; Messages CSV</button>
</div></div>
</div>

<div class="panel" id="panel-users">
<div class="toolbar">
<div class="sw"><span class="si">&#128269;</span><input class="sbox" id="srch-users" placeholder="Search username, email, ID..." oninput="filt('users')"/></div>
<select class="fsel" id="fbanned" onchange="filt('users')"><option value="">All Users</option><option value="active">Active Only</option><option value="banned">Banned Only</option></select>
<span class="rc" id="cnt-users">-</span>
<button class="ebtn" onclick="exportCSV('users')">&#128229; CSV</button>
</div>
<div class="tw"><table id="tbl-users"><thead><tr><th>ID</th><th>Username</th><th>Email</th><th>Age</th><th>Gender</th><th>Genres</th><th>Joined</th><th>Status</th><th>Actions</th></tr></thead>
<tbody id="body-users"><tr><td colspan="9" class="empty">Loading...</td></tr></tbody></table></div>
<div class="pg" id="pg-users"></div>
</div>

<div class="panel" id="panel-watchlist">
<div class="toolbar">
<div class="sw"><span class="si">&#128269;</span><input class="sbox" id="srch-watchlist" placeholder="Search movie title, user ID..." oninput="filt('watchlist')"/></div>
<span class="rc" id="cnt-watchlist">-</span><button class="ebtn" onclick="exportCSV('watchlist')">&#128229; CSV</button>
</div>
<div class="tw"><table id="tbl-watchlist"><thead><tr><th>ID</th><th>User ID</th><th>Movie ID</th><th>Movie Title</th></tr></thead>
<tbody id="body-watchlist"><tr><td colspan="4" class="empty">Loading...</td></tr></tbody></table></div>
<div class="pg" id="pg-watchlist"></div>
</div>

<div class="panel" id="panel-favorites">
<div class="toolbar">
<div class="sw"><span class="si">&#128269;</span><input class="sbox" id="srch-favorites" placeholder="Search movie title, user ID..." oninput="filt('favorites')"/></div>
<span class="rc" id="cnt-favorites">-</span><button class="ebtn" onclick="exportCSV('favorites')">&#128229; CSV</button>
</div>
<div class="tw"><table id="tbl-favorites"><thead><tr><th>ID</th><th>User ID</th><th>Movie ID</th><th>Movie Title</th></tr></thead>
<tbody id="body-favorites"><tr><td colspan="4" class="empty">Loading...</td></tr></tbody></table></div>
<div class="pg" id="pg-favorites"></div>
</div>

<div class="panel" id="panel-reviews">
<div class="toolbar">
<div class="sw"><span class="si">&#128269;</span><input class="sbox" id="srch-reviews" placeholder="Search movie, user, review text..." oninput="filt('reviews')"/></div>
<select class="fsel" id="fsent" onchange="filt('reviews')"><option value="">All Sentiments</option><option value="positive">Positive</option><option value="negative">Negative</option><option value="neutral">Neutral</option></select>
<span class="rc" id="cnt-reviews">-</span><button class="ebtn" onclick="exportCSV('reviews')">&#128229; CSV</button>
</div>
<div class="tw"><table id="tbl-reviews"><thead><tr><th>ID</th><th>User</th><th>Movie</th><th>Review</th><th>Sentiment</th><th>Actions</th></tr></thead>
<tbody id="body-reviews"><tr><td colspan="6" class="empty">Loading...</td></tr></tbody></table></div>
<div class="pg" id="pg-reviews"></div>
</div>

<div class="panel" id="panel-messages">
<div class="toolbar">
<div class="sw"><span class="si">&#128269;</span><input class="sbox" id="srch-messages" placeholder="Search name, email, subject..." oninput="filt('messages')"/></div>
<span class="rc" id="cnt-messages">-</span><button class="ebtn" onclick="exportCSV('messages')">&#128229; CSV</button>
</div>
<div class="tw"><table id="tbl-messages"><thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Subject</th><th>Message</th><th>Date</th><th>Status</th><th>Actions</th></tr></thead>
<tbody id="body-messages"><tr><td colspan="8" class="empty">Loading...</td></tr></tbody></table></div>
<div class="pg" id="pg-messages"></div>
</div>

<div class="mo" id="userModal" onclick="if(event.target===this)closeModal()">
<div class="mbox"><button class="mcl" onclick="closeModal()">&#10005;</button><div id="modal-content"></div></div>
</div>
<div class="mo" id="editModal" onclick="if(event.target===this)closeEdit()">
<div class="mbox" style="max-width:500px">
<button class="mcl" onclick="closeEdit()">&#10005;</button>
<h3 style="margin-bottom:6px;font-size:16px">&#9999; Edit Review</h3>
<p style="color:#64748b;font-size:12px">Edit the review text below</p>
<textarea id="edit-ta" rows="5"></textarea>
<div style="display:flex;gap:10px;justify-content:flex-end">
<button class="cnc" onclick="closeEdit()">Cancel</button>
<button class="sav" onclick="saveReview()">&#128190; Save</button>
</div></div>
</div>

<div class="toast" id="toast"></div>
<footer>CineAI Admin Dashboard &bull; PostgreSQL &bull; &#128274; Admin Only</footer>

<script>
var KEY=new URLSearchParams(window.location.search).get('key')||'';
var TMDB='https://image.tmdb.org/t/p/w92';
var PER=25,PAGES={},D=null,chartInst=null;

function q(id){return document.getElementById(id);}
function esc(v){return String(v||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}

async function loadData(){
  ['users','watchlist','favorites','reviews','messages'].forEach(t=>{var b=q('body-'+t);if(b)b.innerHTML='<tr><td colspan="9" class="empty">Loading...</td></tr>';});
  try{
    var r=await fetch('/admin/api/data?key='+encodeURIComponent(KEY));
    if(!r.ok){toast('Error: '+r.status,'ter');return;}
    D=await r.json();renderAll();
  }catch(e){toast('Failed: '+e.message,'ter');}
}

function renderAll(){
  var s=D.stats;
  q('st-users').textContent=s.users;q('st-banned').textContent=s.banned+' banned';
  q('st-wl').textContent=s.watchlist;q('st-fav').textContent=s.favorites;
  q('st-rev').textContent=s.reviews;q('st-msg').textContent=s.messages;
  if(s.unread_msgs>0){q('st-unread').textContent=s.unread_msgs+' unread';q('st-unread').style.color='#e50914';var b=q('unread-badge');b.textContent=s.unread_msgs;b.style.display='inline';}
  q('an-users').textContent=s.users;q('an-rev').textContent=s.reviews;
  q('an-wl').textContent=s.watchlist;q('an-fav').textContent=s.favorites;
  q('an-ban').textContent=s.banned;q('an-msg').textContent=s.messages;
  q('tb-users').innerHTML='&#128100; Users ('+s.users+')';
  q('tb-reviews').innerHTML='&#128172; Reviews ('+s.reviews+')';
  renderChart(s.pos,s.neg,s.neu);
  buildUsers();buildWL('watchlist');buildWL('favorites');buildReviews();buildMessages();
}

function renderChart(pos,neg,neu){
  var ctx=q('sentChart');if(!ctx)return;
  if(chartInst)chartInst.destroy();
  chartInst=new Chart(ctx,{type:'doughnut',data:{labels:['Positive','Negative','Neutral'],datasets:[{data:[pos,neg,neu],backgroundColor:['rgba(16,185,129,.7)','rgba(239,68,68,.7)','rgba(148,163,184,.5)'],borderColor:['#10b981','#ef4444','#94a3b8'],borderWidth:1.5,hoverOffset:6}]},options:{responsive:true,maintainAspectRatio:true,plugins:{legend:{position:'bottom',labels:{color:'#94a3b8',font:{size:11},padding:14}},tooltip:{callbacks:{label:c=>' '+c.label+': '+c.parsed+' reviews'}}}}});
}

function buildUsers(){
  var b=q('body-users');if(!b)return;
  if(!D.users.length){b.innerHTML='<tr><td colspan="9" class="empty">No users yet</td></tr>';return;}
  b.innerHTML=D.users.map(u=>{
    var bn=u.is_banned;
    var banBtn=bn?'<button class="ba unb-btn" onclick="act(\'POST\',\'/admin/users/'+u.id+'/unban\',this)">Unban</button>':'<button class="ba ban-btn" onclick="act(\'POST\',\'/admin/users/'+u.id+'/ban\',this)">Ban</button>';
    return '<tr class="dr'+(bn?' banned':'')+'" data-s="'+esc(u.username)+' '+esc(u.email)+' '+u.id+'" data-ban="'+(bn?'banned':'active')+'">'
      +'<td>'+u.id+'</td>'
      +'<td><span class="ulink" onclick="showUser('+u.id+')">'+esc(u.username)+'</span></td>'
      +'<td>'+esc(u.email)+'</td><td>'+(u.age||'-')+'</td><td>'+esc(u.gender||'-')+'</td>'
      +'<td style="max-width:160px">'+esc(u.favorite_genres||'-')+'</td>'
      +'<td>'+u.created_at+'</td>'
      +'<td>'+(bn?'&#128308; Banned':'&#128994; Active')+'</td>'
      +'<td class="ac">'+banBtn+'<button class="ba del-btn" onclick="act(\'DELETE\',\'/admin/users/'+u.id+'\',this,true)">Delete</button></td>'
      +'</tr>';
  }).join('');
  initPage('users');
}

function buildWL(tid){
  var data=D[tid],b=q('body-'+tid);if(!b)return;
  if(!data.length){b.innerHTML='<tr><td colspan="4" class="empty">No '+tid+' yet</td></tr>';return;}
  b.innerHTML=data.map(w=>{
    var img=w.poster_path?'<img src="'+TMDB+(w.poster_path.startsWith('/')?'':'/')+w.poster_path+'" class="pthumb" onerror="this.style.display=\'none\'" loading="lazy"/>':'<span style="font-size:18px;margin-right:6px">&#127916;</span>';
    return '<tr class="dr" data-s="'+esc(w.movie_title)+' '+w.user_id+'"><td>'+w.id+'</td><td>'+w.user_id+'</td><td>'+w.movie_id+'</td><td>'+img+esc(w.movie_title)+'</td></tr>';
  }).join('');
  initPage(tid);
}

function buildReviews(){
  var b=q('body-reviews');if(!b)return;
  if(!D.reviews.length){b.innerHTML='<tr><td colspan="6" class="empty">No reviews yet</td></tr>';return;}
  b.innerHTML=D.reviews.map(r=>{
    var prev=esc(r.review_text.length>80?r.review_text.slice(0,80)+'...':r.review_text);
    var full=esc(r.review_text);
    return '<tr class="dr" data-s="'+esc(r.movie_title)+' '+r.user_id+' '+esc(r.review_text.slice(0,40))+'" data-sent="'+r.sentiment+'">'
      +'<td>'+r.id+'</td><td>'+r.user_id+'</td><td>'+esc(r.movie_title)+'</td>'
      +'<td title="'+full+'">'+prev+'</td>'
      +'<td><span class="sb '+r.sentiment+'">'+r.sentiment+'</span></td>'
      +'<td class="ac"><button class="ba edt-btn" onclick="editRev('+r.id+',this.dataset.t)" data-t="'+full+'">Edit</button>'
      +'<button class="ba del-btn" onclick="act(\'DELETE\',\'/admin/reviews/'+r.id+'\',this,true)">Del</button></td>'
      +'</tr>';
  }).join('');
  initPage('reviews');
}

function buildMessages(){
  var b=q('body-messages');if(!b)return;
  if(!D.messages.length){b.innerHTML='<tr><td colspan="8" class="empty">No messages yet</td></tr>';return;}
  b.innerHTML=D.messages.map(m=>{
    var prev=esc(m.message.length>80?m.message.slice(0,80)+'...':m.message);
    var rdBtn=!m.is_read?'<button class="ba edt-btn" onclick="act(\'POST\',\'/admin/messages/'+m.id+'/read\',this)">Mark Read</button>':'';
    return '<tr class="dr'+(m.is_read?'':' unread')+'" data-s="'+esc(m.name)+' '+esc(m.email)+' '+esc(m.subject)+'">'
      +'<td>'+m.id+'</td><td>'+esc(m.name)+'</td><td>'+esc(m.email)+'</td><td>'+esc(m.subject)+'</td>'
      +'<td title="'+esc(m.message)+'">'+prev+'</td>'
      +'<td>'+m.created_at+'</td><td>'+(m.is_read?'&#9989; Read':'&#128994; New')+'</td>'
      +'<td class="ac">'+rdBtn+'<button class="ba del-btn" onclick="act(\'DELETE\',\'/admin/messages/'+m.id+'\',this,true)">Del</button></td>'
      +'</tr>';
  }).join('');
  initPage('messages');
}

function initPage(tid){PAGES[tid]=1;filt(tid);}

function renderPage(tid){
  var rows=Array.from(document.querySelectorAll('#body-'+tid+' tr.dr:not(.hidden)'));
  var pg=PAGES[tid]||1,total=rows.length,pages=Math.ceil(total/PER)||1;
  rows.forEach((r,i)=>r.style.display=(i>=(pg-1)*PER&&i<pg*PER)?'':'none');
  var el=q('pg-'+tid);if(!el)return;
  if(pages<=1){el.innerHTML='';return;}
  var h='<button class="pb" onclick="gp(\''+tid+'\','+Math.max(1,pg-1)+')">&#8249;</button>';
  for(var p=Math.max(1,pg-2);p<=Math.min(pages,pg+2);p++)h+='<button class="pb'+(p===pg?' active':'')+'" onclick="gp(\''+tid+'\','+p+')">'+p+'</button>';
  h+='<button class="pb" onclick="gp(\''+tid+'\','+Math.min(pages,pg+1)+')">&#8250;</button><span class="pi">Page '+pg+'/'+pages+' ('+total+')</span>';
  el.innerHTML=h;
}

function gp(tid,p){PAGES[tid]=p;renderPage(tid);}

function filt(tid){
  var q2=(q('srch-'+tid)||{}).value||'';q2=q2.toLowerCase().trim();
  var sent=(q('fsent')||{}).value||'',ban=(q('fbanned')||{}).value||'';
  var rows=document.querySelectorAll('#body-'+tid+' tr.dr');
  var vis=0;
  rows.forEach(r=>{
    var s=(r.dataset.s||'').toLowerCase();
    var ok=!q2||s.includes(q2);
    if(sent)ok=ok&&r.dataset.sent===sent;
    if(ban==='active')ok=ok&&r.dataset.ban==='active';
    if(ban==='banned')ok=ok&&r.dataset.ban==='banned';
    r.classList.toggle('hidden',!ok);if(ok)vis++;
  });
  var ce=q('cnt-'+tid);if(ce)ce.textContent=(q2||sent||ban?vis+' of '+rows.length:rows.length)+' records';
  PAGES[tid]=1;renderPage(tid);
}

var TABS=['analytics','users','watchlist','favorites','reviews','messages'];
function sw(name){TABS.forEach(t=>{var p=q('panel-'+t),tb=q('tb-'+t),c=q('c-'+t);if(p)p.classList.toggle('active',t===name);if(tb)tb.classList.toggle('active',t===name);if(c)c.classList.toggle('active',t===name);});}

async function act(method,url,btn,confirm_it){
  if(confirm_it&&!confirm('Are you sure? This cannot be undone.'))return;
  btn.disabled=true;var orig=btn.textContent;btn.textContent='...';
  try{
    var r=await fetch(url+'?key='+encodeURIComponent(KEY),{method});
    var d=await r.json();if(!r.ok)throw new Error(d.detail||'Error');
    toast('Done!','tok');setTimeout(()=>loadData(),700);
  }catch(e){toast('Error: '+e.message,'ter');btn.disabled=false;btn.textContent=orig;}
}

function showUser(uid){
  if(!D)return;var u=D.users.find(x=>x.id===uid);if(!u)return;
  var revs=D.reviews.filter(r=>r.user_id===uid);
  var wl=D.watchlist.filter(w=>w.user_id===uid);
  var fav=D.favorites.filter(f=>f.user_id===uid);
  var pos=revs.filter(r=>r.sentiment==='positive').length;
  var neg=revs.filter(r=>r.sentiment==='negative').length;
  var mood=pos>neg?'Positive':neg>pos?'Negative':'Neutral';
  var mc=pos>neg?'#34d399':neg>pos?'#f87171':'#94a3b8';
  q('modal-content').innerHTML=
    '<div class="mun">'+(u.is_banned?'&#128308; ':'')+esc(u.username)+'</div>'
    +'<div class="mem">'+esc(u.email)+'</div>'
    +'<div class="mgr">'
    +'<div class="ms"><div class="n">'+revs.length+'</div><div class="l">Reviews</div></div>'
    +'<div class="ms"><div class="n">'+wl.length+'</div><div class="l">Watchlist</div></div>'
    +'<div class="ms"><div class="n">'+fav.length+'</div><div class="l">Favorites</div></div>'
    +'<div class="ms"><div class="n" style="color:'+mc+'">'+mood+'</div><div class="l">Mood</div></div>'
    +'</div>'
    +(u.favorite_genres?'<p style="font-size:13px;color:#94a3b8;margin-bottom:12px">Genres: '+esc(u.favorite_genres)+'</p>':'')
    +(wl.length?'<div class="mst">&#128203; Watchlist</div><div class="mph" style="margin-bottom:12px">'+wl.slice(0,8).map(w=>'<span class="mpl">'+esc(w.movie_title)+'</span>').join('')+'</div>':'')
    +(fav.length?'<div class="mst">&#10084; Favorites</div><div class="mph" style="margin-bottom:12px">'+fav.slice(0,8).map(f=>'<span class="mpl">'+esc(f.movie_title)+'</span>').join('')+'</div>':'')
    +(revs.length?'<div class="mst">&#128172; Recent Reviews</div>'+revs.slice(0,5).map(r=>'<div style="background:#13132a;border-radius:7px;padding:9px;margin-bottom:6px"><span class="sb '+r.sentiment+'">'+r.sentiment+'</span><span style="font-size:11px;color:#64748b;margin-left:6px">'+esc(r.movie_title)+'</span><div style="font-size:12px;color:#94a3b8;margin-top:4px">'+esc(r.review_text.slice(0,80))+'</div></div>').join(''):'')
    +'<div class="mra">'
    +(u.is_banned?'<button class="ba unb-btn" style="padding:7px 14px;font-size:13px" onclick="act(\'POST\',\'/admin/users/'+u.id+'/unban\',this)">&#9989; Unban</button>':'<button class="ba ban-btn" style="padding:7px 14px;font-size:13px" onclick="act(\'POST\',\'/admin/users/'+u.id+'/ban\',this)">&#128683; Ban</button>')
    +'<button class="ba del-btn" style="padding:7px 14px;font-size:13px" onclick="act(\'DELETE\',\'/admin/users/'+u.id+'\',this,true)">&#128465; Delete</button>'
    +'</div>';
  q('userModal').classList.add('open');
}
function closeModal(){q('userModal').classList.remove('open');}

var _eid=null;
function editRev(id,text){_eid=id;q('edit-ta').value=text.replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&amp;/g,'&').replace(/&quot;/g,'"');q('editModal').classList.add('open');}
function closeEdit(){q('editModal').classList.remove('open');_eid=null;}
async function saveReview(){
  if(!_eid)return;var txt=q('edit-ta').value.trim();if(!txt)return toast('Review text is empty','ter');
  try{
    var r=await fetch('/admin/reviews/'+_eid+'?key='+encodeURIComponent(KEY),{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({review_text:txt})});
    if(!r.ok)throw new Error('Failed');toast('Review updated','tok');closeEdit();setTimeout(()=>loadData(),700);
  }catch(e){toast('Error: '+e.message,'ter');}
}

function exportCSV(tid){
  var tbl=document.getElementById('tbl-'+tid);if(!tbl)return;
  var rows=Array.from(tbl.querySelectorAll('tr')).filter(r=>!r.classList.contains('hidden'));
  var csv=rows.map(r=>Array.from(r.querySelectorAll('th,td')).slice(0,-1).map(c=>'"'+c.textContent.trim().replace(/"/g,'""')+'"').join(',')).join('\\n');
  var a=document.createElement('a');
  a.href='data:text/csv;charset=utf-8,'+encodeURIComponent(csv);
  a.download='cineai_'+tid+'_'+new Date().toISOString().slice(0,10)+'.csv';a.click();
}

function toast(msg,cls){var t=q('toast');t.textContent=msg;t.className='toast '+cls;t.style.display='block';setTimeout(()=>t.style.display='none',2600);}

window.addEventListener('DOMContentLoaded',loadData);
</script></body></html>"""
