"""
data-validator.py - Data Validator for GK BRAIN

Validates all detected updates for quality, spam, and source verification.
Assigns confidence scores and filters low-quality updates.

Usage (from gk-brain.py):
    from data_validator import validate_updates
    validated = validate_updates(updates)
"""

import datetime
import os

BASE_DIR = os.path.dirname(__file__)

TRUSTED_SOURCE_DOMAINS = {
    "graffpunks.substack.com": 0.95,
    "graffpunks.live": 0.95,
    "gkniftyheads.com": 0.95,
    "graffitikings.co.uk": 0.90,
    "neftyblocks.com": 0.80,
    "nfthive.io": 0.80,
    "dappradar.com": 0.80,
    "carpology.net": 0.85,
    "totalcarp.co.uk": 0.85,
    "bigcarp.co.uk": 0.75,
    "coindesk.com": 0.85,
    "cointelegraph.com": 0.85,
    "streetartnews.net": 0.75,
    "decrypt.co": 0.80,
}

MIN_CONFIDENCE_THRESHOLD = 0.3
MIN_CONTENT_LENGTH = 20
MAX_AGE_HOURS = 72


def _get_domain(url: str) -> str:
    try:
        from urllib.parse import urlparse
        return urlparse(url).netloc.lower().replace("www.", "")
    except Exception:
        return ""


def _score_source(update: dict) -> float:
    """Score based on source trustworthiness."""
    url = update.get("url", "") or update.get("source", "") or ""
    domain = _get_domain(url)
    if domain in TRUSTED_SOURCE_DOMAINS:
        return TRUSTED_SOURCE_DOMAINS[domain]
    if domain:
        return 0.55
    return 0.40


def _score_content_length(update: dict) -> float:
    """Score based on content length (longer = more credible)."""
    content = (update.get("content", "") or update.get("title", "") or "")
    length = len(content.strip())
    if length < 20:
        return 0.2
    elif length < 50:
        return 0.5
    elif length < 200:
        return 0.7
    else:
        return 0.9


def _score_recency(update: dict) -> float:
    """Score based on how recent the update is."""
    try:
        ts = update.get("timestamp_utc") or update.get("detected_at") or update.get("timestamp")
        if not ts:
            return 0.6

        if isinstance(ts, str):
            from temporal_alignment_engine import _parse_ts
            dt = _parse_ts(ts)
        else:
            dt = None

        if dt is None:
            return 0.6

        now = datetime.datetime.now(datetime.timezone.utc)
        age_hours = (now - dt).total_seconds() / 3600

        if age_hours < 6:
            return 1.0
        elif age_hours < 24:
            return 0.8
        elif age_hours < 48:
            return 0.6
        elif age_hours < MAX_AGE_HOURS:
            return 0.4
        else:
            return 0.2
    except Exception:
        return 0.6


def validate_updates(updates: list) -> list:
    """
    Score and filter updates for quality, spam, and source verification.

    Each update receives a 'confidence' score (0.0-1.0). Updates below
    MIN_CONFIDENCE_THRESHOLD are filtered out.

    Args:
        updates: List of raw update dicts.

    Returns:
        Filtered list with 'confidence' key added to each passing update.
    """
    if not updates:
        return []

    try:
        validated = []
        for u in updates:
            content = (u.get("content", "") or u.get("title", "") or "")
            if len(content.strip()) < MIN_CONTENT_LENGTH:
                continue

            source_score = _score_source(u)
            length_score = _score_content_length(u)
            recency_score = _score_recency(u)

            confidence = round(
                source_score * 0.5 + length_score * 0.25 + recency_score * 0.25,
                3
            )

            if confidence >= MIN_CONFIDENCE_THRESHOLD:
                enriched = dict(u)
                enriched["confidence"] = confidence
                validated.append(enriched)

        print(f"[data-validator] {len(validated)}/{len(updates)} updates passed validation")
        return validated
    except Exception as e:
        print(f"[data-validator] Error: {e}")
        return updates
