"""
Qualitative benchmark comparing BGE recommendations for The Prestige (2006)
against the IMDb 'More Like This' reference list.
"""

import pandas as pd
from src.recommender import get_recommendations

# IMDb "More Like This" list for The Prestige (2006)  - used as qualitative ground truth
IMDB_PRESTIGE = [
    "The Dark Knight (2008)",
    "Memento (2000)",
    "Inception (2010)",
    "The Dark Knight Rises (2012)",
    "Interstellar (2014)",
    "Batman Begins (2005)",
    "The Departed (2006)",
    "The Shawshank Redemption (1994)",
    "Schindler's List (1993)",
    "Pulp Fiction (1994)",
]

# The Prestige as stored in MovieLens (article moved to end)
PRESTIGE_TITLE = "Prestige, The (2006)"


def run_benchmark(df: pd.DataFrame, cosine_sim, top_n: int = 10, model_name: str = "BGE") -> None:
    """
    Runs get_recommendations for The Prestige (2006) and prints:
      1. BGE top-N results (title, genres, similarity score)
      2. IMDb reference list
      3. Overlap count between the two lists
      4. Contextual note comparing against FMF LSA results
    """
    print("\n" + "=" * 60)
    print(f"BENCHMARK: {PRESTIGE_TITLE}")
    print("=" * 60)

    recs = get_recommendations(PRESTIGE_TITLE, df, cosine_sim, top_n=top_n)

    print(f"\n[{model_name}] Top-{top_n} recommendations:")
    print(f"{'Rank':<5} {'Title':<45} {'Genres':<35} {'Score'}")
    print("-" * 100)
    for _, row in recs.iterrows():
        print(f"{int(row['rank']):<5} {row['title']:<45} {row['genres']:<35} {row['similarity_score']:.4f}")

    print(f"\n[IMDb 'More Like This' reference list for The Prestige (2006)]:")
    for i, title in enumerate(IMDB_PRESTIGE, start=1):
        print(f"  {i:>2}. {title}")

    # Normalize titles for comparison (lowercase, strip whitespace)
    bge_titles_lower = set(t.lower().strip() for t in recs["title"])
    imdb_titles_lower = set(t.lower().strip() for t in IMDB_PRESTIGE)
    overlap = bge_titles_lower & imdb_titles_lower
    print(f"\n[Overlap] BGE top-{top_n} vs IMDb list: {len(overlap)}/{len(IMDB_PRESTIGE)} titles in common")
    if overlap:
        for t in sorted(overlap):
            print(f"  ✓ {t}")

    print("\n[Context  - FMF LSA comparison]")
    print(
        "The FMF LSA model (trained on IMDb metadata including directors, writers, and cast) "
        "placed The Dark Knight (2008), Memento (2000), Inception (2010), "
        "The Dark Knight Rises (2012), Batman Begins (2005), and Interstellar (2014) "
        "in its top-7 results for The Prestige  - capturing Christopher Nolan's directorial "
        "fingerprint across films. BGE embeddings here operate solely on genre and genome-tag "
        "soup (thematic/semantic descriptors), without access to cast or director metadata, "
        "so results reflect content similarity rather than auteur similarity."
    )
    print("=" * 60 + "\n")
