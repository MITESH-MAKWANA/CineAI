"""
Admin API — JSON data endpoints for the admin dashboard.
All endpoints require ?key=ADMIN_SECRET query param.
"""
import os
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import SessionLocal
from models.user import User
from models.watchlist import WatchlistItem, FavoriteItem
from models.review import Review

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


def _u(u):
    return {
        "id": u.id,
        "username": u.username or "",
        "email": u.email or "",
        "age": u.age,
        "gender": u.gender or "",
        "favorite_genres": u.favorite_genres or "",
        "is_banned": getattr(u, "is_banned", False) or False,
        "created_at": str(u.created_at)[:10] if u.created_at else "",
    }


def _w(w):
    return {
        "id": w.id,
        "user_id": w.user_id,
        "movie_id": w.movie_id,
        "movie_title": w.movie_title or "",
        "poster_path": getattr(w, "poster_path", "") or "",
    }


def _r(r):
    return {
        "id": r.id,
        "user_id": r.user_id,
        "movie_id": r.movie_id,
        "movie_title": r.movie_title or "",
        "review_text": r.review_text or "",
        "sentiment": r.sentiment or "",
        "created_at": str(r.created_at)[:10] if r.created_at else "",
    }


@router.get("/data")
def admin_data(db: Session = Depends(get_db), key: str = Depends(require_key)):
    users = db.query(User).order_by(User.id).all()
    watchlist = db.query(WatchlistItem).order_by(WatchlistItem.id).all()
    favorites = db.query(FavoriteItem).order_by(FavoriteItem.id).all()
    reviews = db.query(Review).order_by(Review.id.desc()).all()

    # Contact messages (safe - table might not exist yet)
    messages = []
    try:
        from models.contact import ContactMessage
        msgs = db.query(ContactMessage).order_by(ContactMessage.created_at.desc()).all()
        messages = [{"id": m.id, "name": m.name or "", "email": m.email or "",
                     "subject": m.subject or "", "message": m.message or "",
                     "is_read": m.is_read, "created_at": str(m.created_at)[:16] if m.created_at else ""}
                    for m in msgs]
    except Exception:
        pass

    pos = sum(1 for r in reviews if r.sentiment == "positive")
    neg = sum(1 for r in reviews if r.sentiment == "negative")
    neu = sum(1 for r in reviews if r.sentiment == "neutral")
    banned = sum(1 for u in users if getattr(u, "is_banned", False))
    unread = sum(1 for m in messages if not m["is_read"])

    return {
        "stats": {
            "users": len(users), "watchlist": len(watchlist),
            "favorites": len(favorites), "reviews": len(reviews),
            "messages": len(messages), "banned": banned, "unread_msgs": unread,
            "pos": pos, "neg": neg, "neu": neu,
        },
        "users": [_u(u) for u in users],
        "watchlist": [_w(w) for w in watchlist],
        "favorites": [_w(f) for f in favorites],
        "reviews": [_r(r) for r in reviews],
        "messages": messages,
    }
