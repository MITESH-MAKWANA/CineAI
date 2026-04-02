"""
Sentiment Engine — VADER + Logistic Regression Hybrid
Trained on NLTK VADER lexicon + sklearn pipeline
"""
import os
import joblib
import re
import nltk

try:
    nltk.data.find('sentiment/vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

from nltk.sentiment.vader import SentimentIntensityAnalyzer

MODEL_PATH = os.path.join(os.path.dirname(__file__), "sentiment_model.joblib")


class SentimentEngine:
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
        self.ml_model = None
        if os.path.exists(MODEL_PATH):
            try:
                self.ml_model = joblib.load(MODEL_PATH)
                print("[OK] ML Sentiment model loaded from disk.")
            except Exception as e:
                print(f"[WARN] Could not load ML model: {e}")
        else:
            print("[INFO] No ML model found. Using VADER only.")

    def clean_text(self, text: str) -> str:
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'[^\w\s!?.,]', ' ', text)
        return text.strip().lower()

    def predict(self, text: str) -> dict:
        cleaned = self.clean_text(text)
        vader_scores = self.vader.polarity_scores(text)
        compound = vader_scores["compound"]

        if self.ml_model:
            try:
                ml_pred = self.ml_model.predict([cleaned])[0]
                ml_proba = self.ml_model.predict_proba([cleaned])[0]
                confidence = float(max(ml_proba))
                if compound >= 0.05:
                    vader_sentiment = "positive"
                elif compound <= -0.05:
                    vader_sentiment = "negative"
                else:
                    vader_sentiment = "neutral"
                if ml_pred == vader_sentiment:
                    final_sentiment = ml_pred
                    confidence = min(confidence * 1.1, 1.0)
                else:
                    final_sentiment = ml_pred
                score = (compound + 1) / 2
                return {
                    "sentiment": final_sentiment,
                    "score": round(score, 3),
                    "confidence": round(confidence, 3),
                    "vader_compound": compound,
                    "ml_prediction": ml_pred
                }
            except Exception as e:
                print(f"ML predict error: {e}")

        if compound >= 0.05:
            sentiment = "positive"
        elif compound <= -0.05:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        score = (compound + 1) / 2
        confidence = abs(compound)
        return {
            "sentiment": sentiment,
            "score": round(score, 3),
            "confidence": round(min(confidence, 1.0), 3),
            "vader_compound": compound
        }
