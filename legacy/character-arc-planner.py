"""
character-arc-planner.py — Character Arc Planner for GK BRAIN

Coordinates long-term character story arc direction and development trajectory.
Guides AI toward advancing the right arc at the right moment.

Usage (from gk-brain.py):
    from character_arc_planner import get_arc_direction
    direction = get_arc_direction(rule_ctx, active_arcs)
"""

import os

BASE_DIR = os.path.dirname(__file__)

ARC_STAGE_DESCRIPTIONS = {
    (0, 20): "EARLY STAGE: Establishing the arc. Introduce the challenge or goal organically.",
    (20, 40): "BUILDING: The character is developing in this area. Show growth and early progress.",
    (40, 60): "MID-ARC: Complications emerge. Deepen the stakes. Show the cost of the journey.",
    (60, 80): "APPROACHING CLIMAX: Tension high. The goal is close. Build anticipation.",
    (80, 95): "CLIMAX ZONE: Major moments. Significant events in this arc. Make them count.",
    (95, 101): "RESOLUTION: The arc is nearly complete. Begin closure or transformation.",
}

ARC_BLOCK_AFFINITY = {
    "Fishing Mastery": ["morning"],
    "NFT Legacy": ["afternoon"],
    "Graffiti Immortality": ["afternoon", "evening"],
    "Underground Recognition": ["evening", "night"],
}


def _get_stage_description(progress: float) -> str:
    for (low, high), desc in ARC_STAGE_DESCRIPTIONS.items():
        if low <= progress < high:
            return desc
    return "Arc in progress."


def get_arc_direction(rule_ctx: dict, active_arcs: list) -> str:
    """
    Determine which arc to advance and provide narrative direction for it.

    Selects the most contextually relevant active arc and returns a directive
    string guiding the AI generation.

    Args:
        rule_ctx: Current rule context dict.
        active_arcs: List of active arc dicts from narrative-arc-tracker.

    Returns:
        Narrative direction string for AI prompt.
    """
    try:
        if not active_arcs:
            return "No active arcs. Generate character-focused introspective content."

        block = rule_ctx.get("block", "afternoon")

        # Score arcs by block affinity and urgency
        def arc_score(arc):
            affinity = ARC_BLOCK_AFFINITY.get(arc.get("name", ""), [])
            affinity_bonus = 3 if block in affinity else 0
            # Arcs near climax get priority
            progress = float(arc.get("progress", 0))
            urgency = progress if 60 <= progress <= 90 else 0
            return affinity_bonus + urgency * 0.1

        best_arc = max(active_arcs, key=arc_score)
        name = best_arc.get("name", "unnamed arc")
        progress = float(best_arc.get("progress", 0))
        description = best_arc.get("description", "")
        target = best_arc.get("target", "")
        stage = _get_stage_description(progress)

        direction = (
            f"=== ARC DIRECTION ===\n"
            f"ADVANCE ARC: '{name}' (progress: {progress:.0f}%)\n"
            f"Arc description: {description}\n"
            f"Ultimate target: {target}\n"
            f"Current stage: {stage}\n"
            f"INSTRUCTION: This lore cycle should meaningfully advance '{name}'. "
            f"Reference the arc's themes and move the story closer to its resolution."
        )

        return direction
    except Exception as e:
        print(f"[character-arc-planner] Error: {e}")
        return "Advance the character's story in an authentic, organic way."
