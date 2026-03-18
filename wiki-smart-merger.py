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

Environment variables (see fandom_auth.py for shared vars):
    FANDOM_BOT_USER       Fandom bot username (preferred over FANDOM_USERNAME)
    FANDOM_USERNAME       Fandom username (fallback)
    FANDOM_BOT_PASSWORD   Fandom bot password (preferred over FANDOM_PASSWORD)
    FANDOM_PASSWORD       Fandom password (fallback)
    FANDOM_WIKI_URL       Wiki base URL (default: https://gkniftyheads.fandom.com)
    WIKI_DRY_RUN          Set to "1" to skip all actual writes (default: disabled)
    WIKI_API_DELAY        Seconds to sleep between API write calls (default: 1.0)
"""

import datetime
import hashlib
import importlib.util
import json
import logging
import os
import re
import time
from urllib.parse import urlparse

import filelock

import fandom_auth

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("wiki-smart-merger")

# ---------------------------------------------------------------------------
# Load centralised wiki-formatter module
# ---------------------------------------------------------------------------

def _load_wiki_formatter():
    _path = os.path.join(os.path.dirname(__file__), "wiki-formatter.py")
    _spec = importlib.util.spec_from_file_location("wiki_formatter", _path)
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    return _mod

try:
    _wf = _load_wiki_formatter()
    _lore_to_encyclopedic = _wf.lore_to_encyclopedic
    _apply_wikilinks = _wf.apply_wikilinks
    _build_cite_ref = _wf.build_cite_ref
    _build_category_tags = _wf.build_category_tags
    _ensure_references_section = _wf.ensure_references_section
    _ensure_categories = _wf.ensure_categories
except Exception as _wf_exc:
    print(f"[wiki-smart-merger] wiki-formatter unavailable ({_wf_exc}); using stubs.")
    def _lore_to_encyclopedic(t): return t
    def _apply_wikilinks(t): return t
    def _build_cite_ref(u, ti, ts): return ""
    def _build_category_tags(ut, yr): return ""
    def _ensure_references_section(t): return t
    def _ensure_categories(t, cats): return t

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

QUEUE_FILE = os.path.join(os.path.dirname(__file__), "wiki-update-queue.json")
# Lock file used to prevent concurrent queue reads/writes.
QUEUE_LOCK_FILE = QUEUE_FILE + ".lock"

REJECTED_DRAFTS_FILE = os.path.join(os.path.dirname(__file__), "wiki-rejected-drafts.json")

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
FINGERPRINT_PREFIX_LENGTH = 16     # hex chars of MD5 stored as wiki comment
CONTENT_SNIPPET_LENGTH = 200       # max chars of content shown in a wiki bullet


# ---------------------------------------------------------------------------
# Source validation guard
# ---------------------------------------------------------------------------

# Update types that must never be pushed to the wiki (Brain 2 / Telegram lore)
_BLOCKED_UPDATE_TYPES = {"lore-post", "telegram-lore", "brain-lore"}

# Official online source keywords allowed to trigger wiki updates
_OFFICIAL_SOURCE_KEYWORDS = (
    "substack",
    "medium",
    "graffpunks.live",
    "graffitikings.co.uk",
    "youtube",
    "youtu.be",
    "twitter.com",
    "x.com",
    "fandom.com",
    "fandom.wiki",
)


def _is_valid_wiki_source(update: dict) -> bool:
    """
    Validate that a queued update originated from an official online source
    before allowing it to be written to the Fandom wiki.

    Returns False (and logs a warning) for:
    - Any update from the gk-brain-agent (Brain 2 Telegram posts)
    - Any update with a telegram source
    - Lore-post / telegram-lore / brain-lore update types
    - Content that originated from genesis-lore.md

    Returns True only when the source is one of the approved official online
    sources (Substack, Medium, official websites, YouTube, X/Twitter, Fandom).
    """
    source = update.get("source", "")
    update_type = update.get("type", "")

    def _block(reason: str) -> bool:
        logger.info(
            "[WIKI GUARD] Blocked wiki update — source not in official sources: %s / type: %s",
            source or "(none)",
            update_type or "(none)",
        )
        return False

    # Brain 2 agent-generated posts
    if source == "gk-brain-agent":
        return _block("source is gk-brain-agent")

    # Telegram source (any form)
    if "telegram" in source.lower():
        return _block("telegram source")

    # Lore-post types must never go to wiki
    if update_type in _BLOCKED_UPDATE_TYPES:
        return _block(f"blocked update type: {update_type}")

    # Brain 2 auto-queued wiki_update flag combined with agent source
    if update.get("wiki_update") is True and source == "gk-brain-agent":
        return _block("Brain 2 auto-queued update")

    # genesis-lore.md content
    origin = (
        update.get("origin", "")
        or update.get("file", "")
        or update.get("source_file", "")
        or ""
    )
    if "genesis-lore" in origin.lower():
        return _block("genesis-lore.md content")

    # If source is a URL/identifier, verify it comes from an approved domain.
    # Empty or purely internal sources (no recognised official keyword) are blocked.
    source_lower = source.lower()
    if source_lower and not any(kw in source_lower for kw in _OFFICIAL_SOURCE_KEYWORDS):
        # Only block when the source string looks like an explicit identifier
        # (not an empty queue entry that predates source tagging).
        if source_lower not in ("", "unknown", "manual"):
            return _block("source not in approved official sources list")

    return True


# ---------------------------------------------------------------------------
# Wikitext layout validation
# ---------------------------------------------------------------------------

def _validate_wikitext_layout(wikitext: str, page_title: str) -> tuple[bool, str]:
    """
    Check *wikitext* for common broken layout patterns before writing to wiki.

    Returns ``(True, "")`` when the markup looks safe to publish.
    Returns ``(False, reason)`` when a problem is detected.
    """
    # 1. Unclosed {{ }} template tags
    open_templates = wikitext.count("{{")
    close_templates = wikitext.count("}}")
    if open_templates != close_templates:
        return False, (
            f"unclosed template tags: {open_templates} '{{{{' vs {close_templates} '}}}}'"
        )

    # 2. Unclosed <div> tags
    open_divs = len(re.findall(r"<div[\s>]", wikitext, re.IGNORECASE))
    close_divs = len(re.findall(r"</div\s*>", wikitext, re.IGNORECASE))
    if open_divs != close_divs:
        return False, f"unclosed <div> tags: {open_divs} open vs {close_divs} close"

    # 3. Vertical text artifacts — more than 3 consecutive single-character lines
    lines = wikitext.splitlines()
    consecutive_single = 0
    for line in lines:
        stripped = line.strip()
        if re.match(r"^[A-Za-z]$", stripped):
            consecutive_single += 1
            if consecutive_single > 3:
                return False, "vertical text artifact detected (>3 consecutive single-character lines)"
        else:
            consecutive_single = 0

    # 4. Broken sidebar widget CSS
    if "writing-mode: vertical" in wikitext or "transform: rotate" in wikitext:
        return False, "broken sidebar widget CSS detected (writing-mode or transform:rotate)"

    return True, ""


def _save_rejected_draft(page_title: str, wikitext: str, reason: str) -> None:
    """Persist rejected wikitext to wiki-rejected-drafts.json for human review."""
    try:
        drafts: list = []
        if os.path.exists(REJECTED_DRAFTS_FILE):
            try:
                with open(REJECTED_DRAFTS_FILE, "r", encoding="utf-8") as fh:
                    drafts = json.load(fh)
            except (json.JSONDecodeError, OSError):
                drafts = []
        drafts.append({
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "page_title": page_title,
            "reason": reason,
            "wikitext": wikitext,
        })
        with open(REJECTED_DRAFTS_FILE, "w", encoding="utf-8") as fh:
            json.dump(drafts, fh, indent=2)
        logger.info("Rejected draft saved to %s", REJECTED_DRAFTS_FILE)
    except Exception as exc:
        logger.warning("Failed to save rejected draft: %s", exc)


# ---------------------------------------------------------------------------
# Queue management (file-locked to prevent race conditions)
# ---------------------------------------------------------------------------

def _load_queue() -> list:
    """Load the queue file under an exclusive file lock."""
    lock = filelock.FileLock(QUEUE_LOCK_FILE, timeout=30)
    with lock:
        if os.path.exists(QUEUE_FILE):
            try:
                with open(QUEUE_FILE, "r", encoding="utf-8") as fh:
                    return json.load(fh)
            except (json.JSONDecodeError, OSError):
                logger.warning("Queue file unreadable — starting with empty queue.")
                return []
    return []


def _login(session: requests.Session) -> bool:
    """Log in to Fandom with bot credentials. Returns True on success.

    Retries up to 3 times with exponential backoff on transient errors.
    Never crashes — logs all failures and returns False on auth failure.
    """
    if not FANDOM_USERNAME or not FANDOM_PASSWORD:
        print("[wiki-smart-merger] FANDOM credentials not set — skipping.")
        return False

    max_attempts = 3
    last_exc: Exception = RuntimeError("No attempts made")
    for attempt in range(1, max_attempts + 1):
        try:
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
            status = result.get("clientlogin", {}).get("status", "")
            if status == "PASS":
                print(f"[wiki-smart-merger] Logged in as {FANDOM_USERNAME}")
                return True
            message = result.get("clientlogin", {}).get("message", str(result))
            print(f"[wiki-smart-merger] Login attempt {attempt}/{max_attempts} failed: {message}")
            if status in ("FAIL",):
                # Auth credential failure — no point retrying
                return False
            last_exc = RuntimeError(f"Login status: {status} — {message}")
        except requests.exceptions.HTTPError as exc:
            print(f"[wiki-smart-merger] Login HTTP error (attempt {attempt}/{max_attempts}): {exc}")
            last_exc = exc
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as exc:
            print(f"[wiki-smart-merger] Login connection error (attempt {attempt}/{max_attempts}): {exc}")
            last_exc = exc
        except Exception as exc:
            print(f"[wiki-smart-merger] Login unexpected error (attempt {attempt}/{max_attempts}): {exc}")
            last_exc = exc
        if attempt < max_attempts:
            wait = 2 ** attempt
            print(f"[wiki-smart-merger] Retrying login in {wait}s…")
            time.sleep(wait)

    print(f"[wiki-smart-merger] All login attempts failed: {last_exc}")
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
    Parse wikitext into an ordered dict of {section_heading: section_body}.

    Matches ``== Heading ==`` with optional surrounding whitespace.
    The key ``""`` holds any pre-heading preamble.
    """
    sections: dict[str, str] = {}
    current_heading = ""
    buffer: list[str] = []

    for line in wikitext.splitlines():
        # Robust heading regex: capture opening and closing = runs separately so
        # we can verify they are identical (rejects mismatched counts like == h ===).
        match = re.match(r"^(={2,})\s*(.+?)\s*(={2,})\s*$", line)
        if match and match.group(1) == match.group(3):
            sections[current_heading] = "\n".join(buffer)
            current_heading = match.group(2)
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
            # Always use proper MediaWiki == Section Name == syntax.
            parts.append(f"== {heading} ==")
            parts.append(body)
    return "\n".join(parts).strip() + "\n"


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
    Smart duplicate detection using source URL, exact title+date match,
    and content-hash fingerprint.

    Returns True if this update appears to already be present in *body*.
    """
    # 1. Check by source URL (most reliable — exact key match).
    source_url = update.get("url") or update.get("source", "")
    if source_url and source_url in body:
        logger.debug(
            "Duplicate detected by source URL for '%s'", update.get("title")
        )
        return True

    # 2. Check by exact title + date (not a substring match against full content).
    title = update.get("title", "")
    timestamp = update.get("timestamp", "")
    if title and timestamp:
        date_part = timestamp[:10]  # YYYY-MM-DD
        # Both title and date must be present in the same line.
        for line in body.splitlines():
            if title.lower() in line.lower() and date_part in line:
                logger.debug(
                    "Duplicate detected by title+date for '%s'", title
                )
                return True

    # 3. Check by content fingerprint embedded as a wiki comment.
    content = update.get("content", "")
    if content and len(content) > 50:
        fingerprint = _get_content_fingerprint(content)
        if fingerprint[:FINGERPRINT_PREFIX_LENGTH] in body:
            logger.debug(
                "Duplicate detected by fingerprint for '%s'", update.get("title")
            )
            return True

    return False


# ---------------------------------------------------------------------------
# Smart merge logic
# ---------------------------------------------------------------------------

def _format_update_bullet(update: dict, display_time: str) -> str:
    """Format a single update as a wiki bullet point with inline citation."""
    title = update.get("title", "Update")
    source_url = update.get("url") or update.get("source", "")
    source_domain = _extract_domain(source_url) if source_url else ""
    content = update.get("content", "").strip()
    ts = update.get("timestamp", "")

    # Convert first-person lore to encyclopedic prose
    content = _lore_to_encyclopedic(content)

    # Embed content fingerprint as a hidden comment for future duplicate detection.
    fingerprint_comment = ""
    if content and len(content) > 50:
        fp = _get_content_fingerprint(content)
        fingerprint_comment = f"<!-- fp:{fp[:FINGERPRINT_PREFIX_LENGTH]} -->"

    # Build inline citation
    cite = _build_cite_ref(source_url, title, ts)

    if source_url:
        lines = [
            f"* '''[[{title}]]''' — {source_domain} — {display_time} {fingerprint_comment}",
        ]
        if content:
            snippet = content[:CONTENT_SNIPPET_LENGTH]
            suffix = "..." if len(content) > CONTENT_SNIPPET_LENGTH else ""
            # Apply wikilinks to snippet, then append citation
            linked_snippet = _apply_wikilinks(snippet)
            lines.append(f"  {linked_snippet}{suffix}{cite}")
        elif cite:
            lines[0] = lines[0].rstrip() + cite
    else:
        lines = [
            f"* '''{title}''' — {display_time} {fingerprint_comment}",
        ]
        if content:
            snippet = content[:CONTENT_SNIPPET_LENGTH]
            suffix = "..." if len(content) > CONTENT_SNIPPET_LENGTH else ""
            linked_snippet = _apply_wikilinks(snippet)
            lines.append(f"  {linked_snippet}{suffix}{cite}")
        elif cite:
            lines[0] = lines[0].rstrip() + cite

    return "\n".join(lines)


def _smart_merge_update(
    page_content: str,
    update: dict,
    display_time: str,
) -> tuple[str, bool]:
    """
    Attempt to smart-merge one update into *page_content*.

    Returns ``(new_page_content, merged_ok)``.
    ``merged_ok`` is False only when the update was already present (duplicate).
    Unknown update types are placed in DEFAULT_SECTION.
    """
    update_type = update.get("type", "")
    target_section = SECTION_MAP.get(update_type, DEFAULT_SECTION)

    sections = _parse_sections(page_content)

    # Duplicate check before touching anything.
    if _entry_already_present(page_content, update):
        logger.info(
            "Skipping duplicate: '%s' already present on page.", update.get("title")
        )
        return page_content, False

    bullet = _format_update_bullet(update, display_time)

    if target_section in sections:
        # Insert bullet at the top of the existing section body.
        existing_body = sections[target_section]
        sections[target_section] = bullet + "\n" + existing_body
        logger.debug(
            "Inserted '%s' into existing section '%s'",
            update.get("title"),
            target_section,
        )
    else:
        # Create new section at the end of the page with proper MediaWiki syntax.
        sections[target_section] = bullet + "\n"
        logger.debug(
            "Created new section '%s' for '%s'",
            target_section,
            update.get("title"),
        )

    new_content = _rebuild_page(sections)

    # Ensure == References == section exists
    new_content = _ensure_references_section(new_content)

    # Determine year from update timestamp
    ts = update.get("timestamp", "")
    try:
        dt = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
        year = dt.strftime("%Y")
    except Exception:
        year = str(datetime.datetime.utcnow().year)

    # Build and append any missing category tags
    cat_tags_str = _build_category_tags(update_type, year)
    if cat_tags_str:
        categories = [t for t in cat_tags_str.splitlines() if t.strip()]
        new_content = _ensure_categories(new_content, categories)

    return new_content, True


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
# Stale entry cleanup
# ---------------------------------------------------------------------------

def flush_stale_entries(max_age_days: int = 7) -> None:
    """Remove entries older than *max_age_days* that are already marked used."""
    if not os.path.exists(QUEUE_FILE):
        return
    try:
        with open(QUEUE_FILE, "r", encoding="utf-8") as fh:
            entries = json.load(fh)
    except (json.JSONDecodeError, OSError):
        return

    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=max_age_days)
    kept = [
        e for e in entries
        if not e.get("used")
        or datetime.datetime.fromisoformat(
            e.get("timestamp", "1970-01-01T00:00:00Z").replace("Z", "+00:00")
        ) >= cutoff
    ]
    if len(kept) < len(entries):
        with open(QUEUE_FILE, "w", encoding="utf-8") as fh:
            json.dump(kept, fh, indent=2)
        print(f"[wiki-merger] Flushed {len(entries) - len(kept)} stale queue entries.")


# ---------------------------------------------------------------------------
# Citation-checker loader (lazy import to keep module self-contained)
# ---------------------------------------------------------------------------

def _load_citation_checker():
    """Load wiki-citation-checker.py via importlib. Returns None if not found."""
    path = os.path.join(os.path.dirname(__file__), "wiki-citation-checker.py")
    if not os.path.exists(path):
        return None
    spec = importlib.util.spec_from_file_location("wiki_citation_checker", path)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
        return mod
    except Exception as exc:
        logger.warning("Could not load wiki-citation-checker.py: %s", exc)
        return None


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
        logger.info("No pending wiki updates.")
        flush_stale_entries()
        return {"smart_merged": 0, "appended": 0, "failed": 0, "skipped": 0}

    if dry_run:
        logger.info("[DRY RUN] Would process %d pending wiki updates.", len(pending))
        flush_stale_entries()
        return {"smart_merged": 0, "appended": 0, "failed": 0, "skipped": len(pending)}

    session = fandom_auth.create_session()
    if session is None:
        return {"smart_merged": 0, "appended": 0, "failed": len(pending), "skipped": 0}

    # --- Citation health-check pass (Rule 9) ---
    # Run before any page write so all existing citation URLs are verified live.
    # Errors inside the checker are caught internally and never block the write.
    try:
        wiki_citation_checker = _load_citation_checker()
        if wiki_citation_checker is not None:
            logger.info("Running citation health-check pass before wiki writes…")
            wiki_citation_checker.check_and_repair_citations(session=session, dry_run=dry_run)
        else:
            logger.warning("wiki-citation-checker.py not found — skipping citation pass.")
    except Exception as _cite_exc:
        logger.warning("Citation health-check error (non-fatal): %s", _cite_exc)

    smart_count = 0
    append_count = 0
    failed_count = 0

    # Fetch the main wiki page once; update in-memory for each entry.
    main_page_content = fandom_auth.get_page_content(session, MAIN_WIKI_PAGE)

    for update in pending:
        try:
            # --- Source validation guard (must pass before any wiki write) ---
            if not _is_valid_wiki_source(update):
                update["wiki_done"] = True  # mark as processed so it won't retry
                continue

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
                    # --- Layout validation before writing ---
                    layout_ok, layout_reason = _validate_wikitext_layout(
                        new_main_content, MAIN_WIKI_PAGE
                    )
                    if not layout_ok:
                        logger.info(
                            "[LAYOUT GUARD] Blocked wiki write to %s — layout validation failed: %s",
                            MAIN_WIKI_PAGE,
                            layout_reason,
                        )
                        _save_rejected_draft(MAIN_WIKI_PAGE, new_main_content, layout_reason)
                        merged = False
                    else:
                        ok_smart = fandom_auth.edit_page(
                            session,
                            MAIN_WIKI_PAGE,
                            new_main_content,
                            f"GK BRAIN smart-merge: {update.get('title', 'update')}",
                            check_hash=False,  # We already ran our own dedup check.
                        )
                        if ok_smart:
                            main_page_content = new_main_content
                            smart_count += 1
                            resolved_section = SECTION_MAP.get(
                                update.get("type", ""), DEFAULT_SECTION
                            )
                            logger.info(
                                "Smart-merged '%s' into section '%s'",
                                update.get("title"),
                                resolved_section,
                            )
                        else:
                            merged = False
            except Exception as merge_exc:
                logger.warning(
                    "Smart merge failed for '%s': %s — falling back to append.",
                    update.get("title"),
                    merge_exc,
                )
                merged = False

            # --- Layer 1: Simple append (always runs as audit log) ---
            log_entry = _build_agent_log_entry(update, display_time, merged)
            ok_log = fandom_auth.append_to_page(
                session,
                AGENT_LOG_PAGE,
                log_entry,
                "GK BRAIN auto-log entry",
            )

            # If smart merge did not fire, also append a brief entry to the main page.
            if not merged:
                fallback_entry = (
                    f"\n== Latest Agent Update ==\n"
                    f"'''[[{_sub_page_title(update)}|{update.get('title', 'Update')}]]''' "
                    f"detected on {display_time}. "
                    f"Type: {update.get('type', 'update')}.\n"
                )
                # Validate fallback snippet layout before appending.
                layout_ok, layout_reason = _validate_wikitext_layout(
                    fallback_entry, MAIN_WIKI_PAGE
                )
                if not layout_ok:
                    logger.info(
                        "[LAYOUT GUARD] Blocked fallback append to %s — layout validation failed: %s",
                        MAIN_WIKI_PAGE,
                        layout_reason,
                    )
                    _save_rejected_draft(MAIN_WIKI_PAGE, fallback_entry, layout_reason)
                    failed_count += 1
                    continue
                ok_fallback = fandom_auth.append_to_page(
                    session,
                    MAIN_WIKI_PAGE,
                    fallback_entry,
                    "GK BRAIN: latest update (fallback append)",
                )
                # Re-read main page so next iteration has fresh content.
                main_page_content = fandom_auth.get_page_content(session, MAIN_WIKI_PAGE)

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
            logger.error(
                "Error processing '%s': %s", update.get("title"), exc
            )
            failed_count += 1

        # Polite rate limit between entries.
        time.sleep(fandom_auth.API_DELAY)

    _save_queue(queue)
    flush_stale_entries()

    logger.info(
        "Done — smart_merged=%d, appended=%d, failed=%d, skipped=%d",
        smart_count,
        append_count,
        failed_count,
        len(queue) - len(pending),
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
