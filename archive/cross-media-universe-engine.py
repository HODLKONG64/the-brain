"""
cross-media-universe-engine.py — Cross-Media Universe Engine for GK BRAIN

Manages universe expansion beyond single posts — side characters, alternate
perspectives, and deepening lore threads.

Usage (from gk-brain.py):
    from cross_media_universe_engine import get_universe_hints
    hints = get_universe_hints(rule_ctx, active_arcs)
"""

import json
import os

BASE_DIR = os.path.dirname(__file__)
UNIVERSE_FILE = os.path.join(BASE_DIR, "universe-state.json")

UNIVERSE_FREQUENCY = 8  # 1 in 8 cycles

UNIVERSE_HINTS = [
    (
        "Consider mentioning a side character's perspective on the artist's activities. "
        "What does Dave the bailiff think about the return visits? "
        "What does the gallery owner notice about the artist's evolving work?"
    ),
    (
        "Hint at an alternate storyline simmering in the background. "
        "The Blocktopia connection could deepen here — what do they see in this artist's work "
        "that others don't yet?"
    ),
    (
        "Universe expansion: the artist's reputation is starting to travel. "
        "Someone in a different city has heard of the work. A stranger references a piece. "
        "The world is wider than the character knows."
    ),
    (
        "Introduce a potential future thread: a location not yet visited, "
        "a person not yet met, a project not yet started. Plant the seed subtly."
    ),
    (
        "Side universe: what happened to the last NFT buyer? "
        "Somewhere, someone is looking at the digital art the character made. "
        "That connection exists, even if invisible."
    ),
]

_call_counter = [0]


def _load_state() -> dict:
    if os.path.exists(UNIVERSE_FILE):
        try:
            with open(UNIVERSE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"cycle_count": 0, "hints_used": []}


def _save_state(state: dict) -> None:
    try:
        with open(UNIVERSE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"[universe-engine] Save error: {e}")


def get_universe_hints(rule_ctx: dict, active_arcs: list) -> str:
    """
    Occasionally return a universe expansion hint for richer world building.

    Returns a hint 1 in UNIVERSE_FREQUENCY cycles, otherwise empty string.

    Args:
        rule_ctx: Current rule context dict.
        active_arcs: List of active arc dicts.

    Returns:
        Universe expansion hint string, or empty string.
    """
    try:
        state = _load_state()
        cycle = state.get("cycle_count", 0)
        state["cycle_count"] = cycle + 1
        _save_state(state)

        if cycle % UNIVERSE_FREQUENCY != 0:
            return ""

        hints_used = state.get("hints_used", [])
        available = [i for i in range(len(UNIVERSE_HINTS)) if i not in hints_used[-4:]]
        if not available:
            available = list(range(len(UNIVERSE_HINTS)))

        idx = available[cycle % len(available)]
        hint = UNIVERSE_HINTS[idx]

        state["hints_used"].append(idx)
        state["hints_used"] = state["hints_used"][-10:]
        _save_state(state)

        return (
            f"=== UNIVERSE EXPANSION (optional enrichment) ===\n"
            f"{hint}\n"
            f"INSTRUCTION: If it fits naturally, add a brief universe-expanding detail. "
            f"Keep it as a thread, not a tangent."
        )
    except Exception as e:
        print(f"[universe-engine] Error: {e}")
        return ""
