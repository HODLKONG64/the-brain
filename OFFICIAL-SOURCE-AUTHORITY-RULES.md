# OFFICIAL SOURCE AUTHORITY RULES

**Version:** 1.0  
**Applies to:** All GK BRAIN agents, crawl bots, wiki updaters, and any future agent in this repository.

These rules define which sources are authoritative, how conflicts are resolved, and how all agents must behave when reading, writing, or updating data.

---

## Rule 1 — Official Source List

The following URLs and all their sub-pages are the **only** authoritative sources for GK BRAIN content. Any content originating from these URLs is treated as ground truth.

### Medium & Substack
- `https://medium.com/@GKniftyHEADS` — @Graffitikings / GKniftyHEADS
- `https://graffpunks.substack.com/` — @Graffpunks
- `https://medium.com/@iamcharliebuster` — @CharlieBuster
- `https://medium.com/@noballgamesnfts` — @NoBallGames
- `https://noballgames.substack.com/` — @NoBallGames (Substack)
- `https://treefproject.substack.com/` — @TreefProject

### Official Websites
- `https://graffpunks.live/` — GraffPUNKS Official Hub (24/7 Blockchain Radio)
- `https://graffitikings.co.uk/` — Graffiti Kings Legacy Page

### YouTube
- `https://www.youtube.com/@GKniftyHEADS/videos` — @GKniftyHEADS

### X (formerly Twitter)
- `https://x.com/GraffitiKings` — @GraffitiKings
- `https://x.com/GKNiFTYHEADS` — @GKniftyHEADS
- `https://x.com/HODLWARRIORS` — @HODLWARRIORS
- `https://x.com/GraffPunks` — @GraffPUNKS
- `https://x.com/nftbuster` — @NFTBUSTER

### Instagram
- `https://www.instagram.com/graffitikings/` — @GraffitiKings
- `https://www.instagram.com/gkniftyheads/` — @GKniftyHEADS
- `https://www.instagram.com/hodlwarriors/` — @HODLWARRIORS
- `https://www.instagram.com/graffpunks/` — @GraffPUNKS
- `https://www.instagram.com/nftbuster/` — @NFTBUSTER

### High-Content Hubs
- `https://linktr.ee/gkniftyheads` — Linktree Central Hub
- `https://t.me/gkniftyheads` — Telegram IncubatorHub
- `https://www.facebook.com/GraffPUNKS.Network/` — Facebook Official Page

---

## Rule 2 — Conflict Resolution (Official Source Always Wins)

When a crawl finds new content from any Rule 1 URL that **conflicts** with data already saved in any brain, cache, or JSON file:

1. Delete the old saved data.
2. Save the new data from the official source.
3. Log the change to `crawl-log.json` with the old value, new value, timestamp, and source URL.
4. Do not ask. Do not pause. Execute automatically on every run.

---

## Rule 3 — Brain 2 Lore Sourcing

Brain 2's lore generation must use the following split:

- **70%** derived from Brain 2's own last 7 days of Telegram posts.
- **30%** derived from the official crawl results (Rule 1 URLs).

Brain 2 **must not** read `genesis-lore.md` for any future lore generation. That file was a one-time seed to start the agent. All ongoing lore is generated from Brain 2's rolling Telegram post history and the official crawl.

---

## Rule 4 — Run Schedule

All agents run every **2 hours on even UTC hours**: 00:00, 02:00, 04:00, 06:00, 08:00, 10:00, 12:00, 14:00, 16:00, 18:00, 20:00, 22:00.

Every run performs a **full crawl** of all Rule 1 URLs. Partial or sample crawls are not acceptable.

---

## Rule 5 — Wiki Sync

After every crawl, the Fandom wiki at `https://gkniftyheads.fandom.com/wiki/GKniftyHEADS_Wiki` must be checked:

- If the wiki is behind the latest crawl data → auto-update it via the MediaWiki API.
- If the wiki is already in sync → log the sync status and move on.

Only content sourced from Rule 1 URLs may be written to the wiki. Brain 2 Telegram lore posts must **never** be pushed to the wiki.

---

## Rule 6 — Standard Output Files

All agents write to these standard files (relative to repo root):

| File | Purpose |
|------|---------|
| `crawl-results.json` | Raw crawl results with dedup fingerprints |
| `substack-cache.json` | Parsed Substack/Medium post cache |
| `wiki-cache.json` | Last-known wiki page snapshots |
| `lore-conflict-report.json` | Detected conflicts between sources and saved data |
| `crawl-log.json` | Audit log of every crawl action and conflict resolution |
| `PROJECT-BRIEFING.md` | Auto-updated human-readable briefing for new agents |
| `wiki-citation-log.json` | Log of all citation health-check runs and actions taken |

---

## Rule 7 — Auto-Briefing Update

After every successful crawl, `PROJECT-BRIEFING.md` must be updated with:

- Latest lore summary (one paragraph).
- Most recent Substack/Medium updates (titles + URLs).
- Current wiki sync status.
- Any known conflicts or dead links found.
- Timestamp of the last full run.

This ensures any new Copilot agent reading the repo is immediately fully briefed without needing external context.

---

## Rule 8 — Source Purity (No Unofficial Sources)

Agents must **never** crawl:

- Unofficial fan sites, parody accounts, or community wikis not listed in Rule 1.
- Any URL not explicitly listed in Rule 1 or directly linked from a Rule 1 page as an official sub-page.
- Content generated internally by Brain 2 (Telegram lore posts, generated narratives) must not be treated as an official external source.

If a URL is uncertain, treat it as unofficial and skip it.

---

## Rule 9 — Citation Health-Check Before Any Wiki Write

**All citation URLs on wiki pages must be verified live before any wiki write.**

Before any agent writes new content to any GKniftyHEADS Fandom wiki page, it must run a full citation health-check pass as follows:

### Step 1 — Crawl all current wiki pages
Enumerate every page on the GK fan wiki using the MediaWiki `allpages` API and fetch the current wikitext of each page.

### Step 2 — Check every citation URL
For every external URL found on each page, perform an HTTP health check:
- Send a HEAD (or GET) request and check the response status code.
- Any non-2xx response or network timeout = **dead link**.

### Step 3 — Repair or remove dead links
For each dead link found:

**If a replacement can be found:**
- Query the Wayback Machine availability API (`https://archive.org/wayback/available?url={dead_url}`) for a cached snapshot.
- If a live archived snapshot exists: replace the dead URL with the archived URL in the page wikitext and save the edit to the wiki.

**If no replacement can be found:**
- Delete the citation paragraph or bullet point containing the dead URL from the page wikitext.
- Save the cleaned page to the wiki.

### Step 4 — Log all actions
Every dead link found, every replacement made, and every deletion must be logged to `wiki-citation-log.json` with:
- Page title
- Dead URL
- Replacement URL (or `null` if deleted)
- Action taken (`replaced` or `removed`)
- Timestamp

### Step 5 — Continue with normal wiki write
Only after the citation health-check pass has completed (or failed gracefully) may the agent proceed with writing new content to the wiki.

### Fail-safe
If the citation health-check itself encounters an error (network down, API unavailable, etc.), it must:
- Log the error to `wiki-citation-log.json`.
- **Not** block the normal wiki write — the agent continues to the write step regardless.

The health-check pass must **never** prevent the normal wiki-write flow from completing.

---

*This file is read by all agents before any write operation. Do not delete or truncate it.*
