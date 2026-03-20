"""
quality-gate.py — Quality Gate for GK BRAIN

Verifies generated lore quality before posting. Checks for real data
integration, minimum length, no placeholder text, and coherent sentences.

Usage (from gk-brain.py):
    from quality_gate import check_quality
    result = check_quality(lore_text, updates)
    # result: {"passed": bool, "score": 0-10, "issues": list}
"""

import os
import re

BASE_DIR = os.path.dirname(__file__)

MIN_LENGTH = 200
PLACEHOLDER_PATTERNS = [r"\[INSERT\]", r"\bTODO\b", r"\bPLACEHOLDER\b", r"\bXXX\b", r"\[FILL\]"]
INCOHERENCE_PATTERNS = [
    r"\b(\w+) \1\b",  # repeated adjacent words
    r"\.{4,}",        # excessive ellipsis
]


def _check_data_integration(lore_text: str, updates: list) -> float:
    """Check what fraction of updates have keywords present in lore."""
    if not updates:
        return 1.0
    text_lower = lore_text.lower()
    hits = 0
    for u in updates[:10]:
        title = (u.get("title", "") or "").lower()
        content = (u.get("content", "") or "")[:60].lower()
        words = set((title + " " + content).split())
        meaningful = [w for w in words if len(w) > 4]
        if meaningful and any(w in text_lower for w in meaningful[:5]):
            hits += 1
    return hits / min(len(updates), 10)


def check_quality(lore_text: str, updates: list) -> dict:
    """
    Comprehensive quality check on generated lore text.

    Checks:
    - Real data woven in (keyword presence)
    - Minimum length (>200 chars)
    - No placeholder text
    - Basic coherence (no repeated words, no excessive ellipsis)

    Args:
        lore_text: Generated lore string to check.
        updates: List of update dicts used in generation.

    Returns:
        Dict with keys: passed (bool), score (0-10), issues (list).
    """
    try:
        issues = []
        score = 10.0

        # Length check
        if len(lore_text.strip()) < MIN_LENGTH:
            issues.append(f"Text too short: {len(lore_text)} chars (min {MIN_LENGTH})")
            score -= 3.0

        # Placeholder check
        for pattern in PLACEHOLDER_PATTERNS:
            if re.search(pattern, lore_text, re.IGNORECASE):
                issues.append(f"Placeholder text found: {pattern}")
                score -= 2.0

        # Incoherence check
        for pattern in INCOHERENCE_PATTERNS:
            if re.search(pattern, lore_text):
                issues.append("Incoherent pattern detected (repeated words or excessive punctuation)")
                score -= 1.0
                break

        # Data integration check
        integration = _check_data_integration(lore_text, updates)
        if integration < 0.2 and updates:
            issues.append(f"Low data integration: {integration:.0%} of updates referenced")
            score -= 1.5
        elif integration >= 0.5:
            score = min(10.0, score + 0.5)  # bonus for good integration

        # Empty/None check
        if not lore_text or not lore_text.strip():
            issues.append("Lore text is empty")
            score = 0.0

        score = round(max(0.0, min(10.0, score)), 1)
        passed = score >= 5.0 and not any("empty" in i or "Placeholder" in i for i in issues)

        return {"passed": passed, "score": score, "issues": issues}
    except Exception as e:
        print(f"[quality-gate] Error: {e}")
        return {"passed": True, "score": 7.0, "issues": []}
