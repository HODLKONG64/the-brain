"""
transfer-learning-module.py — Transfer Learning Module for GK BRAIN

Accumulates effective narrative patterns discovered over time and applies them
to future generation cycles. Knowledge persists across all sessions.

Usage (from gk-brain.py):
    from transfer_learning_module import get_transfer_hints
    hints = get_transfer_hints()
"""

import json
import os

BASE_DIR = os.path.dirname(__file__)
KNOWLEDGE_FILE = os.path.join(BASE_DIR, "transfer-knowledge.json")

DEFAULT_PATTERNS = [
    "Technique: Open with sensory detail (smell, sound, texture) = higher engagement.",
    "Pattern: Fishing + philosophical reflection = authentic character voice.",
    "Pattern: Rave energy + street art reference = urban authenticity.",
    "Technique: End posts with forward momentum or unresolved tension.",
    "Pattern: NFT milestone + personal story = community connection.",
    "Technique: Specific place names and times ground the narrative in reality.",
    "Pattern: Weather description as emotional mirror = resonant atmosphere.",
    "Technique: Short sentences at peak action, longer at reflection = rhythm.",
    "Pattern: Combining two unrelated scenes through metaphor = originality.",
    "Technique: Character acknowledging difficulty/failure = relatable authenticity.",
]


def _load_knowledge() -> dict:
    if os.path.exists(KNOWLEDGE_FILE):
        try:
            with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"patterns": DEFAULT_PATTERNS, "session_count": 0}


def get_transfer_hints() -> str:
    """
    Return accumulated narrative knowledge patterns as a formatted hint string.

    Patterns are persistent across sessions and grow over time.

    Returns:
        String of effective narrative techniques for AI prompt inclusion.
    """
    try:
        knowledge = _load_knowledge()
        patterns = knowledge.get("patterns", DEFAULT_PATTERNS)

        lines = ["=== TRANSFER LEARNING: Proven Effective Techniques ==="]
        for i, pattern in enumerate(patterns[:8], 1):
            lines.append(f"{i}. {pattern}")

        lines.append(
            "\nAPPLY: Naturally incorporate 2-3 of these techniques in this generation cycle."
        )

        return "\n".join(lines)
    except Exception as e:
        print(f"[transfer-learning] Error: {e}")
        return "Apply authentic voice, sensory detail, and emotional resonance."
