"""
multi-platform-orchestrator.py - Multi-Platform Orchestrator for GK BRAIN

Coordinates content generation across Telegram, Wiki, and Archive platforms.
Applies platform-specific formatting to base lore content.

Usage (from gk-brain.py):
    from multi_platform_orchestrator import orchestrate_output
    output = orchestrate_output(lore1, lore2, image_prompt1, image_prompt2, updates)
"""

import datetime
import os

BASE_DIR = os.path.dirname(__file__)


def _format_telegram(lore: str, image_prompt: str) -> dict:
    """Format lore for Telegram: casual, punchy, personal voice."""
    formatted = lore.strip()
    # Ensure reasonable paragraph breaks
    if len(formatted) > 500 and "\n\n" not in formatted:
        mid = len(formatted) // 2
        space_idx = formatted.find(" ", mid)
        if space_idx > 0:
            formatted = formatted[:space_idx] + "\n\n" + formatted[space_idx+1:]

    return {
        "text": formatted,
        "image_prompt": image_prompt,
        "platform": "telegram",
        "char_count": len(formatted),
    }


def _format_wiki(lore: str, post_number: int, updates: list) -> dict:
    """Format lore for wiki: encyclopedic, third person, structured."""
    now = datetime.datetime.utcnow()
    date_str = now.strftime("%Y-%m-%d %H:%M UTC")

    # Convert first person to third person (basic)
    wiki_text = lore.replace(" I ", " the artist ").replace(" my ", " the artist's ")
    wiki_text = wiki_text.replace("I'm ", "The artist is ").replace("I've ", "The artist has ")

    sources = []
    for u in updates[:3]:
        url = u.get("url", "") or u.get("source", "")
        if url:
            sources.append(f"* {url}")

    source_section = "\n".join(sources) if sources else "* GK BRAIN autonomous generation"

    wiki_content = (
        f"== {date_str} — Entry {post_number} ==\n\n"
        f"{wiki_text.strip()}\n\n"
        f"=== Sources ===\n{source_section}"
    )

    return {
        "content": wiki_content,
        "platform": "wiki",
        "char_count": len(wiki_content),
    }


def _format_archive(lore: str, image_prompt: str, updates: list) -> dict:
    """Format lore for archive: reference entry, dates prominent, factual."""
    now = datetime.datetime.utcnow()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M UTC")

    categories = list({u.get("category", "general") for u in updates})

    archive_entry = (
        f"DATE: {date_str}\n"
        f"TIME: {time_str}\n"
        f"CATEGORIES: {', '.join(categories) if categories else 'general'}\n"
        f"IMAGE_PROMPT: {image_prompt}\n\n"
        f"ENTRY:\n{lore.strip()}\n\n"
        f"SOURCES_COUNT: {len(updates)}"
    )

    return {
        "content": archive_entry,
        "platform": "archive",
        "char_count": len(archive_entry),
    }


def orchestrate_output(
    lore1: str,
    lore2: str,
    image_prompt1: str,
    image_prompt2: str,
    updates: list,
) -> dict:
    """
    Apply platform-specific formatting to base lore for all output channels.

    Args:
        lore1: First lore post text.
        lore2: Second lore post text.
        image_prompt1: Image generation prompt for post 1.
        image_prompt2: Image generation prompt for post 2.
        updates: List of update dicts used in generation.

    Returns:
        Dict with keys: telegram, wiki, archive — each containing
        platform-formatted content.
    """
    try:
        telegram_output = {
            "post1": _format_telegram(lore1, image_prompt1),
            "post2": _format_telegram(lore2, image_prompt2),
            "image_prompts": [image_prompt1, image_prompt2],
        }

        wiki_output = {
            "post1": _format_wiki(lore1, 1, updates),
            "post2": _format_wiki(lore2, 2, updates),
        }

        archive_output = {
            "post1": _format_archive(lore1, image_prompt1, updates),
            "post2": _format_archive(lore2, image_prompt2, updates),
        }

        return {
            "telegram": telegram_output,
            "wiki": wiki_output,
            "archive": archive_output,
        }
    except Exception as e:
        print(f"[multi-platform-orchestrator] Error: {e}")
        return {
            "telegram": {"post1": {"text": lore1}, "post2": {"text": lore2}},
            "wiki": {"post1": {"content": lore1}, "post2": {"content": lore2}},
            "archive": {"post1": {"content": lore1}, "post2": {"content": lore2}},
        }
