"""
Entry point for the Movie Recommender PAD pipeline (Etapa M — BGE embeddings).

Usage:
    python main.py --data-dir ../ml-25m
    python main.py --data-dir ../ml-25m --model BAAI/bge-large-en-v1.5
    python main.py --data-dir ../ml-25m --all-movies
"""

import argparse

from src.preprocess import build_soup
from src.embeddings import get_embeddings, DEFAULT_MODEL
from src.recommender import build_cosine_matrix
from src.benchmark import run_benchmark


def main():
    parser = argparse.ArgumentParser(
        description="Movie recommender using BGE dense embeddings (Etapa M)."
    )
    parser.add_argument(
        "--data-dir",
        default="../ml-25m",
        help="Path to the MovieLens ml-25m directory (default: ../ml-25m)",
    )
    parser.add_argument(
        "--cache",
        default="embeddings_bge.npy",
        help="Path for the embeddings cache file (default: embeddings_bge.npy)",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Sentence-transformers model to use (default: {DEFAULT_MODEL}). "
             "Use BAAI/bge-large-en-v1.5 for higher quality (requires ~15h on CPU).",
    )
    parser.add_argument(
        "--all-movies",
        action="store_true",
        help="Embed all 62k movies including genre-only entries (slow on CPU).",
    )
    args = parser.parse_args()

    print(f"[main] Loading data from: {args.data_dir}")
    df = build_soup(args.data_dir)

    # By default, restrict to movies with genome-tag coverage.
    # Genre-only soup (~48k movies) provides insufficient semantic signal for
    # dense embeddings; the benchmark title (The Prestige) has genome-tags.
    if not args.all_movies:
        df_embed = df[df["has_genome_tags"]].copy().reset_index(drop=True)
        print(f"[main] Embedding {len(df_embed)} movies with genome-tag coverage "
              f"(use --all-movies to include all {len(df)} movies).")
    else:
        df_embed = df

    embeddings = get_embeddings(df_embed, cache_path=args.cache, model_name=args.model)

    cosine_sim = build_cosine_matrix(embeddings)

    run_benchmark(df_embed, cosine_sim, model_name=args.model)


if __name__ == "__main__":
    main()
