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
3. Run `wiki-cross-checker.py` to compare saved data against the wiki:
   - Cross-check identifies updates missing from the wiki.
   - Only genuinely missing/changed data is sent to the merger.
4. For each missing entry, run `wiki-smart-merger.py`:
   - **Smart Merge (primary):** Read current wiki page → detect existing sections →
     check whether this data is already present (URL, title+date, or content fingerprint) →
     if data is **missing**, insert it into the matching section (see `wiki-merge-rules.md`).
   - Unknown update types go into the `Uncategorized Updates` section (no data loss).
   - **Simple Append (fallback / always):** Append a timestamped log entry to
     `GK_BRAIN_Agent_Log` regardless of smart merge outcome.
5. Mark entry `"wiki_done": true` on success; retain for retry on failure.
6. After all entries processed: delete `crawl-snapshot.json`.

#### Decision Tree for `(rule-wiki-smart)`

```
New update detected?
        │
        ▼
Save ALL detected updates to wiki-update-queue.json (no keyword filtering)
        │
        ▼
Use KEY BITS for: lore, images, random thoughts, GraffPunks alerts, Telegram posts
        │
        ▼
Run wiki-cross-checker.py: compare saved data vs Fandom wiki
        │
        ▼
Is update already on wiki? (URL match / title+date / content fingerprint)
        │
       Yes ──► Log-only (no duplicate)
        │
        No
        ▼
Is update type in SECTION_MAP?  ──── No ──► Insert into "Uncategorized Updates" section
        │
       Yes
        ▼
Smart merge: insert bullet with source attribution into matching section
        │
     Fails ──► Simple append fallback
        │
      Success
        ▼
Always: append audit log entry to GK_BRAIN_Agent_Log
```

#### When to Use Simple vs Smart
| Situation                              | Method                              |
|----------------------------------------|-------------------------------------|
| Update type maps to a known section    | Smart merge → known section         |
| Update type is unknown / unclassified  | Smart merge → Uncategorized Updates |
| Smart merge raises an exception        | Simple append fallback              |
| Data already present (duplicate guard) | Log-only                            |
| Agent log audit trail                  | Always append                       |

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
  1. Log the timeout with timestamp.
  2. Exit gracefully (no "AT THE DOCTORS" message).
  3. On next wake: clear any partial state, restart fresh.

### 50-Fail Graceful Degradation Rule (Lore Generation):
- The agent **NEVER** exits mid-cycle due to lore generation errors.
- Instead: increment a fail counter on each exception.
- On each failure: preserve the best partial lore collected so far.
- **At 50 consecutive failures:** Use partial/fallback lore compiled from collected context.
- Log: `[lore-gen] Completed lore after 50 failures using partial data`
- **Always post to Telegram** — never leave a cycle incomplete.

```python
# Lore generation with 50-fail graceful degradation
fail_counter = 0
best_lore = compile_fallback_from_context(block, rule_ctx)
while fail_counter < 50:
    try:
        lore = generate_lore_with_all_task_points(...)
        break  # success
    except Exception as e:
        fail_counter += 1
        best_lore = compile_partial_lore_from_collected_data()
if fail_counter >= 50:
    lore = best_lore
    print("[lore-gen] Completed after 50 failures")
# Always post to Telegram
post_to_telegram(lore, image)
```

### 50-Fail Graceful Degradation Rule (Image Generation):
- Same 50-fail logic applies to image generation.
- On failure: retry with different reference image.
- At 50 failures: use last successful image (from previous cycle) OR text-only Telegram post.
- **Image failure NEVER blocks the lore post** — Telegram post always goes out.

### Old Rule (REMOVED — DO NOT USE):
- ~~Send "AT THE DOCTORS, YOU WOULDN'T WANT TO SEE THIS :(" on lore generation failure~~
- This behaviour has been removed. The agent now uses graceful degradation.

---

## TASK POINTS EXECUTION RULE

### `(rule-task-points)` — Execute All Calendar Task Points in Order
Each calendar block in `lore-planner.md` now includes a **Task Points** column.
Task points are structured sub-tasks the agent **MUST** address in the generated lore.

**Format in lore-planner.md:**
```
| 06:00–08:00 | Mural-chase wake dream | (dream) (lady-ink) (monday-wake) | **1. Describe the mural location** \| **2. Lady-INK's role in dream** \| **3. Message/vision from dream** \| **4. Emotional state upon waking** |
```

**Execution pipeline:**
1. ✅ Agent reads the current UTC block from the calendar.
2. ✅ Agent extracts all rule tokens from the Rules column.
3. ✅ Agent extracts all task points from the Task Points column (split on `\|`).
4. ✅ Agent executes task points **in order** — each point is a narrative hook addressed in the lore.
5. ✅ All task points are woven into the lore output naturally — not listed mechanically.
6. ✅ Task point outcomes are saved to lore-history.md for continuity.

**Rules for task point execution:**
- Every task point listed must appear in the lore (Post 1 or Post 2).
- Task points must be addressed **naturally** — they are hooks, not bullet points.
- If a task point requires real data (weather, fishing news), the agent fetches it.
- If data is unavailable, the agent invents a plausible, in-character response.
- Task points from the previous block may be referenced for continuity.

---

## GENESIS LORE SEED RULE

### `(rule-genesis-seed)` — First Run Lore Initialisation
- On first run, if `lore-history.md` is empty or missing:
  1. Load `genesis-lore.md` (Block Topia Genesis Narrative, 3,500+ words).
  2. Write genesis lore into `lore-history.md` with a seed timestamp header.
  3. All 55 systems now have immediate access to rich lore context.
  4. Log: `[genesis] Seeded lore-history.md from genesis-lore.md.`
- On subsequent runs: genesis seed is skipped (lore-history.md already populated).
- This eliminates cold-start problems and activates all 55 systems from first click.

**Genesis lore covers (3,700+ words):**
- Main characters: Alfie "Bitcoin KiD" Blaze, Jodie Zoom 2000, Sarah "Queen P-fly", Lady-INK
- Clans: GraffPUNKS, HODL Warriors, Bald-Headed Moonboys (Sets 1 & 2), Bitcoin X Kids, Crowned Royal Moongirls
- Factions: Elder Codex-7, NULL The Prophet, Council of Chains, The Mempool, DeFi Dragons, Art Insurgency, Dream Weavers
- World-building: Block Topia geography, six epochs (1980s→Year 3030), UK urban landscape

---

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
  checks for duplicate content (by source URL, title+date, or content fingerprint),
  and inserts new data into the correct section with full source attribution.
- Unknown update types go into the `Uncategorized Updates` section — no data is lost.
- Every run appends a log entry to `GK_BRAIN_Agent_Log` for full audit trail.
- `wiki-cross-checker.py` compares the agent's saved data against the live wiki before
  merging, ensuring only genuinely missing or changed data triggers wiki edits.
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
