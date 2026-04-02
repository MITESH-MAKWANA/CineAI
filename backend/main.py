"""
CineAI - FastAPI Main Application Entry Point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import APP_NAME, DEBUG
from database import create_all_tables
from routes import auth, movies, recommendations, sentiment, watchlist, favorites
from routes import csv_movies

import os
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"[START] {APP_NAME} API starting up...")
    create_all_tables()
    try:
        from ml.sentiment_engine import SentimentEngine
        app.state.sentiment = SentimentEngine()
        print("[OK] Sentiment engine ready.")
    except Exception as e:
        print(f"[WARN] Sentiment engine startup: {e}")
    try:
        from ml.recommender_engine import RecommenderEngine
        app.state.recommender = RecommenderEngine()
        print("[OK] Recommender engine ready.")
    except Exception as e:
        print(f"[WARN] Recommender engine startup: {e}")
    yield
    # Shutdown
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
    allow_credentials=False,   # False required when allow_origins=["*"]; JWT uses Bearer headers not cookies
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(auth.router)
app.include_router(movies.router)
app.include_router(recommendations.router)
app.include_router(sentiment.router)
app.include_router(watchlist.router)
app.include_router(favorites.router)
app.include_router(csv_movies.router)


@app.get("/", tags=["Health"])
def root():
    return {"app": APP_NAME, "status": "running", "version": "1.0.0", "docs": "/docs"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy", "app": APP_NAME}
