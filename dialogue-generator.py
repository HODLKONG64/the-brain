"""
dialogue-generator.py — NPC Dialogue Generator for GK BRAIN

Provides NPC dialogue and interaction context for creating a living world.
Maintains an NPC registry with personalities tuned to context.

Usage (from gk-brain.py):
    from dialogue_generator import get_npc_dialogue_context
    dialogue_str = get_npc_dialogue_context(rule_ctx, relationships)
"""

import json
import os

BASE_DIR = os.path.dirname(__file__)
NPC_REGISTRY_FILE = os.path.join(BASE_DIR, "npc-registry.json")

DEFAULT_NPCS = {
    "fishing": [
        {
            "name": "Dave",
            "role": "Veteran angler, bailiff",
            "personality": "gruff but wise, shares hard-won knowledge reluctantly",
            "example_lines": [
                "You're using the wrong bait for this time of year, son.",
                "I've seen thousands try that spot. Three catch something.",
                "The big one's been here thirty years. She knows your name by now.",
            ],
        },
        {
            "name": "Old Pete",
            "role": "Lake regular, storyteller",
            "personality": "nostalgic, full of tall tales, generous with time",
            "example_lines": [
                "Back in '98, this whole bank was underwater after the flood.",
                "My personal best? Don't ask. You wouldn't believe me anyway.",
            ],
        },
    ],
    "rave": [
        {
            "name": "Kira",
            "role": "Regular raver, scene veteran",
            "personality": "energetic, inclusive, knows everyone, speaks fast",
            "example_lines": [
                "You made it! I wasn't sure you'd find this place.",
                "The second room is where the real stuff happens. Follow me.",
            ],
        },
        {
            "name": "DJ Marks",
            "role": "Resident DJ, keeper of the sound",
            "personality": "focused, technical, protective of the vibe",
            "example_lines": [
                "This crowd needs another twenty minutes before I drop that track.",
                "You hear that? That's four decks running in phase. Twenty years of practice.",
            ],
        },
    ],
    "art": [
        {
            "name": "Lady-INK",
            "role": "Fellow artist, creative force",
            "personality": "perceptive, challenging, deeply authentic",
            "example_lines": [
                "Why that colour? What are you trying to say that the other colours can't?",
                "The wall remembers everything you put on it. Make it worth remembering.",
            ],
        },
        {
            "name": "Gallery Owner",
            "role": "Commercial art world contact",
            "personality": "calculating, appreciative of talent, speaks in subtext",
            "example_lines": [
                "We've had interest from some collectors. The right piece at the right time.",
            ],
        },
    ],
    "nft": [
        {
            "name": "CryptoMoonBoy",
            "role": "NFT community member, early adopter",
            "personality": "enthusiastic, slightly manic, genuine belief in web3",
            "example_lines": [
                "Floor price is moving. Something's happening with the collection.",
                "The community notices when creators show up. Keep creating.",
            ],
        },
    ],
}


def _load_registry() -> dict:
    if os.path.exists(NPC_REGISTRY_FILE):
        try:
            with open(NPC_REGISTRY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return dict(DEFAULT_NPCS)


def get_npc_dialogue_context(rule_ctx: dict, relationships: dict) -> str:
    """
    Return NPC dialogue context appropriate for the current setting.

    Selects relevant NPCs based on the current block/activity context
    and relationship strength.

    Args:
        rule_ctx: Current rule context dict.
        relationships: Dict of relationship scores from relationship-modeling-system.

    Returns:
        Formatted NPC dialogue context string for AI prompt.
    """
    try:
        registry = _load_registry()
        block = rule_ctx.get("block", "afternoon")
        active_cats = rule_ctx.get("active_categories", [])

        # Determine which NPC context applies
        if any("fishing" in c for c in active_cats) or block == "morning":
            npc_group = "fishing"
        elif any("rave" in c for c in active_cats) or block in ("evening", "night"):
            npc_group = "rave"
        elif any("graffiti" in c or "art" in c for c in active_cats):
            npc_group = "art"
        elif any("nft" in c or "gkdata" in c for c in active_cats):
            npc_group = "nft"
        else:
            npc_group = "art"

        npcs = registry.get(npc_group, [])
        if not npcs:
            return ""

        lines = [f"=== NPC CONTEXT ({npc_group.upper()} setting) ==="]
        for npc in npcs[:2]:
            name = npc.get("name", "NPC")
            role = npc.get("role", "")
            personality = npc.get("personality", "")
            example_lines = npc.get("example_lines", [])
            lines.append(f"\n{name} ({role}): {personality}")
            if example_lines:
                lines.append(f'  Example dialogue: "{example_lines[0]}"')

        lines.append(
            "\nINSTRUCTION: Optionally include a brief NPC interaction. "
            "Keep it authentic to the setting. One or two lines maximum."
        )

        return "\n".join(lines)
    except Exception as e:
        print(f"[dialogue-generator] Error: {e}")
        return ""
