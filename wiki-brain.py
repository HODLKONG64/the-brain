"""
wiki-brain.py — GK BRAIN Wiki Agent

Standalone wiki update agent. Reads wiki-update-queue.json and pushes
pending updates to the Fandom wiki. Runs independently or as part of the
4-brain GitHub Actions pipeline.

Usage:
    python wiki-brain.py [--dry-run]

Required secrets (env vars):
    FANDOM_BOT_USER
    FANDOM_BOT_PASSWORD
    FANDOM_WIKI_URL  (optional override; default: https://gkniftyheads.fandom.com)
"""

# ===========================================================================
# DB-19: Wiki ONLY for https://gkniftyheads.fandom.com — zero Wikipedia influence.
# DB-20: Wiki brain 100% blind to all Telegram output.
# DB-21: Scan these 7 URLs first every run + cite graffpunks.live subpages.
# DB-22: Cross-reference every crawl against PROJECT-DNA.md; force-create missing sections.
# DB-23: Run Wiki Teacher Crew every 2-hour cycle; dynamically expand crawl targets.
# DB-24: Add audit trail comment to every wiki edit section.
# ===========================================================================

FANDOM_WIKI_TARGET = "https://gkniftyheads.fandom.com"  # DB-19: sole wiki target

GRAFFPUNKS_PRIORITY_URLS = [  # DB-21: always scan these 7 first
    "https://graffpunks.live/the-lore/",
    "https://graffpunks.live/gk-factions/",
    "https://graffpunks.live/graffiti-kings-nfts/",
    "https://graffpunks.live/free-nfts/",
    "https://graffpunks.live/graffiti-nfts/",
    "https://graffpunks.live/the-vision/",
    "https://graffpunks.live/xrp-kids/",
]

TEACHER_AGENT_VERSION = "v2.0"  # DB-24 audit trail version tag
TEACHER_CYCLE_HOURS = 2          # DB-23: run every 2 hours


def _append_audit_trail(section_text: str) -> str:
    """DB-24: Append CrewAI Teacher v2 audit trail comment to a wiki section."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    trail = f"\n<!-- Updated via CrewAI Teacher v2 | {ts} UTC -->"
    if "Updated via CrewAI Teacher" not in section_text:
        return section_text + trail
    return section_text


import argparse
import json
import os
import sys
from datetime import datetime, timezone

import importlib.util as _ilu
import pathlib as _pl


def _load_module(name: str, filepath: str):
    spec = _ilu.spec_from_file_location(name, _pl.Path(__file__).parent / filepath)
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _safe_load(name: str, filepath: str):
    """Load a module, returning None on failure (non-fatal)."""
    try:
        return _load_module(name, filepath)
    except Exception as exc:
        print(f"[wiki-brain] Could not load {filepath}: {exc}")
        return None


# ---------------------------------------------------------------------------
# Load required modules
# ---------------------------------------------------------------------------

_data_validator      = _safe_load("data_validator",      "data-validator.py")
_deduplication       = _safe_load("deduplication",        "deduplication-engine.py")
_source_attribution  = _safe_load("source_attribution",   "source-attribution-system.py")
_wiki_updater        = _safe_load("wiki_updater",         "wiki-updater.py")
_wiki_smart_merger   = _safe_load("wiki_smart_merger",    "wiki-smart-merger.py")
_execution_reporter  = _safe_load("execution_reporter",   "execution-reporter.py")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

FANDOM_BOT_USER     = os.environ.get("FANDOM_BOT_USER", "")
FANDOM_BOT_PASSWORD = os.environ.get("FANDOM_BOT_PASSWORD", "")
FANDOM_WIKI_URL     = os.environ.get("FANDOM_WIKI_URL", "https://gkniftyheads.fandom.com")

BASE_DIR            = os.path.dirname(__file__)
QUEUE_FILE          = os.path.join(BASE_DIR, "wiki-update-queue.json")


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

def wiki_brain_health_check() -> bool:
    """
    Verify Fandom credentials before attempting any wiki writes.
    Returns True if credentials are present and the wiki API is reachable.
    """
    import requests

    if not FANDOM_BOT_USER or not FANDOM_BOT_PASSWORD:
        print("[wiki-brain] ❌ FANDOM_BOT_USER or FANDOM_BOT_PASSWORD not set.")
        return False

    wiki_api = FANDOM_WIKI_URL.rstrip("/") + "/api.php"
    try:
        resp = requests.get(
            wiki_api,
            params={"action": "query", "meta": "siteinfo", "format": "json"},
            timeout=10,
        )
        resp.raise_for_status()
        sitename = resp.json().get("query", {}).get("general", {}).get("sitename", "")
        print(f"[wiki-brain] ✅ Wiki API reachable — site: {sitename}")
        return True
    except Exception as exc:
        print(f"[wiki-brain] ❌ Wiki API unreachable: {exc}")
        return False


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
# Main
# ---------------------------------------------------------------------------

def run(dry_run: bool = False) -> int:
    """
    Process all pending wiki updates.
    Returns exit code (0 = success, 1 = partial failure, 2 = fatal error).
    """
    print("[wiki-brain] 🧠 Wiki Brain starting…")

    if not wiki_brain_health_check():
        print("[wiki-brain] Health check failed — aborting.")
        return 2

    queue = _load_queue()
    pending = [u for u in queue if u.get("wiki_update") and not u.get("wiki_done")]
    print(f"[wiki-brain] Pending updates: {len(pending)}")

    if not pending:
        print("[wiki-brain] Nothing to do.")
        return 0

    if dry_run:
        print("[wiki-brain] --dry-run mode — no writes will be made.")
        for u in pending:
            print(f"  • [DRY-RUN] Would push: {u.get('title', 'untitled')} ({u.get('type', '')})")
        return 0

    # Prefer smart merger; fall back to simple updater
    if _wiki_smart_merger is not None:
        try:
            result = _wiki_smart_merger.run_smart_wiki_updates()
            print(f"[wiki-brain] Smart merger result: {result}")
            failed = result.get("failed", 0)
        except Exception as exc:
            print(f"[wiki-brain] Smart merger crashed ({exc}); falling back to simple updater.")
            failed = len(pending)
    else:
        failed = len(pending)

    if failed > 0 and _wiki_updater is not None:
        print(f"[wiki-brain] Falling back to wiki-updater for {failed} items…")
        try:
            result = _wiki_updater.run_wiki_updates()
            print(f"[wiki-brain] Wiki updater result: {result}")
        except Exception as exc:
            print(f"[wiki-brain] Wiki updater also failed: {exc}")
            return 1

    print("[wiki-brain] ✅ Wiki Brain complete.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GK BRAIN Wiki Agent")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    args = parser.parse_args()
    sys.exit(run(dry_run=args.dry_run))
