"""
narrative-interpolation-engine.py — Narrative Interpolation Engine for GK BRAIN

Fills narrative gaps between posts to maintain story continuity.
Generates transition text explaining what happened between the last post and now.

Usage (from gk-brain.py):
    from narrative_interpolation_engine import get_gap_filler
    filler = get_gap_filler(previous_context, current_context)
"""

import os

BASE_DIR = os.path.dirname(__file__)

GAP_FILLERS_BY_TIME = {
    "morning_to_afternoon": [
        "In the quiet hours since the last entry, the artist had packed down the session, "
        "driven back through still roads, and let the morning's events settle.",
        "The morning dissolved into midday without ceremony — the drive back, the gear cleaned, "
        "the phone finally checked.",
    ],
    "afternoon_to_evening": [
        "The afternoon hours between were productive and unremarkable — "
        "the kind of time that only gains meaning in retrospect.",
        "In the gap: studio time, a few messages sent, food eaten standing up. "
        "The evening was already visible in the lowering light.",
    ],
    "evening_to_night": [
        "As the last entry faded, the evening deepened. The city changed register — "
        "quieter on some streets, louder on others.",
        "Between entries: the transition. The moment when the evening stops pretending "
        "to be daytime and becomes itself.",
    ],
    "night_to_morning": [
        "The dark hours passed in their own way — the session deepening, "
        "thoughts becoming sharper as the world slept.",
        "Between the last post and now: the longest hours. The kind you only know "
        "by living through them.",
    ],
    "general": [
        "In the hours between the last entry and now, the artist was absorbed in the work.",
        "Time passed the way it does when you're fully in it — without being noticed.",
        "The gap between entries was filled with the practical and the private.",
    ],
}


def _get_time_slot(context_str: str) -> str:
    """Infer rough time of day from context string."""
    lower = context_str.lower()
    if any(w in lower for w in ["morning", "dawn", "early", "sunrise"]):
        return "morning"
    elif any(w in lower for w in ["afternoon", "midday", "noon"]):
        return "afternoon"
    elif any(w in lower for w in ["evening", "dusk", "sunset"]):
        return "evening"
    elif any(w in lower for w in ["night", "midnight", "dark"]):
        return "night"
    return "general"


def get_gap_filler(previous_context: str, current_context: str) -> str:
    """
    Generate a brief transition text explaining what happened between posts.

    Args:
        previous_context: Text/context from the previous lore post.
        current_context: Text/context for the current lore cycle.

    Returns:
        Transition text string, or empty string if not needed.
    """
    try:
        import hashlib

        prev_time = _get_time_slot(previous_context)
        curr_time = _get_time_slot(current_context)

        if prev_time == curr_time and prev_time != "general":
            return ""  # Same time slot, no transition needed

        key = f"{prev_time}_to_{curr_time}"
        fillers = GAP_FILLERS_BY_TIME.get(key, GAP_FILLERS_BY_TIME["general"])

        # Deterministic selection
        combined = (previous_context[:20] + current_context[:20]).encode()
        idx = int(hashlib.md5(combined).hexdigest(), 16) % len(fillers)

        return fillers[idx]
    except Exception as e:
        print(f"[narrative-interpolation-engine] Error: {e}")
        return ""
