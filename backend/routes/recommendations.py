"""
Recommendations Route — Content-Based Filtering via TF-IDF + Cosine Similarity
"""
from fastapi import APIRouter, Query, Depends, HTTPException
from routes.auth import get_current_user
from models.user import User
import httpx
from config import TMDB_API_KEY, TMDB_BASE_URL

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

_recommender = None

def get_recommender():
    global _recommender
    if _recommender is None:
        try:
            from ml.recommender_engine import RecommenderEngine
            _recommender = RecommenderEngine()
        except Exception as e:
            print(f"⚠️  Recommender load error: {e}")
            _recommender = None
    return _recommender


def tmdb_get(endpoint: str, params: dict = {}) -> dict:
    params["api_key"] = TMDB_API_KEY
    with httpx.Client(timeout=15) as client:
        resp = client.get(f"{TMDB_BASE_URL}{endpoint}", params=params)
        return resp.json() if resp.status_code == 200 else {}


@router.get("/for-movie/{movie_id}")
def recommend_similar(movie_id: int, limit: int = 12):
    """Get ML-based content-similar movies for a given movie ID."""
    rec = get_recommender()
    if rec:
        indices = rec.get_similar(movie_id, limit)
        if indices:
            movies = []
            for mid in indices:
                data = tmdb_get(f"/movie/{mid}")
                if data.get("id"):
                    movies.append(data)
            if movies:
                return {"results": movies, "source": "ml_content_based"}

    # Fallback: TMDB similar
    result = tmdb_get(f"/movie/{movie_id}/similar", {"page": 1})
    return {"results": result.get("results", [])[:limit], "source": "tmdb_similar"}


@router.get("/personalized")
def personalized_recommendations(
    current_user: User = Depends(get_current_user),
    limit: int = 20,
    page: int = 1
):
    """Get personalized recommendations based on user's genre preferences."""
    genres = [g.strip() for g in current_user.favorite_genres.split(",") if g.strip()]
    
    GENRE_MAP = {
        "action": 28, "adventure": 12, "animation": 16, "comedy": 35,
        "crime": 80, "drama": 18, "family": 10751, "fantasy": 14,
        "history": 36, "horror": 27, "music": 10402, "mystery": 9648,
        "romance": 10749, "science fiction": 878, "sci-fi": 878,
        "thriller": 53, "war": 10752, "western": 37
    }
    
    genre_ids = [str(GENRE_MAP[g.lower()]) for g in genres if g.lower() in GENRE_MAP]
    
    params = {
        "sort_by": "vote_average.desc",
        "vote_count.gte": 100,
        "page": page
    }
    if genre_ids:
        params["with_genres"] = "|".join(genre_ids)  # OR across genres
    
    result = tmdb_get("/discover/movie", params)
    results = result.get("results", [])[:limit]
    return {"results": results, "source": "personalized", "genres_used": genres}


@router.get("/trending-ai")
def ai_trending(limit: int = 20):
    """Trending movies weighted by AI score (vote_average × log(vote_count))."""
    import math
    result = tmdb_get("/trending/movie/week", {"page": 1})
    movies = result.get("results", [])
    for m in movies:
        vc = m.get("vote_count", 1) or 1
        va = m.get("vote_average", 0) or 0
        m["ai_score"] = round(va * math.log(max(vc, 1)), 3)
    movies.sort(key=lambda x: x["ai_score"], reverse=True)
    return {"results": movies[:limit]}
