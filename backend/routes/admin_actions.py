"""
Admin Actions Route — Protected endpoints for managing users, reviews, messages.
All endpoints require ?key=ADMIN_SECRET query param.
"""
import os
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal
from models.user import User
from models.review import Review
from models.contact import ContactMessage

router = APIRouter(prefix="/admin", tags=["Admin Actions"])

ADMIN_SECRET = os.getenv("ADMIN_SECRET", "cineai-admin-2024")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_key(key: str = Query(...)):
    if key != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Invalid admin key")
    return key


# ── User Actions ──────────────────────────────────────────────────────────────

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), key: str = Depends(verify_key)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"status": "deleted", "user_id": user_id}


@router.post("/users/{user_id}/ban")
def ban_user(user_id: int, db: Session = Depends(get_db), key: str = Depends(verify_key)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_banned = True
    db.commit()
    return {"status": "banned", "user_id": user_id}


@router.post("/users/{user_id}/unban")
def unban_user(user_id: int, db: Session = Depends(get_db), key: str = Depends(verify_key)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_banned = False
    db.commit()
    return {"status": "unbanned", "user_id": user_id}


# ── Review Actions ────────────────────────────────────────────────────────────

class ReviewUpdate(BaseModel):
    review_text: str


@router.delete("/reviews/{review_id}")
def delete_review(review_id: int, db: Session = Depends(get_db), key: str = Depends(verify_key)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    db.delete(review)
    db.commit()
    return {"status": "deleted", "review_id": review_id}


@router.put("/reviews/{review_id}")
def edit_review(review_id: int, body: ReviewUpdate, db: Session = Depends(get_db), key: str = Depends(verify_key)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    review.review_text = body.review_text.strip()
    db.commit()
    return {"status": "updated", "review_id": review_id}


# ── Message Actions ───────────────────────────────────────────────────────────

@router.post("/messages/{msg_id}/read")
def mark_read(msg_id: int, db: Session = Depends(get_db), key: str = Depends(verify_key)):
    msg = db.query(ContactMessage).filter(ContactMessage.id == msg_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    msg.is_read = True
    db.commit()
    return {"status": "read", "msg_id": msg_id}


@router.delete("/messages/{msg_id}")
def delete_message(msg_id: int, db: Session = Depends(get_db), key: str = Depends(verify_key)):
    msg = db.query(ContactMessage).filter(ContactMessage.id == msg_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    db.delete(msg)
    db.commit()
    return {"status": "deleted", "msg_id": msg_id}
