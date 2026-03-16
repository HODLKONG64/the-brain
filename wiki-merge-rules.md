# WIKI MERGE RULES
# Governs how GK BRAIN's `wiki-smart-merger.py` reads, updates, and extends
# the GKniftyHEADS Fandom wiki every 2-hour cycle.

---

## OVERVIEW

The wiki update system runs in two simultaneous layers:

| Layer | Mechanism | Purpose |
|-------|-----------|---------|
| **Layer 1 — Simple Append** | Always runs | Audit trail; one timestamped log entry per update, appended to `GK_BRAIN_Agent_Log`. Never breaks the wiki. |
| **Layer 2 — Smart Merge** | Runs first; falls back to append if it fails | Inserts new data into the correct named section on the main wiki page. Creates the section if it is missing. |

Both layers run every cycle. The audit log is written even if the smart merge fails.

---

## CATEGORY → SECTION MAPPING

Every detected update is classified into one of these categories (from `update-detector.py`).
Each category maps to a dedicated section on the main wiki page (`GKniftyHEADS_Wiki`).

| Category (from detector) | Wiki Section Heading |
|--------------------------|----------------------|
| `gkdata-real` | `GK & GraffPUNKS Official Updates` |
| `fishing-real` | `Fishing Catches & Lake Adventures` |
| `graffiti-news-real` | `Street Art & Graffiti News` |
| `news-real` | `Crypto & Market News` |
| `rave-real` | `Raves & DJ Events` |
| *(unknown category)* | `Agent Updates` *(fallback)* |

---

## SECTION DETECTION LOGIC

1. Fetch current wikitext of the target page via MediaWiki API.
2. Parse all `== Level 2 ==` and `=== Level 3 ===` headings.
3. **If the target section heading exists:**
   - Prepend the new entry at the top of that section's body.
   - Keep all existing entries below (never delete).
4. **If the target section heading is missing:**
   - Append the new section at the end of the page.
   - Use the canonical heading name from the table above.
5. Write the full updated page back via `action=edit` (bot flag).

---

## MERGE ENTRY FORMAT

Each smart-merged entry uses this structure inside its section:

```
=== <Update Title> ===
''Detected: DD Month YYYY, HH:MM UTC''
* '''Type:''' <Category>
* '''Source:''' [<URL> <URL>]

<First 500 characters of extracted content>

----
```

---

## SIMPLE APPEND LOG FORMAT

Every update also appends one line to `GK_BRAIN_Agent_Log`:

```
* '''[<category>]''' <Update Title> — DD Month YYYY, HH:MM UTC — [<URL> source]
```

---

## SUB-PAGE CREATION

For every update a dedicated sub-page is also created:

- **Title format:** `GK_BRAIN_Agent_Log/YYYY-MM-DD/<category>/<SafeTitle>`
- **Content:** Full update wikitext with source, lore weight, and extracted content.
- **Categories:** `[[Category:GK BRAIN Agent Log]]` and `[[Category:<Type>]]`.

---

## SMART MERGE LOG

A running merge status log is maintained at `GK_BRAIN_Smart_Merge_Log`.
Each line records whether the merge succeeded or fell back to append-only:

```
* DD Month YYYY, HH:MM UTC — [<category>] <Title> — ✅ smart-merged
* DD Month YYYY, HH:MM UTC — [<category>] <Title> — ⚠️ append-only
```

---

## SAFETY GATES

These rules are enforced unconditionally:

1. **Never delete.** The smart merger only adds/prepends content. It never removes
   existing wiki sections or entries.
2. **Always append fallback.** If the smart merge API call fails for any reason,
   the simple append to `GK_BRAIN_Agent_Log` still runs.
3. **One-time use.** An update is only merged once. After successful processing,
   `"wiki_done": true` is set in `wiki-update-queue.json` so the same data is never
   merged again.
4. **Rate limiting.** A 1–2 second sleep is inserted between every API call to
   respect Fandom's rate limits.
5. **Credential guard.** If `FANDOM_USERNAME` or `FANDOM_PASSWORD` are missing,
   the entire module exits cleanly without attempting any network calls.

---

## DECISION TREE: SMART MERGE vs SIMPLE APPEND

```
Update received from wiki-update-queue.json
          │
          ▼
  Credentials set?
  ├── No  → skip all wiki activity, log locally
  └── Yes ▼
          │
    Login to Fandom API
          │
          ▼
  Smart merge to main wiki page
  ├── Section exists?
  │   ├── Yes → prepend entry to section
  │   └── No  → create new section, append to page
  │
  ├── API call succeeds? → mark smart_merged++, continue
  └── API call fails?   → log warning, continue to Layer 2
          │
          ▼
  Simple append to GK_BRAIN_Agent_Log  (ALWAYS RUNS)
          │
          ▼
  Create sub-page  GK_BRAIN_Agent_Log/date/type/title
          │
          ▼
  Append one line to GK_BRAIN_Smart_Merge_Log
          │
          ▼
  Mark update wiki_done = true in queue
```

---

## WHEN TO USE SMART MERGE vs WIKI-UPDATER

| Scenario | Use |
|----------|-----|
| Normal 2-hour cycle with new detected updates | `wiki-smart-merger.py` (preferred) |
| Fallback if smart merger import fails | `wiki-updater.py` (simple append only) |
| Manual one-off wiki correction | `wiki-updater.py` CLI |

`gk-brain.py` attempts `wiki-smart-merger.py` first and falls back to
`wiki-updater.py` automatically.

---

## SECTION MAINTENANCE RULES

- Sections grow chronologically (newest at the top within each section).
- If a section exceeds ~50 entries, the agent may archive older entries to a
  dedicated archive sub-page: `GKniftyHEADS_Wiki/Archive/<SectionName>/<Year>`.
  *(This is a future enhancement; current implementation does not auto-archive.)*
- Section headings must always match the canonical names in the Category → Section
  table above. Do not create ad-hoc section names.
