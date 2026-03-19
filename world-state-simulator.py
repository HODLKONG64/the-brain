"""
world-state-simulator.py - World State Simulator for GK BRAIN

Simulates realistic world state for UK fishing, art, NFT, and crypto
environments based on current UTC time and calendar.

Usage (from gk-brain.py):
    from world_state_simulator import get_world_state
    state = get_world_state(rule_ctx)
"""

import datetime
import os

BASE_DIR = os.path.dirname(__file__)

FISHING_SEASON_MONTHS = {4, 5, 6, 7, 8, 9, 10}
RAVE_SEASON_MONTHS = {4, 5, 6, 7, 8, 9, 10}
ART_ACTIVE_MONTHS = {2, 3, 4, 5, 9, 10, 11}

MONTHLY_NFT_TREND = {
    1: "bear", 2: "neutral", 3: "neutral",
    4: "bull", 5: "bull", 6: "neutral",
    7: "neutral", 8: "bull", 9: "bull",
    10: "bull", 11: "bull", 12: "neutral",
}

MONTHLY_CRYPTO_SENTIMENT = {
    1: "cautious", 2: "building", 3: "optimistic",
    4: "active", 5: "active", 6: "volatile",
    7: "volatile", 8: "recovering", 9: "bullish",
    10: "peak", 11: "high", 12: "year-end frenzy",
}


def _is_weather_favorable(month: int, hour: int) -> bool:
    """Estimate if conditions are broadly favourable for outdoor activity."""
    good_weather_months = {4, 5, 6, 7, 8, 9}
    good_hours = set(range(5, 22))
    return month in good_weather_months and hour in good_hours


def get_world_state(rule_ctx: dict) -> dict:
    """
    Return a dict representing the current simulated world state.

    Keys:
        fishing_season (bool): Carp season active.
        weather_favorable (bool): Broadly good conditions for outdoor activity.
        nft_market_trend (str): 'bull', 'bear', or 'neutral'.
        art_scene_active (bool): Gallery/street art scene active.
        crypto_sentiment (str): Current crypto market mood.
        rave_season (bool): Outdoor rave season active.

    Args:
        rule_ctx: Current rule context dict.

    Returns:
        World state dict.
    """
    try:
        now = datetime.datetime.utcnow()
        month = now.month
        hour = now.hour

        return {
            "fishing_season": month in FISHING_SEASON_MONTHS,
            "weather_favorable": _is_weather_favorable(month, hour),
            "nft_market_trend": MONTHLY_NFT_TREND.get(month, "neutral"),
            "art_scene_active": month in ART_ACTIVE_MONTHS,
            "crypto_sentiment": MONTHLY_CRYPTO_SENTIMENT.get(month, "neutral"),
            "rave_season": month in RAVE_SEASON_MONTHS,
            "month": month,
            "hour_utc": hour,
        }
    except Exception as e:
        print(f"[world-state-simulator] Error: {e}")
        return {
            "fishing_season": True,
            "weather_favorable": True,
            "nft_market_trend": "neutral",
            "art_scene_active": True,
            "crypto_sentiment": "neutral",
            "rave_season": True,
        }
