## DUAL BRAIN RULES

```
DUAL BRAIN RULES (LOCKED — DO NOT VIOLATE)
===========================================
DB-1: BRAIN 1 is the Canon Brain. It learns from web crawls, website updates,
      NFT platforms, social media, and LLM-discovered canonical facts only.
DB-2: BRAIN 1 is the ONLY brain that may update the Fandom wiki.
DB-3: BRAIN 2 is the Telegram Lore Brain. It holds only the last 7 days of
      Telegram lore posts for continuity purposes.
DB-4: BRAIN 2 lore NEVER goes to the wiki. Not a word.
DB-5: BRAIN 2 resets every Sunday at midnight UTC. All posts are wiped.
DB-6: Both brains save data compressed as small as possible (compact JSON only).
DB-7: BRAIN 2 only saves the last 7 days. Anything older is deleted on every run.
DB-8: BRAIN 1 keeps a rolling log of the last 200 web discoveries. Older entries
      are dropped to keep file size small.
DB-9: The agent learns about Crypto Moonboys from: (a) all websites in
      gkandcryptomoonboywebsitestosave.md, (b) LLM responses that contain new
      canonical facts, (c) any other source the agent encounters. All learning
      goes to BRAIN 1 only.
DB-10: Art creation uses LLM prompts to enhance 2D art. LLM art advice/results
       that reveal canonical character appearance details are saved to BRAIN 1
       under character_facts.
```

---

## IMAGE GENERATION & ON-BRAND CONSISTENCY RULES

### Core Principle
- Always ensure that images generated are reflective of the brand's aesthetics and messaging.
- All image generation must use the four approved character image sets as the sole visual references — never invent styles from scratch.

### Character Image Sets (New 4-File System)

The brand uses four dedicated image files as the authoritative visual references:

| File | Path | Purpose |
|------|------|---------|
| Boys Face Expressions | `assets/layers/boys_set_1/boysimagesetone.png` | Boys character face expressions and head variations |
| Boys Bonnets/Accessories | `assets/layers/bonnet_styles_boys_set_2/boysimagesettwo.png` | Boys bonnet styles and accessory variations |
| Girls Face Expressions | `assets/layers/females_set_1/girlsimagesetone.png` | Girls character face expressions and head variations |
| Girls Bonnets/Accessories | `assets/layers/bonnet_styles_females_set_2/girlsimagesettwo.png` | Girls bonnet styles and accessory variations |

### Primary Reference Sources
- **Boys characters**: Use `boysimagesetone.png` for face/expression reference and `boysimagesettwo.png` for bonnet/accessory reference.
- **Girls characters**: Use `girlsimagesetone.png` for face/expression reference and `girlsimagesettwo.png` for bonnet/accessory reference.
- Randomly select from the appropriate set (boys or girls) based on the character being generated.
- Reference existing artworks and media produced by the brand to maintain consistency.

### If NO Reference Images Can Be Found (fallback sequence)
1. **First fallback**: Load the gender-matched image sets — boys (`boysimagesetone.png` + `boysimagesettwo.png`) or girls (`girlsimagesetone.png` + `girlsimagesettwo.png`).
2. **Second fallback**: Use the boys image sets as the universal default when character gender cannot be determined.
3. **Final fallback**: Use generic stock images that align with the brand vibe but are not directly associated with other trademarks, and ensure the color tone and style match the desired imagery before final approval.
4. Never distribute a generated image without verifying it against at least one of the four approved image files.

### How the Agent Ties Images to the Final Lore Details
- Select the correct gender-matched image set (boys vs. girls) based on the character's established lore identity.
- Confirm that face expressions align with the character's current emotional arc and narrative context.
- Confirm that bonnet/accessory visuals reflect the character's faction uniform and development arc.
- Include visual elements that enhance or reflect narrative connections relevant to the brand universe.

### Enforcement & Consistency Checks
- All generated images must trace back to one of the four approved image set files.
- Conduct quarterly reviews of generated imagery to evaluate adherence to on-brand guidelines.
- Implement a checklist that verifies the correct image set was selected (boys vs. girls) prior to distribution.
- Ensure 100% visual consistency is maintained against the reference image sets across all outputs.

### Why These Rules
- To sustain brand integrity and recognition in a competitive market.
- To ensure all visual representations resonate with the target audience and community expectations.
- The 4-file system (2 for boys, 2 for girls) provides clear, organized references that eliminate ambiguity about which visual standards apply to each character type.

---


# NOTE
This file contains IMAGE GENERATION rules only. All lore canon is in `gk-brain-complete.md`.
