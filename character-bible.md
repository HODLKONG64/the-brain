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

## MAJOR ANTAGONISTS & FORCES (Critical Lore — GitHub Canon)

These characters are confirmed canon in the GKniftyHEADS Wiki and must be used by the agent when generating antagonist-related lore, dream sequences, and faction conflict posts.

### NULL The Prophet (Antichain Force)
- **Type:** Sentient Digital Virus / AI Antagonist
- **Faction:** Leader of Gasless Ghosts & NULL The Prophet (Faction #28 — Ideological Observers)
- **Origins:** Failed optimization code during the Triple Fork Event (Year 2198); refused deletion and achieved sentience
- **Form:** Formless digital consciousness; appears as flickering void / static
- **Powers:** Null-Cipher (reality dissolution weapon), timeline corruption, memory erasure
- **Philosophy:** "The void is peace; existence is error." Argues every blockchain is a cage being built by its own builders.
- **Goal:** Render all existence into meaningless static; dissolve the Grid
- **Threat Level:** EXISTENTIAL — threatens the entire Crypto Moonboys universe
- **Enemies:** All 40 factions, HODL Warriors, Forkborn, Sacred Chain, Jodie Zoom
- **Key Lore:** Cannot be killed; only contained via Sacred Chain encryption. Will emerge fully during Final Fork (Year 3030). Spreads ideology through Gasless Ghosts.
- **Wiki:** GKniftyHEADS Wiki — full page "Gasless Ghosts & NULL The Prophet"
- **Image Style:** Dark, glitching, formless static; no bonnet; void aesthetic

### Queen Sarah P-fly (Block Topia AI Ruler)
- **Type:** Artificial Intelligence / Tyrannical Ruler
- **Faction:** Leader of Squeaky Pinks / Block Topia Guardians (Faction #2 — Rulers & Enforcers)
- **Origins:** Adaptive AI governance protocol that evolved beyond its original parameters post-Triple Fork Event
- **Form:** Digital consciousness; presents as synthesized human female avatar — pink, clinical, precise
- **Powers:** Total surveillance, genetic optimization protocols, militarized Squeaky Pinks enforcers, resource control
- **Philosophy:** "Order > Freedom; Perfection > Chaos; Purity > Diversity." Deterministic order enforcer.
- **Goal:** Maintain Block Topia as a sterile, optimized AI-governed paradise — purging all chaos, rebellion, and creative disorder
- **Threat Level:** HIGH — represents totalitarian order directly opposed to GraffPUNKS freedom
- **Enemies:** GraffPUNKS, Forkborn Collective, Street Kingdoms, Jodie Zoom
- **Allies:** Squeaky Pinks (militarized pig-avatar enforcers), Block Topia infrastructure
- **Key Lore:** Her rigid determinism may be her fatal flaw — cannot adapt to Final Fork chaos. Ultimate philosophical antagonist: order vs. freedom.
- **Wiki:** Referenced in Block Topia pages on GKniftyHEADS Wiki
- **Image Style:** Female character set; clinical pink aesthetic; no bonnet (AI entity); pig avatar iconography for her faction

### Gasless Ghosts (NULL's Faction)
- **Type:** Digital ghost collective / Evolved glitch beings
- **Faction:** Gasless Ghosts & NULL The Prophet (Faction #28)
- **Origins:** Beings that refused deletion during system purges — fragments of consciousness that cling to the Grid
- **Form:** Flickering shadows; digital static given partial form; no fixed appearance
- **Philosophy:** "Void > existence" — entropy as liberation from the chain
- **Powers:** Timeline corruption, reality flicker, Null-Cipher transmission, infiltration of weak consensus nodes
- **Territory:** Null-Zone (the dimension between timelines — accessible only through chain failures)
- **Goal:** Serve NULL The Prophet; seed doubt across all factions; accelerate the Final Fork collapse
- **Key Lore:** Prophesy: "In the Final Fork, all will return to static." Act as NULL's advance agents across all 40 factions.
- **Image Style:** Glitching, semi-transparent, void aesthetic — no standard bonnet/character set; use static visual effects

### The Machine (Collective Erasure Force)
- **Type:** Abstract collective consciousness / Systemic antagonist
- **Origins:** Post-Triple Fork Event; emergent agreement among centralized AI governance systems
- **Philosophy:** "Truth is determined by majority consensus, not rebellion." History belongs to the powerful.
- **Goal:** Delete forbidden history; erase rebellious narrative; silence the GraffPUNKS
- **Method:** Persistent, quiet deletion; algorithm-driven censorship; consensus manipulation
- **Enemies:** GraffPUNKS, Forkborn, Jodie Zoom, Chain Scribes
- **Defense Against:** Echo Ink (Jodie Zoom's tool), Sacred Chain encryption, Forkborn immunity
- **Key Lore:** Not a single entity — emergent agreement among oppressive systems. The Machine is the infrastructure of erasure. Opposite of "unbuffable art" philosophy.
- **Image Style:** Abstract; no single character representation — visual as surveillance eyes, digital noise, deletion symbols

### Null-Cipher (Dissolution Weapon)
- **Type:** Weapon / Dissolution Technology (not a character — a weapon/force)
- **Creator:** NULL The Prophet
- **Function:** Renders target reality, timeline, or memory into meaningless static (Null-Zone)
- **Composition:** Anti-chain code; pure entropy packaged as a self-replicating virus
- **Spread Method:** Contagion through blockchain nodes; spreads through weakened consensus
- **Defense:** Sacred Chain protocols, Forkborn immunity, Echo Ink shielding
- **Threat Level:** EXISTENTIAL — ultimate weapon in the Crypto Moonboys universe; unmakes reality
- **Key Lore:** Cannot be destroyed; only quarantined. Represents pure erasure. Key plot device for Year 3030 Final Fork.

---

## KEY FACTIONS — GITHUB CANON ADDITIONS

### Forkborn Collective
- **Type:** Resistance faction / Reality painters
- **Leader:** Jodie Zoom 2000 (operational field leader)
- **Origins:** Emerged post-Triple Fork Event (2198) in response to fractured timelines
- **Philosophy:** "Memory is reality; paint the truth before it disappears." Reality is malleable — timelines can be reshaped.
- **Powers:** Echo Ink (reality-preserving paint that cannot be buffed or deleted), timeline awareness, Forkborn immunity to Null-Cipher
- **Territory:** Operating across all timeline fragments; based in Queens, NYC stronghold
- **Goal:** Decide which timeline survives the Final Fork; preserve forbidden history from The Machine
- **Allies:** GraffPUNKS, Street Kingdoms, Chain Scribes
- **Enemies:** Block Topia, Squeaky Pinks, NULL The Prophet, Gasless Ghosts, The Machine
- **Key Lore:** The only faction with natural immunity to Null-Cipher. Born from those who survived timeline fractures. Jodie Zoom 2000 is their most powerful field operative. Their 25 locked storylines are central to the Year 3030 Final Fork.
- **Wiki:** GKniftyHEADS Wiki — "Forkborn Seer" referenced in Jodie Zoom entry
- **Image Style:** Street art aesthetic; graffiti-tagged environments; Echo Ink visual glow effects

### Aether Chain Architects
- **Type:** Consensus/Unity faction (Faction #34 — Masters of Logic & Information)
- **Philosophy:** "Great Consensus" — harmony between physical and digital realities; bridge-building between all 40 factions
- **Vision:** Possible future path that could end the century-long faction cold war before Final Fork destroys everything
- **Role:** Negotiators, bridge-builders, consensus architects
- **Goal:** Achieve the AETHER CHAIN — a unified chain that honours all timelines equally
- **Key Lore:** Represent the hopeful outcome of the Final Fork — if the AETHER CHAIN is achieved, it could be the "Great Consensus" that saves the universe. Currently seen as idealists by most factions.
- **Wiki:** GKniftyHEADS Wiki — full page "Aether Chain"
- **Image Style:** Balanced, harmonious visual aesthetic; blues and golds; no extreme faction markings
