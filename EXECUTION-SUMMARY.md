# EXECUTION SUMMARY — GK BRAIN Run Lifecycle

This document describes what happens inside a single GitHub Actions workflow run.

---

## Run Trigger

The workflow (`.github/workflows/gk-brain.yml`) fires on a cron every 2 hours:
```
0 */2 * * *
```
It can also be triggered manually via `workflow_dispatch`.

---

## Step-by-Step Execution

### Step 1 — `crawl-brain.py` (Crawl Brain)
- Fetches all URLs listed in `gk-brain-complete.md` § LINKS.
- MD5-fingerprints each result against `crawl-fingerprints.json` to skip duplicates (DB-8).
- Writes newly discovered content to `crawl-results.json` and `brain1-canon.json`.
- No LLM used. Pure HTTP requests.

### Step 2 — `analytics-brain.py` (Analytics Brain)
- Reads `crawl-results.json` and `engagement-tracker.json`.
- Scores content by engagement, novelty, and faction coverage.
- Writes prioritised recommendations to `recommendations.json`.
- Saves a date-stamped JSON report to `reports/analytics-report-YYYY-MM-DD.json`.
- Optional stub modules loaded via `_safe_load()` — missing stubs are silently skipped.

### Step 3 — `gk-brain.py` (Lore Brain)
- Raises `EnvironmentError` immediately if `GROK_API_KEY` or `TELEGRAM_BOT_TOKEN` are absent (DB-10).
- Reads `lore-history.md` (last 40,000 chars) for continuity context (DB-9).
- Reads `recommendations.json` and injects up to 20% canon signal from `brain1-canon.json` (DB-2).
- Calls Claude 3.5 Sonnet (primary) or Grok (fallback) to generate **two lore posts** (DB-11).
- Generates an image for Post 2 using Grok — image stays in memory, never touches disk (DB-13).
- Posts Message 1 (text only) to every chat in `CHANNEL_CHAT_IDS`.
- Sleeps 2 seconds (DB-12).
- Posts Message 2 (text + image caption).
- Calls `pinChatMessage` with `disable_notification=True` (DB-14); pin failure is non-fatal.
- Queues ONLY web-crawl-sourced facts — never its own lore output — to `wiki-update-queue.json` (DB-1).
- Saves lore to `lore-history.md` and updates `bot-state.json`, `engagement-tracker.json`.

### Step 4 — `wiki-brain.py` (Wiki Brain)
- Runs `wiki_brain_health_check()` against `FANDOM_WIKI_URL/api.php`; aborts all writes if it fails (DB-7).
- Logs in via MediaWiki `clientlogin` API (see `fandom_auth.py`).
- Passes each queued entry through `wiki-smart-merger.py → _is_valid_wiki_source()` — Telegram/lore-post entries are silently dropped.
- Builds or refreshes wiki pages via `wiki-page-builder.py` and `wiki-smart-merger.py`.
- Marks processed entries `used: true` in `wiki-update-queue.json`.

### Step 5 — `master-backup-agent.py` (Backup Agent)
- SHA-256 fingerprints all 34 tracked repo files (DB-17).
- Extracts DB-N and MB-N rule headings from `.md` files.
- Detects any rule that contradicts a locked rule → logs conflict, does NOT overwrite (DB-16).
- Writes results atomically to `master-backup-state.json`.
- Always exits with code 0 (DB-15).

### Step 6 — Commit State Files
- Commits all updated JSON / `.md` state files back to `main`.

### Step 7 — Failure Notification
- If any brain step failed, sends a Telegram alert via the `Notify failure` workflow step.

---

## Exit Codes

| Brain | Fatal conditions | Exit code |
|---|---|---|
| `gk-brain.py` | Missing `GROK_API_KEY` / `TELEGRAM_BOT_TOKEN` | Non-zero |
| `wiki-brain.py` | Health-check failure | 2 |
| `master-backup-agent.py` | Any | 0 (always) |

All steps have `continue-on-error: true` — a single failure does not abort the workflow.
