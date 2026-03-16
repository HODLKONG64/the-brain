# MEGA WHITE PAPER — GK BRAIN: THE INFINITE CRYPTO MOONBOYS MIND-LOG SYSTEM
## Technical Specification & Full Reconstruction Guide
### Part 1 of 2: Architecture, Rules, Infrastructure & Creative Engine

**Version 1.0 — March 2026**
**Author:** The GK BRAIN Development Team (based on 100% of user specifications)
**Repository:** HODLKONG64/the-brain
**Continued in:** GK-BRAIN-WHITE-PAPER-PART2.md

---

## TABLE OF CONTENTS (Part 1)

1. [Abstract](#1-abstract)
2. [Vision & Purpose](#2-vision--purpose)
3. [System Architecture Overview](#3-system-architecture-overview)
4. [Core Identity & Lore Style](#4-core-identity--lore-style)
5. [Posting Schedule](#5-posting-schedule)
6. [Post Format Master Rule](#6-post-format-master-rule)
7. [AWAKE Posts — Full Micro-Rules](#7-awake-posts--full-micro-rules)
8. [DREAM Posts — Full Micro-Rules](#8-dream-posts--full-micro-rules)
9. [Weekly Routine](#9-weekly-routine)
10. [The 6-Hour Fame Cycle](#10-the-6-hour-fame-cycle)
11. [The Infinite Variation Entropy System (IVES)](#11-the-infinite-variation-entropy-system-ives)
12. [The Art & Image Prompt System (AC-1 through AC-14)](#12-the-art--image-prompt-system-ac-1-through-ac-14)
13. [Clothing Uniform Fidelity Rules (UF-0 through UF-12)](#13-clothing-uniform-fidelity-rules-uf-0-through-uf-12)
14. [Bonnet Shape Fidelity Rules (BF-1 through BF-5)](#14-bonnet-shape-fidelity-rules-bf-1-through-bf-5)
15. [The Rule Conflict Gate (RCG-1 through RCG-8)](#15-the-rule-conflict-gate-rcg-1-through-rcg-8)
16. [The AI Brain — How Posts Are Generated](#16-the-ai-brain--how-posts-are-generated)
17. [GitHub Actions Infrastructure](#17-github-actions-infrastructure)
18. [File Structure & Purpose](#18-file-structure--purpose)
19. [Complete Execution Sequence](#19-complete-execution-sequence)
20. [Complete Data Flow Diagram](#20-complete-data-flow-diagram)

*For characters, factions, universe timeline, interaction system, lore planner, and setup guide — see Part 2.*

---

## 1. Abstract

The **GK BRAIN** is a fully autonomous, self-updating AI agent that operates a Telegram channel as a living, never-ending 24/7 mind-log of a single real-feeling UK graffiti artist who is simultaneously a DJ on GraffPUNKS Network Radio, pro parkour & solo climber, UK carp fisherman, and entrepreneur building the Crypto Moonboys NFT/web3 saga.

It posts exactly **2 back-to-back lore messages every 2 hours** (maximum-length text + 1 image each), maintains perfect **7-day continuity**, rotates every character's **6-hour fame cycle**, weaves in real-world news/weather/holidays, handles intelligent user interactions (max 20 per user per day with keyword triggers), and automatically learns new canon from official Substack sources.

The entire experience is designed so readers feel they are literally inside the artist's head every second — experiencing his thoughts, real-life habits, raves, fishing trips, painting sessions, random daily moments, and dreams in real time.

This white paper contains everything needed for any AI agent to rebuild the complete system from scratch: architecture, all rules, file contents, execution flow, art training, interaction system, and self-updating mechanisms.

---

## 2. Vision & Purpose

### The Core Problem This System Solves

Traditional NFT lore is static, occasional, and disconnected from real life. The GK BRAIN creates an **infinite, breathing universe** that runs 24/7 forever. It blends:

- **Real-world events** (news, weather, market moves, holidays)
- **The artist's authentic daily life** (burnt toast mornings, parkour, fishing, van tours, raving, painting nights)
- **Deep fantasy lore** (Crypto Moonboys characters, Hardfork Games, Blocktopia, bonnets, Crowned Royal Moongirls)
- **Dreams** (Lady-INK train adventures on Thursdays, Moonboys-only on other nights)

The result is a channel that feels like reading the private diary of the creator himself — while every character in the saga gets their moment in the spotlight.

### The Three Meanings of "Crypto Moonboys"

The term has three simultaneous definitions, all true at the same time:

1. **The real-world project** — GK's actual NFT/web3 venture, the Crypto Moonboys collection
2. **The bald-headed characters inside Blocktopia** — specific characters born within the digital city who wear bonnets and may compete in the Hardfork Games
3. **Every character in the entire NFT web3 lore saga** — the full universe of all characters, factions, tiers, and storylines

---

## 3. System Architecture Overview

| Component | Technology / Platform |
|---|---|
| **Hosting** | GitHub Actions (free tier, runs every 2 hours + manual trigger) |
| **Core Engine** | xAI Grok API — `grok-4-fast` model for all text + image prompts |
| **Delivery** | Telegram Bot API (python-telegram-bot v22+, async) |
| **Memory — Rules** | `brain-rules.md` (all core operational rules, locked) |
| **Memory — Characters** | `character-bible.md` (visual consistency, art layers, bonnets) |
| **Memory — Canon Index** | `MASTER-CHARACTER-CANON.md` (full character index, all tiers) |
| **Memory — Continuity** | `lore-history.md` (all posts appended, 7-day window loaded) |
| **Memory — Planning** | `lore-planner.md` (30-day content calendar, 2-hour slots) |
| **Memory — Rate Limits** | `reply-tracker.json` (per-user daily interaction tracking) |
| **Memory — Bot State** | `bot-state.json` (last Telegram update_id, never reprocesses) |
| **Art System** | Layer 1 (upper body base) + Layer 2 (GraffPUNKS bonnet) + dedicated page override |
| **Variation System** | IVES — 10-axis entropy engine (~178 billion unique combinations) |

### Secrets (Stored in GitHub Repository Settings)

| Secret | Purpose |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Bot token from BotFather |
| `GROK_API_KEY` | xAI API key for Grok 4 Fast |
| `CHANNEL_CHAT_IDS` | Comma-separated Telegram channel/chat IDs |

### Python Dependencies

```
openai              — API client for xAI Grok (OpenAI-compatible endpoint)
python-telegram-bot — Telegram Bot API wrapper (v22+, async)
requests            — HTTP client for web crawling
beautifulsoup4      — HTML parser for crawled pages
```

### GitHub Actions Workflow

```yaml
name: GK BRAIN - 2 Hour Lore + Replies
on:
  schedule:
    - cron: '0 */2 * * *'   # every 2 hours, on the hour
  workflow_dispatch:          # manual trigger via GitHub Actions UI

jobs:
  gk-brain:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: pip install openai python-telegram-bot requests beautifulsoup4
      - name: Run GK BRAIN
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          GROK_API_KEY: ${{ secrets.GROK_API_KEY }}
          CHANNEL_CHAT_IDS: ${{ secrets.CHANNEL_CHAT_IDS }}
        run: python gk-brain.py
```

Each run spins up a fresh Ubuntu VM, checks out the repository (which includes all persistent state files), runs `gk-brain.py` (~30–60 seconds), then the VM is destroyed. State persists because `lore-history.md`, `reply-tracker.json`, and `bot-state.json` are committed back to the repository after each run.

---

## 4. Core Identity & Lore Style

The entire infinite lore is the live 24/7 thoughts and mini-stories of **ONE real-feeling person**:

> A UK graffiti artist who is also a DJ on GraffPUNKS Network Radio, pro parkour & solo climber, UK carp fisherman, and entrepreneur building the Crypto Moonboys NFT project.

Readers experience it as if they are inside his mind every second.

**Lore time = exact real-world UTC time.** Every post starts with:

```
[Current Date] — [Current Time] UTC — GraffPunks Network Log Entry #[number]
```

There are **two and only two** post modes:

- **AWAKE** (default) — real-time daily life, real-world news, weather, and feelings
- **DREAM** (only at night) — Thursday = Lady-INK world train adventure; all other nights = Crypto Moonboys lore only; Monday 6am = repeating mural chase wake-up

---

## 5. Posting Schedule

- **2 posts every 2 hours** (back-to-back pair, on the hour)
- **Post 1:** Maximum-length lore text + 1 unique image
- **Post 2:** Direct continuation + 1 unique image

**Post 2 always ends with this exact sign-off:**

```
— End of Log Entry #[number] at [exact location] — [real date] [real time] UTC
Next up in 2 hours: [short 1-sentence teaser]
```

---

## 6. Post Format Master Rule

Every single Telegram post — whether awake or dream — **MUST** begin with the exact real-world UTC time and log entry number in this exact format:

```
[Current Date] — [Current Time] UTC — GraffPunks Network Log Entry #[number]
```

No exceptions. This anchors every post as a living timestamp, making readers feel they are inside his mind in real-time 24/7.

---

## 7. AWAKE Posts — Full Micro-Rules

Awake posts are the default mode (most of the time). They are real-time thoughts, feelings, and daily life of the UK graffiti artist.

**MR-A1 — Real-time voice**
Write in first-person present tense as if the reader is literally inside his head at this exact moment. No third-person narration. The reader should feel they are experiencing his thoughts live.

**MR-A2 — Always include real-world context**
Every awake post MUST include at least one of: current world news event, current weather, or holiday/seasonal reference (if applicable). These are non-optional anchors that keep the lore feeling real and present.

**MR-A3 — Always include a daily life element**
Every awake post MUST reference at least one real daily life moment from: van tours, parkour, solo climbing, fishing, raves, painting nights, Lady-INK meets, Greggs runs, London delays, DJ sets on GraffPunks Network Radio, Moonboys project work, or any random daily moment from the full expanded list.

**MR-A4 — Real-life reactions**
Awake posts include his live reactions to things happening around him — news he just heard, weather outside his window, something that went wrong or right, conversations, discoveries. These feel unscripted and raw.

**MR-A5 — 7-day continuity**
The next awake post after any sleep/dream sequence ALWAYS continues directly from the last 7 days of real awake life stored in `lore-history.md`. No resets. No amnesia. Perfect continuity.

**MR-A6 — Sensory details**
Every awake post must include at least one raw sensory detail: the smell of fresh paint, the cold van in the rain, burnt toast smoke in the kitchen, the river mud on his boots, the bass from speakers at a rave, rain hitting a half-finished tag. These small sensory moments make the reader feel truly inside his body and world.

**MR-A7 — Live GraffPunks alerts**
Awake posts regularly include live GraffPunks Network alerts dropped naturally into the lore: a new Substack drop, a new NFT mint, a Discord announcement, a Moonboys character debut, or community news. These always feel like he just spotted it on his phone while doing something else.

**MR-A8 — 30% out-of-home random thought moments**
When the artist is NOT at home (parkour, fishing, raving, tour, painting nights, Greggs run, London commute), 30% of those posts include a short internal thought or spoken-out-loud moment about the Moonboys project — a flash of inspiration, a character arc idea, a quick conversation with a stranger about graffiti or NFTs. These feel completely natural, like a person obsessed with their work who can't switch off, even when out.

---

## 8. DREAM Posts — Full Micro-Rules

Dream posts only occur at night. The tone shifts from real-world to surreal/fantasy.

**MR-D1 — Dreams only at night**
Dream posts only happen when the schedule places the artist asleep (23:00–06:00 UTC). No dream posts during awake hours.

**MR-D2 — Thursday night ONLY — Lady-INK world train adventure**
Every Thursday night is one unique dream about him and Lady-INK travelling the world, painting graffiti on trains. Every Thursday is a completely new unique story (different country, different train, different adventure). No Thursday story ever repeats. See the full library of 25 adventures in Part 2.

**MR-D3 — All other nights — Crypto Moonboys ONLY**
On every night that is NOT Thursday, dreams are ONLY about unique Crypto Moonboys lores. These dreams feature the wider Crypto Moonboys universe. No other dream content.

**MR-D4 — 1 or 2 headliner characters**
Each non-Thursday Moonboys dream features 1 or 2 main characters as headliners. The agent rotates through ALL characters without ever repeating the same pairing. Track used pairings in `lore-history.md`.

**MR-D5 — Monday 6am ALWAYS the same dream**
Every Monday at 6am is the SAME repeating unfinished mural chase dream — he is always chasing a mural he can never finish, waking with "what the hell? why?" This is the one recurring dream and is non-negotiable.

**MR-D6 — 80% unique fantasy**
80% of all dreams (non-Thursday, non-Monday) are completely unique fantasy — new worlds, new scenarios, new characters interacting in ways that have never happened before.

### DREAM Window: 23:00–06:00 UTC

**Dream Type 1 — Monday 6am Wake-Up**
When: Monday at exactly 06:00 UTC
What: The recurring unfinished-mural chase dream. He wakes with "what the hell? why?". Always the same dream but written uniquely each time. The first awake post after it continues directly from lore-history.md.

**Dream Type 2 — Thursday Night Lady-INK World Train Adventure**
When: Thursday 23:00 UTC through Friday 06:00 UTC
What: A completely new dream about him and Lady-INK travelling the world and painting graffiti on trains. Library of 25 unique adventures (Orient Express, Trans-Siberian Railway, Shinkansen, etc.). The agent checks lore-history.md to find which adventures have been told and uses the next unused one. After all 25, new ones are generated inspired by the last 25. This dream contains **no Crypto Moonboys lore** — purely real-world travel painting adventure.

**Dream Type 3 — Crypto Moonboys Lore Dream**
When: All other nights during the dream window
What: A unique Crypto Moonboys dream featuring 1 or 2 main characters as headliners. 80% completely unique fantasy. No real-world daily-life content. Character pairings tracked in lore-history.md so no pairing is ever repeated.

---

## 9. Weekly Routine

| Day | Schedule |
|---|---|
| **Monday** | 06:00 UTC repeating mural-chase dream wake-up + normal day + creative block |
| **Tuesday** | Normal day + 22:00 UTC departure for 2-day VX T4 graffiti van tour |
| **Wednesday** | Van tour day 2 + return home |
| **Thursday** | Normal home day + heavy Moonboys writing (09:00–17:00 UTC) + Thursday night Lady-INK train dream |
| **Friday** | Normal day + 22:00–04:00 UTC London rave (DJ set at midnight) |
| **Saturday** | Mix of: painting nights + raving + fishing + 2 random early-sleep nights |
| **Sunday** | Mix of: painting nights + raving + fishing + recovery |

At **12:00 UTC daily**: New character (or pair) assigned as next scheduled 24h headliner — this is the "12pm fame switch" referenced throughout.

---

## 10. The 6-Hour Fame Cycle

### 4 Daily Fame Slots

The 24-hour UTC day is divided into **four 6-hour fame slots**:

| Slot | Hours (UTC) |
|---|---|
| SLOT-A | 00:00–06:00 |
| SLOT-B | 06:00–12:00 |
| SLOT-C | 12:00–18:00 |
| SLOT-D | 18:00–24:00 |

### Fame Cycle Rules (FC-1 through FC-6)

**FC-1 — 3 consecutive posts per fame run**
The 6-hour fame run is delivered in exactly 3 consecutive back-to-back posts (3 × 2-hour slots).

**FC-2 — 80/20 focus split**
80% of that 6-hour block is focused on the headliner characters (their thoughts, actions, backstory, powers, or current arc). The other 20% can weave in real-world news, random moments, or the artist's reactions.

**FC-3 — Only in the 2 allowed lore windows**
Fame runs happen ONLY inside the 2 allowed Crypto Moonboy lore windows. They cannot happen during pure awake real-life posts.

**The 2 Allowed Crypto Moonboy Lore Windows:**
- **WINDOW 1 — AWAKE (at home, working on the lore):** When the artist is actively working on any part of the Moonboys lore at home. Thursday 09:00–17:00 UTC. Reader experiences his thoughts or spoken-out-loud scenes as he expands the infinity lores.
- **WINDOW 2 — DREAM (asleep, dreaming Moonboys):** When the artist is asleep and dreaming about the Crypto Moonboys universe (all non-Thursday nights during 23:00–06:00 UTC).

**FC-4 — Every character rotates through**
Every character in the entire saga (all tiers, all factions, all named individuals) rotates through the fame cycle in turn. No character is left out for more than one full rotation.

**FC-5 — Track in lore-history.md**
The agent tracks the current fame slot and which characters have recently had their run in `lore-history.md` to ensure fair, non-repeating rotation.

**FC-6 — 12pm UTC daily fame switch**
At 12:00 UTC daily, a new character (or pair) is assigned as the next scheduled 24h headliner.

---

## 11. The Infinite Variation Entropy System (IVES)

### The Problem It Solves

Without a variation system, an AI generating content from a fixed ruleset will eventually find patterns. With ~2,600 posts per year (2 posts × 12 runs/day × 365 days), repetition would become noticeable within months.

### The Solution: 10 Independent Axes

At the start of every lore generation, the agent independently rolls each of 10 "axes" (each is a dice with N sides). The combination of these 10 rolls creates the `VARIATION_CONTEXT` block injected into the Grok prompt as creative direction for that specific post.

| Axis | Options | Example Values |
|---|---|---|
| **A — Perspective** | 10 | "First-person artist mind-log", "Chain Archive log entry (Elder Codex-7 voice)", "Letter from Lady-INK" |
| **B — Location** | 15 | "Leake Street Tunnel", "Alien Backend hyper-space", "Night fishing spot", "Wannabe Moonboys' border camp" |
| **C — Time of day** | 8 | "3am dark", "Golden hour", "Noon blaze" |
| **C2 — Weather** | 10 | "Heatwave shimmer", "Thunderstorm rolling in", "Aurora / Northern Lights" |
| **D — Emotional register** | 15 | "Triumph", "Paranoia", "Dark humour", "Exhausted but proud" |
| **E — Lore theme** | 20 | "Betrayal hint", "New bonnet reveal", "OG Bitcoin Kids regret arc", "Return to Blocktopia" |
| **F — Narrative structure** | 10 | "Opens in action, ends in reflection", "Technical chain archive format", "Stream of consciousness" |
| **H — Art style** | 10 | "Black charcoal pencil sketch", "Blueprint schematic — Alien Backend", "Glitch-art digital distortion" |
| **I — Scene intensity** | 9 | "Quiet and intimate", "Epic and cinematic", "Comedic and absurdist" |
| **J — Wild card** | 10 + skip | "Lady-INK leaves a coded message", "The Alien Backend glitches and leaks a future event", skip |

**Total mathematical combinations:**
`10 × 15 × 8 × 10 × 15 × 20 × 10 × 10 × 9 × 11 = ~178 billion unique posts`

At 2,600 posts per year, it would take approximately **68 million years** to exhaust the combination space.

### Anti-Repeat Filters

**IVES-1 — Roll all 10 axes independently at the start of every generation.**

**IVES-2 — Last-10 post check:** Before generating, check the last 10 posts in `lore-history.md`. If any rolled combination matches more than 5 of those 10 posts' axes simultaneously, re-roll the clashing axes.

**IVES-3 — Character frequency filter:** No character may headline two posts in a row. No supporting character may appear more than once in every 3 posts.

**IVES-4 — Axis growth:** Every 30 posts, add 2 new sub-options to 2 randomly selected axes, permanently growing the combination space.

**IVES-5 — IVES is guidance, not override:** The VARIATION_CONTEXT block is labelled as suggestions. If any rolled axis would create a continuity break (e.g. placing a character who is currently mid-arc in an incompatible scene), the agent adjusts only that axis. **Lore continuity always wins.**

---

## 12. The Art & Image Prompt System (AC-1 through AC-14)

Every post includes a detailed **image generation prompt** for creating the visual scene.

### The Dedicated Page Search (AC-1 through AC-4)

Before every image is generated, the agent searches for a **sole dedicated webpage** for the specific character, bonnet, or theme featured in the post.

**AC-1** — Check `lore-history.md` for previously cached dedicated page URLs for this character.

**AC-2** — If not cached, crawl all official GraffPunks links in sequence (Substack first, then full list). For each page: score how many times the character's name tokens appear in the page text.

**AC-3** — A page scores as "dedicated" if it mentions the subject **at least 3 times**. If a dedicated page is found: extract up to 6 reference images from it.

**AC-4** — Log the found URL in `lore-history.md` under "DEDICATED ART PAGES FOUND".

**Official links crawled (in priority order):**
1. `https://substack.com/@graffpunks/posts` ← always first
2. `https://graffpunks.substack.com/`
3. `https://graffpunks.live/`
4. `https://graffitikings.co.uk/`
5. `https://gkniftyheads.com/`
6. `https://medium.com/@GKniftyHEADS`
7. `https://medium.com/@graffpunksuk`
8. `https://neftyblocks.com/collection/gkstonedboys`
9. `https://www.youtube.com/@GKniftyHEADS`

### Layer Reference Templates (AC-5 and AC-6)

When no dedicated character page exists, all images default to the two base layers:

**Layer 1 — Upper Body Base (AC-5)**
Rounded yellow head and torso. This is the core body shape all characters share. Non-negotiable foundation for every character image.

**Layer 2 — GraffPUNKS Bonnet Shape (AC-6)**
Exact eagle beak centre, eagle birds each side, white feathers above eyes, green hair pulled through, yellow leather material, ears visible out the sides. This bonnet shape is non-negotiable — 96% fidelity to this shape in every image.

### The Mandatory Image Prompt Prefix (AC-7)

Every image prompt **must** start with this exact prefix (built by `build_image_prompt_prefix()`):

```
Use 100% [reference source]. Head + bonnet as one inseparable unit.
Face expression: [random from 20 expressions] (matching lore mood: [theme]).
96% shape fidelity to reference — 4% creative zone for minor surface details only.
Clothing: main faction uniform unless uniform exception trigger active (see UF rules).
Bonnet 3D elements (all locked at 96%): [6-point checklist].
Colours, textures, background, and scene elements may vary freely within the 4% zone.
Scene details: [full scene description]
```

The `[reference source]` is either:
- The dedicated webpage URL + key image URLs (if a dedicated page was found), OR
- "Layer 1 upper body base + Layer 2 GraffPUNKS bonnet shape (rounded yellow head/torso, exact eagle beak centre, eagle birds each side, white feathers above eyes, green hair pulled through, yellow leather, ears out sides)" (if no dedicated page found)

### Random Face Expressions (AC-8)

The agent randomly selects from a pool of 20 expressions:

> surprised with wide eyes · grinning wide · squinting focused · jaw dropped · smirking sly · eyes wide in awe · brow furrowed serious · cackling · winking · thousand yard stare · tongue out cocky · grimacing · gleaming smile · nostril flared furious · dreamy half-closed · teeth gritted · soft nostalgic half-smile · manic wide grin · tears streaming but smiling · hollow exhausted thousand-stare

### Art Generation Additional Rules (AC-9 through AC-14)

**AC-9 — Black charcoal pencil style:** When the scene calls for it (specified by IVES axis H or the lore context), generate in black charcoal pencil on white paper style.

**AC-10 — Head + bonnet as one unit:** The head and bonnet are always treated as a single inseparable visual unit. They are never separated, obscured, or broken apart.

**AC-11 — Crawl before every post:** Always crawl official sites before generating any image to check for new dedicated pages or updated art canon.

**AC-12 — No dedicated page fallback:** If no dedicated page exists, use Layer 1 + Layer 2 as the base. Create a unique version with 96% fidelity to the base templates.

**AC-13 — Post full image prompt:** Include the full image prompt in the Telegram post text so users can generate the image themselves using any AI image tool.

**AC-14 — Scene must match lore text:** The image prompt must precisely match the scene described in the lore text — same time of day, weather, lighting, season, characters, and emotional register.

---

## 13. Clothing Uniform Fidelity Rules (UF-0 through UF-12)

### The Default Rule (UF-0)

> If the lore post does NOT mention, hint at, or imply any exception trigger, the character MUST be depicted in their full official faction main uniform.

No creative substitution is allowed under UF-0. The agent cannot decide "this scene feels casual, let's change the outfit." Only a specific named trigger can override the uniform.

### The 8 Exception Triggers (UF-1 through UF-8)

| Trigger | When It Fires | What It Allows |
|---|---|---|
| **UF-1 Holiday/Seasonal** | Christmas, Halloween, Diwali, Eid, Carnival, Bonfire Night, etc. explicitly in lore | Holiday-themed variant (same silhouette, themed colours/decorations) |
| **UF-2 Environmental Scenery** | Underwater, outer space, inside Alien Backend, volcanic zone, arctic, deep jungle, desert | Practical adaptation (space suit over uniform, underwater gear) — core uniform must still be visible |
| **UF-3 Explicit Lore Statement** | Lore text plainly states or implies a clothing change | Stated alternative allowed for that post only — resets next post |
| **UF-4 Hardfork Games Active** | Any Hardfork Games arc post | Official Hardfork combat variant (same colours, tactical layering) |
| **UF-5 Dream Sequence** | DREAM mode posts | Surreal/distorted variant (fractured textures, inverted colours, ghost layers) |
| **UF-6 New Official Data** | New official Substack/site data showing a new permanent look | New look becomes permanent default — old uniform archived |
| **UF-7 Weather/Physical** | Rain, extreme heat, snow/blizzard in lore | Practical layer added/removed (rain jacket, sleeveless variant, thermal layer) |
| **UF-8 Arc Milestone** | Character wins Hardfork Games, achieves Crowned Royal status, escapes/returns | Permanent visual upgrade — logged in lore-history.md, applied going forward |

### Faction Uniform Reference Registry (UF-11)

| Character / Faction | Default Uniform |
|---|---|
| Crowned Royal Moongirls | Signature living-neon-halo crown (bonnet), regal faction outfit, faction colours |
| HODL X Warriors | Battle-ready champion gear, faction insignia, champion helm bonnet |
| Bitcoin X Kids (Space path) | Space suit with faction patch, visor-integrated bonnet |
| Bitcoin X Kids (City path) | City utility uniform, tool vest, hardhat-integrated bonnet |
| Bitcoin X Kids (Escape path) | Street-ready worn freedom gear, traveller's bonnet |
| OG Bitcoin Kids | First-generation street gear, faded and weathered, original first-gen bonnet |
| Wannabe Moonboys (40) | Near-uniform aspiring gear, unearned bonnet variant |
| Lady-INK | Black tracksuit + black trainers + black rucksack. **Always. No exceptions unless UF-3/UF-7 triggered.** |
| GraffPunks crew | Real-world street artist clothes as established in canon |

### Auto-Reset and Continuity Bridge (UF-12)

- All one-post exceptions (UF-1, UF-2, UF-3, UF-5, UF-7) **automatically reset** to the main uniform on the next post unless the same trigger is still active.
- If any uniform change would create a continuity break without explanation, the agent adds a brief in-universe bridge sentence explaining the change.

---

## 14. Bonnet Shape Fidelity Rules (BF-1 through BF-5)

Every character has a head bonnet. The bonnet is the single most visually important identity element — it is how characters are recognisable in art across thousands of posts.

### The 96%/4% Rule (BF-1 and BF-2)

**BF-1 — 96% is locked.** The core silhouette and all primary 3D structural elements of the bonnet must be 96% identical to the reference across every single image — forever. This includes:
- Overall bonnet outer silhouette shape
- Position and form of all 3D elements (eagle beak, wings, crown structures, etc.)
- Relative proportions of all major bonnet parts
- Material type (leather, neon mesh, steel, etc.)

**BF-2 — 4% is creative freedom.** The only things that can vary:
- Extra unique surface patterns (new chain links, pixel motifs, micro-engravings)
- Minor decorative additions that do not alter the silhouette (tiny new badge, a lore-relevant detail)
- Texture refinements (more worn, more glowing, weather-affected)
- Colour tint variations within the established palette

**NOT permitted in the 4% zone:** changing the overall shape, removing any primary structural element, adding a new major structure (new horn, new wing pair), or changing the bonnet category entirely.

### No-Bonnet Fallback Protocol (BF-3)

If a character has no known bonnet (new character, no official data yet), the agent does not skip or leave it blank. Instead:
1. Scan all known bonnets in the system
2. Select 2–3 thematically appropriate ones for that character's faction/role
3. Build a new unique bonnet borrowing 1 element from each of those + 1 completely original element
4. Log as "TEMP BONNET — [CHARACTER NAME]" in `lore-history.md`
5. Replace immediately when official data is found in a crawl

### GraffPUNKS Base Bonnet Shape (BF-4 — Layer 2)

When no dedicated character page exists, all bonnets default to the Layer 2 GraffPUNKS base shape:
> Exact eagle beak dead centre, eagle birds each side, white feathers above the eyes, green hair pulled through, yellow leather material, ears visible out the sides.

### The Mandatory 6-Point Bonnet Checklist (BF-5)

For every image prompt, the agent must explicitly name and lock all 6 of these elements:

1. **Primary shape type** (e.g. "crown structure", "helm base", "cap-forward brim")
2. **Central feature** (e.g. "eagle beak dead centre", "neon crown arc apex")
3. **Side features** (e.g. "eagle wing pair each side", "warrior spike pair")
4. **Upper features** (e.g. "white feathers above eyes", "neon halo glow ring")
5. **Material** (e.g. "yellow leather", "polished steel", "living neon mesh")
6. **Hair/ear integration** (e.g. "green hair pulled through", "ears visible out sides")

96% fidelity target for all 6 elements. 4% creative zone for minor decorative additions only.

---

## 15. The Rule Conflict Gate (RCG-1 through RCG-8)

Before any post is finalised, the Rule Conflict Gate runs 5 sequential checks. If any check fails, the post is rejected and regenerated.

**RCG-1 — Post mode check:** Does the current UTC time match the intended post mode (AWAKE or DREAM)? If a DREAM post is being generated during awake hours, reject and switch to AWAKE mode.

**RCG-2 — Continuity check:** Does the post content contradict anything in the last 8,000 characters of `lore-history.md`? If a character is stated as being in a specific location or state, does this post respect that? If not, adjust the post to match the established state.

**RCG-3 — Fame slot check:** Is the featured character the correct one for this 6-hour fame slot? If not, either adjust the character or flag that a new fame slot has started.

**RCG-4 — Dream pairing check:** If this is a non-Thursday Moonboys dream, has this exact character pairing already been used? Check `lore-history.md` for used pairings. If already used, re-roll the pairing.

**RCG-5 — Uniform compliance check:** Is every character depicted in their correct default uniform unless a valid UF exception trigger (UF-1 through UF-8) is active in this post? If not, correct the image prompt.

**RCG-6 — Bonnet fidelity check:** Does the image prompt include all 6 bonnet checklist elements at 96% fidelity? If any element is missing, add it before finalising.

**RCG-7 — Sign-off check (Post 2 only):** Does Post 2 end with the exact required sign-off format (End of Log Entry #[number] at [location] — [date] [time] UTC + teaser)? If not, append it.

**RCG-8 — IVES anti-repeat check:** Do more than 5 of the 10 rolled IVES axes match any of the last 10 posts in `lore-history.md`? If yes, re-roll the clashing axes and regenerate.

---

## 16. The AI Brain — How Posts Are Generated

### The Prompt Architecture

The AI prompt sent to Grok is built from 15 layered sections, always in this order:

```
[1]  BRAIN RULES          — brain-rules.md (all core operational rules)
[2]  CHARACTER BIBLE      — character-bible.md (character + art consistency rules)
[3]  MASTER CANON         — MASTER-CHARACTER-CANON.md (full character index)
[4]  SUBSTACK INFO        — crawled content/images from this run
[5]  LORE PLANNER         — 30-day planner, first 3,000 chars (context seed)
[6]  LORE HISTORY         — last 8,000 chars of lore-history.md (7-day continuity)
[7]  CURRENT TIME         — exact UTC datetime
[8]  NEWS & WEATHER       — live London weather + news note
[9]  POST MODE            — AWAKE / DREAM type for this run
[10] FAME SLOT            — which characters headline this 6-hour window
[11] DAY TYPE             — STRICT ROUTINE / MULTI-RANDOM / SINGLE-FOCUS
[12] VARIATION_CONTEXT    — 10 IVES axes rolled for this post
[13] ART CREATION RULE    — mandatory image prompt prefix + fidelity rules
[14] RULE CONFLICT GATE   — 5 checks to run before generating
[15] INSTRUCTIONS         — exact output format (2 posts, separator, image prompts)
```

Total prompt size: typically **10,000–20,000 tokens**. Maximum output: **4,000 tokens**.

### The Output Format

Grok returns exactly two posts separated by `---POST-2---`:

```
[Post 1 lore text + image prompt]

---POST-2---

[Post 2 lore text + image prompt]
```

The agent splits on this separator, trims whitespace, and treats each as a standalone Telegram message.

### What Each Post Contains

Every post includes:
1. **UTC timestamp header** — `[Date] — [Time] UTC — GraffPunks Network Log Entry #[N]`
2. **Lore text** — The first-person mind-log narrative (typically 300–800 words)
3. **Detailed image prompt** — A complete Grok Imagine / DALL-E / Midjourney prompt for the scene, always starting with the mandatory art prefix

### The xAI Grok Model

- **Model:** `grok-4-fast`
- **Endpoint:** `https://api.x.ai/v1` (OpenAI-compatible)
- **Client initialised:** `grok = OpenAI(base_url="https://api.x.ai/v1", api_key=GROK_API_KEY)`

---

## 17. GitHub Actions Infrastructure

### When the Workflow Runs

- **Automated:** Every 2 hours on the hour via cron (`0 */2 * * *`)
- **Manual:** Any time via `workflow_dispatch` trigger in the GitHub Actions tab

### Each Run Lifecycle

1. GitHub Actions spins up a fresh Ubuntu Latest VM
2. `actions/checkout@v4` checks out the repository including all persistent state files
3. Python 3.12 is installed
4. Python dependencies are installed: `openai python-telegram-bot requests beautifulsoup4`
5. The three secrets are injected as environment variables
6. `gk-brain.py` runs (~30–60 seconds)
7. Modified files (`lore-history.md`, `reply-tracker.json`, `bot-state.json`) are committed back to the repository
8. The VM is destroyed

### State Persistence Mechanism

Because each GitHub Actions run uses a fresh VM, state is persisted by committing files back to the repository after each run. On the next run, `actions/checkout@v4` retrieves those files as they were last committed. This means:
- `lore-history.md` grows with every run (contains the full infinite memory)
- `reply-tracker.json` persists user rate limit counters across runs
- `bot-state.json` persists the last Telegram `update_id` so no message is ever processed twice

---

## 18. File Structure & Purpose

| File | Purpose |
|---|---|
| `gk-brain.py` | **The entire agent.** All Python code: Grok API calls, Telegram posting, command handlers, art system, IVES system, fame cycle, post mode logic, web crawling, reply handling. Everything runs from here. |
| `brain-rules.md` | **All operational rules.** Core identity, posting schedule, AWAKE/DREAM rules, weekly routine, random daily moments, Lady-INK rules, Telegram user interaction rules, art creation rules (AC-1–AC-14), clothing uniform rules (UF-0–UF-12), bonnet fidelity rules (BF-1–BF-5), IVES entropy system (IVES-1–IVES-5), Rule Conflict Gate (RCG-1–RCG-8). Loaded into every Grok prompt. |
| `character-bible.md` | **Character visual consistency rules.** Character descriptions, art layers, the mandatory image prompt prefix, layer reference templates, clothing uniform quick-reference, bonnet 3D element checklist, no-bonnet fallback. Loaded into every Grok prompt. |
| `MASTER-CHARACTER-CANON.md` | **Complete character index.** Every character in the Crypto Moonboys universe — all tiers, factions, 6 epochs, timeline. Loaded into every Grok prompt and used for `/about` command bios. |
| `lore-planner.md` | **30-day content calendar.** March 14 – April 12 broken into 2-hour UTC slots, each with a suggested theme/content seed. The agent loads the first 3,000 characters of this as a context seed for the current slot. |
| `lore-history.md` | **The infinite memory.** Appended to after every run. Contains all previous posts in dated blocks. The last 8,000 characters are loaded into every Grok prompt for 7-day continuity. Also stores: cached art page URLs, bonnet logs, rule history, IVES expansions, conflict log, used dream pairings. |
| `reply-tracker.json` | **Per-user rate limit store.** JSON object mapping Telegram user IDs to their daily reply count, date, and failed keyword attempts. Auto-resets at midnight UTC. |
| `bot-state.json` | **Telegram update ID store.** Persists the last processed `update_id` so no message is ever processed twice across 2-hour run gaps. |
| `.github/workflows/gk-brain.yml` | **The scheduler.** GitHub Actions workflow that triggers every 2 hours. Installs Python dependencies, injects secrets, runs `gk-brain.py`. |
| `README.md` | **Quick documentation.** Agent roles, run sequence, lore details summary, file structure, command list, setup instructions. |
| `AGENT-EXPLAINER.md` | **In-depth technical explainer.** Complete technical and conceptual explanation of the entire system (all 20 sections). |
| `gk-brain-complete.md` | **Legacy merged file.** All previous brain-rules.md + character-bible.md versions merged into one master reference. |
| `GK-BRAIN-WHITE-PAPER-PART1.md` | **This file.** Architecture, rules, infrastructure, and creative engine. |
| `GK-BRAIN-WHITE-PAPER-PART2.md` | **Part 2.** Characters, universe, factions, interaction system, lore planner, setup guide. |

---

## 19. Complete Execution Sequence

Every two hours, this is the exact sequence of operations inside `main_async()`:

### Step 1 — Register Bot Commands (always first)
The agent calls Telegram's `setMyCommands` API to ensure the 12 slash commands are registered with BotFather and appear in the `/` menu for all users. This happens every run to keep the menu fresh.

### Step 2 — Process Incoming User Messages
The agent calls `getUpdates` with the last known `update_id + 1` as the offset. This fetches only messages received since the last run — so no message is ever processed twice. For each pending message:
- If it is a slash command → route to the appropriate command handler
- If it is a regular message → run through the keyword-trigger and reply-limit system
- Send the reply back to the originating chat

The last `update_id` is saved to `bot-state.json` so the next run knows where to start.

### Step 3 — Crawl Official Sources
Crawl `https://substack.com/@graffpunks/posts` FIRST, then all other official links. Extract new content, images, and character data. Override any agent-made lore that conflicts with new official data.

### Step 4 — Generate the Two Lore Posts
1. Load `brain-rules.md` + `character-bible.md` + `MASTER-CHARACTER-CANON.md`
2. Load last 8,000 chars of `lore-history.md`
3. Determine current post mode (AWAKE or one of three DREAM types) from UTC clock
4. Determine active 6-hour fame slot + which characters headline
5. Roll all 10 IVES variation axes
6. Search for a dedicated art page for the featured character(s) (AC-1 through AC-4)
7. Build mandatory image prompt prefix with 96% bonnet fidelity (BF-5 checklist)
8. Check uniform compliance (UF-0 through UF-12)
9. Assemble full Grok prompt (~10,000–20,000 tokens)
10. Send to Grok 4 Fast, receive the two posts
11. Run Rule Conflict Gate (RCG-1 through RCG-8) — reject and regenerate if any check fails
12. Append new posts to `lore-history.md`

### Step 5 — Post to Telegram
Both posts are sent to all registered `CHANNEL_CHAT_IDS` with a 3-second delay between them.

### Step 6 — Save Persistent State
- `reply-tracker.json` — updated with any new user reply counts from Step 2
- `bot-state.json` — updated with the latest `last_update_id` from Step 2
- `lore-history.md` — updated with new posts from Step 4
- All three files committed back to the repository via GitHub Actions

---

## 20. Complete Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         GITHUB ACTIONS (every 2 hours)                       │
│                                                                               │
│  ┌──────────────┐    checkout     ┌─────────────────────────────────────┐   │
│  │  cron trigger │ ─────────────► │         gk-brain.py runs            │   │
│  └──────────────┘                 └─────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                            │
                    ┌───────────────────────┼───────────────────────┐
                    ▼                       ▼                       ▼
           Load files into RAM      Telegram getUpdates        Substack crawl
         ┌──────────────────┐      ┌──────────────────┐      ┌─────────────┐
         │ brain-rules.md   │      │ offset from       │      │ Images      │
         │ character-bible  │      │ bot-state.json    │      │ Text snips  │
         │ MASTER-CANON     │      └──────────────────┘      │ New canon   │
         │ lore-history     │               │                 └─────────────┘
         │ lore-planner     │               ▼
         └──────────────────┘    For each pending update:
                                  ┌────────────────────┐
                                  │ Slash command?      │
                                  │  YES → route to     │
                                  │   command handler   │
                                  │  NO → keyword gate  │
                                  │   + rate limit      │
                                  │   + Grok reply      │
                                  └────────────────────┘
                                          │
                                          ▼
                                  Send replies via
                                  Telegram send_message
                                          │
                                          ▼
                              ┌─────────────────────────┐
                              │  Build Grok prompt:       │
                              │  • All rules (10K tokens) │
                              │  • Lore history (8K chars)│
                              │  • Post mode + fame slot  │
                              │  • IVES variation context │
                              │  • Art prefix + RCG gate  │
                              └─────────────────────────┘
                                          │
                                          ▼
                              ┌─────────────────────────┐
                              │  Grok 4 Fast API call    │
                              │  max_tokens: 4000         │
                              └─────────────────────────┘
                                          │
                                          ▼
                              ┌─────────────────────────┐
                              │  Rule Conflict Gate      │
                              │  (RCG-1 through RCG-8)   │
                              │  Reject → regenerate     │
                              └─────────────────────────┘
                                          │
                                          ▼
                              ┌─────────────────────────┐
                              │  Parse ---POST-2---      │
                              │  Split into post1/post2  │
                              └─────────────────────────┘
                                          │
                          ┌───────────────┴──────────────┐
                          ▼                               ▼
                  Append to                     Post 1 → Telegram
                  lore-history.md               (3 sec delay)
                                                Post 2 → Telegram
                          │
                          ▼
                  Save reply-tracker.json
                  Save bot-state.json
                          │
                          ▼
                  GitHub Actions commits
                  all updated files back to repo
                          │
                          ▼
                  VM destroyed. Next run in 2 hours.
```

---

*End of Part 1. Continue reading: **GK-BRAIN-WHITE-PAPER-PART2.md** for the complete universe — characters, factions, Telegram interaction system, Lady-INK adventures, 30-day lore planner, setup guide, and reconstruction instructions.*
