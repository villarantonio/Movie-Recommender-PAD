"""
Loads MovieLens ml-25m data and builds the 'soup' feature column used for embeddings.
Replicates the feature engineering from the FMF reference notebook
(Content_Based_Movie_Recommendation_System.ipynb).
"""

import os
import pandas as pd


def build_soup(data_dir: str) -> pd.DataFrame:
    """
    Loads movies.csv, genome-scores.csv, genome-tags.csv and links.csv
    from data_dir. Returns a DataFrame with columns:
      movieId, title, genres, soup, imdbId

    Movies without genome-tag coverage (~48k of 62k) fall back to genre-only soup.
    This mirrors the FMF main notebook's behavior for cold-start titles.
    """
    movies = pd.read_csv(os.path.join(data_dir, "movies.csv"))
    genome_scores = pd.read_csv(os.path.join(data_dir, "genome-scores.csv"))
    genome_tags = pd.read_csv(os.path.join(data_dir, "genome-tags.csv"))
    links = pd.read_csv(os.path.join(data_dir, "links.csv"))

    # Build genre strings: split on "|", replace spaces with underscores
    movies["genres_str"] = movies["genres"].apply(
        lambda g: " ".join(tok.replace(" ", "_") for tok in g.split("|"))
        if g != "(no genres listed)"
        else ""
    )

    # Build genome-tag strings: keep only high-relevance tags (FMF threshold: > 0.5)
    merged = genome_scores.merge(genome_tags, on="tagId")
    high_relevance = merged[merged["relevance"] > 0.5]
    tag_strings = (
        high_relevance.groupby("movieId")["tag"]
        .apply(lambda tags: " ".join(tags))
        .reset_index()
        .rename(columns={"tag": "tag_str"})
    )

    movies = movies.merge(tag_strings, on="movieId", how="left")

    # Combine: genome tags first, then genres (matches FMF ordering)
    def make_soup(row):
        parts = []
        if pd.notna(row["tag_str"]) and row["tag_str"]:
            parts.append(row["tag_str"])
        if row["genres_str"]:
            parts.append(row["genres_str"])
        return " ".join(parts)

    movies["soup"] = movies.apply(make_soup, axis=1)

    n_with_tags = movies["tag_str"].notna().sum()
    n_genre_only = len(movies) - n_with_tags
    print(f"[preprocess] {n_with_tags} movies with genome-tags, "
          f"{n_genre_only} movies using genre-only soup.")

    movies["has_genome_tags"] = movies["tag_str"].notna()

    links = links[["movieId", "imdbId"]]
    result = movies.merge(links, on="movieId", how="left")
    result = result[["movieId", "title", "genres", "soup", "has_genome_tags", "imdbId"]].reset_index(drop=True)
    return result
