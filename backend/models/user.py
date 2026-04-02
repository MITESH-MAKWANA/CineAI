"""SQLAlchemy User model."""
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    favorite_genres = Column(Text, default="")   # comma-separated loved genres
    skipped_genres  = Column(Text, default="")   # comma-separated skipped genres
    age             = Column(Integer, nullable=True)
    gender          = Column(String(30), default="")
    onboarding_done = Column(Integer, default=0)  # 0=no, 1=yes
    avatar_url = Column(String(500), default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
