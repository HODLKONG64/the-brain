"""
update-detector.py — Intelligent Update Detection for GK BRAIN

Crawls all official GK websites, compares against the last saved snapshot,
classifies any detected changes, and returns structured JSON.

Usage (from gk-brain.py):
    from update_detector import detect_updates
    result = detect_updates()
    # result: {"detected": bool, "updates": [...]}
"""

import hashlib
import json
import os
import re
import time
import datetime

import requests
from bs4 import BeautifulSoup

SNAPSHOT_FILE = os.path.join(os.path.dirname(__file__), "crawl-snapshot.json")

# ---------------------------------------------------------------------------
# Noise-reduction keyword guards
# ---------------------------------------------------------------------------

_RAVE_KEYWORDS = re.compile(
    r"\b(drum.?bass|dnb|rave|jungle|techno|dj.?set|club|lineup|festival|tickets|skiddle|ticketmaster|resident.?advisor)\b",
    re.IGNORECASE,
)

_NEWS_KEYWORDS = re.compile(
    r"\b(bitcoin|crypto|nft|blockchain|moonboys|graffpunks|hodl|defi|token|altcoin|eth|solana)\b",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# URL catalogue (mirrors gkandcryptomoonboywebsitestosave.md)
# ---------------------------------------------------------------------------

URLS_BY_CATEGORY = {
    "gkdata-real": [
        "https://graffpunks.substack.com/",
        "https://substack.com/@graffpunks/posts",
        "https://graffpunks.live/",
        "https://gkniftyheads.com/",
        "https://graffitikings.co.uk/",
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
        "https://medium.com/@iamcharliebuster",
        "https://medium.com/@treefproject",
        "https://substack.com/@treefproject/posts",
        "https://substack.com/@noballgames/posts",
        "https://x.com/nftbuster",
        "https://medium.com/@boneidolink",
        "https://deliciousagainpeter.com/",
        "https://www.reddit.com/user/graffpunks/",
    ],
    "news-real": [
        "https://www.coindesk.com/",
        "https://cointelegraph.com/",
        "https://beincrypto.com/",
        "https://decrypt.co/",
        "https://theblock.co/",
        "https://bitcoinmagazine.com/",
        "https://cryptoslate.com/",
        "https://blockworks.co/",
    ],
    "graffiti-news-real": [
        "https://streetartnews.net/",
        "https://www.graffitistreet.com/news/",
        "https://www.graffitiartmagazine.com/",
        "https://arrestedmotion.com/",
    ],
    "fishing-real": [
        "https://www.bigcarp.co.uk/",
        "https://www.carpology.net/",
        "https://www.totalcarp.co.uk/",
        "https://www.carpforum.co.uk/",
        "https://www.fishingmagic.com/",
        "https://www.angling-direct.co.uk/blogs/news",
    ],
    "rave-real": [
        "https://www.residentadvisor.net/events/uk/london/genre/drum-bass",
        "https://www.ticketmaster.co.uk/discover/concerts-music/drum-and-bass",
        "https://www.skiddle.com/whats-on/genre/drum-bass/",
    ],
}

# Minimum carp weight (lbs) to report as fishing-real news
CARP_MIN_WEIGHT_LB = 40
CARP_MAX_HOURS = 70


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fetch(url: str, timeout: int = 15) -> str:
    """Fetch a URL and return its text content. Returns empty string on error."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; GKBrainBot/1.0; "
            "+https://github.com/HODLKONG64/the-brain)"
        )
    }
    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp.text
    except Exception:
        return ""


def _page_hash(html: str) -> str:
    """Return a stable SHA-256 hash of the visible text of an HTML page."""
    soup = BeautifulSoup(html, "html.parser")
    # Remove script/style noise
    for tag in soup(["script", "style", "noscript", "meta", "link"]):
        tag.decompose()
    text = " ".join(soup.get_text(separator=" ").split())
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _extract_title(html: str, url: str) -> str:
    """Extract the most relevant title/headline from a page."""
    soup = BeautifulSoup(html, "html.parser")
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    h1 = soup.find("h1")
    if h1:
        return h1.get_text(strip=True)
    return url


def _extract_snippet(html: str, max_chars: int = 400) -> str:
    """Extract the first meaningful text block from a page."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    paragraphs = soup.find_all("p")
    for p in paragraphs:
        text = p.get_text(strip=True)
        if len(text) > 60:
            return text[:max_chars]
    return ""


# ---------------------------------------------------------------------------
# Snapshot management
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Classification helpers
# ---------------------------------------------------------------------------

_FISHING_WEIGHT_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*(?:lb|lbs|pound|pounds)", re.IGNORECASE
)
_FISHING_KEYWORDS = re.compile(
    r"\b(carp|mirror|common|leather|ghost|koi|bream|tench)\b", re.IGNORECASE
)
_NFT_KEYWORDS = re.compile(
    r"\b(nft|drop|mint|collection|moonboys?|graffpunks?|hodl|blocktopia)\b",
    re.IGNORECASE,
)
_RAVE_KEYWORDS = re.compile(
    r"\b(drum.?bass|dnb|jungle|rave|dj set|london|bristol|manchester|uk tour|tickets?|event)\b",
    re.IGNORECASE,
)
_NEWS_KEYWORDS = re.compile(
    r"\b(bitcoin|ethereum|nft|defi|crypto|blockchain|web3|token|mint|drop|graffiti|street art)\b",
    re.IGNORECASE,
)


def _is_significant_carp_catch(text: str) -> bool:
    """Return True if text contains a carp catch >= CARP_MIN_WEIGHT_LB."""
    if not _FISHING_KEYWORDS.search(text):
        return False
    for m in _FISHING_WEIGHT_RE.finditer(text):
        try:
            if float(m.group(1)) >= CARP_MIN_WEIGHT_LB:
                return True
        except ValueError:
            pass
    return False


def _classify_update(category: str, html: str, url: str) -> dict | None:
    """
    Build a structured update dict for a changed page.
    Returns None if the change is not significant enough.
    """
    title = _extract_title(html, url)
    content = _extract_snippet(html)
    timestamp = datetime.datetime.utcnow().isoformat() + "Z"
    combined = (title + " " + content).lower()

    if category == "fishing-real":
        if not _is_significant_carp_catch(combined):
            return None

    if category == "rave-real":
        if not _RAVE_KEYWORDS.search(combined):
            return None

    if category == "news-real":
        if not _NEWS_KEYWORDS.search(combined):
            return None

    return {
        "type": category,
        "source": url,
        "title": title,
        "content": content,
        "timestamp": timestamp,
        "used": False,
        "wiki_update": True,
        "wiki_done": False,
        "lore_weight": 0.05 if category in ("fishing-real", "graffiti-news-real") else 0.10,
    }


# ---------------------------------------------------------------------------
# Main public function
# ---------------------------------------------------------------------------

def detect_updates() -> dict:
    """
    Crawl all URLs, compare against last snapshot, classify changes.

    Returns:
        {
            "detected": bool,
            "updates": [
                {
                    "type": str,      # e.g. "gkdata-real"
                    "source": str,
                    "title": str,
                    "content": str,
                    "timestamp": str,
                    "used": bool,
                    "wiki_update": bool,
                    "wiki_done": bool,
                    "lore_weight": float,
                }
            ]
        }
    """
    snapshot = _load_snapshot()
    new_snapshot = dict(snapshot)  # start with existing, update as we go
    updates = []

    for category, urls in URLS_BY_CATEGORY.items():
        for url in urls:
            html = _fetch(url)
            if not html:
                # Can't reach the page — skip but keep old hash if present
                continue

            current_hash = _page_hash(html)
            previous_hash = snapshot.get(url)

            new_snapshot[url] = current_hash

            if previous_hash is None:
                # First ever crawl — record hash, no update to report
                continue

            if current_hash != previous_hash:
                update = _classify_update(category, html, url)
                if update:
                    updates.append(update)

            # Small polite delay between requests
            time.sleep(1)

    _save_snapshot(new_snapshot)

    return {
        "detected": len(updates) > 0,
        "updates": updates,
    }


# ---------------------------------------------------------------------------
# CLI self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Running update detector…")
    result = detect_updates()
    print(json.dumps(result, indent=2))
