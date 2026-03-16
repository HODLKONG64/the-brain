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
- Randomly select from the appropriate set (boys or girls) based on the character being generated.
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
