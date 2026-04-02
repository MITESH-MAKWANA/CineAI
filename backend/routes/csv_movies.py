"""
CSV Movies Route — Serves movies from movies1.csv dataset
Supports: list, search, filter by genre/year/rating, movie detail
"""
import csv, os, re
from fastapi import APIRouter, Query
from typing import Optional, List

router = APIRouter(prefix="/csv", tags=["CSV Movies"])

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "ml", "dataset", "tmdbmovies.csv")

# ── Load CSV once at startup ──────────────────────────────────────────────────
_MOVIES: List[dict] = []

def _load():
    global _MOVIES
    if _MOVIES:
        return
    try:
        with open(CSV_PATH, encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    rating = float(row.get("vote_average") or 0)
                    year_raw = row.get("release_date", "")
                    # Handle DD-MM-YYYY and YYYY-MM-DD
                    year = ""
                    if year_raw:
                        parts = year_raw.replace("/", "-").split("-")
                        if len(parts) == 3:
                            year = parts[2] if len(parts[0]) <= 2 else parts[0]
                    genres_raw = row.get("genres", "")
                    genres = [g.strip() for g in genres_raw.split(",") if g.strip()] if genres_raw else []
                    countries_raw = row.get("production_countries", "")
                    countries = [c.strip() for c in countries_raw.split(",") if c.strip()] if countries_raw else []
                    spoken_raw = row.get("spoken_languages", "")
                    spoken = [s.strip() for s in spoken_raw.split(",") if s.strip()] if spoken_raw else []
                    companies_raw = row.get("production_companies", "")
                    companies = [c.strip() for c in companies_raw.split(",") if c.strip()] if companies_raw else []
                    _MOVIES.append({
                        "id": int(row.get("id") or 0),
                        "title": row.get("title", "").strip(),
                        "original_title": row.get("original_title", "").strip(),
                        "status": row.get("status", "").strip(),
                        "vote_average": round(rating, 1),
                        "vote_count": int(row.get("vote_count") or 0),
                        "release_date": year_raw,
                        "year": year,
                        "overview": row.get("overview", "").strip(),
                        "poster_path": row.get("poster_path", "").strip(),
                        "backdrop_path": row.get("backdrop_path", "").strip(),
                        "tagline": row.get("tagline", "").strip(),
                        "runtime": int(row.get("runtime") or 0),
                        "genres": genres,
                        "genre_ids": [],
                        "production_countries": countries,
                        "production_companies": companies,
                        "spoken_languages": spoken,
                        "original_language": row.get("original_language", "").strip(),
                        "popularity": float(row.get("popularity") or 0),
                        "revenue": int(float(row.get("revenue") or 0)),
                        "budget": int(float(row.get("budget") or 0)),
                        "keywords": row.get("keywords", "").strip(),
                        "homepage": row.get("homepage", "").strip(),
                        "imdb_id": row.get("imdb_id", "").strip(),
                    })
                except Exception:
                    continue
        # Sort by popularity descending
        _MOVIES.sort(key=lambda m: m["popularity"], reverse=True)
    except Exception as e:
        print(f"[CSV] Error loading movies: {e}")

_load()

def _paginate(items, page=1, per_page=20):
    total = len(items)
    start = (page - 1) * per_page
    return {
        "results": items[start:start + per_page],
        "total_results": total,
        "total_pages": (total + per_page - 1) // per_page,
        "page": page
    }

# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/movies")
def list_movies(page: int = 1, per_page: int = 20):
    _load()
    return _paginate(_MOVIES, page, per_page)


@router.get("/movies/trending")
def trending(page: int = 1):
    _load()
    top = sorted(_MOVIES, key=lambda m: m["popularity"], reverse=True)
    return _paginate(top, page)


@router.get("/movies/top-rated")
def top_rated(page: int = 1):
    _load()
    top = sorted(_MOVIES, key=lambda m: m["vote_average"], reverse=True)
    return _paginate(top, page)


@router.get("/movies/by-genre")
def by_genre(genre: str, page: int = 1):
    _load()
    gl = genre.lower().strip()
    filtered = [m for m in _MOVIES if any(g.lower() == gl for g in m["genres"])]
    return _paginate(filtered, page)


@router.get("/movies/search")
def search(
    query: Optional[str] = None,
    genre: Optional[str] = None,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    min_rating: Optional[float] = None,
    max_rating: Optional[float] = None,
    language: Optional[str] = None,
    page: int = 1,
    per_page: int = 40,
):
    _load()
    results = _MOVIES[:]

    if query:
        q = query.lower().strip()
        def _match(m):
            if q in m["title"].lower(): return True
            if q in m["overview"].lower(): return True
            if any(q in g.lower() for g in m["genres"]): return True
            kw = m.get("keywords", "") or ""
            if q in kw.lower(): return True
            return False
        results = [m for m in results if _match(m)]

    if genre:
        gl = genre.lower().strip()
        results = [m for m in results if any(g.lower() == gl for g in m["genres"])]

    if year_from:
        results = [m for m in results if m["year"] and int(m["year"]) >= year_from]

    if year_to:
        results = [m for m in results if m["year"] and int(m["year"]) <= year_to]

    if min_rating is not None:
        results = [m for m in results if m["vote_average"] >= min_rating]

    if max_rating is not None:
        results = [m for m in results if m["vote_average"] <= max_rating]

    if language:
        results = [m for m in results if m["original_language"] == language]

    return _paginate(results, page, per_page)


@router.get("/movies/genres")
def all_genres():
    _load()
    genres = set()
    for m in _MOVIES:
        for g in m["genres"]:
            if g:
                genres.add(g)
    return sorted(genres)


@router.get("/movies/years")
def all_years():
    _load()
    years = sorted(set(m["year"] for m in _MOVIES if m["year"] and m["year"].isdigit()), reverse=True)
    return years


@router.get("/movies/{movie_id}")
def movie_detail(movie_id: int):
    _load()
    for m in _MOVIES:
        if m["id"] == movie_id:
            return m
    # Fallback: return empty
    return {"id": movie_id, "title": "Unknown", "genres": [], "overview": ""}
