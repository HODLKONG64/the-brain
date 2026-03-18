# BRAIN-COORDINATOR.md — 4-Brain Architecture

## Overview

GK BRAIN runs as four independent Python brains executed in sequence every 2 hours by the GitHub Actions workflow.

```
┌─────────────────┐
│  crawl-brain.py │  ← Brain 1: Web crawl + dedup fingerprinting
└────────┬────────┘
         │ crawl-results.json
         ▼
┌──────────────────────┐
│  analytics-brain.py  │  ← Brain 2: Engagement analysis + recommendations
└────────┬─────────────┘
         │ recommendations.json, reports/analytics-report-YYYY-MM-DD.json
         ▼
┌─────────────┐
│  gk-brain.py│  ← Brain 3: Lore generation + Telegram posting
└──────┬──────┘
       │ brain1-canon.json (signal), wiki-update-queue.json
       ▼
┌──────────────┐
│  wiki-brain.py│  ← Brain 4: Wiki update (Fandom smart-merge)
└──────────────┘
```

---

## Run Order

| Step | Script | Purpose |
|------|--------|---------|
| 1 | `crawl-brain.py` | Crawl all official GK URLs; write new/changed pages to `crawl-results.json` |
| 2 | `analytics-brain.py` | Analyse `engagement-tracker.json`; write `recommendations.json` + daily report |
| 3 | `gk-brain.py` | Read Brain1 signal, generate lore, post to Telegram |
| 4 | `wiki-brain.py` | Process `wiki-update-queue.json` and push to Fandom wiki |

All brains run with `continue-on-error: true` in the workflow except `gk-brain.py` (the core brain that must succeed).

---

## Inter-Brain JSON Communication

| File | Written by | Read by | Purpose |
|------|-----------|---------|---------|
| `crawl-results.json` | crawl-brain | gk-brain (optional) | Raw crawl discoveries |
| `recommendations.json` | analytics-brain | gk-brain (optional) | Content recommendations |
| `brain1-canon.json` | gk-brain / crawl-brain | gk-brain | Creative signal: 20%-influence narrative seeds |
| `wiki-update-queue.json` | gk-brain | wiki-brain | Pending wiki entries to push |
| `engagement-tracker.json` | gk-brain | analytics-brain | Post engagement metrics |
| `lore-history.md` | gk-brain | gk-brain | 14-day lore continuity buffer |

---

## Secrets Map

| Secret | Used by | Purpose |
|--------|---------|---------|
| `GROK_API_KEY` | gk-brain | Grok text + image generation |
| `GROK_TEXT_MODEL` | gk-brain | Grok model override (default: `grok-3-latest`) |
| `ANTHROPIC_API_KEY` | gk-brain | Claude 3.5 Sonnet fallback for text generation |
| `TELEGRAM_BOT_TOKEN` | gk-brain | Telegram Bot API |
| `CHANNEL_CHAT_IDS` | gk-brain | Comma-separated Telegram channel IDs |
| `MESSAGE_THREAD_ID` | gk-brain | Telegram topic/thread ID (optional) |
| `FANDOM_BOT_USER` | wiki-brain, gk-brain | Fandom bot username |
| `FANDOM_BOT_PASSWORD` | wiki-brain, gk-brain | Fandom bot password |
| `FANDOM_WIKI_URL` | wiki-brain, gk-brain | Wiki base URL |

---

## Cron Schedule

Runs every 2 hours at :00 UTC:

```yaml
schedule:
  - cron: '0 */2 * * *'
```

---

## Brain1 Signal Protocol

`brain1-canon.json` structure:

```json
{
  "updates": [
    {
      "title": "string",
      "content": "string",
      "timestamp": "ISO-8601",
      "b2_used": false
    }
  ],
  "character_facts": {},
  "web_discoveries": []
}
```

- `gk-brain.py` reads the `updates` array and filters to items where `b2_used == false`
- Up to 3 unused signals are injected into lore generation as a ~20% creative influence
- After a successful Telegram post, all used signals are marked `b2_used: true`
- Signals older than 7 days are ignored (staleness guard in `load_brain1_signal()`)
