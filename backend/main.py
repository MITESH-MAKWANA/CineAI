"""
CineAI - FastAPI Main Application Entry Point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from config import APP_NAME, DEBUG
from database import create_all_tables, get_db
from routes import auth, movies, recommendations, sentiment, watchlist, favorites
from routes import csv_movies
import os

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
ADMIN_SECRET    = os.getenv("ADMIN_SECRET", "cineai-admin-2024")


@asynccontextmanager
async def lifespan(app: FastAPI):
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


# ── Admin Dashboard ────────────────────────────────────────────────────────────
@app.get("/admin", response_class=HTMLResponse, tags=["Admin"])
def admin_dashboard(key: str = Query(...)):
    if key != ADMIN_SECRET:
        return HTMLResponse("<h2 style='color:red;font-family:sans-serif'>❌ Invalid admin key</h2>", status_code=403)

    from sqlalchemy.orm import Session
    from database import SessionLocal
    from models.user import User
    from models.watchlist import WatchlistItem, FavoriteItem
    from models.review import Review

    db: Session = SessionLocal()
    try:
        users     = db.query(User).order_by(User.id).all()
        watchlist = db.query(WatchlistItem).order_by(WatchlistItem.id).all()
        favorites = db.query(FavoriteItem).order_by(FavoriteItem.id).all()
        reviews   = db.query(Review).order_by(Review.id).all()
    finally:
        db.close()

    def make_table(title, headers, rows):
        header_html = "".join(f"<th>{h}</th>" for h in headers)
        rows_html = "".join(
            "<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>"
            for row in rows
        )
        return f"""
        <div class="section">
            <h2>{title} <span class="badge">{len(rows)}</span></h2>
            <div class="table-wrap">
                <table>
                    <thead><tr>{header_html}</tr></thead>
                    <tbody>{rows_html if rows else '<tr><td colspan="' + str(len(headers)) + '" class="empty">No data yet</td></tr>'}</tbody>
                </table>
            </div>
        </div>"""

    users_table = make_table("👤 Users", ["ID","Username","Email","Age","Gender","Genres"],
        [(u.id, u.username, u.email, u.age or "-", u.gender or "-", u.favorite_genres or "-") for u in users])

    watch_table = make_table("📋 Watchlist", ["ID","User ID","Movie ID","Movie Title"],
        [(w.id, w.user_id, w.movie_id, w.movie_title) for w in watchlist])

    fav_table = make_table("❤️ Favorites", ["ID","User ID","Movie ID","Movie Title"],
        [(f.id, f.user_id, f.movie_id, f.movie_title) for f in favorites])

    rev_table = make_table("💬 Reviews", ["ID","User ID","Movie","Review","Sentiment"],
        [(r.id, r.user_id, r.movie_title, r.review_text[:60]+"...", r.sentiment) for r in reviews])

    return HTMLResponse(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CineAI Admin Dashboard</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', sans-serif; background: #0f0f1a; color: #e2e8f0; min-height: 100vh; }}
  header {{ background: linear-gradient(135deg,#6c3ef4,#e040fb); padding: 24px 32px; }}
  header h1 {{ font-size: 28px; font-weight: 700; }}
  header p  {{ opacity: 0.85; font-size: 14px; margin-top: 4px; }}
  .stats {{ display: flex; gap: 16px; padding: 24px 32px; flex-wrap: wrap; }}
  .stat {{ background: #1e1e3a; border-radius: 12px; padding: 16px 24px; flex: 1; min-width: 140px; text-align: center; border: 1px solid #2d2d50; }}
  .stat .num {{ font-size: 32px; font-weight: 700; color: #a78bfa; }}
  .stat .lbl {{ font-size: 13px; color: #94a3b8; margin-top: 4px; }}
  .section {{ margin: 0 32px 32px; }}
  .section h2 {{ font-size: 18px; margin-bottom: 12px; display: flex; align-items: center; gap: 10px; }}
  .badge {{ background: #6c3ef4; border-radius: 20px; padding: 2px 10px; font-size: 13px; }}
  .table-wrap {{ overflow-x: auto; border-radius: 12px; border: 1px solid #2d2d50; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
  thead {{ background: #1e1e3a; }}
  th {{ padding: 12px 16px; text-align: left; color: #a78bfa; font-weight: 600; white-space: nowrap; }}
  td {{ padding: 11px 16px; border-top: 1px solid #2d2d50; color: #cbd5e1; }}
  tr:hover td {{ background: #1e1e3a; }}
  .empty {{ text-align: center; color: #64748b; padding: 24px; }}
  footer {{ text-align: center; padding: 24px; color: #475569; font-size: 13px; }}
  .refresh {{ float: right; background: #6c3ef4; color: white; border: none; padding: 8px 16px;
              border-radius: 8px; cursor: pointer; font-size: 13px; text-decoration: none; }}
</style>
</head>
<body>
<header>
  <h1>🎬 CineAI Admin Dashboard</h1>
  <p>Live database viewer — PostgreSQL
     <a class="refresh" href="/admin?key={key}">🔄 Refresh</a>
  </p>
</header>
<div class="stats">
  <div class="stat"><div class="num">{len(users)}</div><div class="lbl">👤 Users</div></div>
  <div class="stat"><div class="num">{len(watchlist)}</div><div class="lbl">📋 Watchlist</div></div>
  <div class="stat"><div class="num">{len(favorites)}</div><div class="lbl">❤️ Favorites</div></div>
  <div class="stat"><div class="num">{len(reviews)}</div><div class="lbl">💬 Reviews</div></div>
</div>
{users_table}
{watch_table}
{fav_table}
{rev_table}
<footer>CineAI Admin Dashboard • Protected by secret key • Data from PostgreSQL</footer>
</body></html>""")
