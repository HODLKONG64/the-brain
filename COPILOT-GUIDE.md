# GitHub Copilot: New Agent Session vs New Chat — What's Best for This Repo?

## Short Answer

**Use a New Agent Session** for almost everything in this repository.

---

## Why This Repo Needs an Agent Session

The GK Brain repository is large and deeply interconnected:

- `gk-brain-complete.md` is the master rules file (~100KB+)
- `MASTER-CHARACTER-CANON.md` and `character-bible.md` cross-reference each other
- `gk-brain.py` loads from several markdown files at runtime
- Rule changes in one file can break behavior in another

A **New Agent Session** (Copilot Agent Mode) can:

- Read multiple files and understand how they connect
- Run code, lint, and tests in the repo
- Make multi-file edits in a single session
- Iterate on changes based on real output


A **New Chat** cannot do any of that — it only answers questions.

---

## When to Use Each

| Task | Best Choice |
|---|---|
| Update a rule in `gk-brain-complete.md` | ✅ New Agent Session |
| Add or edit a character in `MASTER-CHARACTER-CANON.md` | ✅ New Agent Session |
| Debug `gk-brain.py` (Telegram posting, crawl issues) | ✅ New Agent Session |
| Change the fame cycle or dream rotation logic | ✅ New Agent Session |
| Add a new slash command to the bot | ✅ New Agent Session |
| Cross-check lore consistency across files | ✅ New Agent Session |
| Ask a quick question ("what does `/expand` do?") | 💬 New Chat is fine |
| Get a plain-English explanation of a single function | 💬 New Chat is fine |

---

## When to Start a New Agent Session vs Continue an Old One

- **Start a new session** when beginning a different, unrelated task.
- **Continue the same session** for follow-up edits on the same feature — the agent retains full context.
- The agent always has access to the full repo, so starting fresh is safe. There is no persistent state inside the agent session itself.

---

## Quick Copilot Tips for This Repo

1. **Always mention the file by name** — e.g. "update `gk-brain-complete.md`" not just "update the rules".
2. **Be specific about the rule code** — rules are tagged (e.g. `MR-A6`, `AC-1`, `BF-3`). Use those tags so the agent finds the right rule instantly.
3. **One goal per session** — editing the dream rotation AND the art rules in the same session is fine, but mixing unrelated tasks leads to larger, harder-to-review changes.
4. **Review the diff before approving** — the agent will show exactly which lines changed. Check `gk-brain.py` carefully since it's the live runtime file.
