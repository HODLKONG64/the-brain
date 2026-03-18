# OFFICIAL-SOURCE-AUTHORITY-RULES.md

**Version:** 1.0  
**Owner:** HODLKONG64 (@HodlKONG64)  
**Purpose:** Single authoritative rulebook defining which external sources are permitted to trigger updates to the GKniftyHEADS Fandom wiki and what content is absolutely forbidden from appearing there.

---

## RULE 1 — OFFICIAL SOURCES (What counts as an authoritative update)

Only the following external online sources are recognised as authoritative for wiki updates:

1. **Substack** — Posts published on the official GraffPunks / GKniftyHEADS Substack account(s).
2. **Medium** — Articles published from the official Medium account(s).
3. **Official websites** — Content changes on `graffpunks.live` and `graffitikings.co.uk`.
4. **YouTube** — New video titles/descriptions from the official YouTube channel.
5. **X / Twitter** — Posts from the official verified X/Twitter accounts.
6. **Fandom wiki itself** — Corrections or additions found by cross-checking the official GKniftyHEADS Fandom wiki.

Any source NOT in this list is **non-authoritative** and must not trigger a wiki write.

---

## RULE 2 — NON-AUTHORITATIVE SOURCES (What is explicitly blocked)

The following are **never** authoritative sources for wiki updates:

- Brain 2 (`gk-brain-agent`) — Brain 2 is a content generator, not a source authority.
- Telegram posts — Telegram channel posts are for audience distribution only.
- Internal `.json` data files (`brain1-canon.json`, `wiki-update-queue.json`, etc.).
- Auto-generated agent logs (`GK_BRAIN_Agent_Log` entries, diagnostic output).
- `genesis-lore.md` — One-off bootstrap file; its content must never appear on the wiki.

---

## RULE 3 — TELEGRAM LORE POSTS (Explicitly forbidden from wiki)

Brain 2's Telegram lore posts are **for Telegram only**.  
They are **NEVER** pushed to the wiki.  
`genesis-lore.md` content is **NEVER** pushed to the wiki.

---

## RULE 4 — SOURCE TAGGING

Every update queued in `wiki-update-queue.json` must include a `"source"` field that identifies the originating URL or platform (e.g. `"https://graffpunks.substack.com/p/..."`, `"youtube"`, `"x.com"`).  
Updates with `source == "gk-brain-agent"` or `source == "telegram"` are automatically blocked by the source validation guard.

---

## RULE 5 — DEDUPLICATION

Before writing any update to the wiki, the agent must check:

1. Source URL already present in page content → skip.
2. Title + date already present in same line → skip.
3. Content fingerprint (MD5 prefix embedded as wiki comment) already present → skip.

---

## RULE 6 — CROSS-CHECKER FIRST

Before writing to the wiki the agent should run `wiki-cross-checker.py` to confirm the update is not already present on the Fandom wiki.  Only updates confirmed as **missing** from the wiki proceed to the write step.

---

## RULE 7 — LAYOUT SAFETY

Before writing **any** wikitext to a page, the agent must validate the MediaWiki markup:

- All `{{` template tags must be closed with `}}`.
- All `<div>` tags must be closed with `</div>`.
- No vertical text artifacts (single-character lines caused by broken infoboxes).
- No `writing-mode: vertical` or `transform: rotate` CSS.

If validation fails → save to `wiki-rejected-drafts.json` and **skip** — do NOT write to wiki.

---

## RULE 8 — AGENT LOG PAGE

The `GK_BRAIN_Agent_Log` wiki page is the **only** page that may receive auto-generated agent diagnostic entries.  
Agent log entries must **never** be written to the main wiki page (`GKniftyHEADS_Wiki`) or any lore/character pages.

---

## RULE 9 — WIKI CONTENT RESTRICTIONS (WHAT NEVER GOES TO THE WIKI)

The following content types **MUST NEVER** be written to the Fandom wiki under any circumstances:

1. **Brain 2 Telegram lore posts** — Brain 2's generated lore posts are for Telegram only. They are NEVER pushed to the wiki.
2. **`genesis-lore.md` content** — This was a one-off bootstrap file. Its content must never appear on the wiki.
3. **Brain 1 signal data** — `brain1-canon.json` entries are internal pipeline signals, not public wiki content.
4. **Auto-generated agent logs** — GK_BRAIN_Agent_Log entries are internal diagnostics. They must only appear on the `GK_BRAIN_Agent_Log` wiki page if manually approved, never auto-pushed to the main wiki pages.
5. **Any update where `source == "gk-brain-agent"`** — Brain 2 is a content generator, not a source authority.

### ONLY these sources may trigger a wiki update:
- New Substack posts or edits on official Substack domains
- New Medium articles from official accounts
- Official website (`graffpunks.live` / `graffitikings.co.uk`) content changes
- New YouTube video descriptions from the official channel
- Official X/Twitter posts from the listed accounts
- Corrections or additions found by cross-checking the official Fandom wiki itself

### Layout Safety Rule:
Before writing ANY content to the wiki, the agent MUST validate the MediaWiki markup:
- All `{{` template tags must be closed with `}}`
- All `<div>` tags must be closed
- No vertical text artifacts (broken sidebar infoboxes)
- If validation fails → save to `wiki-rejected-drafts.json` and skip — do NOT write to wiki
