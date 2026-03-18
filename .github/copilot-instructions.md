# GK BRAIN — Copilot Agent Instructions

Follow every rule and protocol defined in `copilot-rule.md` at the repository root.
The information below supplements that file and is specific to this repository.

---

## What This Repo Is

**GK BRAIN** is an autonomous AI agent system for the **Crypto Moonboys / GKniftyHEADS NFT universe**.
It runs on GitHub Actions every 2 hours and does two things:

1. **Lore publishing** — generates two consecutive first-person narrative posts in the voice of GK (UK graffiti artist / DJ / parkour runner / carp fisherman / web3 entrepreneur) and posts them to Telegram channels.
2. **Wiki updates** — pushes real-world canon updates to the [GKniftyHEADS Fandom wiki](https://gkniftyheads.fandom.com) via the MediaWiki API.

The system is entirely self-hosted on GitHub Actions (no external servers). It costs nothing to host beyond API call costs.

---

## 4-Brain Pipeline

The workflow runs the four brains in sequence every 2 hours (cron `0 */2 * * *`), then `master-backup-agent.py` last.

```
1. crawl-brain.py          → Brain 1 — web crawl (HTTP only, no LLM)
         ↓ writes crawl-results.json
2. analytics-brain.py      → Brain 2 — analytics & recommendations (rule-based)
         ↓ writes recommendations.json + reports/analytics-report-YYYY-MM-DD.json
3. gk-brain.py             → Brain 3 — lore generation + Telegram posts + wiki queue
         ↓ writes wiki-update-queue.json, lore-history.md, bot-state.json …
4. wiki-brain.py           → Brain 4 — Fandom wiki push (MediaWiki API)
         ↓
5. master-backup-agent.py  → SHA-256 snapshots, rule-conflict checks
```

Workflow file: `.github/workflows/gk-brain.yml`
All 4 brain steps and master-backup use `continue-on-error: true`.
If any brain fails, a Telegram alert is sent via the `Notify failure` step.

---

## Key Rule Files — NEVER Modify Logic Without Explicit Instruction

| File | Contents | Locked Rules |
|---|---|---|
| `brain-rules.md` | Dual-Brain Architecture rules | DB-1 through DB-18 |
| `gk-brain-complete.md` | Master brain config loaded by `gk-brain.py` via `BRAIN_RULES_FILE` | MB-1 through MB-5 |
| `TELEGRAM-BOT-API-RULES.md` | Official Telegram rate-limit & error-handling rules | All sections |
| `OFFICIAL-SOURCE-AUTHORITY-RULES.md` | Source priority & canon authority hierarchy | All sections |

Do **NOT** change logic in these files without being explicitly told to by the repo owner.

---

## Coding Conventions

- **Optional module loading**: All Python files use the `_safe_load()` pattern for optional imports (e.g. `learning-feedback-loop.py`).
- **Standard imports**: Always add `import requests`, `import os`, `import sys` at the top of any file that uses them.
- **Exception handling**: Never use bare `except:` — always catch specific exceptions (e.g. `except requests.RequestException`, `except json.JSONDecodeError`).
- **Atomic state writes**: All state files must be written atomically — write to a `.tmp` file first, then `os.replace(tmp_path, final_path)`.
- **Workflow steps**: All brain steps in `gk-brain.yml` must have `continue-on-error: true`.
- **Python version**: 3.12 (as set by the workflow).

---

## Secrets

| Secret | Used By |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Brain 3 (`gk-brain.py`) |
| `GROK_API_KEY` | Brain 3 — image generation via xAI |
| `ANTHROPIC_API_KEY` | Brain 3 — primary lore text via Claude 3.5 Sonnet |
| `CHANNEL_CHAT_IDS` | Brain 3 — comma-separated Telegram chat IDs to post to |
| `MESSAGE_THREAD_ID` | Brain 3 — optional Telegram topic thread ID |
| `OPENAI_API_KEY` | Optional fallback |
| `GROK_TEXT_MODEL` | Brain 3 — Grok model override (default: `grok-3-latest`) |
| `FANDOM_BOT_USER` | Brain 4 (`wiki-brain.py`) |
| `FANDOM_BOT_PASSWORD` | Brain 4 |
| `FANDOM_WIKI_URL` | Brain 4 — base URL (no trailing slash); code appends `/api.php` |

---

## State Files (Committed Back to `main` After Every Run)

| File | What It Tracks |
|---|---|
| `lore-history.md` | Rolling ~14-day buffer of all lore posts (last 40,000 chars) |
| `bot-state.json` | Last processed Telegram `update_id` (prevents replay) |
| `reply-tracker.json` | Per-user reply count + date + failed keyword attempts |
| `crawl-snapshot.json` | Snapshot of last crawl state |
| `crawl-results.json` | Latest web crawl discoveries |
| `crawl-fingerprints.json` | MD5 dedup fingerprints for crawl results |
| `wiki-update-queue.json` | Pending Fandom wiki updates queued by Brain 3 |
| `master-backup-state.json` | SHA-256 manifest from last master-backup run |
| `brain1-canon.json` | Canon signals from crawl brain for lore injection |
| `engagement-tracker.json` | Per-post Telegram engagement data |
| `recommendations.json` | Analytics brain output for Brain 3 |

---

## Telegram Rules (from `TELEGRAM-BOT-API-RULES.md`)

- **30 msg/s** global limit across all chats combined.
- **1 msg/s** per individual chat — never send 2 messages to the same chat in under 1 second.
- Always call `time.sleep(2)` between Message 1 and Message 2 in the same chat (DB-12).
- On `429 Too Many Requests`: honour the `retry_after` field exactly, then retry once.
- On `400 Bad Request` or `403 Forbidden`: log and skip — never retry without a code fix.
- Text messages: max **4,096** UTF-8 characters. Captions: max **1,024** characters.
- `bot-state.json` must store the last processed `update_id` — read at start, write at end of every reply cycle.
- Never run `getUpdates` and a webhook simultaneously (causes `409 Conflict`).

---

## Fandom Wiki Integration

- **Target wiki**: `https://gkniftyheads.fandom.com`
- **Auth module**: `fandom_auth.py` — uses MediaWiki `clientlogin` API (bot credentials via `FANDOM_BOT_USER` / `FANDOM_BOT_PASSWORD`).
- **Queue file**: `wiki-update-queue.json` — written by Brain 3, consumed by Brain 4.
- **Health check**: `wiki-brain.py` runs `wiki_brain_health_check()` before any write. If login fails it skips all writes for that cycle (no retry in same run) — see DB-7.
- **API base**: `FANDOM_WIKI_URL` + `/api.php` (e.g. `https://gkniftyheads.fandom.com/api.php`).
- Brain 3 lore posts must **never** go into the wiki queue (DB-1). Only real-world facts from crawl/analytics brains belong there.

---

## Stub Files (Do Not Add Logic Unless Explicitly Asked)

The following files exist but are intentionally empty stubs. Do not add implementation logic to them without an explicit instruction:

- `learning-feedback-loop.py`
- `reinforcement-learning-optimizer.py`
- `deduplication-engine.py`
- `source-attribution-system.py`

`analytics-brain.py` loads these via `_safe_load()` and gracefully continues if they are missing or empty — this is expected behaviour, not a bug.

---

## Canon / Lore Files — Read-Only for Agents

Never modify these files. They are source-of-truth canon documents:

- `MASTER-CHARACTER-CANON.md` — complete character index, all 40 factions, full timeline
- `genesis-lore.md` — Block Topia genesis seed narrative (~3,700 words)
- `character-bible.md` — character consistency rules, art layers, image prompt templates

---

## Reports

Analytics reports are saved to the `reports/` folder as:
`reports/analytics-report-YYYY-MM-DD.json`

---

## Brain Rule Summary (DB-1 — DB-14)

| Rule | One-liner |
|---|---|
| DB-1 | Wiki separation — Brain 3 lore posts MUST NOT be queued to the wiki. |
| DB-2 | Brain 1 canon signals may influence at most 20% of any lore post. |
| DB-3 | Brain 1 signals older than 7 days are stale and ignored by the lore generator. |
| DB-4 | Signal lifecycle: unread → used (only after confirmed Telegram post). |
| DB-5 | Post 2 always has an image; prompt must reference a scene from Post 2 text. |
| DB-6 | The 4 brains communicate ONLY via the inter-brain JSON files. No cross-imports. |
| DB-7 | Wiki Brain must run health check before any write; skip all writes if login fails. |
| DB-8 | Crawl Brain must MD5-fingerprint all results to deduplicate before writing. |
| DB-9 | lore-history.md retains last 40,000 characters; older content is trimmed. |
| DB-10 | `gk-brain.py` must raise `EnvironmentError` at start of `main()` if `GROK_API_KEY` or `TELEGRAM_BOT_TOKEN` are missing. |
| DB-11 | When `ANTHROPIC_API_KEY` is set, all lore text goes to Claude 3.5 Sonnet; Grok is fallback. Image gen always uses Grok. |
| DB-12 | `time.sleep(2)` MUST be called between Message 1 and Message 2 in every posting loop. |
| DB-13 | Images MUST NEVER be written to disk. Generated in memory, streamed to Telegram, then discarded. |
| DB-14 | After Message 2, call `pinChatMessage` with `disable_notification=True`. Pin failure must NOT block the loop. |

---

## LLM Routing

| Task | Primary | Fallback |
|---|---|---|
| Lore text generation | Claude 3.5 Sonnet (`ANTHROPIC_API_KEY`) | Grok (`GROK_API_KEY`) |
| Image generation | Grok (`GROK_API_KEY`) | None |

`gk-brain.py` loads rules from `gk-brain-complete.md` via the `BRAIN_RULES_FILE` constant (not `brain-rules.md`).

---

## Common Errors & Fixes

| Error | Fix |
|---|---|
| `ModuleNotFoundError: requests` | Add `import requests` at the top; ensure `requests` is in `requirements.txt`. |
| `learning-feedback-loop.py: No such file or directory` | Normal — analytics-brain uses `_safe_load()` and skips missing stub files. |
| Telegram `429` | Sleep `retry_after` seconds, retry once. |
| Telegram `400`/`403` | Log and skip — do not retry without a code fix. |
| Wiki login fails | `wiki-brain.py` skips all writes for this cycle. Check `FANDOM_BOT_USER` / `FANDOM_BOT_PASSWORD` secrets. |
| `EnvironmentError` on `gk-brain.py` start | `GROK_API_KEY` or `TELEGRAM_BOT_TOKEN` secret is missing or empty. |

