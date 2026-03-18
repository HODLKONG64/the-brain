"""
wiki-updater.py — Fandom Wiki Integration for GK BRAIN

Reads saved update data from wiki-update-queue.json and pushes it to the
GKniftyHEADS Fandom wiki via the MediaWiki API.

Called by gk-brain.py after Telegram posts are sent.

Usage (from gk-brain.py):
    from wiki_updater import run_wiki_updates
    run_wiki_updates()
"""

import json
import os
import re
import datetime
import time

import requests

ERRORS_FILE = os.path.join(os.path.dirname(__file__), "wiki-update-errors.json")

# Retry configuration
_MAX_RETRIES = 3
_RETRY_STATUSES = {429, 503}

QUEUE_FILE = os.path.join(os.path.dirname(__file__), "wiki-update-queue.json")

WIKI_API = "https://gkniftyheads.fandom.com/api.php"
FANDOM_USERNAME = os.environ.get("FANDOM_BOT_USER", os.environ.get("FANDOM_USERNAME", ""))
FANDOM_PASSWORD = os.environ.get("FANDOM_BOT_PASSWORD", os.environ.get("FANDOM_PASSWORD", ""))

# Main wiki page that receives a "Latest Updates" section
MAIN_WIKI_PAGE = "GKniftyHEADS_Wiki"
AGENT_LOG_PAGE = "GK_BRAIN_Agent_Log"


# ---------------------------------------------------------------------------
# Error logging
# ---------------------------------------------------------------------------

def _log_error(context: str, error: str) -> None:
    """Append a failure record to wiki-update-errors.json."""
    try:
        errors: list = []
        if os.path.exists(ERRORS_FILE):
            try:
                with open(ERRORS_FILE, "r", encoding="utf-8") as fh:
                    errors = json.load(fh)
            except (json.JSONDecodeError, OSError):
                errors = []
        errors.append({
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
            "context": context,
            "error": str(error),
        })
        with open(ERRORS_FILE, "w", encoding="utf-8") as fh:
            json.dump(errors, fh, indent=2)
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Retry helper
# ---------------------------------------------------------------------------

def _api_request(method: str, session: requests.Session, url: str, **kwargs) -> requests.Response:
    """Make an API request with up to _MAX_RETRIES retries on 429/503 errors."""
    last_exc: Exception = RuntimeError("No request attempts made")
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            resp = session.request(method, url, **kwargs)
            if resp.status_code in _RETRY_STATUSES and attempt < _MAX_RETRIES:
                wait = 2 ** attempt
                print(f"[wiki-updater] HTTP {resp.status_code} — retry {attempt}/{_MAX_RETRIES} in {wait}s")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp
        except requests.exceptions.HTTPError as exc:
            if exc.response is not None and exc.response.status_code in _RETRY_STATUSES and attempt < _MAX_RETRIES:
                wait = 2 ** attempt
                print(f"[wiki-updater] HTTP {exc.response.status_code} — retry {attempt}/{_MAX_RETRIES} in {wait}s")
                time.sleep(wait)
                last_exc = exc
                continue
            raise
        except requests.exceptions.RequestException as exc:
            if attempt < _MAX_RETRIES:
                wait = 2 ** attempt
                print(f"[wiki-updater] Request error — retry {attempt}/{_MAX_RETRIES} in {wait}s: {exc}")
                time.sleep(wait)
                last_exc = exc
                continue
            raise
    raise last_exc


# ---------------------------------------------------------------------------
# MediaWiki API helpers
# ---------------------------------------------------------------------------

def _get_login_token(session: requests.Session) -> str:
    resp = _api_request("GET", session, WIKI_API, params={
        "action": "query",
        "meta": "tokens",
        "type": "login",
        "format": "json",
    })
    return resp.json()["query"]["tokens"]["logintoken"]


def _login(session: requests.Session) -> bool:
    """Log in to Fandom with bot credentials. Returns True on success."""
    if not FANDOM_USERNAME or not FANDOM_PASSWORD:
        print("[wiki-updater] FANDOM credentials not set — skipping wiki updates.")
        return False

    token = _get_login_token(session)
    resp = _api_request("POST", session, WIKI_API, data={
        "action": "clientlogin",
        "loginmessageformat": "none",
        "username": FANDOM_USERNAME,
        "password": FANDOM_PASSWORD,
        "logintoken": token,
        "rememberMe": 1,
        "format": "json",
    })
    result = resp.json()
    if result.get("clientlogin", {}).get("status") == "PASS":
        print(f"[wiki-updater] Logged in as {FANDOM_USERNAME}")
        return True
    msg = f"Login failed: {result}"
    print(f"[wiki-updater] {msg}")
    _log_error("login", msg)
    return False


def _get_csrf_token(session: requests.Session) -> str:
    resp = _api_request("GET", session, WIKI_API, params={
        "action": "query",
        "meta": "tokens",
        "format": "json",
    })
    return resp.json()["query"]["tokens"]["csrftoken"]


def _get_page_content(session: requests.Session, title: str) -> str:
    """Fetch current wikitext content of a page (empty string if new page)."""
    resp = _api_request("GET", session, WIKI_API, params={
        "action": "query",
        "prop": "revisions",
        "rvprop": "content",
        "titles": title,
        "format": "json",
    })
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
    resp = _api_request("POST", session, WIKI_API, data={
        "action": "edit",
        "title": title,
        "text": content,
        "summary": summary,
        "bot": "true",
        "token": csrf_token,
        "format": "json",
    })
    result = resp.json()
    if result.get("edit", {}).get("result") == "Success":
        return True
    msg = f"Edit failed for '{title}': {result}"
    print(f"[wiki-updater] {msg}")
    _log_error(f"edit:{title}", msg)
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
# Wikitext formatting
# ---------------------------------------------------------------------------

def _update_to_wikitext(update: dict) -> str:
    """Convert a structured update dict to MediaWiki markup."""
    ts = update.get("timestamp", datetime.datetime.utcnow().isoformat() + "Z")
    # Parse ISO timestamp for display
    try:
        dt = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
        display_time = dt.strftime("%d %B %Y, %H:%M UTC")
    except Exception:
        display_time = ts

    update_type = update.get("type", "update").replace("-", " ").title()
    source = update.get("source", "")
    title = update.get("title", "Update")
    content = update.get("content", "")

    lines = [
        f"=== {title} ===",
        f"''Detected: {display_time}''",
        f"* '''Type:''' {update_type}",
        f"* '''Source:''' [{source} {source}]",
        "",
        content,
        "",
        "----",
    ]
    return "\n".join(lines)


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


def add_to_queue(updates: list) -> None:
    """
    Merge new updates into the queue file.
    Called by gk-brain.py after update detection.
    """
    queue = _load_queue()
    existing_sources = {e.get("source", "") + e.get("timestamp", "") for e in queue}
    for u in updates:
        key = u.get("source", "") + u.get("timestamp", "")
        if key not in existing_sources:
            queue.append(u)
    _save_queue(queue)


def persist_queue_updates(updates: list) -> None:
    """
    Update existing queue entries in-place (e.g. to persist the 'used' flag).
    Matches entries by source + timestamp and overwrites their data.
    Called by gk-brain.py after marking updates as used.
    """
    if not updates:
        return
    queue = _load_queue()
    index = {
        u.get("source", "") + u.get("timestamp", ""): i
        for i, u in enumerate(queue)
    }
    for u in updates:
        key = u.get("source", "") + u.get("timestamp", "")
        if key in index:
            queue[index[key]] = u
        else:
            queue.append(u)
    _save_queue(queue)


# ---------------------------------------------------------------------------
# Main public function
# ---------------------------------------------------------------------------

def run_wiki_updates() -> dict:
    """
    Process all pending wiki updates from the queue.

    Returns:
        {"success": int, "failed": int, "skipped": int}
    """
    if not FANDOM_USERNAME or not FANDOM_PASSWORD:
        print("[wiki-updater] Credentials missing — skipping wiki update.")
        return {"success": 0, "failed": 0, "skipped": 0}

    queue = _load_queue()
    pending = [u for u in queue if u.get("wiki_update") and not u.get("wiki_done")]

    if not pending:
        print("[wiki-updater] No pending wiki updates.")
        return {"success": 0, "failed": 0, "skipped": 0}

    session = requests.Session()
    if not _login(session):
        _log_error("run_wiki_updates", "Login failed — skipping wiki updates")
        return {"success": 0, "failed": len(pending), "skipped": 0}

    csrf_token = _get_csrf_token(session)
    success_count = 0
    failed_count = 0

    for update in pending:
        try:
            wikitext = _update_to_wikitext(update)
            sub_page = _sub_page_title(update)

            # 1. Create a dedicated sub-page for this update
            sub_success = _edit_page(
                session,
                sub_page,
                wikitext,
                f"GK BRAIN auto-update: {update.get('title', 'update')}",
                csrf_token,
            )

            # 2. Append a brief entry to the main agent log
            ts = update.get("timestamp", "")
            try:
                dt = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
                display_time = dt.strftime("%d %B %Y, %H:%M UTC")
            except Exception:
                display_time = ts

            log_entry = (
                f"* '''[[{sub_page}|{update.get('title', 'Update')}]]''' "
                f"— {update.get('type', 'update')} — {display_time}"
            )
            log_success = _append_to_page(
                session,
                AGENT_LOG_PAGE,
                log_entry,
                "GK BRAIN auto-log entry",
                csrf_token,
            )

            # 3. Update the main wiki page "Latest Agent Updates" section
            latest_entry = (
                f"\n== Latest Agent Update ==\n"
                f"'''[[{sub_page}|{update.get('title', 'Update')}]]''' "
                f"detected on {display_time}. "
                f"Type: {update.get('type', 'update')}.\n"
            )
            main_success = _append_to_page(
                session,
                MAIN_WIKI_PAGE,
                latest_entry,
                "GK BRAIN: latest update",
                csrf_token,
            )

            if sub_success and log_success and main_success:
                update["wiki_done"] = True
                success_count += 1
                print(f"[wiki-updater] Updated wiki for: {update.get('title')}")
            else:
                failed_count += 1
                _log_error(
                    f"update:{update.get('title', 'unknown')}",
                    f"One or more page edits failed (sub={sub_success}, log={log_success}, main={main_success})",
                )

        except Exception as exc:
            msg = f"Error processing update '{update.get('title')}': {exc}"
            print(f"[wiki-updater] {msg}")
            _log_error(f"update:{update.get('title', 'unknown')}", msg)
            failed_count += 1

        # Polite rate limit
        time.sleep(2)

    # Persist queue with updated wiki_done flags
    _save_queue(queue)

    print(
        f"[wiki-updater] Done — success={success_count}, "
        f"failed={failed_count}, skipped={len(queue) - len(pending)}"
    )
    return {"success": success_count, "failed": failed_count, "skipped": len(queue) - len(pending)}


# ---------------------------------------------------------------------------
# CLI self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Running wiki updater…")
    result = run_wiki_updates()
    print(json.dumps(result, indent=2))
