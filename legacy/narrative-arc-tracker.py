"""
narrative-arc-tracker.py — Narrative Arc Tracker for GK BRAIN

Identifies and tracks multiple simultaneous story arcs, monitoring
progress from 0-100% and detecting arc-relevant lore content.

Usage (from gk-brain.py):
    from narrative_arc_tracker import get_active_arcs, update_arc_progress, add_arc
    arcs = get_active_arcs()
    update_arc_progress(lore_text)
    add_arc("New Arc", "Description", "Target outcome")
"""

import json
import os

BASE_DIR = os.path.dirname(__file__)
ARCS_FILE = os.path.join(BASE_DIR, "narrative-arcs.json")

DEFAULT_ARCS = [
    {
        "name": "Fishing Mastery",
        "description": "The artist's journey toward legendary carp angling status.",
        "target": "Catch a 50lb+ common carp and have it witnessed.",
        "progress": 40,
        "keywords": ["carp", "fish", "catch", "lake", "rod", "session", "pb"],
        "active": True,
    },
    {
        "name": "NFT Legacy",
        "description": "Building a lasting NFT art collection recognised by the community.",
        "target": "GKniftyHEADS collection reaches 100 unique holders.",
        "progress": 30,
        "keywords": ["nft", "mint", "holder", "collection", "token", "blockchain"],
        "active": True,
    },
    {
        "name": "Graffiti Immortality",
        "description": "Leaving permanent artistic marks across UK cities.",
        "target": "Complete a major commissioned mural in a prominent location.",
        "progress": 55,
        "keywords": ["mural", "graffiti", "wall", "spray", "commissioned", "street art"],
        "active": True,
    },
    {
        "name": "Underground Recognition",
        "description": "Becoming a known name in the UK underground rave circuit.",
        "target": "Headline a significant underground event.",
        "progress": 45,
        "keywords": ["rave", "dj", "headline", "warehouse", "underground", "set"],
        "active": True,
    },
]

PROGRESS_INCREMENT = 2


def _load_arcs() -> list:
    if os.path.exists(ARCS_FILE):
        try:
            with open(ARCS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return list(DEFAULT_ARCS)


def _save_arcs(arcs: list) -> None:
    try:
        with open(ARCS_FILE, "w", encoding="utf-8") as f:
            json.dump(arcs, f, indent=2)
    except Exception as e:
        print(f"[narrative-arc-tracker] Save error: {e}")


def get_active_arcs() -> list:
    """
    Return list of currently active narrative arcs.

    Returns:
        List of arc dicts with name, description, target, and progress fields.
    """
    try:
        arcs = _load_arcs()
        return [a for a in arcs if a.get("active", True)]
    except Exception as e:
        print(f"[narrative-arc-tracker] get_active_arcs error: {e}")
        return list(DEFAULT_ARCS)


def update_arc_progress(lore_text: str) -> None:
    """
    Detect arc-relevant keywords in lore and increment matching arc progress.

    Args:
        lore_text: Recently generated lore string.
    """
    try:
        arcs = _load_arcs()
        text_lower = lore_text.lower()

        for arc in arcs:
            if not arc.get("active", True):
                continue
            keywords = arc.get("keywords", [])
            hits = sum(1 for kw in keywords if kw in text_lower)
            if hits >= 1:
                arc["progress"] = min(100, arc.get("progress", 0) + PROGRESS_INCREMENT * hits)
                if arc["progress"] >= 100:
                    arc["active"] = False
                    arc["completed"] = True

        _save_arcs(arcs)
    except Exception as e:
        print(f"[narrative-arc-tracker] update_arc_progress error: {e}")


def add_arc(name: str, description: str, target: str) -> None:
    """
    Add a new narrative arc to the tracker.

    Args:
        name: Arc name.
        description: Brief description of the arc.
        target: The goal/resolution condition for the arc.
    """
    try:
        arcs = _load_arcs()
        arcs.append({
            "name": name,
            "description": description,
            "target": target,
            "progress": 0,
            "keywords": [],
            "active": True,
        })
        _save_arcs(arcs)
    except Exception as e:
        print(f"[narrative-arc-tracker] add_arc error: {e}")
