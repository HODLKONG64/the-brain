"""
narrative-tension-curve.py — Narrative Tension Curve Manager for GK BRAIN

Manages story pacing and tension for professionally structured narrative.
Builds tension over time toward climactic moments.

Usage (from gk-brain.py):
    from narrative_tension_curve import get_tension_hint
    hint = get_tension_hint(rule_ctx, arc_progress)
"""

import json
import os

BASE_DIR = os.path.dirname(__file__)
TENSION_FILE = os.path.join(BASE_DIR, "tension-state.json")

TENSION_DESCRIPTIONS = {
    (0, 2): ("CALM", "Low tension. Establish scene and character. No urgency."),
    (2, 4): ("BUILDING", "Gentle tension rising. Introduce a goal or question."),
    (4, 6): ("ENGAGED", "Moderate tension. Complications begin. Stakes clarified."),
    (6, 8): ("TENSE", "High tension. Building toward climax. Hint at major event."),
    (8, 10): ("CLIMAX", "Peak tension. Major event imminent or occurring. Make it count."),
    (10, 11): ("RESOLUTION", "Tension releasing. Aftermath. New equilibrium forming."),
}


def _get_tension_description(level: float) -> tuple:
    for (low, high), (label, desc) in TENSION_DESCRIPTIONS.items():
        if low <= level < high:
            return label, desc
    return "UNKNOWN", "Continue narrative development."


def _load_tension() -> dict:
    if os.path.exists(TENSION_FILE):
        try:
            with open(TENSION_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"level": 3.0, "cycle_count": 0, "last_climax_cycle": 0}


def _save_tension(state: dict) -> None:
    try:
        with open(TENSION_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"[tension-curve] Save error: {e}")


def get_tension_hint(rule_ctx: dict, arc_progress: dict) -> str:
    """
    Return narrative tension hint for the current cycle.

    Tension naturally builds over ~12 cycles then resets after a climax.
    Arc progress can accelerate tension.

    Args:
        rule_ctx: Current rule context dict.
        arc_progress: Dict of arc names to progress values.

    Returns:
        Formatted tension hint string.
    """
    try:
        state = _load_tension()
        level = float(state.get("level", 3.0))
        cycle = int(state.get("cycle_count", 0))
        last_climax = int(state.get("last_climax_cycle", 0))

        # Natural tension build: +0.2 per cycle, reset after climax
        cycles_since_climax = cycle - last_climax
        if cycles_since_climax > 20 and level >= 9:
            # Reset after climax
            level = 2.0
            state["last_climax_cycle"] = cycle
        else:
            level = min(10.0, level + 0.2)

        # Arc progress boost
        if arc_progress:
            max_progress = max(arc_progress.values()) if isinstance(arc_progress, dict) else 0
            if max_progress > 75:
                level = min(10.0, level + 0.5)

        # Block-based adjustment
        block = rule_ctx.get("block", "afternoon")
        if block == "night":
            level = min(10.0, level + 0.3)

        state["level"] = round(level, 1)
        state["cycle_count"] = cycle + 1
        _save_tension(state)

        label, description = _get_tension_description(level)

        return (
            f"=== NARRATIVE TENSION: {level:.1f}/10 [{label}] ===\n"
            f"{description}\n"
            f"INSTRUCTION: Calibrate the emotional intensity of this lore post to match "
            f"tension level {level:.0f}/10."
        )
    except Exception as e:
        print(f"[tension-curve] Error: {e}")
        return "TENSION: Moderate. Maintain engaging narrative momentum."
