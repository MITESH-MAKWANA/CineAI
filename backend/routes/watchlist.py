"""Watchlist Routes (CRUD)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from database import get_db
from models.watchlist import WatchlistItem
from routes.auth import get_current_user
from models.user import User

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])


class MovieItem(BaseModel):
    movie_id: int
    movie_title: str
    poster_path: str = ""
    vote_average: float = 0
    genre_ids: List[int] = []


@router.get("/")
def get_watchlist(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = db.query(WatchlistItem).filter(WatchlistItem.user_id == current_user.id).all()
    return [
        {
            "id": i.id, "movie_id": i.movie_id, "movie_title": i.movie_title,
            "poster_path": i.poster_path, "vote_average": i.vote_average,
            "genre_ids": [int(g) for g in i.genre_ids.split(",") if g],
            "added_at": str(i.added_at)
        }
        for i in items
    ]


@router.post("/add", status_code=201)
def add_to_watchlist(data: MovieItem, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.query(WatchlistItem).filter(
        WatchlistItem.user_id == current_user.id,
        WatchlistItem.movie_id == data.movie_id
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Movie already in watchlist")
    item = WatchlistItem(
        user_id=current_user.id,
        movie_id=data.movie_id,
        movie_title=data.movie_title,
        poster_path=data.poster_path,
        vote_average=str(data.vote_average),
        genre_ids=",".join(str(g) for g in data.genre_ids)
    )
    db.add(item)
    db.commit()
    return {"message": "Added to watchlist", "movie_id": data.movie_id}


@router.delete("/remove/{movie_id}")
def remove_from_watchlist(movie_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(WatchlistItem).filter(
        WatchlistItem.user_id == current_user.id,
        WatchlistItem.movie_id == movie_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Not found in watchlist")
    db.delete(item)
    db.commit()
    return {"message": "Removed from watchlist"}


@router.get("/check/{movie_id}")
def check_watchlist(movie_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    exists = db.query(WatchlistItem).filter(
        WatchlistItem.user_id == current_user.id,
        WatchlistItem.movie_id == movie_id
    ).first()
    return {"in_watchlist": bool(exists)}
