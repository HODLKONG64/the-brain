# LLM Orchestration Architecture

## Overview

The GK BRAIN system uses **two API providers** for AI tasks:

| Provider | Purpose | Model | Endpoint |
|---|---|---|---|
| **Anthropic** | Text / Lore generation | `claude-3-5-sonnet-20241022` | `https://api.anthropic.com/v1/messages` |
| **xAI / Grok** | Image generation | `grok-imagine-image` | `https://api.x.ai/v1/images/generations` |

The **55 Python modules** in the repo are **context builders** — they enrich and
structure the data passed to Claude. They are **not** separate LLM pipelines.

---

## 1. Lore / Text Generation

### Model
- **Primary:** `claude-3-5-sonnet-20241022` via Anthropic API
- **Fallback:** `grok-4-fast` via xAI API (used when `ANTHROPIC_API_KEY` is absent)

### API Endpoint
- Primary: `https://api.anthropic.com/v1/messages`
- Fallback: `https://api.x.ai/v1/chat/completions`

### Authentication
- Primary: `ANTHROPIC_API_KEY` (header: `x-api-key`)
- Fallback: `GROK_API_KEY` (header: `Authorization: Bearer`)

### Request Format (Anthropic)
```json
{
  "model": "claude-3-5-sonnet-20241022",
  "system": "<brain rules + character bible + lore history>",
  "messages": [{"role": "user", "content": "<lore prompt>"}],
  "max_tokens": 4096
}
```

### Response Parsing
The response is parsed for four labelled sections:
- `POST 1:` — first lore entry (plain text)
- `IMAGE PROMPT 1:` — image generation prompt for post 1
- `POST 2:` — second lore entry (image caption)
- `IMAGE PROMPT 2:` — image generation prompt for post 2

### Error Handling
- 3 retries with exponential backoff (2s, 4s) on 5xx / connection errors
- 4xx errors (auth, bad request) raised immediately without retry
- Fallback to Grok if `ANTHROPIC_API_KEY` not set

### Context Built By (55 modules)
All tiers feed into the system prompt / user prompt passed to Claude:

| Tier | Modules | Purpose |
|---|---|---|
| Tier 1 — Data | 10 modules | Validate, deduplicate, fuse multi-source data |
| Tier 2 — Planning | 8 modules | Narrative arc planning, prioritisation, reasoning |
| Tier 3 — Character | 9 modules | Character memory, personality, relationships |
| Tier 4 — Generation | 10 modules | Lore fusion, dialogue, style, tension, interpolation |
| Tier 5 — QA | 7 modules | Coherence, contradiction, plagiarism checks |
| Tier 6 — Analytics | 6 modules | Metrics, feedback loop, trend detection |
| Tier 7 — Orchestration | 2 modules | Health monitoring, platform coordination |

---

## 2. Image Generation

### Model
`grok-imagine-image` via xAI API

### API Endpoint
`https://api.x.ai/v1/images/generations`

### Authentication
`GROK_API_KEY` (header: `Authorization: Bearer`)

### Request Format
```json
{
  "model": "grok-imagine-image",
  "prompt": "<image prompt from lore generation>",
  "n": 1,
  "response_format": "url",
  "image": "<base64-encoded reference art (optional)>"
}
```

### Reference Images
Four approved character image sets used as visual references:
- `assets/layers/boys_set_1/boysimagesetone.png`
- `assets/layers/bonnet_styles_boys_set_2/boysimagesettwo.png`
- `assets/layers/females_set_1/girlsimagesetone.png`
- `assets/layers/bonnet_styles_females_set_2/girlsimagesettwo.png`

Gender is auto-detected from lore text; the matching set is loaded and passed
as `image` in the request.

### Response Parsing
The API returns a URL; a second `GET` request downloads the image bytes.

### Error Handling
- On failure, the image is skipped and the Telegram post is sent text-only
- Up to `IMAGE_MAX_FAILS` (50) generation attempts per post

---

## 3. Wiki Updates

### No LLM involved
Wiki updates use **rule-based wikitext formatting** — no AI call is made.

### Flow
1. `gk-brain.py` saves structured update dicts to `wiki-update-queue.json`
2. `wiki-smart-merger.py` reads the queue and:
   - Fetches current page wikitext from Fandom MediaWiki API
   - Smart-merges new entries into the correct section
   - Falls back to append if smart merge is not applicable
3. `wiki-updater.py` provides a simpler append-only fallback

### Fandom Authentication
MediaWiki `clientlogin` flow:
1. `GET /api.php?action=query&meta=tokens&type=login` → `logintoken`
2. `POST /api.php` with `action=clientlogin`, credentials, and `logintoken`
3. Verify `clientlogin.status == "PASS"`
4. `GET /api.php?action=query&meta=tokens` → `csrftoken` for edits

3 retry attempts with exponential backoff on all API calls.

---

## 4. The 4-Brain Architecture

The system is split into four independent agents that communicate via JSON files:

| Brain | File | Primary LLM | Runs |
|---|---|---|---|
| **Lore Brain** | `gk-brain.py` | Claude 3.5 Sonnet (text) + Grok (image) | Every 2 hours |
| **Crawl Brain** | `crawl-brain.py` | None (HTTP only) | Every 2 hours (first) |
| **Analytics Brain** | `analytics-brain.py` | None (rule-based) | Every 2 hours (second) |
| **Wiki Brain** | `wiki-brain.py` | None (MediaWiki API) | Every 2 hours (last) |

### Inter-Brain Communication Files
| File | Written By | Read By |
|---|---|---|
| `crawl-results.json` | Crawl Brain | Lore Brain |
| `recommendations.json` | Analytics Brain | Lore Brain |
| `wiki-update-queue.json` | Lore Brain | Wiki Brain |
| `engagement-tracker.json` | Lore Brain | Analytics Brain |

---

## 5. Secrets Required

| Secret | Used By |
|---|---|
| `ANTHROPIC_API_KEY` | Lore Brain (Claude text generation) |
| `GROK_API_KEY` | Lore Brain (image generation) |
| `TELEGRAM_BOT_TOKEN` | Lore Brain (posting) |
| `TELEGRAM_CHANNEL_ID` / `CHANNEL_CHAT_IDS` | Lore Brain (posting) |
| `FANDOM_BOT_USER` | Wiki Brain |
| `FANDOM_BOT_PASSWORD` | Wiki Brain |
| `FANDOM_WIKI_URL` | Wiki Brain |


