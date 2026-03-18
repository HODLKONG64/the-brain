"""
crawl-brain.py — GK BRAIN Standalone Web Crawl Brain

Handles ALL web crawling for the 4-brain architecture.
Writes deduplicated results to crawl-results.json.

Usage:
    python crawl-brain.py
"""

import hashlib
import json
import os
import time
import datetime
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(__file__)
RESULTS_FILE = os.path.join(BASE_DIR, "crawl-results.json")
SNAPSHOT_FILE = os.path.join(BASE_DIR, "crawl-snapshot.json")

CRAWL_URLS = [
    "https://graffpunks.substack.com/",
    "https://substack.com/@graffpunks/posts",
    "https://graffpunks.live/",
    "https://gkniftyheads.com/",
    "https://graffitikings.co.uk/",
    "https://www.youtube.com/@GKniftyHEADS",
    "https://medium.com/@GKniftyHEADS",
    "https://medium.com/@graffpunksuk",
    "https://neftyblocks.com/collection/gkstonedboys",
    "https://x.com/GraffPunks",
    "https://x.com/GKNiFTYHEADS",
]

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; GKBrainBot/1.0; "
        "+https://github.com/HODLKONG64/the-brain)"
    )
}


def _fetch(url: str, timeout: int = 15) -> str:
    """Fetch URL and return text content. Returns empty string on error."""
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=timeout)
        resp.raise_for_status()
        return resp.text
    except Exception:
        return ""


def _page_hash(html: str) -> str:
    """Return a stable SHA-256 hash of the visible text of an HTML page."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "meta", "link"]):
        tag.decompose()
    text = " ".join(soup.get_text(separator=" ").split())
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _extract_title(html: str, url: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    h1 = soup.find("h1")
    if h1:
        return h1.get_text(strip=True)
    return url


def _extract_snippet(html: str, max_chars: int = 400) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    for p in soup.find_all("p"):
        text = p.get_text(strip=True)
        if len(text) > 60:
            return text[:max_chars]
    return ""


def _content_fingerprint(title: str, snippet: str) -> str:
    """Create a deduplication fingerprint from title + snippet."""
    combined = (title + " " + snippet[:200]).lower()
    return hashlib.md5(" ".join(combined.split()).encode()).hexdigest()[:16]


def _load_snapshot() -> dict:
    if os.path.exists(SNAPSHOT_FILE):
        try:
            with open(SNAPSHOT_FILE, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_snapshot(snapshot: dict) -> None:
    with open(SNAPSHOT_FILE, "w", encoding="utf-8") as fh:
        json.dump(snapshot, fh, indent=2)


def _load_results() -> list:
    if os.path.exists(RESULTS_FILE):
        try:
            with open(RESULTS_FILE, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError):
            return []
    return []


def _save_results(results: list) -> None:
    with open(RESULTS_FILE, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2)


def _domain_matches(url: str, allowed_domains: list) -> bool:
    """Check if a URL's domain is in the allowed list using urlparse."""
    try:
        netloc = urlparse(url).netloc.lower().replace("www.", "")
        return any(netloc == d.lower().replace("www.", "") for d in allowed_domains)
    except Exception:
        return False


def crawl() -> list:
    """
    Crawl all configured URLs, detect changes, and write new results to
    crawl-results.json with dedup fingerprinting.

    Returns a list of new crawl result dicts.
    """
    snapshot = _load_snapshot()
    existing_results = _load_results()
    existing_fps = {r.get("fingerprint") for r in existing_results if r.get("fingerprint")}

    new_snapshot = dict(snapshot)
    new_results = []

    for url in CRAWL_URLS:
        html = _fetch(url)
        if not html:
            continue

        current_hash = _page_hash(html)
        previous_hash = snapshot.get(url)
        new_snapshot[url] = current_hash

        if previous_hash is None:
            # First crawl — record hash, no result to report
            continue

        if current_hash != previous_hash:
            title = _extract_title(html, url)
            snippet = _extract_snippet(html)
            fp = _content_fingerprint(title, snippet)

            if fp not in existing_fps:
                result = {
                    "url": url,
                    "title": title,
                    "snippet": snippet,
                    "fingerprint": fp,
                    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
                    "used": False,
                }
                new_results.append(result)
                existing_fps.add(fp)

        time.sleep(1)

    _save_snapshot(new_snapshot)

    if new_results:
        all_results = existing_results + new_results
        _save_results(all_results)
        print(f"[crawl-brain] {len(new_results)} new result(s) saved.")
    else:
        print("[crawl-brain] No new changes detected.")

    return new_results


if __name__ == "__main__":
    results = crawl()
    print(json.dumps(results, indent=2))
