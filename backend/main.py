"""
CineAI - FastAPI Main Application Entry Point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from config import APP_NAME
from database import create_all_tables
from routes import auth, movies, recommendations, sentiment, watchlist, favorites
from routes import csv_movies
from routes import contact, admin_actions, admin_api
import os

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
ADMIN_SECRET    = os.getenv("ADMIN_SECRET", "cineai-admin-2024")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"[START] {APP_NAME} API starting up...")
    try:
        create_all_tables()
    except Exception as e:
        print(f"[WARN] DB init: {e}")
    try:
        from ml.sentiment_engine import SentimentEngine
        app.state.sentiment = SentimentEngine()
        print("[OK] Sentiment engine ready.")
    except Exception as e:
        print(f"[WARN] Sentiment engine startup: {e}")
    # Recommender loads lazily on first request to avoid startup timeout
    yield
    print(f"[STOP] {APP_NAME} shutting down.")


app = FastAPI(
    title=f"{APP_NAME} API",
    description="AI-powered Movie Recommendation & Sentiment Analysis Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(movies.router)
app.include_router(recommendations.router)
app.include_router(sentiment.router)
app.include_router(watchlist.router)
app.include_router(favorites.router)
app.include_router(csv_movies.router)
app.include_router(contact.router)
app.include_router(admin_actions.router)
app.include_router(admin_api.router)


@app.get("/", tags=["Health"])
def root():
    return {"app": APP_NAME, "status": "running", "version": "1.0.0", "docs": "/docs"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy", "app": APP_NAME}



# Admin Dashboard
@app.get("/admin", response_class=HTMLResponse, tags=["Admin"])
def admin_dashboard(key: str = Query(default="")):
    from admin_dashboard import LOGIN_HTML, WRONG_HTML, DASHBOARD_HTML
    if not key:
        return HTMLResponse(LOGIN_HTML)
    if key != ADMIN_SECRET:
        return HTMLResponse(WRONG_HTML, status_code=403)
    return HTMLResponse(DASHBOARD_HTML)

