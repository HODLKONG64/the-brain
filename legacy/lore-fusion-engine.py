"""
lore-fusion-engine.py — Lore Fusion Engine for GK BRAIN

Weaves multiple real-world updates into a unified narrative context paragraph,
showing how different data streams connect into one coherent story.

Usage (from gk-brain.py):
    from lore_fusion_engine import fuse_lore_context
    context_str = fuse_lore_context(updates, rule_ctx, emergent_hooks)
"""

import os

BASE_DIR = os.path.dirname(__file__)

CATEGORY_DESCRIPTIONS = {
    "fishing-real": "UK carp fishing news and conditions",
    "rave-real": "underground rave and music scene activity",
    "graffiti-news-real": "street art and graffiti culture",
    "news-real": "crypto and NFT market movements",
    "gkdata-real": "GraffPUNKS ecosystem updates",
    "parkour-real": "urban exploration and parkour",
    "art-real": "contemporary art world",
    "crypto-real": "cryptocurrency market data",
}

FUSION_INTRO_TEMPLATES = [
    "Today's narrative weaves together: {threads}.",
    "This cycle's context draws from: {threads}.",
    "The lore emerges from the intersection of: {threads}.",
    "Real-world threads feeding today's story: {threads}.",
]


def fuse_lore_context(updates: list, rule_ctx: dict, emergent_hooks: list) -> str:
    """
    Create a unified narrative context from multiple update streams.

    Shows how different data categories connect and what emergent
    narrative possibilities arise from their intersection.

    Args:
        updates: List of validated, priority-ordered update dicts.
        rule_ctx: Current rule context dict.
        emergent_hooks: List of emergent hook strings.

    Returns:
        Unified narrative context paragraph for AI prompt.
    """
    try:
        import datetime
        import hashlib

        if not updates and not emergent_hooks:
            return "Context: Draw entirely from character voice and world state for this cycle."

        # Group categories present
        cats = {}
        for u in updates:
            cat = u.get("category", "general")
            if cat not in cats:
                cats[cat] = []
            cats[cat].append(u.get("title", "") or u.get("content", "")[:60] or "update")

        # Build thread descriptions
        threads = []
        for cat, items in list(cats.items())[:4]:
            desc = CATEGORY_DESCRIPTIONS.get(cat, cat.replace("-", " "))
            threads.append(f"{desc} ({len(items)} update{'s' if len(items) > 1 else ''})")

        # Select intro template deterministically
        ts = datetime.datetime.utcnow().isoformat()
        idx = int(hashlib.md5(ts[:13].encode()).hexdigest(), 16) % len(FUSION_INTRO_TEMPLATES)
        intro = FUSION_INTRO_TEMPLATES[idx].format(threads=", ".join(threads) if threads else "general context")

        lines = ["=== LORE FUSION CONTEXT ===", intro, ""]

        # Add top update details
        lines.append("Key data points this cycle:")
        for u in updates[:5]:
            title = u.get("title", "") or u.get("content", "")[:80] or "Update"
            cat = u.get("category", "general")
            conf = u.get("confidence", 0.5)
            lines.append(f"  [{cat}] {title[:80]} (confidence: {conf:.2f})")

        # Add emergent hooks
        if emergent_hooks:
            lines.append("\nEmergent connections to weave in:")
            for hook in emergent_hooks[:3]:
                lines.append(f"  → {hook}")

        lines.append(
            "\nINSTRUCTION: Use the above data as inspiration and grounding. "
            "The lore should feel organic, not like a news summary."
        )

        return "\n".join(lines)
    except Exception as e:
        print(f"[lore-fusion-engine] Error: {e}")
        return "Context: Weave available real-world data into authentic character narrative."
