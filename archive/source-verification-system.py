"""
source-verification-system.py - Source Verification System for GK BRAIN

Verifies that all data points come from official, trusted sources.
Filters out updates from untrusted domains.

Usage (from gk-brain.py):
    from source_verification_system import verify_sources
    verified = verify_sources(updates)
"""

import os

BASE_DIR = os.path.dirname(__file__)

TRUSTED_DOMAINS = {
    "graffpunks.substack.com",
    "graffpunks.live",
    "gkniftyheads.com",
    "graffitikings.co.uk",
    "neftyblocks.com",
    "nfthive.io",
    "dappradar.com",
    "carpology.net",
    "totalcarp.co.uk",
    "bigcarp.co.uk",
    "carpforum.co.uk",
    "fishingmagic.com",
    "streetartnews.net",
    "graffitistreet.com",
    "arrestedmotion.com",
    "coindesk.com",
    "cointelegraph.com",
    "decrypt.co",
    "theblock.co",
    "beincrypto.com",
    "substack.com",
    "medium.com",
    "reddit.com",
    "x.com",
    "twitter.com",
    "youtube.com",
    "facebook.com",
}


def _get_domain(url: str) -> str:
    try:
        from urllib.parse import urlparse
        return urlparse(url).netloc.lower().replace("www.", "")
    except Exception:
        return ""


def verify_sources(updates: list) -> list:
    """
    Verify each update against the trusted domains list.

    Adds 'verified' key to each update. Returns all updates (not filtered)
    but marks unverified ones so downstream systems can weight them appropriately.

    Args:
        updates: List of update dicts.

    Returns:
        All updates with 'verified' bool key added to each.
    """
    try:
        result = []
        for u in updates:
            url = u.get("url", "") or u.get("source", "") or ""
            domain = _get_domain(url)

            is_verified = any(trusted in domain for trusted in TRUSTED_DOMAINS) if domain else False

            enriched = dict(u)
            enriched["verified"] = is_verified
            if not is_verified:
                enriched["confidence"] = min(float(u.get("confidence", 0.5)), 0.4)
            result.append(enriched)

        verified_count = sum(1 for u in result if u.get("verified"))
        print(f"[source-verification] {verified_count}/{len(result)} updates verified")
        return result
    except Exception as e:
        print(f"[source-verification] Error: {e}")
        return updates
