"""
download_live_data.py
---------------------
Downloads all live data from the deployed CineAI backend
and merges it into your local cineai.db so DB Browser shows everything.

Usage:
    python download_live_data.py
"""

import requests
import sqlite3
import json

# ── Config ────────────────────────────────────────────────────────────────────
LIVE_API   = "https://cineai-ifyr.onrender.com"
ADMIN_KEY  = "cineai-admin-2024"
LOCAL_DB   = "cineai.db"
# ─────────────────────────────────────────────────────────────────────────────

print("🔄 Fetching live data from Render...")
try:
    resp = requests.get(f"{LIVE_API}/auth/admin/export", params={"key": ADMIN_KEY}, timeout=60)
    resp.raise_for_status()
    data = resp.json()
except Exception as e:
    print(f"❌ Failed to fetch: {e}")
    exit(1)

users     = data.get("users", [])
watchlist = data.get("watchlist", [])
reviews   = data.get("reviews", [])

print(f"✅ Fetched {len(users)} users, {len(watchlist)} watchlist, {len(reviews)} reviews")

# ── Merge into local DB ───────────────────────────────────────────────────────
conn   = sqlite3.connect(LOCAL_DB)
cursor = conn.cursor()

added_users = 0
for u in users:
    cursor.execute("SELECT id FROM users WHERE id = ?", (u["id"],))
    if cursor.fetchone() is None:
        cursor.execute(
            "INSERT INTO users (id, username, email, hashed_password, age, gender, favorite_genres) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (u["id"], u["username"], u["email"], "[from-live]",
             u.get("age"), u.get("gender",""), u.get("favorite_genres",""))
        )
        added_users += 1

added_watch = 0
for w in watchlist:
    cursor.execute("SELECT id FROM watchlist WHERE id = ?", (w["id"],))
    if cursor.fetchone() is None:
        cursor.execute(
            "INSERT INTO watchlist (id, user_id, movie_id) VALUES (?, ?, ?)",
            (w["id"], w["user_id"], w["movie_id"])
        )
        added_watch += 1

added_reviews = 0
for r in reviews:
    cursor.execute("SELECT id FROM reviews WHERE id = ?", (r["id"],))
    if cursor.fetchone() is None:
        try:
            cursor.execute(
                "INSERT INTO reviews (id, user_id, movie_id, review_text, sentiment) "
                "VALUES (?, ?, ?, ?, ?)",
                (r["id"], r["user_id"], r["movie_id"], r["review_text"], r["sentiment"])
            )
            added_reviews += 1
        except Exception:
            pass

conn.commit()
conn.close()

print(f"\n✅ Merge complete!")
print(f"   👤 New users added     : {added_users}")
print(f"   📋 New watchlist added : {added_watch}")
print(f"   💬 New reviews added   : {added_reviews}")
print(f"\n📂 Now open cineai.db in DB Browser — you'll see all live data!")
