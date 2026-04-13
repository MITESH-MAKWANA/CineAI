"""SQLAlchemy User model."""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    favorite_genres = Column(Text, default="")
    skipped_genres  = Column(Text, default="")
    age             = Column(Integer, nullable=True)
    gender          = Column(String(30), default="")
    onboarding_done = Column(Integer, default=0)
    avatar_url      = Column(String(500), default="")
    is_banned       = Column(Boolean, default=False, nullable=False)
    is_online       = Column(Boolean, default=False, nullable=False)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    updated_at      = Column(DateTime(timezone=True), onupdate=func.now())
    last_login      = Column(DateTime(timezone=True), nullable=True)
