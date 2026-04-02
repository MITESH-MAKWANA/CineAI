"""
Train & Save Recommender Model
Run: python train_recommender.py
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATASET_PATH = os.path.join(os.path.dirname(__file__), 'dataset', 'movies.csv')
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'recommender_model.joblib')


def train():
    if not os.path.exists(DATASET_PATH):
        print(f'❌ Dataset not found at {DATASET_PATH}')
        return

    df = pd.read_csv(DATASET_PATH)
    df = df.dropna(subset=['tmdb_id', 'overview'])

    print(f'📊 Dataset size: {len(df)} movies')

    df['soup'] = (
        df['overview'].fillna('') + ' ' +
        df['genres'].fillna('') + ' ' +
        df['keywords'].fillna('')
    )

    tfidf = TfidfVectorizer(
        stop_words='english',
        max_features=5000,
        ngram_range=(1, 2),
        sublinear_tf=True
    )
    tfidf_matrix = tfidf.fit_transform(df['soup'])
    sim_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

    movie_ids = df['tmdb_id'].astype(int).tolist()

    data = {'movie_ids': movie_ids, 'similarity_matrix': sim_matrix}
    joblib.dump(data, MODEL_PATH)

    print(f'✅ Recommender model saved to {MODEL_PATH}')
    print(f'   Matrix shape: {sim_matrix.shape}')

    # Quick test
    from ml.recommender_engine import RecommenderEngine
    rec = RecommenderEngine()
    test_id = movie_ids[0]
    similar = rec.get_similar(test_id, 5)
    print(f'   Test — Similar to movie {test_id}: {similar}')


if __name__ == '__main__':
    train()
