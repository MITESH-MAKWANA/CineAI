"""Watchlist & Favorites ORM models."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from database import Base


class WatchlistItem(Base):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    movie_id = Column(Integer, nullable=False)
    movie_title = Column(String(255), nullable=False)
    poster_path = Column(String(500), default="")
    vote_average = Column(String(10), default="0")
    genre_ids = Column(Text, default="")
    added_at = Column(DateTime(timezone=True), server_default=func.now())


class FavoriteItem(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    movie_id = Column(Integer, nullable=False)
    movie_title = Column(String(255), nullable=False)
    poster_path = Column(String(500), default="")
    vote_average = Column(String(10), default="0")
    genre_ids = Column(Text, default="")
    added_at = Column(DateTime(timezone=True), server_default=func.now())
