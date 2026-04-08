"""
download_live_data.py
---------------------
Downloads all live data from the deployed CineAI backend (PostgreSQL on Render)
and merges it into your local cineai.db so DB Browser for SQLite shows everything.

Usage:
    python download_live_data.py
"""

import requests
import sqlite3

# ── Config ────────────────────────────────────────────────────────────────────
LIVE_API  = "https://cineai-ifyr.onrender.com"
ADMIN_KEY = "cineai-admin-2024"
LOCAL_DB  = "cineai.db"
# ─────────────────────────────────────────────────────────────────────────────

print("🔄 Fetching live data from Render...")
try:
    resp = requests.get(
        f"{LIVE_API}/auth/admin/export",
        params={"key": ADMIN_KEY},
        timeout=60
    )
    resp.raise_for_status()
    data = resp.json()
except Exception as e:
    print(f"❌ Failed to fetch: {e}")
    exit(1)

live_users     = data.get("users", [])
live_watchlist = data.get("watchlist", [])
live_reviews   = data.get("reviews", [])

print(f"✅ Fetched {len(live_users)} users, {len(live_watchlist)} watchlist, {len(live_reviews)} reviews from Render")

# ── Get next available local ID ───────────────────────────────────────────────
conn   = sqlite3.connect(LOCAL_DB)
cursor = conn.cursor()

cursor.execute("SELECT MAX(id) FROM users")
max_local_id = cursor.fetchone()[0] or 0

# ── Check which live emails already exist locally ─────────────────────────────
cursor.execute("SELECT email FROM users")
local_emails = {row[0].lower() for row in cursor.fetchall()}

cursor.execute("SELECT movie_id, user_id FROM watchlist")
local_watch_pairs = {(row[0], row[1]) for row in cursor.fetchall()}

cursor.execute("SELECT movie_id, user_id FROM reviews") if cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name='reviews'"
).fetchone() else None
try:
    cursor.execute("SELECT movie_id, user_id FROM reviews")
    local_review_pairs = {(row[0], row[1]) for row in cursor.fetchall()}
except:
    local_review_pairs = set()

# ── Map live user IDs to local IDs ───────────────────────────────────────────
live_to_local_id = {}  # live_user_id → local_user_id

added_users    = 0
skipped_users  = 0
next_id        = max_local_id + 1

for u in live_users:
    email = u["email"].lower()
    if email in local_emails:
        # User already exists locally — find their local ID
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        if row:
            live_to_local_id[u["id"]] = row[0]
        skipped_users += 1
    else:
        # New user from live — insert with a new non-conflicting ID
        cursor.execute(
            "INSERT INTO users (id, username, email, hashed_password, age, gender, favorite_genres) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (next_id, u["username"], email, "[live-import]",
             u.get("age"), u.get("gender", ""), u.get("favorite_genres", ""))
        )
        live_to_local_id[u["id"]] = next_id
        local_emails.add(email)
        next_id += 1
        added_users += 1

# ── Merge watchlist ───────────────────────────────────────────────────────────
added_watch = 0
for w in live_watchlist:
    local_uid = live_to_local_id.get(w["user_id"])
    if local_uid is None:
        continue
    pair = (w["movie_id"], local_uid)
    if pair not in local_watch_pairs:
        try:
            cursor.execute(
                "INSERT INTO watchlist (user_id, movie_id, movie_title) VALUES (?, ?, ?)",
                (local_uid, w["movie_id"], w.get("movie_title", "Unknown"))
            )
            local_watch_pairs.add(pair)
            added_watch += 1
        except Exception as e:
            pass

# ── Merge reviews ─────────────────────────────────────────────────────────────
added_reviews = 0
for r in live_reviews:
    local_uid = live_to_local_id.get(r["user_id"])
    if local_uid is None:
        continue
    pair = (r["movie_id"], local_uid)
    if pair not in local_review_pairs:
        try:
            cursor.execute(
                "INSERT INTO reviews (user_id, movie_id, movie_title, review_text, sentiment) "
                "VALUES (?, ?, ?, ?, ?)",
                (local_uid, r["movie_id"], r.get("movie_title", ""), r["review_text"], r["sentiment"])
            )
            local_review_pairs.add(pair)
            added_reviews += 1
        except Exception as e:
            pass

conn.commit()
conn.close()

print(f"\n✅ Merge complete!")
print(f"   👤 New users added     : {added_users}  (skipped {skipped_users} already existing)")
print(f"   📋 New watchlist added : {added_watch}")
print(f"   💬 New reviews added   : {added_reviews}")
print(f"\n📂 Now open/refresh cineai.db in DB Browser for SQLite!")
print(f"   File: cineai.db in CineAI\\backend\\")
