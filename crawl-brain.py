"""
crawl-brain.py — GK BRAIN Crawl Agent

Standalone web crawl agent. Checks all official links every 2 hours,
detects new content, and writes discovered updates to crawl-results.json.

gk-brain.py reads crawl-results.json at startup instead of doing crawls inline.

Includes dedup fingerprinting so the same content is never flagged twice.

Usage:
    python crawl-brain.py

Writes:
    crawl-results.json  — latest crawl results (read by gk-brain.py)
"""

import datetime
import hashlib
import json
import os
import sys
import time
import importlib.util as _ilu
import pathlib as _pl

import requests
from bs4 import BeautifulSoup


def _load_module(name: str, filepath: str):
    spec = _ilu.spec_from_file_location(name, _pl.Path(__file__).parent / filepath)
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _safe_load(name: str, filepath: str):
    """Load a module, returning None on failure (non-fatal)."""
    try:
        return _load_module(name, filepath)
    except Exception as exc:
        print(f"[crawl-brain] Could not load {filepath}: {exc}")
        return None


# ---------------------------------------------------------------------------
# Load helper modules
# ---------------------------------------------------------------------------

_update_detector = _safe_load("update_detector", "update-detector.py")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

BASE_DIR          = os.path.dirname(__file__)
CRAWL_RESULTS_FILE = os.path.join(BASE_DIR, "crawl-results.json")
FINGERPRINT_FILE  = os.path.join(BASE_DIR, "crawl-fingerprints.json")

# All official links to check
URLS_TO_CHECK = [
    # Official GK & Moonboys
    "https://graffitikings.co.uk/",
    "https://graffpunks.live/",
    "https://gkniftyheads.com/",
    "https://graffpunks.substack.com/",
    "https://substack.com/@graffpunks/posts",
    "https://www.youtube.com/@GKniftyHEADS",
    "https://www.facebook.com/GraffPUNKS.Network/",
    "https://medium.com/@GKniftyHEADS",
    "https://medium.com/@games4punks",
    "https://medium.com/@HODLWARRIORS",
    "https://medium.com/@graffpunksuk",
    "https://medium.com/@GRAFFITIKINGS",
    "https://x.com/GraffPunks",
    "https://x.com/GKNiFTYHEADS",
    "https://x.com/GraffitiKings",
    "https://neftyblocks.com/collection/gkstonedboys",
    "https://neftyblocks.com/collection/noballgamess",
    "https://nfthive.io/collection/noballgamess",
    "https://dappradar.com/nft-collection/crypto-moonboys",
    # Charlie Buster & Treef
    "https://medium.com/@iamcharliebuster",
    "https://medium.com/@treefproject",
    "https://substack.com/@treefproject/posts",
    "https://substack.com/@noballgames/posts",
    "https://x.com/nftbuster",
    # Real-people & extra canon
    "https://medium.com/@boneidolink",
    "https://deliciousagainpeter.com/",
    "https://www.reddit.com/user/graffpunks/",
]

REQUEST_TIMEOUT = 15
CRAWL_DELAY     = 1.5  # seconds between requests


# ---------------------------------------------------------------------------
# Fingerprint helpers
# ---------------------------------------------------------------------------

def _load_fingerprints() -> set:
    """Load previously seen content fingerprints."""
    if os.path.exists(FINGERPRINT_FILE):
        try:
            with open(FINGERPRINT_FILE, "r", encoding="utf-8") as fh:
                return set(json.load(fh))
        except (json.JSONDecodeError, OSError):
            return set()
    return set()


def _save_fingerprints(fingerprints: set) -> None:
    try:
        with open(FINGERPRINT_FILE, "w", encoding="utf-8") as fh:
            # Keep only last 5000 fingerprints to prevent unbounded growth
            fp_list = sorted(fingerprints)[-5000:]
            json.dump(fp_list, fh)
    except OSError as exc:
        print(f"[crawl-brain] Could not save fingerprints: {exc}")


def _fingerprint(text: str) -> str:
    """Create a short MD5 fingerprint of normalised text."""
    clean = " ".join(text.lower().split())[:500]
    return hashlib.md5(clean.encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Crawl helpers
# ---------------------------------------------------------------------------

def _fetch_page(url: str) -> str | None:
    """Fetch a URL and return text content, or None on failure."""
    try:
        headers = {"User-Agent": "GK-BRAIN-CrawlBot/1.0 (+https://gkniftyheads.com/)"}
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        # Remove script/style noise
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:3000]
    except Exception as exc:
        print(f"[crawl-brain] Failed to fetch {url}: {exc}")
        return None


def _extract_title(url: str, content: str) -> str:
    """Extract a meaningful title from content or fall back to domain."""
    lines = [l.strip() for l in content.splitlines() if l.strip()]
    if lines:
        return lines[0][:80]
    return url.split("/")[2] if "/" in url else url[:80]


def _classify_url(url: str) -> str:
    """Classify a URL into a content category using proper domain matching."""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        # Use netloc (e.g. 'substack.com' or 'www.substack.com') for comparison.
        # Strip 'www.' prefix and lower-case for consistent matching.
        host = parsed.netloc.lower().lstrip("www.")
    except Exception:
        return "website"

    if host == "substack.com" or host.endswith(".substack.com"):
        return "substack"
    if host == "medium.com" or host.endswith(".medium.com"):
        return "medium"
    if host in ("x.com", "twitter.com"):
        return "twitter"
    if host == "youtube.com" or host.endswith(".youtube.com"):
        return "youtube"
    if host == "neftyblocks.com" or host == "atomichub.io":
        return "nft-marketplace"
    if host == "dappradar.com":
        return "nft-analytics"
    if host == "reddit.com" or host.endswith(".reddit.com"):
        return "reddit"
    return "website"


# ---------------------------------------------------------------------------
# Main crawl
# ---------------------------------------------------------------------------

def crawl_all() -> dict:
    """
    Crawl all URLs, detect new content, return structured results.
    Skips content already seen (via fingerprint).
    """
    now = datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z")
    fingerprints = _load_fingerprints()
    new_results = []
    checked = 0
    new_count = 0

    for url in URLS_TO_CHECK:
        content = _fetch_page(url)
        checked += 1

        if not content:
            time.sleep(CRAWL_DELAY)
            continue

        fp = _fingerprint(content)
        if fp in fingerprints:
            print(f"[crawl-brain] No change: {url[:60]}")
        else:
            print(f"[crawl-brain] NEW content: {url[:60]}")
            fingerprints.add(fp)
            new_count += 1
            new_results.append({
                "url": url,
                "category": _classify_url(url),
                "title": _extract_title(url, content),
                "content": content[:500],
                "fingerprint": fp,
                "detected_at": now,
                "used_in_lore": False,
            })

        time.sleep(CRAWL_DELAY)

    _save_fingerprints(fingerprints)

    results = {
        "last_crawl": now,
        "checked_urls": checked,
        "new_items": new_count,
        "results": new_results,
    }
    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run() -> int:
    """
    Run crawl pipeline.
    Returns exit code (0 = success, 1 = error).
    """
    print("[crawl-brain] 🧠 Crawl Brain starting…")

    # If update-detector module is available, use it for full crawl capability
    if _update_detector is not None:
        try:
            print("[crawl-brain] Using update-detector module…")
            detector_result = _update_detector.detect_updates()
            now = datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z")
            results = {
                "last_crawl": now,
                "checked_urls": len(URLS_TO_CHECK),
                "new_items": len(detector_result.get("updates", [])),
                "results": [
                    {**u, "used_in_lore": False}
                    for u in detector_result.get("updates", [])
                ],
            }
        except Exception as exc:
            print(f"[crawl-brain] update-detector failed ({exc}); falling back to built-in crawl.")
            results = crawl_all()
    else:
        results = crawl_all()

    # Save results
    try:
        crawl_results_file = os.path.join(BASE_DIR, "crawl-results.json")
        with open(crawl_results_file, "w", encoding="utf-8") as fh:
            json.dump(results, fh, indent=2, ensure_ascii=False)
        print(
            f"[crawl-brain] ✅ Crawl complete — "
            f"{results['new_items']} new items from {results['checked_urls']} URLs."
        )
        print(f"[crawl-brain] Results saved to crawl-results.json")
        return 0
    except Exception as exc:
        print(f"[crawl-brain] ❌ Failed to save results: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(run())
