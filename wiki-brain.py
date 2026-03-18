"""
wiki-brain.py — GK BRAIN Standalone Wiki Brain

Reads wiki-update-queue.json and pushes pending updates to the
GKniftyHEADS Fandom wiki via wiki-smart-merger.py.

Features:
    - Credential health check before any writes
    - --dry-run flag for safe testing

Usage:
    python wiki-brain.py
    python wiki-brain.py --dry-run
"""

import argparse
import json

import importlib.util as _ilu
import pathlib as _pl


def _load_module(name: str, filepath: str):
    spec = _ilu.spec_from_file_location(name, _pl.Path(__file__).parent / filepath)
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_fandom_auth = _load_module("fandom_auth", "fandom_auth.py")
_wiki_smart_merger = _load_module("wiki_smart_merger", "wiki-smart-merger.py")


def wiki_brain_health_check() -> bool:
    """
    Verify Fandom credentials are configured and can log in before making
    any writes. Returns True on success, False otherwise.
    """
    if not _fandom_auth.FANDOM_USERNAME or not _fandom_auth.FANDOM_PASSWORD:
        print("[wiki-brain] FANDOM credentials not set — health check FAILED.")
        return False

    session = _fandom_auth.create_session()
    if session is None:
        print("[wiki-brain] Could not log in to Fandom — health check FAILED.")
        return False

    print(
        f"[wiki-brain] Health check PASSED — logged in as {_fandom_auth.FANDOM_USERNAME}"
    )
    return True


def run(dry_run: bool = False) -> dict:
    """
    Run the wiki brain: health check then process pending queue entries.
    """
    print(f"[wiki-brain] Starting {'(DRY RUN) ' if dry_run else ''}...")

    if not dry_run:
        if not wiki_brain_health_check():
            print("[wiki-brain] Skipping wiki updates due to failed health check.")
            return {"smart_merged": 0, "appended": 0, "failed": 0, "skipped": 0}

    result = _wiki_smart_merger.run_smart_wiki_updates(dry_run=dry_run)
    print(f"[wiki-brain] Done: {result}")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GK BRAIN wiki brain")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Log what would be written without making any API write calls.",
    )
    args = parser.parse_args()
    output = run(dry_run=args.dry_run)
    print(json.dumps(output, indent=2))
