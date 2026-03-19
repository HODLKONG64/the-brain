# CROSS-PLATFORM CONSISTENCY — GK BRAIN

Rules and mechanisms that keep GK BRAIN output consistent across all platforms
(Telegram, Fandom wiki, web sources).

---

## 1. The Consistency Problem

GK BRAIN posts to **Telegram** every 2 hours and writes to the **Fandom wiki** based on
web crawl results. Without consistency rules, the following problems arise:

- Lore generated for Telegram could contradict official source facts found on the web
- Character names, faction affiliations, or timeline references could drift across posts
- Wiki content could duplicate or contradict Telegram content

---

## 2. Separation of Concerns (DB-1 & DB-6)

The fundamental consistency mechanism is **strict separation**:

| Platform | Content source | May influence other platforms? |
|---|---|---|
| **Telegram** | AI-generated lore (Claude/Grok) seeded by web crawl | NEVER feeds wiki |
| **Fandom wiki** | Real-world facts from official web sources only | Does not feed Telegram directly |
| **Web crawl** | Official source URLs (see `gkandcryptomoonboywebsitestosave.md`) | Feeds BOTH (via `brain1-canon.json` for lore context + `wiki-update-queue.json` for wiki) |

---

## 3. Canon as the Single Source of Truth

`brain1-canon.json` is the shared canon signal store:
- Written by Crawl Brain (`crawl-brain.py`) from verified official source URLs
- Read by Lore Brain (`gk-brain.py`) for up to 20% context injection (DB-2)
- Signals older than 7 days are treated as stale by the Lore Brain (DB-3)
- Signal marked `b2_used: true` ONLY after a confirmed Telegram post (DB-4)

This ensures both Telegram posts and wiki content trace back to the same verified facts.

---

## 4. Name & Entity Consistency

Before any proper noun appears in Telegram lore or a wiki page, it must be:
1. **Found on an official source URL** (verified by Crawl Brain)
2. **Cross-checked against `MASTER-CHARACTER-CANON.md`** for correct faction, role, and spelling
3. **Not present in `non-canon-names.log`** (which tracks rejected fan-invented names)

---

## 5. Lore History as Continuity Buffer (DB-9)

`lore-history.md` retains the last 40,000 characters (~14 days of posts). Every new lore
generation call receives this buffer as context, preventing the narrator from:
- Contradicting events posted in the last 2 weeks
- Repeating identical narrative beats
- Killing off characters who were just introduced

---

## 6. Deduplication (DB-8)

`crawl-brain.py` uses SHA-256 fingerprinting (via `deduplication-engine.py`) on every
crawl result before writing to `crawl-results.json`. A result with an existing fingerprint
is silently discarded. This prevents the same real-world update from seeding multiple
identical lore posts or wiki entries.

---

## 7. Wiki ↔ Telegram Firewall

The Lore Brain MUST NEVER use content from previous Telegram posts as a wiki source.
Specifically, `_is_valid_wiki_source()` in `wiki-smart-merger.py` blocks:
- Any update with `source == "gk-brain-agent"`
- Any update with `"telegram"` in the source string
- Any update with type `lore-post`, `telegram-lore`, or `brain-lore`

---

## 8. Cross-Wiki Consistency

`wiki-cross-checker.py` runs after page writes to detect internal inconsistencies between
wiki pages — for example, a character listed in two conflicting factions, or a date
mismatch between an event page and a character bio.

---

## 9. Backup Agent as Consistency Monitor (DB-15 through DB-19)

`master-backup-agent.py` runs last every cycle and:
- SHA-256 fingerprints all 34 tracked files (detects unauthorised changes)
- Extracts DB-N and MB-N rules — if any incoming file tries to change a locked rule, the conflict is logged and the new rule is discarded (DB-16)
- Ensures no brain has accidentally imported from another brain's module (DB-6 / DB-18)
