"""
Loads MovieLens ml-25m data and builds the 'soup' feature column used for embeddings.
Replicates the feature engineering from the FMF reference notebook
(Content_Based_Movie_Recommendation_System.ipynb).
"""

import os
import pandas as pd


def _find_file(directory, basename):
    for ext in (".tsv.gz", ".tsv"):
        p = os.path.join(directory, basename + ext)
        if os.path.exists(p):
            return p
    raise FileNotFoundError(f"{basename}(.tsv.gz|.tsv) nao encontrado em {directory}")


def load_imdb_people(imdb_dir: str) -> pd.DataFrame:
    principals_path = _find_file(imdb_dir, "title.principals")
    names_path = _find_file(imdb_dir, "name.basics")

    keep_categories = {"director", "writer", "actor", "actress"}

    # title.principals has ~60M rows — read in chunks and filter early to save memory
    chunks = []
    for chunk in pd.read_csv(
        principals_path,
        sep="\t",
        usecols=["tconst", "ordering", "nconst", "category"],
        chunksize=500_000,
        dtype=str,
        na_values="\\N",
    ):
        chunk = chunk[chunk["category"].isin(keep_categories)]
        mask_cast = chunk["category"].isin({"actor", "actress"})
        # Keep all directors/writers; limit cast to top-3 billed (ordering <= 3)
        chunk = pd.concat([
            chunk[~mask_cast],
            chunk[mask_cast][chunk[mask_cast]["ordering"].astype(int) <= 3],
        ])
        chunks.append(chunk)

    principals = pd.concat(chunks, ignore_index=True)

    names = pd.read_csv(
        names_path,
        sep="\t",
        usecols=["nconst", "primaryName"],
        dtype=str,
        na_values="\\N",
    )

    merged = principals.merge(names, on="nconst")
    merged["name_tok"] = merged["primaryName"].str.replace(" ", "_", regex=False)

    people_str = (
        merged.groupby("tconst")["name_tok"]
        .apply(lambda s: " ".join(s))
        .reset_index()
        .rename(columns={"name_tok": "people_str"})
    )
    print(f"[preprocess] IMDb people loaded: {len(people_str):,} titles with cast/crew data.")
    return people_str


def build_soup(data_dir: str, imdb_dir: str = None) -> pd.DataFrame:
    """
    Loads movies.csv, genome-scores.csv, genome-tags.csv and links.csv
    from data_dir. Returns a DataFrame with columns:
      movieId, title, genres, soup, has_genome_tags, imdbId

    If imdb_dir is provided, enriches the soup with director, writer and
    top-3 cast names from title.principals.tsv(.gz) and name.basics.tsv(.gz).
    Names are formatted with underscores (e.g. Christopher_Nolan) so the
    BGE model treats each person as a single token.

    Movies without genome-tag coverage (~48k of 62k) fall back to genre-only soup.
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

    if imdb_dir is not None:
        people = load_imdb_people(imdb_dir)
        # Convert imdbId (integer, no leading zeros) → tconst format: "tt" + 7-digit zero-padded
        result["tconst"] = result["imdbId"].dropna().astype(int).apply(
            lambda x: f"tt{x:07d}"
        )
        result = result.merge(people, on="tconst", how="left")
        n_enriched = result["people_str"].notna().sum()
        print(f"[preprocess] {n_enriched:,} movies enriched with IMDb cast/crew metadata.")
        result["soup"] = result.apply(
            lambda row: (row["soup"] + " " + row["people_str"])
            if pd.notna(row.get("people_str")) else row["soup"],
            axis=1,
        )
        result = result.drop(columns=["tconst", "people_str"])

    result = result[["movieId", "title", "genres", "soup", "has_genome_tags", "imdbId"]].reset_index(drop=True)
    return result
