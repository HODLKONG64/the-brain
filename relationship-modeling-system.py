"""
relationship-modeling-system.py — Relationship Modeling System for GK BRAIN

Models and tracks the strength of relationships between the character
and key NPCs/communities on a 0-10 scale.

Usage (from gk-brain.py):
    from relationship_modeling_system import get_relationship_context, update_relationships
    rel_str = get_relationship_context()
    update_relationships(lore_text)
"""

import json
import os

BASE_DIR = os.path.dirname(__file__)
REL_FILE = os.path.join(BASE_DIR, "relationships.json")

DEFAULT_RELATIONSHIPS = {
    "fishing_community": 6,
    "art_collective": 7,
    "nft_investors": 5,
    "lady_ink": 6,
    "rave_crowd": 7,
    "blocktopia": 5,
    "graffpunks_community": 8,
}

RELATIONSHIP_KEYWORDS = {
    "fishing_community": ["fisherman", "angler", "lake", "carp", "fishing community"],
    "art_collective": ["gallery", "collective", "artist", "mural", "exhibition"],
    "nft_investors": ["investor", "nft", "holder", "collector", "buyer"],
    "lady_ink": ["lady-ink", "lady ink", "ladyink", "she said", "she smiled"],
    "rave_crowd": ["rave", "dance floor", "crowd", "warehouse", "underground"],
    "blocktopia": ["blocktopia", "block", "topia"],
    "graffpunks_community": ["graffpunks", "community", "network", "punks"],
}

RELATIONSHIP_LABELS = {
    (0, 3): "distant/unknown",
    (3, 5): "acquaintance",
    (5, 7): "respected connection",
    (7, 9): "close ally",
    (9, 11): "deep bond",
}


def _get_label(score: float) -> str:
    for (low, high), label in RELATIONSHIP_LABELS.items():
        if low <= score < high:
            return label
    return "neutral"


def _load_relationships() -> dict:
    if os.path.exists(REL_FILE):
        try:
            with open(REL_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return dict(DEFAULT_RELATIONSHIPS)


def _save_relationships(rels: dict) -> None:
    try:
        with open(REL_FILE, "w", encoding="utf-8") as f:
            json.dump(rels, f, indent=2)
    except Exception as e:
        print(f"[relationship-modeling] Save error: {e}")


def get_relationship_context() -> str:
    """
    Return a formatted string of current relationship statuses for AI context.

    Returns:
        Multi-line relationship context string.
    """
    try:
        rels = _load_relationships()
        lines = ["=== RELATIONSHIP CONTEXT ==="]
        for name, score in rels.items():
            label = _get_label(float(score))
            display = name.replace("_", " ").title()
            lines.append(f"• {display}: {score}/10 ({label})")
        lines.append(
            "\nINSTRUCTION: Let relationship strength shape how the character "
            "references and interacts with these groups."
        )
        return "\n".join(lines)
    except Exception as e:
        print(f"[relationship-modeling] get_relationship_context error: {e}")
        return "Character has positive relationships across fishing, art, and rave communities."


def update_relationships(lore_text: str) -> None:
    """
    Update relationship scores based on mentions in lore text.

    Args:
        lore_text: Recently generated lore string.
    """
    try:
        rels = _load_relationships()
        text_lower = lore_text.lower()

        for name, keywords in RELATIONSHIP_KEYWORDS.items():
            hits = sum(1 for kw in keywords if kw in text_lower)
            if hits > 0:
                current = float(rels.get(name, DEFAULT_RELATIONSHIPS.get(name, 5)))
                rels[name] = round(min(10.0, current + 0.05 * hits), 2)

        _save_relationships(rels)
    except Exception as e:
        print(f"[relationship-modeling] update_relationships error: {e}")
