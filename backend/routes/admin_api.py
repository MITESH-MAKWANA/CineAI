"""
Admin API — JSON data endpoints for the admin dashboard.
All endpoints require ?key=ADMIN_SECRET query param.
"""
import os
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import SessionLocal

router = APIRouter(prefix="/admin/api", tags=["Admin API"])
ADMIN_SECRET = os.getenv("ADMIN_SECRET", "cineai-admin-2024")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_key(key: str = Query(...)):
    if key != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Invalid admin key")
    return key


def fmt(dt):
    return str(dt)[:16].replace("T", " ") if dt else "-"


# ── Lightweight stats for polling ─────────────────────────────────────
@router.get("/stats")
def admin_stats(db: Session = Depends(get_db), key: str = Depends(require_key)):
    """Fast endpoint for 30s live polling — counts only."""
    try:
        r = db.execute(text("""
            SELECT
              (SELECT COUNT(*) FROM users) as users,
              (SELECT COUNT(*) FROM watchlist) as watchlist,
              (SELECT COUNT(*) FROM favorites) as favorites,
              (SELECT COUNT(*) FROM reviews) as reviews,
              (SELECT COUNT(*) FROM contact_messages) as messages,
              (SELECT COUNT(*) FROM contact_messages WHERE NOT is_read) as unread
        """)).fetchone()
        return {"users": r[0], "watchlist": r[1], "favorites": r[2],
                "reviews": r[3], "messages": r[4], "unread": r[5]}
    except Exception:
        db.rollback()
        return {"users": 0, "watchlist": 0, "favorites": 0,
                "reviews": 0, "messages": 0, "unread": 0}


# ── Full data endpoint ────────────────────────────────────────────────
@router.get("/data")
def admin_data(db: Session = Depends(get_db), key: str = Depends(require_key)):
    """Full dashboard data — called on load and refresh."""

    # ── Users with activity counts ────────────────────────────────────
    user_list = []
    try:
        rows = db.execute(text("""
            SELECT u.id, u.username, u.email, u.age, u.gender,
                   u.favorite_genres,
                   COALESCE(u.is_banned, false) AS is_banned,
                   u.created_at, u.last_login,
                   COUNT(DISTINCT w.id) AS wl_count,
                   COUNT(DISTINCT f.id) AS fav_count,
                   COUNT(DISTINCT r.id) AS rev_count
            FROM users u
            LEFT JOIN watchlist w ON w.user_id = u.id
            LEFT JOIN favorites f ON f.user_id = u.id
            LEFT JOIN reviews r ON r.user_id = u.id
            GROUP BY u.id
            ORDER BY u.id
        """)).fetchall()
        for row in rows:
            user_list.append({
                "id": row[0], "username": row[1] or "", "email": row[2] or "",
                "age": row[3], "gender": row[4] or "",
                "favorite_genres": row[5] or "",
                "is_banned": bool(row[6]),
                "created_at": fmt(row[7]),
                "last_login": fmt(row[8]),
                "wl_count": row[9] or 0,
                "fav_count": row[10] or 0,
                "rev_count": row[11] or 0,
            })
    except Exception:
        db.rollback()
        try:
            rows = db.execute(text(
                "SELECT id, username, email, age, gender, favorite_genres, created_at FROM users ORDER BY id"
            )).fetchall()
            for row in rows:
                user_list.append({
                    "id": row[0], "username": row[1] or "", "email": row[2] or "",
                    "age": row[3], "gender": row[4] or "",
                    "favorite_genres": row[5] or "", "is_banned": False,
                    "created_at": fmt(row[6]), "last_login": "-",
                    "wl_count": 0, "fav_count": 0, "rev_count": 0,
                })
        except Exception:
            db.rollback()

    # ── Watchlist ─────────────────────────────────────────────────────
    wl_list = []
    try:
        rows = db.execute(text(
            "SELECT id, user_id, movie_id, movie_title, "
            "COALESCE(poster_path,'') AS poster_path, added_at FROM watchlist ORDER BY id"
        )).fetchall()
        for r in rows:
            wl_list.append({"id": r[0], "user_id": r[1], "movie_id": r[2],
                            "movie_title": r[3] or "", "poster_path": r[4] or "",
                            "added_at": fmt(r[5])})
    except Exception:
        db.rollback()

    # ── Favorites ─────────────────────────────────────────────────────
    fav_list = []
    try:
        rows = db.execute(text(
            "SELECT id, user_id, movie_id, movie_title, "
            "COALESCE(poster_path,'') AS poster_path, added_at FROM favorites ORDER BY id"
        )).fetchall()
        for r in rows:
            fav_list.append({"id": r[0], "user_id": r[1], "movie_id": r[2],
                             "movie_title": r[3] or "", "poster_path": r[4] or "",
                             "added_at": fmt(r[5])})
    except Exception:
        db.rollback()

    # ── Reviews ───────────────────────────────────────────────────────
    rev_list = []
    try:
        rows = db.execute(text(
            "SELECT id, user_id, movie_id, movie_title, review_text, "
            "sentiment, created_at FROM reviews ORDER BY id DESC"
        )).fetchall()
        for r in rows:
            rev_list.append({
                "id": r[0], "user_id": r[1], "movie_id": r[2],
                "movie_title": r[3] or "", "review_text": r[4] or "",
                "sentiment": r[5] or "", "created_at": fmt(r[6]),
            })
    except Exception:
        db.rollback()

    # ── Messages ──────────────────────────────────────────────────────
    msg_list = []
    try:
        rows = db.execute(text(
            "SELECT id, name, email, subject, message, is_read, created_at "
            "FROM contact_messages ORDER BY created_at DESC"
        )).fetchall()
        for r in rows:
            msg_list.append({
                "id": r[0], "name": r[1] or "", "email": r[2] or "",
                "subject": r[3] or "", "message": r[4] or "",
                "is_read": bool(r[5]), "created_at": fmt(r[6]),
            })
    except Exception:
        db.rollback()

    # ── Popular movies ────────────────────────────────────────────────
    popular = []
    try:
        rows = db.execute(text("""
            SELECT movie_title, COUNT(*) AS cnt
            FROM (
                SELECT movie_title FROM watchlist
                UNION ALL
                SELECT movie_title FROM favorites
            ) t
            WHERE movie_title IS NOT NULL AND movie_title != ''
            GROUP BY movie_title ORDER BY cnt DESC LIMIT 10
        """)).fetchall()
        popular = [{"title": r[0], "count": r[1]} for r in rows]
    except Exception:
        db.rollback()

    # ── Stats ─────────────────────────────────────────────────────────
    pos = sum(1 for r in rev_list if r["sentiment"] == "positive")
    neg = sum(1 for r in rev_list if r["sentiment"] == "negative")
    neu = sum(1 for r in rev_list if r["sentiment"] == "neutral")
    banned = sum(1 for u in user_list if u["is_banned"])
    unread = sum(1 for m in msg_list if not m["is_read"])
    active = sum(1 for u in user_list if u["rev_count"] + u["wl_count"] + u["fav_count"] > 0)

    # Top 5 most active users
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
        "users": user_list,
        "watchlist": wl_list,
        "favorites": fav_list,
        "reviews": rev_list,
        "messages": msg_list,
        "popular": popular,
        "top_users": top_users,
    }
