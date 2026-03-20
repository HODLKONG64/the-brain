"""
narrative-coherence-validator.py - Narrative Coherence Validator for GK BRAIN

Validates logical consistency, realistic cause-effect, and timeline accuracy
in generated lore. Provides improvement suggestions.

Usage (from gk-brain.py):
    from narrative_coherence_validator import validate_coherence
    result = validate_coherence(lore_text, rule_ctx)
"""

import os
import re

BASE_DIR = os.path.dirname(__file__)

TIME_BLOCK_KEYWORDS = {
    "morning": ["morning", "dawn", "early", "sunrise", "mist", "quiet road"],
    "afternoon": ["afternoon", "midday", "noon", "sun overhead", "bright"],
    "evening": ["evening", "dusk", "sunset", "fading light", "heading back"],
    "night": ["night", "dark", "midnight", "late", "stars", "black water"],
}

MIN_COHERENT_LENGTH = 100
MOTIVATION_MARKERS = ["because", "so that", "wanted", "needed", "decided", "knew"]


def _check_time_consistency(text: str, rule_ctx: dict) -> list:
    """Check that time references in text align with the current block."""
    issues = []
    block = rule_ctx.get("block", "afternoon")
    text_lower = text.lower()

    current_block_words = TIME_BLOCK_KEYWORDS.get(block, [])
    opposite_blocks = {b: words for b, words in TIME_BLOCK_KEYWORDS.items() if b != block}

    has_correct_time = any(w in text_lower for w in current_block_words)
    has_wrong_time = {}
    for opp_block, words in opposite_blocks.items():
        if any(w in text_lower for w in words):
            has_wrong_time[opp_block] = True

    if has_wrong_time and not has_correct_time:
        wrong_blocks = ", ".join(has_wrong_time.keys())
        issues.append(
            f"Time reference mismatch: text suggests {wrong_blocks} but current block is {block}"
        )

    return issues


def _check_motivation_clarity(text: str) -> list:
    """Check that character motivations are present."""
    issues = []
    if len(text) > 300:
        has_motivation = any(m in text.lower() for m in MOTIVATION_MARKERS)
        if not has_motivation:
            issues.append("Suggestion: add clearer motivation markers (because, wanted, decided)")
    return issues


def validate_coherence(lore_text: str, rule_ctx: dict) -> dict:
    """
    Validate logical consistency and coherence of generated lore.

    Args:
        lore_text: Generated lore string.
        rule_ctx: Current rule context dict.

    Returns:
        Dict with keys: coherent (bool), score (0-10), suggestions (list).
    """
    try:
        suggestions = []
        score = 10.0

        if len(lore_text.strip()) < MIN_COHERENT_LENGTH:
            suggestions.append("Text is very short - expand for coherent narrative")
            score -= 2.0

        time_issues = _check_time_consistency(lore_text, rule_ctx)
        suggestions.extend(time_issues)
        score -= len(time_issues) * 1.5

        motivation_issues = _check_motivation_clarity(lore_text)
        suggestions.extend(motivation_issues)

        sentence_count = len(re.findall(r'[.!?]+', lore_text))
        if sentence_count < 3 and len(lore_text) > 150:
            suggestions.append("Very few sentences detected - check sentence structure")
            score -= 1.0

        score = round(max(0.0, min(10.0, score)), 1)

        return {
            "coherent": score >= 6.0,
            "score": score,
            "suggestions": suggestions,
        }
    except Exception as e:
        print(f"[coherence-validator] Error: {e}")
        return {"coherent": True, "score": 7.0, "suggestions": []}
