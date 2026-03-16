# GK BRAIN — IN-DEPTH EXPLAINER
## What This Telegram Bot & AI Agent Does, and Exactly How It Does It

> Last updated: March 15, 2026

---

## TABLE OF CONTENTS

1. [The Big Picture — What Is This?](#1-the-big-picture--what-is-this)
2. [Who Is "GK"? — The Character at the Centre](#2-who-is-gk--the-character-at-the-centre)
3. [The Universe — Crypto Moonboys Lore](#3-the-universe--crypto-moonboys-lore)
4. [How the Agent Runs — Infrastructure](#4-how-the-agent-runs--infrastructure)
5. [The Complete Run Sequence — Step by Step](#5-the-complete-run-sequence--step-by-step)
6. [The AI Brain — How Posts Are Generated](#6-the-ai-brain--how-posts-are-generated)
7. [AWAKE vs DREAM Mode](#7-awake-vs-dream-mode)
8. [The Fame Cycle System](#8-the-fame-cycle-system)
9. [The Infinite Variation Entropy System (IVES)](#9-the-infinite-variation-entropy-system-ives)
10. [The Art & Image Prompt System](#10-the-art--image-prompt-system)
11. [Clothing Uniform Rules](#11-clothing-uniform-rules)
12. [Bonnet Shape Fidelity Rules](#12-bonnet-shape-fidelity-rules)
13. [The Rule Conflict Gate (RCG)](#13-the-rule-conflict-gate-rcg)
14. [The Telegram Interaction System](#14-the-telegram-interaction-system)
15. [The 12 Slash Commands — What Each One Does](#15-the-12-slash-commands--what-each-one-does)
16. [The Memory & Continuity System](#16-the-memory--continuity-system)
17. [The Web Crawl & Canon Update System](#17-the-web-crawl--canon-update-system)
18. [Every File Explained](#18-every-file-explained)
19. [How to Set Up & Run](#19-how-to-set-up--run)
20. [Complete Data Flow Diagram (Text)](#20-complete-data-flow-diagram-text)

---

## 1. The Big Picture — What Is This?

**GK BRAIN** is a fully autonomous AI agent that runs 24 hours a day, 7 days a week, with zero human input once deployed. Every two hours it wakes up, thinks, writes, and publishes — automatically.

Specifically it does two things:

**Thing 1 — It is a lore-publishing machine.**
Every 2 hours it generates two consecutive story posts from an infinite, never-repeating narrative universe called **Crypto Moonboys**, written in the first-person voice of a real-feeling UK character known as GK (a graffiti artist, DJ, parkour runner, carp fisherman, and web3 entrepreneur). These posts are published directly to a Telegram channel, complete with detailed AI image-generation prompts for each scene. The saga is continuous — each post picks up exactly where the last one left off.

**Thing 2 — It is an interactive Telegram bot.**
Between its scheduled posts, users in the channel can send it messages. It reads them, filters them through a keyword-trigger system, and replies with AI-generated lore expansions, character bios, world-building info, and more. It also responds to 12 dedicated slash commands that give instant access to specific information about the universe.

The entire system runs on **GitHub Actions** (the free CI/CD platform built into GitHub), costs nothing to host, and requires only three secrets: a Telegram bot token, an xAI Grok API key, and a list of Telegram channel IDs.

---

## 2. Who Is "GK"? — The Character at the Centre

GK is not a fictional fantasy character in the traditional sense. He is written as a **completely real-feeling, present-tense person living in London right now**. Readers are placed directly inside his mind. Every post starts with the exact real-world UTC date and time, and a log entry number, creating the feeling that this is a live mind-log streaming in real time.

**GK's real-world identity:**
- UK graffiti artist (sprays legal and illegal walls, works with Lady-INK)
- DJ on **GraffPunks Network Radio**
- Professional-level parkour runner and solo climber
- UK carp fisherman
- Entrepreneur building the **Crypto Moonboys** NFT project

**GK's daily life as written by the agent:**
- He wakes up, makes tea, goes to Greggs, takes his VX T4 van on road tours
- He has a weekly routine: Monday is the start of the week after a recurring mural-chase dream; Tuesday/Wednesday is a van tour; Thursday is deep Moonboys writing day; Friday is rave/DJ set night; weekends are a mix of painting nights, fishing, and raving
- He has 25 known real-world girlfriends (Lady-INK is one identity; she only appears when he's about to go spray graffiti)
- He reacts to real-world news, real London weather, and real-world crypto/NFT events — all pulled live at each run

**Why this matters:** The posts feel like reading someone's actual thoughts. The AI is not writing generic fantasy content. It is method-acting a specific, detailed, consistent human being, 24/7, across thousands of posts, forever.

---

## 3. The Universe — Crypto Moonboys Lore

Inside GK's head — and particularly in his dreams — lives an entire parallel digital universe called **Blocktopia**. This is the Crypto Moonboys saga.

### The Three Meanings of "Crypto Moonboys"

The term has three distinct definitions, all simultaneously true:

1. **The real-world project** — GK's actual NFT/web3 venture, the Crypto Moonboys collection
2. **The bald-headed characters inside Blocktopia** — specific characters born within the digital city who wear bonnets and may compete in the Hardfork Games
3. **Every character in the entire NFT web3 lore saga** — the full universe of all characters

### The World of Blocktopia

**City Block Topia** is a gleaming digital-physical megacity. It has no factions in the traditional sense — just workers needed for a city to run. It is governed jointly by two elite groups:

- **Crowned Royal Moongirls** — Elite ascended women with living neon halo crowns. Run the city alongside the HODL X Warriors.
- **HODL X Warriors** — Champions who won the Hardfork Games. Defenders of the city.

Other key groups:

| Group | Description |
|---|---|
| **Bitcoin X Kids** | Three life-paths available: Space Programme, City Worker, or Escape. Most who escape regret it. |
| **OG Bitcoin Kids** | The first generation to escape Blocktopia. Many now live with regret. Their stories are cautionary tales. |
| **Bald-headed Moonboys (inside)** | Older Bitcoin Kids born inside Blocktopia. They wear any bonnet from birth. |
| **Bald-headed Wannabe Moonboys (40)** | 40 faction members from *outside* Blocktopia trying to earn entry. They are forced to wear one clan bonnet until they win. NOT the same as those inside. |
| **The Grid** | The everyday citizens of City Block Topia — workers, residents, the backbone of the city. |
| **Alien Backend** | The mysterious hyper-dimensional state-machine behind the blockchain. Non-Euclidean. Unknowable. |

### The Hardfork Games

The ultimate competition in Blocktopia. No warning, no mercy, unpredictable schedule. Three stages:

1. **Parkour Gauntlet** — Navigate the city's lethal geometry at full sprint
2. **Spray Cipher** — Encode your identity in a living mural that the chain must verify
3. **Final Hardfork** — One-on-one consensus battle: split the chain or merge it

**Prize:** Winners become HODL X Warriors and are paired with a Crowned Royal Moongirl.

### Real-World Characters Who Cross Into the Lore

Several real-world figures from GK's life appear in the saga:

- **Lady-INK** — Mixed-race, described as looking like Beyoncé. Always in black tracksuit, black trainers, black rucksack of paint. The bridge between the real world and Blocktopia. Appears in dreams as a Crowned Royal Moongirl in training.
- **Charlie Buster** — Legendary UK street artist from Leake Street Tunnel. Mentor in dreams.
- **Bone Idol Ink** — Tattoo artist. Creates living tattoo murals with Lady-INK in dreams.
- **Delicious Again Peter** — Chef who turns food into narrative graffiti concepts.
- **AI-Chunks** — An AI artist that merges real graffiti with Blocktopia digital art.
- **Jodie Zoom** — Key GraffPunks crew member.

### Official Characters from Substack

Characters confirmed in official GraffPunks Substack posts:

- **Elder Codex-7** — Last surviving Chain Scribe of the Great HODL War, Year 3008 Grid Archives
- **Chain Scribe** — Keeper of Grid Archives; records all lore and Hardfork Games history
- **The Grid** — Citizens of City Block Topia
- **Level-9** — Decrypted cosmological whitepaper level
- **Sacred Chain Ontology** — The non-Euclidean ledger mechanics behind the Alien Backend

---

## 4. How the Agent Runs — Infrastructure

### Platform: GitHub Actions

The agent is not hosted on a server. It runs entirely inside **GitHub Actions** — the free CI/CD pipeline built into every GitHub repository. A workflow file (`.github/workflows/gk-brain.yml`) defines:

- **When to run:** every 2 hours on the hour (`cron: '0 */2 * * *'`) plus a manual trigger button
- **What to run:** a single Python script (`gk-brain.py`)
- **What environment:** Ubuntu latest, Python 3.12

```yaml
on:
  schedule:
    - cron: '0 */2 * * *'   # every 2 hours, on the hour
  workflow_dispatch:          # manual trigger via GitHub Actions UI
```

Each run spins up a fresh Ubuntu virtual machine, checks out the repository, installs Python dependencies, runs the script, and then the VM is destroyed. The script takes ~30–60 seconds.

### Secrets

Three secrets are stored in the GitHub repository's Settings → Secrets:

| Secret | What it stores |
|---|---|
| `TELEGRAM_BOT_TOKEN` | The bot token from BotFather for the Telegram bot |
| `GROK_API_KEY` | The xAI API key for accessing Grok 4 Fast (the AI model) |
| `CHANNEL_CHAT_IDS` | Comma-separated list of Telegram channel/chat IDs to post to |

### Python Dependencies

```
openai          — API client used to talk to xAI's Grok model (OpenAI-compatible endpoint)
python-telegram-bot — Telegram Bot API wrapper (v22+, async)
requests        — HTTP client for web crawling
beautifulsoup4  — HTML parser for extracting text and images from crawled pages
```

### The AI Model: Grok 4 Fast

The agent uses **xAI's Grok 4 Fast** model via the OpenAI-compatible API endpoint at `https://api.x.ai/v1`. The model receives a very large prompt (typically 10,000–20,000 tokens) containing all rules, character data, lore history, and the current context. It returns up to 4,000 tokens of output: the two lore posts plus their image prompts.

---

## 5. The Complete Run Sequence — Step by Step

Every two hours, this is the exact sequence of operations inside `main_async()`:

### Step 1 — Register Bot Commands (always first)
The agent calls Telegram's `setMyCommands` API to ensure the 12 slash commands are registered with BotFather and appear in the `/` menu for all users. This happens every run to keep the menu fresh even if commands are added or changed.

### Step 2 — Process Incoming User Messages
The agent calls `getUpdates` with the last known `update_id + 1` as the offset. This fetches only messages received since the last run — so no message is ever processed twice. For each pending message:
- If it is a slash command → route to the appropriate command handler
- If it is a regular message → run through the keyword-trigger and reply-limit system
- Send the reply back to the originating chat

The last `update_id` is saved to `bot-state.json` so the next run knows where to start.

### Step 3 — Generate the Two Lore Posts
This is the main creative work. The agent:
1. Crawls the official GraffPunks Substack for new images and content
2. Determines the current post mode (AWAKE or one of three DREAM types)
3. Determines the active 6-hour fame slot (which characters headline)
4. Rolls all 10 IVES variation axes to get a unique creative context
5. Searches for a dedicated art page for the featured character(s)
6. Builds the mandatory image prompt prefix with 96% bonnet fidelity
7. Assembles the full Grok prompt (~10,000–20,000 tokens)
8. Sends to Grok 4 Fast, receives the two posts
9. Appends the new posts to `lore-history.md`

### Step 4 — Post to Telegram
Both posts are sent to all registered channel chat IDs with a 3-second delay between them.

### Step 5 — Save Persistent State
- `reply-tracker.json` — updated with any new user reply counts from Step 2
- `bot-state.json` — updated with the latest `last_update_id` from Step 2

The GitHub Actions commit that triggered this run will have committed the updated `lore-history.md` and the JSON trackers as artefacts. On the next run, these files are checked out again — this is how state persists across runs despite each run using a fresh VM.

---

## 6. The AI Brain — How Posts Are Generated

### The Prompt Architecture

The AI prompt sent to Grok is built from multiple layered sections, always in this order:

```
[1] BRAIN RULES          — brain-rules.md (all core operational rules)
[2] CHARACTER BIBLE      — character-bible.md (character + art consistency rules)
[3] MASTER CANON         — MASTER-CHARACTER-CANON.md (full character index)
[4] SUBSTACK INFO        — crawled content/images from this run
[5] LORE PLANNER         — 30-day planner, first 3,000 chars (context seed)
[6] LORE HISTORY         — last 8,000 chars of lore-history.md (7-day continuity)
[7] CURRENT TIME         — exact UTC datetime
[8] NEWS & WEATHER       — live London weather + news note
[9] POST MODE            — AWAKE / DREAM type for this run
[10] FAME SLOT           — which characters headline this 6-hour window
[11] DAY TYPE            — STRICT ROUTINE / MULTI-RANDOM / SINGLE-FOCUS
[12] VARIATION_CONTEXT   — 10 IVES axes rolled for this post
[13] ART CREATION RULE   — mandatory image prompt prefix + fidelity rules
[14] RULE CONFLICT GATE  — 5 checks to run before generating
[15] INSTRUCTIONS        — exact output format (2 posts, separator, image prompts)
```

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
3. **Detailed image prompt** — A complete Grok Imagine / DALL-E / Midjourney prompt for generating a scene illustration, always starting with the mandatory art prefix (see Section 10)

---

## 7. AWAKE vs DREAM Mode

The agent determines which mode to use by checking the **real UTC clock** at the moment of each run. This is not a setting — it is computed live every time.

### DREAM Window: 23:00–06:00 UTC

During these hours, posts are dream sequences. There are three distinct dream types:

#### Dream Type 1 — Monday 6am Wake-Up
**When:** Monday at exactly 06:00 UTC  
**What:** The recurring unfinished-mural chase dream. He wakes with "what the hell? why?". Always the same dream but written uniquely each time. The first awake post after it continues directly from lore-history.md.

#### Dream Type 2 — Thursday Night Lady-INK World Train Adventure
**When:** Thursday 23:00 UTC through Friday 06:00 UTC  
**What:** A completely new dream about him and Lady-INK travelling the world and painting graffiti on trains. There is a library of 25 unique adventures (Orient Express, Trans-Siberian Railway, Shinkansen, etc.). The agent checks lore-history.md to find which adventures have already been told and uses the next unused one. After all 25, new ones are generated inspired by the last 25. This dream contains **no Crypto Moonboys lore** — it is purely the real-world travel painting adventure.

#### Dream Type 3 — Crypto Moonboys Lore Dream
**When:** All other nights during the dream window  
**What:** A unique Crypto Moonboys dream featuring 1 or 2 main characters as headliners. 80% completely unique fantasy. No real-world daily-life content. Character pairings are tracked in lore-history.md so no pairing is ever repeated.

### AWAKE Window: 06:00–23:00 UTC

During these hours, posts are first-person real-life mind-logs. The agent must include:
- At least one current world news event, weather update, or holiday/seasonal reference
- At least one real daily life moment (van tour, parkour, fishing, rave, painting night, Lady-INK meet, etc.)
- At least one raw sensory detail (paint smell, cold van, burnt toast, river mud smell)
- Real-life reactions to things happening right now

Two sub-types of awake posts exist:

**WINDOW 1 — Artist at home working on Moonboys lore**  
Used when it is Thursday 09:00–17:00 UTC. GK is at his desk, actively expanding the saga. Full Crypto Moonboys fame run with the active fame slot characters.

**AWAKE REAL-LIFE WINDOW**  
All other awake hours. Focus is on real daily life. A Moonboys fame run only happens if the lore explicitly places him at home writing.

---

## 8. The Fame Cycle System

The 24-hour UTC day is divided into **four 6-hour fame slots**:

| Slot | Hours (UTC) |
|---|---|
| SLOT-A | 00:00–06:00 |
| SLOT-B | 06:00–12:00 |
| SLOT-C | 12:00–18:00 |
| SLOT-D | 18:00–24:00 |

At the start of each slot, the agent assigns **1 to 3 headliner characters** from the Crypto Moonboys universe for that slot's fame run. The actual selection is delegated to Grok — the AI checks lore-history.md for recently featured characters and ensures no character headlines two consecutive slots.

Within each slot, **80% of the posts** must focus on those headliner characters (their thoughts, powers, arc, current situation). The remaining **20%** may weave in real-world news, sensory moments, or the artist's reactions.

The fame run only appears inside the **correct lore window**:
- WINDOW 1 — when GK is awake at home writing (Crypto Moonboys content in daytime)
- WINDOW 2 — when GK is asleep dreaming (Crypto Moonboys content in dream-mode)

---

## 9. The Infinite Variation Entropy System (IVES)

This is the system that ensures no two lore posts ever feel the same — and that this guarantee holds for at least 5 years of continuous output.

### The Problem It Solves

Without a variation system, an AI generating content from a fixed ruleset will eventually find patterns. The same locations, the same narrative styles, the same emotional registers will begin to repeat. With ~2,600 posts per year (2 posts × 12 runs/day × 365 days), repetition would become noticeable within months.

### The Solution: 10 Independent Axes

At the start of every lore generation, the agent independently rolls each of 10 "axes" (think of each as a dice with N sides). The combination of these 10 rolls creates the `VARIATION_CONTEXT` block injected into the prompt as creative direction for that specific post.

| Axis | Options | Example values |
|---|---|---|
| A — Perspective | 10 | "First-person artist mind-log", "Chain Archive log entry (Elder Codex-7 voice)", "Letter from Lady-INK" |
| B — Location | 15 | "Leake Street Tunnel", "Alien Backend hyper-space", "Night fishing spot", "Wannabe Moonboys' border camp" |
| C — Time of day | 8 | "3am dark", "Golden hour", "Noon blaze" |
| C — Weather | 10 | "Heatwave shimmer", "Thunderstorm rolling in", "Aurora / Northern Lights" |
| D — Emotional register | 15 | "Triumph", "Paranoia", "Dark humour", "Exhausted but proud" |
| E — Lore theme | 20 | "Betrayal hint", "New bonnet reveal", "OG Bitcoin Kids regret arc", "Return to Blocktopia" |
| F — Narrative structure | 10 | "Opens in action, ends in reflection", "Technical chain archive format", "Stream of consciousness" |
| H — Art style | 10 | "Black charcoal pencil sketch", "Blueprint schematic style — Alien Backend", "Glitch-art digital distortion" |
| I — Scene intensity | 9 | "Quiet and intimate", "Epic and cinematic", "Comedic and absurdist" |
| J — Wild card | 10 + skip | "Lady-INK leaves a coded message", "The Alien Backend glitches and leaks a future event", skip |

**Total mathematical combinations:**
`10 × 15 × 8 × 10 × 15 × 20 × 10 × 10 × 9 × 11 = ~178 billion unique posts`

At 2,600 posts per year, it would take approximately **68 million years** to exhaust the combination space.

### Anti-Repeat Filters

Even within this vast space, the agent runs additional checks:
- **IVES-2**: Before generating, check the last 10 posts in lore-history.md. If any rolled combination matches more than 5 of those 10 posts' axes simultaneously, re-roll the clashing axes.
- **IVES-3**: No character may headline two posts in a row. No supporting character may appear more than once in every 3 posts.
- **IVES-4**: Every 30 posts, add 2 new sub-options to 2 randomly selected axes, permanently growing the space.

### Important: IVES is guidance, not override

The VARIATION_CONTEXT block in the prompt is labelled as **suggestions**. If any rolled axis would create a continuity break (e.g. placing a character who is currently mid-arc in an incompatible scene), the agent adjusts only that axis. The lore continuity always wins.

---

## 10. The Art & Image Prompt System

Every post includes a detailed **image generation prompt** for creating the visual scene. This is not a decorative add-on — it is a precise technical specification for any AI image generator (Grok Imagine, Midjourney, DALL-E, etc.).

### The Dedicated Page Search (AC-1 through AC-4)

Before every image is generated, the agent searches for a **sole dedicated webpage** for the specific character, bonnet, or theme featured in the post.

The search process:
1. Check `lore-history.md` for previously cached dedicated page URLs for this character
2. If not cached, crawl all official GraffPunks links in sequence (Substack first, then the full list)
3. For each page: score how many times the character's name tokens appear in the page text
4. A page scores as "dedicated" if it mentions the subject **at least 3 times**
5. If a dedicated page is found: extract up to 6 reference images from it
6. Log the found URL in `lore-history.md` under "DEDICATED ART PAGES FOUND"

**Official links crawled (in priority order):**
- `https://substack.com/@graffpunks/posts` ← always first
- `https://graffpunks.substack.com/`
- `https://graffpunks.live/`
- `https://graffitikings.co.uk/`
- `https://gkniftyheads.com/`
- `https://medium.com/@GKniftyHEADS`
- `https://medium.com/@graffpunksuk`
- `https://neftyblocks.com/collection/gkstonedboys`
- `https://www.youtube.com/@GKniftyHEADS`

### The Mandatory Image Prompt Prefix

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
- The dedicated webpage URL + key image URLs (if a dedicated page was found)
- "Layer 1 upper body base + Layer 2 GraffPUNKS bonnet shape (rounded yellow head/torso, exact eagle beak centre, eagle birds each side, white feathers above eyes, green hair pulled through, yellow leather, ears out sides)" (if no dedicated page found)

### Random Face Expressions (AC-8)

The agent randomly selects from a pool of 20 expressions to ensure every image has a different emotion:

> surprised with wide eyes · grinning wide · squinting focused · jaw dropped · smirking sly · eyes wide in awe · brow furrowed serious · cackling · winking · thousand yard stare · tongue out cocky · grimacing · gleaming smile · nostril flared furious · dreamy half-closed · teeth gritted · soft nostalgic half-smile · manic wide grin · tears streaming but smiling · hollow exhausted thousand-stare

---

## 11. Clothing Uniform Rules

Every character has an **official faction main uniform**. This is the default visual state for every image, forever — until an exception is explicitly triggered.

### The Default Rule (UF-0)

> If the lore post does NOT mention, hint at, or imply any exception trigger, the character MUST be depicted in their full official faction main uniform.

No creative substitution is allowed under UF-0. The agent cannot decide "this scene feels casual, let's change the outfit." Only a specific named trigger can override the uniform.

### The 8 Exception Triggers

| Trigger | When it fires | What it allows |
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

| Character/Faction | Default Uniform |
|---|---|
| Crowned Royal Moongirls | Signature living-neon-halo crown (bonnet), regal faction outfit, faction colours |
| HODL X Warriors | Battle-ready champion gear, faction insignia, champion helm bonnet |
| Bitcoin X Kids (Space path) | Space suit with faction patch, visor-integrated bonnet |
| Bitcoin X Kids (City path) | City utility uniform, tool vest, hardhat-integrated bonnet |
| Bitcoin X Kids (Escape path) | Street-ready worn freedom gear, traveller's bonnet |
| OG Bitcoin Kids | First-generation street gear, faded and weathered, original first-gen bonnet |
| Wannabe Moonboys (40) | Near-uniform aspiring gear, unearned bonnet variant |
| Lady-INK | Black tracksuit + black trainers + black rucksack. **Always.** |
| GraffPunks crew | Real-world street artist clothes as established in canon |

### Auto-Reset and Continuity Bridge

- All one-post exceptions (UF-1, UF-2, UF-3, UF-5, UF-7) **automatically reset** to the main uniform on the next post unless the same trigger is still active
- If any uniform change would create a continuity break without explanation, the agent adds a brief in-universe bridge sentence explaining the change (UF-12)

---

## 12. Bonnet Shape Fidelity Rules

Every character has a head bonnet. The bonnet is the single most visually important identity element — it is how characters are recognisable in art across thousands of posts.

### The 96%/4% Rule (BF-1 and BF-2)

**96% is locked.** The core silhouette and all primary 3D structural elements of the bonnet must be 96% identical to the reference across every single image — forever. This includes:
- Overall bonnet outer silhouette shape
- Position and form of all 3D elements (eagle beak, wings, crown structures, etc.)
- Relative proportions of all major bonnet parts
- Material type (leather, neon mesh, steel, etc.)

**4% is creative freedom.** The only things that can vary:
- Extra unique surface patterns (new chain links, pixel motifs, micro-engravings)
- Minor decorative additions that do not alter the silhouette (tiny new badge, a lore-relevant detail)
- Texture refinements (more worn, more glowing, weather-affected)
- Colour tint variations within the established palette

**NOT permitted in the 4% zone:** changing the overall shape, removing any primary structural element, adding a new major structure (new horn, new wing pair), or changing the bonnet category entirely.

### The Mandatory 6-Point Bonnet Checklist (BF-5)

For every image prompt, the agent must explicitly name and lock all 6 of these elements:

1. **Primary shape type** (e.g. "crown structure", "helm base", "cap-forward brim")
2. **Central feature** (e.g. "eagle beak dead centre", "neon crown arc apex")
3. **Side features** (e.g. "eagle wing pair each side", "warrior spike pair")
4. **Upper features** (e.g. "white feathers above eyes", "neon halo glow ring")
5. **Material** (e.g. "yellow leather", "polished steel", "living neon mesh")
6. **Hair/ear integration** (e.g. "green hair pulled through", "ears visible out sides")

### The GraffPUNKS Base Bonnet (Layer 2)

When no dedicated character page exists, all bonnets default to the Layer 2 GraffPUNKS base shape:
> Exact eagle beak centre, eagle birds each side, white feathers above eyes, green hair pulled through, yellow leather material, ears visible out the sides.

### No-Bonnet Fallback Protocol (BF-3)

If a character has no known bonnet (new character, no official data yet), the agent does not skip or leave it blank. Instead:

1. Scans all known character bonnets in lore-history.md and the character bible
2. Selects 2–3 most thematically appropriate existing bonnets as inspiration
3. Creates a new unique bonnet that borrows **1 structural element** from each inspiration + introduces **at least 1 completely original element** specific to this character's persona
4. Logs this as `TEMP BONNET — [CHARACTER NAME] — awaiting official data` in lore-history.md
5. Uses this temporary bonnet at 96% fidelity in all posts for this character until official data is found

When official data arrives, the temporary bonnet is retired, the official bonnet is locked in at 96%, and a single lore post acknowledges the "evolution/reveal" in-universe.

---

## 13. The Rule Conflict Gate (RCG)

The Rule Conflict Gate is a safety mechanism that runs before every lore and art generation. Its purpose: prevent new or updated rules from breaking the infinite lore flow.

### Triple-Check Protocol (RCG-1)

Before any rule is applied, the agent verifies three things:

**CHECK 1 — Accuracy:** Is this rule still accurate based on the latest crawled data? If the 2-hour crawl found conflicting official data, update the rule first.

**CHECK 2 — Consistency:** Does applying this rule produce output consistent with the last 7 days of lore history? If not, soften it to a strong suggestion for this post and add a lore-coherent bridge sentence.

**CHECK 3 — Flow:** Does this rule make the lore feel organic and alive, or mechanical and forced? If mechanical, find the most natural way to honour the rule's intent while maintaining the mind-log voice.

### Three-Level Conflict Severity (RCG-3)

| Level | Condition | Agent Response |
|---|---|---|
| **Level 1 — Minor** | Small detail mismatch (wrong hat in one scene) | Fix silently, log in lore-history.md, continue |
| **Level 2 — Moderate** | Would require noticeable retconning | Add in-universe bridge line, log fix, continue |
| **Level 3 — Major** | Would fundamentally contradict an active arc or established canon fact | DO NOT apply the conflicting element. Generate without it. Log "RCG LEVEL-3 BLOCK" in lore-history.md. Flag for user review. |

### Rule Staleness Detection (RCG-2)

If a rule has not produced a positive lore outcome in the last 20 posts, the agent flags it as "stale" and reduces its weighting to 30% for the next 10 posts. If it still underperforms, a "RULE REVIEW NEEDED" note is logged. **Only a human can permanently remove a rule.**

### Lore Flow Test (RCG-6)

After generating lore text, the agent asks itself:  
*"If I read only the last 3 posts plus this new post, does the saga feel like a natural, living, evolving story? Or does it feel like a list of rules being executed?"*

If the answer is "list of rules": rewrite the post once, prioritising narrative voice, while still honouring all active rules.

### Human Override Gate (RCG-8)

Any rule can be manually overridden by the user at any time by posting a new instruction. The agent immediately applies it, logs it as `HUMAN OVERRIDE — [UTC timestamp]` in lore-history.md, and treats it as the new locked rule from that moment forward. Human overrides are never ignored or delayed.

---

## 14. The Telegram Interaction System

### How User Messages Are Processed

Every 2-hour run, the agent fetches all Telegram messages received since the previous run using `getUpdates`. The `last_update_id` from `bot-state.json` is used as the offset so each message is only processed once.

For each message, the routing logic is:

```
Is the message a slash command (starts with "/")?
  YES → route to process_command() → return response
        (if unknown command: fall through to keyword handling)
  NO  → route to handle_user_message()
```

### The Keyword Trigger System

Regular user messages (not slash commands) must contain at least one **trigger keyword** to receive a full AI-generated reply. The trigger keyword list includes terms like: `expand`, `continue`, `moonboys`, `moonboy`, `lore`, `graffpunk`, `lady-ink`, `hardfork`, `bonnet`, `blocktopia`, `hodl`, `graffiti`, `bitcoin x kids`, `gk`, `jodie zoom`, `elder codex`, and more.

**If no keyword is found:**
- 1st failure: replies "sorry please say the magic words"
- 2nd failure: replies with 💩 emoji
- After 2 failures in one day: **silence until midnight UTC reset**

**If a keyword is found:** the agent calls Grok to generate a 200–500 word AI reply in the artist's mind-log voice, drawing on the full canon and lore history for continuity.

### Rate Limiting

- **Max 20 replies per user per 24 hours** (resets at midnight UTC)
- After 20 replies, all further messages from that user are silently ignored until midnight
- Slash commands **bypass** the keyword gate and do NOT count against the 20/day limit
- The daily count per user is stored in `reply-tracker.json` with the date, so it resets automatically

---

## 15. The 12 Slash Commands — What Each One Does

All 12 commands are registered with BotFather on every run. They appear in the `/` menu in Telegram.

### Static Commands (instant, no AI call needed)

| Command | Response |
|---|---|
| `/start` | Welcome message: explains the bot, links to `/help` and `/lore`, sets the mood — "The infinite saga is live." |
| `/factions` | Describes all 6 factions (Crowned Royal Moongirls, HODL X Warriors, Bitcoin X Kids, OG Bitcoin Kids, Bald-headed Wannabe Moonboys, The Grid) with emoji headers |
| `/hardfork` | Explains the Hardfork Games: 3 stages (Parkour Gauntlet, Spray Cipher, Final Hardfork), prize (becoming HODL X Warrior + Crowned Royal Moongirl pairing) |
| `/links` | Lists all 8 official GraffPunks links with emoji (Substack, graffpunks.live, Graffiti Kings, GKniftyHEADS, Medium ×2, NeftyBlocks, YouTube) |
| `/artrule` | Full explanation of the locked art creation rule: 96% bonnet fidelity, 4% creative zone, clothing uniform lock, UF exception triggers, no-bonnet BF-3 fallback, the mandatory image prompt prefix |
| `/characters` | Lists all main characters with one-line descriptions, groups, and tells users to use `/about [name]` for full bios |

### Live-Computed Commands (calculated from current state, no AI call)

| Command | Response |
|---|---|
| `/help` | Complete formatted list of all 12 commands, organised by category (Lore & Content / World Info / Art / Links & Status / Help). Includes rate limit note. |
| `/status` | Current UTC time, post mode (AWAKE/DREAM type), and active fame slot. Also confirms the 2-hour schedule and art crawl status. |
| `/whosnext` | The name of the next 6-hour fame slot (SLOT-A/B/C/D) and how many hours until it starts. Explains that 1–3 characters will be headlining. |

### AI-Generated Commands (calls Grok, ~5–10 seconds)

| Command | Response |
|---|---|
| `/lore` | Returns the most recent lore post entry from `lore-history.md` (up to 3,800 chars), with a note to use `/expand` to continue |
| `/expand` | Asks Grok to continue the most recent lore post by 200–300 words in mind-log style, then first person, as if the artist is expanding the saga in real time |
| `/about [name]` | Asks Grok for a 150-word punchy Eternal Codex bio for the named character. If the character is not in the canon, Grok says so and suggests a similar one. Usage: `/about LadyINK` or `/about ElderCodex7` |

---

## 16. The Memory & Continuity System

### lore-history.md — The Long-Term Memory

Every post generated by the agent is immediately appended to `lore-history.md` in this format:

```
--- NEW POSTS 2026-03-15 12:00 UTC | MODE: POST MODE: AWAKE | ACTIVE 6-HOUR FAME SLOT: SLOT-C | DAY TYPE: MULTI-RANDOM ---
Post 1:
[full post 1 text]
Post 2:
[full post 2 text]
```

The agent loads the **last 8,000 characters** of this file into every Grok prompt. This gives the AI approximately 7 days of recent lore as context — enough to maintain perfect continuity. The AI knows what happened yesterday, who GK was with, what the weather was, which characters appeared in last night's dreams, which arcs are active.

This file also contains:
- `[DEDICATED ART PAGE] charactername: URL` — cached art page URLs
- `RULE HISTORY — [RULE ID]` — archived old rule versions
- `RULE UPDATED — [RULE ID]` — update logs with UTC timestamps
- `RCG LEVEL-3 BLOCK` — blocked conflict entries for user review
- `CONFLICT LOG` — all RCG actions
- `IVES EXPANSIONS` — new axis options added every 30 posts
- `TEMP BONNET — [CHARACTER NAME]` — temporary bonnet designs

### bot-state.json — Update ID Persistence

```json
{"last_update_id": 12345678}
```

This simple file stores the last processed Telegram `update_id`. Without it, every 2-hour run would re-process all messages from the past. With it, each message is processed exactly once.

### reply-tracker.json — Rate Limit Memory

```json
{
  "123456789": {"date": "2026-03-15", "count": 3, "failed_attempts": 0},
  "987654321": {"date": "2026-03-15", "count": 20, "failed_attempts": 2}
}
```

Stores per-user reply counts and failure counts, keyed by Telegram user ID. The `date` field enables automatic midnight UTC reset — if the stored date doesn't match today, the record is reset to zero.

---

## 17. The Web Crawl & Canon Update System

### Priority Crawl Order

Every run, before any content is generated, the agent crawls official sources in this order:

1. **Substack** (`https://substack.com/@graffpunks/posts`) — **always first**
2. All other official GraffPunks links in the `OFFICIAL_ART_LINKS` list

### What It Looks For

- New text content about characters, factions, lore
- New images (reference images for art generation)
- Dedicated pages for specific characters (AC-1 through AC-4)
- Anything that conflicts with previously stored agent-created content

### The Override Rule (Adaptive Rule)

> Any new official online content for real people/characters found on official links = **immediate scrap of agent-made content** and switch to the new official data.

This is the highest-priority rule in the system. It means:
- If GK posts a new character design on Substack, the agent's temporary version is deleted immediately
- The new official look is locked in at 96% fidelity from that moment forward
- Old data is archived in lore-history.md (not permanently deleted) for historical reference
- A single lore post acknowledges the "evolution/reveal" in-universe

### The 2-Hour Crawl Interval

The crawl happens every 2 hours because that is when the GitHub Actions workflow runs. There is no persistent background process — the crawl is part of each scheduled run. This means the agent is always working with information that is at most 2 hours stale.

---

## 18. Every File Explained

| File | Purpose |
|---|---|
| `gk-brain.py` | **The entire agent.** All Python code: Grok API calls, Telegram posting, command handlers, art system, IVES system, fame cycle, post mode logic, web crawling, reply handling. Everything runs from here. |
| `brain-rules.md` | **All operational rules.** Core identity, posting schedule, AWAKE/DREAM rules, weekly routine, random daily moments, Lady-INK rules, Telegram user interaction rules, art creation rules (AC-1–AC-14), clothing uniform rules (UF-0–UF-12), bonnet fidelity rules (BF-1–BF-5), IVES entropy system (IVES-1–IVES-5), Rule Conflict Gate (RCG-1–RCG-8). Loaded into every Grok prompt. |
| `character-bible.md` | **Character visual consistency rules.** Character descriptions, art layers, the mandatory image prompt prefix, layer reference templates, clothing uniform quick-reference, bonnet 3D element checklist, no-bonnet fallback. Loaded into every Grok prompt. |
| `MASTER-CHARACTER-CANON.md` | **Complete character index.** Every character in the Crypto Moonboys universe — all tiers, factions, timeline. Loaded into every Grok prompt and used for `/about` command bios. |
| `lore-planner.md` | **30-day content calendar.** March 14 – April 12 broken into 2-hour UTC slots, each with a suggested theme/content seed. The agent loads the first 3,000 characters of this as a context seed for the current slot. |
| `lore-history.md` | **The infinite memory.** Appended to after every run. Contains all previous posts in dated blocks. The last 8,000 characters are loaded into every Grok prompt for 7-day continuity. Also stores: cached art page URLs, bonnet logs, rule history, IVES expansions, conflict log. |
| `reply-tracker.json` | **Per-user rate limit store.** JSON object mapping Telegram user IDs to their daily reply count, date, and failed keyword attempts. Auto-resets at midnight UTC. |
| `bot-state.json` | **Telegram update ID store.** Persists the last processed `update_id` so no message is ever processed twice across 2-hour run gaps. |
| `.github/workflows/gk-brain.yml` | **The scheduler.** GitHub Actions workflow that triggers every 2 hours. Installs Python dependencies, injects secrets, runs `gk-brain.py`. |
| `README.md` | **Quick documentation.** Agent roles, run sequence, lore details summary, file structure, command list, setup instructions. |
| `AGENT-EXPLAINER.md` | **This file.** In-depth technical and conceptual explanation of the entire system. |

---

## 19. How to Set Up & Run

### Prerequisites

1. A GitHub account with this repository forked or cloned
2. A Telegram bot token (create via `@BotFather` on Telegram — `/newbot`)
3. An xAI API key for Grok (sign up at `https://x.ai`)
4. One or more Telegram channel/group IDs to post to
   - Add the bot as an admin to your channel
   - Get the channel ID (use `@userinfobot` or the Telegram API)

### Step 1 — Add Secrets to GitHub

Go to your repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these three secrets:

| Name | Value |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Your BotFather token, e.g. `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11` |
| `GROK_API_KEY` | Your xAI API key |
| `CHANNEL_CHAT_IDS` | Comma-separated channel IDs, e.g. `-1001234567890,-1009876543210` |

### Step 2 — Enable GitHub Actions

Go to your repository → **Actions** tab. If Actions are disabled, click **"I understand my workflows, go ahead and enable them"**.

### Step 3 — Test Run

Go to **Actions** → **GK BRAIN - 2 Hour Lore + Replies** → **Run workflow** → **Run workflow**.

Watch the run complete. The logs will show:
```
GK BRAIN running at 2026-03-15 12:00:00+00:00
✅ Bot commands registered
✅ Incoming updates processed
✅ Post 1 sent
✅ Post 2 sent
```

Check your Telegram channel — two posts should appear within 30 seconds.

### Step 4 — Automatic Running

After the first manual test, the cron schedule takes over automatically. The agent will post every 2 hours on the hour without any further human input.

### Adding a New Character

Edit `MASTER-CHARACTER-CANON.md` to add the character's full Eternal Codex entry. The agent will begin including them in fame cycle rotation on the next run.

### Updating Rules

Edit `brain-rules.md` directly. All rules changes take effect on the next run. Any change that conflicts with established lore will be handled by the Rule Conflict Gate (see Section 13).

---

## 20. Complete Data Flow Diagram (Text)

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
         │ MASTER-CANON     │      └──────────────────┘      └─────────────┘
         │ lore-history     │               │
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
                              │  • Art prefix             │
                              │  • RCG conflict gate      │
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
                  updated files back to repo
                          │
                          ▼
                  VM destroyed. Next run in 2 hours.
```

---

*This document is the complete in-depth reference for the GK BRAIN system. For quick reference, see `README.md`. For all operational rules, see `brain-rules.md`. For character data, see `MASTER-CHARACTER-CANON.md`.*
