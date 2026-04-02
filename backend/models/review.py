"""Review ORM model for sentiment analysis storage."""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from database import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    movie_id = Column(Integer, nullable=False, index=True)
    movie_title = Column(String(255), nullable=False)
    review_text = Column(Text, nullable=False)
    sentiment = Column(String(20), default="")  # positive / negative / neutral
    sentiment_score = Column(String(20), default="")  # score as string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
