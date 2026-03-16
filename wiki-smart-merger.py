"""
wiki-smart-merger.py — Intelligent Wiki Merge System for GK BRAIN

Extends wiki-updater.py with smart section detection and targeted merging.

Behaviour per cycle:
  1. SMART MERGE  — Read current wiki page, detect existing sections,
                    insert/update the matching category section.
  2. SIMPLE APPEND — Always append a timestamped log entry regardless of
                     whether the smart merge succeeded (audit trail).

Called by gk-brain.py after Telegram posts are sent, as a drop-in
replacement for (or alongside) wiki-updater.run_wiki_updates().

Usage (from gk-brain.py):
    from wiki_smart_merger import run_smart_wiki_updates
    run_smart_wiki_updates()
"""

import json
import os
import re
import datetime
import time

import requests

# ---------------------------------------------------------------------------
# Configuration  (mirrors wiki-updater.py)
# ---------------------------------------------------------------------------

QUEUE_FILE = os.path.join(os.path.dirname(__file__), "wiki-update-queue.json")

WIKI_API = "https://gkniftyheads.fandom.com/api.php"
FANDOM_USERNAME = os.environ.get("FANDOM_USERNAME", "")
FANDOM_PASSWORD = os.environ.get("FANDOM_PASSWORD", "")

MAIN_WIKI_PAGE = "GKniftyHEADS_Wiki"
AGENT_LOG_PAGE = "GK_BRAIN_Agent_Log"
SMART_MERGE_LOG_PAGE = "GK_BRAIN_Smart_Merge_Log"

# ---------------------------------------------------------------------------
# Category → wiki section mapping
# Every category detected in update-detector.py maps to a named wiki section.
# ---------------------------------------------------------------------------

CATEGORY_SECTION_MAP = {
    "gkdata-real": "GK & GraffPUNKS Official Updates",
    "fishing-real": "Fishing Catches & Lake Adventures",
    "graffiti-news-real": "Street Art & Graffiti News",
    "news-real": "Crypto & Market News",
    "rave-real": "Raves & DJ Events",
}

# Fallback section if category is unknown
DEFAULT_SECTION = "Agent Updates"


# ---------------------------------------------------------------------------
# MediaWiki API helpers  (same as wiki-updater.py)
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
        print("[wiki-smart-merger] FANDOM credentials not set — skipping wiki updates.")
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
    """Fetch current wikitext content of a page (empty string if new page)."""
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
    """Edit (or create) a wiki page. Returns True on success."""
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
    """Append a section to an existing page (or create if not exists)."""
    existing = _get_page_content(session, title)
    new_content = existing.strip() + "\n\n" + section_wikitext.strip() + "\n"
    return _edit_page(session, title, new_content, summary, csrf_token)


# ---------------------------------------------------------------------------
# Smart section detection + merge helpers
# ---------------------------------------------------------------------------

def _parse_sections(wikitext: str) -> dict:
    """
    Parse wikitext into a dict of {section_heading: section_body}.
    Headings matched at == level 2 and === level 3.
    Returns an ordered dict mapping heading text → body text.
    """
    sections = {}
    current_heading = "__PREAMBLE__"
    current_lines = []

    for line in wikitext.splitlines():
        m = re.match(r"^(={2,3})\s*(.+?)\s*\1\s*$", line)
        if m:
            sections[current_heading] = "\n".join(current_lines)
            current_heading = m.group(2).strip()
            current_lines = []
        else:
            current_lines.append(line)

    sections[current_heading] = "\n".join(current_lines)
    return sections


def _rebuild_wikitext(sections: dict) -> str:
    """Rebuild full wikitext from a parsed sections dict."""
    parts = []
    for heading, body in sections.items():
        if heading == "__PREAMBLE__":
            if body.strip():
                parts.append(body.strip())
        else:
            parts.append(f"== {heading} ==")
            if body.strip():
                parts.append(body.strip())
    return "\n\n".join(parts) + "\n"


def _format_update_entry(update: dict, display_time: str) -> str:
    """Format a single update as a wiki list entry."""
    source = update.get("source", "")
    title = update.get("title", "Update")
    content = update.get("content", "")
    update_type = update.get("type", "update").replace("-", " ").title()

    source_line = f"* '''Source:''' [{source}]" if source else ""

    lines = [
        f"=== {title} ===",
        f"''Detected: {display_time}''",
        f"* '''Type:''' {update_type}",
    ]
    if source_line:
        lines.append(source_line)
    lines += [
        "",
        content[:500] if content else "",
        "",
        "----",
    ]
    return "\n".join(lines)


def _smart_merge_into_page(
    session: requests.Session,
    page_title: str,
    section_heading: str,
    new_entry_wikitext: str,
    summary: str,
    csrf_token: str,
) -> bool:
    """
    Read the page, locate the target section (or create it), prepend the new
    entry at the top of that section, and write the page back.

    Returns True on success.
    """
    existing_wikitext = _get_page_content(session, page_title)
    sections = _parse_sections(existing_wikitext)

    if section_heading in sections:
        # Section exists — prepend new entry after the heading
        old_body = sections[section_heading].strip()
        sections[section_heading] = new_entry_wikitext.strip() + (
            ("\n\n" + old_body) if old_body else ""
        )
    else:
        # Section missing — append it at the end
        sections[section_heading] = new_entry_wikitext.strip()

    new_wikitext = _rebuild_wikitext(sections)
    return _edit_page(session, page_title, new_wikitext, summary, csrf_token)


# ---------------------------------------------------------------------------
# Queue management  (mirrors wiki-updater.py)
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

    For every pending update:
      1. SMART MERGE  — Insert the update into the correct category section
                        on the main wiki page (creates section if missing).
      2. SIMPLE APPEND — Always append a timestamped entry to the agent log
                         (audit trail — never skipped).
      3. SUB-PAGE     — Create a dedicated sub-page with the full update detail.

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
    smart_merged = 0
    appended = 0
    failed = 0

    for update in pending:
        try:
            # --- Shared helpers ---
            ts = update.get("timestamp", "")
            try:
                dt = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
                display_time = dt.strftime("%d %B %Y, %H:%M UTC")
            except Exception:
                display_time = ts

            update_type = update.get("type", "update")
            title = update.get("title", "Update")
            source = update.get("source", "")

            # Derive the target wiki section from the update category
            section_heading = CATEGORY_SECTION_MAP.get(update_type, DEFAULT_SECTION)

            # --- 1. SMART MERGE into main wiki page ---
            entry_wikitext = _format_update_entry(update, display_time)
            merge_ok = _smart_merge_into_page(
                session,
                MAIN_WIKI_PAGE,
                section_heading,
                entry_wikitext,
                f"GK BRAIN smart-merge: [{update_type}] {title}",
                csrf_token,
            )
            if merge_ok:
                smart_merged += 1
                print(f"[wiki-smart-merger] Smart-merged into section '{section_heading}': {title}")
            else:
                print(f"[wiki-smart-merger] Smart merge failed for '{title}' — falling back to append.")

            time.sleep(1)

            # --- 2. SIMPLE APPEND to agent log (always runs) ---
            log_entry = (
                f"* '''[{update_type}]''' {title} "
                f"— {display_time}"
                + (f" — [{source} source]" if source else "")
            )
            append_ok = _append_to_page(
                session,
                AGENT_LOG_PAGE,
                log_entry,
                f"GK BRAIN log entry: {title}",
                csrf_token,
            )
            if append_ok:
                appended += 1

            time.sleep(1)

            # --- 3. SUB-PAGE — full detail page for this update ---
            sub_page = _sub_page_title(update)
            sub_wikitext = _full_update_wikitext(update, display_time)
            _edit_page(
                session,
                sub_page,
                sub_wikitext,
                f"GK BRAIN auto-update: {title}",
                csrf_token,
            )

            time.sleep(1)

            # --- 4. Smart merge log entry ---
            merge_status = "✅ smart-merged" if merge_ok else "⚠️ append-only"
            merge_log = (
                f"* {display_time} — [{update_type}] {title} — {merge_status}"
            )
            _append_to_page(
                session,
                SMART_MERGE_LOG_PAGE,
                merge_log,
                "GK BRAIN smart-merge log",
                csrf_token,
            )

            if merge_ok or append_ok:
                update["wiki_done"] = True
            else:
                failed += 1

        except Exception as exc:
            print(f"[wiki-smart-merger] Error processing '{update.get('title')}': {exc}")
            failed += 1

        time.sleep(2)

    _save_queue(queue)

    print(
        f"[wiki-smart-merger] Done — smart_merged={smart_merged}, "
        f"appended={appended}, failed={failed}, skipped={len(queue) - len(pending)}"
    )
    return {
        "smart_merged": smart_merged,
        "appended": appended,
        "failed": failed,
        "skipped": len(queue) - len(pending),
    }


# ---------------------------------------------------------------------------
# Wikitext formatting helpers
# ---------------------------------------------------------------------------

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


def _full_update_wikitext(update: dict, display_time: str) -> str:
    """Build a complete wiki sub-page for a single update."""
    source = update.get("source", "")
    title = update.get("title", "Update")
    content = update.get("content", "")
    update_type = update.get("type", "update").replace("-", " ").title()
    section_heading = CATEGORY_SECTION_MAP.get(update.get("type", ""), DEFAULT_SECTION)

    lines = [
        f"= {title} =",
        f"''Detected by GK BRAIN on {display_time}''",
        "",
        "== Details ==",
        f"* '''Type:''' {update_type}",
        f"* '''Category section:''' {section_heading}",
        f"* '''Lore weight:''' {update.get('lore_weight', 0.05) * 100:.0f}% of lore",
        "",
        "== Content ==",
        content if content else "''(No content extracted)''",
        "",
        "[[Category:GK BRAIN Agent Log]]",
        f"[[Category:{update_type}]]",
    ]
    if source:
        lines.insert(6, f"* '''Source:''' [{source}]")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Running smart wiki merger…")
    result = run_smart_wiki_updates()
    print(json.dumps(result, indent=2))
