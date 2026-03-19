# GK WIKI COMPLETE ANALYSIS

State-of-the-wiki analysis for `gkniftyheads.fandom.com` as understood by GK BRAIN.

---

## 1. Wiki Identity

| Property | Value |
|---|---|
| Platform | Fandom (MediaWiki) |
| Base URL | `https://gkniftyheads.fandom.com` |
| API endpoint | `https://gkniftyheads.fandom.com/api.php` |
| Canonical main page | `GKniftyHEADS Wiki` (after SEO rename from `Main Page`) |
| Redirect URLs | `/wiki/Main_Page` → `/wiki/GKniftyHEADS_Wiki` |
| No-redirect URL | `/wiki/Main_Page?redirect=no` |

---

## 2. Content Scope

The wiki documents the entire Crypto Moonboys / GKniftyHEADS universe:

### Universe Pillars
- **40 Factions** across 6 pillars (Rulers, Resource, Economic, Military, Ideological, Logic)
- **Characters** — named individuals from all factions plus real-world project founders
- **Lore Events** — Triple Fork Event (2198), Zero-Block Event, Hardfork Games, Final Fork Prophecy (3030)
- **Locations** — Blocktopia (inside/outside), Null-Zone, Citadel, Sacred Chain network nodes
- **Technologies** — Echo Ink, Sacred Chain, Null-Cipher, AETHER CHAIN
- **NFT Collections** — Crypto Moonboys, HODL Warriors, GraffPUNKS, NoballGames, etc.
- **Real-World Entities** — GraffitiKings UK, GraffPUNKS Network, Graffiti Queens, collaborators

### Known Page Categories
```
Characters | Lore Events | NFT Collections | Weapons | Locations
Toys | Games | Keys | GraffPUNKS | Moonboys | HODL X Warriors
Crowned Royal Moongirls | Bitcoin X Kids | OG Bitcoin Kids
Blocktopia | Hard Fork Games | GK BRAIN Auto-Generated | Pages needing images
```

---

## 3. Known Content Gap Areas

These topic areas require dedicated wiki pages but may be missing or incomplete:

- All 40 faction pages (many stub or absent)
- Individual character pages for HODL X Warriors (15 per cycle)
- Individual character pages for Crowned Royal Moongirls (15)
- The Triple Fork Event — detailed timeline
- The Hardfork Games — stage-by-stage breakdown
- Sacred Chain — technical and lore explanation
- AETHER CHAIN — peace-treaty lore arc
- NULL The Prophet — origin, powers, Null-Cipher
- Elder Codex-7 — Chain Scribes leader
- Queen Sarah P-fly — Block Topia AI origin
- Jodie Zoom 2000 — Forkborn Collective, Echo Ink wielder
- Each NFT collection — supply, mint dates, WAX chain details
- GraffitiKings UK — real-world background, connection to GK universe
- graffpunks.live — blockchain radio station lore tie-in

---

## 4. Content Rules for This Wiki

This is a **Fandom wiki**, not Wikipedia. Citation rules are relaxed:

- Official project websites are primary sources ✅
- Creator Substack / Medium posts are valid ✅
- Official social media (X, Instagram, Facebook) is valid ✅
- YouTube content from official channels is valid ✅
- Fan-invented content from non-official sites is NOT valid ❌
- Brain 3 Telegram lore posts are NOT wiki sources ❌

---

## 5. Priority Writing Order

When running a backfill pass, write pages in this order:

1. Faction index pages (all 40)
2. Major characters
3. Foundational lore events (Triple Fork, Final Fork Prophecy)
4. Key technologies and locations
5. NFT collections and game mechanics
6. Real-world entities and collaborators
7. Minor characters and secondary locations

---

## 6. Health Metrics

- `wiki-brain.py` logs write success/failure counts each cycle.
- `wiki-citation-checker.py` verifies all cited URLs are live before writes.
- `wiki-gap-detector.py` compares known canon entities against existing pages to identify gaps.
- `master-backup-agent.py` fingerprints `wiki-update-queue.json` each cycle.
