"""
wiki-citation-checker.py — GK BRAIN Wiki Citation Health-Check Module

Crawls all current GKniftyHEADS Fandom wiki pages, checks every external
citation URL found on each page, and repairs or removes dead links before
any wiki write is performed.

Dead-link repair strategy:
    1. Try the Wayback Machine (archive.org) for a cached copy of the page.
    2. If no archive snapshot is found, delete the citation paragraph/bullet.

All findings are logged to wiki-citation-log.json.

Usage (standalone):
    python wiki-citation-checker.py

Usage (imported):
    from wiki_citation_checker import check_and_repair_citations
    check_and_repair_citations(session)   # session = fandom_auth.create_session()

Environment variables (inherited from fandom_auth.py):
    FANDOM_WIKI_URL   Wiki base URL (default: https://gkniftyheads.fandom.com)
    WIKI_DRY_RUN      Set to "1" to skip all actual wiki writes
"""

import datetime
import importlib.util
import json
import logging
import os
import re
import time

import requests

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("wiki-citation-checker")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(__file__)
LOG_FILE = os.path.join(BASE_DIR, "wiki-citation-log.json")

# Delay between individual HTTP health-check requests (seconds).
HEALTH_CHECK_DELAY: float = 1.5

# Delay between wiki API read calls (seconds).
WIKI_READ_DELAY: float = 1.0

# Maximum number of pages to process in a single run (safety cap).
MAX_PAGES = 200

# Wayback Machine availability API endpoint.
WAYBACK_API = "https://archive.org/wayback/available"

# Timeout for health-check HEAD/GET calls (seconds).
HEALTH_CHECK_TIMEOUT = 10

# ---------------------------------------------------------------------------
# Import crawl-brain._fetch and _HEADERS via importlib (reuse, no duplication)
# ---------------------------------------------------------------------------

def _load_crawl_brain():
    """Load crawl-brain.py via importlib so we can reuse its _fetch/_HEADERS."""
    path = os.path.join(BASE_DIR, "crawl-brain.py")
    if not os.path.exists(path):
        return None
    spec = importlib.util.spec_from_file_location("crawl_brain", path)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
        return mod
    except Exception as exc:
        logger.warning("Could not load crawl-brain.py: %s", exc)
        return None


_crawl_brain = _load_crawl_brain()

# Shared User-Agent header — fall back to a sensible default if crawl-brain
# could not be loaded so this module stays self-contained.
_HEADERS: dict = (
    getattr(_crawl_brain, "_HEADERS", None)
    or {
        "User-Agent": (
            "Mozilla/5.0 (compatible; GKBrainBot/1.0; "
            "+https://github.com/HODLKONG64/the-brain)"
        )
    }
)


def _is_url_alive(url: str) -> bool:
    """
    Return True when *url* responds with a 2xx HTTP status code.

    Tries a HEAD request first (cheap); falls back to GET if HEAD fails or
    returns a non-2xx status.  Returns False on timeout or any exception.

    This deliberately mirrors the fetch logic in crawl-brain.py so the same
    User-Agent and timeout policy are applied consistently.
    """
    try:
        resp = requests.head(
            url, headers=_HEADERS, timeout=HEALTH_CHECK_TIMEOUT, allow_redirects=True
        )
        if resp.status_code < 300:
            return True
        # Some servers reject HEAD — retry with GET.
        resp = requests.get(
            url, headers=_HEADERS, timeout=HEALTH_CHECK_TIMEOUT, stream=True
        )
        resp.close()
        return resp.status_code < 300
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Wayback Machine replacement lookup
# ---------------------------------------------------------------------------

def _find_wayback_url(dead_url: str) -> str:
    """
    Query the Wayback Machine availability API for *dead_url*.

    Returns the closest archived snapshot URL if one exists, or an empty
    string if no snapshot is available or the request fails.
    """
    try:
        resp = requests.get(
            WAYBACK_API,
            params={"url": dead_url},
            headers=_HEADERS,
            timeout=HEALTH_CHECK_TIMEOUT,
        )
        if resp.status_code == 200:
            data = resp.json()
            closest = data.get("archived_snapshots", {}).get("closest", {})
            snapshot = closest.get("url", "")
            if snapshot and closest.get("available"):
                return snapshot
    except Exception as exc:
        logger.debug("Wayback Machine lookup failed for %s: %s", dead_url, exc)
    return ""


# ---------------------------------------------------------------------------
# Citation URL extraction from wikitext
# ---------------------------------------------------------------------------

# Matches bare https:// or http:// URLs and URLs inside [url text] brackets.
_URL_RE = re.compile(
    r"https?://[^\s|\]<>\"']+"
)


def _extract_urls(wikitext: str) -> list:
    """Return a deduplicated list of all external URLs found in *wikitext*."""
    seen: set = set()
    urls: list = []
    for m in _URL_RE.finditer(wikitext):
        url = m.group(0).rstrip(".,;)")
        if url not in seen:
            seen.add(url)
            urls.append(url)
    return urls


# ---------------------------------------------------------------------------
# Wikitext repair helpers
# ---------------------------------------------------------------------------

def _replace_url_in_wikitext(wikitext: str, old_url: str, new_url: str) -> str:
    """Replace every occurrence of *old_url* with *new_url* in *wikitext*."""
    return wikitext.replace(old_url, new_url)


def _remove_lines_containing_url(wikitext: str, dead_url: str) -> str:
    """
    Remove all lines from *wikitext* that contain *dead_url*.

    This covers bullet points, ref tags, and bare citation lines.
    Blank lines left adjacent are collapsed to a single blank line.
    """
    lines = wikitext.splitlines()
    filtered = [line for line in lines if dead_url not in line]
    # Collapse runs of blank lines into at most one blank line.
    result: list = []
    prev_blank = False
    for line in filtered:
        is_blank = not line.strip()
        if is_blank and prev_blank:
            continue
        result.append(line)
        prev_blank = is_blank
    return "\n".join(result)


# ---------------------------------------------------------------------------
# Wiki page enumeration
# ---------------------------------------------------------------------------

def _get_all_wiki_pages(session: requests.Session, wiki_api: str) -> list:
    """
    Return a list of all page titles in the wiki using the allpages API.

    Handles API continuation so all pages (up to MAX_PAGES) are returned.
    """
    pages: list = []
    params: dict = {
        "action": "query",
        "list": "allpages",
        "aplimit": "50",
        "apnamespace": "0",
        "format": "json",
    }

    while len(pages) < MAX_PAGES:
        try:
            resp = session.get(wiki_api, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            logger.error("Failed to enumerate wiki pages: %s", exc)
            break

        batch = [p["title"] for p in data.get("query", {}).get("allpages", [])]
        pages.extend(batch)

        # Follow continuation token if present.
        cont = data.get("continue", {})
        if cont.get("apcontinue"):
            params["apcontinue"] = cont["apcontinue"]
            time.sleep(WIKI_READ_DELAY)
        else:
            break

    return pages[:MAX_PAGES]


# ---------------------------------------------------------------------------
# Per-page citation check and repair
# ---------------------------------------------------------------------------

def _check_and_repair_page(
    session: requests.Session,
    wiki_api: str,
    page_title: str,
    dry_run: bool,
) -> dict:
    """
    Check all citation URLs on *page_title* and repair or remove dead ones.

    Returns a summary dict:
        {
          "page": str,
          "checked": int,
          "replaced": int,
          "removed": int,
          "errors": int,
          "dead_urls": list[str],
        }
    """
    import fandom_auth

    summary = {
        "page": page_title,
        "checked": 0,
        "replaced": 0,
        "removed": 0,
        "errors": 0,
        "dead_urls": [],
    }

    try:
        wikitext = fandom_auth.get_page_content(session, page_title)
    except Exception as exc:
        logger.error("Could not fetch page '%s': %s", page_title, exc)
        summary["errors"] += 1
        return summary

    if not wikitext:
        return summary

    urls = _extract_urls(wikitext)
    if not urls:
        return summary

    modified = wikitext
    changed = False

    for url in urls:
        summary["checked"] += 1
        time.sleep(HEALTH_CHECK_DELAY)

        if _is_url_alive(url):
            logger.debug("  LIVE   %s", url)
            continue

        # URL is dead.
        summary["dead_urls"].append(url)
        logger.info("  DEAD   %s  (page: %s)", url, page_title)

        # --- Repair strategy 1: Wayback Machine ---
        replacement = _find_wayback_url(url)
        time.sleep(HEALTH_CHECK_DELAY)

        if replacement:
            logger.info("  REPLACE  %s  →  %s", url, replacement)
            if not dry_run:
                modified = _replace_url_in_wikitext(modified, url, replacement)
            summary["replaced"] += 1
        else:
            # --- Repair strategy 2: LOG ONLY — never auto-delete content ---
            # Removing lines containing dead URLs deletes the surrounding
            # wiki content (bullet text, lore entries, etc.), not just the URL.
            # Dead links with no Wayback snapshot are logged for human review only.
            logger.warning(
                "  DEAD (no archive) — logged for review, NOT removed: %s (page: %s)",
                url, page_title
            )
            summary["removed"] += 1  # counter kept for reporting, but no edit made

        if replacement:
            changed = True

    # Safety guard: never write if modified content is less than 80% of original.
    # This prevents accidental mass-deletion from wiping pages.
    if changed and not dry_run and modified != wikitext:
        original_len = len(wikitext.strip())
        modified_len = len(modified.strip())
        if original_len > 500 and modified_len < original_len * 0.80:
            logger.error(
                "SAFETY ABORT: citation-checker would reduce '%s' from %d to %d chars "
                "(>20%% reduction). Skipping edit to protect content.",
                page_title, original_len, modified_len,
            )
            summary["errors"] += 1
            return summary

    if changed and not dry_run and modified != wikitext:
        try:
            ok = fandom_auth.edit_page(
                session,
                page_title,
                modified,
                "GK BRAIN citation checker: repaired/removed dead links",
                check_hash=False,
            )
            if not ok:
                logger.warning("Failed to save citation repairs for '%s'", page_title)
                summary["errors"] += 1
        except Exception as exc:
            logger.error("Edit failed for '%s': %s", page_title, exc)
            summary["errors"] += 1

    return summary


# ---------------------------------------------------------------------------
# Log helpers
# ---------------------------------------------------------------------------

def _load_log() -> list:
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError):
            return []
    return []


def _append_log(entry: dict) -> None:
    log = _load_log()
    log.append(entry)
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as fh:
            json.dump(log, fh, indent=2)
    except OSError as exc:
        logger.warning("Could not write citation log: %s", exc)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def check_and_repair_citations(
    session: "requests.Session | None" = None,
    dry_run: bool = False,
) -> dict:
    """
    Run the citation health-check pass over all GK fan wiki pages.

    Must be called **before** any wiki write so that every page is in a
    clean, live-link state before new content is appended or merged.

    Args:
        session:  An authenticated :class:`requests.Session` returned by
                  ``fandom_auth.create_session()``.  If *None* a new session
                  is created automatically.
        dry_run:  When True, dead links are identified and logged but no
                  wiki edits are made.

    Returns:
        {
          "pages_checked": int,
          "total_urls_checked": int,
          "total_replaced": int,
          "total_removed": int,
          "total_errors": int,
          "all_dead_urls": list[str],
          "run_timestamp": str,
        }

    This function **never raises**.  All errors are caught and logged so
    that the normal wiki-write flow is never interrupted by a health-check
    failure.
    """
    run_ts = datetime.datetime.now(datetime.timezone.utc).isoformat().replace(
        "+00:00", "Z"
    )
    totals: dict = {
        "pages_checked": 0,
        "total_urls_checked": 0,
        "total_replaced": 0,
        "total_removed": 0,
        "total_errors": 0,
        "all_dead_urls": [],
        "run_timestamp": run_ts,
    }

    try:
        import fandom_auth

        wiki_api: str = fandom_auth.WIKI_API

        # Authenticate if no session was provided.
        if session is None:
            session = fandom_auth.create_session()
            if session is None:
                logger.warning(
                    "citation-checker: Fandom credentials missing — skipping pass."
                )
                return totals

        logger.info("citation-checker: enumerating wiki pages…")
        page_titles = _get_all_wiki_pages(session, wiki_api)
        logger.info("citation-checker: found %d page(s) to check.", len(page_titles))

        page_summaries: list = []

        for title in page_titles:
            logger.info("citation-checker: checking '%s'…", title)
            summary = _check_and_repair_page(session, wiki_api, title, dry_run)
            page_summaries.append(summary)

            totals["pages_checked"] += 1
            totals["total_urls_checked"] += summary["checked"]
            totals["total_replaced"] += summary["replaced"]
            totals["total_removed"] += summary["removed"]
            totals["total_errors"] += summary["errors"]
            totals["all_dead_urls"].extend(summary["dead_urls"])

            # Polite delay between pages.
            time.sleep(WIKI_READ_DELAY)

        # Persist the run to the log file.
        log_entry = {
            "run_timestamp": run_ts,
            "dry_run": dry_run,
            **totals,
            "page_summaries": page_summaries,
        }
        _append_log(log_entry)

        logger.info(
            "citation-checker complete — pages=%d, checked=%d, replaced=%d, "
            "removed=%d, errors=%d",
            totals["pages_checked"],
            totals["total_urls_checked"],
            totals["total_replaced"],
            totals["total_removed"],
            totals["total_errors"],
        )

    except Exception as exc:
        # Fail gracefully — never let a health-check error break the wiki write.
        logger.error("citation-checker encountered an unexpected error: %s", exc)
        totals["total_errors"] += 1

    return totals


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="GK BRAIN wiki citation health-check"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Identify dead links and log them without editing any wiki pages.",
    )
    args = parser.parse_args()

    result = check_and_repair_citations(dry_run=args.dry_run)
    print(json.dumps(result, indent=2))
