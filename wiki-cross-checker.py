"""
wiki-cross-checker.py — Cross-Check Saved Data Against Fandom Wiki

After the agent detects updates and uses them for lore/images, this module
compares what the agent found (wiki-update-queue.json) vs what is currently
on the Fandom wiki and flags missing or changed data for wiki updates.

Usage (from gk-brain.py or standalone):
    from wiki_cross_checker import cross_check_and_flag_missing
    missing = cross_check_and_flag_missing()
"""

import hashlib
import json
import os
import re

import requests

# ---------------------------------------------------------------------------
# Configuration (shared with wiki-smart-merger.py)
# ---------------------------------------------------------------------------

QUEUE_FILE = os.path.join(os.path.dirname(__file__), "wiki-update-queue.json")

WIKI_BASE = os.environ.get("FANDOM_WIKI_URL", "https://gkniftyheads.fandom.com").rstrip("/")
WIKI_API = WIKI_BASE + "/api.php"
FANDOM_USERNAME = os.environ.get("FANDOM_BOT_USER", os.environ.get("FANDOM_USERNAME", ""))
FANDOM_PASSWORD = os.environ.get("FANDOM_BOT_PASSWORD", os.environ.get("FANDOM_PASSWORD", ""))

MAIN_WIKI_PAGE = "GKniftyHEADS_Wiki"

# Fingerprinting constants — must match wiki-smart-merger.py
FINGERPRINT_CONTENT_LENGTH = 500   # chars of normalised content used for MD5
FINGERPRINT_PREFIX_LENGTH = 16     # hex chars of MD5 hash stored in wiki comments


# ---------------------------------------------------------------------------
# Fingerprinting helpers
# ---------------------------------------------------------------------------

def _get_content_fingerprint(text: str) -> str:
    """Create an MD5 hash fingerprint of content for deduplication."""
    clean = " ".join(text.lower().split())[:FINGERPRINT_CONTENT_LENGTH]
    return hashlib.md5(clean.encode()).hexdigest()


# ---------------------------------------------------------------------------
# MediaWiki API helpers
# ---------------------------------------------------------------------------

def _get_login_token(session: requests.Session) -> str:
    resp = session.get(WIKI_API, params={
        "action": "query",
        "meta": "tokens",
        "type": "login",
        "format": "json",
    })
    resp.raise_for_status()
    return resp.json()["query"]["tokens"]["logintoken"]


def _login(session: requests.Session) -> bool:
    """Log in to Fandom with bot credentials. Returns True on success."""
    if not FANDOM_USERNAME or not FANDOM_PASSWORD:
        print("[wiki-cross-checker] FANDOM credentials not set — skipping.")
        return False

    token = _get_login_token(session)
    resp = session.post(WIKI_API, data={
        "action": "clientlogin",
        "loginmessageformat": "none",
        "username": FANDOM_USERNAME,
        "password": FANDOM_PASSWORD,
        "logintoken": token,
        "loginreturnurl": WIKI_BASE,
        "rememberMe": 1,
        "format": "json",
    })
    resp.raise_for_status()
    result = resp.json()
    if result.get("clientlogin", {}).get("status") == "PASS":
        print(f"[wiki-cross-checker] Logged in as {FANDOM_USERNAME}")
        return True
    print(f"[wiki-cross-checker] Login failed: {result}")
    return False


def _get_page_content(session: requests.Session, title: str) -> str:
    """Return current wikitext of a page, or empty string if the page is new."""
    resp = session.get(WIKI_API, params={
        "action": "query",
        "prop": "revisions",
        "rvprop": "content",
        "titles": title,
        "format": "json",
    })
    resp.raise_for_status()
    pages = resp.json()["query"]["pages"]
    for page in pages.values():
        revisions = page.get("revisions", [])
        if revisions:
            return revisions[0].get("*", "")
    return ""


# ---------------------------------------------------------------------------
# Queue helpers
# ---------------------------------------------------------------------------

def _load_queue() -> list:
    if os.path.exists(QUEUE_FILE):
        try:
            with open(QUEUE_FILE, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError):
            return []
    return []


# ---------------------------------------------------------------------------
# Cross-check logic
# ---------------------------------------------------------------------------

def get_saved_data_fingerprints() -> dict[str, dict]:
    """
    Read all saved updates from wiki-update-queue.json and return a mapping of
    {fingerprint: update_dict} for every entry that has not yet been marked
    wiki_done.
    """
    queue = _load_queue()
    result: dict[str, dict] = {}
    for entry in queue:
        if entry.get("wiki_done"):
            continue
        content = entry.get("content") or ""
        title = entry.get("title") or ""
        text = content if content else title
        if not text:
            continue
        fp = _get_content_fingerprint(text)
        result[fp] = entry
    return result


def get_wiki_page_fingerprints(page_body: str) -> set[str]:
    """
    Extract all embedded fingerprint comments from a wiki page body and return
    the set of fingerprint prefixes found.

    Fingerprints are embedded by wiki-smart-merger.py as HTML comments of the
    form <!-- fp:XXXXXXXXXXXXXXXX -->.
    """
    pattern = r"<!-- fp:([0-9a-f]{" + str(FINGERPRINT_PREFIX_LENGTH) + r"}) -->"
    return set(re.findall(pattern, page_body))


def cross_check_and_flag_missing(session: requests.Session | None = None) -> list[dict]:
    """
    Compare the agent's saved data (wiki-update-queue.json) against the current
    wiki page content.

    Returns a list of update dicts that are:
    - Completely missing from the wiki (needs adding), or
    - Stored in the queue but not yet wiki_done.

    Side-effect: prints a summary of findings to stdout.
    """
    # Load saved updates
    saved_fingerprints = get_saved_data_fingerprints()
    if not saved_fingerprints:
        print("[wiki-cross-checker] No pending updates in queue to cross-check.")
        return []

    # Optionally fetch the wiki page to compare fingerprints
    wiki_fingerprints: set[str] = set()
    if session is None and FANDOM_USERNAME and FANDOM_PASSWORD:
        session = requests.Session()
        if not _login(session):
            session = None

    if session is not None:
        try:
            page_body = _get_page_content(session, MAIN_WIKI_PAGE)
            wiki_fingerprints = get_wiki_page_fingerprints(page_body)
        except Exception as exc:
            print(f"[wiki-cross-checker] Could not fetch wiki page: {exc}")

    missing: list[dict] = []
    for fp, update in saved_fingerprints.items():
        if fp[:FINGERPRINT_PREFIX_LENGTH] not in wiki_fingerprints:
            missing.append(update)

    print(
        f"[wiki-cross-checker] {len(missing)}/{len(saved_fingerprints)} "
        f"saved updates are missing from wiki."
    )
    return missing


# ---------------------------------------------------------------------------
# CLI self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Running wiki cross-checker…")
    missing_updates = cross_check_and_flag_missing()
    print(f"Missing updates: {len(missing_updates)}")
    for u in missing_updates:
        print(f"  - [{u.get('type', 'unknown')}] {u.get('title', '?')}")
