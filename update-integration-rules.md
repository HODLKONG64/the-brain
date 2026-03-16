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

### `(rule-wiki-smart)` — Intelligent Smart Merge Wiki Update (Preferred)
Replaces `(rule-wiki)` as the primary wiki update strategy.
Defined fully in `wiki-merge-rules.md`. Summary:

1. After **both** Telegram posts are sent successfully, call `wiki-smart-merger.py`.
2. **Layer 1 — Smart Merge:**
   - Read current wikitext of the main wiki page (`GKniftyHEADS_Wiki`).
   - Parse existing `== Section ==` headings.
   - Map the update category to its canonical section using the table in `wiki-merge-rules.md`.
   - If the section exists: **prepend** the new entry at the top (newest first).
   - If the section is missing: **create** it and append to the page.
   - Write the updated page back via the MediaWiki API.
3. **Layer 2 — Simple Append (audit trail, always runs):**
   - Append one timestamped log line to `GK_BRAIN_Agent_Log` regardless of whether
     the smart merge succeeded.
4. **Sub-page creation:** Create a dedicated full-detail sub-page for every update at
   `GK_BRAIN_Agent_Log/YYYY-MM-DD/<category>/<Title>`.
5. **Fallback:** If `wiki-smart-merger.py` fails to import or errors out, automatically
   fall back to `wiki-updater.py` simple-append behaviour.
6. **Safety:** Never delete existing wiki content. One-time use enforced via
   `"wiki_done": true` in `wiki-update-queue.json`.

#### Category → Wiki Section Mapping
| Detected Category | Wiki Section |
|-------------------|--------------|
| `gkdata-real` | GK & GraffPUNKS Official Updates |
| `fishing-real` | Fishing Catches & Lake Adventures |
| `graffiti-news-real` | Street Art & Graffiti News |
| `news-real` | Crypto & Market News |
| `rave-real` | Raves & DJ Events |

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
3. **Try `wiki-smart-merger.py` first** (`run_smart_wiki_updates()`):
   - Smart-merge each update into the correct named section.
   - Always append audit log entry regardless of merge outcome.
4. **Fallback to `wiki-updater.py`** (`run_wiki_updates()`) if smart merger errors.
5. Mark successfully processed entries `"wiki_done": true`.
6. Delete `crawl-snapshot.json` → fresh crawl next cycle.
7. Sleep until next 2-hour cron ping.

---

## HOW SAVED WEBSITE DATA FEEDS INTO LORE

This section answers: *"Does the agent's rules tell it how to use saved new updated
data from all sites (news, fishing, etc.) to build lore from all official saved
websites listed in the GitHub files?"*

**Yes.** Every URL in `gkandcryptomoonboywebsitestosave.md` is crawled by
`update-detector.py` each cycle. When a page changes, the update is classified,
saved to `wiki-update-queue.json`, and passed to the lore generator.

### Complete Source-to-Lore Pipeline

```
gkandcryptomoonboywebsitestosave.md   (official URL list)
          │
          ▼
update-detector.py                     (crawls all URLs, detects changes)
          │
          ├── Category: gkdata-real    → radio alert or 10% lore weave
          ├── Category: news-real      → 5-10% lore weave
          ├── Category: graffiti-news-real → 5-10% lore weave
          ├── Category: fishing-real   → 5% lore mention (≥40 lb catch only)
          └── Category: rave-real      → woven into (rave) block
          │
          ▼
wiki-update-queue.json                 (saves all detected changes)
          │
          ▼
gk-brain.py  generate_lore_pair()      (builds AI prompt with update context)
          │
          ▼
Grok AI                                (generates lore with 5-10% real data)
          │
          ├── Telegram post (2 per cycle)
          └── wiki-smart-merger.py     (updates wiki sections)
```

### Per-Category Lore Rules

#### `gkdata-real` — Official GK / GraffPUNKS Data
Sources: graffpunks.substack.com, graffpunks.live, gkniftyheads.com,
graffitikings.co.uk, YouTube, Medium posts, NeftyBlocks, NFTHive, DappRadar,
X/Twitter, collaborator sites (Charlie Buster, BoneIdoLink, Delicious Again Peter,
TREEF Project, NoballGames, AI Chunks, Reddit).

- **Major update** (new NFT drop, new collection, new project announcement):
  → Format as GraffPUNKS Network Radio Alert:
    `🔴 [GRAFFPUNKS NETWORK RADIO — ALERT] :: [summary in character voice]`
- **Minor update** (new post, new image, page text change):
  → Weave into **~10% of lore**: artist reads about it, hears about it, reacts.
- Always mark as `"used": true` after one appearance.

#### `news-real` — Crypto & Breaking News
Sources: CoinDesk, CoinTelegraph, BeInCrypto, Decrypt, The Block,
Bitcoin Magazine, CryptoSlate, Blockworks.

- Extract the most relevant crypto, political, or street art story published
  within the last 2 hours.
- Weave into **~5-10% of lore**: natural character reaction
  ("caught something on the news about…", "phone lit up with…").
- Never exceed 10% of total lore text.
- Always mark as used after one appearance.

#### `graffiti-news-real` — Street Art & Graffiti News
Sources: StreetArtNews, GraffitiStreet, GraffitiArtMagazine, ArrestedMotion.

- Extract most recent street art story, contest, or artist feature.
- Weave into **~5-10% of lore**: character hears about it from a mate, sees a clip
  online, reads about it while waiting for a fishing bite.
- Only use if change detected from last snapshot. Mark as used.

#### `fishing-real` — UK Carp Fishing News
Sources: BigCarp, Carpology, TotalCarp, CarpForum, FishingMagic, Angling Direct.

- **Only use if:** extracted text contains a carp catch **≥40 lb** keyword match.
- Weave into **~5% of lore** (maximum): overheard on the bank, read on phone,
  seen on a forum post while packing up.
- Example integration: "Saw on Carpology that someone banked a 52-pounder at
  Redmire last night. Makes me think this swim might give up something similar."
- Mark as used. Do not repeat.

#### `rave-real` — UK Drum & Bass Events
Sources: Resident Advisor, Ticketmaster, Skiddle.

- Flag any new event or DJ booking in the next 30 days.
- Weave naturally into any `(rave)` calendar block.
- Use real venue name and real DJ names if available.
- Activate `(live)` rule if GraffPUNKS Network Radio is live that night.

#### `lady-ink-hint` — Lady-INK Trigger
Monitored via `gkdata-real` sources using keyword matching
(Lady-INK, female graffiti artist, street art muse).

- If keyword match found: activate `(lady-ink)` rule for this cycle.
- Lady-INK appears only in graffiti or dream blocks (see `(lady-ink)` rule above).

### Integration Ratio Rules

| Situation | Lore Composition |
|-----------|-----------------|
| Update detected (any category) | 5-10% update content + 90-95% calendar/character lore |
| No updates detected | 100% calendar-driven lore |
| Major `gkdata-real` update | Radio alert format (may exceed 10% if formatted as announcement) |

### One-Time Use Rule
- Each detected update is marked `"used": true` after it appears in **one** Telegram post.
- The same update is **never** used again in future cycles.
- `wiki-update-queue.json` is the single source of truth for used/unused updates.

### Character Epoch Rule
- Before generating lore, check all featured characters.
- Characters from 1980s London **cannot** mix with Year 3009 Blocktopia characters
  in the same lore post.
- Exception: Dream sequences (all epochs can mix in surreal dream logic).
