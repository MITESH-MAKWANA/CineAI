"""
Sentiment Analysis Route
Uses VADER (NLTK) + ML model (Logistic Regression / TF-IDF)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models.review import Review
from routes.auth import get_current_user
from models.user import User
import os, json

router = APIRouter(prefix="/sentiment", tags=["Sentiment Analysis"])

# Lazy-load ML components
_sentiment_pipeline = None

def get_sentiment_pipeline():
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        try:
            from ml.sentiment_engine import SentimentEngine
            _sentiment_pipeline = SentimentEngine()
        except Exception as e:
            print(f"⚠️  Sentiment model load error: {e}")
            _sentiment_pipeline = None
    return _sentiment_pipeline


class ReviewRequest(BaseModel):
    movie_id: int
    movie_title: str
    review_text: str


class SentimentRequest(BaseModel):
    text: str


@router.post("/analyze")
def analyze_text(data: SentimentRequest):
    """Analyze sentiment of any text (no auth required)."""
    engine = get_sentiment_pipeline()
    if engine:
        result = engine.predict(data.text)
    else:
        # Fallback: simple keyword-based
        result = _simple_sentiment(data.text)
    return result


@router.post("/review")
def submit_review(
    data: ReviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a movie review and get sentiment analysis."""
    engine = get_sentiment_pipeline()
    if engine:
        sentiment_result = engine.predict(data.review_text)
    else:
        sentiment_result = _simple_sentiment(data.review_text)

    review = Review(
        user_id=current_user.id,
        movie_id=data.movie_id,
        movie_title=data.movie_title,
        review_text=data.review_text,
        sentiment=sentiment_result["sentiment"],
        sentiment_score=str(sentiment_result["score"])
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    return {
        "review_id": review.id,
        "sentiment": sentiment_result["sentiment"],
        "score": sentiment_result["score"],
        "confidence": sentiment_result.get("confidence", 0),
        "message": f"Your review is classified as {sentiment_result['sentiment'].upper()}"
    }


@router.get("/reviews/{movie_id}")
def get_movie_reviews(movie_id: int, db: Session = Depends(get_db)):
    """Get all reviews and sentiment stats for a movie."""
    reviews = db.query(Review).filter(Review.movie_id == movie_id).all()
    pos = sum(1 for r in reviews if r.sentiment == "positive")
    neg = sum(1 for r in reviews if r.sentiment == "negative")
    neu = sum(1 for r in reviews if r.sentiment == "neutral")
    total = len(reviews)
    return {
        "total": total,
        "positive": pos,
        "negative": neg,
        "neutral": neu,
        "sentiment_score": round((pos - neg) / total * 100, 1) if total else 0,
        "reviews": [
            {
                "id": r.id,
                "review_text": r.review_text,
                "sentiment": r.sentiment,
                "score": r.sentiment_score,
                "created_at": str(r.created_at)
            }
            for r in reviews[-20:]  # Last 20 reviews
        ]
    }


def _simple_sentiment(text: str) -> dict:
    """Fallback simple keyword sentiment."""
    text_lower = text.lower()
    positive_words = ["great", "amazing", "excellent", "loved", "fantastic", "good",
                      "wonderful", "outstanding", "brilliant", "superb", "perfect", "best"]
    negative_words = ["bad", "terrible", "awful", "horrible", "worst", "hate",
                      "boring", "disappointing", "weak", "poor", "dull", "lame"]
    pos_score = sum(text_lower.count(w) for w in positive_words)
    neg_score = sum(text_lower.count(w) for w in negative_words)
    if pos_score > neg_score:
        return {"sentiment": "positive", "score": 0.75, "confidence": 0.7}
    elif neg_score > pos_score:
        return {"sentiment": "negative", "score": 0.25, "confidence": 0.7}
    else:
        return {"sentiment": "neutral", "score": 0.5, "confidence": 0.6}
