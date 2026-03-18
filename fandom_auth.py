"""
fandom_auth.py — Shared Fandom/MediaWiki Authentication & API Helper

Centralises all Fandom API session management so that wiki-updater.py,
wiki-smart-merger.py, and gk-wiki-updater-v2.py all share the same
robust implementation.

Environment variables (all required unless noted):
    FANDOM_BOT_USER       Fandom bot username (preferred over FANDOM_USERNAME)
    FANDOM_USERNAME       Fandom username (fallback)
    FANDOM_BOT_PASSWORD   Fandom bot password (preferred over FANDOM_PASSWORD)
    FANDOM_PASSWORD       Fandom password (fallback)
    FANDOM_WIKI_URL       Base URL of the wiki, e.g. https://gkniftyheads.fandom.com
                          (no trailing slash; defaults to https://gkniftyheads.fandom.com)
    WIKI_DRY_RUN          Set to "1" to log what would be written without actually
                          writing (default: unset / disabled)
    WIKI_API_DELAY        Minimum seconds to sleep between consecutive API write
                          calls (default: 1.0)
"""

import hashlib
import logging
import os
import time
from typing import Optional

import requests

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

WIKI_BASE: str = os.environ.get(
    "FANDOM_WIKI_URL", "https://gkniftyheads.fandom.com"
).rstrip("/")
WIKI_API: str = WIKI_BASE + "/api.php"

FANDOM_USERNAME: str = os.environ.get(
    "FANDOM_BOT_USER", os.environ.get("FANDOM_USERNAME", "")
)
FANDOM_PASSWORD: str = os.environ.get(
    "FANDOM_BOT_PASSWORD", os.environ.get("FANDOM_PASSWORD", "")
)

# Dry-run flag: set WIKI_DRY_RUN=1 to skip all write operations.
DRY_RUN: bool = os.environ.get("WIKI_DRY_RUN", "0").strip() == "1"

# Minimum delay between consecutive API write calls (seconds).
API_DELAY: float = float(os.environ.get("WIKI_API_DELAY", "1.0"))

# Retry configuration for transient failures.
_RETRY_ATTEMPTS: int = 3
_RETRY_BACKOFF: tuple[float, ...] = (2.0, 4.0, 8.0)

# ---------------------------------------------------------------------------
# Retry helper
# ---------------------------------------------------------------------------


def _api_call_with_retry(fn, *args, **kwargs):
    """
    Call *fn* with *args*/*kwargs*, retrying up to _RETRY_ATTEMPTS times on
    HTTP 429 / 5xx responses or transient ``requests`` exceptions.

    Raises the last exception (or a RuntimeError with the last bad response)
    if all attempts fail.
    """
    last_exc: Optional[Exception] = None
    last_bad_response: Optional[requests.Response] = None

    for attempt in range(1, _RETRY_ATTEMPTS + 1):
        backoff = _RETRY_BACKOFF[attempt - 1]
        try:
            response = fn(*args, **kwargs)
            # Re-raise on server/rate-limit errors so the retry logic fires.
            if isinstance(response, requests.Response):
                if response.status_code == 429 or response.status_code >= 500:
                    last_bad_response = response
                    if attempt < _RETRY_ATTEMPTS:
                        logger.warning(
                            "HTTP %s on attempt %d/%d — retrying in %.0fs",
                            response.status_code,
                            attempt,
                            _RETRY_ATTEMPTS,
                            backoff,
                        )
                        time.sleep(backoff)
                        continue
                    # Final attempt exhausted.
                    break
            return response
        except requests.RequestException as exc:
            last_exc = exc
            if attempt < _RETRY_ATTEMPTS:
                logger.warning(
                    "Request error on attempt %d/%d: %s — retrying in %.0fs",
                    attempt,
                    _RETRY_ATTEMPTS,
                    exc,
                    backoff,
                )
                time.sleep(backoff)

    if last_exc:
        raise last_exc
    if last_bad_response is not None:
        raise requests.HTTPError(
            f"HTTP {last_bad_response.status_code} after {_RETRY_ATTEMPTS} attempts",
            response=last_bad_response,
        )
    raise RuntimeError("All retry attempts exhausted")


# ---------------------------------------------------------------------------
# Content hash helper
# ---------------------------------------------------------------------------


def content_hash(text: str) -> str:
    """Return a SHA-256 hex digest of *text* (normalised whitespace)."""
    normalised = " ".join(text.split())
    return hashlib.sha256(normalised.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# MediaWiki API helpers
# ---------------------------------------------------------------------------


def get_login_token(session: requests.Session) -> str:
    """Fetch the ``logintoken`` needed for the ``action=login`` flow."""
    resp = _api_call_with_retry(
        session.get,
        WIKI_API,
        params={
            "action": "query",
            "meta": "tokens",
            "type": "login",
            "format": "json",
        },
    )
    resp.raise_for_status()
    return resp.json()["query"]["tokens"]["logintoken"]


def login(session: requests.Session) -> bool:
    """
    Perform a two-step Fandom/MediaWiki login using the supported ``action=login`` flow.

    Step 1: GET ``action=query&meta=tokens&type=login`` → ``logintoken``
    Step 2: POST ``action=login`` with lgname, lgpassword, and lgtoken.

    Returns True on success, False otherwise.
    """
    if not FANDOM_USERNAME or not FANDOM_PASSWORD:
        logger.warning("FANDOM credentials not set — skipping wiki operations.")
        return False

    try:
        lgtoken = get_login_token(session)
    except Exception as exc:
        logger.error("Failed to fetch login token: %s", exc)
        return False

    try:
        resp = _api_call_with_retry(
            session.post,
            WIKI_API,
            data={
                "action": "login",
                "lgname": FANDOM_USERNAME,
                "lgpassword": FANDOM_PASSWORD,
                "lgtoken": lgtoken,
                "format": "json",
            },
        )
        resp.raise_for_status()
        result = resp.json()
    except Exception as exc:
        logger.error("Login POST failed: %s", exc)
        return False

    status = result.get("login", {}).get("result", "")
    if status == "Success":
        logger.info("Logged in to Fandom as %s", FANDOM_USERNAME)
        return True

    logger.error("Fandom login failed (result=%s): %s", status, result)
    return False


def get_csrf_token(session: requests.Session) -> str:
    """
    Fetch a fresh CSRF/edit token.

    This must be called immediately before every edit to avoid using a
    stale/expired token.
    """
    resp = _api_call_with_retry(
        session.get,
        WIKI_API,
        params={"action": "query", "meta": "tokens", "format": "json"},
    )
    resp.raise_for_status()
    return resp.json()["query"]["tokens"]["csrftoken"]


def get_page_content(session: requests.Session, title: str) -> str:
    """
    Fetch the current wikitext content of *title*.

    Returns an empty string if the page does not exist.
    """
    resp = _api_call_with_retry(
        session.get,
        WIKI_API,
        params={
            "action": "query",
            "prop": "revisions",
            "rvprop": "content",
            "titles": title,
            "format": "json",
        },
    )
    resp.raise_for_status()
    pages = resp.json()["query"]["pages"]
    for page in pages.values():
        revisions = page.get("revisions", [])
        if revisions:
            return revisions[0].get("*", "")
    return ""


def edit_page(
    session: requests.Session,
    title: str,
    content: str,
    summary: str,
    *,
    check_hash: bool = True,
) -> bool:
    """
    Replace the full content of *title* with *content*.

    When *check_hash* is True (default), the current page content is fetched
    first; if it is identical to *content* (ignoring whitespace normalisation)
    the edit is skipped and True is returned (no-op success).

    In dry-run mode (``WIKI_DRY_RUN=1``) the function logs what it would do
    and returns True without making any API write call.

    Returns True on success (or no-op), False on failure.
    """
    if check_hash:
        try:
            existing = get_page_content(session, title)
            if content_hash(existing) == content_hash(content):
                logger.info("Page '%s' unchanged — skipping edit.", title)
                return True
        except Exception as exc:
            logger.warning("Could not fetch page for hash check ('%s'): %s", title, exc)

    if DRY_RUN:
        logger.info(
            "[DRY RUN] Would edit page '%s' (summary: %s)", title, summary
        )
        return True

    # Fresh CSRF token for each edit attempt to avoid expiry issues.
    try:
        csrf_token = get_csrf_token(session)
    except Exception as exc:
        logger.error("Could not fetch CSRF token before editing '%s': %s", title, exc)
        return False

    try:
        resp = _api_call_with_retry(
            session.post,
            WIKI_API,
            data={
                "action": "edit",
                "title": title,
                "text": content,
                "summary": summary,
                "bot": "true",
                "token": csrf_token,
                "format": "json",
            },
        )
        resp.raise_for_status()
    except Exception as exc:
        logger.error("Edit request failed for '%s': %s", title, exc)
        return False

    result = resp.json()
    if result.get("edit", {}).get("result") == "Success":
        logger.info("Edited page '%s' — %s", title, summary)
        time.sleep(API_DELAY)
        return True

    logger.error("Edit API error for '%s': %s", title, result)
    return False


def append_to_page(
    session: requests.Session,
    title: str,
    section_wikitext: str,
    summary: str,
) -> bool:
    """
    Append *section_wikitext* to the bottom of *title*.

    Fetches the current content, appends, then calls :func:`edit_page`.
    Returns True on success.
    """
    try:
        existing = get_page_content(session, title)
    except Exception as exc:
        logger.error("Could not fetch '%s' for append: %s", title, exc)
        return False

    new_content = existing.strip() + "\n\n" + section_wikitext.strip() + "\n"
    return edit_page(session, title, new_content, summary, check_hash=False)


def create_session() -> Optional[requests.Session]:
    """
    Create a :class:`requests.Session`, log in, and return it.

    Returns None if login fails so callers can bail early.
    """
    session = requests.Session()
    if login(session):
        return session
    return None
