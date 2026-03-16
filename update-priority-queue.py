"""
update-priority-queue.py - Update Priority Queue for GK BRAIN

Intelligent priority queue for processing updates in optimal order.
Scores and sorts updates based on relevance, freshness, and arc alignment.

Usage (from gk-brain.py):
    from update_priority_queue import prioritize_updates
    ordered = prioritize_updates(updates, rule_ctx)
"""

import datetime
import json
import os

BASE_DIR = os.path.dirname(__file__)
QUEUE_FILE = os.path.join(BASE_DIR, "priority-queue.json")

IMPORTANCE_SCORES = {
    "gkdata-real": 4,
    "fishing-real": 3,
    "rave-real": 3,
    "graffiti-news-real": 3,
    "news-real": 2,
    "parkour-real": 2,
    "crypto-real": 2,
    "art-real": 2,
    "meta-real": 1,
}

BLOCK_CATEGORY_AFFINITY = {
    "morning": ["fishing-real", "gkdata-real"],
    "afternoon": ["news-real", "crypto-real", "gkdata-real"],
    "evening": ["rave-real", "graffiti-news-real"],
    "night": ["rave-real", "gkdata-real", "art-real"],
}


def _freshness_score(update: dict) -> float:
    """Score 0-3 based on recency."""
    try:
        ts_str = update.get("timestamp_utc") or update.get("detected_at") or update.get("timestamp")
        if not ts_str:
            return 1.0
        now = datetime.datetime.now(datetime.timezone.utc)

        from temporal_alignment_engine import _parse_ts, _make_aware
        dt = _make_aware(_parse_ts(str(ts_str)))
        if dt is None:
            return 1.0

        age_hours = (now - dt).total_seconds() / 3600
        if age_hours < 6:
            return 3.0
        elif age_hours < 24:
            return 2.0
        elif age_hours < 48:
            return 1.0
        else:
            return 0.0
    except Exception:
        return 1.0


def prioritize_updates(updates: list, rule_ctx: dict) -> list:
    """
    Score and sort updates in priority order for narrative generation.

    Scoring factors:
    - Calendar/block relevance: +5 if category matches current block
    - Freshness: 0-3 points based on age
    - Category importance: 1-4 points
    - Confidence: 0-2 bonus points

    Args:
        updates: List of validated update dicts.
        rule_ctx: Current rule context dict.

    Returns:
        Updates sorted by priority score (highest first).
    """
    try:
        block = rule_ctx.get("block", "afternoon")
        affinity_cats = BLOCK_CATEGORY_AFFINITY.get(block, [])

        scored = []
        for u in updates:
            score = 0.0
            cat = u.get("category", "")

            if cat in affinity_cats:
                score += 5

            score += IMPORTANCE_SCORES.get(cat, 1)
            score += _freshness_score(u)
            score += float(u.get("confidence", 0.5)) * 2

            scored.append((score, u))

        scored.sort(key=lambda x: x[0], reverse=True)
        ordered = [u for _, u in scored]

        return ordered
    except Exception as e:
        print(f"[priority-queue] Error: {e}")
        return updates
