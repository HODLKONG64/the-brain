# UPDATE INTEGRATION RULES
# Formal rule system for how the GK BRAIN agent uses detected updates.
# All rules referenced with (rule-name) tokens.

---

## ENTRY POINT

### `(rule-one)` — Main Update Entry Point
- Called at the start of every 2-hour cycle.
- Triggers `(rule-2)` (web crawl).
- If crawl returns updates: triggers `(rule-2-real)`.
- If no updates: agent generates pure calendar-based lore and exits.

---

## CRAWL RULES

### `(rule-2)` — Web Crawl + Save Data + Extract Key Parts
1. Run `update-detector.py` against all URLs in `gkandcryptomoonboywebsitestosave.md`.
2. Compare current page content against `crawl-snapshot.json`.
3. Extract changed sections: title, first paragraph, key data points.
4. Save results to `wiki-update-queue.json` (one entry per detected change).
5. Return structured update JSON to main agent.

### `(rule-3)` — Extended Crawl (Activated When Updates Are Sparse)
- If `(rule-2)` finds fewer than 2 updates, also check:
  - RSS feeds for all Substack sources.
  - Twitter/X recent posts (if accessible).
  - NFT platform "latest sales" endpoints.
- Merge results with `(rule-2)` output.
- Still classify by category before returning.

### `(rule-2-real)` — Apply When Rule Has "real" Suffix
- Any activity rule token ending in `-real` (e.g., `fishing-real`, `graffiti-news-real`) means:
  1. Perform a targeted web search for that real-world content.
  2. Extract the single most relevant, recent item.
  3. Mark it with `"use_in_lore": true` and `"lore_weight": 0.05` (5% max).
  4. The item will appear as a brief mention woven naturally into the lore.
  5. Mark as "used" in the update queue so it is not repeated next cycle.

---

## WIKI RULES

### `(rule-wiki)` — Update Wiki After Telegram Post (Simple Append)
1. After **both** Telegram posts are sent successfully:
2. Load `wiki-update-queue.json`.
3. For each entry: call `wiki-updater.py`.
4. `wiki-updater.py` creates or updates the relevant Fandom wiki page.
5. On success: delete the entry from `wiki-update-queue.json`.
6. On failure: log error, retain entry for next cycle retry.
7. After all entries processed: delete `crawl-snapshot.json` (fresh start next cycle).

### `(rule-wiki-smart)` — Intelligent Wiki Merge (Smart Layer)
1. After **both** Telegram posts are sent successfully:
2. Load `wiki-update-queue.json`.
3. For each entry, run `wiki-smart-merger.py`:
   - **Smart Merge (primary):** Read current wiki page → detect existing sections →
     check whether this data is already present (duplicate guard) →
     if data is **missing**, insert it into the matching section (see `wiki-merge-rules.md`).
   - **Simple Append (fallback / always):** Append a timestamped log entry to
     `GK_BRAIN_Agent_Log` regardless of smart merge outcome.
4. Mark entry `"wiki_done": true` on success; retain for retry on failure.
5. After all entries processed: delete `crawl-snapshot.json`.

#### Decision Tree for `(rule-wiki-smart)`

```
New update detected?
        │
        ▼
Is update type in SECTION_MAP?  ──── No ──► Simple append to main page + log entry
        │
       Yes
        ▼
Does target section already contain this data?  ──── Yes ──► Log-only (no duplicate)
        │
        No
        ▼
Smart merge: insert bullet into matching section  ──── Fails ──► Simple append fallback
        │
      Success
        ▼
Always: append audit log entry to GK_BRAIN_Agent_Log
```

#### When to Use Simple vs Smart
| Situation                              | Method        |
|----------------------------------------|---------------|
| Update type maps to a known section    | Smart merge   |
| Update type is unknown / unclassified  | Simple append |
| Smart merge raises an exception        | Simple append |
| Data already present (duplicate guard) | Log-only      |
| Agent log audit trail                  | Always append |

---

## ACTIVITY RULES

### `(fishing)` — Artist at Carp Lake
1. Web search: "UK carp lakes" → pick random lake name.
2. Web search: UK weather for current UTC time + artist's location.
3. Generate lake scene: morning mist / afternoon sun / evening bite window based on time token.
4. Describe bait setup, rods, waiting, sounds, atmosphere.
5. Optionally: parkour warm-up to reach the swim.

### `(fishing-real)` — Real UK Carp Catch News
1. Web search: "UK carp catch record recent 40lb 70 hours".
2. Scan `fishing-real` URLs in `gkandcryptomoonboywebsitestosave.md`.
3. If catch ≥40lb found within 70 hours: extract lake name, weight, method.
4. Weave into **~5% of lore**: "overheard on the fishing forums…" or "read on his phone while waiting for a bite…".
5. Mark as used. Do NOT repeat.

### `(graffiti)` — Artist Painting/Tagging
1. Pick random UK wall location or landmark.
2. Generate paint session: colour choices, style, surroundings, time of day.
3. May include: police scare, other writers, paint running out, passing trains.

### `(graffiti-news-real)` — Real Street Art News
1. Scan `graffiti-news-real` URLs in `gkandcryptomoonboywebsitestosave.md`.
2. Extract most recent street art story, contest, or artist feature.
3. Weave into **~5-10% of lore**: "saw a clip online…" or "heard from a mate…".
4. Mark as used.

### `(rave)` — Artist Raving
1. Scan `rave-real` URLs for current UK drum & bass nightclub events.
2. Pick one real or plausible venue (e.g., "Printworks London", "Fabric").
3. Web search: 4 random UK drum & bass DJs with current relevance.
4. Describe: arriving at venue, sound system, crowd, sweat, bass.

### `(rave-real)` — Real UK Rave / DJ Event
1. Same as `(rave)` but ensure venue and DJs are real and current.
2. If GraffPUNKS Network Radio is live: trigger `(live)` rule inline.

### `(live)` — GraffPUNKS Network Radio Live Alert
Format: `🔴 [GRAFFPUNKS NETWORK RADIO — LIVE] :: [artist hears alert]`
- Inline in lore text, not a separate post.
- Example: "While fishing, phone buzzes — 🔴 GraffPUNKS Network Radio LIVE. He tucks it back in his pocket and watches the rod tip."
- Example: "Mid-queue at Printworks — 🔴 GraffPUNKS Network Radio drops a new track, hears it through someone's speaker."

### `(night)` — Night Theme Enforcement
- All lore text must describe night: darkness, streetlights, stars, cold air, silence.
- All image prompts must specify: "dark night scene", "neon glow", "moonlit".

### `(early-morning)` — Pre-Dawn / Misty Sunrise Theme
- Lore must describe: mist rising, first light, dew, cold breath, birds waking.
- Image prompts: "misty sunrise", "golden hour beginning", "foggy street".

### `(morning)` — Morning Theme
- Bright morning energy, people starting the day, cafes opening, trains busy.

### `(afternoon)` — Afternoon Theme
- Warm light, slower pace, productive creative time.

### `(evening)` — Evening / Dusk Theme
- Golden hour, end of day, reflecting, winding down or gearing up for night.

### `(outside)` — UK Weather Integration
1. Web search: "UK weather [current UTC time]" or use last fetched weather data.
2. Include actual conditions: temperature, cloud cover, wind, rain or sun.
3. Visualise in image prompt: match weather to scene.
4. Include in lore log details: "Weather: 7°C, overcast, 15mph NW wind."

### `(news-real)` — Breaking News Integration
1. Check `news-real` URLs in `gkandcryptomoonboywebsitestosave.md`.
2. Extract breaking crypto, political, or street art story from last 2 hours.
3. Weave into **~5-10% of lore**: natural character reaction.
4. Never more than 10% of total lore text.
5. Mark as used.

### `(gkdata-real)` — Official GK Update Integration
1. Run `(rule-2)` for `gkdata-real` URLs.
2. If update detected:
   - **Option A (Radio Alert):** Format as GraffPUNKS Network Radio announcement.
     Format: `🔴 [GRAFFPUNKS NETWORK RADIO — ALERT] :: [update summary in character voice]`
   - **Option B (Lore Weave):** Weave into lore as ~10% of text.
   - Agent uses AI classification to decide: major drop → Option A; minor update → Option B.
3. Use update **only once** (mark in `wiki-update-queue.json`).

### `(random)` — Pure Character Invention
- Agent makes up content entirely in character.
- No external data needed.
- Stay within: artist's persona, weekly routine, Blocktopia lore, character bible.

### `(random-news)` — Random Character-Filtered News Angle
- Agent picks any recent news angle (from `news-real` sources).
- Filters through the artist's perspective and personality.
- Keeps it human and brief: "caught something on the radio about…".

### `(dream)` — Dream Sequence Rules
- Lore is a dream: surreal, non-linear, vivid imagery.
- Always state it is a dream in the opening line.
- `(moonboys)` dreams: 1-2 Crypto Moonboys characters as headliners.
  - Rotate pairings so no two characters headline together twice in a row.
- `(lady-ink)` dreams: Lady-INK is present.
- `(train-dream)`: Artist and Lady-INK travel the world painting trains (unique new story every Thursday/Saturday).
- `(monday-wake)`: Dream ends with: "what the hell? why?" confusion + mural that was never finished.
- `(saturday-ink-dream)`: Lady-INK steals his cap on the train.

### `(lady-ink)` — Lady-INK Appearance Rules
- Lady-INK appears **only** when:
  - Artist is going out to spray graffiti, OR
  - It is a dream/night sequence (Thursday night, Saturday night, or `(lady-ink)` block).
- She meets him a few hours before the spray session.
- Rotate through 25 unique storylines (track in lore-history.md).

---

## UPDATE INTEGRATION DECISION LOGIC

### When an Update is Detected:
1. Extract key data: title, source, summary, timestamp.
2. Classify by type: `gkdata-real`, `fishing-real`, `graffiti-news-real`, `news-real`, `rave-real`, `lady-ink-hint`.
3. Determine integration method:
   - `gkdata-real` major (new NFT drop, new collection) → GraffPUNKS Network Radio Alert format.
   - `gkdata-real` minor (new post, new image) → 10% lore weave.
   - `fishing-real` → 5% lore mention (overheard, read on phone).
   - `graffiti-news-real` → 5-10% lore weave.
   - `news-real` → 5-10% lore weave.
   - `rave-real` → Weave into `(rave)` block naturally.
   - `lady-ink-hint` → Activate `(lady-ink)` rule if not already active.
4. Mark update as `"used": true` in `wiki-update-queue.json`.
5. **The update appears in ONLY ONE Telegram post per cycle.**

### Lore Composition Ratios:
- **If update detected:**
  - 5-10% update content (naturally woven)
  - 90-95% calendar-driven lore (character continuity + weekly routine)
- **If no update detected:**
  - 100% calendar-driven lore

### Character Epoch Rule:
- Before generating lore, check all featured characters.
- Characters from 1980s London **cannot** mix with Year 3009 Blocktopia characters in the same lore post.
- Exception: Dream sequences (all epochs can mix in surreal dream logic).

### One-Time Use Rule:
- Each detected update is marked `"used": true` after it appears in a post.
- The same update is **never** used again in future cycles.
- `wiki-update-queue.json` is the source of truth for used/unused updates.

---

## ERROR HANDLING RULE

### Stuck Agent Rule (>5 Minutes Without Output):
- If the agent has not produced a Telegram post within 5 minutes of its scheduled run:
  1. Send to Telegram: "AT THE DOCTORS, YOU WOULDN'T WANT TO SEE THIS :("
  2. Log the error with timestamp.
  3. Sleep until next 2-hour cycle.
  4. On next wake: clear any partial state, restart fresh.

---

## POST-TELEGRAM WIKI UPDATE FLOW

1. Telegram posts sent ✅
2. Load `wiki-update-queue.json` for this cycle.
3. For each entry with `"wiki_update": true`:
   - **Primary:** Call `wiki-smart-merger.py` — smart section merge + audit log.
   - **Fallback:** If smart merger is unavailable, call `wiki-updater.py` (simple append).
4. Mark entry `"wiki_done": true`.
5. Delete processed entries from queue.
6. Delete `crawl-snapshot.json` → fresh crawl next cycle.
7. Sleep until next 2-hour cron ping.

### Smart Merger Summary
- `wiki-smart-merger.py` reads the current wiki page, detects existing sections,
  checks for duplicate content, and inserts new data into the correct section.
- Every run appends a log entry to `GK_BRAIN_Agent_Log` for full audit trail.
- See `wiki-merge-rules.md` for the full category → section mapping and merge patterns.

---

## GODLIKE MODE

### `(rule-godlike)` — Activate All 55 Systems
- Engages all 55 integrated systems in the correct tier order.
- Tier 1 (Data): validate → causal inference → knowledge graph → multi-source fusion → world state → anomaly detection → temporal alignment → source attribution → priority queue → deduplication.
- Tier 2 (Planning): hierarchical plan → adaptive weights → theory of mind → constraints → symbolic reasoning → RL optimizer → transfer learning → uncertainty quantification.
- Tier 3 (Character): memory bank → emotional state → skill levels → relationships → arc tracking → interpolation → personality → world bible → arc planner → memory references.
- Tier 4 (Generation): emergent hooks → lore fusion → NPC dialogue → sentiment → style → tension curve → meta-narrative → gap filler → causal weaving → universe hints.
- Tier 5 (QA): quality gate → contradiction check → ethical filter → source verify → coherence validate → plagiarism detect → consistency proof.
- Tier 6 (Analytics): engagement track → performance metrics → learning feedback → recursive discovery → trend prediction → comparative analysis → debug report.
- Tier 7 (Integration): multi-platform orchestrate → system health monitor.
