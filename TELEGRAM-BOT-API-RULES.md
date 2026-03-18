# TELEGRAM BOT API — OFFICIAL RULES & COMPLIANCE (GK BRAIN)

This file documents all official Telegram Bot API rules, rate limits, and best practices
that the GK BRAIN agent MUST follow. Updated: 2026-03-18.

---

## 1. RATE LIMITS (Official Telegram Policy)

### Per-Bot Global Limits
- **30 messages/second** maximum across all chats combined.
- **1 message/second per individual chat** — never send 2 messages to the same chat in under 1 second.
- Bulk broadcasts to more than 30 different chats: max **30 messages/second** total.
- If a `429 Too Many Requests` error is received, honour the `retry_after` field (in seconds) EXACTLY before retrying.

### Per-Chat Limits
- **1 message/second** to a single chat/channel.
- For channels with more than 100 members: Telegram may throttle faster than 1/second.
- `time.sleep(2)` between Message 1 and Message 2 (same chat) satisfies this rule. (See DB-12.)

### Inline Query Limits
- Max **1 inline query answer per user per second**.

---

## 2. MESSAGE SIZE LIMITS

| Content Type | Limit |
|---|---|
| Text message (sendMessage) | 4,096 UTF-8 characters |
| Caption (photo/video/document) | 1,024 UTF-8 characters |
| Inline keyboard callback data | 64 bytes |
| File size via Bot API | 50 MB |
| Photo file size | 10 MB |

**GK BRAIN must truncate all text messages at 4,096 characters and captions at 1,024 characters before sending.**

---

## 3. FLOOD WAIT / ERROR HANDLING

| Error Code | Meaning | Required Action |
|---|---|---|
| 400 Bad Request | Malformed request | Log and skip; never retry without fixing |
| 401 Unauthorized | Invalid bot token | Raise EnvironmentError; halt run |
| 403 Forbidden | Bot kicked/blocked from chat | Log chat_id; skip that chat for this run |
| 409 Conflict | Multiple bot instances polling | Only one getUpdates poller at a time |
| 429 Too Many Requests | Rate limit hit | Sleep retry_after seconds; retry once |
| 500/502/503/504 | Telegram server error | Exponential backoff; max 3 retries |

**Never retry a 400 or 403 without a code fix. Never retry a 429 without sleeping first.**

---

## 4. GETUPDATE / WEBHOOK RULES

- **Never run getUpdates and a webhook simultaneously** — this causes a 409 Conflict.
- Always pass the last update_id + 1 as the offset parameter to getUpdates to prevent replaying old updates.
- bot-state.json stores the last processed update_id — this MUST be read at the start of every reply cycle and written at the end.
- Webhook secret tokens, if used, must be validated server-side for every incoming request.

---

## 5. PINNING MESSAGES

- pinChatMessage requires the bot to have "Pin Messages" admin right in the target chat.
- Always use disable_notification=True for silent pins (no push notification to members).
- Pinning failure MUST NOT block or interrupt the posting flow. (See DB-13.)
- Each basic group can only have one pinned message; channels and supergroups support multiple pins.

---

## 6. BOT PERMISSIONS (Admin Rights Required)

| Action | Required Admin Right |
|---|---|
| Send messages to channel | Post Messages |
| Pin messages | Pin Messages |
| Delete messages | Delete Messages |
| Edit others messages | Edit Messages |
| Invite users | Invite Users via Link |

The GK BRAIN bot requires at minimum: **Post Messages + Pin Messages** in every target channel/group.

---

## 7. CONTENT POLICY

- Bots MUST NOT send spam, unsolicited commercial messages, or misleading content.
- Bots MUST NOT harvest user data beyond what is needed for their stated function.
- Bots operating in channels/groups must comply with Telegram Terms of Service and applicable local laws.
- NSFW/adult content is only permitted in age-gated channels explicitly approved by Telegram.
- Automated bots must not impersonate real humans in ways that deceive users.

---

## 8. TELEGRAM CHANNEL VS GROUP RULES

| Feature | Channel | Supergroup | Basic Group |
|---|---|---|---|
| Anonymous posting | Yes | No | No |
| Multiple pinned messages | Yes | Yes | No |
| Max members | Unlimited | Unlimited | 200 |
| Edit history | Yes | Yes | No |
| Message threading | No | Yes (with topics) | No |

---

## 9. REPLY HANDLING RULES

- Reply to a specific message using reply_to_message_id parameter.
- Max 20 replies per user per 24 hours (GK BRAIN internal limit — enforced by reply-tracker.json). This is stricter than Telegram own limits, which is intentional to prevent spam reports.
- Only reply to messages that contain relevant Moonboys/GK topic keywords (enforced by GK BRAIN keyword filter).
- Never reply to other bots.

---

## 10. COMPLIANCE CHECKLIST (Run Before Each Posting Cycle)

- TELEGRAM_BOT_TOKEN is set and valid (DB-10 fast-fail)
- CHANNEL_CHAT_IDS has at least one valid chat ID
- Message 1 text is 4,096 characters or fewer
- Message 2 caption is 1,024 characters or fewer
- time.sleep(2) between Message 1 and Message 2 in same chat (DB-12)
- pinChatMessage with disable_notification=True after Message 2 (DB-13)
- On 429 error: sleep retry_after, then retry once only
- On 403 error: log and skip chat; do not retry
- Never run concurrent getUpdates polling instances

---

## 11. ENFORCEMENT IN GK BRAIN

These rules are enforced by the following components:
- gk-brain.py: _telegram_post(), _telegram_send_photo(), _pin_message(), post_to_telegram()
- brain-rules.md: DB-10 (env fast-fail), DB-12 (rate guard), DB-13 (auto-pin), DB-14 (Telegram API compliance)
- TELEGRAM-BOT-API-RULES.md: this file — authoritative reference
- master-backup-agent.py: validates Telegram compliance on every sync cycle
