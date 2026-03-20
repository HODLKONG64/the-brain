"""
keyword-ranking-engine.py — GK BRAIN Keyword Ranking Engine

Extracts and ranks keywords from GK BRAIN lore documents using TF-IDF.
Checks GKniftyHEADS Fandom wiki coverage for each top keyword.
Returns structured results usable by gk-brain.py.

Usage:
    from keyword_ranking_engine import rank_keywords
    results = rank_keywords(documents)
"""

import os
import re
import requests
from sklearn.feature_extraction.text import TfidfVectorizer

FANDOM_WIKI_BASE = "https://gkniftyheads.fandom.com/wiki/"
TOP_N = 30  # number of keywords to return


def _check_fandom_coverage(keyword: str) -> bool:
    """Check if a keyword has a dedicated GKniftyHEADS Fandom wiki page."""
    slug = keyword.strip().replace(" ", "_").title()
    url = FANDOM_WIKI_BASE + slug
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; GKBrainBot/1.0; "
            "+https://github.com/HODLKONG64/the-brain)"
        )
    }
    try:
        resp = requests.head(url, headers=headers, timeout=10, allow_redirects=True)
        return resp.status_code == 200
    except Exception:
        return False


def rank_keywords(documents: list, top_n: int = TOP_N, check_wiki: bool = False) -> list:
    """
    Extract and rank keywords from a list of text documents using TF-IDF.

    Args:
        documents: List of text strings (lore files, character bible, etc.)
        top_n: Number of top keywords to return.
        check_wiki: If True, check GKniftyHEADS Fandom wiki coverage (slow).

    Returns:
        List of dicts: [{"keyword": str, "weight": float, "wiki_coverage": bool|None}]
    """
    if not documents or not any(d.strip() for d in documents):
        return []

    # Filter to GK-relevant tokens only (min 3 chars, alphabetic or hyphenated)
    vectorizer = TfidfVectorizer(
        max_features=500,
        stop_words="english",
        token_pattern=r"(?u)\b[A-Za-z][A-Za-z-]{2,}\b",
        ngram_range=(1, 2),
    )
    try:
        tfidf_matrix = vectorizer.fit_transform(documents)
    except ValueError:
        return []

    feature_names = vectorizer.get_feature_names_out()
    importance = tfidf_matrix.sum(axis=0).A1
    ranked = sorted(zip(feature_names, importance), key=lambda x: x[1], reverse=True)
    top = ranked[:top_n]

    results = []
    for keyword, weight in top:
        wiki_coverage = None
        if check_wiki:
            wiki_coverage = _check_fandom_coverage(keyword)
        results.append({
            "keyword": keyword,
            "weight": round(float(weight), 4),
            "wiki_coverage": wiki_coverage,
        })

    return results


if __name__ == "__main__":
    import json
    sample = [
        "GraffPUNKS Crypto Moonboys BlockTopia HODL Warriors Lady-INK lore graffiti",
        "Bitcoin Kids factions Hash-Guilds Hardfork Games bonnet parkour fisherman",
    ]
    print(json.dumps(rank_keywords(sample, top_n=10), indent=2))