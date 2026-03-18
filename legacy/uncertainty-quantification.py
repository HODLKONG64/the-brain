"""
uncertainty-quantification.py — Uncertainty Quantification for GK BRAIN

Tracks and communicates confidence levels for all data and generated content.
Provides aggregate confidence scores and identifies low-confidence data points.

Usage (from gk-brain.py):
    from uncertainty_quantification import quantify_uncertainty, check_confidence_threshold
    unc = quantify_uncertainty(updates)
    reliable = check_confidence_threshold(updates, threshold=0.3)
"""

import os

BASE_DIR = os.path.dirname(__file__)


def quantify_uncertainty(updates: list) -> dict:
    """
    Calculate aggregate confidence statistics across all updates.

    Args:
        updates: List of update dicts, each optionally with a 'confidence' key.

    Returns:
        Dict with keys: aggregate_confidence, low_confidence_items,
        high_confidence_items, recommendation.
    """
    try:
        if not updates:
            return {
                "aggregate_confidence": 0.0,
                "low_confidence_items": [],
                "high_confidence_items": [],
                "recommendation": "No updates available. Generate from world state only.",
            }

        scores = [float(u.get("confidence", 0.5)) for u in updates]
        avg = sum(scores) / len(scores)

        low = [u for u in updates if float(u.get("confidence", 0.5)) < 0.4]
        high = [u for u in updates if float(u.get("confidence", 0.5)) >= 0.7]

        if avg >= 0.7:
            recommendation = "High confidence data available. Generate with strong real-world integration."
        elif avg >= 0.5:
            recommendation = "Moderate confidence. Blend real data with character-driven narrative."
        else:
            recommendation = "Low confidence data. Weight character voice and world state over data."

        return {
            "aggregate_confidence": round(avg, 3),
            "low_confidence_items": [u.get("title", "unknown")[:40] for u in low],
            "high_confidence_items": [u.get("title", "unknown")[:40] for u in high],
            "recommendation": recommendation,
        }
    except Exception as e:
        print(f"[uncertainty-quantification] Error: {e}")
        return {
            "aggregate_confidence": 0.5,
            "low_confidence_items": [],
            "high_confidence_items": [],
            "recommendation": "Proceed with balanced narrative approach.",
        }


def check_confidence_threshold(updates: list, threshold: float = 0.3) -> list:
    """
    Filter updates to those meeting the minimum confidence threshold.

    Args:
        updates: List of update dicts.
        threshold: Minimum confidence score (default 0.3).

    Returns:
        Filtered list containing only updates at or above the threshold.
    """
    try:
        return [u for u in updates if float(u.get("confidence", 0.5)) >= threshold]
    except Exception as e:
        print(f"[uncertainty-quantification] check_confidence_threshold error: {e}")
        return updates
