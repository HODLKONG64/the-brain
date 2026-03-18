"""
multi-platform-orchestrator.py - Multi-Platform Orchestrator for GK BRAIN

Coordinates content generation across Telegram, Wiki, and Archive platforms.
Applies platform-specific formatting to base lore content.

Usage (from gk-brain.py):
    from multi_platform_orchestrator import orchestrate_output
    output = orchestrate_output(lore1, lore2, image_prompt1, image_prompt2, updates)
"""

import datetime
import importlib.util
import os

BASE_DIR = os.path.dirname(__file__)

# ---------------------------------------------------------------------------
# Load centralised wiki-formatter module
# ---------------------------------------------------------------------------

def _load_wiki_formatter():
    _path = os.path.join(BASE_DIR, "wiki-formatter.py")
    _spec = importlib.util.spec_from_file_location("wiki_formatter", _path)
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    return _mod

try:
    _wf = _load_wiki_formatter()
    _lore_to_encyclopedic = _wf.lore_to_encyclopedic
    _apply_wikilinks = _wf.apply_wikilinks
    _build_cite_ref = _wf.build_cite_ref
    _build_category_tags = _wf.build_category_tags
    _ensure_references_section = _wf.ensure_references_section
except Exception as _wf_exc:
    print(f"[multi-platform-orchestrator] wiki-formatter unavailable ({_wf_exc}); using stubs.")
    def _lore_to_encyclopedic(t): return t
    def _apply_wikilinks(t): return t
    def _build_cite_ref(u, ti, ts): return ""
    def _build_category_tags(ut, yr): return ""
    def _ensure_references_section(t): return t


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
    """Format lore for wiki: encyclopedic, third person, structured with citations."""
    now = datetime.datetime.utcnow()
    date_str = now.strftime("%Y-%m-%d %H:%M UTC")
    year = now.strftime("%Y")
    ts_iso = now.isoformat() + "Z"

    # Convert first person to encyclopedic third person
    wiki_text = _lore_to_encyclopedic(lore)

    # Apply wikilinks to body text
    wiki_text = _apply_wikilinks(wiki_text)

    # Build source references
    ref_lines: list[str] = []
    for u in updates[:3]:
        url = u.get("url", "") or u.get("source", "")
        title = u.get("title", "GK BRAIN source")
        if url:
            ref_lines.append(_build_cite_ref(url, title, ts_iso))

    if not ref_lines:
        ref_lines.append(_build_cite_ref("", "GK BRAIN autonomous generation", ts_iso))

    refs_inline = "".join(ref_lines)

    wiki_content = (
        f"== {date_str} — Entry {post_number} ==\n\n"
        f"=== Summary ===\n"
        f"{wiki_text.strip()}{refs_inline}\n"
    )

    # Append references section and category tags
    wiki_content = _ensure_references_section(wiki_content)
    cat_tags = _build_category_tags("lore-post", year)
    if cat_tags:
        wiki_content = wiki_content.rstrip() + "\n\n" + cat_tags + "\n"

    return {
        "content": wiki_content,
        "platform": "wiki",
        "char_count": len(wiki_content),
    }


def format_lore_for_wiki(lore: str, updates: list) -> str:
    """
    Convert a lore post to encyclopedic MediaWiki format.

    This is the public entry point for converting raw lore text to wiki format.
    It can be imported and called by any module that needs to write lore posts
    to the Fandom wiki (e.g. wiki-smart-merger.py, wiki-updater.py).

    Args:
        lore: Raw lore text (may be first-person Telegram style).
        updates: List of update dicts that informed this lore post.

    Returns:
        Fully formatted MediaWiki wikitext string.
    """
    result = _format_wiki(lore, 1, updates)
    return result.get("content", lore)


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

