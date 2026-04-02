"""
Train & Save Sentiment Model (Logistic Regression + TF-IDF pipeline)
Run: python train_sentiment.py
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import joblib
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import re

nltk.download('stopwords', quiet=True)
nltk.download('vader_lexicon', quiet=True)

DATASET_PATH = os.path.join(os.path.dirname(__file__), "dataset", "reviews.csv")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "sentiment_model.joblib")


def clean_text(text: str) -> str:
    text = str(text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[^\w\s!?.,]', ' ', text)
    return text.strip().lower()


def train():
    if not os.path.exists(DATASET_PATH):
        print(f"[ERROR] Dataset not found at {DATASET_PATH}")
        return

    df = pd.read_csv(DATASET_PATH)
    df = df.dropna(subset=["review_text", "sentiment"])
    df["clean_text"] = df["review_text"].apply(clean_text)

    print(f"[INFO] Dataset size: {len(df)} reviews")
    print(f"[INFO] Label distribution:\n{df['sentiment'].value_counts()}")

    X = df["clean_text"]
    y = df["sentiment"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=10000,
            stop_words="english",
            sublinear_tf=True
        )),
        ("clf", LogisticRegression(
            C=5.0,
            max_iter=500,
            class_weight="balanced",
            solver="lbfgs"
        ))
    ])

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    print("\n[REPORT] Classification Report:")
    print(classification_report(y_test, y_pred))

    joblib.dump(pipeline, MODEL_PATH)
    print(f"[OK] Sentiment model saved to {MODEL_PATH}")


if __name__ == "__main__":
    train()
