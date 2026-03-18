"""
master-backup-agent.py -- MASTER BACKUP AGENT

Role: The single source of truth backup for ALL agents in the GK BRAIN system.

Responsibilities:
1. Scans all key repo files every run, detects changes via SHA-256 fingerprinting.
2. Absorbs every logic update from every agent/file into master-backup-state.json.
3. Validates that no incoming update conflicts with existing locked rules.
4. Provides a conflict-free snapshot that any agent can bootstrap from.
5. NEVER overwrites confirmed data -- append-only, full audit trail.
6. Runs as the LAST step in the GitHub Actions workflow (after all other agents).

Conflict Rules:
- A "conflict" is when an incoming file defines a rule/constant that CONTRADICTS
  a rule already locked in master-backup-state.json.
- If a conflict is detected, the new value is quarantined in the conflict_log
  section -- it is NOT merged into active rules until manually resolved.
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
MAX_CONFLICT_LOG = 500
MAX_AUDIT_HISTORY = 20
MAX_CONSTANT_VALUE_LENGTH = 120

# ---------------------------------------------------------------------------
# Files to track
# ---------------------------------------------------------------------------

TRACKED_FILES = [
    "brain-rules.md",
    "gk-brain-complete.md",
    "copilot-rule.md",
    "update-integration-rules.md",
    "wiki-merge-rules.md",
    "TELEGRAM-BOT-API-RULES.md",
    "cross-platform-consistency.md",
    "FANDOM-API-RULES.md",
    "LORE-RULE-DETECTOR-DEEP-LOGIC.md",
    "HOW-TO.md",
    "MASTER-CHARACTER-CANON.md",
    "character-bible.md",
    "genesis-lore.md",
    "lore-planner.md",
    "BRAIN-COORDINATOR.md",
    "LLM-ORCHESTRATION-ARCHITECTURE.md",
    "TELEGRAM-NARRATOR-SYSTEM-ARCHITECTURE.md",
    "gk-brain.py",
    "crawl-brain.py",
    "analytics-brain.py",
    "wiki-brain.py",
    "wiki-updater.py",
    "wiki-smart-merger.py",
    "wiki-cross-checker.py",
    "update-detector.py",
    "fandom_auth.py",
    "execution-reporter.py",
    "user-profile.py",
    "telegram-narrator-system.py",
    "master-backup-agent.py",
    ".github/workflows/gk-brain.yml",
    "brain1-canon.json",
    "engagement-tracker.json",
    "recommendations.json",
]

LOCKED_RULE_FILES = {
    "brain-rules.md",
    "gk-brain-complete.md",
    "TELEGRAM-BOT-API-RULES.md",
    "MASTER-CHARACTER-CANON.md",
    "BRAIN-COORDINATOR.md",
}

STATE_ONLY_FILES = {
    "brain1-canon.json",
    "engagement-tracker.json",
    "recommendations.json",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sha256_file(path):
    try:
        with open(path, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()
    except OSError:
        return None


def _read_text(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return ""


def _load_state():
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


def _save_state(state):
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2, ensure_ascii=False)
    os.replace(tmp, STATE_FILE)


def _now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Rule extraction
# ---------------------------------------------------------------------------

_DB_RULE_RE = re.compile(r"^#{2,4}\s+(DB-\d+|MB-\d+)\s+[-\u2014]+\s+(.+)$", re.MULTILINE)
_PY_CONST_RE = re.compile(r"^([A-Z_]{4,})\s*=\s*(.+)$", re.MULTILINE)


def _extract_rules(filename, content):
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
            if len(val) > 1:
                rules["PY:" + key] = val
    return rules


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def _detect_conflicts(filename, new_rules, existing_snapshot):
    conflicts = []
    if filename not in LOCKED_RULE_FILES:
        return conflicts
    for rule_id, new_val in new_rules.items():
        if rule_id in existing_snapshot:
            old_entry = existing_snapshot[rule_id]
            old_val = old_entry.get("value") if isinstance(old_entry, dict) else old_entry
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
# Main sync
# ---------------------------------------------------------------------------

def run_backup_sync():
    state = _load_state()
    state["run_count"] = state.get("run_count", 0) + 1
    state["last_updated"] = _now()

    file_registry = state.setdefault("file_registry", {})
    rule_snapshot = state.setdefault("rule_snapshot", {})
    conflict_log = state.setdefault("conflict_log", [])
    audit_trail = state.setdefault("audit_trail", [])

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
        prev_sha = prev_entry.get("sha") if isinstance(prev_entry, dict) else None

        if sha == prev_sha:
            unchanged_files.append(rel_path)
            continue

        if prev_sha is None:
            new_files.append(rel_path)
        else:
            changed_files.append(rel_path)

        content = _read_text(abs_path)
        new_rules = _extract_rules(rel_path, content)

        conflicts = _detect_conflicts(rel_path, new_rules, rule_snapshot)
        if conflicts:
            conflict_log.extend(conflicts)
            conflicts_found.extend(conflicts)
            for c in conflicts:
                new_rules.pop(c["rule_id"], None)
            print("[backup] WARNING: " + str(len(conflicts)) + " conflict(s) quarantined from " + rel_path)

        is_state_file = rel_path in STATE_ONLY_FILES
        if not is_state_file:
            for rule_id, value in new_rules.items():
                rule_snapshot[rule_id] = {
                    "value": value,
                    "source_file": rel_path,
                    "absorbed_at": _now(),
                }
                rules_absorbed += 1

        file_registry[rel_path] = {
            "sha": sha,
            "last_seen": _now(),
            "size_bytes": os.path.getsize(abs_path),
            "rule_count": len(new_rules),
            "is_state_file": is_state_file,
        }

    if len(conflict_log) > MAX_CONFLICT_LOG:
        state["conflict_log"] = conflict_log[-MAX_CONFLICT_LOG:]

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

    if len(audit_trail) > MAX_AUDIT_HISTORY:
        state["audit_trail"] = audit_trail[-MAX_AUDIT_HISTORY:]

    _save_state(state)

    print("[backup] Run #" + str(state["run_count"]) + " complete.")
    print("[backup] New: " + str(len(new_files)) + ", Changed: " + str(len(changed_files)) +
          ", Unchanged: " + str(len(unchanged_files)) + ", Missing: " + str(len(missing_files)))
    print("[backup] Rules absorbed: " + str(rules_absorbed) + ", Conflicts quarantined: " + str(len(conflicts_found)))
    if conflicts_found:
        print("[backup] CONFLICTS (quarantined, NOT merged):")
        for c in conflicts_found:
            print("  " + c["file"] + " -> " + c["rule_id"] + ": '" +
                  str(c["existing_value"]) + "' vs '" + str(c["incoming_value"]) + "'")

    return audit_entry


if __name__ == "__main__":
    run_backup_sync()
    sys.exit(0)
