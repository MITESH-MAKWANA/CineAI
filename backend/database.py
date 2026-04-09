"""
CineAI Database Setup - SQLAlchemy with SQLite (local) + PostgreSQL (production)
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL

# Render gives postgres:// but SQLAlchemy needs postgresql://
_db_url = DATABASE_URL
if _db_url.startswith("postgres://"):
    _db_url = _db_url.replace("postgres://", "postgresql://", 1)

# SQLite needs check_same_thread=False; PostgreSQL does not
_is_sqlite = _db_url.startswith("sqlite")
_connect_args = {"check_same_thread": False} if _is_sqlite else {}

engine = create_engine(_db_url, connect_args=_connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency to get DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_migrations():
    """Safely add new columns to existing tables. Never raises."""
    try:
        from sqlalchemy import text
        if _is_sqlite:
            with engine.connect() as conn:
                result = conn.execute(text("PRAGMA table_info(users)"))
                cols = [row[1] for row in result]
                if "is_banned" not in cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN is_banned INTEGER DEFAULT 0"))
                if "last_login" not in cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN last_login DATETIME"))
                conn.commit()
        else:
            # PostgreSQL — use engine.begin() for auto-commit transaction
            with engine.begin() as conn:
                conn.execute(text(
                    "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_banned BOOLEAN DEFAULT FALSE"
                ))
                conn.execute(text(
                    "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMPTZ"
                ))
        print("[OK] Migrations applied.")
    except Exception as e:
        print(f"[WARN] Migration skipped (non-fatal): {e}")


def create_all_tables():
    """Create all tables defined in models. Never raises."""
    try:
        from models import user, watchlist, review, contact  # noqa: F401
        Base.metadata.create_all(bind=engine)
        print(f"[OK] Database tables created ({_db_url[:30]}...).")
        run_migrations()
    except Exception as e:
        print(f"[WARN] create_all_tables error (non-fatal): {e}")
