"""
Admin Actions Route — Protected endpoints for managing users, reviews, messages.
All endpoints require ?key=ADMIN_SECRET query param.
Uses raw SQL for reliability — bypasses ORM stale-state issues.
"""
import os
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import SessionLocal

router = APIRouter(prefix="/admin", tags=["Admin Actions"])
ADMIN_SECRET = os.getenv("ADMIN_SECRET", "cineai-admin-2024")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _db():
    """Open a fresh session — avoids stale ORM state issues."""
    return SessionLocal()


def verify_key(key: str = Query(...)):
    if key != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Invalid admin key")
    return key


# ── User Actions ──────────────────────────────────────────────────────────────

@router.post("/users/{user_id}/ban")
def ban_user(user_id: int, key: str = Query(...)):
    verify_key(key)
    db = _db()
    try:
        result = db.execute(
            text("UPDATE users SET is_banned = true WHERE id = :id"),
            {"id": user_id}
        )
        db.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return {"status": "banned", "user_id": user_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ban failed: {str(e)[:300]}")
    finally:
        db.close()


@router.post("/users/{user_id}/unban")
def unban_user(user_id: int, key: str = Query(...)):
    verify_key(key)
    db = _db()
    try:
        result = db.execute(
            text("UPDATE users SET is_banned = false WHERE id = :id"),
            {"id": user_id}
        )
        db.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return {"status": "unbanned", "user_id": user_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unban failed: {str(e)[:300]}")
    finally:
        db.close()


@router.delete("/users/{user_id}")
def delete_user(user_id: int, key: str = Query(...)):
    verify_key(key)
    db = _db()
    try:
        # Check user exists first
        row = db.execute(text("SELECT id FROM users WHERE id = :id"), {"id": user_id}).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="User not found")
        # Delete related records in order to avoid FK violations
        db.execute(text("DELETE FROM watchlist WHERE user_id = :id"), {"id": user_id})
        db.execute(text("DELETE FROM favorites WHERE user_id = :id"), {"id": user_id})
        db.execute(text("DELETE FROM reviews WHERE user_id = :id"), {"id": user_id})
        # Delete any contact messages from this email (optional, soft approach)
        # Now delete the user
        db.execute(text("DELETE FROM users WHERE id = :id"), {"id": user_id})
        db.commit()
        return {"status": "deleted", "user_id": user_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)[:300]}")
    finally:
        db.close()


# ── Review Actions ────────────────────────────────────────────────────────────

class ReviewUpdate(BaseModel):
    review_text: str


@router.delete("/reviews/{review_id}")
def delete_review(review_id: int, key: str = Query(...)):
    verify_key(key)
    db = _db()
    try:
        result = db.execute(
            text("DELETE FROM reviews WHERE id = :id"),
            {"id": review_id}
        )
        db.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Review not found")
        return {"status": "deleted", "review_id": review_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e)[:200])
    finally:
        db.close()


# ── Message Actions ───────────────────────────────────────────────────────────

@router.post("/messages/{msg_id}/read")
def mark_read(msg_id: int, key: str = Query(...)):
    verify_key(key)
    db = _db()
    try:
        result = db.execute(
            text("UPDATE contact_messages SET is_read = true WHERE id = :id"),
            {"id": msg_id}
        )
        db.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Message not found")
        return {"status": "read", "msg_id": msg_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e)[:200])
    finally:
        db.close()


@router.delete("/messages/{msg_id}")
def delete_message(msg_id: int, key: str = Query(...)):
    verify_key(key)
    db = _db()
    try:
        result = db.execute(
            text("DELETE FROM contact_messages WHERE id = :id"),
            {"id": msg_id}
        )
        db.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Message not found")
        return {"status": "deleted", "msg_id": msg_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e)[:200])
    finally:
        db.close()
