"""
master-backup-agent.py — MASTER BACKUP AGENT

Role: The single source of truth backup for ALL agents in the GK BRAIN system.

Responsibilities:
1. Scans all key repo files every run, detects changes via SHA-256 fingerprinting.
2. Absorbs every logic update from every agent/file into master-backup-state.json.
3. Validates that no incoming update conflicts with existing locked rules.
4. Provides a conflict-free snapshot that any agent can bootstrap from.
5. NEVER overwrites confirmed data — append-only, full audit trail.
6. Runs as the LAST step in the GitHub Actions workflow (after all other agents).

Conflict Rules:
- A "conflict" is when an incoming file defines a rule/constant that CONTRADICTS
  a rule already locked in master-backup-state.json.
- If a conflict is detected, the new value is quarantined in the "conflict_log"
  section — it is NOT merged into active rules until manually resolved.
- Safe updates (new rules, additions, new files) are always accepted.

State File: master-backup-state.json
"""

import hashlib
import json
import os
import datetime
import re
import sys

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, "master-backup-state.json")
MAX_CONFLICT_LOG = 500        # max stored conflict entries before pruning oldest
MAX_SNAPSHOT_HISTORY = 20    # keep last N snapshots in audit trail
MAX_CONSTANT_VALUE_LENGTH = 120  # truncate extracted Python constant values to this length

# ---------------------------------------------------------------------------
# Files to track (all key logic/rule/canon files)
# ---------------------------------------------------------------------------

TRACKED_FILES = [
    # Core rules
    "brain-rules.md",
    "gk-brain-complete.md",
    "copilot-rule.md",
    "update-integration-rules.md",
    "wiki-merge-rules.md",
    "wiki-image-rules.md",
    "TELEGRAM-BOT-API-RULES.md",
    "OFFICIAL-SOURCE-AUTHORITY-RULES.md",
    "WEBLORERULES.md",
    "cross-platform-consistency.md",
    "FANDOM-API-RULES.md",
    "LORE-RULE-DETECTOR-DEEP-LOGIC.md",
    "HOW-TO.md",

    # Canon / lore
    "MASTER-CHARACTER-CANON.md",
    "character-bible.md",
    "genesis-lore.md",
    "lore-planner.md",
    "BRAIN-COORDINATOR.md",
    "LLM-ORCHESTRATION-ARCHITECTURE.md",
    "TELEGRAM-NARRATOR-SYSTEM-ARCHITECTURE.md",

    # Agent code
    "gk-brain.py",
    "gk-brain-recovery.py",
    "crawl-brain.py",
    "analytics-brain.py",
    "wiki-brain.py",
    "wiki-updater.py",
    "wiki-smart-merger.py",
    "wiki-cross-checker.py",
    "wiki-citation-checker.py",
    "wiki-formatter.py",
    "wiki-page-builder.py",
    "web-lore-agent.py",
    "update-detector.py",
    "fandom_auth.py",
    "execution-reporter.py",
    "user-profile.py",
    "master-backup-agent.py",

    # Workflows
    ".github/workflows/gk-brain.yml",
    ".github/workflows/web-lore-agent.yml",

    # State files (tracked but not merged into rule snapshot)
    "brain1-canon.json",
    "engagement-tracker.json",
    "recommendations.json",
]

# These files contain LOCKED rules that cannot be overridden by later updates.
# If a later run detects a change to any locked rule key, it is quarantined.
LOCKED_RULE_FILES = {
    "brain-rules.md",
    "gk-brain-complete.md",
    "TELEGRAM-BOT-API-RULES.md",
    "OFFICIAL-SOURCE-AUTHORITY-RULES.md",
    "MASTER-CHARACTER-CANON.md",
    "BRAIN-COORDINATOR.md",
    "copilot-rule.md",
}

# Files that are state/runtime data — changes are always accepted, never conflict-checked
STATE_ONLY_FILES = {
    "brain1-canon.json",
    "engagement-tracker.json",
    "recommendations.json",
    "crawl-results.json",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sha256_file(path: str) -> str | None:
    """Return SHA-256 hex digest of a file, or None if the file does not exist."""
    try:
        with open(path, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()
    except OSError:
        return None


def _read_text(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return ""


def _load_state() -> dict:
    """Load master-backup-state.json, returning a fresh skeleton if missing."""
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return {
            "schema_version": "1.0",
            "created_at": _now(),
            "last_updated": _now(),
            "run_count": 0,
            "file_registry": {},
            "rule_snapshot": {},
            "conflict_log": [],
            "audit_trail": [],
        }


def _save_state(state: dict) -> None:
    """Persist state to master-backup-state.json (atomic write via temp file)."""
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2, ensure_ascii=False)
    os.replace(tmp, STATE_FILE)


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Rule extraction (lightweight — extracts DB-xx rules and key constants)
# ---------------------------------------------------------------------------

# Matches lines like: ### DB-1 — Wiki Separation
# Note: three dash variants (em dash —, en dash –, hyphen -) are matched to handle
# copy/paste differences in rule headings across different editors.
_DB_RULE_RE = re.compile(r"^#{2,4}\s+(DB-\d+)\s+[—–-]+\s+(.+)$", re.MULTILINE)

# Matches Python constants like: SOME_CONSTANT = 42
# Minimum 3 chars to capture short but meaningful names (e.g. MAX, URL, API).
_PY_CONST_RE = re.compile(r"^([A-Z_]{3,})\s*=\s*(.+)$", re.MULTILINE)


def _extract_rules(filename: str, content: str) -> dict:
    """
    Extract named rules and key constants from file content.
    Returns a dict like {"DB-1": "Wiki Separation — ...", "DB-12": "..."}
    """
    rules = {}
    if filename.endswith(".md"):
        for match in _DB_RULE_RE.finditer(content):
            rule_id = match.group(1)
            rule_title = match.group(2).strip()
            rules[rule_id] = rule_title
    elif filename.endswith(".py"):
        for match in _PY_CONST_RE.finditer(content):
            key = match.group(1)
            val = match.group(2).strip()[:MAX_CONSTANT_VALUE_LENGTH]
            # Only track meaningful constants (skip single-char assignments)
            if len(val) > 1:
                rules[f"PY:{key}"] = val
    return rules


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def _detect_conflicts(
    filename: str,
    new_rules: dict,
    existing_snapshot: dict,
) -> list[dict]:
    """
    Compare new_rules against existing_snapshot for conflicts.
    A conflict occurs when a rule key exists in both dicts with DIFFERENT values
    AND the file is in LOCKED_RULE_FILES.

    Returns a list of conflict dicts.
    """
    conflicts = []
    if filename not in LOCKED_RULE_FILES:
        return conflicts

    for rule_id, new_val in new_rules.items():
        if rule_id in existing_snapshot:
            old_val = existing_snapshot[rule_id].get("value")
            if old_val is not None and old_val != new_val:
                conflicts.append({
                    "detected_at": _now(),
                    "file": filename,
                    "rule_id": rule_id,
                    "existing_value": old_val,
                    "incoming_value": new_val,
                    "status": "quarantined",
                    "resolution": None,
                })
    return conflicts


# ---------------------------------------------------------------------------
# Main sync logic
# ---------------------------------------------------------------------------

def run_backup_sync() -> dict:
    """
    Full sync cycle:
    1. Load existing state.
    2. Scan all tracked files for SHA changes.
    3. For changed/new files: extract rules, detect conflicts, update registry.
    4. Quarantine conflicting rules; merge safe updates into rule_snapshot.
    5. Append audit entry.
    6. Save state.

    Returns a summary dict.
    """
    state = _load_state()
    state["run_count"] = state.get("run_count", 0) + 1
    state["last_updated"] = _now()

    file_registry: dict = state.setdefault("file_registry", {})
    rule_snapshot: dict = state.setdefault("rule_snapshot", {})
    conflict_log: list = state.setdefault("conflict_log", [])
    audit_trail: list = state.setdefault("audit_trail", [])

    new_files = []
    changed_files = []
    unchanged_files = []
    missing_files = []
    conflicts_found = []
    rules_absorbed = 0

    for rel_path in TRACKED_FILES:
        abs_path = os.path.join(BASE_DIR, rel_path)
        sha = _sha256_file(abs_path)

        if sha is None:
            missing_files.append(rel_path)
            continue

        prev_entry = file_registry.get(rel_path, {})
        prev_sha = prev_entry.get("sha")

        if sha == prev_sha:
            unchanged_files.append(rel_path)
            continue

        # File is new or changed — process it
        if prev_sha is None:
            new_files.append(rel_path)
        else:
            changed_files.append(rel_path)

        content = _read_text(abs_path)
        new_rules = _extract_rules(rel_path, content)

        # Conflict detection (only for locked rule files)
        conflicts = _detect_conflicts(rel_path, new_rules, rule_snapshot)
        if conflicts:
            conflict_log.extend(conflicts)
            conflicts_found.extend(conflicts)
            # Remove conflicting keys from new_rules so they aren't merged
            for c in conflicts:
                new_rules.pop(c["rule_id"], None)
            print(
                f"[backup] ⚠️  {len(conflicts)} conflict(s) quarantined from {rel_path}"
            )

        # Merge safe rules into snapshot
        is_state_file = rel_path in STATE_ONLY_FILES
        if not is_state_file:
            for rule_id, value in new_rules.items():
                rule_snapshot[rule_id] = {
                    "value": value,
                    "source_file": rel_path,
                    "absorbed_at": _now(),
                }
                rules_absorbed += 1

        # Update file registry
        file_registry[rel_path] = {
            "sha": sha,
            "last_seen": _now(),
            "size_bytes": os.path.getsize(abs_path),
            "rule_count": len(new_rules),
            "is_state_file": is_state_file,
        }

    # Prune conflict log if too large
    if len(conflict_log) > MAX_CONFLICT_LOG:
        conflict_log = conflict_log[-MAX_CONFLICT_LOG:]
        state["conflict_log"] = conflict_log

    # Append audit entry
    audit_entry = {
        "run_at": _now(),
        "run_number": state["run_count"],
        "new_files": len(new_files),
        "changed_files": len(changed_files),
        "unchanged_files": len(unchanged_files),
        "missing_files": len(missing_files),
        "rules_absorbed": rules_absorbed,
        "conflicts_quarantined": len(conflicts_found),
        "new_file_list": new_files,
        "changed_file_list": changed_files,
        "missing_file_list": missing_files,
    }
    audit_trail.append(audit_entry)

    # Keep audit trail to last MAX_SNAPSHOT_HISTORY entries
    if len(audit_trail) > MAX_SNAPSHOT_HISTORY:
        state["audit_trail"] = audit_trail[-MAX_SNAPSHOT_HISTORY:]

    _save_state(state)

    # Print summary
    print(f"[backup] Run #{state['run_count']} complete.")
    print(f"[backup] New files: {len(new_files)}, Changed: {len(changed_files)}, "
          f"Unchanged: {len(unchanged_files)}, Missing: {len(missing_files)}")
    print(f"[backup] Rules absorbed: {rules_absorbed}, Conflicts quarantined: {len(conflicts_found)}")
    if new_files:
        print(f"[backup] New: {new_files}")
    if changed_files:
        print(f"[backup] Changed: {changed_files}")
    if conflicts_found:
        print(f"[backup] ⚠️  CONFLICTS (quarantined, NOT merged):")
        for c in conflicts_found:
            print(f"         {c['file']} → {c['rule_id']}: "
                  f"'{c['existing_value']}' vs '{c['incoming_value']}'")
    if missing_files:
        print(f"[backup] Missing (not in repo): {missing_files}")

    return audit_entry


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    result = run_backup_sync()
    # Exit 0 always — conflicts are quarantined but never cause a workflow failure
    sys.exit(0)
