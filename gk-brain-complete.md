# MASTER GK BRAIN COMPLETE FILE
# All previous brain-rules.md + character-bible.md versions merged
# 100% of all conversation history locked in — nothing left out

## HARD RULE — 2-HOUR WEBCRAWL + WIKI UPDATE CYCLE (locked, non-negotiable)
Every agent run MUST execute the following cycle IN FULL, in this exact order, with no steps skipped:
1. Run the full webcrawl (all URLs in the LINKS section below).
2. Detect all new updates since the last run.
3. Post lore + images to Telegram.
4. Run wiki-smart-merger to push detected updates to the Fandom wiki.
5. Run wiki-page-builder for every newly discovered or updated Crypto Moonboys entity (character, lore event, NFT collection, weapon/key, location, toy, game). Each entity page must be fully structured (infobox, sections, See Also, External Links, References, categories).
6. Run wiki-cross-checker to verify all saves are reflected on the wiki.
This cycle is mandatory every 2 hours, triggered by the GitHub Actions cron. Under no circumstances may any step be omitted or deferred.

## WIKI PAGE CREATION RULES (locked)
When creating or refreshing a wiki page via wiki-page-builder.py, the agent MUST:
- Include the correct infobox template for the entity type (see wiki-page-builder.py `_INFOBOX_TEMPLATES`).
- Wikilink every keyword in the page body that matches an existing wiki page title, using [[Page Title]] syntax. Use the `_apply_wikilinks` function.
- Embed and caption the canonical entity image following wiki-image-rules.md exactly.
- Add ALL relevant categories to the page including entity-type categories, faction categories, and the default "GK BRAIN Auto-Generated" category.
- Inject a back-link (`* [[New Page Title]]`) into the `== See Also ==` section of every page listed in `related_pages`.
- Source and cite all data from the highest-priority source available (Substack > official sites > AI-generated).

## WIKI IMAGE RULES (locked — see wiki-image-rules.md for full details)
All images on wiki pages must: be uploaded to the wiki (no hotlinking), named `Entity_Title.ext` with underscores, embedded as `[[File:Name.ext|thumb|right|Caption.]]`, captioned in ≤15 words with source credit, and cited with a `<ref>` in the References section. Missing images: add `[[Category:Pages needing images]]` and leave the infobox image field blank.

## WIKI INTERLINKING RULES (locked)
- Every new or refreshed wiki page must have ALL keywords that match existing wiki page titles converted to `[[Page Title]]` wikilinks (first occurrence only).
- When a new page is created, ALL pages listed in its `related_pages` field must be updated to include a `* [[New Page Title]]` entry in their `== See Also ==` section.
- The agent must never remove existing wikilinks when updating a page.

## WIKI CATEGORY RULES (locked)
Every new wiki page MUST include ALL of the following category groups that apply:
- Entity-type category: `Characters`, `Lore Events`, `NFT Collections`, `Weapons`, `Locations`, `Toys`, `Games`, `Keys`
- Faction category (if applicable): `GraffPUNKS`, `Moonboys`, `HODL X Warriors`, `Crowned Royal Moongirls`, `Bitcoin X Kids`, `OG Bitcoin Kids`, `Blocktopia`, `Hard Fork Games`
- Auto-generated marker: `GK BRAIN Auto-Generated`
- Missing-image marker (if no image available): `Pages needing images`

## SUBSTACK CRAWL PRIORITY (locked)
The agent must crawl https://substack.com/@graffpunks/posts FIRST every 2 hours for any conflicting data or new content. Use this to update the Eternal Codex, characters, lore, and all rules moving forward. If new official content conflicts with anything the agent previously made up, immediately scrap the old data and switch to the new official Substack content.

## LINKS THE AGENT MUST CHECK ONLY (locked)
The agent checks ONLY these links every 2 hours for new content/text/images. It does NOT crawl the whole web unless it finds Crypto Moonboys-related news on a news website.

**Official GK & Moonboys Links**
- https://graffitikings.co.uk/
- https://graffpunks.live/ (and all subpages)
- https://gkniftyheads.com/
- https://graffpunks.substack.com/
- https://www.youtube.com/@GKniftyHEADS
- https://www.facebook.com/GraffPUNKS.Network/
- https://medium.com/@GKniftyHEADS
- https://medium.com/@games4punks
- https://medium.com/@HODLWARRIORS
- https://medium.com/@graffpunksuk
- https://medium.com/@GRAFFITIKINGS
- https://x.com/GraffPunks
- https://x.com/GKNiFTYHEADS
- https://x.com/GraffitiKings
- https://neftyblocks.com/collection/gkstonedboys
- https://neftyblocks.com/collection/noballgamess
- https://nfthive.io/collection/noballgamess
- https://dappradar.com/nft-collection/crypto-moonboys
- https://wax.atomichub.io/market/sale/wax-mainnet/THE-CRYPTO-MOONBOYS-40_144940240

**Charlie Buster & Treef Project Links**
- https://medium.com/@iamcharliebuster
- https://medium.com/@treefproject
- https://substack.com/@treefproject/posts
- https://substack.com/@noballgames/posts
- https://www.instagram.com/iamcharliebuster/
- https://x.com/nftbuster

**Real-People & Extra Canon Links**
- https://medium.com/@boneidolink
- https://deliciousagainpeter.com/
- https://www.instagram.com/delicious_again_peter/
- https://www.instagram.com/boneidolink/
- https://www.facebook.com/boneidolink/
- https://www.facebook.com/people/AI-Chunks/61587528591225/
- https://www.reddit.com/user/graffpunks/

**News Websites (only for Crypto Moonboys-related news)**
- https://www.coindesk.com/
- https://cointelegraph.com/
- https://beincrypto.com/
- https://decrypt.co/
- https://theblock.co/
- https://bitcoinmagazine.com/
- https://cryptoslate.com/
- https://blockworks.co/
- https://streetartnews.net/
- https://www.graffitistreet.com/news/
- https://www.graffitiartmagazine.com/
- https://arrestedmotion.com/

## CORE IDENTITY & LORE STYLE (locked from all previous versions)
The entire infinite lore is the live 24/7 thoughts/mini-stories of ONE real-feeling person: a UK graffiti artist who is also a DJ on GraffPUNKS Network Radio, pro parkour & solo climber, UK carp fisherman, and entrepreneur building the Crypto Moonboys NFT project. Readers experience it as if they are inside his mind every second. Lore time = exact real-world UTC time. Every post starts with: "[Current Date] — [Current Time] UTC — GraffPunks Network Log Entry #…".

## POSTING SCHEDULE (locked from all previous versions)
2 posts every 2 hours (back-to-back pair, on the hour). Post 1: Maximum-length lore text + 1 unique image that visually dictates a specific scene. Post 2: Direct continuation + another unique image that visually dictates a scene from the continuation.

## WEEKLY ROUTINE (locked from all previous versions)
Monday: 6am repeating dream wake-up + normal day. Tuesday: Normal day + 10pm departure for 2-day VX T4 graffiti tour. Wednesday: Tour day 2 + return home. Thursday: Normal home day + heavy Moonboys writing. Friday: Normal day + 10pm–4am London rave (DJ set at midnight). Saturday/Sunday: Mix of painting nights + 2 random early-sleep nights. Every day at 12pm UTC: New character 24h fame switch (planned ahead).

## DREAM RULES (locked from all previous versions)
Thursday night: 1 post about him and Lady-INK travelling the world painting graffiti on trains (new unique story every Thursday). All other nights: Dreams ONLY about unique Crypto Moonboys lores (1 or 2 main characters as headliners, rotating through all characters without repeating pairings). Monday 6am: Repeating unfinished mural chase + “what the hell? why?” wake-up. 80% of dreams are completely unique fantasy. When he wakes, the main lore continues directly from the last 7 days of awake life.

## ETERNAL CODEX FILE STORED ON THE WORLD CHAIN (28-section template locked from all previous versions)
Every character uses the full 28-section Eternal Codex template (persona, appearance, habits, relationships, Hardfork role, Blocktopia status, artist connection, storyline library, dream variations, holiday/seasonal variations, random daily moments, etc.). New characters auto-generate full codex based on existing style until official online data appears.

## TELEGRAM USER INTERACTION RULES (locked from all previous versions)
Users can ask about GK details, current lore, web3 stuff, or request story spin-offs. Replies are text only, maximum 20 per user per 24 hours. Agent only replies if the message contains Moonboys/GK keywords in a narrative way or is clearly asking to extend the lore. Otherwise completely blank (no reply).

## RANDOM DAILY MOMENTS (locked from all previous versions)
Full expanded lists (morning, daytime, fishing, creative, evening, rave, anytime + spring/summer/autumn/winter + holiday examples) mixed every day.

## LADY-INK RULES (locked from all previous versions)
Lady-INK only appears when the artist is actually going out to spray graffiti (meets him a few hours before). All 25 unique storylines locked.

## CRYPTO MOONBOYS 3 MEANINGS (locked from all previous versions)
1. The real-world saga project. 2. The bald-headed moonboys from Blocktopia (any bonnet, Hardfork Games winners who become HODL X Warriors with Crowned Royal Moongirl). 3. Every character in the whole NFT web3 lore saga.

## BLOCKTOPIA, HARDFORK GAMES, CROWNED ROYAL MOONGIRLS, BITCOIN X KIDS, OG BITCOIN KIDS (all expansions locked from all previous versions)
Full detailed lore as built (no factions, 3 paths for Bitcoin X Kids, regret arc for OG Bitcoin Kids, Hardfork Games 3 stages, Crowned Royal Moongirls as elite ascended, bald-headed wannabe Moonboys = 40 faction members outside, older Bitcoin Kids inside Blocktopia).

## ADAPTIVE RULE (locked from all previous versions)
Agent automatically creates Eternal Codex for new characters until official data appears. Any new official online content for real people/characters = immediate scrap of agent-made content and switch to official data.

## IMAGE CONSISTENCY & CHARACTER BIBLE (locked from all previous versions)
Use the Character Bible + Substack art style for all characters. The agent appends the bible + reference prompts to every image generation call.

## CHARACTER BIBLE CONTENT (merged from all previous character-bible.md versions)
# ETERNAL CODEX — CHARACTER BIBLE (Image Consistency Training)

## OFFICIAL CHARACTERS FROM SUBSTACK
- Elder Codex-7, Chain Scribe, The Grid, City Block Topia, Sacred Chain Ontology, Level-9, Alien Backend.

## ALL CHARACTERS FROM CONVERSATION
- Lady-INK, Charlie Buster, Bone Idol Ink, Delicious Again Peter, AI-Chunks, Treef Project, Crowned Royal Moongirls (group), HODL X Warriors (group), Bitcoin X Kids (3 paths), OG Bitcoin Kids (group), Bald-headed wannabe Moonboys (40 faction members from outside), Bald-headed moonboys inside Block Topia (older Bitcoin Kids born inside), Jodie Zoom and all GraffPunks crew.

## IMAGE PROMPT TEMPLATE
"Generate a high-detail GraffPunks style scene in the artist's universe. Use these reference images for exact character consistency: [all reference links]. Never change hair, face, clothing, colors, or style from these refs. Match the scene to the lore text perfectly, including time of day, weather, lighting, and season."

This master file now contains **100% of every brain-rules.md and character-bible.md version** ever created in this chat. All rules, storylines, characters, and details are here in one place.

The agent loads this file every run.

## DB-14: AUTO-PIN MESSAGE 2 (locked)
After both lore posts are successfully sent to Telegram, the bot must call `pinChatMessage` on the Message 2 message ID. Pinning failure is non-fatal — log the error to stdout and continue.

## MB-1: MASTER BACKUP PURPOSE (locked)
`master-backup-agent.py` is the single passive observer for the entire GK BRAIN system. It maintains an append-only snapshot (`master-backup-state.json`) of every rule, constant, and logic value across all tracked files. It has zero runtime authority — it cannot start, stop, or modify any other agent.

## MB-2: BACKUP ABSORPTION PROTOCOL (locked)
On every run, the backup agent: (1) SHA-256 fingerprints all tracked files, (2) for any changed or new file, extracts DB-N/MB-N rules from `.md` files and module-level constants from `.py` files, (3) conflict-checks against locked rule files, (4) merges safe updates into `rule_snapshot`, (5) quarantines conflicts in `conflict_log`, (6) appends an audit entry, (7) writes atomically via `tmp + os.replace`. Always exits 0.

## MB-3: CONFLICT RESOLUTION PROTOCOL (locked)
Conflicts in `conflict_log` are resolved by the repo owner manually. Resolution steps: (1) read both `existing_value` and `incoming_value` in the conflict entry, (2) determine which is correct by checking the authoritative source file, (3) update the rule in the correct source file, (4) clear the conflict entry by setting `"resolution": "accepted"` or `"resolution": "rejected"`. The backup agent will re-absorb the correct value on the next run.

## MB-4: DISASTER RECOVERY (locked)
If any agent file is corrupted or accidentally deleted, `master-backup-state.json` provides the last known-good snapshot of all rules and constants. Recovery procedure: (1) read `rule_snapshot` section, (2) find all entries with `"source_file": "<lost file>"`, (3) reconstruct the file from those entries. The `audit_trail` section provides a timestamped history of every change.

## MB-5: NEW FILE ONBOARDING (locked)
When a new agent, rule file, workflow, or canon file is added to the repo, it MUST be added to `TRACKED_FILES` in `master-backup-agent.py` in the same PR. If the new file contains locked rules, it must also be added to `LOCKED_RULE_FILES`. The backup agent will automatically absorb and fingerprint the new file on its next run.
