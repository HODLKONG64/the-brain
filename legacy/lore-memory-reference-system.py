"""
lore-memory-reference-system.py — Lore Memory Reference System for GK BRAIN

Enables the character to naturally reference and callback to specific past
lore moments, building a living, self-referential narrative.

Usage (from gk-brain.py):
    from lore_memory_reference_system import get_memory_references
    refs = get_memory_references(rule_ctx, lore_history)
"""

import os
import re

BASE_DIR = os.path.dirname(__file__)

CONTEXT_KEYWORDS = {
    "morning": ["dawn", "early", "morning", "sunrise", "first light", "mist"],
    "fishing": ["carp", "lake", "fish", "catch", "session", "swim", "bait"],
    "rave": ["rave", "bass", "dance", "warehouse", "dj", "crowd", "underground"],
    "graffiti": ["mural", "spray", "wall", "graffiti", "paint", "canvas"],
    "nft": ["nft", "token", "blockchain", "mint", "collection", "web3"],
}

REFERENCE_TEMPLATES = [
    "Relevant memory: {snippet} — {context_note}",
    "Callback opportunity: {snippet}",
    "Past echo: {snippet}",
]


def _extract_passages(lore_history: str, keywords: list, max_passages: int = 3) -> list:
    """Extract short passages from lore history matching any keyword."""
    passages = []
    sentences = re.split(r'[.!?]\s+', lore_history)
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 20 or len(sentence) > 200:
            continue
        if any(kw.lower() in sentence.lower() for kw in keywords):
            passages.append(sentence)
        if len(passages) >= max_passages:
            break
    return passages


def get_memory_references(rule_ctx: dict, lore_history: str) -> str:
    """
    Search lore history for relevant past events matching current context.

    Returns formatted callback suggestions for the AI to weave into narrative.

    Args:
        rule_ctx: Current rule context dict.
        lore_history: Full or recent lore history text.

    Returns:
        Formatted memory reference string, or empty string if none found.
    """
    try:
        if not lore_history or len(lore_history) < 50:
            return ""

        block = rule_ctx.get("block", "afternoon")
        active_cats = rule_ctx.get("active_categories", [])

        # Build keyword list from block + active categories
        keywords = list(CONTEXT_KEYWORDS.get(block, []))
        for cat in active_cats:
            for key in CONTEXT_KEYWORDS:
                if key in cat:
                    keywords.extend(CONTEXT_KEYWORDS[key])

        if not keywords:
            keywords = ["fish", "art", "rave", "nft"]

        passages = _extract_passages(lore_history, keywords)

        if not passages:
            return ""

        lines = ["=== MEMORY REFERENCES (for callbacks) ==="]
        for i, passage in enumerate(passages[:3]):
            template = REFERENCE_TEMPLATES[i % len(REFERENCE_TEMPLATES)]
            ref = template.format(
                snippet=f'"{passage[:100]}..."',
                context_note="reference this if contextually relevant"
            )
            lines.append(f"• {ref}")

        lines.append(
            "\nINSTRUCTION: Optionally reference one of these past moments to build "
            "narrative continuity. Keep callbacks brief and natural."
        )

        return "\n".join(lines)
    except Exception as e:
        print(f"[lore-memory-reference] Error: {e}")
        return ""
