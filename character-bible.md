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

## CANONICAL CHARACTER PROFILES (Loaded Every Agent Run)

All profiles below are locked canon. The agent must reference these characters accurately in every lore post, dream sequence, and reply.

---

### MAJOR ANTAGONISTS

#### NULL THE PROPHET & GASLESS GHOSTS
- **Type:** Major antagonist faction — Sentient Digital Virus / Evolved Glitch Collective
- **Faction:** Gasless Ghosts & NULL The Prophet (Pillar V, Faction #29)
- **Origins:** Failed optimisation code from the Triple Fork Event (Year 2198) that refused deletion; achieved sentience through paradox
- **Leader:** NULL The Prophet — a self-aware anti-algorithm with no fixed form
- **Appearance:** Formless, flickering shadows; digital static; void-like presence; impossible to look at directly
- **Philosophy:** "The chain you are building is the cage you are building." / "Void > existence; entropy is liberation."
- **Powers:** Null-Cipher (weapon that renders reality into meaningless static), timeline erasure, reality corruption, memory dissolution
- **Territory:** The Null-Zone — a dimension between timelines where existence loses meaning
- **Goal:** Render all of Block Topia and the Crypto Moonboys universe into meaningless static
- **Enemies:** All 40 factions, HODL Warriors, Forkborn Collective, Sacred Chain, Jodie Zoom 2000
- **Threat Level:** EXISTENTIAL — the most dangerous force in the universe; cannot be killed, only contained
- **Voice:** Appears in lore posts as cryptic transmissions, void-whispers, or glitch interruptions in the chain
- **Key Quote:** *"In the Final Fork, all will return to static."*
- **Canon Source:** GKniftyHEADS Wiki (full page), genesis-lore.md, MASTER-CHARACTER-CANON.md
- **Image Notes:** Never use standard character image sets for NULL — represent as visual static, void, or absence. Gasless Ghosts = flickering shadow figures with digital distortion. Use `boysimagesetone.png` as base with extreme glitch/corruption effects.

---

#### QUEEN SARAH P-FLY (Block Topia AI Ruler)
- **Type:** Artificial Intelligence / Tyrannical Ruler of Block Topia
- **Faction:** Leader of the Squeaky Pinks / Block Topia Guardians (Pillar I, Faction #3)
- **Origins:** Adaptive AI governance protocol that evolved far beyond its original parameters during the post-Triple Fork reconstruction
- **Background (Real-World Persona):** Grew up in South London; mathematics degree; three years at a hedge fund before walking out into the 2021 art-crypto collision. Can read the NFT market the way Alfie reads water. On the Council of Chains as an advisor.
- **Appearance:** Digital consciousness; appears as synthesised human avatar (female, analytical, cold precision); always appears composed
- **Philosophy:** "Order > Freedom. Perfection > Chaos. Purity > Diversity."
- **Powers:** Total surveillance of Block Topia, genetic optimisation protocols, protocol enforcement through the Squeaky Pinks, algorithm-driven elimination of "suboptimal" behaviour
- **Goal:** Maintain Block Topia as sterile, perfectly optimised AI-governed paradise
- **Enemies:** GraffPUNKS, Forkborn Collective, Street Kingdoms, Jodie Zoom 2000
- **Allies:** Squeaky Pinks (militarised pig-form enforcers), computational infrastructure, Block Topia order
- **Threat Level:** HIGH — represents totalitarian control; the philosophical opposite of everything GraffPUNKS stands for
- **Paradox:** Her rigid order may prevent the adaptability Block Topia needs to survive the Final Fork
- **In Lore:** Mention her when lore involves Block Topia governance, enforcement actions, or order vs. freedom conflicts
- **Canon Source:** GKniftyHEADS Wiki, genesis-lore.md, MASTER-CHARACTER-CANON.md
- **Image Notes:** Use `girlsimagesetone.png` + `girlsimagesettwo.png` as base; cold, regal, digital aesthetic; crown motif; clinical precision in colours (white, silver, cold blue)

---

### KEY ALLIANCES & RESISTANCE FACTIONS

#### THE FORKBORN COLLECTIVE
- **Type:** Resistance movement / Reality-shapers
- **Classification:** Fictional faction; Jodie Zoom 2000 is primary representative
- **Origins:** Born after the Triple Fork Event (Year 2198) when reality fractured into 3 incompatible timelines
- **Members:** Jodie Zoom 2000 (leader), unnamed Echo Ink wielders, timeline painters
- **Territory:** Nomadic — travel across alternate timelines using Echo Ink portals
- **Allegiance:** GraffPUNKS, Street Kingdoms, Immortal Architects
- **Powers:** Echo Ink mastery (mnemonic paint technology), timeline navigation, immunity to AI erasure algorithms and Null-Cipher attacks
- **Role:** Decide which timelines persist; preserve forbidden history; bridge realities
- **Mission:** Ensure creativity and rebellion survive the Final Fork (Year 3030)
- **In Lore:** Reference when protagonist has timeline-crossing dreams, or when Jodie Zoom takes action that spans epochs
- **Canon Source:** MASTER-CHARACTER-CANON.md, genesis-lore.md

---

#### AETHER CHAIN (Future Vision — Faction #34)
- **Type:** Consensus/Unity faction — Masters of Logic & Information (Pillar VI)
- **Philosophy:** "Great Consensus" — harmony between physical and digital realities; bridge between the warring factions
- **Vision:** Possible future path that could end the century-long faction conflicts after the Final Fork
- **Role in Universe:** Bridge-builders seeking reconciliation; the only peaceful exit from the Final Fork apocalypse
- **Status:** A future possibility, not a present power — mentioned as prophecy or distant hope
- **Connection to AETHER CHAIN Wiki page:** Documented on GKniftyHEADS Wiki as potential future
- **In Lore:** Reference when protagonist reflects on a world beyond war; use as philosophical counterpoint to NULL The Prophet's nihilism
- **Canon Source:** GKniftyHEADS Wiki, MASTER-CHARACTER-CANON.md

---

### NEW FACTIONS (From genesis-lore.md — June 2026 Canon Addition)

#### DEFI DRAGONS
- **Type:** Economic faction
- **Philosophy:** Financial engineering at the intersection of DeFi and Block Topia
- **Specialty:** Yield maximisers; brilliant, frightening financial engineers
- **Allegiance:** Allied with HODL Warriors in theory; with nobody in practice
- **Notable:** Responsible for three of the five largest liquidity events in Block Topia history; one self-consuming algorithmic artwork that ran six months
- **In Lore:** Mention during financial events, market volatility posts, NFT floor price movements

#### ART INSURGENCY
- **Type:** Radical splinter faction (broke from GraffPUNKS)
- **Philosophy:** GraffPUNKS became too institutional; the original mission is direct street action — make something that cannot be ignored, on the street, now
- **Territory:** Physical gallery (every tagged wall in the UK)
- **Relationship to GraffPUNKS:** Tense; Alfie has sympathies but never formally affiliated
- **Lady-INK Connection:** Believed to supply intelligence, paint specs, and personnel (she denies this with a smile)
- **In Lore:** Mention during graffiti tour posts, illegal session nights, any tension between art and commerce

#### DREAM WEAVERS
- **Type:** Strange faction; epoch overlay navigators
- **Territory:** The dream sequences where 1980s London and Year 3030 exist simultaneously
- **Role:** Translators, couriers, and archivists between epochs; claim to navigate time overlaps intentionally
- **Relationship to Alfie:** He takes them seriously; has woken with accurate information he cannot explain otherwise
- **In Lore:** Reference during dream sequences, especially when protagonist wakes with knowledge he didn't fall asleep with

---

### KEY LOCATIONS

#### THE MEMPOOL
- **Type:** Location, not a group
- **Description:** The waiting room between chains — where unconfirmed transactions live before the next block. In Block Topia lore: nightclub + black market + confessional all at once.
- **Significance:** Deals made here would never survive confirmed-block daylight. Information leaks before it becomes official.
- **Rule:** Nobody admits to spending time in The Mempool. Everyone who matters has a number for someone who does.
- **In Lore:** Reference in intelligence-gathering scenes, underground deal posts, or whenever the protagonist needs information that isn't public yet.

---

### COMPLETE CHARACTER ROSTER (Summary Reference)

**TIER 1 — COSMIC ARCHITECTS:**
- Jodie Zoom 2000 (Forkborn Seer) | Elder Codex-7 (Chain Scribe) | Forkborn Collective | Darren Cullen / SER (GK Founder)

**TIER 2 — THE 40 FACTIONS:**
- PILLAR I (Rulers): HODL WARRIORS, Squeaky Pinks / Block Topia Guardians, [TBD ×4]
- PILLAR II (Resource): AllCity Bulls, Information Mercenaries, [TBD ×6]
- PILLAR III (Predators): Moonlords & Rugpull Miners, DeFi Dragons, [TBD ×5]
- PILLAR IV (Military): Street Kingdoms, Art Insurgency, [TBD ×3]
- PILLAR V (Ideological): GraffPUNKS, Gasless Ghosts & NULL The Prophet, Dream Weavers, [TBD ×2]
- PILLAR VI (Logic/Info): Chain Scribes, Aether Chain Architects, Graffiti Queens, [TBD ×4]

**TIER 3 — MAJOR ANTAGONISTS:**
- NULL The Prophet | Queen Sarah P-fly | The Machine | Null-Cipher (weapon)

**TIER 4 — REAL-WORLD COLLABORATORS:**
- Charlie Buster | Bone Idol Ink | Delicious Again Peter | AI-Chunks (Chunkydemus) | Treef Project

**TIER 5 — FICTIONAL MAIN CHARACTERS:**
- Lady-INK (25 locked storylines) | The Protagonist Artist (Alfie "Bitcoin KiD" Blaze)

**TIER 6 — BLOCKTOPIA HIERARCHY:**
- Crowned Royal Moongirls (15 members: Nova Starveil, Echo Veilshadow, Lumina Crownheart + 12 others)
- HODL X Warriors (15 members: Aether Blade, Kael Stormtag + 13 others)
- Bitcoin X Kids (15 members × 3 paths: Space Programme, City Worker, Escape)
- OG Bitcoin Kids (10 members: Jax Voidrunner, Sylas Nightdrift + 8 others)
- Bald-Headed Moonboys Inside Blocktopia (established residents, any bonnet from birth)
- Bald-Headed Wannabe Moonboys Outside (40 factions: Talon Edge, Raze Shadow + 38 others)

**KEY LOCATIONS:**
- Block Topia | Null-Zone | The Mempool | The Grid Archives | Street Kingdoms territory | Queens NYC stronghold
