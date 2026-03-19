# AGENT EXPLAINER — GK BRAIN System Overview

GK BRAIN is an **autonomous AI agent system** for the Crypto Moonboys / GKniftyHEADS NFT
universe. It runs entirely inside GitHub Actions — no server required. Every 2 hours it
crawls official sources, generates lore, posts to Telegram, and updates the Fandom wiki.

---

## The 4+1 Brain Architecture

| Brain | File | What it does |
|---|---|---|
| **Brain 1 — Crawl** | `crawl-brain.py` | HTTP-only web crawl; writes `crawl-results.json` |
| **Brain 2 — Analytics** | `analytics-brain.py` | Rule-based scoring; writes `recommendations.json` |
| **Brain 3 — Lore** | `gk-brain.py` | Generates lore via Claude / Grok, posts to Telegram, queues wiki updates |
| **Brain 4 — Wiki** | `wiki-brain.py` | Pushes queued updates to Fandom wiki via MediaWiki API |
| **Brain 5 — Backup** | `master-backup-agent.py` | SHA-256 fingerprints all tracked files, conflict-checks locked rules |

Brains communicate exclusively through JSON state files — no cross-imports between brain modules (DB-6).

---

## Key Rules at a Glance

- **DB-1** — Telegram lore posts are NEVER queued to the wiki.
- **DB-10** — `gk-brain.py` raises `EnvironmentError` if `GROK_API_KEY` or `TELEGRAM_BOT_TOKEN` are missing.
- **DB-11** — Claude 3.5 Sonnet for text; Grok for image generation (always).
- **DB-12** — `time.sleep(2)` between every Message 1 and Message 2 in the same chat.
- **DB-13** — Images are NEVER written to disk; streamed to Telegram then discarded.
- **DB-14** — `pinChatMessage` with `disable_notification=True` after Message 2.

Full rule set: `brain-rules.md` (DB-1 to DB-19) and `gk-brain-complete.md` (MB-1 to MB-5).

---

## Secrets Required

| Secret | Used by |
|---|---|
| `ANTHROPIC_API_KEY` | Brain 3 — Claude text generation |
| `GROK_API_KEY` | Brain 3 — image generation |
| `TELEGRAM_BOT_TOKEN` | Brain 3 — posting |
| `CHANNEL_CHAT_IDS` | Brain 3 — comma-separated chat IDs |
| `MESSAGE_THREAD_ID` | Brain 3 — optional topic thread |
| `FANDOM_BOT_USER` | Brain 4 — wiki login |
| `FANDOM_BOT_PASSWORD` | Brain 4 — wiki login |
| `FANDOM_WIKI_URL` | Brain 4 — base URL (no trailing slash) |

---

## State Files Committed After Every Run

`lore-history.md`, `bot-state.json`, `crawl-results.json`, `crawl-fingerprints.json`,
`wiki-update-queue.json`, `recommendations.json`, `engagement-tracker.json`,
`master-backup-state.json`, and daily analytics reports under `reports/`.

---

## Where to Go Next

| Goal | File |
|---|---|
| Understand the full architecture | `BRAIN-COORDINATOR.md` |
| Locked lore & wiki rules | `brain-rules.md` |
| Telegram compliance | `TELEGRAM-BOT-API-RULES.md` |
| Wiki integration guide | `FANDOM-WIKI-INTEGRATION-GUIDE.md` |
| Run the system manually | `HOW-TO.md` |
