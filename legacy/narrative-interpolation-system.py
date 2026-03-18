"""
narrative-interpolation-system.py — Narrative Interpolation System for GK BRAIN

Generates plausible off-screen activity explanations for time gaps between
lore posts, maintaining story continuity.

Usage (from gk-brain.py):
    from narrative_interpolation_system import interpolate_gap
    gap_text = interpolate_gap(last_lore_time, current_time, rule_ctx)
"""

import datetime
import os

BASE_DIR = os.path.dirname(__file__)

GAP_TEMPLATES_BY_BLOCK = {
    "morning": [
        "In the quiet hours before dawn, the artist was preparing gear, thinking through the approach.",
        "The night dissolved into early morning hours spent checking tackle and watching weather apps.",
        "Between the last entry and now, sleep came in fragments — the anticipation of the session too strong.",
    ],
    "afternoon": [
        "The intervening hours were spent absorbed in the work — time lost its edges.",
        "Between posts: a long drive through flat countryside, podcasts, and the particular focus of transit.",
        "The hours between were productive but unremarkable — the kind of time that only makes sense in retrospect.",
    ],
    "evening": [
        "As daylight withdrew, the hours between were spent packing up, reflecting, transitioning.",
        "The gap was filled with the practical rituals: cleaning, packing, eating, moving.",
        "Between entries, the pace slowed to a walk — processing the day before the night begins.",
    ],
    "night": [
        "The dark hours passed in their own rhythm — sounds amplified, thoughts vivid.",
        "Between posts: the session deepened. Hours on the bank, watching float tips, listening.",
        "The small hours brought their particular clarity. No one else around. Just the work.",
    ],
}


def interpolate_gap(last_lore_time: str, current_time: str, rule_ctx: dict) -> str:
    """
    Generate a plausible off-screen activity description for a time gap.

    Args:
        last_lore_time: ISO timestamp string of the last lore post.
        current_time: ISO timestamp string of the current time.
        rule_ctx: Current rule context dict.

    Returns:
        Brief interpolation text string, or empty string if gap is small.
    """
    try:
        import hashlib

        # Parse times
        def _parse(ts_str):
            try:
                return datetime.datetime.fromisoformat(str(ts_str).replace("Z", "+00:00"))
            except Exception:
                return datetime.datetime.now(datetime.timezone.utc)

        last = _parse(last_lore_time)
        now = _parse(current_time)
        gap_hours = (now - last).total_seconds() / 3600

        if gap_hours < 3:
            return ""  # small gap, no interpolation needed

        block = rule_ctx.get("block", "afternoon")
        templates = GAP_TEMPLATES_BY_BLOCK.get(block, GAP_TEMPLATES_BY_BLOCK["afternoon"])

        # Deterministic selection based on current time
        idx = int(hashlib.md5(current_time.encode()).hexdigest(), 16) % len(templates)
        selected = templates[idx]

        hours_str = f"{gap_hours:.0f}"
        return f"[In the {hours_str} hours since the last entry: {selected}]"
    except Exception as e:
        print(f"[narrative-interpolation] Error: {e}")
        return ""
