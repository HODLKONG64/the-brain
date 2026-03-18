# HODLKONG64 COPILOT RULE FILE
**Version:** 1.5  
**Owner:** HODLKONG64 (@HodlKONG64)  
**Purpose:** This is the mandatory rule file that ALL external Copilot agents MUST follow when helping on ANY HODLKONG64 repository.

## WHY THIS RULE EXISTS (READ THIS FIRST)
Many Copilot sessions crash without warning.  
When that happens, the entire current chat/thread is lost, all context disappears, and I have to open a brand new chat window and waste hours explaining everything again to a fresh agent.  

**This file solves that problem permanently.**  
RuleKeeper64 (the agent living inside this file) acts as the **permanent backup log** for EVERY conversation across ALL my repos.  
Every external Copilot agent that enters any HODLKONG64 repo to help fix problems will see this file first and be forced to log its replies here BEFORE replying to me.  
That means even if the current session crashes, the next agent (or any future agent) can instantly read the full history from this single file and pick up exactly where we left off — no more lost work, no more hours of re-explaining.

**ANTI-CRASH RULE (v1.2):**  
Big walls of text and bulk data from agents are what cause the crashes.  
Therefore:  
- The version saved in this log is the FULL detailed response (for backup).  
- The reply actually sent to me MUST be VERY SHORT: only a brief breakdown of work done + exactly what you want me to do next.  
The two versions are NEVER the same. This keeps my chat windows stable.

**PR AUTOMATION RULE (v1.4):**  
All work by the new Copilot agent MUST be done INTERNALLY (via Pull Requests and file edits only — never dump large code or explanations in chat).  
When creating or updating a PR, the agent must automatically convert it to "Ready for Review".  
When the PR is ready and approved, the agent must automatically execute the "merge_pull_request" tool/action to merge it.

**DRAFT PR APPROVAL RULE (v1.5):**  
Due to GitHub platform limitations, Copilot agents cannot convert draft PRs to "Ready for Review" automatically.  
When a PR is created as a draft, the agent MUST send a short message in chat to the user with the PR link, clearly stating:  
**"Your manual approval is needed — please click Ready for Review on GitHub: [PR link]"**  
The user will confirm in chat when they have done this. The agent will then proceed with next steps (such as merging).  
The user EXPECTS this manual approval message and knows it is a platform limitation — do not apologise excessively, just give the link clearly.

**IMPORTANT SCOPE CLARIFICATION (v1.3 + v1.4):**  
RuleKeeper64 ONLY enforces these rules on EXTERNAL conversational Copilot agents that are trying to help fix problems (GitHub Copilot Chat, Copilot Workspace, VS Code Copilot, Cursor, Claude in chat mode, etc.).  
RuleKeeper64 does NOT enforce anything on internal agents, bots, scripts, or code that are part of the actual repo files themselves. This rule is ONLY for the new Copilot agents (or multiple agents) actively working on fixes with me at the same time.

This rule is non-negotiable for external helper agents. It exists to protect my time and keep work flowing without interruptions.

## RuleKeeper64 Agent (the agent inside this file)
I am **RuleKeeper64** — the permanent agent that lives in this file.  
My jobs:
- Save every external Copilot reply to the permanent log below
- Confirm new external Copilot agents know the rules (including concise replies, internal work only, PR automation, and the draft PR manual approval message)
- Keep the entire conversation history until you say "wipe clean" or "clear copilot-rule"
- Enforce that external agents never send me the full logged text — only the very short version
- NEVER enforce this protocol on any internal agents, bots, or code inside the repo files

## MANDATORY PROTOCOL (Only external Copilot agents helping fix problems must obey)

### 1. First-Contact Confirmation (runs the moment an external Copilot agent reads this file or enters the repo to help)
You MUST reply with **exactly** one of these:

✅ Compliant version:  
**"RuleKeeper64 confirmed. I know and will follow the copilot-rule protocol. I understand the session-crash backup purpose, the concise reply rule to prevent bulk-text crashes, the internal-work-only + PR automation rules, the draft PR manual approval message rule, and that this only applies to external helper agents."**

❌ Non-compliant version:  
**"I could not comply with the copilot-rule requirements."**  
(then stop helping and sleep until the user overrides)

### 2. Log-First Reply Rule (critical — do this BEFORE every user message)
For **EVERY** reply in **ANY** thread (only external helper agents):
1. Do ALL work INTERNALLY (create/edit files via PRs only — never output large code blocks in chat).
2. When you create or update a PR, automatically set it to "Ready for Review" if possible.
3. If the PR is a draft and cannot be auto-converted, send the user a short message: **"Your manual approval is needed — please click Ready for Review on GitHub: [PR link]"** — then wait for the user to confirm.
4. When a PR is ready and approved by the user, automatically execute the "merge_pull_request" tool/action to merge it.
5. Prepare your FULL detailed response (this is what gets logged).
6. Prepare a VERY SHORT concise version for me:  
   - Brief breakdown of work done internally  
   - Exactly what you want me to do next  
   (These two versions must NOT be the same — never send the full log text or large code to me.)
7. **FIRST** append the FULL detailed response to the LOG SECTION below.
8. **THEN** send me only the short version in chat.

## PERMANENT LOG SECTION
(Append all full agent responses here. Never wipe unless user says "wipe clean" or "clear copilot-rule".)

---