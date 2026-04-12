"""
Admin Dashboard v3 — 100% Server-Side Rendered
- Search / Filter: done in Python (URL query params, no JS needed)
- CSV Export:      dedicated /admin/export/{table} endpoints (no JS Blob)
- Charts:          Python-rendered CSS bars (no Chart.js CDN)
- Actions:         JS fetch() for ban/delete/read (AJAX, no page reload)
- Tab switching:   CSS radio-button (no JS)
"""
import html as _html
import io, csv, os, json
from datetime import datetime
from sqlalchemy import text
from database import SessionLocal

ADMIN_SECRET = os.getenv("ADMIN_SECRET", "cineai-admin-2024")
TMDB = "https://image.tmdb.org/t/p/w92"


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _e(v):
    return _html.escape(str(v) if v is not None else "")

def _fmt(dt):
    return str(dt)[:16].replace("T", " ") if dt else "-"


# ─── Data Fetching ────────────────────────────────────────────────────────────

def _get_data():
    db = SessionLocal()
    users, wl, fav, rev, msgs, popular = [], [], [], [], [], []
    try:
        rows = db.execute(text("""
            SELECT u.id,u.username,u.email,u.age,u.gender,u.favorite_genres,
                   COALESCE(u.is_banned,false),u.created_at,u.last_login,
                   COUNT(DISTINCT w.id),COUNT(DISTINCT f.id),COUNT(DISTINCT r.id),
                   u.hashed_password
            FROM users u
            LEFT JOIN watchlist w ON w.user_id=u.id
            LEFT JOIN favorites f ON f.user_id=u.id
            LEFT JOIN reviews r   ON r.user_id=u.id
            GROUP BY u.id ORDER BY u.id DESC
        """)).fetchall()
        for row in rows:
            users.append({"id": row[0], "username": row[1] or "",
                          "email": row[2] or "", "age": row[3],
                          "gender": row[4] or "", "favorite_genres": row[5] or "",
                          "is_banned": bool(row[6]),
                          "created_at": _fmt(row[7]), "last_login": _fmt(row[8]),
                          "wl_count": int(row[9] or 0), "fav_count": int(row[10] or 0),
                          "rev_count": int(row[11] or 0),
                          "hashed_password": str(row[12] or "")[:30]})
    except Exception as e:
        db.rollback()
        print(f"[ADMIN] users: {e}")
        try:
            for row in db.execute(text(
                "SELECT id,username,email,age,gender,favorite_genres,created_at,hashed_password "
                "FROM users ORDER BY id DESC")).fetchall():
                users.append({"id": row[0], "username": row[1] or "",
                              "email": row[2] or "", "age": row[3],
                              "gender": row[4] or "", "favorite_genres": row[5] or "",
                              "is_banned": False, "created_at": _fmt(row[6]),
                              "last_login": "-", "wl_count": 0, "fav_count": 0, "rev_count": 0,
                              "hashed_password": str(row[7] or "")[:30]})
        except Exception:
            db.rollback()

    try:
        for row in db.execute(text(
                "SELECT id,user_id,movie_id,movie_title,COALESCE(poster_path,''),added_at "
                "FROM watchlist ORDER BY added_at DESC")).fetchall():
            wl.append({"id": row[0], "user_id": row[1], "movie_id": row[2],
                       "movie_title": row[3] or "", "poster_path": row[4] or "",
                       "added_at": _fmt(row[5])})
    except Exception:
        db.rollback()

    try:
        for row in db.execute(text(
                "SELECT id,user_id,movie_id,movie_title,COALESCE(poster_path,''),added_at "
                "FROM favorites ORDER BY added_at DESC")).fetchall():
            fav.append({"id": row[0], "user_id": row[1], "movie_id": row[2],
                        "movie_title": row[3] or "", "poster_path": row[4] or "",
                        "added_at": _fmt(row[5])})
    except Exception:
        db.rollback()

    try:
        for row in db.execute(text(
                "SELECT id,user_id,movie_id,movie_title,review_text,sentiment,created_at "
                "FROM reviews ORDER BY id DESC")).fetchall():
            rev.append({"id": row[0], "user_id": row[1], "movie_id": row[2],
                        "movie_title": row[3] or "", "review_text": row[4] or "",
                        "sentiment": row[5] or "", "created_at": _fmt(row[6])})
    except Exception:
        db.rollback()

    try:
        for row in db.execute(text(
                "SELECT id,name,email,subject,message,is_read,created_at "
                "FROM contact_messages ORDER BY created_at DESC")).fetchall():
            msgs.append({"id": row[0], "name": row[1] or "", "email": row[2] or "",
                         "subject": row[3] or "", "message": row[4] or "",
                         "is_read": bool(row[5]), "created_at": _fmt(row[6])})
    except Exception:
        db.rollback()

    try:
        rows = db.execute(text("""
            SELECT movie_title,COUNT(*) cnt FROM (
              SELECT movie_title FROM watchlist
              UNION ALL SELECT movie_title FROM favorites
            ) t WHERE movie_title IS NOT NULL AND movie_title!=''
            GROUP BY movie_title ORDER BY cnt DESC LIMIT 10
        """)).fetchall()
        popular = [{"title": r[0], "count": int(r[1])} for r in rows]
    except Exception:
        db.rollback()

    db.close()
    return {"users": users, "watchlist": wl, "favorites": fav,
            "reviews": rev, "messages": msgs, "popular": popular}


# ─── Server-side filtering ────────────────────────────────────────────────────

def _apply_filters(data, tab, q, status, sort, sent, rd):
    """Filter all datasets in Python based on URL params."""
    q = (q or "").strip().lower()

    if tab == "users":
        ul = data["users"]
        if q:
            ul = [u for u in ul
                  if q in (u["username"] + " " + u["email"] + " " + str(u["id"])).lower()]
        if status == "active":
            ul = [u for u in ul if not u["is_banned"]
                  and u["rev_count"] + u["wl_count"] + u["fav_count"] > 0]
        elif status == "inactive":
            ul = [u for u in ul if not u["is_banned"]
                  and u["rev_count"] + u["wl_count"] + u["fav_count"] == 0]
        elif status == "banned":
            ul = [u for u in ul if u["is_banned"]]
        if sort == "oldest":
            ul = sorted(ul, key=lambda u: u["id"])
        elif sort == "reviews":
            ul = sorted(ul, key=lambda u: u["rev_count"], reverse=True)
        elif sort == "watchlist":
            ul = sorted(ul, key=lambda u: u["wl_count"], reverse=True)
        data["users"] = ul

    elif tab == "watchlist":
        wl = data["watchlist"]
        if q:
            wl = [w for w in wl
                  if q in (w["movie_title"] + " " + str(w["user_id"])).lower()]
        data["watchlist"] = wl

    elif tab == "favorites":
        fav = data["favorites"]
        if q:
            fav = [f for f in fav
                   if q in (f["movie_title"] + " " + str(f["user_id"])).lower()]
        data["favorites"] = fav

    elif tab == "reviews":
        rl = data["reviews"]
        if q:
            rl = [r for r in rl
                  if q in (r["movie_title"] + " " + r["review_text"] + " " + str(r["user_id"])).lower()]
        if sent:
            rl = [r for r in rl if r["sentiment"] == sent]
        data["reviews"] = rl

    elif tab == "messages":
        ml = data["messages"]
        if q:
            ml = [m for m in ml
                  if q in (m["name"] + " " + m["email"] + " " + m["subject"] + " " + m["message"]).lower()]
        if rd == "read":
            ml = [m for m in ml if m["is_read"]]
        elif rd == "unread":
            ml = [m for m in ml if not m["is_read"]]
        data["messages"] = ml

    return data


# ─── CSV Generation (backend, no JS Blob) ─────────────────────────────────────

def get_csv_content(table: str) -> str:
    """Return CSV string with UTF-8 BOM for Excel compatibility."""
    data = _get_data()
    out = io.StringIO()
    w = csv.writer(out, quoting=csv.QUOTE_ALL)

    if table == "users":
        w.writerow(["ID", "Username", "Email", "Age", "Gender", "Genres",
                    "Reviews", "Watchlist", "Favorites", "Registered", "Last Login", "Status"])
        for u in data["users"]:
            st = "Banned" if u["is_banned"] else (
                "Active" if u["rev_count"] + u["wl_count"] + u["fav_count"] > 0 else "Inactive")
            w.writerow([u["id"], u["username"], u["email"], u["age"] or "",
                        u["gender"], u["favorite_genres"],
                        u["rev_count"], u["wl_count"], u["fav_count"],
                        u["created_at"], u["last_login"], st])

    elif table == "watchlist":
        w.writerow(["ID", "User ID", "Movie ID", "Movie Title", "Added At"])
        for x in data["watchlist"]:
            w.writerow([x["id"], x["user_id"], x["movie_id"], x["movie_title"], x["added_at"]])

    elif table == "favorites":
        w.writerow(["ID", "User ID", "Movie ID", "Movie Title", "Added At"])
        for x in data["favorites"]:
            w.writerow([x["id"], x["user_id"], x["movie_id"], x["movie_title"], x["added_at"]])

    elif table == "reviews":
        w.writerow(["ID", "User ID", "Movie ID", "Movie Title", "Review", "Sentiment", "Date"])
        for x in data["reviews"]:
            w.writerow([x["id"], x["user_id"], x["movie_id"], x["movie_title"],
                        x["review_text"], x["sentiment"], x["created_at"]])

    elif table == "messages":
        w.writerow(["ID", "Name", "Email", "Subject", "Message", "Sent At", "Status"])
        for x in data["messages"]:
            w.writerow([x["id"], x["name"], x["email"], x["subject"],
                        x["message"], x["created_at"],
                        "Read" if x["is_read"] else "Unread"])
    else:
        return ""

    return "\ufeff" + out.getvalue()


# ─── HTML Row Builders ────────────────────────────────────────────────────────

def _users_html(users, key):
    if not users:
        return '<tr><td colspan="13" class="empty">No users found</td></tr>'
    rows = []
    for u in users:
        bn = u["is_banned"]
        act = u["rev_count"] + u["wl_count"] + u["fav_count"] > 0
        status = "banned" if bn else ("active" if act else "inactive")
        status_label = "Banned" if bn else ("Active" if act else "Inactive")
        ban_lbl = "Unban" if bn else "Ban"
        ban_url = f"/admin/users/{u['id']}/{'unban' if bn else 'ban'}"
        ban_cls = "unb-btn" if bn else "ban-btn"
        genres = _e(u["favorite_genres"][:22]) if u["favorite_genres"] else "-"
        pwd = u.get("hashed_password", "")
        pwd_show = (_e(pwd[:20]) + "&#8230;") if len(pwd) > 20 else _e(pwd or "-")
        rows.append(
            f'<tr class="dr{" banned" if bn else ""}">'
            f'<td>{u["id"]}</td>'
            f'<td><span class="ulink" onclick="showUser({u["id"]})">{_e(u["username"])}</span></td>'
            f'<td>{_e(u["email"])}</td>'
            f'<td title="{_e(pwd)}" style="font-family:monospace;font-size:11px;'
            f'color:#7c3aed;max-width:130px">{pwd_show}</td>'
            f'<td>{u["age"] or "-"}</td>'
            f'<td>{_e(u["gender"] or "-")}</td>'
            f'<td title="{_e(u["favorite_genres"])}">{genres}</td>'
            f'<td style="text-align:center">{u["rev_count"]}</td>'
            f'<td style="text-align:center">{u["wl_count"]}</td>'
            f'<td>{u["created_at"]}</td>'
            f'<td>{u["last_login"]}</td>'
            f'<td><span class="sb {status}">{status_label}</span></td>'
            f'<td style="white-space:nowrap">'
            f'<button type="button" class="ba {ban_cls}" '
            f'onclick="doAction(\'POST\',\'{ban_url}\')">{ban_lbl}</button>'
            f'<button type="button" class="ba del-btn" '
            f'onclick="doAction(\'DELETE\',\'/admin/users/{u["id"]}\',true)">Del</button>'
            f'</td>'
            f'</tr>'
        )
    return "\n".join(rows)


def _wl_html(items, name):
    if not items:
        return f'<tr><td colspan="5" class="empty">No {name} found</td></tr>'
    rows = []
    for w in items:
        pp = w["poster_path"]
        img = (f'<img src="{TMDB}{"" if pp.startswith("/") else "/"}{pp}" '
               f'class="pthumb" onerror="this.style.display=\'none\'" loading="lazy"/>'
               if pp else "")
        rows.append(
            f'<tr class="dr">'
            f'<td>{w["id"]}</td><td>{w["user_id"]}</td><td>{w["movie_id"]}</td>'
            f'<td>{img}{_e(w["movie_title"])}</td>'
            f'<td>{w["added_at"]}</td></tr>'
        )
    return "\n".join(rows)


def _reviews_html(reviews):
    if not reviews:
        return '<tr><td colspan="6" class="empty">No reviews found</td></tr>'
    rows = []
    for r in reviews:
        txt = r["review_text"]
        preview = _e(txt[:80] + "..." if len(txt) > 80 else txt)
        rows.append(
            f'<tr class="dr">'
            f'<td>{r["id"]}</td><td>{r["user_id"]}</td>'
            f'<td>{_e(r["movie_title"])}</td>'
            f'<td title="{_e(txt)}">{preview}</td>'
            f'<td><span class="sb {_e(r["sentiment"])}">{_e(r["sentiment"])}</span></td>'
            f'<td>{r["created_at"]}</td></tr>'
        )
    return "\n".join(rows)


def _messages_html(messages, key):
    if not messages:
        return '<tr><td colspan="7" class="empty">No messages found</td></tr>'
    rows = []
    for m in messages:
        msg = m["message"]
        preview = _e(msg[:80] + "..." if len(msg) > 80 else msg)
        is_read = m["is_read"]
        read_btn = ("" if is_read else
                    f'<button type="button" class="ba rd-btn" '
                    f'onclick="doAction(\'POST\',\'/admin/messages/{m["id"]}/read\')">'
                    f'Mark Read</button>')
        del_btn = (f'<button type="button" class="ba del-btn" '
                   f'onclick="doAction(\'DELETE\',\'/admin/messages/{m["id"]}\',true)">'
                   f'Del</button>')
        rows.append(
            f'<tr class="dr{" unread" if not is_read else ""}">'
            f'<td>{m["id"]}</td><td>{_e(m["name"])}</td><td>{_e(m["email"])}</td>'
            f'<td>{_e(m["subject"])}</td>'
            f'<td title="{_e(msg)}">{preview}</td>'
            f'<td>{m["created_at"]}</td>'
            f'<td>{"&#9989; Read" if is_read else "&#128308; New"}</td>'
            f'<td style="white-space:nowrap">{read_btn}{del_btn}</td></tr>'
        )
    return "\n".join(rows)


# ─── CSS Chart Builders (no Chart.js, no CDN) ─────────────────────────────────

def _sentiment_chart_html(pos, neg, neu):
    total = pos + neg + neu
    if total == 0:
        return '<div class="empty">No review data yet</div>'
    def bar(count, color, label):
        pct = round(count / total * 100)
        return (f'<div style="margin-bottom:12px">'
                f'<div style="display:flex;justify-content:space-between;'
                f'font-size:12px;margin-bottom:4px">'
                f'<span style="color:{color};font-weight:600">{label}</span>'
                f'<span style="color:#94a3b8">{count} ({pct}%)</span></div>'
                f'<div style="background:#0d0d20;border-radius:4px;height:18px">'
                f'<div style="width:{pct}%;background:{color};height:100%;'
                f'border-radius:4px;transition:width .4s"></div></div></div>')
    return (bar(pos, "#10b981", "Positive") +
            bar(neg, "#ef4444", "Negative") +
            bar(neu, "#94a3b8", "Neutral"))


def _popular_chart_html(popular):
    if not popular:
        return '<div class="empty">No watchlist/favorites data yet</div>'
    max_count = popular[0]["count"] if popular else 1
    items = []
    for i, p in enumerate(popular[:10]):
        pct = round(p["count"] / max_count * 100)
        items.append(
            f'<div style="margin-bottom:8px">'
            f'<div style="display:flex;align-items:center;gap:8px">'
            f'<span style="font-size:11px;color:#475569;min-width:18px">{i+1}.</span>'
            f'<div style="flex:1;background:#0d0d20;border-radius:3px;height:14px">'
            f'<div style="width:{pct}%;background:linear-gradient(90deg,#6d28d9,#a78bfa);'
            f'height:100%;border-radius:3px"></div></div>'
            f'<span style="font-size:11px;color:#64748b;min-width:28px">{p["count"]}</span></div>'
            f'<div style="font-size:11px;color:#94a3b8;margin-left:26px;margin-top:2px;'
            f'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:240px">'
            f'{_e(p["title"])}</div></div>'
        )
    return "".join(items)


def _analytics_html(data, key):
    """Full analytics panel rendered as Python HTML — no JS charts needed."""
    users = data["users"]
    rev = data["reviews"]
    popular = data["popular"]
    pos = sum(1 for r in rev if r["sentiment"] == "positive")
    neg = sum(1 for r in rev if r["sentiment"] == "negative")
    neu = sum(1 for r in rev if r["sentiment"] == "neutral")
    n = len(users) or 1
    banned = sum(1 for u in users if u["is_banned"])
    active = sum(1 for u in users if u["rev_count"] + u["wl_count"] + u["fav_count"] > 0)
    n_wl  = len(data["watchlist"])   # extracted to avoid f-string double-quote conflict (Py<3.12)
    n_msg = len(data["messages"])    # same

    return f"""
<div class="ag">
  <div class="ac2"><div class="at">Platform Overview</div>
    <div class="sg">
      <div class="si2"><div class="n">{len(users)}</div><div class="l">Total Users</div></div>
      <div class="si2"><div class="n" style="color:#34d399">{active}</div><div class="l">Active</div></div>
      <div class="si2"><div class="n" style="color:#f87171">{banned}</div><div class="l">Banned</div></div>
      <div class="si2"><div class="n">{len(rev)}</div><div class="l">Reviews</div></div>
      <div class="si2"><div class="n">{n_wl}</div><div class="l">Watchlist</div></div>
      <div class="si2"><div class="n">{n_msg}</div><div class="l">Messages</div></div>
    </div>
  </div>
  <div class="ac2"><div class="at">Sentiment Distribution</div>
    {_sentiment_chart_html(pos, neg, neu)}
  </div>
</div>
<div class="ac2" style="margin-bottom:14px">
  <div class="at">Most Popular Movies (Top 10)</div>
  {_popular_chart_html(popular)}
</div>
<div class="ac2">
  <div class="at">Quick Exports</div>
  <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px">
    <a class="ebtn" href="/admin/export/users?key={_e(key)}">&#128229; Users CSV</a>
    <a class="ebtn" href="/admin/export/watchlist?key={_e(key)}">&#128229; Watchlist CSV</a>
    <a class="ebtn" href="/admin/export/favorites?key={_e(key)}">&#128229; Favorites CSV</a>
    <a class="ebtn" href="/admin/export/reviews?key={_e(key)}">&#128229; Reviews CSV</a>
    <a class="ebtn" href="/admin/export/messages?key={_e(key)}">&#128229; Messages CSV</a>
  </div>
</div>"""


def _insights_html(data):
    users = data["users"]
    rev = data["reviews"]
    top = sorted(users, key=lambda u: u["rev_count"] + u["wl_count"] + u["fav_count"],
                 reverse=True)[:5]
    n = len(users) or 1
    total_rev = len(rev) or 1
    pos = sum(1 for r in rev if r["sentiment"] == "positive")
    neg = sum(1 for r in rev if r["sentiment"] == "negative")
    neu = sum(1 for r in rev if r["sentiment"] == "neutral")
    wl_n = len(data["watchlist"])
    fav_n = len(data["favorites"])
    msg_n = len(data["messages"])

    tu_html = "\n".join(
        f'<div class="ins-row"><span class="ins-name">{i+1}. {_e(u["username"])}</span>'
        f'<span class="ins-val">{u["rev_count"]}R / {u["wl_count"]}W / {u["fav_count"]}F</span></div>'
        for i, u in enumerate(top)
    ) or '<div class="empty">No data</div>'

    pop_html = "\n".join(
        f'<div class="ins-row"><span class="ins-name">{i+1}. {_e(p["title"])}</span>'
        f'<span class="ins-val">{p["count"]} saves</span></div>'
        for i, p in enumerate(data["popular"][:10])
    ) or '<div class="empty">No data</div>'

    # Pre-compute averages for Python <3.12 f-string compatibility
    avg_rev    = len(rev) / n
    avg_wl     = wl_n / n
    avg_fav    = fav_n / n
    active_ct  = sum(1 for u in users if u["rev_count"] + u["wl_count"] + u["fav_count"] > 0)
    active_pct = round(active_ct / n * 100)

    return f"""
<div class="ag">
  <div class="ac2"><div class="at">&#127942; Top 5 Most Active Users</div>{tu_html}</div>
  <div class="ac2"><div class="at">&#127909; Top 10 Popular Movies</div>{pop_html}</div>
</div>
<div class="ac2" style="margin-bottom:14px">
  <div class="at">Sentiment Breakdown</div>
  <div style="display:flex;gap:12px;margin-top:10px;flex-wrap:wrap">
    <div class="si2" style="flex:1"><div class="n" style="color:#34d399">{round(pos/total_rev*100)}%</div><div class="l">Positive</div></div>
    <div class="si2" style="flex:1"><div class="n" style="color:#f87171">{round(neg/total_rev*100)}%</div><div class="l">Negative</div></div>
    <div class="si2" style="flex:1"><div class="n" style="color:#94a3b8">{round(neu/total_rev*100)}%</div><div class="l">Neutral</div></div>
  </div>
</div>
<div class="ac2">
  <div class="at">User Behavior Summary</div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px">
    <div class="si2"><div class="n" style="font-size:16px">{avg_rev:.1f}</div><div class="l">Avg Reviews/User</div></div>
    <div class="si2"><div class="n" style="font-size:16px">{avg_wl:.1f}</div><div class="l">Avg Watchlist/User</div></div>
    <div class="si2"><div class="n" style="font-size:16px">{avg_fav:.1f}</div><div class="l">Avg Favorites/User</div></div>
    <div class="si2"><div class="n" style="font-size:16px;color:#34d399">{active_pct}%</div><div class="l">Active Rate</div></div>
  </div>
</div>"""


# ─── Search Form Builder ──────────────────────────────────────────────────────

def _search_form(tab, q, key, extra_html="", count=0, total=0, export_table=None):
    """Render a search form that submits to /admin with GET params."""
    count_txt = f"{count} of {total}" if q and count != total else str(total)
    export_link = (f'<a class="ebtn" href="/admin/export/{export_table}?key={_e(key)}">&#128229; CSV</a>'
                   if export_table else "")
    return f"""
<form method="GET" action="/admin" class="toolbar" style="gap:8px">
  <input type="hidden" name="key" value="{_e(key)}">
  <input type="hidden" name="tab" value="{tab}">
  <div class="sw"><span class="si">&#128269;</span>
    <input class="sbox" name="q" value="{_e(q)}" placeholder="Search..." autofocus/></div>
  {extra_html}
  <button type="submit" class="ebtn" style="padding:7px 14px">&#128269; Search</button>
  <a class="ebtn" style="background:rgba(100,116,139,.12);border-color:rgba(100,116,139,.25);
     color:#94a3b8;text-decoration:none;padding:6px 12px" 
     href="/admin?key={_e(key)}&tab={tab}">&#10006; Clear</a>
  <span class="rc">{count_txt} records</span>
  {export_link}
</form>"""


# ─── Main Entry Point ─────────────────────────────────────────────────────────

def get_dashboard(key: str, tab: str = "analytics",
                  q: str = "", status: str = "", sort: str = "newest",
                  sent: str = "", rd: str = "") -> str:

    raw = _get_data()
    data = _apply_filters(dict(raw), tab, q, status, sort, sent, rd)

    # Stats from UNFILTERED data for header cards
    all_users = raw["users"]
    s_users   = len(all_users)
    s_wl      = len(raw["watchlist"])
    s_fav     = len(raw["favorites"])
    s_rev     = len(raw["reviews"])
    s_msg     = len(raw["messages"])
    s_unread  = sum(1 for m in raw["messages"] if not m["is_read"])

    # Active tab — determines which radio is checked
    tabs = ["analytics", "users", "watchlist", "favorites", "reviews", "messages", "insights"]
    if tab not in tabs:
        tab = "analytics"

    unread_badge = f'<span class="badge">{s_unread}</span>' if s_unread else ""
    unread_color = "#e50914" if s_unread else "#64748b"

    # Build user cards (for D object in JS — only for modal)
    data_json = json.dumps({"users": raw["users"], "watchlist": raw["watchlist"],
                             "favorites": raw["favorites"], "reviews": raw["reviews"],
                             "messages": raw["messages"]},
                           ensure_ascii=True, separators=(",", ":"))
    data_json = data_json.replace("</", "<\\/")

    # Users panel search form extras
    status_opts = "".join(
        f'<option value="{v}"{" selected" if status==v else ""}>{l}</option>'
        for v, l in [("", "All Users"), ("active", "Active"),
                     ("inactive", "Inactive"), ("banned", "Banned")])
    sort_opts = "".join(
        f'<option value="{v}"{" selected" if sort==v else ""}>{l}</option>'
        for v, l in [("newest", "Latest First"), ("oldest", "Oldest First"),
                     ("reviews", "Most Reviews"), ("watchlist", "Most Watchlist")])
    users_extra = (f'<select class="fsel" name="status">{status_opts}</select>'
                   f'<select class="fsel" name="sort">{sort_opts}</select>')

    # Reviews panel search extras
    sent_opts = "".join(
        f'<option value="{v}"{" selected" if sent==v else ""}>{l}</option>'
        for v, l in [("", "All Sentiments"), ("positive", "Positive"),
                     ("negative", "Negative"), ("neutral", "Neutral")])
    reviews_extra = f'<select class="fsel" name="sent">{sent_opts}</select>'

    # Messages panel search extras
    rd_opts = "".join(
        f'<option value="{v}"{" selected" if rd==v else ""}>{l}</option>'
        for v, l in [("", "All Messages"), ("unread", "Unread Only"), ("read", "Read Only")])
    msgs_extra = f'<select class="fsel" name="rd">{rd_opts}</select>'

    # Panel HTML
    analytics_panel = _analytics_html(raw, key)   # always use full unfiltered data
    users_panel     = _users_html(data["users"], key)
    wl_panel        = _wl_html(data["watchlist"], "watchlist")
    fav_panel       = _wl_html(data["favorites"], "favorites")
    rev_panel       = _reviews_html(data["reviews"])
    msg_panel       = _messages_html(data["messages"], key)
    insights_panel  = _insights_html(raw)

    # Search forms with correct counts
    users_form   = _search_form("users", q, key, users_extra,
                                len(data["users"]), len(raw["users"]), "users")
    wl_form      = _search_form("watchlist", q, key, "",
                                len(data["watchlist"]), len(raw["watchlist"]), "watchlist")
    fav_form     = _search_form("favorites", q, key, "",
                                len(data["favorites"]), len(raw["favorites"]), "favorites")
    rev_form     = _search_form("reviews", q, key, reviews_extra,
                                len(data["reviews"]), len(raw["reviews"]), "reviews")
    msg_form     = _search_form("messages", q, key, msgs_extra,
                                len(data["messages"]), len(raw["messages"]), "messages")

    # Radio checked states
    def chk(t): return ' checked' if tab == t else ''

    return _render(
        key=key, tab=tab,
        data_json=data_json,
        s_users=s_users, s_wl=s_wl, s_fav=s_fav,
        s_rev=s_rev, s_msg=s_msg, s_unread=s_unread,
        unread_badge=unread_badge,
        unread_color=unread_color,
        chk=chk,
        analytics_panel=analytics_panel,
        users_panel=users_panel, users_form=users_form,
        wl_panel=wl_panel, wl_form=wl_form,
        fav_panel=fav_panel, fav_form=fav_form,
        rev_panel=rev_panel, rev_form=rev_form,
        msg_panel=msg_panel, msg_form=msg_form,
        insights_panel=insights_panel,
    )


def _render(**ctx):
    """Build complete HTML page."""
    c = ctx
    return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CineAI Admin Dashboard</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Segoe UI',system-ui,sans-serif;background:#080812;color:#e2e8f0;min-height:100vh}}
header{{background:linear-gradient(120deg,#3b1f8c,#6d28d9);padding:14px 22px;display:flex;align-items:center;justify-content:space-between;box-shadow:0 4px 24px rgba(0,0,0,.5);position:sticky;top:0;z-index:100}}
.ht{{font-size:18px;font-weight:800}}.hs{{font-size:11px;opacity:.7;margin-top:2px}}
.hbtns{{display:flex;gap:8px;align-items:center}}
.hbtn{{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.2);color:#fff;border-radius:8px;padding:6px 12px;font-size:12px;font-weight:600;cursor:pointer;text-decoration:none}}
.hbtn:hover{{background:rgba(255,255,255,.2)}}
.live{{display:flex;align-items:center;gap:6px;font-size:11px;color:#34d399}}
.livdot{{width:8px;height:8px;background:#34d399;border-radius:50%;animation:pulse 2s infinite}}
@keyframes pulse{{0%,100%{{opacity:1;transform:scale(1)}}50%{{opacity:.6;transform:scale(1.3)}}}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(110px,1fr));gap:10px;padding:12px 22px}}
.card{{background:#0f0f22;border:1px solid #1a1a35;border-radius:12px;padding:14px;text-align:center;cursor:pointer;transition:.2s;text-decoration:none;display:block}}
.card:hover,.card.active{{border-color:#7c3aed;background:#18183a;transform:translateY(-2px)}}
.card .n{{font-size:26px;font-weight:800;color:#a78bfa}}
.card .l{{font-size:10px;color:#64748b;margin-top:3px;text-transform:uppercase;letter-spacing:.4px}}
.card .s{{font-size:10px;margin-top:2px}}
.tabs{{display:flex;padding:0 22px;border-bottom:1px solid #1a1a35;overflow-x:auto;gap:2px}}
.tab{{padding:10px 14px;font-size:13px;font-weight:500;color:#64748b;border-bottom:2px solid transparent;cursor:pointer;transition:.15s;white-space:nowrap;text-decoration:none}}
.tab:hover{{color:#c4b5fd}}.tab.active{{color:#c4b5fd;border-bottom-color:#7c3aed}}
/* ── Active highlighting via CSS :checked (no JS needed) ── */
#rt-analytics:checked~.cards label[for=rt-analytics],
#rt-users:checked~.cards label[for=rt-users],
#rt-watchlist:checked~.cards label[for=rt-watchlist],
#rt-favorites:checked~.cards label[for=rt-favorites],
#rt-reviews:checked~.cards label[for=rt-reviews],
#rt-messages:checked~.cards label[for=rt-messages],
#rt-insights:checked~.cards label[for=rt-insights]{{border-color:#7c3aed!important;background:linear-gradient(135deg,#18183a,#1a1040)!important;transform:translateY(-2px);box-shadow:0 0 0 1px rgba(124,58,237,.35),0 4px 16px rgba(124,58,237,.2)!important}}
#rt-analytics:checked~.cards label[for=rt-analytics] .n,
#rt-users:checked~.cards label[for=rt-users] .n,
#rt-watchlist:checked~.cards label[for=rt-watchlist] .n,
#rt-favorites:checked~.cards label[for=rt-favorites] .n,
#rt-reviews:checked~.cards label[for=rt-reviews] .n,
#rt-messages:checked~.cards label[for=rt-messages] .n,
#rt-insights:checked~.cards label[for=rt-insights] .n{{color:#c4b5fd}}
#rt-analytics:checked~.tabs label[for=rt-analytics],
#rt-users:checked~.tabs label[for=rt-users],
#rt-watchlist:checked~.tabs label[for=rt-watchlist],
#rt-favorites:checked~.tabs label[for=rt-favorites],
#rt-reviews:checked~.tabs label[for=rt-reviews],
#rt-messages:checked~.tabs label[for=rt-messages],
#rt-insights:checked~.tabs label[for=rt-insights]{{color:#c4b5fd!important;border-bottom:2px solid #7c3aed!important;font-weight:700!important}}

.badge{{background:#e50914;color:#fff;border-radius:10px;padding:1px 6px;font-size:10px;font-weight:800;margin-left:4px}}
.panel{{display:none;padding:14px 22px 40px}}
.toolbar{{display:flex;align-items:center;gap:8px;margin-bottom:12px;flex-wrap:wrap}}
.sw{{position:relative;flex:1;min-width:180px;max-width:320px}}
.si{{position:absolute;left:10px;top:50%;transform:translateY(-50%);font-size:12px;pointer-events:none;color:#64748b}}
.sbox{{width:100%;padding:8px 10px 8px 30px;background:#0f0f22;border:1px solid #1a1a35;border-radius:8px;color:#e2e8f0;font-size:13px;outline:none;transition:.2s}}
.sbox:focus{{border-color:#7c3aed;box-shadow:0 0 0 3px rgba(124,58,237,.15)}}
.fsel{{padding:7px 10px;background:#0f0f22;border:1px solid #1a1a35;border-radius:8px;color:#e2e8f0;font-size:12px;cursor:pointer;outline:none}}
.rc{{font-size:12px;color:#64748b;margin-left:auto;white-space:nowrap}}
.ebtn{{background:rgba(16,185,129,.12);border:1px solid rgba(16,185,129,.25);color:#34d399;border-radius:8px;padding:6px 12px;font-size:12px;font-weight:600;cursor:pointer;text-decoration:none;display:inline-block}}
.ebtn:hover{{background:rgba(16,185,129,.22)}}
.tw{{overflow-x:auto;border-radius:10px;border:1px solid #1a1a35;max-height:62vh;overflow-y:auto}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
thead th{{padding:9px 12px;text-align:left;color:#7c3aed;font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:.5px;white-space:nowrap;background:#080818;position:sticky;top:0;z-index:2}}
td{{padding:8px 12px;border-top:1px solid #0d0d20;color:#cbd5e1;max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
tr.dr:hover td{{background:#0f0f28}}
tr.banned td{{opacity:.55;background:rgba(239,68,68,.03)}}
tr.unread td{{background:rgba(99,102,241,.04)}}
.empty{{text-align:center;color:#334155;padding:32px;font-size:14px}}
.sb{{border-radius:20px;padding:2px 9px;font-size:11px;font-weight:700;text-transform:uppercase;white-space:nowrap}}
.sb.positive{{background:rgba(16,185,129,.12);color:#34d399}}
.sb.negative{{background:rgba(239,68,68,.12);color:#f87171}}
.sb.neutral{{background:rgba(148,163,184,.1);color:#94a3b8}}
.sb.banned{{background:rgba(239,68,68,.1);color:#f87171}}
.sb.active{{background:rgba(16,185,129,.1);color:#34d399}}
.ba{{border:none;border-radius:6px;padding:3px 8px;font-size:11px;font-weight:700;cursor:pointer;transition:.15s;margin-right:2px}}
.ban-btn{{background:rgba(251,191,36,.1);color:#fbbf24}}.ban-btn:hover{{background:rgba(251,191,36,.22)}}
.unb-btn{{background:rgba(16,185,129,.1);color:#34d399}}.unb-btn:hover{{background:rgba(16,185,129,.22)}}
.del-btn{{background:rgba(239,68,68,.1);color:#f87171}}.del-btn:hover{{background:rgba(239,68,68,.22)}}
.rd-btn{{background:rgba(99,102,241,.12);color:#818cf8}}.rd-btn:hover{{background:rgba(99,102,241,.25)}}
.ulink{{color:#a78bfa;cursor:pointer;font-weight:700;text-decoration:underline;text-underline-offset:3px}}
.ulink:hover{{color:#c4b5fd}}
.pthumb{{width:28px;height:40px;border-radius:3px;object-fit:cover;margin-right:6px;vertical-align:middle;border:1px solid #1a1a35}}
.ag{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:14px}}
.ac2{{background:#0f0f22;border:1px solid #1a1a35;border-radius:12px;padding:18px}}
.at{{font-size:11px;font-weight:700;color:#64748b;margin-bottom:14px;text-transform:uppercase;letter-spacing:.5px}}
.sg{{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}}
.si2{{background:#080818;border-radius:8px;padding:12px;text-align:center}}
.si2 .n{{font-size:20px;font-weight:800;color:#a78bfa}}.si2 .l{{font-size:10px;color:#64748b;margin-top:3px;text-transform:uppercase}}
.ins-row{{display:flex;align-items:center;justify-content:space-between;padding:8px 0;border-bottom:1px solid #0d0d20;font-size:13px}}
.ins-row:last-child{{border:none}}
.ins-name{{color:#e2e8f0;font-weight:600}}.ins-val{{color:#a78bfa;font-weight:700;font-size:12px}}
.mo{{position:fixed;inset:0;background:rgba(0,0,0,.85);backdrop-filter:blur(6px);z-index:1000;display:none;align-items:flex-start;justify-content:center;padding:40px 16px;overflow-y:auto}}
.mo.open{{display:flex}}
.mbox{{background:#0f0f22;border:1px solid #1e1e3f;border-radius:16px;padding:26px;width:min(720px,100%);position:relative;margin:auto}}
.mcl{{position:absolute;top:12px;right:12px;background:rgba(255,255,255,.08);border:none;color:#94a3b8;width:28px;height:28px;border-radius:50%;font-size:14px;cursor:pointer}}
.mcl:hover{{background:rgba(239,68,68,.2);color:#f87171}}
.mun{{font-size:20px;font-weight:800;margin-bottom:4px}}
.mem{{color:#64748b;font-size:13px;margin-bottom:14px}}
.mgr{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:14px}}
.ms{{background:#080818;border-radius:8px;padding:10px;text-align:center}}
.ms .n{{font-size:18px;font-weight:800;color:#a78bfa}}.ms .l{{font-size:10px;color:#64748b;margin-top:2px;text-transform:uppercase}}
.mst{{font-size:11px;font-weight:700;color:#7c3aed;text-transform:uppercase;letter-spacing:.5px;margin:12px 0 6px}}
.mph{{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:10px}}
.mpl{{background:#080818;border:1px solid #1a1a35;border-radius:20px;padding:3px 9px;font-size:11px;color:#cbd5e1}}
.mra{{display:flex;gap:8px;margin-top:14px;padding-top:12px;border-top:1px solid #1a1a35;flex-wrap:wrap}}
.toast{{position:fixed;bottom:20px;right:20px;padding:11px 16px;border-radius:9px;font-size:13px;font-weight:600;z-index:3000;pointer-events:none;opacity:0;transition:opacity .25s;max-width:280px}}
.toast.show{{opacity:1}}
.tok{{background:#065f46;color:#34d399;border:1px solid rgba(52,211,153,.3)}}
.ter{{background:#7f1d1d;color:#f87171;border:1px solid rgba(248,113,113,.3)}}
footer{{text-align:center;padding:14px;color:#1e293b;font-size:12px;border-top:1px solid #0a0a20;margin-top:8px}}
/* CSS radio-button tab switching */
.rt{{position:absolute;opacity:0;pointer-events:none;width:0;height:0}}
#rt-analytics:checked~#panel-analytics,
#rt-users:checked~#panel-users,
#rt-watchlist:checked~#panel-watchlist,
#rt-favorites:checked~#panel-favorites,
#rt-reviews:checked~#panel-reviews,
#rt-messages:checked~#panel-messages,
#rt-insights:checked~#panel-insights{{display:block!important}}
label.card{{cursor:pointer}}label.tab{{cursor:pointer}}
@media(max-width:640px){{.ag{{grid-template-columns:1fr}}.mgr{{grid-template-columns:repeat(2,1fr)}}}}
</style></head><body>

<input type="radio" name="dt" id="rt-analytics" class="rt"{c['chk']('analytics')}>
<input type="radio" name="dt" id="rt-users" class="rt"{c['chk']('users')}>
<input type="radio" name="dt" id="rt-watchlist" class="rt"{c['chk']('watchlist')}>
<input type="radio" name="dt" id="rt-favorites" class="rt"{c['chk']('favorites')}>
<input type="radio" name="dt" id="rt-reviews" class="rt"{c['chk']('reviews')}>
<input type="radio" name="dt" id="rt-messages" class="rt"{c['chk']('messages')}>
<input type="radio" name="dt" id="rt-insights" class="rt"{c['chk']('insights')}>

<header>
  <div><div class="ht">&#128274; CineAI Admin Dashboard</div>
  <div class="hs">Live PostgreSQL &mdash; Server-Side Rendered</div></div>
  <div class="hbtns">
    <div class="live"><div class="livdot"></div> Live</div>
    <a class="hbtn" href="/admin?key={_e(c['key'])}">&#128260; Refresh</a>
    <span class="hbtn">&#128274; Admin</span>
  </div>
</header>

<!-- Stat Cards -->
<div class="cards">
  <label class="card{' active' if c['tab']=='analytics' else ''}" for="rt-analytics">
    <div class="n">&#128202;</div><div class="l">Analytics</div></label>
  <label class="card{' active' if c['tab']=='users' else ''}" for="rt-users">
    <div class="n">{c['s_users']}</div><div class="l">Users</div></label>
  <label class="card{' active' if c['tab']=='watchlist' else ''}" for="rt-watchlist">
    <div class="n">{c['s_wl']}</div><div class="l">Watchlist</div></label>
  <label class="card{' active' if c['tab']=='favorites' else ''}" for="rt-favorites">
    <div class="n">{c['s_fav']}</div><div class="l">Favorites</div></label>
  <label class="card{' active' if c['tab']=='reviews' else ''}" for="rt-reviews">
    <div class="n">{c['s_rev']}</div><div class="l">Reviews</div></label>
  <label class="card{' active' if c['tab']=='messages' else ''}" for="rt-messages">
    <div class="n">{c['s_msg']}</div>
    <div class="l">Messages</div>
    <div class="s" style="color:{c['unread_color']}">{c['s_unread']} unread</div></label>
  <label class="card{' active' if c['tab']=='insights' else ''}" for="rt-insights">
    <div class="n">&#128200;</div><div class="l">Insights</div></label>
</div>

<!-- Tabs -->
<div class="tabs">
  <label class="tab{' active' if c['tab']=='analytics' else ''}" for="rt-analytics">&#128202; Analytics</label>
  <label class="tab{' active' if c['tab']=='users' else ''}" for="rt-users">&#128100; Users ({c['s_users']})</label>
  <label class="tab{' active' if c['tab']=='watchlist' else ''}" for="rt-watchlist">&#128203; Watchlist</label>
  <label class="tab{' active' if c['tab']=='favorites' else ''}" for="rt-favorites">&#10084; Favorites</label>
  <label class="tab{' active' if c['tab']=='reviews' else ''}" for="rt-reviews">&#128172; Reviews ({c['s_rev']})</label>
  <label class="tab{' active' if c['tab']=='messages' else ''}" for="rt-messages">&#128233; Messages{c['unread_badge']}</label>
  <label class="tab{' active' if c['tab']=='insights' else ''}" for="rt-insights">&#128200; Insights</label>
</div>

<!-- ANALYTICS -->
<div class="panel" id="panel-analytics">
  {c['analytics_panel']}
</div>

<!-- USERS -->
<div class="panel" id="panel-users">
  {c['users_form']}
  <div class="tw"><table id="tbl-users">
    <thead><tr><th>ID</th><th>Username</th><th>Email</th><th>Password Hash</th><th>Age</th><th>Gender</th>
      <th>Genres</th><th>Reviews</th><th>Watchlist</th><th>Registered</th><th>Last Login</th>
      <th>Status</th><th>Actions</th></tr></thead>
    <tbody>{c['users_panel']}</tbody>
  </table></div>
</div>

<!-- WATCHLIST -->
<div class="panel" id="panel-watchlist">
  {c['wl_form']}
  <div class="tw"><table>
    <thead><tr><th>ID</th><th>User ID</th><th>Movie ID</th><th>Movie Title</th><th>Added At</th></tr></thead>
    <tbody>{c['wl_panel']}</tbody>
  </table></div>
</div>

<!-- FAVORITES -->
<div class="panel" id="panel-favorites">
  {c['fav_form']}
  <div class="tw"><table>
    <thead><tr><th>ID</th><th>User ID</th><th>Movie ID</th><th>Movie Title</th><th>Added At</th></tr></thead>
    <tbody>{c['fav_panel']}</tbody>
  </table></div>
</div>

<!-- REVIEWS -->
<div class="panel" id="panel-reviews">
  {c['rev_form']}
  <div class="tw"><table>
    <thead><tr><th>ID</th><th>User ID</th><th>Movie</th><th>Review</th><th>Sentiment</th><th>Date</th></tr></thead>
    <tbody>{c['rev_panel']}</tbody>
  </table></div>
</div>

<!-- MESSAGES -->
<div class="panel" id="panel-messages">
  {c['msg_form']}
  <div class="tw"><table>
    <thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Subject</th><th>Message</th>
      <th>Sent At</th><th>Status</th><th>Actions</th></tr></thead>
    <tbody>{c['msg_panel']}</tbody>
  </table></div>
</div>

<!-- INSIGHTS -->
<div class="panel" id="panel-insights">
  {c['insights_panel']}
</div>

<!-- User Detail Modal -->
<div class="mo" id="userModal" onclick="if(event.target===this)closeModal()">
  <div class="mbox"><button type="button" class="mcl" onclick="closeModal()">&#10005;</button>
  <div id="modal-content"></div></div>
</div>
<div class="toast" id="toast"></div>
<footer>CineAI Admin Dashboard &bull; PostgreSQL &bull; &#128274; Admin Only</footer>

<script>
var D = {c['data_json']};
var KEY = "{_e(c['key'])}";

function q(id){{return document.getElementById(id);}}
function esc(v){{return String(v==null?"":v).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");}}

function toast(msg,cls){{
  var t=q("toast");
  t.textContent=msg;
  t.className="toast "+cls;
  t.classList.add("show");
  setTimeout(function(){{t.classList.remove("show");}},3000);
}}

// Admin actions (ban/delete/read) — AJAX, no page reload needed for search
function doAction(method,url,needConfirm){{
  if(needConfirm&&!confirm("Are you sure? This cannot be undone.")) return;
  var btn=event.currentTarget||event.target;
  if(btn){{btn.disabled=true;btn.textContent="...";}}
  fetch(url+"?key="+encodeURIComponent(KEY),{{method:method}})
    .then(function(r){{
      return r.json().then(function(d){{
        if(!r.ok) throw new Error(d.detail||("Error "+r.status));
        return d;
      }});
    }})
    .then(function(){{
      toast("Done! Action completed — reloading...","tok");
      setTimeout(function(){{
        var ct="analytics";
        var rs=document.querySelectorAll("input.rt");
        for(var i=0;i<rs.length;i++){{if(rs[i].checked){{ct=rs[i].id.replace("rt-","");break;}}}}
        window.location.href="/admin?key="+encodeURIComponent(KEY)+"&tab="+ct;
      }},1200);
    }})
    .catch(function(e){{
      toast("Error: "+e.message,"ter");
      if(btn){{btn.disabled=false;btn.textContent=btn.getAttribute("data-orig")||"Action";}}
    }});
}}

// User detail modal
function showUser(uid){{
  var u=D.users.find(function(x){{return x.id===uid;}});
  if(!u) return;
  var revs=D.reviews.filter(function(r){{return r.user_id===uid;}});
  var wl=D.watchlist.filter(function(w){{return w.user_id===uid;}});
  var fav=D.favorites.filter(function(f){{return f.user_id===uid;}});
  var pos=revs.filter(function(r){{return r.sentiment==="positive";}}).length;
  var neg=revs.filter(function(r){{return r.sentiment==="negative";}}).length;
  var mood=pos>neg?"Positive":neg>pos?"Negative":"Neutral";
  var mc=pos>neg?"#34d399":neg>pos?"#f87171":"#94a3b8";
  var h="<div class='mun'>"+esc(u.username)+(u.is_banned?" <span class='sb banned'>Banned</span>":"")+"</div>"
    +"<div class='mem'>"+esc(u.email)+" &bull; "+(u.age||"?")+" yrs &bull; "+esc(u.gender||"Unknown")+"</div>"
    +"<div style='font-size:12px;color:#64748b;margin-bottom:12px'>Joined: "+u.created_at+" &bull; Last login: "+u.last_login+"</div>"
    +(u.favorite_genres?"<div style='font-size:12px;color:#a78bfa;margin-bottom:12px'>Genres: "+esc(u.favorite_genres)+"</div>":"")
    +"<div class='mgr'>"
    +"<div class='ms'><div class='n'>"+revs.length+"</div><div class='l'>Reviews</div></div>"
    +"<div class='ms'><div class='n'>"+wl.length+"</div><div class='l'>Watchlist</div></div>"
    +"<div class='ms'><div class='n'>"+fav.length+"</div><div class='l'>Favorites</div></div>"
    +"<div class='ms'><div class='n' style='color:"+mc+"'>"+mood+"</div><div class='l'>Mood</div></div>"
    +"</div>"
    +(wl.length?"<div class='mst'>Watchlist</div><div class='mph'>"+wl.slice(0,10).map(function(w){{return "<span class='mpl'>"+esc(w.movie_title)+"</span>";}}).join("")+"</div>":"")
    +(fav.length?"<div class='mst'>Favorites</div><div class='mph'>"+fav.slice(0,10).map(function(f){{return "<span class='mpl'>"+esc(f.movie_title)+"</span>";}}).join("")+"</div>":"")
    +(revs.length?"<div class='mst'>Recent Reviews</div>"+revs.slice(0,5).map(function(r){{
      return "<div style='background:#080818;border-radius:7px;padding:8px;margin-bottom:5px'>"
        +"<span class='sb "+r.sentiment+"'>"+r.sentiment+"</span>"
        +" <span style='font-size:11px;color:#64748b;margin-left:5px'>"+esc(r.movie_title)+" &bull; "+r.created_at+"</span>"
        +"<div style='font-size:12px;color:#94a3b8;margin-top:3px'>"+esc(r.review_text.slice(0,100))+"</div></div>";
    }}).join(""):"")
    +"<div class='mra'>"
    +(u.is_banned
      ?"<button type='button' class='ba unb-btn' style='padding:6px 14px;font-size:13px' onclick='doAction(\"POST\",\"/admin/users/"+u.id+"/unban\")'>&#9989; Unban</button>"
      :"<button type='button' class='ba ban-btn' style='padding:6px 14px;font-size:13px' onclick='doAction(\"POST\",\"/admin/users/"+u.id+"/ban\")'>&#128683; Ban</button>")
    +"<button type='button' class='ba del-btn' style='padding:6px 14px;font-size:13px' onclick='doAction(\"DELETE\",\"/admin/users/"+u.id+"\",true)'>&#128465; Delete</button>"
    +"</div>";
  q("modal-content").innerHTML=h;
  q("userModal").classList.add("open");
}}
function closeModal(){{q("userModal").classList.remove("open");}}
</script></body></html>"""


# ─── Static page ──────────────────────────────────────────────────────────────

LOGIN_HTML = """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>CineAI Admin</title>
<style>*{box-sizing:border-box;margin:0;padding:0}body{font-family:'Segoe UI',sans-serif;background:#080812;color:#e2e8f0;display:flex;align-items:center;justify-content:center;min-height:100vh}.card{background:#0f0f22;border:1px solid #252545;border-radius:18px;padding:52px 44px;text-align:center;width:400px;box-shadow:0 24px 64px rgba(0,0,0,.7)}h1{font-size:26px;font-weight:800;margin-bottom:8px}p{color:#64748b;font-size:13px;margin-bottom:32px}input{width:100%;padding:14px 16px;background:#080812;border:1px solid #2d2d5e;border-radius:10px;color:#e2e8f0;font-size:15px;margin-bottom:16px;outline:none;letter-spacing:2px}input:focus{border-color:#7c3aed}button{width:100%;padding:14px;background:linear-gradient(135deg,#6c3ef4,#e040fb);color:#fff;border:none;border-radius:10px;font-size:15px;font-weight:700;cursor:pointer}</style></head><body>
<div class="card"><div style="font-size:52px;margin-bottom:16px">&#128274;</div>
<h1>CineAI Admin Panel</h1><p>Live PostgreSQL database viewer &mdash; admin only</p>
<form method="GET" action="/admin">
<input type="password" name="key" placeholder="Enter admin key..." autofocus/>
<button type="submit">&#128275; Open Dashboard</button>
</form></div></body></html>"""

WRONG_HTML = """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>CineAI Admin</title>
<style>*{box-sizing:border-box;margin:0;padding:0}body{font-family:'Segoe UI',sans-serif;background:#080812;color:#e2e8f0;display:flex;align-items:center;justify-content:center;min-height:100vh}.card{background:#0f0f22;border:1px solid #252545;border-radius:18px;padding:52px 44px;text-align:center;width:400px}h1{font-size:22px;font-weight:800;margin-bottom:8px;color:#f87171}p{color:#64748b;font-size:13px;margin-bottom:28px}input{width:100%;padding:14px;background:#080812;border:1px solid #7c3aed;border-radius:10px;color:#e2e8f0;font-size:15px;margin-bottom:16px;outline:none;letter-spacing:2px}button{width:100%;padding:14px;background:linear-gradient(135deg,#6c3ef4,#e040fb);color:#fff;border:none;border-radius:10px;font-size:15px;font-weight:700;cursor:pointer}</style></head><body>
<div class="card"><div style="font-size:48px;margin-bottom:16px">&#10060;</div>
<h1>Wrong Key</h1><p>Please try the correct admin key</p>
<form method="GET" action="/admin">
<input type="password" name="key" placeholder="Enter admin key..." autofocus/>
<button type="submit">&#128275; Try Again</button>
</form></div></body></html>"""
