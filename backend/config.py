"""
CineAI Backend Configuration
Loads environment variables with defaults.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# TMDB
TMDB_API_KEY: str = os.getenv("TMDB_API_KEY", "")
TMDB_BASE_URL: str = os.getenv("TMDB_BASE_URL", "https://api.themoviedb.org/3")
TMDB_IMAGE_BASE: str = "https://image.tmdb.org/t/p"

# Auth
JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "changeme-dev-secret-key-not-for-prod")
JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "10080"))  # 7 days

# Database
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./cineai.db")

# App
APP_NAME: str = os.getenv("APP_NAME", "CineAI")
DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
ALLOWED_ORIGINS: list = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:5174,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:5174"
).split(",")
