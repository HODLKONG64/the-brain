"""
emotional-intelligence-system.py — Emotional Intelligence System for GK BRAIN

Tracks the character's internal emotional state and adjusts lore tone
accordingly. State evolves based on recent lore content.

Usage (from gk-brain.py):
    from emotional_intelligence_system import get_emotional_state, update_emotional_state
    state = get_emotional_state(rule_ctx, recent_lore)
    update_emotional_state(new_lore_text)
"""

import json
import os
import re

BASE_DIR = os.path.dirname(__file__)
STATE_FILE = os.path.join(BASE_DIR, "emotional-state.json")

POSITIVE_WORDS = ["caught", "success", "amazing", "beautiful", "perfect", "love", "proud",
                  "excited", "brilliant", "won", "achieved", "connected", "peaceful"]
NEGATIVE_WORDS = ["missed", "failed", "frustrating", "cold", "difficult", "tired", "lost",
                  "nothing", "empty", "gone", "rain", "problem", "struggle"]

DEFAULT_STATE = {
    "mood": "thoughtful",
    "stress_level": 4,
    "confidence": 6,
    "last_updated": None,
}

MOODS = ["frustrated", "sad", "thoughtful", "calm", "determined", "happy", "excited"]
TONE_MAP = {
    "frustrated": "terse, clipped sentences, undercurrent of tension",
    "sad": "introspective, quiet, muted colours in description",
    "thoughtful": "meditative, observational, philosophical undertone",
    "calm": "measured, grounded, patient voice",
    "determined": "purposeful, forward-looking, active verbs",
    "happy": "light, energetic, expansive descriptions",
    "excited": "fast-paced, exclamatory, vivid imagery",
}


def _load_state() -> dict:
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return dict(DEFAULT_STATE)


def _save_state(state: dict) -> None:
    try:
        import datetime
        state["last_updated"] = datetime.datetime.utcnow().isoformat()
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"[emotional-intelligence] Save error: {e}")


def get_emotional_state(rule_ctx: dict, recent_lore: str) -> dict:
    """
    Return the character's current emotional state with tone hints.

    Args:
        rule_ctx: Current rule context dict.
        recent_lore: Recent lore text for sentiment analysis.

    Returns:
        Dict with: mood, stress_level, confidence, tone_hint.
    """
    try:
        state = _load_state()

        # Analyse recent lore sentiment
        text_lower = recent_lore.lower()
        pos_count = sum(1 for w in POSITIVE_WORDS if w in text_lower)
        neg_count = sum(1 for w in NEGATIVE_WORDS if w in text_lower)

        # Nudge mood based on sentiment
        mood_idx = MOODS.index(state.get("mood", "thoughtful")) if state.get("mood") in MOODS else 2
        if pos_count > neg_count + 2:
            mood_idx = min(mood_idx + 1, len(MOODS) - 1)
        elif neg_count > pos_count + 2:
            mood_idx = max(mood_idx - 1, 0)

        state["mood"] = MOODS[mood_idx]
        state["tone_hint"] = TONE_MAP.get(state["mood"], "balanced, authentic voice")

        # Block-based adjustments
        block = rule_ctx.get("block", "afternoon")
        if block == "morning":
            state["stress_level"] = max(2, state.get("stress_level", 4) - 1)
        elif block == "night":
            state["confidence"] = min(10, state.get("confidence", 6) + 1)

        return state
    except Exception as e:
        print(f"[emotional-intelligence] get_emotional_state error: {e}")
        return {"mood": "thoughtful", "stress_level": 4, "confidence": 6, "tone_hint": "balanced voice"}


def update_emotional_state(lore_text: str) -> None:
    """
    Update the stored emotional state based on new lore content.

    Args:
        lore_text: Newly generated lore text to analyse.
    """
    try:
        state = _load_state()
        text_lower = lore_text.lower()

        pos = sum(1 for w in POSITIVE_WORDS if w in text_lower)
        neg = sum(1 for w in NEGATIVE_WORDS if w in text_lower)

        stress = state.get("stress_level", 4)
        confidence = state.get("confidence", 6)

        if pos > neg:
            confidence = min(10, confidence + 0.5)
            stress = max(0, stress - 0.5)
        elif neg > pos:
            stress = min(10, stress + 0.5)
            confidence = max(0, confidence - 0.5)

        state["stress_level"] = round(stress, 1)
        state["confidence"] = round(confidence, 1)

        _save_state(state)
    except Exception as e:
        print(f"[emotional-intelligence] update_emotional_state error: {e}")
