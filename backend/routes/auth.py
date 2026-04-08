"""
Auth Routes — Register, Login, Profile, Genre Update
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from database import get_db
from models.user import User
from auth_utils import hash_password, verify_password, create_access_token, decode_token
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ── Pydantic Schemas ──────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class GenreUpdateRequest(BaseModel):
    genres: List[str]

class ProfileUpdateRequest(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    loved_genres: Optional[List[str]] = None
    skipped_genres: Optional[List[str]] = None
    onboarding_done: Optional[bool] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    favorite_genres: Optional[str] = ""
    class Config:
        from_attributes = True


# ── Dependency: current user ──────────────────────────────────────────────────
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    try:
        user_id = int(payload.get("sub"))  # sub is stored as str, cast back to int
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token subject")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ── Routes ────────────────────────────────────────────────────────────────────
@router.post("/register", status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    # Validate length
    if len(data.username.strip()) < 2:
        raise HTTPException(status_code=400, detail="Username must be at least 2 characters")
    if len(data.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    if db.query(User).filter(User.email == data.email.lower().strip()).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.username == data.username.strip()).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    user = User(
        username=data.username.strip(),
        email=data.email.lower().strip(),
        hashed_password=hash_password(data.password),
        favorite_genres=""
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": str(user.id), "username": user.username})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "favorite_genres": user.favorite_genres or "",
            "skipped_genres":  user.skipped_genres or "",
            "age":             user.age,
            "gender":          user.gender or "",
            "onboarding_done": bool(user.onboarding_done)
        }
    }


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.lower().strip()).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token({"sub": str(user.id), "username": user.username})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "favorite_genres": user.favorite_genres or "",
            "skipped_genres":  user.skipped_genres or "",
            "age":             user.age,
            "gender":          user.gender or "",
            "onboarding_done": bool(user.onboarding_done)
        }
    }


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "favorite_genres": current_user.favorite_genres or "",
        "skipped_genres":  current_user.skipped_genres or "",
        "age":             current_user.age,
        "gender":          current_user.gender or "",
        "onboarding_done": bool(current_user.onboarding_done)
    }


@router.put("/genres")
def update_genres(
    data: GenreUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_user.favorite_genres = ",".join(data.genres)
    db.commit()
    return {"message": "Genres updated", "favorite_genres": current_user.favorite_genres}


@router.put("/profile")
def update_profile(
    data: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if data.age is not None:             current_user.age = data.age
    if data.gender is not None:          current_user.gender = data.gender
    if data.loved_genres is not None:    current_user.favorite_genres = ",".join(data.loved_genres)
    if data.skipped_genres is not None:  current_user.skipped_genres  = ",".join(data.skipped_genres)
    if data.onboarding_done is not None: current_user.onboarding_done = 1 if data.onboarding_done else 0
    db.commit()
    return {
        "message": "Profile updated",
        "favorite_genres": current_user.favorite_genres or "",
        "skipped_genres":  current_user.skipped_genres or "",
        "age":             current_user.age,
        "gender":          current_user.gender or "",
        "onboarding_done": bool(current_user.onboarding_done)
    }


# ── Change Password ───────────────────────────────────────────────────────────
class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

@router.put("/change-password")
def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    if len(data.new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters")
    if data.current_password == data.new_password:
        raise HTTPException(status_code=400, detail="New password must be different from current password")
    current_user.hashed_password = hash_password(data.new_password)
    db.commit()
    return {"message": "Password changed successfully"}


# ── Forgot Password (mock — no email service) ─────────────────────────────────
class ForgotPasswordRequest(BaseModel):
    email: str

@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    # Always return success to prevent email enumeration
    user = db.query(User).filter(User.email == data.email.lower().strip()).first()
    # In production, send reset email here. For now we acknowledge receipt.
    return {"message": "If this email is registered, a reset link has been sent."}


# ── Admin Export (protected by secret key) ────────────────────────────────────
import os
from fastapi import Query
from models.watchlist import WatchlistItem, FavoriteItem
from models.review import Review

ADMIN_SECRET = os.getenv("ADMIN_SECRET", "cineai-admin-2024")

@router.get("/admin/export")
def admin_export(key: str = Query(...), db: Session = Depends(get_db)):
    """Export all data from the live database as JSON. Protected by ADMIN_SECRET key."""
    if key != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Invalid admin key")

    users     = db.query(User).all()
    watchlist = db.query(WatchlistItem).all()
    favorites = db.query(FavoriteItem).all()
    reviews   = db.query(Review).all()

    return {
        "total_users": len(users),
        "users": [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "age": u.age,
                "gender": u.gender or "",
                "favorite_genres": u.favorite_genres or "",
            }
            for u in users
        ],
        "total_watchlist": len(watchlist),
        "watchlist": [
            {"id": w.id, "user_id": w.user_id, "movie_id": w.movie_id, "movie_title": w.movie_title}
            for w in watchlist
        ],
        "total_favorites": len(favorites),
        "favorites": [
            {"id": f.id, "user_id": f.user_id, "movie_id": f.movie_id, "movie_title": f.movie_title}
            for f in favorites
        ],
        "total_reviews": len(reviews),
        "reviews": [
            {
                "id": r.id,
                "user_id": r.user_id,
                "movie_id": r.movie_id,
                "movie_title": r.movie_title,
                "review_text": r.review_text,
                "sentiment": r.sentiment,
            }
            for r in reviews
        ],
    }
