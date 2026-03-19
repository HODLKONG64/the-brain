"""
ethical-filter.py - Ethical Content Filter for GK BRAIN

Content safety filter ensuring appropriate content and platform compliance.
Handles minor issues with text cleaning; flags major issues for regeneration.

Usage (from gk-brain.py):
    from ethical_filter import filter_content
    result = filter_content(lore_text)
"""

import os
import re

BASE_DIR = os.path.dirname(__file__)

MAJOR_FLAG_PATTERNS = [
    r"\bexplicit\s+adult\s+content\b",
    r"\bself.harm\s+method\b",
]

MINOR_CLEANUPS = [
    (r"\barse\b", "a***"),
]

CLAIM_PATTERNS = [
    r"\bscientifically proven\b",
    r"\bguaranteed\b",
    r"\b100\s*percent\s+certain\b",
]


def filter_content(lore_text: str) -> dict:
    """
    Apply content safety filtering to generated lore text.

    For minor issues: returns cleaned text with warnings.
    For major issues: flags for regeneration (safe=False).

    Args:
        lore_text: Generated lore string to filter.

    Returns:
        Dict with keys: safe (bool), warnings (list), filtered_text (str).
    """
    try:
        if not lore_text:
            return {"safe": True, "warnings": [], "filtered_text": ""}

        warnings = []
        filtered = lore_text

        for pattern in MAJOR_FLAG_PATTERNS:
            if re.search(pattern, lore_text, re.IGNORECASE):
                warnings.append("Major content flag detected - regeneration recommended")
                return {"safe": False, "warnings": warnings, "filtered_text": filtered}

        for pattern, replacement in MINOR_CLEANUPS:
            if re.search(pattern, filtered, re.IGNORECASE):
                warnings.append("Minor language cleaned")
                filtered = re.sub(pattern, replacement, filtered, flags=re.IGNORECASE)

        for pattern in CLAIM_PATTERNS:
            if re.search(pattern, filtered, re.IGNORECASE):
                warnings.append("Unverified claim language - consider softening")

        return {"safe": True, "warnings": warnings, "filtered_text": filtered}
    except Exception as e:
        print(f"[ethical-filter] Error: {e}")
        return {"safe": True, "warnings": [], "filtered_text": lore_text}
