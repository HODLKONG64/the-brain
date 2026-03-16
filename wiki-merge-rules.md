# wiki-merge-rules.md
# Decision Rules for Smart Wiki Updates — GK BRAIN

These rules govern how `wiki-smart-merger.py` reads, analyses, and updates
Fandom wiki pages intelligently without clobbering existing content.

---

## 1. Section Detection Rules

The merger identifies **Level-2 headings** (`== Heading ==`) as top-level sections.

| Section Heading            | Description                              |
|----------------------------|------------------------------------------|
| `Fishing Records`          | Real carp catches, lake names, weights   |
| `Graffiti & Street Art`    | Street art news, murals, tagging events  |
| `NFT Drops & Collections`  | GKniftyHEADS NFT releases & mints       |
| `Crypto & Market News`     | Crypto prices, market moves, news        |
| `Rave & Music Events`      | UK drum & bass events, DJ appearances    |
| `Events & Meetups`         | General events and community meetups     |
| `Latest News`              | Breaking crypto / news weave snippets    |
| `Characters`               | GKniftyHEADS characters + Lady-INK      |
| `Locations & Landmarks`    | Locations discovered in lore            |
| `Art Movements & Styles`   | Noted art styles referenced in lore     |
| `Dream & Raid Events`      | Dream sequences and raid storylines     |
| `Special Events`           | One-off or seasonal special events      |
| `Uncategorized Updates`    | Updates whose type is not yet mapped    |

### Detection Algorithm
1. Read full wikitext of the target page.
2. Split on `== Heading ==` patterns (Level-2 only).
3. Build a `{heading: body}` map (order preserved).
4. Identify which target section exists or is absent.

---

## 2. Category → Section Mapping

| Update Type          | Target Wiki Section           |
|----------------------|-------------------------------|
| `fishing-real`       | Fishing Records               |
| `fishing`            | Fishing Records               |
| `graffiti-news-real` | Graffiti & Street Art         |
| `graffiti`           | Graffiti & Street Art         |
| `gkdata-real`        | NFT Drops & Collections       |
| `nft`                | NFT Drops & Collections       |
| `crypto`             | Crypto & Market News          |
| `rave-real`          | Rave & Music Events           |
| `rave`               | Rave & Music Events           |
| `event`              | Events & Meetups              |
| `news-real`          | Latest News                   |
| `news`               | Latest News                   |
| `character`          | Characters                    |
| `character-profile`  | Characters                    |
| `lady-ink-hint`      | Characters                    |
| `location`           | Locations & Landmarks         |
| `place`              | Locations & Landmarks         |
| `art-movement`       | Art Movements & Styles        |
| `art`                | Art Movements & Styles        |
| `dream`              | Dream & Raid Events           |
| `raid`               | Dream & Raid Events           |
| `special-event`      | Special Events                |
| *(any other type)*   | Uncategorized Updates         |

All update types are now handled — unknown types go to `Uncategorized Updates`
instead of being silently dropped.

---

## 3. Merge Patterns

### 3.1 Insert into Existing Section
When the target section already exists on the page:

```
== Fishing Records ==
• NEW ENTRY inserted here (top of section)
• previous entry …
• older entry …
```

New items are prepended (most recent first).

### 3.2 Create New Section
When the target section does **not** exist:

```
(end of existing page)

== Fishing Records ==
• new entry …
```

The section is appended at the bottom of the page.

### 3.3 Duplicate Guard
Before inserting, the merger checks in this order:
1. **Source URL** — is the exact URL already present anywhere on the page?
2. **Title + date** — does a `title.*YYYY-MM-DD` regex match the page body?
3. **Content fingerprint** — is the 16-char MD5 prefix (embedded as `<!-- fp:… -->`)
   already present in the page body?

If any check passes → skip smart merge for this entry (log only).

---

## 4. Simple Append Fallback

The agent-run log entry is **always** written to `GK_BRAIN_Agent_Log`,
regardless of whether smart merge succeeded.

Format:
```
* '''[[GK_BRAIN_Agent_Log/YYYY-MM-DD/type/Title|Title]]'''
  — type — DD Month YYYY, HH:MM UTC ✅ smart-merged
```

Or if append-only:
```
* '''[[GK_BRAIN_Agent_Log/YYYY-MM-DD/type/Title|Title]]'''
  — type — DD Month YYYY, HH:MM UTC 📋 appended
```

### When to Use Simple Append
- Smart merge raises an exception.
- Entry is detected as already present (duplicate guard fires).
- Credentials are unavailable (no-op for both layers).

---

## 5. Conflict Resolution

| Situation                         | Action                                      |
|-----------------------------------|---------------------------------------------|
| Entry already in section          | Skip insert; log-only                       |
| Section exists, entry is new      | Prepend bullet to section                   |
| Section does not exist            | Create section at page bottom               |
| Update type unknown               | Insert into Uncategorized Updates section   |
| API edit fails                    | Fall back to simple append; log failure     |
| Credentials missing               | Skip all wiki operations; print warning     |

---

## 6. Safety Gates

- **Never delete** existing content — only add or update.
- **Never overwrite** a section — always prepend new bullets to existing body.
- **Always** write the agent-run log entry (Layer 1) even if Layer 2 fails.
- **Rate limit** — 2-second sleep between API calls to avoid Fandom rate limits.
- **Re-read** the main page after each fallback append so the next iteration
  has the freshest content (avoids clobbering concurrent edits).

---

## 7. Examples

### Example A — New Fishing Catch
```json
{ "type": "fishing-real", "title": "50lb Mirror Carp at Redmire Pool",
  "content": "Record catch reported on CarpTalk forums, 26 March 2026.",
  "source": "https://carptalk.com/..." }
```
→ Merged into `== Fishing Records ==` on `GKniftyHEADS_Wiki`.
→ Bullet: `* '''50lb Mirror Carp at Redmire Pool''' — Fishing Real — 26 March 2026, 14:00 UTC`
→ Log entry on `GK_BRAIN_Agent_Log` marked ✅ smart-merged.

### Example B — New NFT Drop
```json
{ "type": "gkdata-real", "title": "GKniftyHEADS Series 4 Drop",
  "content": "New 50-piece collection minted on Ethereum.",
  "source": "https://gkniftyheads.fandom.com/..." }
```
→ Merged into `== NFT Drops & Collections ==` on `GKniftyHEADS_Wiki`.

### Example C — Unknown Type (Fallback)
```json
{ "type": "misc-update", "title": "Random Update", "content": "…" }
```
→ Type not in mapping → simple append to `GKniftyHEADS_Wiki`.
→ Log entry on `GK_BRAIN_Agent_Log` marked 📋 appended.
