# FANDOM REFERENCE CARD — GK BRAIN

Quick-reference cheat-sheet for Fandom / MediaWiki API calls used by the GK BRAIN system.

---

## Authentication Flow (`fandom_auth.py`)

```
POST /api.php?action=query&meta=tokens&type=login
  → logintoken

POST /api.php?action=clientlogin&loginreturnurl=...&logintoken=...
     &username=FANDOM_BOT_USER&password=FANDOM_BOT_PASSWORD
  → Login OK / FAIL
```

**CSRF token** (needed for all edit/write calls):
```
POST /api.php?action=query&meta=tokens
  → csrftoken
```

---

## Edit / Create a Page

```
POST /api.php
  action=edit
  title=<page title>
  text=<full wikitext>
  summary=<edit summary>
  token=<csrftoken>
  bot=1
```

Response `edit.result == "Success"` means the write succeeded.

---

## Read an Existing Page

```
GET /api.php?action=query&prop=revisions&rvprop=content&titles=<title>&format=json
```

---

## Upload an Image

```
POST /api.php
  action=upload
  filename=<File:Name.ext>
  file=<binary>
  text=<page wikitext for the file page>
  token=<csrftoken>
```

---

## Key API Parameters

| Parameter | Default | Notes |
|---|---|---|
| `format` | `json` | Always use `json` |
| `maxlag` | `5` | Seconds; Fandom will return `maxlag` error if server is busy — retry after `Retry-After` header |
| `bot` | `1` | Marks edits as bot edits (suppress Recent Changes noise) |
| `minor` | — | Set for small clean-up edits |

---

## Error Codes to Know

| Code | Meaning |
|---|---|
| `badtoken` | CSRF token invalid or expired — re-query tokens |
| `edit-conflict` | Another edit happened concurrently — re-read page and retry |
| `protectedpage` | Page locked; bot needs sysop or higher rights |
| `ratelimited` | Too many edits — sleep and retry |
| `maxlag` | Server lag too high — honour `Retry-After` |

---

## Environment Variables

| Variable | Purpose |
|---|---|
| `FANDOM_BOT_USER` | Bot username |
| `FANDOM_BOT_PASSWORD` | Bot password |
| `FANDOM_WIKI_URL` | Base URL, e.g. `https://gkniftyheads.fandom.com` |

Derived: `WIKI_API = FANDOM_WIKI_URL.rstrip('/') + '/api.php'`

---

## Wikitext Quick Reference

```wikitext
== Section Heading ==
=== Sub-section ===

[[Wikilink to page]]
[[Page Title|Display Text]]

{{Infobox Character
| name   = Example
| image  = [[File:Example.png|thumb|right|Caption.]]
| faction = GraffPUNKS
}}

[[Category:Characters]]
[[Category:GK BRAIN Auto-Generated]]
```
