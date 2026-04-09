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


@router.get("/data")
def admin_data(db: Session = Depends(get_db), key: str = Depends(require_key)):
    """Return all admin dashboard data as JSON. Fully fault-tolerant."""

    # ── Users ──────────────────────────────────────────────────────────
    user_list = []
    try:
        rows = db.execute(text(
            "SELECT id, username, email, age, gender, favorite_genres, "
            "COALESCE(is_banned, false) as is_banned, "
            "created_at FROM users ORDER BY id"
        )).fetchall()
        for r in rows:
            user_list.append({
                "id": r[0], "username": r[1] or "", "email": r[2] or "",
                "age": r[3], "gender": r[4] or "",
                "favorite_genres": r[5] or "",
                "is_banned": bool(r[6]),
                "created_at": str(r[7])[:10] if r[7] else "",
            })
    except Exception:
        db.rollback()
        # Fallback without is_banned column
        try:
            rows = db.execute(text(
                "SELECT id, username, email, age, gender, favorite_genres, "
                "created_at FROM users ORDER BY id"
            )).fetchall()
            for r in rows:
                user_list.append({
                    "id": r[0], "username": r[1] or "", "email": r[2] or "",
                    "age": r[3], "gender": r[4] or "",
                    "favorite_genres": r[5] or "",
                    "is_banned": False,
                    "created_at": str(r[6])[:10] if r[6] else "",
                })
        except Exception:
            db.rollback()

    # ── Watchlist ──────────────────────────────────────────────────────
    wl_list = []
    try:
        rows = db.execute(text(
            "SELECT id, user_id, movie_id, movie_title, "
            "COALESCE(poster_path, '') as poster_path "
            "FROM watchlist ORDER BY id"
        )).fetchall()
        for r in rows:
            wl_list.append({"id": r[0], "user_id": r[1], "movie_id": r[2],
                            "movie_title": r[3] or "", "poster_path": r[4] or ""})
    except Exception:
        db.rollback()
        try:
            rows = db.execute(text(
                "SELECT id, user_id, movie_id, movie_title FROM watchlist ORDER BY id"
            )).fetchall()
            for r in rows:
                wl_list.append({"id": r[0], "user_id": r[1], "movie_id": r[2],
                                "movie_title": r[3] or "", "poster_path": ""})
        except Exception:
            db.rollback()

    # ── Favorites ──────────────────────────────────────────────────────
    fav_list = []
    try:
        rows = db.execute(text(
            "SELECT id, user_id, movie_id, movie_title, "
            "COALESCE(poster_path, '') as poster_path "
            "FROM favorites ORDER BY id"
        )).fetchall()
        for r in rows:
            fav_list.append({"id": r[0], "user_id": r[1], "movie_id": r[2],
                             "movie_title": r[3] or "", "poster_path": r[4] or ""})
    except Exception:
        db.rollback()
        try:
            rows = db.execute(text(
                "SELECT id, user_id, movie_id, movie_title FROM favorites ORDER BY id"
            )).fetchall()
            for r in rows:
                fav_list.append({"id": r[0], "user_id": r[1], "movie_id": r[2],
                                 "movie_title": r[3] or "", "poster_path": ""})
        except Exception:
            db.rollback()

    # ── Reviews ────────────────────────────────────────────────────────
    rev_list = []
    try:
        from models.review import Review
        rows = db.execute(text(
            "SELECT id, user_id, movie_id, movie_title, review_text, "
            "sentiment, created_at FROM reviews ORDER BY id DESC"
        )).fetchall()
        for r in rows:
            rev_list.append({
                "id": r[0], "user_id": r[1], "movie_id": r[2],
                "movie_title": r[3] or "", "review_text": r[4] or "",
                "sentiment": r[5] or "", "created_at": str(r[6])[:10] if r[6] else "",
            })
    except Exception:
        db.rollback()

    # ── Messages ───────────────────────────────────────────────────────
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
                "is_read": bool(r[5]), "created_at": str(r[6])[:16] if r[6] else "",
            })
    except Exception:
        db.rollback()

    # ── Stats ──────────────────────────────────────────────────────────
    pos = sum(1 for r in rev_list if r["sentiment"] == "positive")
    neg = sum(1 for r in rev_list if r["sentiment"] == "negative")
    neu = sum(1 for r in rev_list if r["sentiment"] == "neutral")
    banned = sum(1 for u in user_list if u["is_banned"])
    unread = sum(1 for m in msg_list if not m["is_read"])

    return {
        "stats": {
            "users": len(user_list), "watchlist": len(wl_list),
            "favorites": len(fav_list), "reviews": len(rev_list),
            "messages": len(msg_list), "banned": banned, "unread_msgs": unread,
            "pos": pos, "neg": neg, "neu": neu,
        },
        "users": user_list,
        "watchlist": wl_list,
        "favorites": fav_list,
        "reviews": rev_list,
        "messages": msg_list,
    }
