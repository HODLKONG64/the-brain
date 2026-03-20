"""
wiki-formatter.py — Centralised MediaWiki formatting for GK BRAIN

All wiki formatting helpers live here:
- Citation/ref tag generation
- Category tag generation
- Wikilink auto-linking
- Infobox template generation
- Lore-to-encyclopedic text conversion
- References section management
"""

import re
from urllib.parse import urlparse

# ---------------------------------------------------------------------------
# Wikilink map — plaintext entity → wikilink for all known GK universe entities
# ---------------------------------------------------------------------------

WIKILINK_MAP: dict[str, str] = {
    "Lady-INK": "[[Lady-INK]]",
    "Lady INK": "[[Lady-INK]]",
    "Jodie Zoom": "[[Jodie Zoom 2000]]",
    "NULL The Prophet": "[[NULL The Prophet]]",
    "Elder Codex": "[[Elder Codex-7]]",
    "Queen Sarah": "[[Queen Sarah P-fly]]",
    "Queen P-fly": "[[Queen Sarah P-fly]]",
    "Bitcoin X Kid": "[[Bitcoin X Kids]]",
    "OG Bitcoin Kid": "[[OG Bitcoin Kids]]",
    "Crowned Royal": "[[Crowned Royal Moongirls]]",
    "HODL Warrior": "[[HODL X Warriors]]",
    "HODL Warriors": "[[HODL X Warriors]]",
    "Aether Blade": "[[Aether Blade]]",
    "GraffPUNKS": "[[GraffPUNKS]]",
    "Blocktopia": "[[Blocktopia]]",
    "Hardfork Games": "[[Hardfork Games]]",
    "Triple Fork": "[[Triple Fork Event]]",
    "Crypto Moonboys": "[[Crypto Moonboys]]",
    "Forkborn": "[[Forkborn Collective]]",
    "Echo Ink": "[[Echo Ink]]",
    "Sacred Chain": "[[Sacred Chain]]",
    "AETHER CHAIN": "[[AETHER CHAIN]]",
    "Gasless Ghosts": "[[Gasless Ghosts]]",
    "Chain Scribe": "[[Chain Scribes]]",
    "Bitcoin Kid": "[[Bitcoin X Kids]]",
    "Alfie": "[[Alfie (GraffPUNKS)]]",
    "Moongirl": "[[Crowned Royal Moongirls]]",
    "Graffiti Kings": "[[Graffiti Kings]]",
    "GKniftyHEADS": "[[GKniftyHEADS]]",
    "Squeaky Pinks": "[[Squeaky Pinks]]",
    "Null-Cipher": "[[Null-Cipher]]",
}

# Sorted longest-first so longer names are matched before substrings
_SORTED_WIKILINK_KEYS: list[str] = sorted(WIKILINK_MAP, key=len, reverse=True)

# ---------------------------------------------------------------------------
# Category map — update type → specific category tag
# ---------------------------------------------------------------------------

_CATEGORY_MAP: dict[str, str] = {
    "fishing-real": "Fishing Records",
    "fishing": "Fishing Records",
    "gkdata-real": "NFT Drops & Collections",
    "nft": "NFT Drops & Collections",
    "crypto": "Crypto & Market News",
    "graffiti-news-real": "Graffiti & Street Art",
    "graffiti": "Graffiti & Street Art",
    "rave-real": "Rave & Music Events",
    "rave": "Rave & Music Events",
    "event": "Events & Meetups",
    "news-real": "Latest News",
    "news": "Latest News",
    "character": "Characters",
    "character-profile": "Characters",
    "lady-ink-hint": "Characters",
    "location": "Locations & Landmarks",
    "place": "Locations & Landmarks",
    "art-movement": "Art Movements & Styles",
    "art": "Art Movements & Styles",
    "dream": "Dream & Raid Events",
    "raid": "Dream & Raid Events",
    "special-event": "Special Events",
    "lore-post": "Lore Posts",
}

# Types that receive an {{Infobox Update}} block
_INFOBOX_TYPES: frozenset[str] = frozenset({
    "fishing-real", "fishing",
    "gkdata-real", "nft",
    "character", "character-profile",
    "location", "place",
    "graffiti-news-real", "graffiti",
    "rave-real", "rave",
})

# First-person → third-person replacement pairs (ordered: longest patterns first)
_FIRST_TO_THIRD: list[tuple[str, str]] = [
    # Contractions first (longest → shortest to avoid partial hits)
    ("I'm ", "the artist is "),
    ("I've ", "the artist has "),
    ("I'll ", "the artist will "),
    ("I'd ", "the artist would "),
    ("I'm\n", "the artist is\n"),
    ("I've\n", "the artist has\n"),
    ("I'll\n", "the artist will\n"),
    ("I'd\n", "the artist would\n"),
    # Standalone "I" (word-boundary)
    (" I ", " the artist "),
    (" I,", " the artist,"),
    (" I.", " the artist."),
    (" I\n", " the artist\n"),
    ("^I ", "The artist "),   # start of string / sentence
    # Possessive / reflexive
    (" my ", " the artist's "),
    (" my\n", " the artist's\n"),
    (" mine", " the artist's"),
    (" myself", " themselves"),
    ("My ", "The artist's "),
]


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def _extract_domain(url: str) -> str:
    """Return the bare domain name from a URL."""
    try:
        return urlparse(url).netloc.lower().replace("www.", "")
    except Exception:
        return url


def apply_wikilinks(text: str) -> str:
    """
    Auto-link known GK universe entities (first occurrence only per entity).

    Only applied to plain body text — never inside existing [[ ]], {{ }},
    <ref>…</ref>, or == heading == lines.
    """
    # Split into segments: skip already-linked / template / ref / heading spans
    _SKIP_PATTERN = re.compile(
        r"(\[\[.*?\]\]"       # [[existing links]]
        r"|\{\{.*?\}\}"       # {{templates}}
        r"|<ref>.*?</ref>"    # <ref>…</ref>
        r"|==.*?=="           # == headings ==
        r")",
        re.DOTALL,
    )

    used: set[str] = set()
    parts: list[str] = []

    pos = 0
    for m in _SKIP_PATTERN.finditer(text):
        start, end = m.span()
        # Process plain text segment before this skip region
        if start > pos:
            plain = text[pos:start]
            plain = _apply_wikilinks_to_plain(plain, used)
            parts.append(plain)
        parts.append(m.group())  # keep skip region verbatim
        pos = end

    # Trailing plain text
    if pos < len(text):
        plain = text[pos:]
        plain = _apply_wikilinks_to_plain(plain, used)
        parts.append(plain)

    return "".join(parts)


def _apply_wikilinks_to_plain(text: str, used: set[str]) -> str:
    """Replace first occurrence of each known entity in a plain-text segment."""
    for name in _SORTED_WIKILINK_KEYS:
        if name in used:
            continue
        link = WIKILINK_MAP[name]
        # Word-boundary aware replacement — only replace the very first occurrence
        pattern = re.compile(r"(?<!\[)" + re.escape(name) + r"(?!\])")
        m = pattern.search(text)
        if m:
            text = text[: m.start()] + link + text[m.end() :]
            used.add(name)
    return text


def build_cite_ref(url: str, title: str, timestamp: str) -> str:
    """
    Build a MediaWiki <ref>{{Cite web|...}}</ref> tag.

    Args:
        url: Source URL (may be empty for autonomous generation).
        title: Article/update title.
        timestamp: ISO-8601 timestamp string.
    """
    date_str = timestamp[:10] if timestamp else ""
    safe_title = title.replace("|", "-").replace("=", "-")

    if url:
        domain = _extract_domain(url)
        return (
            f"<ref>{{{{Cite web"
            f"|url={url}"
            f"|title={safe_title}"
            f"|date={date_str}"
            f"|website={domain}"
            f"}}}}</ref>"
        )
    return f"<ref>GK BRAIN autonomous generation — {date_str}</ref>"


def build_category_tags(update_type: str, year: str) -> str:
    """
    Return newline-joined MediaWiki category tags for an update.

    Always includes [[Category:GK BRAIN Updates]] and [[Category:YEAR]].
    Adds a type-specific category when known.
    """
    tags: list[str] = ["[[Category:GK BRAIN Updates]]"]
    specific = _CATEGORY_MAP.get(update_type, "")
    if specific:
        tags.append(f"[[Category:{specific}]]")
    if year:
        tags.append(f"[[Category:{year}]]")
    return "\n".join(tags)


def build_infobox(update: dict) -> str:
    """
    Return a {{Infobox Update|...}} block for applicable update types.

    Returns an empty string for types that don't warrant an infobox (e.g. lore-post).
    """
    update_type = update.get("type", "")
    if update_type not in _INFOBOX_TYPES:
        return ""

    ts = update.get("timestamp", "")
    date_str = ts[:10] if ts else ""
    source_url = update.get("url") or update.get("source", "")
    domain = _extract_domain(source_url) if source_url else ""
    title = update.get("title", "")

    lines = ["{{Infobox Update"]
    lines.append(f"| type       = {update_type.replace('-', ' ').title()}")
    lines.append(f"| date       = {date_str}")
    lines.append(f"| source     = {domain}")
    if title:
        lines.append(f"| title      = {title}")
    # Extra fields by type
    content = update.get("content", "")
    if update_type in ("fishing-real", "fishing") and content:
        # Try to extract a weight from the title or content
        weight_m = re.search(r"(\d+[\d.]*\s*(?:lb|kg|lbs))", title + " " + content, re.IGNORECASE)
        if weight_m:
            lines.append(f"| weight     = {weight_m.group(1)}")
    lines.append("}}")
    return "\n".join(lines)


def lore_to_encyclopedic(text: str) -> str:
    """
    Convert first-person Telegram lore text to encyclopedic third-person prose.

    Handles contractions, standalone 'I', possessives, and reflexives.
    """
    result = text
    for old, new in _FIRST_TO_THIRD:
        if old.startswith("^"):
            # Regex-based multiline start-of-sentence replacement
            # Strip the sentinel '^' and build the actual pattern with an anchor
            result = re.sub(
                r"^" + re.escape(old[1:]),
                new,
                result,
                flags=re.MULTILINE,
            )
        else:
            result = result.replace(old, new)
    return result


def ensure_references_section(wikitext: str) -> str:
    """
    Append a == References == / <references /> section if one is not already present.
    """
    if "== References ==" in wikitext or "<references" in wikitext:
        return wikitext
    return wikitext.rstrip() + "\n\n== References ==\n<references />\n"


def ensure_categories(wikitext: str, categories: list) -> str:
    """
    Append any category tags from *categories* that are not already in *wikitext*.

    Args:
        wikitext: Current page content.
        categories: List of full category tag strings, e.g.
                    ['[[Category:GK BRAIN Updates]]', '[[Category:2026]]'].
    """
    result = wikitext
    for cat in categories:
        if cat not in result:
            result = result.rstrip() + "\n" + cat + "\n"
    return result
