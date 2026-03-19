# HOW-TO — GK BRAIN Operational Guide

Step-by-step instructions for running, testing, and maintaining the GK BRAIN system.

---

## Prerequisites

- Python 3.12
- All secrets set (see `AGENT-EXPLAINER.md` § Secrets Required)
- `pip install -r requirements.txt`

---

## Running Individual Brains

```bash
# Brain 1 — web crawl only
python crawl-brain.py

# Brain 2 — analytics only
python analytics-brain.py

# Brain 3 — lore generation + Telegram post
python gk-brain.py

# Brain 4 — wiki push (live)
python wiki-brain.py

# Brain 4 — wiki push (dry run, no writes)
python wiki-brain.py --dry-run

# Brain 5 — backup agent
python master-backup-agent.py
```

---

## Running the Full Pipeline Locally

```bash
python crawl-brain.py && \
python analytics-brain.py && \
python gk-brain.py && \
python wiki-brain.py && \
python master-backup-agent.py
```

---

## Triggering a Manual GitHub Actions Run

1. Go to **Actions** → **GK BRAIN** workflow.
2. Click **Run workflow** → **Run workflow** (uses `main` branch).

The workflow runs all 5 brains in sequence, then commits updated state files back to `main`.

---

## Checking the Wiki Queue

```bash
cat wiki-update-queue.json | python -m json.tool | grep -E '"page_title"|"source"|"used"'
```

Entries with `"used": false` are pending. Entries with `"used": true` have been processed.

---

## Clearing Stale Queue Entries

`wiki-smart-merger.py` automatically flushes entries where `used == true` and timestamp older
than the configured cutoff. To trigger a manual flush:

```python
from wiki_smart_merger import flush_stale_entries
flush_stale_entries()
```

---

## Adding a New Official Source Domain

1. Add the domain keyword to `_OFFICIAL_SOURCE_KEYWORDS` in `wiki-smart-merger.py`.
2. Add the same domain to the `## Approved Domains` table in `OFFICIAL-SOURCE-AUTHORITY-RULES.md`.
3. Add the full URL to `gkandcryptomoonboywebsitestosave.md`.
4. Add the full URL to the seed list in `crawl-brain.py` (and `gk-brain-complete.md` § LINKS).

---

## Updating the Lore History Buffer

`lore-history.md` keeps the last 40,000 characters (~14 days). To manually trim it:

```python
with open("lore-history.md") as f:
    content = f.read()
content = content[-40000:]
with open("lore-history.md", "w") as f:
    f.write(content)
```

---

## Resetting bot-state.json

If Telegram updates are being replayed, reset the offset:

```bash
echo '{"last_update_id": 0}' > bot-state.json
```

---

## Checking Analytics Reports

Reports are stored in `reports/analytics-report-YYYY-MM-DD.json`.

```bash
ls -lt reports/ | head -5
cat reports/analytics-report-$(date +%Y-%m-%d).json | python -m json.tool
```

---

## Environment Variables Quick Reference

| Variable | Required by | Notes |
|---|---|---|
| `ANTHROPIC_API_KEY` | Brain 3 | Claude text generation |
| `GROK_API_KEY` | Brain 3 | Image generation (required — fast-fail DB-10) |
| `TELEGRAM_BOT_TOKEN` | Brain 3 | Required — fast-fail DB-10 |
| `CHANNEL_CHAT_IDS` | Brain 3 | Comma-separated chat IDs |
| `MESSAGE_THREAD_ID` | Brain 3 | Optional topic thread ID |
| `FANDOM_BOT_USER` | Brain 4 | Fandom bot username |
| `FANDOM_BOT_PASSWORD` | Brain 4 | Fandom bot password |
| `FANDOM_WIKI_URL` | Brain 4 | Base URL, no trailing slash |
| `GROK_TEXT_MODEL` | Brain 3 | Override Grok model (default: `grok-3-latest`) |
