## IMAGE GENERATION & ON-BRAND CONSISTENCY RULES

### 1. Core Principle (locked)
Every image must be 100% on-brand and feel like it came from the same universe as the official GraffPunks art on Substack, Medium, and uploaded reference files. Goal: near 100% visual consistency for every character across thousands of posts so readers instantly recognise them.

### 2. Primary Reference Sources (in strict order — agent MUST follow this sequence every time)

**Layer Files (permanent base — no final training files needed yet because these replace them):**
- **Layer 1:** Upper body base from "template kid 4.png" (rounded yellow head + torso — locked foundation for all Crypto Moonboys characters)
- **Layer 2:** GraffPUNKS bonnet shape (exact centre eagle beak + eagle bird on each side + white feathers above eyes + green GraffPUNK hair pulled through + yellow leather material + ears popping out sides). Head + bonnet treated as ONE single unit — never separated.

**Official Online References (crawled every run):**
- Agent first crawls https://substack.com/@graffpunks/posts looking for sole dedicated webpages about the specific character or theme in the current lore
- If a dedicated page exists, the agent learns the character's look 90% exactly from the images on that page (head + bonnet as one unit, then adds a random face expression that matches the lore mood/theme)
- This overrides Layers 1 & 2 only if the official page shows a clearer/more up-to-date version — otherwise Layers 1 & 2 stay the anchor

**Black Charcoal Pencil Style (default for all lore images unless the lore specifically asks for colour):**
- All images generated in high-contrast black charcoal pencil on white paper style (dramatic shading, textured lines, exactly like the header artworks)

### 3. If NO Reference Images Can Be Found (fallback rules — in exact order)

1. Use Layer 1 base + Layer 2 bonnet shape exactly (100% fidelity — head + bonnet as one unit)
2. Add a random face expression from the 20-expression pool (angry, surprised, grinning, thoughtful, X-eyes, etc.) that perfectly matches the mood of the 2-hour lore block
3. Create cool unique bonnet colours/patterns and small clothing details inspired by all existing characters in character-bible.md (never repeat the exact same pattern twice in a row)
4. Keep the overall silhouette and proportions near 100% identical to the uploaded layers and any previous posts in lore-history.md (the agent checks the last 7 days of images for consistency)
5. Generate the image prompt with the exact phrase:
   > "Use 100% Layer 1 upper body + 100% Layer 2 bonnet shape as one unit. Random face to match lore mood. Black charcoal pencil on white paper. On-brand GraffPunks style. Near 100% consistency with all previous official and generated images."

This fallback ensures the agent can always finish the task without stalling, while staying on-brand.

### 4. How the Agent Ties Images to the Final Lore Details

- Agent first writes the full lore text (using all brain-rules)
- Then extracts the key visual elements from that text (time of day, weather, location, character actions, mood, news alert, etc.)
- Image prompt is built to dictate a scene exactly matching the lore (e.g. "artist painting at 3am in rain on a train with Lady-INK")
- Every image must illustrate one specific moment from the lore post it accompanies

### 5. Enforcement & Consistency Checks (the agent does this automatically)

- Before sending any post, the agent reviews the last 7 days of lore-history.md images to ensure characters look near 100% the same
- If any drift is detected, it forces a correction in the next prompt
- Grok Imagine (via the API) is always instructed to respect the layers and references first

### 6. Why These Rules (the "why" locked in)

- No final art training files exist yet — so we use the uploaded layers + live Substack crawl as the permanent "training"
- This guarantees characters stay instantly recognisable forever
- The fallback rules make sure the agent never gets stuck and can always generate on-brand images
- Everything stays 100% on-brand with the official GraffPunks aesthetic

### Required Layer Image Files (upload from your PC to repo)

The following image files must be added to the `/assets/layers/` folder in this repository:
- **`template_kid_4.png`** — Layer 1: rounded yellow head + torso base
- **`graffpunks_bonnet_layer_2.png`** — Layer 2: GraffPUNKS bonnet shape (centre eagle beak + eagle birds + white feathers + green hair + yellow leather + ears)