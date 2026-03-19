"""
comparative-analysis-system.py - Comparative Analysis System for GK BRAIN

Compares performance across different lore types to identify what resonates
and provides actionable insights for content optimisation.

Usage (from gk-brain.py):
    from comparative_analysis_system import get_performance_insights
    insights = get_performance_insights()
"""

import json
import os

BASE_DIR = os.path.dirname(__file__)
ANALYSIS_FILE = os.path.join(BASE_DIR, "comparative-analysis.json")

DEFAULT_INSIGHTS = {
    "top_patterns": [
        "fishing + philosophy: consistently high quality scores",
        "rave + graffiti combo: strong engagement signals",
        "nft + art connection: community resonance",
        "morning session posts: authenticity premium",
    ],
    "weak_patterns": [
        "pure crypto news without character anchor: low engagement",
        "disconnected events without causal thread: below average",
        "very short posts under 150 chars: consistently lower scores",
    ],
    "observations": [
        "Posts with specific place names outperform generic ones",
        "Sensory detail correlates with quality scores",
        "Callbacks to past events improve continuity scores",
    ],
    "cycle_count": 0,
}


def _load_analysis() -> dict:
    if os.path.exists(ANALYSIS_FILE):
        try:
            with open(ANALYSIS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return dict(DEFAULT_INSIGHTS)


def get_performance_insights() -> str:
    """
    Return performance insights comparing different lore types.

    Returns:
        Formatted insights string for AI prompt guidance.
    """
    try:
        analysis = _load_analysis()

        lines = ["=== COMPARATIVE PERFORMANCE INSIGHTS ==="]

        top = analysis.get("top_patterns", DEFAULT_INSIGHTS["top_patterns"])
        lines.append("\nTop performing patterns:")
        for p in top[:4]:
            lines.append(f"  + {p}")

        weak = analysis.get("weak_patterns", DEFAULT_INSIGHTS["weak_patterns"])
        lines.append("\nUnderperforming patterns (avoid):")
        for p in weak[:3]:
            lines.append(f"  - {p}")

        obs = analysis.get("observations", DEFAULT_INSIGHTS["observations"])
        lines.append("\nKey observations:")
        for o in obs[:3]:
            lines.append(f"  * {o}")

        lines.append(
            "\nAPPLY: Use top patterns as templates. Avoid weak patterns. "
            "Let observations guide craft decisions."
        )

        return "\n".join(lines)
    except Exception as e:
        print(f"[comparative-analysis] Error: {e}")
        return "Performance insights unavailable. Apply general best practices."
