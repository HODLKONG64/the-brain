"""
predictive-trend-engine.py - Predictive Trend Engine for GK BRAIN

Forecasts upcoming trends in fishing, NFT, art, and music scenes
based on calendar patterns and seasonal knowledge.

Usage (from gk-brain.py):
    from predictive_trend_engine import get_trend_predictions
    predictions = get_trend_predictions(rule_ctx)
"""

import datetime
import os

BASE_DIR = os.path.dirname(__file__)

MONTHLY_TRENDS = {
    1: {
        "fishing": "Slow. Cold water, carp dormant. Focus on preparation and gear review.",
        "nft": "Market quiet post-Christmas. Reflection and planning phase.",
        "art": "Gallery season starting. Indoor exhibitions active.",
        "rave": "Underground scene continues but outdoor events absent.",
        "overall": "Inward, reflective. Quality over quantity.",
    },
    2: {
        "fishing": "Still quiet. Pre-season anticipation building. Venue scouting.",
        "nft": "Market starting to stir. Early movers positioning.",
        "art": "Studio productivity high. Dark evenings good for creative work.",
        "rave": "Warehouse scene active. Pre-spring energy.",
        "overall": "Patience and craft. Building toward the year ahead.",
    },
    3: {
        "fishing": "Season approaching. First mild sessions possible. Anticipation.",
        "nft": "Spring market activity emerging. New collections launching.",
        "art": "Art fairs begin. Gallery buzz increasing.",
        "rave": "Transition period. Indoor to outdoor shift starting.",
        "overall": "Renewal. The year begins in earnest.",
    },
    4: {
        "fishing": "Season opens properly. Active fishing. Prime carp conditions.",
        "nft": "Spring market active. Good sentiment.",
        "art": "Outdoor murals season begins. Street art active.",
        "rave": "First outdoor events. Season starting.",
        "overall": "Everything coming alive. Peak productive energy.",
    },
    5: {
        "fishing": "Excellent conditions. Long days, feeding fish.",
        "nft": "Momentum building. Community events.",
        "art": "Outdoor art everywhere. Festival season beginning.",
        "rave": "Outdoor raves starting. High energy.",
        "overall": "Full engagement. All scenes active simultaneously.",
    },
    6: {
        "fishing": "Long evenings ideal. Overnight sessions rewarding.",
        "nft": "Market stabilising. Established projects consolidating.",
        "art": "Festival exhibitions. Public art prominent.",
        "rave": "Peak outdoor rave season. Multiple events weekly.",
        "overall": "Midsummer momentum. Everything at full pace.",
    },
    7: {
        "fishing": "Peak summer. Dawn sessions exceptional.",
        "nft": "Summer lull possible. Attention splits.",
        "art": "Major summer exhibitions. International attention.",
        "rave": "Festival season peak. Biggest events of year.",
        "overall": "Abundant. Rich experiences across all domains.",
    },
    8: {
        "fishing": "Late summer. Big fish moving. Monster carp season.",
        "nft": "Late summer market. Activity picking up pre-autumn.",
        "art": "Final summer shows. Autumn previews beginning.",
        "rave": "Late summer events. Season peak winding toward close.",
        "overall": "Harvest mode. Capitalising on the season's richness.",
    },
    9: {
        "fishing": "Autumn crunch. Some of the best fishing of year. Big fish.",
        "nft": "Autumn market awakening. New season energy.",
        "art": "Major gallery season starts. Frieze preview.",
        "rave": "Indoor season returns. Warehouse culture resurgent.",
        "overall": "Deep focus. Serious work begins.",
    },
    10: {
        "fishing": "Heavy autumn sessions. Big carp feeding hard pre-winter.",
        "nft": "Bull market sentiment. Q4 activity.",
        "art": "Frieze London. Peak gallery season.",
        "rave": "Full indoor season. Peak underground activity.",
        "overall": "Intensity. Everything concentrated and vital.",
    },
    11: {
        "fishing": "Slowing. Cold water approaching. Sessions more strategic.",
        "nft": "Year-end market. Strong activity.",
        "art": "Post-Frieze. Studio season deepening.",
        "rave": "Strong indoor season. November events reliable.",
        "overall": "Drawing toward year end. Consolidation and reflection.",
    },
    12: {
        "fishing": "Winter quiet. Occasional sessions. Year review.",
        "nft": "Year-end intensity. Final drops. New year planning.",
        "art": "Christmas exhibitions. Year-end shows.",
        "rave": "NYE events. Underground celebrations.",
        "overall": "Year-end. Maximum significance. Every action weighted.",
    },
}


def get_trend_predictions(rule_ctx: dict) -> str:
    """
    Return seasonal trend predictions for the current month.

    Args:
        rule_ctx: Current rule context dict.

    Returns:
        Formatted trend prediction string for AI prompt.
    """
    try:
        now = datetime.datetime.utcnow()
        month = now.month
        trends = MONTHLY_TRENDS.get(month, MONTHLY_TRENDS[6])

        month_name = now.strftime("%B")
        lines = [f"=== TREND PREDICTIONS: {month_name} ==="]
        for domain, prediction in trends.items():
            lines.append(f"  {domain.upper()}: {prediction}")

        # Next month preview
        next_month = (month % 12) + 1
        next_trends = MONTHLY_TRENDS.get(next_month, {})
        if next_trends.get("overall"):
            next_name = datetime.date(now.year, next_month, 1).strftime("%B")
            lines.append(f"\nNext month ({next_name}) outlook: {next_trends['overall']}")

        return "\n".join(lines)
    except Exception as e:
        print(f"[predictive-trend] Error: {e}")
        return "Trend data unavailable. Proceed with character-driven narrative."
