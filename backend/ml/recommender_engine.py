"""
Content-Based Movie Recommender
TF-IDF on movie overview + genres + keywords -> Cosine Similarity matrix
"""
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

MODEL_PATH = os.path.join(os.path.dirname(__file__), "recommender_model.joblib")
DATASET_PATH = os.path.join(os.path.dirname(__file__), "dataset", "movies.csv")


class RecommenderEngine:
    def __init__(self):
        self.movie_ids = []
        self.similarity_matrix = None
        self.id_to_idx = {}

        if os.path.exists(MODEL_PATH):
            try:
                data = joblib.load(MODEL_PATH)
                self.movie_ids = data["movie_ids"]
                self.similarity_matrix = data["similarity_matrix"]
                self.id_to_idx = {mid: i for i, mid in enumerate(self.movie_ids)}
                print(f"[OK] Recommender loaded: {len(self.movie_ids)} movies.")
            except Exception as e:
                print(f"[WARN] Recommender load error: {e}")
                self._train_from_dataset()
        else:
            self._train_from_dataset()

    def _train_from_dataset(self):
        if not os.path.exists(DATASET_PATH):
            print("[WARN] No dataset found for recommendations.")
            return
        try:
            df = pd.read_csv(DATASET_PATH)
            df = df.dropna(subset=["tmdb_id", "overview"])
            df["soup"] = (
                df["overview"].fillna("") + " " +
                df["genres"].fillna("") + " " +
                df["keywords"].fillna("")
            )
            tfidf = TfidfVectorizer(stop_words="english", max_features=5000)
            tfidf_matrix = tfidf.fit_transform(df["soup"])
            sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
            self.movie_ids = df["tmdb_id"].astype(int).tolist()
            self.similarity_matrix = sim
            self.id_to_idx = {mid: i for i, mid in enumerate(self.movie_ids)}
            joblib.dump({"movie_ids": self.movie_ids, "similarity_matrix": sim}, MODEL_PATH)
            print(f"[OK] Recommender trained & saved: {len(self.movie_ids)} movies.")
        except Exception as e:
            print(f"[WARN] Training failed: {e}")

    def get_similar(self, movie_id: int, limit: int = 12) -> list:
        if movie_id not in self.id_to_idx or self.similarity_matrix is None:
            return []
        idx = self.id_to_idx[movie_id]
        scores = list(enumerate(self.similarity_matrix[idx]))
        scores = sorted(scores, key=lambda x: x[1], reverse=True)
        top = [self.movie_ids[i] for i, _ in scores[1:limit+1]]
        return top
