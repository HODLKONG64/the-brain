# TELEGRAM NARRATOR SYSTEM ARCHITECTURE

How GK BRAIN's Telegram narrator works — from lore generation to message delivery.

---

## 1. Narrator Identity

The GK narrator is a **first-person voice character** — GK himself:
- UK graffiti artist, DJ, parkour runner, carp fisherman, web3 entrepreneur
- Posts in authentic, informal UK English
- Weaves real-world Web3 events with Crypto Moonboys universe lore
- Never breaks character; never reveals the agent behind the posts

---

## 2. Posting Architecture

```
gk-brain.py
    │
    ├── Load lore-history.md (last 40,000 chars — DB-9)
    ├── Load brain1-canon.json signals (≤20% injection — DB-2)
    ├── Load recommendations.json (Brain 2 priority picks)
    │
    ├── Generate Post 1 text  ──→  Claude 3.5 Sonnet (primary) / Grok (fallback) — DB-11
    ├── Generate Post 2 text  ──→  Claude 3.5 Sonnet (primary) / Grok (fallback)
    ├── Generate Post 2 image ──→  Grok Aurora (always) — DB-5, DB-13
    │
    ├── For each chat_id in CHANNEL_CHAT_IDS:
    │       ├── sendMessage(Post 1 text)              ← max 4,096 chars
    │       ├── time.sleep(2)                         ← DB-12
    │       ├── sendPhoto(Post 2 image, caption=Post 2 text)  ← caption max 1,024 chars
    │       └── pinChatMessage(msg2_id, disable_notification=True)  ← DB-14
    │
    └── Save lore-history.md, bot-state.json, engagement-tracker.json
```

---

## 3. Lore Generation Pipeline

### Context Assembly
Every generation call receives:
1. Full brain rules from `gk-brain-complete.md` (system prompt)
2. Lore history (last 40,000 chars) for continuity
3. Canon signals from `brain1-canon.json` (up to 20% of content)
4. Analytics recommendations (faction/character focus for this cycle)
5. Current time block → maps to narrator mood and topic category

### Dual-Post Structure
- **Post 1** — Scene-setter. Introduces the situation, location, or faction event.
- **Post 2** — Action/revelation. Develops the thread. Always accompanied by an AI image (DB-5).
- Posts are narratively consecutive — Post 2 must follow from Post 1.

---

## 4. Image Generation (DB-5 & DB-13)

1. Image prompt is extracted from concrete scene elements in Post 2 text.
2. Grok `aurora` model generates the image in memory as raw bytes.
3. Bytes are streamed directly to Telegram via `sendPhoto` multipart upload.
4. Bytes are discarded immediately after the successful send.
5. **No image file is ever written to disk or committed to the repo.**

If image generation fails: Post 2 is sent as plain text. The image prompt is logged for audit.

---

## 5. Reply System

The bot also responds to inbound messages in chats where it has read access:

```
getUpdates(offset=last_update_id+1)
    │
    ├── For each update:
    │       ├── Check: does message contain project keywords?  → YES: eligible for reply
    │       ├── Check: user reply count today < 20?           → YES: eligible for reply
    │       ├── Check: sender is not another bot?             → YES: eligible for reply
    │       │
    │       └── Generate reply via LLM → sendMessage(reply_to_message_id=...)
    │
    └── Save last_update_id to bot-state.json
```

**Rate limit:** Max 20 replies per user per 24 hours (enforced by `reply-tracker.json`).

---

## 6. State Files

| File | Contents | Written by |
|---|---|---|
| `bot-state.json` | Last processed `update_id` | `gk-brain.py` end of every run |
| `reply-tracker.json` | Per-user `{count, date, failed_keywords}` | `gk-brain.py` reply loop |
| `lore-history.md` | Rolling 40,000-char lore buffer | `gk-brain.py` save_lore_history() |
| `engagement-tracker.json` | Per-post view/reaction metrics | `gk-brain.py` |

---

## 7. Narrator Tone Guidelines

- Authentic UK slang and cadence
- Combines street-art culture with blockchain/NFT narrative
- References real project events (verified via Crawl Brain — NEVER from Telegram itself)
- Dark humour, passion, and urgency in equal measure
- Each pair of posts should feel like a genuine update from the field

---

## 8. Related Files

| File | Purpose |
|---|---|
| `gk-brain.py` | Full narrator implementation |
| `gk-brain-complete.md` | Master brain rules loaded as LLM system prompt |
| `TELEGRAM-BOT-API-RULES.md` | Official Telegram compliance rules |
| `READMENOWBOT.md` | Quick-start bot setup guide |
| `LLM-ORCHESTRATION-ARCHITECTURE.md` | Model routing architecture |
