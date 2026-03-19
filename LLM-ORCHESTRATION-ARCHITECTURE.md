# LLM ORCHESTRATION ARCHITECTURE — GK BRAIN

How GK BRAIN routes language model and image generation calls.

---

## 1. LLM Routing Overview

| Task | Primary model | Fallback model | Env key required |
|---|---|---|---|
| Lore text generation (Posts 1 & 2) | Claude 3.5 Sonnet | Grok (`GROK_TEXT_MODEL`) | `ANTHROPIC_API_KEY` (primary) / `GROK_API_KEY` (fallback) |
| Image generation (Post 2 image) | Grok image model | None — plain text fallback | `GROK_API_KEY` |

**Rule DB-11:** When `ANTHROPIC_API_KEY` is set, ALL primary lore text routes through Claude 3.5 Sonnet
via `_llm_chat()`. Grok text generation is used only when `ANTHROPIC_API_KEY` is absent.
Image generation **always** uses Grok regardless of `ANTHROPIC_API_KEY` status.

---

## 2. Claude Integration (`gk-brain.py → _llm_chat()`)

```
ANTHROPIC_API_KEY present?
  YES → POST https://api.anthropic.com/v1/messages
        model: claude-3-5-sonnet-20241022
        max_tokens: configurable (default ≈ 2048)
        system: brain rules from gk-brain-complete.md
        user: lore prompt with faction/character context
        → returns generated lore text
  NO  → fall through to Grok text generation
```

The system prompt is loaded from `gk-brain-complete.md` via the `BRAIN_RULES_FILE` constant
at module load time.

---

## 3. Grok Text Integration (Fallback)

```
GROK_API_KEY present, ANTHROPIC_API_KEY absent?
  YES → POST https://api.x.ai/v1/chat/completions
        model: GROK_TEXT_MODEL env var (default: grok-3-latest)
        messages: [{role: system, content: brain_rules},
                   {role: user, content: lore_prompt}]
        → returns generated lore text
```

---

## 4. Grok Image Generation

Post 2 always carries an image (DB-5). The image generation flow:

```
_generate_image(prompt) via Grok API
  → POST https://api.x.ai/v1/images/generations
    model: aurora (or configured image model)
    prompt: scene description derived from Post 2 lore text
    → returns image bytes in memory

Image bytes → _telegram_send_photo()  (streamed directly, never written to disk — DB-13)
Image bytes discarded after send
```

If image generation fails, Post 2 falls back to plain text (the image prompt is still generated
and logged, but not retried).

---

## 5. Context Injected into Every LLM Call

Every lore generation prompt includes:

1. **Brain rules** — full content of `gk-brain-complete.md` as system prompt
2. **Lore history** — last 40,000 chars of `lore-history.md` for continuity (DB-9)
3. **Canon signal** — up to 20% of the prompt from `brain1-canon.json` (DB-2); signals older than 7 days are excluded (DB-3)
4. **Recommendations** — top faction/character picks from `recommendations.json` (Brain 2 output)
5. **Time block** — current UTC hour → mapped to a posting persona / mood

---

## 6. Output Constraints

| Output | Hard limit | Enforcement |
|---|---|---|
| Message 1 (text) | 4,096 UTF-8 chars | Truncated at `gk-brain.py:_post_message()` |
| Message 2 (caption) | 1,024 UTF-8 chars | Truncated at `gk-brain.py:_post_caption()` |
| Image prompt | 1,000 chars (Grok limit) | Trimmed before API call |

---

## 7. Error Handling

| Error | Action |
|---|---|
| Claude API error (any 4xx/5xx) | Fall through to Grok text fallback |
| Grok text API error | Log error; skip lore post for this cycle |
| Grok image API error | Skip image; post Message 2 as plain text |
| `EnvironmentError` (missing keys) | Raised at `main()` start; entire brain exits non-zero (DB-10) |

---

## 8. Model Configuration

| Variable | Default | Override via |
|---|---|---|
| Claude text model | `claude-3-5-sonnet-20241022` | Hardcoded in `gk-brain.py` |
| Grok text model | `grok-3-latest` | `GROK_TEXT_MODEL` env var |
| Grok image model | `aurora` | Hardcoded in `gk-brain.py` |
