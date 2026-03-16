"""
recursive-update-discovery.py - Recursive Update Discovery for GK BRAIN

Discovers meta-updates about the character's own posts and growing online
presence. Generates synthetic meta-update suggestions based on lore milestones.

Usage (from gk-brain.py):
    from recursive_update_discovery import discover_meta_updates
    meta_updates = discover_meta_updates(lore_history)
"""

import os
import re

BASE_DIR = os.path.dirname(__file__)

MILESTONE_KEYWORDS = {
    "fishing_reputation": {
        "keywords": ["carp", "fish", "catch", "lake", "session"],
        "threshold": 10,
        "update": {
            "title": "Fishing Reputation Building",
            "content": "The character's fishing exploits have generated enough narrative presence to suggest a growing reputation in the angling community.",
            "category": "meta-real",
            "confidence": 0.6,
        },
    },
    "nft_momentum": {
        "keywords": ["nft", "token", "mint", "blockchain", "collection"],
        "threshold": 8,
        "update": {
            "title": "NFT Narrative Momentum",
            "content": "The GKniftyHEADS NFT narrative thread has gained sufficient depth to suggest real collector interest.",
            "category": "meta-real",
            "confidence": 0.6,
        },
    },
    "art_legacy": {
        "keywords": ["graffiti", "mural", "spray", "wall", "canvas", "paint"],
        "threshold": 6,
        "update": {
            "title": "Graffiti Legacy Accumulating",
            "content": "Repeated artistic output in the lore suggests a growing body of work that may attract notice.",
            "category": "meta-real",
            "confidence": 0.5,
        },
    },
    "rave_identity": {
        "keywords": ["rave", "dj", "bass", "warehouse", "underground"],
        "threshold": 5,
        "update": {
            "title": "Underground Identity Solidifying",
            "content": "Consistent rave scene presence in the lore indicates a recognisable underground identity forming.",
            "category": "meta-real",
            "confidence": 0.5,
        },
    },
}


def discover_meta_updates(lore_history: str) -> list:
    """
    Scan lore history for milestones and return synthetic meta-update suggestions.

    Args:
        lore_history: Full or recent lore history text.

    Returns:
        List of synthetic meta-update dicts (may be empty).
    """
    try:
        if not lore_history or len(lore_history) < 100:
            return []

        text_lower = lore_history.lower()
        meta_updates = []

        for milestone_name, config in MILESTONE_KEYWORDS.items():
            keywords = config["keywords"]
            threshold = config["threshold"]
            count = sum(len(re.findall(r'\b' + kw + r'\b', text_lower)) for kw in keywords)

            if count >= threshold:
                update = dict(config["update"])
                update["milestone"] = milestone_name
                update["keyword_count"] = count
                meta_updates.append(update)

        return meta_updates
    except Exception as e:
        print(f"[recursive-update-discovery] Error: {e}")
        return []
