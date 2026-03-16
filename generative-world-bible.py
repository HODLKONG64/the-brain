"""
generative-world-bible.py — Generative World Bible for GK BRAIN

Auto-generates and maintains the living world documentation: known locations,
NPCs, established facts, and timeline. Grows with each cycle.

Usage (from gk-brain.py):
    from generative_world_bible import get_world_bible_context, update_world_bible
    bible_str = get_world_bible_context()
    update_world_bible(lore_text)
"""

import json
import os
import re

BASE_DIR = os.path.dirname(__file__)
BIBLE_FILE = os.path.join(BASE_DIR, "world-bible-state.json")

DEFAULT_BIBLE = {
    "locations": [
        "Windermere Lake District — primary fishing venue",
        "Printworks, London — rave and events venue",
        "Manchester city walls — established graffiti territory",
        "Shoreditch, East London — art gallery district",
    ],
    "npcs": [
        "Lady-INK — fellow artist, fellow traveller",
        "Dave the Bailiff — guardian of the northern lake",
        "The Blocktopia crew — digital art collective",
    ],
    "established_facts": [
        "The artist is based in the UK",
        "Fishing sessions typically last overnight",
        "GKniftyHEADS NFT collection exists on WAX blockchain",
        "The character's medium is spray paint and digital art",
    ],
    "timeline_notes": [],
    "last_updated": None,
}

LOCATION_PATTERNS = [
    r"\bat ([\w\s]+lake|[\w\s]+reservoir|[\w\s]+venue|[\w\s]+gallery)\b",
    r"\bin ([\w\s]+warehouse|[\w\s]+studio|[\w\s]+park)\b",
]
NPC_PATTERNS = [
    r"\b([A-Z][a-z]+-[A-Z][A-Z]+)\b",  # Lady-INK style names
    r"\b([A-Z][a-z]+ the [A-Z][a-z]+)\b",  # Dave the Bailiff style
]


def _load_bible() -> dict:
    if os.path.exists(BIBLE_FILE):
        try:
            with open(BIBLE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return dict(DEFAULT_BIBLE)


def _save_bible(bible: dict) -> None:
    try:
        import datetime
        bible["last_updated"] = datetime.datetime.utcnow().isoformat()
        with open(BIBLE_FILE, "w", encoding="utf-8") as f:
            json.dump(bible, f, indent=2)
    except Exception as e:
        print(f"[world-bible] Save error: {e}")


def get_world_bible_context() -> str:
    """
    Return condensed world bible context for AI prompt enrichment.

    Returns:
        Multi-line string summarising the known world.
    """
    try:
        bible = _load_bible()
        lines = ["=== WORLD BIBLE (established facts) ==="]

        lines.append("\nKnown Locations:")
        for loc in bible.get("locations", [])[:5]:
            lines.append(f"  • {loc}")

        lines.append("\nKnown NPCs:")
        for npc in bible.get("npcs", [])[:4]:
            lines.append(f"  • {npc}")

        lines.append("\nEstablished Facts:")
        for fact in bible.get("established_facts", [])[:4]:
            lines.append(f"  • {fact}")

        lines.append(
            "\nINSTRUCTION: Stay consistent with these established world facts. "
            "New lore must not contradict them."
        )

        return "\n".join(lines)
    except Exception as e:
        print(f"[world-bible] get_world_bible_context error: {e}")
        return "World: Contemporary UK. Artist lives across fishing lakes, city walls, and underground venues."


def update_world_bible(lore_text: str) -> None:
    """
    Extract new locations and NPCs from lore text and add to bible.

    Args:
        lore_text: Recently generated lore string.
    """
    try:
        bible = _load_bible()

        for pattern in LOCATION_PATTERNS:
            matches = re.findall(pattern, lore_text, re.IGNORECASE)
            for match in matches:
                entry = match.strip().title()
                if entry and entry not in bible["locations"] and len(entry) > 4:
                    bible["locations"].append(entry)

        for pattern in NPC_PATTERNS:
            matches = re.findall(pattern, lore_text)
            for match in matches:
                if match not in bible["npcs"] and len(match) > 3:
                    bible["npcs"].append(match)

        # Keep lists trimmed
        bible["locations"] = bible["locations"][-30:]
        bible["npcs"] = bible["npcs"][-20:]

        _save_bible(bible)
    except Exception as e:
        print(f"[world-bible] update_world_bible error: {e}")
