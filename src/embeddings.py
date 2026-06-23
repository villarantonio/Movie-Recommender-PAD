"""
Generates and caches dense BGE embeddings for the movie soup column.
Uses sentence-transformers with a BGE model (no API key required).

Default model: BAAI/bge-small-en-v1.5 (33M params, 384-dim, ~20 min on CPU for 13k movies).
For higher quality at the cost of runtime: BAAI/bge-large-en-v1.5 (335M params, 1024-dim).
"""

import os
import time
import numpy as np

DEFAULT_MODEL = "BAAI/bge-small-en-v1.5"


def get_embeddings(
    df,
    cache_path: str = "embeddings_bge.npy",
    model_name: str = DEFAULT_MODEL,
) -> np.ndarray:
    """
    Generates BGE embeddings for df['soup']. Loads from cache_path if it exists;
    otherwise encodes all rows with model_name and saves to cache_path.
    Returns array of shape (n_movies, embedding_dim).
    """
    if os.path.exists(cache_path):
        print(f"[embeddings] Loading cache: {cache_path}")
        return np.load(cache_path)

    print(f"[embeddings] Generating embeddings with {model_name} ...")
    print(f"[embeddings] {len(df)} movies to encode — this may take several minutes on CPU.")
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(model_name)
    t0 = time.time()
    embeddings = model.encode(
        df["soup"].tolist(),
        batch_size=64,
        show_progress_bar=True,
        normalize_embeddings=True,  # BGE recommends normalization for cosine similarity
    )
    elapsed = time.time() - t0
    print(f"[embeddings] Done in {elapsed:.1f}s. Shape: {embeddings.shape}")
    np.save(cache_path, embeddings)
    return embeddings
