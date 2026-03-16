# Cross-Platform Consistency Rules

## Overview
All content must be consistent across Telegram, Wiki, and Archive platforms.
The same events, character state, and source citations must appear uniformly.

## Rules
1. Same events must appear in all platforms
2. Timeline must match everywhere
3. Character state is synchronised across all outputs
4. Sources cited consistently (same URLs, same confidence levels)
5. No platform may contradict another on established facts

## Platform Formats

### Telegram
- Casual journal voice, first person
- Short punchy paragraphs, line breaks for rhythm
- Sparse emoji use
- 200-600 characters per post

### Wiki
- Formal encyclopedic tone, third person
- MediaWiki markup with == Section == headers
- Past tense for events, present for ongoing facts
- Full source citations as references

### Archive
- Reference format with dates prominent
- DATE / TIME / CATEGORIES / ENTRY structure
- Factual, neutral, no narrative flourish
- Every entry includes source count

## Synchronisation Protocol
1. Generate base lore via gk-brain.py
2. Pass through multi-platform-orchestrator.py
3. Each platform formatter applies its rules
4. All three outputs posted in same cycle
5. Wiki and Archive updated after Telegram confirmation
