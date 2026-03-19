# LORE RULE DETECTOR — DEEP LOGIC

How GK BRAIN enforces lore consistency rules during content generation.

---

## 1. Purpose

The Lore Rule Detector ensures every generated post:
- Uses only canon names and entities verified against official sources
- Does not contradict established lore (factions, characters, timeline)
- Stays within the 20% canon-signal injection cap (DB-2)
- Ignores signals older than 7 days (DB-3)

The core engine lives in `legacy/lore-rule-detector-engine.py` and is referenced by
`analytics-brain.py` via `_safe_load()`.

---

## 2. Canon Verification Flow

```
New proper noun detected in generated text
    │
    ▼
Check brain1-canon.json (signals from Crawl Brain)
    │
    ├── Found on official source URL → CANON ✅ → allow in lore, cite source
    │
    └── NOT on official source → NON-CANON ❌
            │
            ├── Log to non-canon-names.log
            └── Remove from generated text before posting
```

---

## 3. Signal Injection Rules (DB-2 and DB-3)

**DB-2 — 20% Cap:**
```
total_lore_tokens = len(generated_lore.split())
canon_signal_tokens = sum(len(s.get("content","").split()) for s in injected_signals)
assert canon_signal_tokens / total_lore_tokens <= 0.20
```

**DB-3 — 7-Day Staleness:**
```python
from datetime import datetime, timezone, timedelta
STALE_THRESHOLD = timedelta(days=7)
now = datetime.now(timezone.utc)
for signal in brain1_canon:
    age = now - datetime.fromisoformat(signal["timestamp"])
    if age > STALE_THRESHOLD:
        continue  # skip — stale, do NOT mark as used
```

---

## 4. Locked Rules the Detector Enforces

| Rule | Check |
|---|---|
| DB-1 | Lore posts never queued to wiki; detector blocks any `wiki_update` flag on a lore post |
| DB-2 | Canon signal share ≤ 20% of generated lore token count |
| DB-3 | Signals older than 7 days silently skipped |
| DB-4 | Signal marked `b2_used: true` ONLY after confirmed Telegram post |
| DB-5 | Post 2 image prompt contains at least one concrete scene element from Post 2 text |
| DB-11 | LLM routing: Claude primary → Grok text fallback (detector validates routing choice) |

---

## 5. Non-Canon Name Log

All rejected proper nouns are appended to `non-canon-names.log` with:
```
[TIMESTAMP] NON-CANON: "<name>" — found at URL: <url> — NOT in official sources
```

This log is committed back to `main` each run and can be reviewed manually to identify
fan-invented content that is trying to infiltrate the lore pipeline.

---

## 6. Faction Continuity Checks

Before finalising a lore post, the detector verifies:
- Named factions exist in the 40-faction roster (see `brain-rules.md` § The 40 Factions)
- Characters are assigned to their correct faction
- Timeline references do not contradict the Triple Fork Event (Year 2198) or Final Fork Prophecy (Year 3030)
- Technologies (Echo Ink, Sacred Chain, Null-Cipher, AETHER CHAIN) are used correctly

---

## 7. Integration with `analytics-brain.py`

`analytics-brain.py` loads the detector via `_safe_load()`:

```python
def _safe_load(module_path):
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("mod", module_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        return None

lore_detector = _safe_load("legacy/lore-rule-detector-engine.py")
```

If the module is missing or fails to load, analytics continues without it — no crash.

---

## 8. Rule Conflict Detection (Master Backup Agent)

`master-backup-agent.py` extracts all `DB-N` rule headings from `.md` files and checks
for contradictions against the locked rule set. If a file tries to override a DB rule,
the conflict is logged to `master-backup-state.json["conflicts"]` and the new rule is
silently discarded (DB-16).
