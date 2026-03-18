# GK BRAIN — System Documentation

---

## 1. What is GK BRAIN

**GK BRAIN** is a fully autonomous AI agent system for the **Crypto Moonboys / GKniftyHEADS NFT universe**. It wakes up every 2 hours via GitHub Actions, generates two consecutive lore posts in the first-person voice of GK (a UK graffiti artist, DJ, parkour runner, carp fisherman, and web3 entrepreneur), posts them to Telegram channels, and pushes real-world canon updates to the [GKniftyHEADS Fandom wiki](https://gkniftyheads.fandom.com). It is entirely self-hosted on GitHub Actions with no external servers — once deployed it runs forever with zero human input.

---

## 2. System Architecture

### 4-Brain Pipeline

```
Every 2 hours (cron: '0 */2 * * *')
──────────────────────────────────────────────────────────────────
 Brain 1  crawl-brain.py          Web crawl & content detection
              │ writes: crawl-results.json, crawl-fingerprints.json
              ▼
 Brain 2  analytics-brain.py      Analytics & recommendations
              │ writes: recommendations.json
              │         reports/analytics-report-YYYY-MM-DD.json
              ▼
 Brain 3  gk-brain.py             Lore generation + Telegram posts
              │ reads:  crawl-results.json, recommendations.json
              │ writes: wiki-update-queue.json, lore-history.md,
              │         bot-state.json, reply-tracker.json,
              │         brain1-canon.json, engagement-tracker.json
              ▼
 Brain 4  wiki-brain.py           Fandom wiki push
              │ reads:  wiki-update-queue.json
              │ pushes: gkniftyheads.fandom.com via MediaWiki API
              ▼
         master-backup-agent.py   SHA-256 snapshots + rule-conflict check
──────────────────────────────────────────────────────────────────
 Then: commit all state files back to main  [skip ci]
       upload execution report artifact (14 day retention)
       Telegram failure alert if any brain failed
```

### Workflow Schedule

| Field | Value |
|---|---|
| File | `.github/workflows/gk-brain.yml` |
| Cron | `0 */2 * * *` (every 2 hours on the hour) |
| Manual trigger | `workflow_dispatch` |
| Max runtime | 35 minutes |
| All brain steps | `continue-on-error: true` |

---

## 3. Quick Start

### Required Secrets (GitHub → Settings → Secrets → Actions)

| Secret | Purpose |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Bot token from BotFather |
| `GROK_API_KEY` | xAI API key (image generation + text fallback) |
| `ANTHROPIC_API_KEY` | Claude 3.5 Sonnet key (primary text generation) |
| `CHANNEL_CHAT_IDS` | Comma-separated Telegram chat IDs to post to |
| `MESSAGE_THREAD_ID` | Optional: Telegram topic thread ID |
| `FANDOM_BOT_USER` | Fandom bot account username |
| `FANDOM_BOT_PASSWORD` | Fandom bot account password |
| `FANDOM_WIKI_URL` | Wiki base URL, no trailing slash (e.g. `https://gkniftyheads.fandom.com`) |
| `OPENAI_API_KEY` | Optional fallback |
| `GROK_TEXT_MODEL` | Optional: Grok model override (default: `grok-3-latest`) |

### How to Trigger Manually

1. Go to **Actions → GK BRAIN - 4 Brain System (2 Hour Cycle)**
2. Click **Run workflow → Run workflow**
3. Watch the 5 brain steps complete in ~30–45 minutes
4. Posts appear in your Telegram channel within the first few minutes

### LLM Routing

| Task | Primary | Fallback |
|---|---|---|
| Lore text generation | Claude 3.5 Sonnet (`ANTHROPIC_API_KEY`) | Grok (`GROK_API_KEY`) |
| Image generation | Grok (`GROK_API_KEY`) | None |

---

## 4. File Map

### Python Scripts

| File | Role |
|---|---|
| `crawl-brain.py` | Brain 1 — HTTP crawls all URLs in `gkandcryptomoonboywebsitestosave.md`; MD5 deduplicates results |
| `analytics-brain.py` | Brain 2 — Analyses post engagement, writes `recommendations.json` and analytics reports |
| `gk-brain.py` | Brain 3 — Core lore engine: loads rules, generates lore, posts to Telegram, queues wiki updates |
| `wiki-brain.py` | Brain 4 — Reads `wiki-update-queue.json`, authenticates with Fandom, pushes MediaWiki edits |
| `master-backup-agent.py` | Final step — SHA-256 manifest of all files, rule-conflict detection |
| `fandom_auth.py` | Fandom MediaWiki `clientlogin` auth helper (used by wiki-brain.py) |
| `update-detector.py` | Detects new content from crawled URLs using `URLS_BY_CATEGORY` |
| `execution-reporter.py` | Generates `execution-report-YYYY-MM-DD-HHMMSS.json` after lore runs |
| `data-validator.py` | Validates JSON state files |
| `wiki-smart-merger.py` | Merges incoming wiki content with existing pages |
| `wiki-cross-checker.py` | Cross-checks wiki content for consistency |
| `wiki-updater.py` | Low-level MediaWiki page writer |
| `wiki-formatter.py` | Formats lore content into MediaWiki markup |
| `wiki-page-builder.py` | Assembles full wiki pages from sections |
| `wiki-citation-checker.py` | Validates source citations on wiki pages |
| `dialogue-generator.py` | Generates character dialogue for lore posts |
| `sentiment-analyzer.py` | Analyses sentiment of lore posts |
| `web-lore-agent.py` | Fetches and processes web lore sources |
| `gk-brain-recovery.py` | Recovery/debug runner for Brain 3 |
| `performance-metrics-system.py` | Tracks performance metrics |
| `predictive-trend-engine.py` | Predicts trending topics for lore injection |
| `quality-gate.py` | QA gate before Telegram posting |
| `debug-report-generator.py` | Generates debug reports on failures |
| `system-health-monitor.py` | System-wide health checks |
| `user-profile.py` | Manages Telegram user profiles for reply system |
| `update-priority-queue.py` | Priority queue for content updates |

### Stub Files (Empty — Do Not Add Logic Without Explicit Instruction)

| File | Status |
|---|---|
| `learning-feedback-loop.py` | Stub — loaded via `_safe_load()`, missing is expected |
| `reinforcement-learning-optimizer.py` | Stub — same |
| `deduplication-engine.py` | Stub — same |
| `source-attribution-system.py` | Stub — same |

### Key Markdown Rule / Canon Files (Do Not Modify Logic Without Explicit Instruction)

| File | Contents |
|---|---|
| `brain-rules.md` | DB-1 through DB-18 locked dual-brain architecture rules |
| `gk-brain-complete.md` | MB-1 through MB-5 master brain config (loaded by `gk-brain.py`) |
| `TELEGRAM-BOT-API-RULES.md` | Official Telegram rate-limit and error-handling rules |
| `OFFICIAL-SOURCE-AUTHORITY-RULES.md` | Source priority and canon authority hierarchy |
| `MASTER-CHARACTER-CANON.md` | ⛔ READ-ONLY — complete character index, 40 factions, full timeline |
| `genesis-lore.md` | ⛔ READ-ONLY — Block Topia genesis seed narrative (~3,700 words) |
| `character-bible.md` | ⛔ READ-ONLY — character consistency, art layers, image prompt templates |
| `WEBLORERULES.md` | Web lore extraction rules |
| `wiki-merge-rules.md` | Wiki merge rules |
| `wiki-image-rules.md` | Wiki image rules |
| `update-integration-rules.md` | Rules for integrating content updates |
| `copilot-rule.md` | Root-level Copilot agent rules |
| `FANDOM-API-RULES.md` | Fandom API rules |
| `FANDOM-OAUTH-TECHNICAL-BREAKDOWN.md` | OAuth technical details for Fandom |
| `gkandcryptomoonboywebsitestosave.md` | All URLs crawled by Brain 1 |
| `lore-planner.md` | 7-day repeating calendar with 2-hour UTC slot breakdown |

### State JSON Files (Committed Back to `main` Every Run)

| File | What It Tracks |
|---|---|
| `lore-history.md` | Rolling ~14-day buffer of all lore posts (last 40,000 characters) |
| `bot-state.json` | Last processed Telegram `update_id` (prevents update replay) |
| `reply-tracker.json` | Per-user reply count, date, failed keyword attempts |
| `crawl-snapshot.json` | Snapshot of last crawl state |
| `crawl-results.json` | Latest web crawl discoveries from Brain 1 |
| `crawl-fingerprints.json` | MD5 dedup fingerprints for crawl results |
| `wiki-update-queue.json` | Pending Fandom wiki updates queued by Brain 3 |
| `master-backup-state.json` | SHA-256 manifest from last master-backup run |
| `brain1-canon.json` | Canon signals from crawl brain (max 20% lore influence per DB-2) |
| `engagement-tracker.json` | Per-post Telegram engagement data |
| `recommendations.json` | Analytics brain output for Brain 3 |

### Reports Folder

`reports/analytics-report-YYYY-MM-DD.json` — daily analytics reports from Brain 2.

---

## 5. Brain Rules Summary (DB-1 — DB-14)

| Rule | Summary |
|---|---|
| **DB-1** | Wiki separation — Brain 3 lore posts must NOT be queued to the wiki. Only real-world crawl/analytics facts belong there. |
| **DB-2** | Brain 1 canon signals may influence at most **20%** of any lore post. The other 80% comes from calendar rules, character continuity, and time block. |
| **DB-3** | Brain 1 signals older than 7 days are stale and must be ignored by the lore generator (but not deleted — kept for archival). |
| **DB-4** | Signal lifecycle: `unread` → `used` (only after a confirmed successful Telegram post). |
| **DB-5** | Post 2 is always sent with an image. The image prompt must reference a concrete scene from the Post 2 lore text — not a generic fallback. |
| **DB-6** | The 4 brains communicate **only** via inter-brain JSON files. No brain may import functions from another brain's primary module. |
| **DB-7** | Wiki Brain must run `wiki_brain_health_check()` before any write. If credentials fail, all writes for that cycle are skipped — no retry in same run. |
| **DB-8** | Crawl Brain must MD5-fingerprint all results (title + snippet) to deduplicate before writing to `crawl-results.json`. |
| **DB-9** | `lore-history.md` retains the last **40,000 characters** (~14 days). Older content is trimmed automatically by `save_lore_history()`. |
| **DB-10** | `gk-brain.py` must raise `EnvironmentError` at the start of `main()` if `GROK_API_KEY` or `TELEGRAM_BOT_TOKEN` are not set. |
| **DB-11** | When `ANTHROPIC_API_KEY` is set, all lore text routes through Claude 3.5 Sonnet. Grok is fallback for text. Image generation always uses Grok. |
| **DB-12** | `time.sleep(2)` MUST be called between Message 1 and Message 2 in every Telegram posting loop. |
| **DB-13** | Generated images must NEVER be written to disk. They are produced in memory, streamed to Telegram via multipart upload, then discarded. |
| **DB-14** | After Message 2, call `pinChatMessage` with `disable_notification=True`. Pin failure must NOT block or interrupt the posting loop. |

---

## 6. Telegram Integration

### Rate Limits (from `TELEGRAM-BOT-API-RULES.md`)

| Limit | Value |
|---|---|
| Global rate | 30 messages/second across all chats |
| Per-chat rate | 1 message/second |
| Between Msg 1 and Msg 2 (same chat) | `time.sleep(2)` — mandatory (DB-12) |

### Message Size Limits

| Type | Limit |
|---|---|
| Text message (`sendMessage`) | 4,096 UTF-8 characters |
| Caption (photo/video) | 1,024 UTF-8 characters |

### Error Handling

| Code | Action |
|---|---|
| `400 Bad Request` | Log and skip — **never retry without a code fix** |
| `401 Unauthorized` | Raise `EnvironmentError`; halt the run |
| `403 Forbidden` | Log chat_id; skip that chat for this run |
| `409 Conflict` | Only one `getUpdates` poller allowed at a time |
| `429 Too Many Requests` | Sleep `retry_after` seconds exactly; retry once |
| `5xx` | Exponential backoff; max 3 retries |

### Key Rules

- `bot-state.json` stores the last processed `update_id` — must be read at start and written at end of every reply cycle.
- Never run `getUpdates` and a webhook simultaneously.
- All slash commands bypass the keyword trigger gate and do NOT count against the 20/day reply limit.
- Max 20 replies per user per 24h (non-slash-command replies).

---

## 7. Fandom Wiki Integration

### Auth Method

`fandom_auth.py` uses the MediaWiki `clientlogin` API with `FANDOM_BOT_USER` and `FANDOM_BOT_PASSWORD`.
Wiki base URL is `FANDOM_WIKI_URL`; API endpoint is `FANDOM_WIKI_URL + '/api.php'`.

### Queue System

1. Brain 3 (`gk-brain.py`) detects real-world canon updates from `crawl-results.json`.
2. It appends them to `wiki-update-queue.json` (never Telegram lore posts — DB-1).
3. Brain 4 (`wiki-brain.py`) reads the queue, authenticates, and pushes MediaWiki edits.
4. After successful push, the queue entries are marked consumed.

### Key Files

| File | Purpose |
|---|---|
| `fandom_auth.py` | Auth helper |
| `wiki-brain.py` | Queue consumer + MediaWiki writer |
| `wiki-update-queue.json` | Pending edits |
| `wiki-smart-merger.py` | Merges new content with existing wiki pages |
| `FANDOM-API-RULES.md` | Official API rules |
| `wiki-merge-rules.md` | Merge strategy rules |

---

## 8. State Files

| File | What It Tracks | Brain |
|---|---|---|
| `lore-history.md` | Last 40,000 chars of lore posts for continuity | Brain 3 |
| `bot-state.json` | Last Telegram `update_id` to prevent replay | Brain 3 |
| `reply-tracker.json` | Per-user reply limits (count, date, failed attempts) | Brain 3 |
| `crawl-snapshot.json` | Last crawl state snapshot | Brain 1 |
| `crawl-results.json` | Latest crawl discoveries | Brain 1 |
| `crawl-fingerprints.json` | MD5 dedup fingerprints | Brain 1 |
| `wiki-update-queue.json` | Pending wiki edits | Brain 3 / Brain 4 |
| `master-backup-state.json` | SHA-256 file manifest | master-backup |
| `brain1-canon.json` | Canon signals with `b2_used` lifecycle flag | Brain 1 / Brain 3 |
| `engagement-tracker.json` | Per-post engagement data | Brain 3 |
| `recommendations.json` | Analytics recommendations | Brain 2 |

All state files are committed back to `main` after every run with `[skip ci]` to avoid re-triggering the workflow.

---

## 9. Adding New Rules

To add a new DB-N rule to `brain-rules.md`:

1. Open `brain-rules.md`.
2. Find the `## DUAL BRAIN ARCHITECTURE RULES (DB-1 — DB-N)` section.
3. Add a new `### DB-N+1 — Short Title` subsection following the same format as existing rules.
4. Update the section header number range (e.g. `DB-1 — DB-15`).
5. If the rule affects code behaviour in `gk-brain.py`, `crawl-brain.py`, `analytics-brain.py`, or `wiki-brain.py`, implement the corresponding code change immediately.
6. Update the Brain Rules Summary table in this README.

---

## 10. Troubleshooting

### `requests` import error in brain scripts

**Symptom:** `ModuleNotFoundError: No module named 'requests'` at runtime.

**Fix:** Ensure `import requests` is at the top of the file AND `requests` is in `requirements.txt`. The `requests` package must be an explicit top-level import — do not rely on transitive imports from other libraries.

### Missing stub files (`learning-feedback-loop.py`, etc.)

**Symptom:** `[analytics-brain] Could not load learning-feedback-loop.py: No such file or directory`

**Status:** This is **expected behaviour**. These are intentional stubs. `analytics-brain.py` uses `_safe_load()` and continues without them. Do not create these files with logic unless explicitly instructed.

### Telegram `429 Too Many Requests`

**Fix:** Read the `retry_after` value from the error response. Sleep exactly that many seconds. Retry once. Never retry before sleeping.

### Telegram `400` or `403`

**Fix:** Do not retry. Log the error and skip that message/chat. A `400` means a malformed request (fix the code); a `403` means the bot was blocked or kicked from that chat.

### Wiki login fails

**Symptom:** Brain 4 skips all wiki writes; `wiki_brain_health_check()` fails.

**Fix:** Verify `FANDOM_BOT_USER` and `FANDOM_BOT_PASSWORD` secrets are set correctly. Check that the Fandom bot account has not been locked. Brain 4 will retry on the next scheduled run automatically.

### `EnvironmentError` at start of `gk-brain.py`

**Symptom:** `EnvironmentError: GROK_API_KEY is required` or similar.

**Fix:** Ensure `GROK_API_KEY` and `TELEGRAM_BOT_TOKEN` are both set as GitHub Actions secrets with non-empty values. This is an intentional fast-fail (DB-10).

### Workflow runs but produces no Telegram posts

**Check:**
1. Is `TELEGRAM_BOT_TOKEN` set?
2. Is `CHANNEL_CHAT_IDS` set (comma-separated, no spaces)?
3. Has the bot been added as admin to each target chat?
4. Check the `🧠 Run Lore Brain` step logs in GitHub Actions.

### Analytics report file missing

**Symptom:** `reports/analytics-report-YYYY-MM-DD.json` not found.

**Fix:** Brain 2 writes this file. If Brain 1 (crawl) fails, Brain 2 still runs due to `continue-on-error: true`. Check the `📊 Run Analytics Brain` step logs.

---

## 11. Official Links — External Canon Sources

The agent checks these sources every 2 hours. They are the official sources of truth for all lore updates.

| Source | URL |
|---|---|
| Substack (primary canon) | https://substack.com/@graffpunks/posts |
| GraffPunks Live | https://graffpunks.live/ |
| GKniftyHEADS Website | https://gkniftyheads.com/ |
| GKniftyHEADS Wiki | https://gkniftyheads.fandom.com/ |
| Graffiti Kings | https://graffitikings.co.uk/ |
| YouTube | https://www.youtube.com/@GKniftyHEADS |
| Medium | https://medium.com/@GKniftyHEADS |
| X/Twitter | https://x.com/GraffPunks |

---

## 12. Archived Docs

The following individual documentation files have been consolidated into this README. They have been replaced with redirect notes:

- `READMENOWBOT.md` → see README.md
- `HOW-TO.md` → see README.md (Section 3: Quick Start + Section 7: Fandom Wiki Integration)
- `EXECUTION-SUMMARY.md` → see README.md
- `BRAIN-COORDINATOR.md` → see README.md (Section 2: System Architecture)
- `FANDOM-REFERENCE-CARD.md` → see README.md (Section 7: Fandom Wiki Integration)
- `FANDOM-QUICK-DEBUG-GUIDE.md` → see README.md (Section 10: Troubleshooting)
- `GK-WIKI-COMPLETE-ANALYSIS.md` → see README.md
- `GK-WIKI-URL-API-DIAGNOSTICS.md` → see README.md
- `cross-platform-consistency.md` → see README.md
- `AGENT-EXPLAINER.md` → consolidated into README.md
- `LLM-ORCHESTRATION-ARCHITECTURE.md` → consolidated into README.md (Section 3: Quick Start, LLM Routing)
- `FANDOM-WIKI-INTEGRATION-GUIDE.md` → consolidated into README.md (Section 7)
- `TELEGRAM-NARRATOR-SYSTEM-ARCHITECTURE.md` → consolidated into README.md (Section 6)
- `LORE-RULE-DETECTOR-DEEP-LOGIC.md` → consolidated into README.md (Section 5: Brain Rules)

**Active rule files kept untouched:** `brain-rules.md`, `gk-brain-complete.md`, `TELEGRAM-BOT-API-RULES.md`, `OFFICIAL-SOURCE-AUTHORITY-RULES.md`, `MASTER-CHARACTER-CANON.md`, `genesis-lore.md`, `character-bible.md`, `WEBLORERULES.md`, `wiki-merge-rules.md`, `wiki-image-rules.md`, `update-integration-rules.md`, `copilot-rule.md`, `FANDOM-API-RULES.md`, `FANDOM-OAUTH-TECHNICAL-BREAKDOWN.md`

---

*Last updated: 2026-03-18. GK BRAIN is fully operational and self-updating.*
