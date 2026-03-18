"""
skill-progression-tracker.py — RPG-Style Skill Tracker for GK BRAIN

Tracks the character's skills on a 1-10 scale, incrementing them as
matching content appears in lore and updates.

Usage (from gk-brain.py):
    from skill_progression_tracker import get_skill_levels, update_skills
    skills = get_skill_levels()
    update_skills(lore_text, updates)
"""

import json
import os

BASE_DIR = os.path.dirname(__file__)
SKILLS_FILE = os.path.join(BASE_DIR, "skill-levels.json")

DEFAULT_SKILLS = {
    "fishing": 6,
    "art": 7,
    "parkour": 5,
    "dj": 6,
    "web3": 5,
    "social": 6,
}

SKILL_KEYWORDS = {
    "fishing": ["carp", "fish", "lake", "catch", "bait", "rod", "reel", "session", "swim"],
    "art": ["graffiti", "mural", "paint", "canvas", "spray", "sketch", "gallery", "colour"],
    "parkour": ["parkour", "jump", "vault", "rooftop", "urban", "freerun", "climb"],
    "dj": ["dj", "mix", "turntable", "set", "track", "bass", "decks", "rave"],
    "web3": ["nft", "blockchain", "token", "mint", "wallet", "crypto", "web3", "dao"],
    "social": ["community", "people", "crowd", "network", "connect", "talk", "friend"],
}

MAX_SKILL = 10
INCREMENT = 0.1


def _load_skills() -> dict:
    if os.path.exists(SKILLS_FILE):
        try:
            with open(SKILLS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return dict(DEFAULT_SKILLS)


def _save_skills(skills: dict) -> None:
    try:
        with open(SKILLS_FILE, "w", encoding="utf-8") as f:
            json.dump(skills, f, indent=2)
    except Exception as e:
        print(f"[skill-tracker] Save error: {e}")


def get_skill_levels() -> dict:
    """
    Return the character's current skill levels.

    Returns:
        Dict mapping skill name to current level (1.0-10.0).
    """
    try:
        return _load_skills()
    except Exception as e:
        print(f"[skill-tracker] get_skill_levels error: {e}")
        return dict(DEFAULT_SKILLS)


def update_skills(lore_text: str, updates: list) -> None:
    """
    Increment relevant skills based on content in lore text and updates.

    Args:
        lore_text: Generated lore string.
        updates: List of update dicts used in generation.
    """
    try:
        skills = _load_skills()
        combined = lore_text.lower() + " "
        for u in updates:
            combined += (u.get("content", "") or u.get("title", "") or "").lower() + " "

        for skill, keywords in SKILL_KEYWORDS.items():
            hits = sum(1 for kw in keywords if kw in combined)
            if hits >= 2:
                current = float(skills.get(skill, DEFAULT_SKILLS.get(skill, 5)))
                skills[skill] = round(min(MAX_SKILL, current + INCREMENT * hits), 2)

        _save_skills(skills)
    except Exception as e:
        print(f"[skill-tracker] update_skills error: {e}")
