# OFFICIAL SOURCE AUTHORITY RULES
**Version:** 1.0  
**Owner:** HODLKONG64  
**Applies to:** ALL webcrawl agents, Brain 2 (gk-brain.py), crawl-brain.py, wiki-brain.py, wiki-smart-merger.py, and any future agent in this repo  
**Last Updated:** 2026-03-18

---

## RULE 1 — OFFICIAL SOURCE LIST (HIGHEST AUTHORITY)

Any content found at the URLs below — or on any sub-page/child-page that lives under these domains — is OFFICIAL and AUTHORITATIVE.

When a webcrawl agent finds new content from these sources that CONFLICTS with previously saved crawl data, the agent MUST:
1. Accept the new content as correct
2. Overwrite / replace the old saved data with the new data
3. Save the new data to the relevant cache file (e.g. `crawl-results.json`, `substack-cache.json`, etc.)
4. Delete the old conflicting entry — do NOT keep both versions
5. Log the update in the crawl log with timestamp, source URL, and a brief description of what changed

### OFFICIAL SOURCE DOMAINS AND URLS

#### SUBSTACK / MEDIUM (Lore, Strategy, Universe Updates)
- https://graffpunks.substack.com/ (and ALL sub-pages/posts under this domain)
- https://medium.com/@GKniftyHEADS (and ALL articles)
- https://medium.com/@iamcharliebuster (and ALL articles)
- https://medium.com/@noballgamesnfts (and ALL articles)
- https://noballgames.substack.com/ (and ALL sub-pages/posts)
- https://treefproject.substack.com/ (and ALL sub-pages/posts)

#### OFFICIAL WEBSITES
- https://graffpunks.live/
- https://graffitikings.co.uk/

#### YOUTUBE
- https://www.youtube.com/@GKniftyHEADS/videos (and ALL videos/descriptions under this channel)

#### X / TWITTER
- https://x.com/GraffitiKings
- https://x.com/GKNiFTYHEADS
- https://x.com/HODLWARRIORS
- https://x.com/GraffPunks
- https://x.com/nftbuster

#### INSTAGRAM
- https://www.instagram.com/graffitikings/
- https://www.instagram.com/gkniftyheads/
- https://www.instagram.com/hodlwarriors/
- https://www.instagram.com/graffpunks/
- https://www.instagram.com/nftbuster/

#### LINKTREE / HUB
- https://linktr.ee/gkniftyheads (and ALL links it points to)

#### TELEGRAM
- https://t.me/gkniftyheads

#### FACEBOOK
- https://www.facebook.com/GraffPUNKS.Network/

#### FANDOM WIKI (Official Canon Reference)
- https://gkniftyheads.fandom.com/wiki/GKniftyHEADS_Wiki (and ALL sub-pages under this wiki)

---

## RULE 2 — CONFLICT RESOLUTION PROTOCOL

When ANY crawl agent finds new content from an OFFICIAL SOURCE (listed in Rule 1) that conflicts with previously cached/saved data:

```
IF new_content.source IN official_sources:
    → new_content IS CORRECT
    → DELETE old conflicting data
    → SAVE new_content to cache
    → LOG the update with: timestamp, source_url, what_changed
    → DO NOT keep both versions
    → DO NOT ask for human confirmation — just update automatically
ELSE:
    → Flag the conflict for review
    → Do NOT auto-overwrite
    → Log as "unverified conflict — pending review"
```

---

## RULE 3 — LORE SOURCING RULES FOR BRAIN 2 (gk-brain.py)

### What Brain 2 uses for lore inspiration:
1. **PRIMARY SOURCE (70%):** The last 7 days of Brain 2's own Telegram posts (saved in lore history file — `lore-history.txt` or equivalent)
2. **SECONDARY SOURCE (30%):** Fresh content crawled from the OFFICIAL SOURCES above (Substack posts, wiki updates, Medium articles)

### What Brain 2 must NEVER use for lore:
- `genesis-lore.md` — this was a one-off first-run inspiration file only. Brain 2 must NOT read or reference this file for lore generation after the initial setup run.
- `brain1-canon.json` — Brain 1 signals are injected by the Brain 1 pipeline. Brain 2 does not read this file directly for lore.
- Any cached crawl data older than 7 days

### Brain 1 Signal Integration:
- Brain 2 MUST incorporate Brain 1 signals (passed via the pipeline) into its lore posts
- Brain 1 signal influence: **30% of lore content** should reflect or be inspired by the most recent Brain 1 updates
- Only the most recent Brain 1 signals (within the last 7 days) are valid — older signals are stale and must be ignored
- Only signals that were actually injected into the current prompt count as "used" — do NOT mark unused signals as used

---

## RULE 4 — 2-HOUR RUN CYCLE SCHEDULE

The agent runs every 2 hours on even UTC hours:
- 00:00 UTC, 02:00 UTC, 04:00 UTC, 06:00 UTC, 08:00 UTC, 10:00 UTC
- 12:00 UTC, 14:00 UTC, 16:00 UTC, 18:00 UTC, 20:00 UTC, 22:00 UTC

On EVERY run, the crawl agent MUST:
1. Fetch and check ALL OFFICIAL SOURCES listed in Rule 1 for new or updated content
2. Follow sub-links / child pages on each domain to catch new posts, articles, videos
3. Compare fetched content against previously cached data
4. Apply Rule 2 conflict resolution
5. Save updated cache files
6. Pass any relevant new content/updates to Brain 2 for lore integration
7. Check the Fandom wiki and flag any pages that are outdated vs current lore
8. Log a crawl summary with: timestamp, sources checked, conflicts found, updates applied

---

## RULE 5 — WIKI SYNC RULES (wiki-brain.py / wiki-smart-merger.py)

The Fandom wiki at https://gkniftyheads.fandom.com/wiki/GKniftyHEADS_Wiki is the OFFICIAL PUBLIC CANON record.

On each 2-hour cycle:
1. Read the current wiki page content via the Fandom API
2. Compare against the most recent Brain 2 lore posts (last 7 days)
3. Compare against any new OFFICIAL SOURCE content fetched this cycle
4. If the wiki is BEHIND or CONTRADICTS the official sources:
   - Generate an update using the new official content
   - Push the update to the wiki via the Fandom API
   - Log: what page was updated, what changed, timestamp
5. If the wiki is UP TO DATE — log "wiki in sync" and move on

---

## RULE 6 — CACHE FILE NAMING CONVENTION

All crawl agents must save cached data to these standard files:

| Data Type | File |
|-----------|------|
| General crawl results | `crawl-results.json` |
| Substack post cache | `substack-cache.json` |
| Fandom wiki cache | `wiki-cache.json` |
| Lore conflict report | `lore-conflict-report.json` |
| Crawl run log | `crawl-log.json` |
| Agent briefing (auto-updated) | `PROJECT-BRIEFING.md` |

All cache files store only data from the last 7 days. Entries older than 7 days are automatically deleted on each run.

---

## RULE 7 — PROJECT BRIEFING AUTO-UPDATE

After every successful crawl cycle, the agent MUST update `PROJECT-BRIEFING.md` with:
- Date/time of last successful crawl
- Sources checked and their last-updated timestamps
- Summary of any lore conflicts found and resolved
- Current wiki sync status
- Any Brain 1 signals received and their status (used / pending / stale)

This file is what new Copilot agents read to instantly get up to speed on the project without needing to ask questions.

---

## RULE 8 — DO NOT CRAWL LIST

These sources must NEVER be crawled, scraped, or used as data inputs:
- Any random third-party NFT aggregator or marketplace not listed above
- Any unofficial fan site or parody account
- Any X/Twitter account not in the official list above
- Any content from before 2021 unless it appears on an official source

---

## SUMMARY TABLE

| Rule | What it does |
|------|-------------|
| Rule 1 | Lists all official sources — content from these always wins |
| Rule 2 | Auto-overwrite old data when official source has new version |
| Rule 3 | Brain 2 lore sources: 70% own posts, 30% official crawl, never genesis-lore |
| Rule 4 | Run every 2 hours on even UTC hours — full crawl every run |
| Rule 5 | Wiki sync on every run — update if behind official sources |
| Rule 6 | Standard cache file names for all agents |
| Rule 7 | Auto-update PROJECT-BRIEFING.md after every run |
| Rule 8 | Never crawl unofficial or non-listed sources |
