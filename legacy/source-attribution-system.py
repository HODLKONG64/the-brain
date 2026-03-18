"""
source-attribution-system.py - Source Attribution System for GK BRAIN

Tags every data point with full metadata for transparent attribution.
Adds human-readable attribution strings to all updates.

Usage (from gk-brain.py):
    from source_attribution_system import attribute_updates
    attributed = attribute_updates(updates)
"""

import datetime
import os

BASE_DIR = os.path.dirname(__file__)

SOURCE_DISPLAY_NAMES = {
    "graffpunks.substack.com": ("GraffPUNKS Substack", "verified", "high"),
    "graffpunks.live": ("GraffPUNKS Live", "verified", "high"),
    "gkniftyheads.com": ("GKniftyHEADS Official", "verified", "high"),
    "graffitikings.co.uk": ("GraffitiKings UK", "verified", "high"),
    "neftyblocks.com": ("NeftyBlocks NFT Market", "verified", "medium"),
    "nfthive.io": ("NFT Hive", "verified", "medium"),
    "dappradar.com": ("DappRadar", "verified", "medium"),
    "carpology.net": ("Carpology Magazine", "verified", "high"),
    "totalcarp.co.uk": ("Total Carp", "verified", "high"),
    "coindesk.com": ("CoinDesk", "verified", "high"),
    "cointelegraph.com": ("CoinTelegraph", "verified", "high"),
    "streetartnews.net": ("Street Art News", "verified", "medium"),
}


def _get_domain(url: str) -> str:
    try:
        from urllib.parse import urlparse
        return urlparse(url).netloc.lower().replace("www.", "")
    except Exception:
        return ""


def _build_attribution(url: str, confidence: float) -> dict:
    """Build a complete attribution dict for a given URL."""
    domain = _get_domain(url)
    if domain in SOURCE_DISPLAY_NAMES:
        display_name, trust, level = SOURCE_DISPLAY_NAMES[domain]
    else:
        if domain:
            display_name = domain
            trust = "unverified"
            level = "low" if confidence < 0.5 else "medium"
        else:
            display_name = "Unknown Source"
            trust = "unverified"
            level = "low"

    display_text = f"Source: {display_name} ({trust}, {level} confidence)"

    return {
        "source_url": url,
        "source_domain": domain,
        "source_display": display_name,
        "trust_status": trust,
        "confidence_level": level,
        "detection_time": datetime.datetime.utcnow().isoformat(),
        "display_text": display_text,
    }


def attribute_updates(updates: list) -> list:
    """
    Add full attribution metadata to each update.

    Args:
        updates: List of update dicts.

    Returns:
        List of updates each with an 'attribution' dict added.
    """
    try:
        attributed = []
        for u in updates:
            url = u.get("url", "") or u.get("source", "") or ""
            confidence = float(u.get("confidence", 0.5))
            enriched = dict(u)
            enriched["attribution"] = _build_attribution(url, confidence)
            attributed.append(enriched)
        return attributed
    except Exception as e:
        print(f"[source-attribution] Error: {e}")
        return updates
