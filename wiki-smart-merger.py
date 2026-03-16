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
import json
import os
import re
import time

import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

QUEUE_FILE = os.path.join(os.path.dirname(__file__), "wiki-update-queue.json")

WIKI_API = os.environ.get("FANDOM_WIKI_URL", "https://gkniftyheads.fandom.com").rstrip("/") + "/api.php"
FANDOM_USERNAME = os.environ.get("FANDOM_BOT_USER", os.environ.get("FANDOM_USERNAME", ""))
FANDOM_PASSWORD = os.environ.get("FANDOM_BOT_PASSWORD", os.environ.get("FANDOM_PASSWORD", ""))

MAIN_WIKI_PAGE = "GKniftyHEADS_Wiki"
AGENT_LOG_PAGE = "GK_BRAIN_Agent_Log"

# Mapping: update type → wiki section heading (title-case, no '==' markers)
SECTION_MAP: dict[str, str] = {
    "fishing-real": "Fishing Records",
    "fishing": "Fishing Records",
    "graffiti-news-real": "Graffiti & Street Art",
    "graffiti": "Graffiti & Street Art",
    "gkdata-real": "NFT Drops & Collections",
    "nft": "NFT Drops & Collections",
    "rave-real": "Rave & Music Events",
    "rave": "Rave & Music Events",
    "news-real": "Latest News",
    "character": "Characters",
    "location": "Locations",
    "art-movement": "Art Movements & Styles",
    "dream": "Dream & Raid Events",
    "raid": "Dream & Raid Events",
    "lady-ink-hint": "Characters",
}

# Keywords used to scan existing section content for duplicate detection
DUPLICATE_KEYWORDS: dict[str, list[str]] = {
    "fishing-real": ["carp", "lb", "lake", "catch"],
    "fishing": ["carp", "lake", "fishing"],
    "graffiti-news-real": ["graffiti", "street art", "mural"],
    "graffiti": ["graffiti", "tag", "spray"],
    "gkdata-real": ["nft", "drop", "collection", "mint"],
    "nft": ["nft", "drop", "collection"],
    "rave-real": ["rave", "drum", "bass", "dj"],
    "rave": ["rave", "drum", "bass"],
    "news-real": ["news", "breaking"],
    "character": [],
    "location": [],
    "art-movement": [],
    "dream": ["dream", "raid"],
    "raid": ["raid", "dream"],
    "lady-ink-hint": ["lady-ink", "lady ink"],
}


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
        "action": "login",
        "lgname": FANDOM_USERNAME,
        "lgpassword": FANDOM_PASSWORD,
        "lgtoken": token,
        "format": "json",
    })
    resp.raise_for_status()
    result = resp.json()
    if result.get("login", {}).get("result") == "Success":
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


def _entry_already_present(body: str, update: dict) -> bool:
    """
    Heuristic: check whether this specific update already appears in a section.
    Uses the update title and a subset of duplicate keywords.
    """
    title = update.get("title", "").lower()
    if title and title in body.lower():
        return True
    content = update.get("content", "").lower()[:120]
    if content and content in body.lower():
        return True
    return False


# ---------------------------------------------------------------------------
# Smart merge logic
# ---------------------------------------------------------------------------

def _format_update_bullet(update: dict, display_time: str) -> str:
    """Format a single update as a wiki bullet point for insertion."""
    update_type = update.get("type", "update").replace("-", " ").title()
    source = update.get("source", "")
    title = update.get("title", "Update")
    content = update.get("content", "").strip()
    source_link = f" ([{source} source])" if source else ""

    lines = [
        f"* '''{title}''' — {update_type} — {display_time}{source_link}",
    ]
    if content:
        lines.append(f"  {content}")
    return "\n".join(lines)


def _smart_merge_update(
    page_content: str,
    update: dict,
    display_time: str,
) -> tuple[str, bool]:
    """
    Attempt to smart-merge one update into page_content.

    Returns (new_page_content, merged_ok).
    merged_ok is False when the update was already present or the type is unknown.
    """
    update_type = update.get("type", "")
    target_section = SECTION_MAP.get(update_type)

    if not target_section:
        return page_content, False

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

def run_smart_wiki_updates() -> dict:
    """
    Process all pending wiki updates using the hybrid smart-merge + append strategy.

    Returns:
        {"smart_merged": int, "appended": int, "failed": int, "skipped": int}
    """
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
                        print(
                            f"[wiki-smart-merger] Smart-merged '{update.get('title')}' "
                            f"into section '{SECTION_MAP.get(update.get('type', ''))}'"
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
    print("Running smart wiki merger…")
    result = run_smart_wiki_updates()
    print(json.dumps(result, indent=2))
