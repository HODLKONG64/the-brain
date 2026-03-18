"""
causal-inference-engine.py - Causal Inference Engine for GK BRAIN

Builds causal models of why events happen in the lore world.
Generates causal reasoning strings for AI prompt enrichment.

Usage (from gk-brain.py):
    from causal_inference_engine import build_causal_context
    causal_str = build_causal_context(updates, rule_ctx)
"""

import os

BASE_DIR = os.path.dirname(__file__)

CAUSAL_RULES = [
    {
        "trigger_category": "fishing-real",
        "trigger_block": "morning",
        "effect": "carp caught because early morning feeding window + calm conditions + focused approach",
        "mechanism": "Dawn triggers carp feeding behaviour. Reduced human activity = calm water = active fish.",
    },
    {
        "trigger_category": "fishing-real",
        "trigger_block": "evening",
        "effect": "fish moving at last light — dusk feeding period begins",
        "mechanism": "Temperature drop triggers carp to move into margins as day heat dissipates.",
    },
    {
        "trigger_category": "rave-real",
        "trigger_block": "night",
        "effect": "peak rave energy because crowd warmed up + DJ reading the room + late hour removes inhibition",
        "mechanism": "Underground events build slowly. Peak collective energy occurs 2-3 hours in.",
    },
    {
        "trigger_category": "gkdata-real",
        "trigger_block": "afternoon",
        "effect": "NFT activity because market hours overlap + community online + new content drops",
        "mechanism": "NFT market activity mirrors traditional market hours with community overlap.",
    },
    {
        "trigger_category": "graffiti-news-real",
        "trigger_block": "evening",
        "effect": "graffiti session because low light + reduced foot traffic + preparation complete",
        "mechanism": "Street art requires cover of reduced visibility. Evening is optimal for outdoor work.",
    },
    {
        "trigger_category": "news-real",
        "trigger_block": "afternoon",
        "effect": "crypto market movement because US market open + institutional activity + news catalyst",
        "mechanism": "Crypto markets are 24/7 but peak activity correlates with US trading hours.",
    },
]


def build_causal_context(updates: list, rule_ctx: dict) -> str:
    """
    Analyse updates and rule context to generate causal reasoning text.

    Args:
        updates: List of validated update dicts.
        rule_ctx: Current rule context dict (block, categories, etc.)

    Returns:
        Formatted causal context string for AI prompt inclusion.
    """
    try:
        block = rule_ctx.get("block", "afternoon")
        active_cats = {u.get("category", "") for u in updates}

        matched_rules = []
        for rule in CAUSAL_RULES:
            cat_match = rule["trigger_category"] in active_cats
            block_match = rule["trigger_block"] == block
            if cat_match or block_match:
                matched_rules.append(rule)

        if not matched_rules:
            return (
                "CAUSAL CONTEXT: Events unfold according to the rhythms of the natural world "
                "and human patterns. Show the logic beneath the surface."
            )

        lines = ["=== CAUSAL INFERENCE MODEL ==="]
        for rule in matched_rules[:3]:
            lines.append(f"\n[{rule['trigger_category']} + {rule['trigger_block']}]")
            lines.append(f"  Effect: {rule['effect']}")
            lines.append(f"  Mechanism: {rule['mechanism']}")

        lines.append(
            "\nINSTRUCTION: Use this causal reasoning to ground the narrative. "
            "Events happen for reasons — make those reasons visible."
        )

        return "\n".join(lines)
    except Exception as e:
        print(f"[causal-inference] Error: {e}")
        return "Causal context: Events in the narrative have natural, logical causes."
