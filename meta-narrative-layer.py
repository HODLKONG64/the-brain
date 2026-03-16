"""
meta-narrative-layer.py — Meta-Narrative Layer for GK BRAIN

Adds self-aware meta-narrative elements when the character reflects on
their own growing story and online presence. Used sparingly.

Usage (from gk-brain.py):
    from meta_narrative_layer import get_meta_hints
    meta = get_meta_hints(rule_ctx, emotional_state)
"""

import os

BASE_DIR = os.path.dirname(__file__)

META_FREQUENCY = 5  # 1 in META_FREQUENCY calls returns a meta hint

META_HINTS = [
    (
        "The character might notice they're becoming known — a stranger recognising their work, "
        "a comment that landed further than expected. Subtle, not self-congratulatory."
    ),
    (
        "Reflect on the pattern of life: the same lake, different seasons; "
        "the same walls, different messages. The character begins to see their own loops."
    ),
    (
        "The character notices how their two worlds — digital and physical — are bleeding together. "
        "NFT holders asking about the catch. Anglers asking about the drops."
    ),
    (
        "A moment of perspective: stepping back to see the whole arc. "
        "How far from the beginning. How much further to go. Not stated — implied."
    ),
    (
        "The character considers legacy — not fame, but permanence. "
        "The mural that outlasts the lease. The token that outlasts the platform."
    ),
]

_call_counter = [0]


def get_meta_hints(rule_ctx: dict, emotional_state: dict) -> str:
    """
    Occasionally return a subtle meta-narrative hint for the AI to weave in.

    Returns a hint 1 in META_FREQUENCY calls. Otherwise returns empty string.

    Args:
        rule_ctx: Current rule context dict.
        emotional_state: Dict from emotional-intelligence-system.

    Returns:
        Meta hint string, or empty string.
    """
    try:
        _call_counter[0] += 1

        if _call_counter[0] % META_FREQUENCY != 0:
            return ""

        # Select hint based on mood
        mood = emotional_state.get("mood", "thoughtful")
        idx = 0
        if mood in ("thoughtful", "calm"):
            idx = 1
        elif mood in ("happy", "excited"):
            idx = 0
        elif mood == "determined":
            idx = 4
        else:
            idx = (_call_counter[0] // META_FREQUENCY) % len(META_HINTS)

        hint = META_HINTS[idx % len(META_HINTS)]

        return (
            f"=== META-NARRATIVE (optional, use subtly) ===\n"
            f"{hint}\n"
            f"INSTRUCTION: If this resonates with the current cycle, weave it in "
            f"as a quiet undercurrent — never explicit self-commentary."
        )
    except Exception as e:
        print(f"[meta-narrative] Error: {e}")
        return ""
