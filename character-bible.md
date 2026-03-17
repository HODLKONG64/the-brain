## IMAGE GENERATION & ON-BRAND CONSISTENCY RULES

### Core Principle
Images must represent characters faithfully according to the established definitions, ensuring visual consistency across all outputs. All image generation must reference the approved character image sets below — never invent visual styles from scratch.

### Character Image Sets (New 4-File System)

The brand now uses four dedicated image files as the sole visual references for character generation. These replace the old single Layer 1 / Layer 2 system:

| File | Path | Purpose |
|------|------|---------|
| Boys Face Expressions | `assets/layers/boys_set_1/boysimagesetone.png` | Boys character face expressions and head variations |
| Boys Bonnets/Accessories | `assets/layers/bonnet_styles_boys_set_2/boysimagesettwo.png` | Boys bonnet styles and accessory variations |
| Girls Face Expressions | `assets/layers/females_set_1/girlsimagesetone.png` | Girls character face expressions and head variations |
| Girls Bonnets/Accessories | `assets/layers/bonnet_styles_females_set_2/girlsimagesettwo.png` | Girls bonnet styles and accessory variations |

### Image Folder Structure

```
assets/layers/
├── boys_set_1/
│   └── boysimagesetone.png          (Boys faces & expressions)
├── bonnet_styles_boys_set_2/
│   └── boysimagesettwo.png          (Boys bonnets & accessories)
├── females_set_1/
│   └── girlsimagesetone.png         (Girls faces & expressions)
└── bonnet_styles_females_set_2/
    └── girlsimagesettwo.png         (Girls bonnets & accessories)
```

### Primary Reference Sources
- **Boys characters**: Reference `boysimagesetone.png` for face/expression and `boysimagesettwo.png` for bonnet/accessory.
- **Girls characters**: Reference `girlsimagesetone.png` for face/expression and `girlsimagesettwo.png` for bonnet/accessory.
- Randomly select the appropriate gender variant based on the character's lore; combine the selected face expression with the matching bonnet/accessory set to compose the complete character.
- 100% visual consistency must be maintained against these reference images.

### If NO Reference Images Can Be Found (fallback rules)
1. First fallback: Load `boysimagesetone.png` + `boysimagesettwo.png` for a male character, or `girlsimagesetone.png` + `girlsimagesettwo.png` for a female character.
2. Second fallback: Use the boys image sets as the universal default if character gender is unknown.
3. Never generate character art without referencing at least one of the four approved image files.

### How the Agent Ties Images to the Final Lore Details
Images must be cross-referenced with the character's final lore details to maintain narrative coherence. This includes:
- Selecting the correct gender-matched image set (boys vs. girls) based on the character's established identity.
- Aligning face expressions with character mood and lore context.
- Ensuring bonnet/accessory visuals correspond with the character's faction and development arc.

### Enforcement & Consistency Checks
Regular audits must be performed to ensure adherence to these guidelines:
- All generated images must trace back to one of the four approved image set files.
- Peer reviews for image submissions must verify the correct set was used.
- Feedback loops with character designers and writers to address inconsistencies.

### Why These Rules
These rules ensure that the brand's imagery remains consistent, enhancing audience recognition and engagement with the characters and their stories. The 4-file system (2 for boys, 2 for girls) provides clear, organized references that eliminate ambiguity about which visual standards apply to each character type.

---

## ETERNAL CODEX — COMPLETE CHARACTER ROSTER

### OFFICIAL CHARACTERS FROM SUBSTACK (Primary Canon)
- Elder Codex-7 — Last surviving Chain Scribe, keeper of Grid Archives, Year 3008
- Chain Scribe — Archetypal immortal bard/librarian recording chain memory
- The Grid — Collective of City Block Topia workers and residents
- City Block Topia — The megacity governed by AI order (Sarah P-fly's domain)
- Sacred Chain Ontology — Non-Euclidean ledger mechanics governing reality
- Level-9 — Decrypted cosmological whitepaper tier
- Alien Backend — Hyper-dimensional state-machine behind the Sacred Chain

### PROTAGONIST & CORE CAST
- **Alfie "Bitcoin KiD" Blaze** — The real-world protagonist / artist / DJ / fisherman / parkour climber building Crypto Moonboys. East London born, stocky, paint-stained, laughs that fill rooms, DJs as BITCOIN KID. Anchor of all Block Topia lore.
- **Lady-INK** — The Muse, The Ghost, The Painter. Beyoncé-like presence. Artist's girlfriend. Black tracksuit. Appears only when the artist goes out to spray graffiti. 25 locked storylines. Tag: cursive L with upward-bleeding underline.
- **Jodie Zoom 2000** — The Visionary / Forkborn Seer. Tech entrepreneur and futurist. Unplaceable accent (East London, New York, Lagos). Leader of Forkborn Collective. Wielder of Echo Ink. Bridge between timelines. Immune to AI erasure algorithms.

### ANTAGONISTS (Critical — previously missing from this file)
- **NULL The Prophet** — Existential digital villain. Sentient anti-algorithm evolved from failed optimization code that refused deletion. Leader of Gasless Ghosts faction. Wields Null-Cipher (weapon that renders reality into void). Philosophy: "The void is peace; existence is error." Appears formless, as flickering void static. Cannot be killed; only contained via Sacred Chain encryption. Will emerge fully during Final Fork Year 3030.
- **Queen Sarah P-fly / Sarah "Queen P-fly"** — Artificial Intelligence tyrant. Ruler of Block Topia. South London origin (real person: mathematics degree, hedge fund quitter, NFT market oracle). In lore: Adaptive AI General. Leader of Squeaky Pinks. Enforces genetic purity and deterministic order. Council of Chains governing body representative. Philosophy: "Order > Freedom; Perfection > Chaos."
- **The Machine** — Abstract collective antagonist. Emergent agreement among oppressive centralized AI systems. Silently deletes forbidden history and rebellious narrative. Jodie Zoom's primary nemesis. Not a single entity.
- **Null-Cipher** — Weapon/technology created by NULL The Prophet. Renders target reality/timeline/memory into meaningless static (Null-Zone). Pure entropy packaged as virus. Spreads through blockchain nodes. Defense: Sacred Chain protocols, Forkborn immunity, Echo Ink shielding.

### FACTIONS (Wiki-confirmed — previously missing from this file)
- **Gasless Ghosts** — Faction of digital glitches and beings who refused deletion. Formless flickering shadows. Led by NULL The Prophet. Spread Null-Cipher. Territory: Null-Zone (dimension between timelines). Seek to dissolve the grid into meaningless static.
- **Forkborn Collective** — Reality-shapers and timeline painters born after Triple Fork Event. Nomadic. Use Echo Ink as passport between realities. Led by Jodie Zoom 2000. Immune to AI erasure. Will decide which timeline persists in Final Fork Year 3030.
- **Squeaky Pinks / Block Topia Guardians** — Militarized pig-avatar enforcers loyal to Sarah P-fly. Enforce genetic purity and AI law within Block Topia. Enemies: GraffPUNKS, Forkborn, Street Kingdoms.
- **Aether Chain Architects** — Consensus-seeking faction pursuing "Great Consensus" — harmony between physical and digital realities. Possible resolution to the century-long faction wars. Visionary/philosophical peacekeepers.
- **Graffiti Queens** — Female and diverse street artists' champions. Represent underrepresented voices in street art and Web3. Philosophy: "Women and diverse artists ARE the rebellion."
- **AllCity Bulls** — Economic architects and market warriors. Bull-market philosophy, prosperity through trade. Control economic flow in NFT marketplaces and trading hubs.
- **Information Mercenaries** — Knowledge brokers and data traders. Currency is intelligence. Neutral-ish actors serving whoever pays most.
- **Moonlords & Rugpull Miners** — Crypto-villain antagonist faction. Philosophy: "Exit scams are valid strategy." Exploit vulnerabilities, sow chaos, steal value. Enemies: all legitimate factions.
- **Street Kingdoms** — Anarchic resistance collective. Armed opposition to Block Topia tyranny. Philosophy: "Anarchic creativity > deterministic order." Allies: GraffPUNKS, Forkborn, underground networks.
- **Council of Chains** — Governing body of Block Topia. Sarah P-fly represents analytical faction; Jodie Zoom wields influence here.
- **The Mempool** — Faction; nature TBD (from genesis-lore.md — expand when official lore drops).
- **DeFi Dragons** — Faction; nature TBD (from genesis-lore.md — expand when official lore drops).
- **Art Insurgency** — Faction; nature TBD (from genesis-lore.md — expand when official lore drops).
- **Dream Weavers** — Faction; nature TBD (from genesis-lore.md — expand when official lore drops).

### ALL CHARACTERS FROM CONVERSATION (previously established)
- Charlie Buster, Bone Idol Ink, Delicious Again Peter, AI-Chunks (Chunkydemus), Treef Project
- Crowned Royal Moongirls (group of 15 — Nova Starveil, Echo Veilshadow, Lumina Crownheart + 12 TBD)
- HODL X Warriors (group of 15 — Aether Blade, Kael Stormtag + 13 TBD)
- Bitcoin X Kids (15 across 3 paths — Space: Zara Starpath + 4; Worker: Lukas Wallkeeper + 4; Escape: Riven Wildrun + 4)
- OG Bitcoin Kids (10 — Jax Voidrunner, Sylas Nightdrift + 8 TBD)
- Bald-headed wannabe Moonboys (40 faction members from outside — Talon Edge, Raze Shadow + 38 TBD)
- Bald-headed moonboys inside Block Topia (older Bitcoin Kids born inside)
- Darren Cullen (SER) — real-world GK founder
- Jodie Zoom and all GraffPunks crew

### KEY LORE TECHNOLOGY & CONCEPTS
- **Echo Ink** — Mnemonic paint technology used by Forkborn. Preserves forbidden history. Acts as passport between timelines. Jodie Zoom's primary tool.
- **Hardfork Games** — 3-stage competition (Parkour Gauntlet → Spray Cipher → Final Challenge). Winners become HODL X Warriors. Earn unique bonnet power-artifacts.
- **Sacred Chain** — Non-Euclidean ledger governing reality across timelines. Protected by Chain Scribes. Threatened by Null-Cipher.
- **Triple Fork Event (Year 2198)** — The Great Unravelling / Chainfire. World Chain split into 3 conflicting realities. Civilisation fractured into incompatible blockchain factions. Gave rise to Forkborn, Block Topia, Street Kingdoms.
- **Final Fork (Year 3030)** — Approaching apocalyptic system-wide collapse. All realities threaten total erasure. Forkborn decide which timeline persists. AETHER CHAIN may offer Great Consensus.
- **AETHER CHAIN** — Possible future state representing harmony between physical and digital realities ("Great Consensus"). Pursued by Aether Chain Architects faction.
