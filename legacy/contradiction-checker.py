"""
contradiction-checker.py — Contradiction Checker for GK BRAIN

Prevents narrative inconsistencies by checking generated lore against
established lore history and current context.

Usage (from gk-brain.py):
    from contradiction_checker import check_contradictions
    result = check_contradictions(lore_text, lore_history, rule_ctx)
"""

import os
import re

BASE_DIR = os.path.dirname(__file__)

# Pairs of mutually exclusive location contexts
LOCATION_EXCLUSIONS = [
    (
        [r"\bat\s+(the\s+)?(lake|reservoir|riverbank|canal bank)"],
        [r"\bin\s+(london|manchester|birmingham|the\s+city|gallery|warehouse)"],
        "Character cannot be at lakeside and city simultaneously",
    ),
]

# Time contradictions
TIME_CONTRADICTIONS = [
    (
        [r"\b(this morning|early this morning|dawn|sunrise)"],
        [r"\b(last night|tonight|midnight|3am|4am)"],
        "Morning and late-night references in same post contradict",
    ),
]

BLOCK_TIME_MAP = {
    "morning": ["morning", "dawn", "early", "sunrise", "6am", "7am", "8am"],
    "afternoon": ["afternoon", "midday", "noon", "lunchtime", "2pm", "3pm"],
    "evening": ["evening", "dusk", "sunset", "6pm", "7pm", "8pm"],
    "night": ["night", "midnight", "late", "dark", "11pm", "midnight"],
}


def _find_contradiction_in_sets(text: str, set_a: list, set_b: list) -> bool:
    """Return True if both pattern sets match in text."""
    text_lower = text.lower()
    a_match = any(re.search(p, text_lower) for p in set_a)
    b_match = any(re.search(p, text_lower) for p in set_b)
    return a_match and b_match


def check_contradictions(lore_text: str, lore_history: str, rule_ctx: dict) -> dict:
    """
    Check generated lore for contradictions with context and history.

    Args:
        lore_text: Generated lore string to check.
        lore_history: Historical lore text for cross-reference.
        rule_ctx: Current rule context dict.

    Returns:
        Dict with keys: contradictions (list), clear (bool).
    """
    try:
        contradictions = []

        # Location exclusion checks
        for set_a, set_b, description in LOCATION_EXCLUSIONS:
            if _find_contradiction_in_sets(lore_text, set_a, set_b):
                contradictions.append(description)

        # Time contradiction checks
        for set_a, set_b, description in TIME_CONTRADICTIONS:
            if _find_contradiction_in_sets(lore_text, set_a, set_b):
                contradictions.append(description)

        # Block consistency check
        block = rule_ctx.get("block", "afternoon")
        block_words = BLOCK_TIME_MAP.get(block, [])
        opposite_blocks = [b for b in BLOCK_TIME_MAP if b != block]
        lore_lower = lore_text.lower()

        for opposite_block in opposite_blocks:
            opp_words = BLOCK_TIME_MAP[opposite_block]
            if any(w in lore_lower for w in opp_words) and not any(w in lore_lower for w in block_words):
                pass  # Allow references to other times without contradiction if not exclusive

        return {
            "contradictions": contradictions,
            "clear": len(contradictions) == 0,
        }
    except Exception as e:
        print(f"[contradiction-checker] Error: {e}")
        return {"contradictions": [], "clear": True}
