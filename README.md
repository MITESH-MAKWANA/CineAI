# 🎬 CineAI — AI-Powered Movie Recommendation & Sentiment Analysis Platform

> **Smart recommendations. Better entertainment.**  
> A full-stack, production-ready OTT-style platform with ML-powered movie recommendations and NLP sentiment analysis.



---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 AI Recommendations | Content-Based Filtering (TF-IDF + Cosine Similarity) |
| 💬 Sentiment Analysis | VADER + Logistic Regression hybrid NLP model |
| 🎬 TMDB Integration | Real-time movie data, posters, trailers |
| 🔐 JWT Auth | Secure register/login with bcrypt passwords |
| 📌 Watchlist & ❤️ Favorites | Persistent personal lists |
| 🔍 Smart Search | Filters by genre, source, rating, release year |
| 🌍 Global Cinema | Hollywood, Bollywood, Anime, K-Drama & more |
| 📱 Responsive UI | Netflix-inspired dark UI, works on all devices |

---

## 🗂️ Project Structure

```
CineAI/
├── backend/         # FastAPI Python backend
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── auth_utils.py
│   ├── routes/      # auth, movies, recommendations, sentiment, watchlist, favorites
│   ├── models/      # SQLAlchemy ORM models
│   ├── ml/          # Sentiment & Recommender engines + datasets
│   ├── .env.example
│   └── requirements.txt
│
└── frontend/        # React + Vite frontend
    ├── src/
    │   ├── api/         # Axios calls
    │   ├── context/     # AuthContext
    │   ├── components/  # Navbar, Footer, MovieCard, MovieRow, etc.
    │   └── pages/       # Home, Explore, MovieDetail, Login, Register, etc.
    ├── .env.example
    └── package.json
```

---

## 🚀 Quick Start (Local)

### Prerequisites
- Python 3.10+
- Node.js 18+
- A free [TMDB API Key](https://www.themoviedb.org/settings/api)

---

### 1️⃣ Backend Setup

```bash
cd CineAI/backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env      # Windows
cp .env.example .env        # Mac/Linux

# ⚠️  EDIT .env and add your TMDB_API_KEY

# (Optional) Pre-train the sentiment model
python ml/train_sentiment.py

# Run the backend server
uvicorn main:app --reload --port 8000
```

✅ Backend will be available at: https://cineai-ifyr.onrender.com
📖 API Docs (Swagger): https://cineai-ifyr.onrender.com/docs

---

### 2️⃣ Frontend Setup

```bash
cd CineAI/frontend

# Install dependencies
npm install

# Configure environment
copy .env.example .env      # Windows
cp .env.example .env        # Mac/Linux

# Start dev server
npm run dev
```

✅ Frontend will be available at: https://cineai-frontend.vercel.app

---

## 🔑 Environment Variables

### Backend (`backend/.env`)
```env
TMDB_API_KEY=your_tmdb_api_key_here
JWT_SECRET_KEY=your-super-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=10080
DATABASE_URL=sqlite:///./cineai.db
ALLOWED_ORIGINS=http://localhost:5173
```

### Frontend (`frontend/.env`)
```env
VITE_API_URL=http://localhost:8000
VITE_TMDB_IMAGE_BASE=https://image.tmdb.org/t/p
```

---

## 🧠 AI/ML Details

### Sentiment Analysis
- **Model**: TF-IDF Vectorizer + Logistic Regression (sklearn pipeline)
- **Booster**: VADER lexicon (NLTK) — handles negation, intensifiers
- **Classes**: `positive` | `negative` | `neutral`
- **Dataset**: `backend/ml/dataset/reviews.csv` (expandable)
- **Training**: `python ml/train_sentiment.py`
- **Output**: `backend/ml/sentiment_model.joblib`

### Content-Based Recommender
- **Method**: TF-IDF on movie overview + genres + keywords → Cosine Similarity matrix
- **Dataset**: `backend/ml/dataset/movies.csv` (seeded with 50 popular films)
- **Auto-train**: Runs on first server startup if model file not found
- **Output**: `backend/ml/recommender_model.joblib`

---

## 📡 API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | ❌ | Register new user |
| POST | `/auth/login` | ❌ | Login & get JWT |
| GET | `/auth/me` | ✅ | Get current user |
| PUT | `/auth/genres` | ✅ | Update genre preferences |
| GET | `/movies/trending` | ❌ | Trending movies |
| GET | `/movies/top-rated` | ❌ | Top rated movies |
| GET | `/movies/search` | ❌ | Search & filter movies |
| GET | `/movies/{id}` | ❌ | Movie detail + videos |
| GET | `/recommendations/for-movie/{id}` | ❌ | Similar movies (ML) |
| GET | `/recommendations/personalized` | ✅ | Personalized picks |
| POST | `/sentiment/analyze` | ❌ | Analyze text sentiment |
| POST | `/sentiment/review` | ✅ | Submit movie review |
| GET | `/sentiment/reviews/{id}` | ❌ | Get movie sentiment stats |
| GET | `/watchlist/` | ✅ | Get user watchlist |
| POST | `/watchlist/add` | ✅ | Add to watchlist |
| DELETE | `/watchlist/remove/{id}` | ✅ | Remove from watchlist |
| GET | `/favorites/` | ✅ | Get user favorites |
| POST | `/favorites/add` | ✅ | Add to favorites |
| DELETE | `/favorites/remove/{id}` | ✅ | Remove from favorites |

---

## 🌐 Deployment

### Frontend → Vercel
```bash
cd frontend
npm run build

# Deploy via Vercel CLI
npx vercel --prod

# Or connect GitHub repo to vercel.com dashboard
# Set environment variable: VITE_API_URL=https://your-backend.onrender.com
```

### Backend → Render
1. Create a new **Web Service** on [render.com](https://render.com)
2. Connect your GitHub repo, set Root Directory to `backend/`
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn main:app --host 0.0.0.0 --port 10000`
5. Add all environment variables from `.env`

### Backend → Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

cd backend
railway login
railway init
railway up
```

---

## 🗄️ Database

- **Local**: SQLite (`backend/cineai.db`) — zero config, auto-created on startup
- **Production**: Swap `DATABASE_URL` to PostgreSQL URL (Render/Railway provide free PostgreSQL)

---

## 📁 Pages Overview

| Page | Route | Auth Required |
|---|---|---|
| Home | `/` | ❌ |
| Login | `/login` | ❌ |
| Register | `/register` | ❌ |
| Genre Select | `/genre-select` | ✅ |
| Explore | `/explore` | ❌ |
| Movie Detail | `/movie/:id` | ❌ |
| Favorites | `/favorites` | ✅ |
| Watchlist | `/watchlist` | ✅ |
| About | `/about` | ❌ |
| Contact | `/contact` | ❌ |

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m 'Add my feature'`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 🙏 Acknowledgements

- [TMDB](https://www.themoviedb.org/) for the incredible movie database API
- [FastAPI](https://fastapi.tiangolo.com/) for the blazing-fast Python backend
- [scikit-learn](https://scikit-learn.org/) for the ML toolkit
- [NLTK](https://www.nltk.org/) for natural language processing

---

*© 2026 CineAI — Powered by AI & Machine Learning*
