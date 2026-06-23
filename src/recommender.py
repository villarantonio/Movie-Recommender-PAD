"""
Cosine similarity computation and top-N recommendation retrieval.
Uses sklearn.metrics.pairwise.cosine_similarity, consistent with the FMF reference.
"""

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


def build_cosine_matrix(embeddings: np.ndarray) -> np.ndarray:
    """
    Returns the normalized embeddings to be used for on-demand cosine similarity.

    A full (n x n) similarity matrix for 62k movies would require ~14 GB of RAM,
    so similarity is computed per query in get_recommendations instead.
    For datasets with fewer than 20k movies the full matrix could be materialized,
    but this implementation keeps memory usage constant regardless of catalog size.
    """
    n = len(embeddings)
    if n > 20_000:
        print(
            f"[recommender] {n} movies detected — using on-demand similarity "
            "(full matrix would require ~{:.0f} GB RAM).".format(n * n * 4 / 1e9)
        )
    return embeddings


def get_recommendations(
    title: str,
    df: pd.DataFrame,
    cosine_sim: np.ndarray,
    top_n: int = 10,
) -> pd.DataFrame:
    """
    Returns the top_n most similar movies to the given title.

    cosine_sim may be either:
      - a (n, embedding_dim) array of normalized embeddings (on-demand mode), or
      - a full (n, n) precomputed similarity matrix.

    Raises ValueError if the title is not found in df['title'].
    Result columns: rank, title, genres, similarity_score.
    """
    title_to_idx = dict(zip(df["title"], df.index))
    if title not in title_to_idx:
        raise ValueError(
            f"Title '{title}' not found. "
            "Check exact spelling including year, e.g. 'Prestige, The (2006)'."
        )

    idx = title_to_idx[title]

    # Detect whether cosine_sim is a full matrix (n×n) or embeddings (n×d, d≠n)
    n = len(df)
    if cosine_sim.ndim == 2 and cosine_sim.shape == (n, n):
        sim_scores = cosine_sim[idx]
    else:
        # On-demand: compute similarity for this single query
        sim_scores = cosine_similarity(cosine_sim[[idx]], cosine_sim)[0]

    # Sort descending, skip self (score == 1.0 at position idx)
    ranked = sorted(enumerate(sim_scores), key=lambda x: x[1], reverse=True)
    ranked = [(i, s) for i, s in ranked if i != idx][:top_n]

    rows = []
    for rank, (movie_idx, score) in enumerate(ranked, start=1):
        rows.append({
            "rank": rank,
            "title": df.loc[movie_idx, "title"],
            "genres": df.loc[movie_idx, "genres"],
            "similarity_score": round(float(score), 4),
        })

    return pd.DataFrame(rows)
