# brain-rules.md — GK BRAIN Core Rules (DB-37 Lean: 12 Rules Only)

> Prompt-safe subset. Full rules DB-13 through DB-36 + lore canon live in PROJECT-DNA.md.
> BRAIN_RULES_FILE in gk-brain.py points to gk-brain-complete.md for the full config.

---

## DB-1 — Wiki Separation
Brain 3 (gk-brain.py) MUST NOT queue its own Telegram lore posts to the wiki queue. Only real-world updates detected by crawl-brain or analytics-brain belong in the wiki. The wiki reflects external facts, not internal lore posts.

## DB-2 — 20% Creative Signal Rule
Brain1 canon signals (brain1-canon.json) may influence at most 20% of any lore post. The remaining 80% must come from calendar rules, character continuity, and the time block. A brain1 signal is a seed, not a script.

## DB-3 — 7-Day Signal Vault
Brain1 canon signals older than 7 days MUST be treated as stale and ignored by the lore generator. Stale signals must not be marked used — they remain in the vault for potential archival review.

## DB-4 — Signal Lifecycle
A brain1 signal progresses through three states:
1. **Unread** — `b2_used: false`, available for injection
2. **Used** — `b2_used: true`, set only after a confirmed successful Telegram post
3. **Stale** — older than 7 days, silently skipped without marking as used

## DB-5 — Post 2 Image Cue
Post 2 is always sent WITH an image. The image prompt for Post 2 must visually reference at least one concrete scene element from the Post 2 lore text (not a generic GraffPunks fallback). If image generation fails, Post 2 falls back to plain text — but the image prompt must still be generated.

## DB-6 — Brain Isolation
Each of the 4 brains (crawl, analytics, gk, wiki) runs as an independent process. They communicate ONLY via the inter-brain JSON files listed in BRAIN-COORDINATOR.md. No brain may import functions from another brain's primary module.

## DB-7 — Wiki Brain Gatekeeper
wiki-brain.py MUST run a credential health check (`wiki_brain_health_check()`) before making any write calls. If credentials are missing or login fails, all wiki writes for that cycle are skipped — never retried in the same run.

## DB-8 — Crawl Deduplication
crawl-brain.py MUST use content fingerprinting (MD5 of title + snippet) to deduplicate new crawl results before writing to crawl-results.json. A result with an existing fingerprint MUST be silently discarded.

## DB-9 — Lore History Retention
The lore-history.md buffer retains the last 40,000 characters (~14 days of posts). Older content is trimmed automatically by save_lore_history(). This ensures the lore generator always has 2 weeks of continuity context.

## DB-10 — Env Fast-Fail
gk-brain.py MUST raise EnvironmentError immediately at the start of main() if GROK_API_KEY or TELEGRAM_BOT_TOKEN are not set. No partial execution is allowed without these two credentials.

## DB-11 — Claude Routing
When ANTHROPIC_API_KEY is set, all primary lore text generation routes through Claude 3.5 Sonnet via _llm_chat(). Grok is used as the fallback. Image generation always uses Grok regardless of ANTHROPIC_API_KEY.

## DB-12 — Telegram Rate Guard
A mandatory time.sleep(2) MUST be called between posting Message 1 and Message 2 in every Telegram posting loop. This guards against Telegram's per-bot rate limits for rapid sequential messages to the same chat.

## DB-37 — Lean 4-Brain Mandate (No Bloat Allowed)
**Implemented: 2026-03-20**

The GK BRAIN system runs on exactly 4 active brains + 2 support agents. No other Python files may be active in root.

**Active root files (permanent):**
- `crawl-brain.py` — Brain 1: web crawl
- `analytics-brain.py` — Brain 2: analytics & recommendations
- `gk-brain.py` — Brain 3: lore generation + Telegram + wiki queue
- `wiki-brain.py` — Brain 4: Fandom wiki push
- `error-guardian-agent.py` — Almighty Doctor & Supreme Overlord
- `master-backup-agent.py` — SHA-256 snapshots & rule conflict checks

**All other `.py` files** have been archived to `archive/` with one-line root stubs. Archived files must not be re-activated in root without explicit owner instruction.

**brain-rules.md** is limited to exactly 12 core DB rules (DB-1 through DB-12) plus this rule (DB-37). All extended rules (DB-13 through DB-36), lore canon, faction data, real people, and wiki pipeline rules live in `PROJECT-DNA.md` and `gk-brain-complete.md`.

This makes the Crypto Moonboys GK BRAIN fast, stable, and infinitely creative with zero conflicts and all canon locked forever.
