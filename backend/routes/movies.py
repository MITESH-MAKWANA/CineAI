"""
Movies Routes — TMDB proxy with search, filters, trending, top rated
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import httpx
from config import TMDB_API_KEY, TMDB_BASE_URL

router = APIRouter(prefix="/movies", tags=["Movies"])

GENRE_MAP = {
    "action": 28, "adventure": 12, "animation": 16, "comedy": 35,
    "crime": 80, "documentary": 99, "drama": 18, "family": 10751,
    "fantasy": 14, "history": 36, "horror": 27, "music": 10402,
    "mystery": 9648, "romance": 10749, "science fiction": 878,
    "sci-fi": 878, "thriller": 53, "war": 10752, "western": 37
}

LANGUAGE_MAP = {
    "hollywood": "en",
    "bollywood": "hi",
    "anime": "ja",
    "korean": "ko",
    "french": "fr",
    "spanish": "es",
    "german": "de",
    "tamil": "ta",
    "telugu": "te",
}


def tmdb_get(endpoint: str, params: dict = {}) -> dict:
    params["api_key"] = TMDB_API_KEY
    url = f"{TMDB_BASE_URL}{endpoint}"
    with httpx.Client(timeout=15) as client:
        resp = client.get(url, params=params)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="TMDB API error")
        return resp.json()


@router.get("/trending")
def get_trending(page: int = 1):
    return tmdb_get("/trending/movie/week", {"page": page})


@router.get("/popular")
def get_popular(page: int = 1):
    return tmdb_get("/movie/popular", {"page": page})


@router.get("/top-rated")
def get_top_rated(page: int = 1):
    return tmdb_get("/movie/top_rated", {"page": page})


@router.get("/upcoming")
def get_upcoming(page: int = 1):
    return tmdb_get("/movie/upcoming", {"page": page})


@router.get("/by-genre")
def get_by_genre(genre: str, page: int = 1):
    genre_id = GENRE_MAP.get(genre.lower())
    if not genre_id:
        raise HTTPException(status_code=400, detail=f"Unknown genre: {genre}")
    return tmdb_get("/discover/movie", {
        "with_genres": genre_id,
        "sort_by": "popularity.desc",
        "page": page
    })


@router.get("/search")
def search_movies(
    query: Optional[str] = None,
    genre: Optional[str] = None,
    source: Optional[str] = None,
    min_rating: Optional[float] = None,
    max_rating: Optional[float] = None,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    page: int = 1
):
    params = {"page": page, "sort_by": "popularity.desc", "include_adult": False}

    if query:
        # Use search endpoint when there's a text query
        result = tmdb_get("/search/movie", {"query": query, "page": page})
        return result

    # Discover with filters
    if genre:
        genre_id = GENRE_MAP.get(genre.lower())
        if genre_id:
            params["with_genres"] = genre_id

    if source:
        lang = LANGUAGE_MAP.get(source.lower())
        if lang:
            params["with_original_language"] = lang

    if min_rating is not None:
        params["vote_average.gte"] = min_rating
    if max_rating is not None:
        params["vote_average.lte"] = max_rating

    if year_from:
        params["primary_release_date.gte"] = f"{year_from}-01-01"
    if year_to:
        params["primary_release_date.lte"] = f"{year_to}-12-31"

    return tmdb_get("/discover/movie", params)


@router.get("/{movie_id}")
def get_movie_detail(movie_id: int):
    details = tmdb_get(f"/movie/{movie_id}", {
        "append_to_response": "videos,credits,similar,reviews"
    })
    return details


@router.get("/{movie_id}/videos")
def get_movie_videos(movie_id: int):
    return tmdb_get(f"/movie/{movie_id}/videos")


@router.get("/genres/list")
def get_genre_list():
    return tmdb_get("/genre/movie/list")
