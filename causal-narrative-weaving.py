"""
causal-narrative-weaving.py — Causal Narrative Weaving for GK BRAIN

Weaves cause-and-effect relationships into storytelling for scientific
grounding. Shows WHY things happen, not just what.

Usage (from gk-brain.py):
    from causal_narrative_weaving import get_causal_narrative_hints
    hints = get_causal_narrative_hints(updates, rule_ctx, causal_model)
"""

import os

BASE_DIR = os.path.dirname(__file__)

CAUSAL_PATTERNS = {
    "fishing": {
        "triggers": ["temperature drop", "pressure change", "rain", "dawn", "dusk"],
        "effects": ["feeding frenzy", "fish move shallow", "carp surface", "fish go deep"],
        "template": (
            "Show the CAUSE: {trigger} → EFFECT: {effect}. "
            "The catch happened for a reason. Make the science visible."
        ),
    },
    "nft": {
        "triggers": ["whale movement", "market news", "community post", "twitter trend"],
        "effects": ["floor price shifts", "volume spike", "new holders", "community buzz"],
        "template": (
            "Show the CAUSE: {trigger} → EFFECT: {effect}. "
            "Market events have reasons. Ground the NFT narrative in real dynamics."
        ),
    },
    "rave": {
        "triggers": ["sound system quality", "crowd energy", "track selection", "time of night"],
        "effects": ["peak moment", "crowd unity", "emotional release", "transcendent experience"],
        "template": (
            "Show the CAUSE: {trigger} → EFFECT: {effect}. "
            "The best rave moments don't just happen — they're engineered by factors."
        ),
    },
    "graffiti": {
        "triggers": ["weather", "location choice", "preparation", "emotional state"],
        "effects": ["piece quality", "longevity", "impact on viewers", "self-expression depth"],
        "template": (
            "Show the CAUSE: {trigger} → EFFECT: {effect}. "
            "Every mark on the wall has a reason. Show the intention."
        ),
    },
}


def get_causal_narrative_hints(updates: list, rule_ctx: dict, causal_model: str) -> str:
    """
    Return narrative hints showing WHY things happen in the story.

    Takes the causal model from causal-inference-engine and translates it
    into specific narrative writing instructions.

    Args:
        updates: List of validated update dicts.
        rule_ctx: Current rule context dict.
        causal_model: Causal context string from causal-inference-engine.

    Returns:
        Formatted narrative hints string for AI prompt.
    """
    try:
        active_cats = set(u.get("category", "") for u in updates)
        lines = ["=== CAUSAL NARRATIVE INSTRUCTIONS ==="]

        # Find matching causal patterns
        found_patterns = []
        if any("fishing" in c for c in active_cats):
            found_patterns.append(("fishing", CAUSAL_PATTERNS["fishing"]))
        if any("nft" in c or "gkdata" in c for c in active_cats):
            found_patterns.append(("nft", CAUSAL_PATTERNS["nft"]))
        if any("rave" in c for c in active_cats):
            found_patterns.append(("rave", CAUSAL_PATTERNS["rave"]))
        if any("graffiti" in c for c in active_cats):
            found_patterns.append(("graffiti", CAUSAL_PATTERNS["graffiti"]))

        for domain, pattern in found_patterns[:2]:
            trigger = pattern["triggers"][0]
            effect = pattern["effects"][0]
            instruction = pattern["template"].format(trigger=trigger, effect=effect)
            lines.append(f"\n[{domain.upper()}] {instruction}")

        if causal_model and len(causal_model) > 20:
            lines.append(f"\nCausal context: {causal_model[:200]}")

        lines.append(
            "\nCORE PRINCIPLE: Events in the lore have scientific and logical causes. "
            "Don't just describe what happens — show what made it happen."
        )

        return "\n".join(lines)
    except Exception as e:
        print(f"[causal-narrative-weaving] Error: {e}")
        return "Show cause and effect in the narrative. Events happen for reasons."
