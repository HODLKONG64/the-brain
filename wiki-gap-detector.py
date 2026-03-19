"""
wiki-gap-detector.py — GK BRAIN Wiki Gap Detector

Detects content that exists on official sources but is MISSING from the
GKniftyHEADS Fandom wiki. This is fundamentally different from crawl-brain.py:

- crawl-brain fingerprints homepages (broken — always says 0 new items)
- wiki-gap-detector extracts INDIVIDUAL article links/titles from each source
  and compares them against what is already documented on the wiki.

Gap detection strategy:
  1. For each source URL, extract a list of (title, url) article links
     — using RSS/Atom feed if available, HTML link scraping as fallback.
  2. Fetch the current wiki page content.
  3. For each article: if neither the article URL nor a normalised title
     substring appears anywhere in the wiki text → it's a GAP.
  4. Log gaps to wiki-gap-report.json.
  5. Queue gaps into wiki-update-queue.json for wiki-brain.py to push.

Usage:
    python wiki-gap-detector.py [--dry-run] [--verbose]

Writes:
    wiki-gap-report.json      — full gap report (all sources, all gaps)
    wiki-update-queue.json    — appends new gap items (if not dry-run)

Environment variables:
    FANDOM_WIKI_URL   Wiki base URL (default: https://gkniftyheads.fandom.com)
    FANDOM_BOT_USER   Fandom bot username (for wiki read)
    FANDOM_BOT_PASSWORD / FANDOM_PASSWORD  Fandom bot password
    WIKI_DRY_RUN      Set to "1" to skip queue writes
"""

import argparse
import datetime
import hashlib
import importlib.util
import json
import logging
import os
import re
import sys
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("wiki-gap-detector")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GAP_REPORT_FILE = os.path.join(BASE_DIR, "wiki-gap-report.json")
QUEUE_FILE = os.path.join(BASE_DIR, "wiki-update-queue.json")

MAIN_WIKI_PAGE = "GKniftyHEADS_Wiki"
AGENT_LOG_PAGE = "GK_BRAIN_Agent_Log"

REQUEST_TIMEOUT = 15
CRAWL_DELAY = 1.2   # seconds between HTTP calls
MAX_ARTICLES_PER_SOURCE = 30  # cap per source to avoid overloading queue

DRY_RUN: bool = os.environ.get("WIKI_DRY_RUN", "0") == "1"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; GKBrainWikiGapBot/1.0; "
        "+https://github.com/HODLKONG64/the-brain)"
    )
}

# ---------------------------------------------------------------------------
# Source definitions
# Tuple: (label, homepage_url, rss_url_or_None, update_type)
#
# RSS/Atom URLs are tried first. If None, HTML scraping is used.
# update_type maps to wiki-smart-merger.py SECTION_MAP keys.
# ---------------------------------------------------------------------------

SOURCES = [
    # GK & GraffPunks — Substack (has RSS)
    (
        "graffpunks-substack",
        "https://graffpunks.substack.com/",
        "https://graffpunks.substack.com/feed",
        "news-real",
    ),
    (
        "graffpunks-substack-posts",
        "https://substack.com/@graffpunks/posts",
        "https://graffpunks.substack.com/feed",
        "news-real",
    ),
    # Treef — Substack
    (
        "treef-substack",
        "https://substack.com/@treefproject/posts",
        "https://treefproject.substack.com/feed",
        "news-real",
    ),
    # NoballGames — Substack
    (
        "noballgames-substack",
        "https://substack.com/@noballgames/posts",
        "https://noballgames.substack.com/feed",
        "news-real",
    ),
    # Medium authors — Medium has RSS at medium.com/feed/@author
    (
        "medium-gkniftyheads",
        "https://medium.com/@GKniftyHEADS",
        "https://medium.com/feed/@GKniftyHEADS",
        "news-real",
    ),
    (
        "medium-games4punks",
        "https://medium.com/@games4punks",
        "https://medium.com/feed/@games4punks",
        "news-real",
    ),
    (
        "medium-hodlwarriors",
        "https://medium.com/@HODLWARRIORS",
        "https://medium.com/feed/@HODLWARRIORS",
        "news-real",
    ),
    (
        "medium-graffpunksuk",
        "https://medium.com/@graffpunksuk",
        "https://medium.com/feed/@graffpunksuk",
        "news-real",
    ),
    (
        "medium-graffitikings",
        "https://medium.com/@GRAFFITIKINGS",
        "https://medium.com/feed/@GRAFFITIKINGS",
        "graffiti-news-real",
    ),
    (
        "medium-charliebuster",
        "https://medium.com/@iamcharliebuster",
        "https://medium.com/feed/@iamcharliebuster",
        "news-real",
    ),
    (
        "medium-treef",
        "https://medium.com/@treefproject",
        "https://medium.com/feed/@treefproject",
        "news-real",
    ),
    (
        "medium-boneidolink",
        "https://medium.com/@boneidolink",
        "https://medium.com/feed/@boneidolink",
        "news-real",
    ),
    # Official websites — HTML scraping only
    (
        "graffitikings-website",
        "https://graffitikings.co.uk/",
        None,
        "graffiti-news-real",
    ),
    (
        "graffpunks-live",
        "https://graffpunks.live/",
        None,
        "news-real",
    ),
    (
        "gkniftyheads-website",
        "https://gkniftyheads.com/",
        None,
        "news-real",
    ),
    (
        "deliciousagainpeter",
        "https://deliciousagainpeter.com/",
        None,
        "news-real",
    ),
    # Reddit — HTML scraping
    (
        "reddit-graffpunks",
        "https://www.reddit.com/user/graffpunks/",
        None,
        "news-real",
    ),
    # NFT marketplaces — HTML scraping
    (
        "neftyblocks-gkstonedboys",
        "https://neftyblocks.com/collection/gkstonedboys",
        None,
        "gkdata-real",
    ),
    (
        "neftyblocks-noballgamess",
        "https://neftyblocks.com/collection/noballgamess",
        None,
        "gkdata-real",
    ),
    (
        "nfthive-noballgamess",
        "https://nfthive.io/collection/noballgamess",
        None,
        "gkdata-real",
    ),
    (
        "dappradar-cryptomoonboys",
        "https://dappradar.com/nft-collection/crypto-moonboys",
        None,
        "gkdata-real",
    ),
]

# ---------------------------------------------------------------------------
# fandom_auth loader
# ---------------------------------------------------------------------------

def _load_fandom_auth():
    """Load fandom_auth.py. Returns module or None."""
    path = os.path.join(BASE_DIR, "fandom_auth.py")
    if not os.path.exists(path):
        return None
    spec = importlib.util.spec_from_file_location("fandom_auth", path)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
        return mod
    except Exception as exc:
        logger.warning("Could not load fandom_auth.py: %s", exc)
        return None

# ---------------------------------------------------------------------------
# RSS / Atom feed parser
# ---------------------------------------------------------------------------

def _parse_rss_feed(feed_url: str) -> list:
    """
    Fetch and parse an RSS or Atom feed.

    Returns a list of dicts: [{"title": str, "url": str, "published": str}]
    Returns empty list on failure.
    """
    try:
        resp = requests.get(
            feed_url, headers=_HEADERS, timeout=REQUEST_TIMEOUT
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "xml")

        items = []

        # RSS 2.0
        for item in soup.find_all("item", limit=MAX_ARTICLES_PER_SOURCE):
            title = item.find("title")
            link = item.find("link")
            pub = item.find("pubDate") or item.find("dc:date")
            if title and link:
                items.append({
                    "title": title.get_text(strip=True),
                    "url": link.get_text(strip=True),
                    "published": pub.get_text(strip=True) if pub else "",
                })

        # Atom
        if not items:
            for entry in soup.find_all("entry", limit=MAX_ARTICLES_PER_SOURCE):
                title = entry.find("title")
                link = entry.find("link")
                pub = entry.find("published") or entry.find("updated")
                href = ""
                if link:
                    href = link.get("href", "") or link.get_text(strip=True)
                if title and href:
                    items.append({
                        "title": title.get_text(strip=True),
                        "url": href,
                        "published": pub.get_text(strip=True) if pub else "",
                    })

        return items

    except Exception as exc:
        logger.debug("RSS parse failed for %s: %s", feed_url, exc)
        return []


# ---------------------------------------------------------------------------
# HTML article link scraper (fallback when no RSS)
# ---------------------------------------------------------------------------

def _scrape_article_links(page_url: str) -> list:
    """
    Scrape a page for article/post links.

    Heuristics:
    - Links containing /post/, /article/, /p/, /r/, /collection/ in the path
    - Links with meaningful text (>10 chars, not just a domain name)
    - Deduplication by URL

    Returns list of dicts: [{"title": str, "url": str, "published": ""}]
    """
    try:
        resp = requests.get(
            page_url, headers=_HEADERS, timeout=REQUEST_TIMEOUT
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        base_domain = urlparse(page_url).netloc
        seen_urls: set = set()
        items = []

        # Article path patterns — broad enough to catch most CMS structures
        article_path_re = re.compile(
            r"/(post|article|p|r|s|collection|blog|news|story|nft|drop|update)/",
            re.IGNORECASE,
        )

        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            text = a.get_text(strip=True)

            # Skip empty, javascript, anchor-only links
            if not href or href.startswith("#") or href.startswith("javascript"):
                continue

            # Resolve relative URLs
            full_url = urljoin(page_url, href)

            # Only keep links on the same domain or substack/medium subdomains
            parsed = urlparse(full_url)
            if parsed.netloc != base_domain:
                # Allow cross-subdomain for Substack / Medium
                if not (
                    base_domain == "substack.com" or base_domain.endswith(".substack.com") or
                    base_domain == "medium.com" or base_domain.endswith(".medium.com")
                ):
                    continue

            if full_url in seen_urls:
                continue

            # Must match article path pattern OR have meaningful link text
            path_match = article_path_re.search(parsed.path)
            text_ok = len(text) > 10 and len(text) < 200

            if path_match or text_ok:
                seen_urls.add(full_url)
                items.append({
                    "title": text[:120] if text else full_url,
                    "url": full_url,
                    "published": "",
                })

            if len(items) >= MAX_ARTICLES_PER_SOURCE:
                break

        return items

    except Exception as exc:
        logger.debug("HTML scrape failed for %s: %s", page_url, exc)
        return []


# ---------------------------------------------------------------------------
# Article fetcher — RSS first, HTML fallback
# ---------------------------------------------------------------------------

def _fetch_articles(label: str, homepage_url: str, rss_url) -> list:
    """
    Fetch article list for a source. Tries RSS first, falls back to HTML scrape.

    Returns list of dicts: [{"title": str, "url": str, "published": str}]
    """
    articles = []

    if rss_url:
        logger.info("[gap-detector] [%s] Trying RSS: %s", label, rss_url)
        articles = _parse_rss_feed(rss_url)
        if articles:
            logger.info(
                "[gap-detector] [%s] RSS: %d article(s) found", label, len(articles)
            )
            return articles
        else:
            logger.info(
                "[gap-detector] [%s] RSS empty/failed — falling back to HTML scrape",
                label,
            )

    logger.info("[gap-detector] [%s] HTML scrape: %s", label, homepage_url)
    articles = _scrape_article_links(homepage_url)
    logger.info(
        "[gap-detector] [%s] HTML scrape: %d link(s) found", label, len(articles)
    )
    return articles


# ---------------------------------------------------------------------------
# Wiki content fetcher
# ---------------------------------------------------------------------------

def _fetch_wiki_text(fandom_auth, session) -> str:
    """Fetch the full wikitext of the main GK wiki page. Returns '' on failure."""
    try:
        text = fandom_auth.get_page_content(session, MAIN_WIKI_PAGE)
        if text:
            logger.info(
                "[gap-detector] Wiki page fetched: %d chars", len(text)
            )
        else:
            logger.warning("[gap-detector] Wiki page returned empty content.")
        return text or ""
    except Exception as exc:
        logger.error("[gap-detector] Failed to fetch wiki page: %s", exc)
        return ""


# ---------------------------------------------------------------------------
# Gap detection
# ---------------------------------------------------------------------------

def _normalise(text: str) -> str:
    """Lower-case, strip punctuation, collapse whitespace."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return " ".join(text.split())


def _is_in_wiki(article: dict, wiki_text_lower: str) -> bool:
    """
    Return True if this article appears to already be documented in the wiki.

    Checks:
    1. Exact URL match (most reliable)
    2. Normalised title substring (>=4 significant words match)
    """
    url = article.get("url", "")
    title = article.get("title", "")

    # 1. URL match
    if url and url.lower() in wiki_text_lower:
        return True

    # 2. Title match — require at least 4 significant words to match
    if title:
        norm_title = _normalise(title)
        words = [w for w in norm_title.split() if len(w) > 3]
        if len(words) >= 4:
            # Check if at least 4 consecutive words appear in wiki
            for i in range(len(words) - 3):
                phrase = " ".join(words[i:i+4])
                if phrase in wiki_text_lower:
                    return True

    return False


def _build_queue_entry(article: dict, update_type: str, source_label: str) -> dict:
    """Build a wiki-update-queue.json entry for a gap article."""
    ts = article.get("published", "")
    if not ts:
        ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    else:
        # Try to normalise the timestamp to ISO format
        try:
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(ts)
            ts = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        except Exception:
            pass

    return {
        "title": article.get("title", "Unknown"),
        "url": article.get("url", ""),
        "source": article.get("url", ""),
        "source_label": source_label,
        "type": update_type,
        "content": f"Article detected by wiki-gap-detector from {source_label}. See source URL for full content.",
        "timestamp": ts,
        "wiki_update": True,
        "wiki_done": False,
        "detected_by": "wiki-gap-detector",
    }


# ---------------------------------------------------------------------------
# Queue management
# ---------------------------------------------------------------------------

def _load_queue() -> list:
    if os.path.exists(QUEUE_FILE):
        try:
            with open(QUEUE_FILE, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError):
            return []
    return []


def _save_queue(queue: list) -> None:
    tmp = QUEUE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(queue, fh, indent=2, ensure_ascii=False)
    os.replace(tmp, QUEUE_FILE)


def _queue_gaps(gaps: list, dry_run: bool) -> int:
    """
    Append gap items to wiki-update-queue.json.

    Returns number of items actually queued (skips items already in queue).
    """
    if dry_run:
        logger.info("[gap-detector] DRY-RUN — not writing to queue.")
        return 0

    queue = _load_queue()
    existing_urls = {e.get("url", "") for e in queue}
    existing_titles = {_normalise(e.get("title", "")) for e in queue}

    added = 0
    for gap in gaps:
        url = gap.get("url", "")
        norm_title = _normalise(gap.get("title", ""))

        if url and url in existing_urls:
            logger.debug("[gap-detector] Already in queue (URL): %s", url)
            continue
        if norm_title and norm_title in existing_titles:
            logger.debug(
                "[gap-detector] Already in queue (title): %s", gap.get("title")
            )
            continue

        queue.append(gap)
        existing_urls.add(url)
        existing_titles.add(norm_title)
        added += 1

    if added > 0:
        _save_queue(queue)
        logger.info("[gap-detector] Queued %d new gap item(s).", added)
    else:
        logger.info("[gap-detector] No new items to queue.")

    return added


# ---------------------------------------------------------------------------
# Gap report persistence
# ---------------------------------------------------------------------------

def _save_gap_report(report: dict) -> None:
    try:
        tmp = GAP_REPORT_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2, ensure_ascii=False)
        os.replace(tmp, GAP_REPORT_FILE)
        logger.info("[gap-detector] Gap report saved to %s", GAP_REPORT_FILE)
    except Exception as exc:
        logger.warning("[gap-detector] Could not save gap report: %s", exc)


# ---------------------------------------------------------------------------
# Main detector function
# ---------------------------------------------------------------------------

def detect_wiki_gaps(dry_run: bool = False, verbose: bool = False) -> dict:
    """
    Run the full wiki gap detection pass.

    Returns:
        {
          "sources_checked": int,
          "articles_found": int,
          "gaps_detected": int,
          "gaps_queued": int,
          "gap_details": list,
          "run_timestamp": str,
        }
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    run_ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    print("[wiki-gap-detector] Detecting wiki gaps...")

    # --- Load fandom_auth and create session ---
    fandom_auth = _load_fandom_auth()
    session = None
    wiki_text = ""

    if fandom_auth is not None:
        try:
            session = fandom_auth.create_session()
        except Exception as exc:
            logger.warning("[gap-detector] Could not create Fandom session: %s", exc)

        if session is not None:
            wiki_text = _fetch_wiki_text(fandom_auth, session)
        else:
            logger.warning(
                "[gap-detector] No Fandom session — wiki comparison will be skipped. "
                "All discovered articles will be treated as gaps."
            )
    else:
        logger.warning(
            "[gap-detector] fandom_auth.py not found — wiki comparison skipped. "
            "All discovered articles will be treated as gaps."
        )

    wiki_text_lower = _normalise(wiki_text) if wiki_text else ""

    if wiki_text:
        print(f"[wiki-gap-detector] Wiki page fetched: {len(wiki_text):,} chars")
    else:
        print("[wiki-gap-detector] Wiki page unavailable — all articles flagged as gaps")

    # --- Process each source ---
    total_articles = 0
    all_gaps: list = []
    source_reports: list = []

    for label, homepage_url, rss_url, update_type in SOURCES:
        print(f"[wiki-gap-detector] Checking source: {label}")

        articles = _fetch_articles(label, homepage_url, rss_url)
        time.sleep(CRAWL_DELAY)

        source_gaps = []
        for article in articles:
            total_articles += 1
            if not _is_in_wiki(article, wiki_text_lower):
                gap_entry = _build_queue_entry(article, update_type, label)
                source_gaps.append(gap_entry)
                logger.info(
                    "[GAP] %-30s | %s",
                    label,
                    article.get("title", "?")[:80],
                )
            else:
                logger.debug(
                    "[OK ] %-30s | %s",
                    label,
                    article.get("title", "?")[:80],
                )

        all_gaps.extend(source_gaps)
        source_reports.append({
            "source": label,
            "homepage": homepage_url,
            "articles_found": len(articles),
            "gaps": len(source_gaps),
            "gap_titles": [g["title"] for g in source_gaps],
        })

        print(
            f"[wiki-gap-detector]   -> {len(articles)} article(s) found, "
            f"{len(source_gaps)} gap(s) detected"
        )

    # --- Queue gaps ---
    queued = _queue_gaps(all_gaps, dry_run=dry_run)

    # --- Summary ---
    result = {
        "run_timestamp": run_ts,
        "dry_run": dry_run,
        "sources_checked": len(SOURCES),
        "articles_found": total_articles,
        "gaps_detected": len(all_gaps),
        "gaps_queued": queued,
        "gap_details": all_gaps,
        "source_reports": source_reports,
    }

    _save_gap_report(result)

    print(
        f"\n[wiki-gap-detector] Done: "
        f"{len(SOURCES)} sources, "
        f"{total_articles} articles found, "
        f"{len(all_gaps)} gaps detected, "
        f"{queued} queued for wiki update"
    )

    if all_gaps:
        print(f"\n[wiki-gap-detector] Top gaps:")
        for g in all_gaps[:10]:
            print(f"  * [{g['type']}] {g['title'][:70]}")
        if len(all_gaps) > 10:
            print(f"  ... and {len(all_gaps) - 10} more (see wiki-gap-report.json)")

    return result


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="GK BRAIN Wiki Gap Detector -- finds content missing from the wiki"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Detect gaps and report them without writing to wiki-update-queue.json",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable DEBUG logging for full article-by-article output",
    )
    args = parser.parse_args()

    result = detect_wiki_gaps(dry_run=args.dry_run, verbose=args.verbose)
    print(json.dumps({
        "sources_checked": result["sources_checked"],
        "articles_found": result["articles_found"],
        "gaps_detected": result["gaps_detected"],
        "gaps_queued": result["gaps_queued"],
    }, indent=2))
    sys.exit(0)
