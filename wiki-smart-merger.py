"""
wiki-smart-merger.py — Smart Wiki Merge System for GK BRAIN

Combines simple append logging (always reliable) with smart section merging
(intelligent data detection and page updates).

Layer 1 — Simple (Always Works):
    - Appends every agent run as a timestamped log entry.
    - Never alters existing wiki structure.
    - Used as fallback if smart merge fails.

Layer 2 — Smart (Enhanced):
    - Reads current wiki page content.
    - Detects existing sections via heading patterns.
    - Compares new detected data against existing content.
    - Identifies "missing" data by category (characters, locations, fishing
      catches, NFT drops, art movements, raid/dream events).
    - Inserts new items into the matching section; appends a new section when
      none exists.

Hybrid approach:
    - Primary : attempt smart merge for each detected update.
    - Fallback : always append an agent-run log entry.
    - Result  : wiki grows intelligently while staying safe.

Usage (from gk-brain.py or standalone):
    from wiki_smart_merger import run_smart_wiki_updates
    run_smart_wiki_updates()
"""

import datetime
import hashlib
import json
import os
import re
import time
from urllib.parse import urlparse

import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

QUEUE_FILE = os.path.join(os.path.dirname(__file__), "wiki-update-queue.json")

WIKI_BASE = os.environ.get("FANDOM_WIKI_URL", "https://gkniftyheads.fandom.com").rstrip("/")
WIKI_API = WIKI_BASE + "/api.php"
FANDOM_USERNAME = os.environ.get("FANDOM_BOT_USER", os.environ.get("FANDOM_USERNAME", ""))
FANDOM_PASSWORD = os.environ.get("FANDOM_BOT_PASSWORD", os.environ.get("FANDOM_PASSWORD", ""))

MAIN_WIKI_PAGE = "GKniftyHEADS_Wiki"
AGENT_LOG_PAGE = "GK_BRAIN_Agent_Log"

# Mapping: update type → wiki section heading (title-case, no '==' markers)
SECTION_MAP: dict[str, str] = {
    # Lore Posts
    "lore-post": "Latest Lore Posts",
    # Fishing
    "fishing-real": "Fishing Records",
    "fishing": "Fishing Records",
    # Graffiti & Street Art
    "graffiti-news-real": "Graffiti & Street Art",
    "graffiti": "Graffiti & Street Art",
    # NFT & Crypto
    "gkdata-real": "NFT Drops & Collections",
    "nft": "NFT Drops & Collections",
    "crypto": "Crypto & Market News",
    # Music & Events
    "rave-real": "Rave & Music Events",
    "rave": "Rave & Music Events",
    "event": "Events & Meetups",
    # News & Updates
    "news-real": "Latest News",
    "news": "Latest News",
    # Characters & Lore
    "character": "Characters",
    "character-profile": "Characters",
    "lady-ink-hint": "Characters",
    # Locations
    "location": "Locations & Landmarks",
    "place": "Locations & Landmarks",
    # Art & Culture
    "art-movement": "Art Movements & Styles",
    "art": "Art Movements & Styles",
    # Dreams & Special Events
    "dream": "Dream & Raid Events",
    "raid": "Dream & Raid Events",
    "special-event": "Special Events",
}

# Default section for update types not present in SECTION_MAP
DEFAULT_SECTION = "Uncategorized Updates"

# Fingerprinting constants
FINGERPRINT_CONTENT_LENGTH = 500   # chars of normalised content used for MD5
FINGERPRINT_PREFIX_LENGTH = 16     # hex chars of MD5 hash stored in wiki comments
CONTENT_SNIPPET_LENGTH = 200       # max chars of content shown in a wiki bullet


# ---------------------------------------------------------------------------
# MediaWiki API helpers (mirrors wiki-updater.py; kept self-contained)
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
        print("[wiki-smart-merger] FANDOM credentials not set — skipping.")
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
        print(f"[wiki-smart-merger] Logged in as {FANDOM_USERNAME}")
        return True
    print(f"[wiki-smart-merger] Login failed: {result}")
    return False


def _get_csrf_token(session: requests.Session) -> str:
    resp = session.get(WIKI_API, params={
        "action": "query",
        "meta": "tokens",
        "format": "json",
    })
    resp.raise_for_status()
    return resp.json()["query"]["tokens"]["csrftoken"]


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


def _edit_page(
    session: requests.Session,
    title: str,
    content: str,
    summary: str,
    csrf_token: str,
) -> bool:
    """Replace the full content of a wiki page. Returns True on success."""
    resp = session.post(WIKI_API, data={
        "action": "edit",
        "title": title,
        "text": content,
        "summary": summary,
        "bot": "true",
        "token": csrf_token,
        "format": "json",
    })
    resp.raise_for_status()
    result = resp.json()
    if result.get("edit", {}).get("result") == "Success":
        return True
    print(f"[wiki-smart-merger] Edit failed for '{title}': {result}")
    return False


def _append_to_page(
    session: requests.Session,
    title: str,
    section_wikitext: str,
    summary: str,
    csrf_token: str,
) -> bool:
    """Append wikitext to the bottom of a page (simple layer). Returns True on success."""
    existing = _get_page_content(session, title)
    new_content = existing.strip() + "\n\n" + section_wikitext.strip() + "\n"
    return _edit_page(session, title, new_content, summary, csrf_token)


# ---------------------------------------------------------------------------
# Section analysis helpers
# ---------------------------------------------------------------------------

def _parse_sections(wikitext: str) -> dict[str, str]:
    """
    Parse wikitext into a dict of {section_heading: section_body}.

    Handles == Level 2 == headings only (top-level wiki sections).
    Returns an ordered dict where key '' holds any pre-heading preamble.
    """
    sections: dict[str, str] = {}
    current_heading = ""
    buffer: list[str] = []

    for line in wikitext.splitlines():
        match = re.match(r"^==\s*(.+?)\s*==\s*$", line)
        if match:
            sections[current_heading] = "\n".join(buffer)
            current_heading = match.group(1)
            buffer = []
        else:
            buffer.append(line)

    sections[current_heading] = "\n".join(buffer)
    return sections


def _rebuild_page(sections: dict[str, str]) -> str:
    """Re-serialise a sections dict back to wikitext."""
    parts: list[str] = []
    for heading, body in sections.items():
        if heading == "":
            parts.append(body)
        else:
            parts.append(f"== {heading} ==")
            parts.append(body)
    return "\n".join(parts).strip() + "\n"


def _section_contains(body: str, keywords: list[str]) -> bool:
    """Return True if any keyword appears in body (case-insensitive)."""
    lower = body.lower()
    return any(kw.lower() in lower for kw in keywords)


def _get_content_fingerprint(text: str) -> str:
    """Create an MD5 hash fingerprint of content for deduplication."""
    clean = " ".join(text.lower().split())[:FINGERPRINT_CONTENT_LENGTH]
    return hashlib.md5(clean.encode()).hexdigest()


def _extract_domain(url: str) -> str:
    """Extract the bare domain name from a URL."""
    try:
        return urlparse(url).netloc.lower().replace("www.", "")
    except Exception:
        return url


def _entry_already_present(body: str, update: dict) -> bool:
    """
    Smart duplicate detection using source URL, title+timestamp, and content
    hash fingerprinting.

    Returns True if this exact data is already on the wiki page.
    """
    # 1. Check by source URL (most reliable)
    source_url = update.get("url") or update.get("source", "")
    if source_url and source_url in body:
        return True

    # 2. Check by title + date (exact match)
    title = update.get("title", "")
    timestamp = update.get("timestamp", "")
    if title and timestamp:
        date_part = timestamp[:10]  # YYYY-MM-DD
        if re.search(re.escape(title) + r".*" + re.escape(date_part), body, re.IGNORECASE):
            return True

    # 3. Check by content fingerprint (first FINGERPRINT_PREFIX_LENGTH chars of MD5 hash)
    content = update.get("content", "")
    if content and len(content) > 50:
        fingerprint = _get_content_fingerprint(content)
        if fingerprint[:FINGERPRINT_PREFIX_LENGTH] in body:
            return True

    return False


# ---------------------------------------------------------------------------
# Smart merge logic
# ---------------------------------------------------------------------------

def _format_update_bullet(update: dict, display_time: str) -> str:
    """Format a single update as a wiki bullet point with source attribution."""
    title = update.get("title", "Update")
    source_url = update.get("url") or update.get("source", "")
    source_domain = _extract_domain(source_url) if source_url else ""
    content = update.get("content", "").strip()

    # Embed content fingerprint as a hidden comment for future duplicate detection
    fingerprint_comment = ""
    if content and len(content) > 50:
        fp = _get_content_fingerprint(content)
        fingerprint_comment = f"<!-- fp:{fp[:FINGERPRINT_PREFIX_LENGTH]} -->"

    if source_url:
        lines = [
            f"* '''[[{title}]]''' — {source_domain} — {display_time} {fingerprint_comment}",
        ]
        if content:
            snippet = content[:CONTENT_SNIPPET_LENGTH]
            suffix = "..." if len(content) > CONTENT_SNIPPET_LENGTH else ""
            lines.append(f"  {snippet}{suffix}")
    else:
        lines = [
            f"* '''{title}''' — {display_time} {fingerprint_comment}",
        ]
        if content:
            snippet = content[:CONTENT_SNIPPET_LENGTH]
            suffix = "..." if len(content) > CONTENT_SNIPPET_LENGTH else ""
            lines.append(f"  {snippet}{suffix}")

    return "\n".join(lines)


def _smart_merge_update(
    page_content: str,
    update: dict,
    display_time: str,
) -> tuple[str, bool]:
    """
    Attempt to smart-merge one update into page_content.

    Returns (new_page_content, merged_ok).
    merged_ok is False only when the update was already present.
    Unknown update types are placed in DEFAULT_SECTION instead of being dropped.
    """
    update_type = update.get("type", "")
    target_section = SECTION_MAP.get(update_type, DEFAULT_SECTION)

    sections = _parse_sections(page_content)

    # Check whether update already exists anywhere on the page
    if _entry_already_present(page_content, update):
        print(
            f"[wiki-smart-merger] '{update.get('title')}' already present — skipping smart merge."
        )
        return page_content, False

    bullet = _format_update_bullet(update, display_time)

    if target_section in sections:
        # Insert bullet at the top of the existing section body
        existing_body = sections[target_section]
        sections[target_section] = bullet + "\n" + existing_body
    else:
        # Create new section at the end of the page
        sections[target_section] = bullet + "\n"

    return _rebuild_page(sections), True


def _build_agent_log_entry(update: dict, display_time: str, merged: bool) -> str:
    """Build the simple append log entry for the agent log page."""
    sub_page = _sub_page_title(update)
    merge_note = " ✅ smart-merged" if merged else " 📋 appended"
    return (
        f"* '''[[{sub_page}|{update.get('title', 'Update')}]]''' "
        f"— {update.get('type', 'update')} — {display_time}{merge_note}"
    )


def _sub_page_title(update: dict) -> str:
    """Generate a wiki sub-page title for a single update."""
    ts = update.get("timestamp", "")
    try:
        dt = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
        date_str = dt.strftime("%Y-%m-%d")
    except Exception:
        date_str = "undated"

    raw_title = update.get("title", "Update")
    safe_title = re.sub(r"[^A-Za-z0-9 _-]", "", raw_title)[:50].strip()
    update_type = update.get("type", "update")
    return f"GK_BRAIN_Agent_Log/{date_str}/{update_type}/{safe_title}"


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
    with open(QUEUE_FILE, "w", encoding="utf-8") as fh:
        json.dump(queue, fh, indent=2)


# ---------------------------------------------------------------------------
# Main public function
# ---------------------------------------------------------------------------

def run_smart_wiki_updates(dry_run: bool = False) -> dict:
    """
    Process all pending wiki updates using the hybrid smart-merge + append strategy.

    Args:
        dry_run: If True, print what would be written without making any API calls.

    Returns:
        {"smart_merged": int, "appended": int, "failed": int, "skipped": int}
    """
    if dry_run:
        queue = _load_queue()
        pending = [u for u in queue if u.get("wiki_update") and not u.get("wiki_done")]
        print(f"[wiki-smart-merger] DRY-RUN — {len(pending)} pending update(s) would be processed:")
        for u in pending:
            ts = u.get("timestamp", "")
            try:
                dt = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
                display_time = dt.strftime("%d %B %Y, %H:%M UTC")
            except Exception:
                display_time = ts
            section = SECTION_MAP.get(u.get("type", ""), DEFAULT_SECTION)
            print(f"  • [{u.get('type', '?')}] {u.get('title', '?')} → section '{section}' at {display_time}")
        return {"smart_merged": 0, "appended": 0, "failed": 0, "skipped": len(pending)}

    if not FANDOM_USERNAME or not FANDOM_PASSWORD:
        print("[wiki-smart-merger] Credentials missing — skipping wiki update.")
        return {"smart_merged": 0, "appended": 0, "failed": 0, "skipped": 0}

    queue = _load_queue()
    pending = [u for u in queue if u.get("wiki_update") and not u.get("wiki_done")]

    if not pending:
        print("[wiki-smart-merger] No pending wiki updates.")
        return {"smart_merged": 0, "appended": 0, "failed": 0, "skipped": 0}

    session = requests.Session()
    if not _login(session):
        return {"smart_merged": 0, "appended": 0, "failed": len(pending), "skipped": 0}

    csrf_token = _get_csrf_token(session)
    smart_count = 0
    append_count = 0
    failed_count = 0

    # Fetch the main wiki page once; update in-memory for each entry
    main_page_content = _get_page_content(session, MAIN_WIKI_PAGE)

    for update in pending:
        try:
            ts = update.get("timestamp", "")
            try:
                dt = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
                display_time = dt.strftime("%d %B %Y, %H:%M UTC")
            except Exception:
                display_time = ts

            # --- Layer 2: Smart merge ---
            merged = False
            try:
                new_main_content, merged = _smart_merge_update(
                    main_page_content, update, display_time
                )
                if merged:
                    ok_smart = _edit_page(
                        session,
                        MAIN_WIKI_PAGE,
                        new_main_content,
                        f"GK BRAIN smart-merge: {update.get('title', 'update')}",
                        csrf_token,
                    )
                    if ok_smart:
                        main_page_content = new_main_content
                        smart_count += 1
                        resolved_section = SECTION_MAP.get(update.get('type', ''), DEFAULT_SECTION)
                        print(
                            f"[wiki-smart-merger] Smart-merged '{update.get('title')}' "
                            f"into section '{resolved_section}'"
                        )
                    else:
                        merged = False
            except Exception as merge_exc:
                print(
                    f"[wiki-smart-merger] Smart merge failed for "
                    f"'{update.get('title')}': {merge_exc} — falling back to append."
                )
                merged = False

            # --- Layer 1: Simple append (always runs as audit log) ---
            log_entry = _build_agent_log_entry(update, display_time, merged)
            ok_log = _append_to_page(
                session,
                AGENT_LOG_PAGE,
                log_entry,
                "GK BRAIN auto-log entry",
                csrf_token,
            )

            # If smart merge did not fire, also append a brief entry to the main page
            if not merged:
                fallback_entry = (
                    f"\n== Latest Agent Update ==\n"
                    f"'''[[{_sub_page_title(update)}|{update.get('title', 'Update')}]]''' "
                    f"detected on {display_time}. "
                    f"Type: {update.get('type', 'update')}.\n"
                )
                ok_fallback = _append_to_page(
                    session,
                    MAIN_WIKI_PAGE,
                    fallback_entry,
                    "GK BRAIN: latest update (fallback append)",
                    csrf_token,
                )
                # Re-read main page so next iteration has fresh content
                main_page_content = _get_page_content(session, MAIN_WIKI_PAGE)

                if ok_fallback and ok_log:
                    append_count += 1
                    update["wiki_done"] = True
                else:
                    failed_count += 1
            else:
                if ok_log:
                    update["wiki_done"] = True
                else:
                    failed_count += 1

        except Exception as exc:
            print(
                f"[wiki-smart-merger] Error processing "
                f"'{update.get('title')}': {exc}"
            )
            failed_count += 1

        # Polite rate limit
        time.sleep(2)

    _save_queue(queue)

    print(
        f"[wiki-smart-merger] Done — "
        f"smart_merged={smart_count}, appended={append_count}, "
        f"failed={failed_count}, skipped={len(queue) - len(pending)}"
    )
    return {
        "smart_merged": smart_count,
        "appended": append_count,
        "failed": failed_count,
        "skipped": len(queue) - len(pending),
    }


# ---------------------------------------------------------------------------
# CLI self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="GK BRAIN Smart Wiki Merger")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be written to the wiki without making any API calls.",
    )
    args = parser.parse_args()

    print("Running smart wiki merger…")
    result = run_smart_wiki_updates(dry_run=args.dry_run)
    print(json.dumps(result, indent=2))
