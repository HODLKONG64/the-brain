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
1. crawl-brain.py     → writes crawl-results.json
        ↓
2. analytics-brain.py → writes recommendations.json + reports/analytics-report-YYYY-MM-DD.json
        ↓
3. gk-brain.py        → reads crawl-results.json + recommendations.json
                      → generates lore + images
                      → posts to Telegram
                      → writes wiki-update-queue.json
        ↓
4. wiki-brain.py      → reads wiki-update-queue.json
                      → pushes to Fandom wiki
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

The workflow (`.github/workflows/gk-brain-cron.yml`) runs every 2 hours:

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
5. **Failure notification** — sends a Telegram alert if any step failed

---

## What Each Brain Saves Back to Git

After every run, the workflow commits these state files:

| File | Brain |
|---|---|
| `lore-history.md` | Lore Brain |
| `bot-state.json` | Lore Brain |
| `crawl-snapshot.json` | Lore Brain |
| `wiki-update-queue.json` | Lore Brain / Wiki Brain |
| `telegram-offset.json` | Lore Brain |
| `engagement-tracker.json` | Lore Brain |
| `crawl-results.json` | Crawl Brain |
| `crawl-fingerprints.json` | Crawl Brain |
| `recommendations.json` | Analytics Brain |
| `reports/analytics-report-*.json` | Analytics Brain |

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
