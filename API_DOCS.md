# CineAI API Documentation

## Base URL
- Local: `http://localhost:8000`
- Production: `https://your-backend.onrender.com`

## Authentication
All protected endpoints require a JWT Bearer token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```
Tokens are obtained from `/auth/login` or `/auth/register`.

---

## 🔐 Auth Endpoints

### POST /auth/register
Register a new user.

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```
**Response:** `201`
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": { "id": 1, "username": "john", "email": "john@example.com", "favorite_genres": "" }
}
```

---

### POST /auth/login
Login with email and password.

**Request Body:**
```json
{ "email": "string", "password": "string" }
```
**Response:** Same as register

---

### GET /auth/me ✅ Protected
Get current authenticated user profile.

**Response:**
```json
{ "id": 1, "username": "john", "email": "john@example.com", "favorite_genres": "Action,Drama" }
```

---

### PUT /auth/genres ✅ Protected
Update user's favorite genres.

**Request Body:**
```json
{ "genres": ["Action", "Drama", "Sci-Fi"] }
```

---

## 🎬 Movies Endpoints

### GET /movies/trending
Returns weekly trending movies from TMDB.

**Query Params:** `page` (default: 1)

**Response:** TMDB paginated results object with `results[]` array.

---

### GET /movies/top-rated
Top rated movies.

**Query Params:** `page`

---

### GET /movies/popular
Popular movies.

**Query Params:** `page`

---

### GET /movies/by-genre
Movies filtered by genre.

**Query Params:**
- `genre` (string): action, comedy, drama, thriller, science fiction, horror, romance, animation, fantasy, crime, war, music, family, history, mystery, western
- `page` (default: 1)

---

### GET /movies/search
Advanced search and filter.

**Query Params:**
- `query` (string, optional): text search
- `genre` (string, optional): genre filter
- `source` (string, optional): hollywood, bollywood, anime, korean, french, spanish, tamil, telugu
- `min_rating` (float, optional): minimum vote_average (1-10)
- `max_rating` (float, optional): maximum vote_average (1-10)
- `year_from` (int, optional): from release year
- `year_to` (int, optional): to release year
- `page` (default: 1)

---

### GET /movies/{movie_id}
Full movie detail including videos, credits, similar movies.

**Response:** TMDB movie detail object with `videos`, `credits`, `similar` appended.

---

### GET /movies/{movie_id}/videos
Movie trailer and video clips.

---

## 🤖 Recommendations Endpoints

### GET /recommendations/for-movie/{movie_id}
ML-based content similar movies.

**Query Params:** `limit` (default: 12)

**Response:**
```json
{
  "results": [...movies],
  "source": "ml_content_based"
}
```

---

### GET /recommendations/personalized ✅ Protected
Personalized recommendations based on saved genre preferences.

**Query Params:** `page`, `limit` (default: 20)

**Response:**
```json
{
  "results": [...movies],
  "source": "personalized",
  "genres_used": ["Action", "Drama"]
}
```

---

### GET /recommendations/trending-ai
AI-scored trending movies (vote_average × log(vote_count)).

---

## 💬 Sentiment Endpoints

### POST /sentiment/analyze
Analyze sentiment of any text (no auth required).

**Request Body:**
```json
{ "text": "This movie was absolutely amazing!" }
```
**Response:**
```json
{
  "sentiment": "positive",
  "score": 0.87,
  "confidence": 0.92,
  "vader_compound": 0.75
}
```

---

### POST /sentiment/review ✅ Protected
Submit a movie review and get sentiment analysis. Saves to database.

**Request Body:**
```json
{
  "movie_id": 27205,
  "movie_title": "Inception",
  "review_text": "A mind-bending masterpiece!"
}
```
**Response:**
```json
{
  "review_id": 1,
  "sentiment": "positive",
  "score": 0.92,
  "confidence": 0.88,
  "message": "Your review is classified as POSITIVE"
}
```

---

### GET /sentiment/reviews/{movie_id}
Get all reviews and sentiment aggregation for a movie.

**Response:**
```json
{
  "total": 25,
  "positive": 18,
  "negative": 4,
  "neutral": 3,
  "sentiment_score": 56.0,
  "reviews": [...]
}
```

---

## 📌 Watchlist Endpoints

### GET /watchlist/ ✅ Protected
Get user's watchlist.

### POST /watchlist/add ✅ Protected
Add a movie to watchlist.

**Request Body:**
```json
{
  "movie_id": 27205,
  "movie_title": "Inception",
  "poster_path": "/path.jpg",
  "vote_average": 8.4,
  "genre_ids": [28, 878, 53]
}
```

### DELETE /watchlist/remove/{movie_id} ✅ Protected
Remove from watchlist.

### GET /watchlist/check/{movie_id} ✅ Protected
Check if movie is in watchlist.

**Response:** `{ "in_watchlist": true }`

---

## ❤️ Favorites Endpoints

### GET /favorites/ ✅ Protected
### POST /favorites/add ✅ Protected  (same body as watchlist)
### DELETE /favorites/remove/{movie_id} ✅ Protected
### GET /favorites/check/{movie_id} ✅ Protected

**Check Response:** `{ "in_favorites": true }`

---

## ❌ Error Responses

| Status | Meaning |
|---|---|
| 400 | Bad Request — invalid input |
| 401 | Unauthorized — invalid/expired token |
| 404 | Not Found |
| 409 | Conflict — duplicate entry |
| 422 | Unprocessable Entity — validation error |
| 500 | Internal Server Error |

**Error Format:**
```json
{ "detail": "Error message here" }
```
