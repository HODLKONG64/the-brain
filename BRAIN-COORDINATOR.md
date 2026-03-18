# BRAIN COORDINATOR

The GK BRAIN system runs as **four co-operating autonomous agents**, each with a
focused role. They run in sequence every 2 hours via GitHub Actions.

---

## 4-Brain Architecture

| Brain | File | Role | Model |
|---|---|---|---|
| **Crawl Brain** | `crawl-brain.py` | Web crawl & content detection | None (HTTP only) |
| **Analytics Brain** | `analytics-brain.py` | Performance analytics & recommendations | None (rule-based) |
| **Lore Brain** | `gk-brain.py` | Lore generation + Telegram posting + wiki queue | Claude 3.5 Sonnet (text) + Grok (image) |
| **Wiki Brain** | `wiki-brain.py` | Fandom wiki push | None (MediaWiki API) |

---

## Run Order (Every 2 Hours)

```
1. crawl-brain.py          → writes crawl-results.json
        ↓
2. analytics-brain.py      → writes recommendations.json + reports/analytics-report-YYYY-MM-DD.json
        ↓
3. gk-brain.py             → reads crawl-results.json + recommendations.json
                           → generates lore + images
                           → posts to Telegram
                           → writes wiki-update-queue.json
        ↓
4. wiki-brain.py           → reads wiki-update-queue.json
                           → pushes to Fandom wiki
        ↓
5. master-backup-agent.py  → fingerprints all tracked files
                           → absorbs rule/constant changes
                           → conflict-checks locked files
                           → writes master-backup-state.json
```

Each step has `continue-on-error: true` so one failure does not stop the chain.

---

## Inter-Brain Communication (JSON Files)

| File | Written By | Read By | Purpose |
|---|---|---|---|
| `crawl-results.json` | Crawl Brain | Lore Brain | Latest web crawl discoveries |
| `recommendations.json` | Analytics Brain | Lore Brain | Character/faction recommendations |
| `wiki-update-queue.json` | Lore Brain | Wiki Brain | Pending Fandom wiki updates |
| `engagement-tracker.json` | Lore Brain | Analytics Brain | Per-post engagement data |
| `crawl-fingerprints.json` | Crawl Brain | Crawl Brain | Dedup fingerprints (internal) |

---

## Secrets Required by Each Brain

| Secret | Crawl Brain | Analytics Brain | Lore Brain | Wiki Brain |
|---|---|---|---|---|
| `ANTHROPIC_API_KEY` | — | — | ✅ (Claude text) | — |
| `GROK_API_KEY` | — | — | ✅ (image gen) | — |
| `TELEGRAM_BOT_TOKEN` | — | — | ✅ | — |
| `CHANNEL_CHAT_IDS` | — | — | ✅ | — |
| `MESSAGE_THREAD_ID` | — | — | ✅ (optional) | — |
| `FANDOM_BOT_USER` | — | — | — | ✅ |
| `FANDOM_BOT_PASSWORD` | — | — | — | ✅ |
| `FANDOM_WIKI_URL` | — | — | — | ✅ (optional override) |

---

## GitHub Actions Cron Schedule

The workflow (`.github/workflows/gk-brain.yml`) runs every 2 hours:

```yaml
on:
  schedule:
    - cron: '0 */2 * * *'
```

Steps (in order, all with `continue-on-error: true`):
1. `python crawl-brain.py`
2. `python analytics-brain.py`
3. `python gk-brain.py`
4. `python wiki-brain.py`
5. `python master-backup-agent.py`
6. **Commit state files** — commits all updated JSON/MD state files back to `main`
7. **Failure notification** — sends a Telegram alert if any brain step failed

---

## What Each Brain Saves Back to Git

After every run, the workflow commits these state files:

| File | Brain |
|---|---|
| `lore-history.md` | Lore Brain |
| `bot-state.json` | Lore Brain |
| `brain2-telegram-lore.json` | Lore Brain |
| `crawl-snapshot.json` | Lore Brain |
| `wiki-update-queue.json` | Lore Brain / Wiki Brain |
| `telegram-offset.json` | Lore Brain |
| `engagement-tracker.json` | Lore Brain |
| `crawl-results.json` | Crawl Brain |
| `crawl-fingerprints.json` | Crawl Brain |
| `recommendations.json` | Analytics Brain |
| `reports/analytics-report-*.json` | Analytics Brain |
| `master-backup-state.json` | Backup Agent |

---

## Running Brains Manually

Each brain can be run standalone for testing:

```bash
# Crawl only
python crawl-brain.py

# Analytics only
python analytics-brain.py

# Full lore run
python gk-brain.py

# Wiki push only (preview mode)
python wiki-brain.py --dry-run

# Wiki push (live)
python wiki-brain.py
```

---

## Failure Recovery

- Each brain logs all errors to stdout (captured by GitHub Actions).
- `execution-reporter.py` generates `execution-report-YYYY-MM-DD-HHMMSS.json` after every lore run.
- Wiki Brain runs `wiki_brain_health_check()` before any writes.
- If Fandom login fails, Wiki Brain retries 3 times with backoff before giving up gracefully.
- A `notify-failure` workflow step sends a Telegram alert if the overall run fails.

---

## Brain 5: Master Backup Agent

| Property | Value |
|---|---|
| File | `master-backup-agent.py` |
| Workflow | `gk-brain.yml` (runs last, after wiki-brain) |
| Role | Passive observer — SHA-256 fingerprints all tracked files, absorbs rule/constant changes, conflict-checks locked files, writes `master-backup-state.json` |
| Always exits 0 | Yes — never blocks the commit step |
| State file | `master-backup-state.json` |

---

## Brain 3b: Web Lore Agent (Separate 6-Hour Cycle)

| Property | Value |
|---|---|
| File | `web-lore-agent.py` |
| Workflow | `.github/workflows/web-lore-agent.yml` |
| Schedule | Every 6 hours (`0 */6 * * *`) |
| Role | Crawls web sources for new lore material, enriches `wiki-update-queue.json` |
| State files | `web-lore-cache.json`, `web-lore-output.json`, `non-canon-names.log` |

Note: The web lore agent runs on its own independent schedule. The master-backup-agent also runs at the end of the web-lore-agent workflow so any files changed by the web lore agent are captured immediately, in addition to running at the end of the main 2-hour cycle.
