"""
character-memory-bank.py — Character Memory Bank for GK BRAIN

Comprehensive memory system storing what the character has learned and
experienced across all lore generation cycles.

Usage (from gk-brain.py):
    from character_memory_bank import get_character_memory, add_memory
    memory_str = get_character_memory()
    add_memory("Caught 38lb mirror carp at Windermere", "fishing_experiences")
"""

import json
import os

BASE_DIR = os.path.dirname(__file__)
MEMORY_FILE = os.path.join(BASE_DIR, "character-memory.json")

MAX_MEMORIES_PER_CATEGORY = 20

DEFAULT_MEMORY = {
    "fishing_experiences": [
        "First night session at a northern reservoir — cold but electric.",
        "Caught a 28lb common carp after a 6-hour wait.",
    ],
    "art_events": [
        "Completed a large mural at a community wall in Manchester.",
        "Exhibited pieces at a pop-up gallery in Shoreditch.",
    ],
    "rave_memories": [
        "All-night warehouse session with 200 people, sunrise arrival.",
        "DJ set at an underground Friday event — crowd responded perfectly.",
    ],
    "nft_milestones": [
        "First GKniftyHEADS NFT minted and listed on WAX.",
        "NoBallGames collection reached 50 unique holders.",
    ],
    "relationships": [
        "Lady-INK: fellow artist, respected creative, occasional collaborator.",
        "The fishing community at the lake: respectful nods, shared silence.",
    ],
}


def _load_memory() -> dict:
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return dict(DEFAULT_MEMORY)


def _save_memory(memory: dict) -> None:
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=2)
    except Exception as e:
        print(f"[character-memory-bank] Save error: {e}")


def get_character_memory() -> str:
    """
    Return a formatted memory string for inclusion in the AI prompt.

    Returns:
        Multi-line string summarising the character's key memories.
    """
    try:
        memory = _load_memory()
        lines = ["=== CHARACTER MEMORY BANK ==="]

        for category, entries in memory.items():
            if entries:
                label = category.replace("_", " ").title()
                lines.append(f"\n[{label}]")
                for entry in entries[-3:]:  # last 3 per category
                    lines.append(f"  • {entry}")

        lines.append(
            "\nINSTRUCTION: Reference relevant memories naturally in narrative. "
            "Build continuity by callbacks to past events."
        )

        return "\n".join(lines)
    except Exception as e:
        print(f"[character-memory-bank] get_character_memory error: {e}")
        return "Character has a rich history of fishing, art, raves, and NFT adventures."


def add_memory(event: str, category: str) -> None:
    """
    Add a new memory event to the specified category.

    Args:
        event: Description of the event to remember.
        category: One of the memory categories (e.g. 'fishing_experiences').
    """
    try:
        memory = _load_memory()
        if category not in memory:
            memory[category] = []
        memory[category].append(event)
        # Trim to max
        memory[category] = memory[category][-MAX_MEMORIES_PER_CATEGORY:]
        _save_memory(memory)
    except Exception as e:
        print(f"[character-memory-bank] add_memory error: {e}")
