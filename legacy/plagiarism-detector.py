"""
plagiarism-detector.py - Plagiarism Detector for GK BRAIN

Prevents unintended copying from source materials by detecting high
overlap between generated lore and source update content.

Usage (from gk-brain.py):
    from plagiarism_detector import check_originality
    result = check_originality(lore_text, updates)
"""

import os

BASE_DIR = os.path.dirname(__file__)

SIMILARITY_THRESHOLD = 0.40


def _ngrams(text: str, n: int = 4) -> set:
    """Generate word n-grams from text."""
    words = text.lower().split()
    if len(words) < n:
        return set()
    return {" ".join(words[i:i+n]) for i in range(len(words) - n + 1)}


def _similarity_score(text_a: str, text_b: str) -> float:
    """Calculate n-gram overlap similarity between two texts."""
    try:
        if not text_a or not text_b:
            return 0.0
        grams_a = _ngrams(text_a)
        grams_b = _ngrams(text_b)
        if not grams_a or not grams_b:
            return 0.0
        overlap = grams_a & grams_b
        return len(overlap) / max(len(grams_a), 1)
    except Exception:
        return 0.0


def check_originality(lore_text: str, updates: list) -> dict:
    """
    Check generated lore for excessive similarity with source update content.

    Flags if more than 40% n-gram overlap exists with any single source.

    Args:
        lore_text: Generated lore string to check.
        updates: List of update dicts used in generation.

    Returns:
        Dict with: original (bool), similarity_scores (dict), max_similarity (float).
    """
    try:
        if not updates or not lore_text:
            return {"original": True, "similarity_scores": {}, "max_similarity": 0.0}

        similarity_scores = {}
        for u in updates:
            source_text = (u.get("content", "") or u.get("title", "") or "")
            if not source_text or len(source_text) < 20:
                continue
            url = u.get("url", "") or u.get("source", "") or f"update_{len(similarity_scores)}"
            key = url[:50]
            similarity_scores[key] = round(_similarity_score(lore_text, source_text), 3)

        max_sim = max(similarity_scores.values()) if similarity_scores else 0.0
        original = max_sim < SIMILARITY_THRESHOLD

        if not original:
            flagged = [k for k, v in similarity_scores.items() if v >= SIMILARITY_THRESHOLD]
            print(f"[plagiarism-detector] High similarity detected: {flagged}")

        return {
            "original": original,
            "similarity_scores": similarity_scores,
            "max_similarity": round(max_sim, 3),
        }
    except Exception as e:
        print(f"[plagiarism-detector] Error: {e}")
        return {"original": True, "similarity_scores": {}, "max_similarity": 0.0}
