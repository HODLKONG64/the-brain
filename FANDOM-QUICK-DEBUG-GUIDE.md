# FANDOM QUICK DEBUG GUIDE

Use this guide when wiki writes are silently failing or content is not appearing on the wiki.

---

## 1. Check the Wiki Brain Health Check

`wiki-brain.py` performs a GET to `{FANDOM_WIKI_URL}/api.php` before any write.
If it returns a non-200 status the brain aborts and logs:

```
[wiki-brain] health check failed — skipping all writes this cycle
```

**Fix:** Verify `FANDOM_WIKI_URL` secret is set correctly (no trailing slash) and the wiki is reachable.

---

## 2. Confirm Credentials Are Set

| Secret | Expected value |
|---|---|
| `FANDOM_BOT_USER` | Your Fandom bot account username |
| `FANDOM_BOT_PASSWORD` | Bot password (not your personal password) |
| `FANDOM_WIKI_URL` | `https://gkniftyheads.fandom.com` (no trailing slash) |

The code derives the API endpoint as `FANDOM_WIKI_URL + "/api.php"`.

---

## 3. Check the Wiki Update Queue

Inspect `wiki-update-queue.json` for pending entries. Each entry should have:
```json
{
  "page_title": "Some Page",
  "content": "...",
  "source": "https://graffpunks.live/...",
  "type": "wiki-update",
  "used": false
}
```
- Entries with `"used": true` have already been processed.
- Entries where `_is_valid_wiki_source()` returned `False` are blocked (see section 4).

---

## 4. Source Validation Failures

`wiki-smart-merger.py → _is_valid_wiki_source()` blocks entries from:
- Source `gk-brain-agent` (Brain 3 lore posts — intentionally blocked per DB-1).
- Any source containing `"telegram"`.
- Update types `lore-post`, `telegram-lore`, `brain-lore`.
- Sources that do not match any keyword in `_OFFICIAL_SOURCE_KEYWORDS`.

**Symptom:** Queue entries exist but nothing is written.
**Fix:** Check the `source` field on blocked entries. If the domain is legitimate, add it to
`_OFFICIAL_SOURCE_KEYWORDS` in `wiki-smart-merger.py` AND to `OFFICIAL-SOURCE-AUTHORITY-RULES.md`.

---

## 5. Wikitext Layout Errors

`wiki-smart-merger.py → _validate_wikitext_layout()` rejects pages with broken markup.
Check GitHub Actions logs for lines containing `[WIKI LAYOUT]`.

---

## 6. Rate Limit / API Errors

| Code | Meaning | Action |
|---|---|---|
| `maxlag` | Fandom server busy | Increase `maxlag` parameter (default 5 s) |
| `edit-conflict` | Concurrent edit | Retry after a few seconds |
| `protectedpage` | Page is locked | Use a bot account with sysop rights |
| `badtoken` | CSRF token expired | Re-login and retry |

---

## 7. Canonical Wiki URL

The wiki has three equivalent URLs:
- `https://gkniftyheads.fandom.com/wiki/Main_Page` (redirect)
- `https://gkniftyheads.fandom.com/wiki/Main_Page?redirect=no` (no-redirect version)
- `https://gkniftyheads.fandom.com/wiki/GKniftyHEADS_Wiki` (canonical after SEO rename)

The agent always writes to **page titles**, not URLs, so the rename does not affect writes.

---

## 8. Run Wiki Brain Standalone (Dry Run)

```bash
python wiki-brain.py --dry-run
```

This logs what would be written without touching the live wiki.
