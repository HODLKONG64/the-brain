# THE BRAIN — GK BRAIN AGENT (Full Documentation)

This repository runs the **GK BRAIN** — an autonomous Telegram posting agent that generates the infinite Crypto Moonboys lore saga 24/7.

> 📖 **Want the full in-depth explanation?** Read **[AGENT-EXPLAINER.md](./AGENT-EXPLAINER.md)** — a complete technical and conceptual deep-dive into exactly what this bot does and how every part of it works (infrastructure, AI prompting, art rules, variation system, commands, memory, and more).

## AGENT KEY ROLES
- Live 24/7 mind-log narrator of a real-feeling UK graffiti artist/DJ/parkour climber/fisherman/entrepreneur.
- Maintains perfect 7-day awake continuity using lore-history.md.
- Crawls Substack first every run for official canon updates and overrides anything conflicting.
- Generates exactly 2 back-to-back lore posts every 2 hours (on the hour) with images.
- Handles Telegram user replies (max 20 per user per 24h, only on relevant Moonboys/GK topics).
- Enforces perfect character consistency using Layer 1 + Layer 2 + future layers.
- Updates its own memory (Crypto Moonboys bank/brain) instantly when new official data appears.

## EVERY ACTION THE AGENT TAKES EVERY 2 HOURS (exact sequence)
1. Crawls https://substack.com/@graffpunks/posts FIRST for new content/images.
2. Checks all locked links for updates.
3. Loads gk-brain-complete.md + character-bible.md + MASTER-CHARACTER-CANON.md + lore-history.md.
4. Generates 2 back-to-back lore posts (maximum length + image prompts).
5. Appends new posts to lore-history.md for 7-day continuity.
6. Posts both to the Telegram channel.
7. Saves reply-tracker.json.
8. Logs run summary.

## ALL BRAIN LORE DETAILS (100% from final files — key backup)
- **Core Identity**: Live 24/7 thoughts of one UK graffiti artist/DJ/parkour/solo climber/carp fisherman/entrepreneur building Crypto Moonboys NFT project. Every post starts with exact UTC time and log entry number.
- **Posting Schedule**: 2 posts every 2 hours (back-to-back pair on the hour). Post 1 = max-length text + 1 image. Post 2 = direct continuation + 1 image.
- **Weekly Routine**: Monday 6am repeating dream, Tuesday 10pm VX T4 van tour, Wednesday return, Thursday heavy writing, Friday rave/DJ set, **Sat/Sun mix of painting + raving + fishing + early sleep**. 12pm UTC daily character fame switch.
- **Dream Rules**: Thursday night = unique Lady-INK world train painting adventure (MR-D2). All other nights = unique Crypto Moonboys dreams (1-2 characters rotating, no repeat pairings — MR-D3/MR-D4). Monday 6am = repeating unfinished mural chase wake-up (MR-D5). 80% dreams unique fantasy (MR-D6). Wakes directly into 7-day awake continuity (MR-A5).
- **Crypto Moonboys 3 Meanings** (locked): 1. Real-world saga project. 2. Bald-headed moonboys from Blocktopia (any bonnet, Hardfork winners → HODL X Warriors with Crowned Royal Moongirl). 3. Every character in the whole NFT web3 lore saga.
- **Blocktopia & Factions**: Pre-war = no factions, just workers needed for city to run. Post-war = 40 GK Factions (outside rebellion) unify into Hash-Guilds. Inside = older Bitcoin Kids born with freedom.
- **Hardfork Games**: 3 stages (Parkour Gauntlet, Spray Cipher, Final Hardfork). Winners = HODL X Warriors, collect as many bonnets as wanted (unique powers), marry Crowned Royal Moongirl.
- **Bitcoin X Kids**: 3 paths (Space Programme, City Worker, Escape). Most escapees regret it.
- **OG Bitcoin Kids**: First generation who escaped — many now regret it.
- **Bald-headed Moonboys**: Inside (older Bitcoin Kids born in city) = wear any bonnet from birth. Outside (40 wannabe faction members) = forced to wear one clan bonnet until they win.
- **Lady-INK Rules**: Only appears when artist is going out to spray (meets hours before). All 25 detailed storylines locked + expanded.
- **Random Daily Moments**: Full expanded list (burnt toast, parkour slips, fishing bites, Greggs runs, London delays, seasonal/holiday variations) mixed every day.
- **Awake vs Dream Modes**: The agent always determines the current post mode from the real UTC time/day before generating. AWAKE = real-time daily life, news, weather, feelings (MR-A1 to MR-A5). DREAM = night-time only, type depends on day (MR-D1 to MR-D6). Mode is injected into every prompt via `get_post_mode()` in `gk-brain.py`.
- **7-Day Awake Continuity**: Agent always continues directly from last 7 days of awake events stored in lore-history.md.
- **Telegram Rules**: Max 20 replies per user per 24h. Only replies on Moonboys/GK narrative topics or requests to extend lore. Hidden keyword trigger system — first fail = "sorry please say the magic words", second fail = 💩 emoji. After 2 keyword fails per day, silence until midnight reset. Text-only replies, links allowed, no images.
- **Art Creation Rule (AC-1–AC-14 + BF-1–BF-5 + UF-0–UF-12)**: Before every image, the agent crawls official links for a page solely dedicated to the current character. Locks in head + bonnet as one visual unit with **96% shape fidelity** (4% creative zone for minor details only). All 3D bonnet elements named explicitly in prompt. Clothing always the main faction uniform unless a Uniform Exception Trigger (UF-1–UF-8) is active in the lore. Adds a random face expression matching the lore mood. If no dedicated page exists, uses Layer 1 + Layer 2 base templates. No-bonnet fallback (BF-3) creates a unique bonnet from existing character inspirations. Every image prompt starts with the mandatory prefix. New dedicated pages logged in `lore-history.md`.
- **6-Hour Fame Cycle (FC-1–FC-6)**: Every 6 hours (UTC), 1–3 characters get a fame run in 3 consecutive posts. Only inside 2 daily lore windows: WINDOW 1 = awake at home writing; WINDOW 2 = asleep dreaming. All characters rotate fairly; tracked in lore-history.md.
- **25 Lady-INK Thursday Dream Library**: 25 unique Thursday night train-painting adventures — Orient Express, Trans-Siberian, Shinkansen, etc. After all 25 used, new dreams are inspired by the last 25.
- **Day Randomisation**: Each day randomly assigned: STRICT ROUTINE, MULTI-RANDOM, or SINGLE-FOCUS. Weekly anchors never overridden.
- **Sensory Details (MR-A6)**: Every awake post includes at least one raw sensory detail (paint smell, cold van, burnt toast, river mud).
- **Live GraffPunks Alerts (MR-A7)**: Regular alert interruptions in awake posts (new drops, Substack, NFT news).
- **30% Out-of-Home Thought Moments (MR-A8)**: 30% of out-of-home posts include a flash thought or conversation about the Moonboys project.
- **Character Art Training (Layers)**: Layer 1 = upper body base (rounded yellow head/torso). Layer 2 = GraffPUNKS bonnet (exact eagle beak centre, eagle birds each side, white feathers above eyes, green hair pulled through, yellow leather, ears out sides). All future layers added on top. 100% shape fidelity enforced.
- **Adaptive Rule**: Any new official Substack data = scrap old agent-made content instantly.
- **Image Generation**: Every post includes detailed Grok Imagine prompt using Substack style + uploaded layers + exact bonnet/head shape.

## FILE STRUCTURE & PURPOSE
- `gk-brain-complete.md` → All core rules, routines, dreams, continuity, 3 meanings, etc. (merged complete brain rules file loaded by the agent).
- `character-bible.md` → Character consistency, art layers, image prompt template.
- `MASTER-CHARACTER-CANON.md` → Complete Crypto Moonboys universe character index (all tiers, factions, timeline). Loaded every run — agent auto-uses any updated canon data going forward.
- `DEEP-DIVE-AUDIT-REPORT.md` → **Comprehensive 10-section audit** of all GitHub files + all linked platforms (GKniftyHEADS Wiki, GraffPunks Substack, Medium, GraffPunks.live, collaborator sites). Last updated: March 17, 2026.
- `genesis-lore.md` → 3,700+ word Block Topia genesis seed narrative (all 55 AI systems initialise from this foundation).
- `gk-brain.py` → The actual agent code (loads files, generates posts, posts to Telegram).
- `.github/workflows/gk-brain.yml` → GitHub Actions workflow (runs every 2 hours + manual trigger).
- `lore-history.md` → Stores every post ever made for 7-day continuity.
- `lore-planner.md` → 7-day repeating calendar with 2-hour UTC slot breakdown. Agent uses matching slot as context seed each run.
- `reply-tracker.json` → Tracks Telegram reply limits per user (count, date, failed_attempts).
- `bot-state.json` → Persists the last processed Telegram update_id so commands are never replayed.
- `AGENT-EXPLAINER.md` → Full in-depth technical and conceptual explanation of the entire system (20 sections, ~50KB).

## TELEGRAM COMMANDS
All commands are registered with BotFather on every run and processed at the start of each 2-hour run.
Slash commands bypass the keyword trigger gate and do NOT count against the 20/day reply limit.

| Command | What it does |
|---|---|
| `/start` | Welcome message + quick-start guide |
| `/help` | Full list of all commands |
| `/lore` | Show the latest lore post |
| `/status` | Brain status: active fame slot, awake/dream mode, UTC time |
| `/whosnext` | Characters starring in the next 6-hour fame slot |
| `/characters` | Full character list from the Eternal Codex |
| `/factions` | All factions with brief descriptions |
| `/hardfork` | The Hardfork Games: 3 stages, rules, prize |
| `/links` | All official GraffPunks links |
| `/expand` | Continue the last lore post (200–300 words, AI-generated) |
| `/about [name]` | Eternal Codex bio for any character — e.g. `/about LadyINK` |
| `/artrule` | The locked art creation rule + mandatory image prompt prefix |

## HOW TO RUN / TEST
1. Commit all files.
2. Go to Actions tab → “GK BRAIN - 2 Hour Lore + Replies” → Run workflow.
3. First run creates lore-history.md automatically.
4. Posts appear in your Telegram channel within 30 seconds.

## BACKUP NOTES (everything from final files)
- Substack crawl is priority #1.
- All 25 Lady-INK storylines + full random moments + 7-day continuity + dream rotation locked.
- Bonnet shape 100% fixed (Layer 2) — no changes allowed.
- Agent automatically updates memory on any new official data.
- This README contains every key detail from all final files as permanent backup.

**The GK BRAIN is now fully operational and self-updating.**

## OFFICIAL LINKS — EXTERNAL CANON SOURCES

The agent checks these sources every 2 hours. They are the **official sources of truth** for all lore updates.

### GraffPunks & Crypto Moonboys
- **Substack (primary canon):** https://substack.com/@graffpunks/posts
- **GraffPunks Live:** https://graffpunks.live/
- **GKniftyHEADS Website:** https://gkniftyheads.com/
- **GKniftyHEADS Wiki (character canon):** https://gkniftyheads.fandom.com/
- **Graffiti Kings:** https://graffitikings.co.uk/
- **YouTube:** https://www.youtube.com/@GKniftyHEADS
- **Medium (@GKniftyHEADS):** https://medium.com/@GKniftyHEADS
- **X/Twitter:** https://x.com/GraffPunks

### MASTER CHARACTER CANON
> 📋 **Complete universe character index:** See **[MASTER-CHARACTER-CANON.md](./MASTER-CHARACTER-CANON.md)** — all tiers, all 40 factions, full timeline (1980s–Year 3030), real-world collaborators, publication roadmap, and cross-reference matrix. **Loaded every run — agent auto-uses any updated canon data going forward.**

### Character Groups Wiki Pages (GKniftyHEADS Fandom)
- GraffPUNKS: https://gkniftyheads.fandom.com/wiki/GraffPUNKS
- HODL Warriors: https://gkniftyheads.fandom.com/wiki/HODL_WARRIORS
- Crypto Moonboys: https://gkniftyheads.fandom.com/wiki/CRYPTO_MOONBOYS
- Gasless Ghosts & NULL The Prophet: https://gkniftyheads.fandom.com/wiki/Gasless_Ghosts_%26_NULL_The_Prophet
- Block Topia: https://gkniftyheads.fandom.com/wiki/Block_Topia
- Sacred Chain: https://gkniftyheads.fandom.com/wiki/Sacred_Chain
- Aether Chain: https://gkniftyheads.fandom.com/wiki/Aether_Chain

Last updated: March 18, 2026
