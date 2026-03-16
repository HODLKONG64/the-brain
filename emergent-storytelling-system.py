"""
emergent-storytelling-system.py — Emergent Storytelling System for GK BRAIN

Creates emergent story possibilities by finding unexpected connections between
different update types and data streams.

Usage (from gk-brain.py):
    from emergent_storytelling_system import find_emergent_hooks
    hooks = find_emergent_hooks(updates, rule_ctx)
"""

import os

BASE_DIR = os.path.dirname(__file__)

# Pairs that create interesting narrative intersections
EMERGENT_PAIRS = [
    (
        {"fishing-real", "news-real"},
        "The price of fishing equipment mirrors the cost of NFTs — scarcity and desire drive both markets.",
    ),
    (
        {"fishing-real", "gkdata-real"},
        "Fund the next fishing session through NFT proceeds — art and nature financing each other.",
    ),
    (
        {"rave-real", "graffiti-news-real"},
        "The warehouse wall becomes the canvas — rave energy translated into paint.",
    ),
    (
        {"gkdata-real", "news-real"},
        "The blockchain mirrors the street — decentralised, ungovernable, authentic.",
    ),
    (
        {"fishing-real", "rave-real"},
        "The patience of the lake session and the abandon of the dance floor — two extremes of the same life.",
    ),
    (
        {"graffiti-news-real", "gkdata-real"},
        "Street art permanence vs NFT permanence — which lasts longer: paint or code?",
    ),
    (
        {"news-real", "rave-real"},
        "Crypto market volatility and the underground rave scene share the same energy: wild, unpredictable, alive.",
    ),
    (
        {"fishing-real", "graffiti-news-real"},
        "The carp surface pattern becomes the mural — nature as artistic reference.",
    ),
]


def find_emergent_hooks(updates: list, rule_ctx: dict) -> list:
    """
    Find unexpected narrative connections between present update categories.

    Args:
        updates: List of update dicts with 'category' keys.
        rule_ctx: Current rule context dict.

    Returns:
        List of emergent hook strings for AI narrative weaving.
    """
    try:
        present_cats = {u.get("category", "") for u in updates if u.get("category")}

        hooks = []
        for required_cats, hook_text in EMERGENT_PAIRS:
            if required_cats.issubset(present_cats):
                hooks.append(hook_text)

        # Also generate a block-specific emergent hook
        block = rule_ctx.get("block", "afternoon")
        if block == "morning" and "fishing-real" in present_cats:
            hooks.append(
                "Dawn session: the first cast of the day carries the weight of all previous attempts."
            )
        elif block == "night" and "rave-real" in present_cats:
            hooks.append(
                "After midnight: the music and the darkness create a private world within the public event."
            )

        return hooks[:5]  # limit to top 5 most relevant hooks
    except Exception as e:
        print(f"[emergent-storytelling] Error: {e}")
        return []
