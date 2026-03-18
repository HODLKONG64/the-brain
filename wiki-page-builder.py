"""
wiki-page-builder.py — Rich Structured Wiki Page Builder for GK BRAIN

Creates or fully refreshes a structured Fandom wiki page for any Crypto Moonboys
entity (characters, lore events, NFT collections, weapons/keys, locations, toys,
Hard Fork Games, etc.).

Key features:
- Generates fully-structured MediaWiki wikitext for any entity type.
- Automatically adds an Infobox for character-type entities.
- Wikilinks every keyword in the body that matches an existing wiki page title.
- Embeds and captions images via MediaWiki file upload + [[File:…]] syntax.
- Appends all relevant [[Category:…]] tags.
- Adds cross-links back from related pages (See Also injection).

Usage (from gk-brain.py or standalone):
    from wiki_page_builder import build_wiki_page
    result = build_wiki_page(entity)
    # result → {"success": bool, "page_title": str, "created": bool}
"""

import os
import re
import time
import urllib.parse

import requests

# ---------------------------------------------------------------------------
# Configuration — mirrors wiki-smart-merger.py / wiki-updater.py pattern
# ---------------------------------------------------------------------------

WIKI_BASE = os.environ.get("FANDOM_WIKI_URL", "https://gkniftyheads.fandom.com").rstrip("/")
WIKI_API = WIKI_BASE + "/api.php"
FANDOM_USERNAME = os.environ.get("FANDOM_BOT_USER", os.environ.get("FANDOM_USERNAME", ""))
FANDOM_PASSWORD = os.environ.get("FANDOM_BOT_PASSWORD", os.environ.get("FANDOM_PASSWORD", ""))

# Infobox template names keyed by entity type
_INFOBOX_TEMPLATES: dict[str, str] = {
    "character": "Infobox character",
    "lore_event": "Infobox event",
    "nft_collection": "Infobox collection",
    "weapon": "Infobox item",
    "key": "Infobox item",
    "location": "Infobox location",
    "place": "Infobox location",
    "toy": "Infobox item",
    "game": "Infobox game",
}

# Default category that every new page receives regardless of entity type
_DEFAULT_CATEGORY = "GK BRAIN Auto-Generated"


# ---------------------------------------------------------------------------
# MediaWiki API helpers (same pattern as wiki-smart-merger.py and wiki-updater.py)
# ---------------------------------------------------------------------------

def _get_login_token(session: requests.Session) -> str:
    resp = session.get(WIKI_API, params={
        "action": "query",
        "meta": "tokens",
        "type": "login",
        "format": "json",
    })
    resp.raise_for_status()
    return resp.json()["query"]["tokens"]["logintoken"]


def _login(session: requests.Session) -> bool:
    """Log in to Fandom with bot credentials. Returns True on success."""
    if not FANDOM_USERNAME or not FANDOM_PASSWORD:
        print("[wiki-page-builder] FANDOM credentials not set — skipping.")
        return False

    token = _get_login_token(session)
    resp = session.post(WIKI_API, data={
        "action": "clientlogin",
        "loginmessageformat": "none",
        "username": FANDOM_USERNAME,
        "password": FANDOM_PASSWORD,
        "logintoken": token,
        "loginreturnurl": WIKI_BASE,
        "rememberMe": 1,
        "format": "json",
    })
    resp.raise_for_status()
    result = resp.json()
    if result.get("clientlogin", {}).get("status") == "PASS":
        print(f"[wiki-page-builder] Logged in as {FANDOM_USERNAME}")
        return True
    print(f"[wiki-page-builder] Login failed: {result}")
    return False


def _get_csrf_token(session: requests.Session) -> str:
    resp = session.get(WIKI_API, params={
        "action": "query",
        "meta": "tokens",
        "format": "json",
    })
    resp.raise_for_status()
    return resp.json()["query"]["tokens"]["csrftoken"]


def _get_page_content(session: requests.Session, title: str) -> str:
    """Return current wikitext of a page, or empty string if the page is new."""
    resp = session.get(WIKI_API, params={
        "action": "query",
        "prop": "revisions",
        "rvprop": "content",
        "titles": title,
        "format": "json",
    })
    resp.raise_for_status()
    pages = resp.json()["query"]["pages"]
    for page in pages.values():
        revisions = page.get("revisions", [])
        if revisions:
            return revisions[0].get("*", "")
    return ""


def _page_exists(session: requests.Session, title: str) -> bool:
    """Return True if the given wiki page already exists."""
    resp = session.get(WIKI_API, params={
        "action": "query",
        "titles": title,
        "format": "json",
    })
    resp.raise_for_status()
    pages = resp.json()["query"]["pages"]
    return "-1" not in pages


def _edit_page(
    session: requests.Session,
    title: str,
    content: str,
    summary: str,
    csrf_token: str,
) -> bool:
    """Replace (or create) a wiki page with full wikitext. Returns True on success."""
    resp = session.post(WIKI_API, data={
        "action": "edit",
        "title": title,
        "text": content,
        "summary": summary,
        "bot": "true",
        "token": csrf_token,
        "format": "json",
    })
    resp.raise_for_status()
    result = resp.json()
    if result.get("edit", {}).get("result") == "Success":
        return True
    print(f"[wiki-page-builder] Edit failed for '{title}': {result}")
    return False


def _fetch_all_page_titles(session: requests.Session) -> list[str]:
    """
    Return a list of all wiki page titles via the MediaWiki ``allpages`` API.
    Used to build the keyword→page-title map for auto-interlinking.
    """
    titles: list[str] = []
    apcontinue: str | None = None

    while True:
        params: dict = {
            "action": "query",
            "list": "allpages",
            "aplimit": "500",
            "apnamespace": "0",
            "format": "json",
        }
        if apcontinue is not None:
            params["apfrom"] = apcontinue

        resp = session.get(WIKI_API, params=params)
        resp.raise_for_status()
        data = resp.json()

        for page in data.get("query", {}).get("allpages", []):
            titles.append(page["title"])

        cont = data.get("continue", {}).get("apcontinue")
        if cont:
            apcontinue = cont
            time.sleep(0.5)
        else:
            break

    return titles


def _upload_image_from_url(
    session: requests.Session,
    csrf_token: str,
    filename: str,
    image_url: str,
    comment: str = "",
) -> bool:
    """
    Upload an image to the wiki from a remote URL using the MediaWiki upload API.

    Parameters
    ----------
    filename:  Target filename on the wiki (e.g. ``Bitcoin_Kid.jpg``).
    image_url: Publicly-accessible URL of the source image.
    comment:   Edit summary / upload comment.

    Returns True on success.
    """
    resp = session.post(WIKI_API, data={
        "action": "upload",
        "filename": filename,
        "url": image_url,
        "comment": comment or f"Uploaded by GK BRAIN wiki-page-builder",
        "ignorewarnings": "true",
        "token": csrf_token,
        "format": "json",
    })
    resp.raise_for_status()
    result = resp.json()
    if result.get("upload", {}).get("result") in ("Success", "Warning"):
        print(f"[wiki-page-builder] Uploaded image '{filename}'")
        return True
    print(f"[wiki-page-builder] Image upload failed for '{filename}': {result}")
    return False


# ---------------------------------------------------------------------------
# Interlinking helpers
# ---------------------------------------------------------------------------

def _build_keyword_map(page_titles: list[str], current_title: str) -> dict[str, str]:
    """
    Build a sorted (longest-first) map of ``{keyword: page_title}`` from all
    existing wiki page titles.  The current page is excluded so it does not
    link to itself.
    """
    kw_map: dict[str, str] = {}
    for title in page_titles:
        if title.strip().lower() == current_title.strip().lower():
            continue
        kw_map[title] = title
    # Sort longest first so multi-word titles are matched before shorter subsets
    return dict(sorted(kw_map.items(), key=lambda kv: len(kv[0]), reverse=True))


def _apply_wikilinks(text: str, keyword_map: dict[str, str]) -> str:
    """
    Replace the *first* occurrence of each keyword in ``text`` with a
    ``[[Page Title]]`` wikilink.  Already-wikilinked occurrences (i.e. inside
    ``[[…]]``) are skipped.  The replacement is case-insensitive.

    Strategy: split the text into wikilink tokens (``[[…]]``) and plain-text
    segments; apply replacements only in plain-text segments to avoid
    double-linking.
    """
    if not keyword_map:
        return text

    for keyword, page_title in keyword_map.items():
        # Skip if this keyword is already wikilinked anywhere in the text
        if f"[[{page_title}]]" in text or f"[[{page_title}|" in text:
            continue

        # Split text into alternating [plain, wikilink, plain, wikilink, …] segments
        # Pattern matches [[…]] tokens
        token_pattern = re.compile(r"(\[\[.*?\]\])", re.DOTALL)
        segments = token_pattern.split(text)

        escaped = re.escape(keyword)
        word_pattern = re.compile(r"\b" + escaped + r"\b", re.IGNORECASE)
        replaced = False
        new_segments: list[str] = []

        for seg in segments:
            if replaced:
                new_segments.append(seg)
                continue
            if seg.startswith("[["):
                # This is a wikilink token — do not modify
                new_segments.append(seg)
            else:
                new_seg = word_pattern.sub(f"[[{page_title}]]", seg, count=1)
                if new_seg != seg:
                    replaced = True
                new_segments.append(new_seg)

        text = "".join(new_segments)

    return text


def _inject_see_also_into_page(
    session: requests.Session,
    csrf_token: str,
    related_page_title: str,
    new_page_title: str,
) -> bool:
    """
    Ensure ``new_page_title`` appears in the ``== See Also ==`` section of
    ``related_page_title``.  Creates the section if it does not exist.
    Returns True if the page was modified (or already had the link).
    """
    content = _get_page_content(session, related_page_title)
    if not content:
        return False

    # If already linked, nothing to do
    if f"[[{new_page_title}]]" in content or f"[[{new_page_title}|" in content:
        return True

    new_link_line = f"* [[{new_page_title}]]"

    if "== See Also ==" in content:
        # Insert after the heading line
        content = content.replace(
            "== See Also ==",
            f"== See Also ==\n{new_link_line}",
            1,
        )
    else:
        # Append a new See Also section before the first category tag (or at end)
        cat_match = re.search(r"\[\[Category:", content)
        see_also_block = f"\n== See Also ==\n{new_link_line}\n"
        if cat_match:
            insert_pos = cat_match.start()
            content = content[:insert_pos] + see_also_block + "\n" + content[insert_pos:]
        else:
            content = content.rstrip() + "\n" + see_also_block

    return _edit_page(
        session,
        related_page_title,
        content,
        f"GK BRAIN: add cross-link to [[{new_page_title}]]",
        csrf_token,
    )


# ---------------------------------------------------------------------------
# Wikitext generation
# ---------------------------------------------------------------------------

def _derive_image_filename(entity: dict) -> str:
    """
    Derive a safe wiki filename from the entity title + image URL extension.
    E.g. ``Bitcoin Kid`` + ``.jpg`` → ``Bitcoin_Kid.jpg``.
    """
    title = entity.get("title", "unknown")
    image_url = entity.get("image_url") or ""
    # Attempt to infer extension from URL
    path = urllib.parse.urlparse(image_url).path
    _, ext = os.path.splitext(path)
    if ext.lower() not in (".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"):
        ext = ".jpg"
    safe_title = re.sub(r"[^A-Za-z0-9_\-]", "_", title).strip("_")
    return f"{safe_title}{ext}"


def _detect_faction(text: str) -> str:
    """Detect the most prominent faction keyword in a block of text."""
    factions = [
        "GraffPUNKS",
        "Moonboys",
        "HODL X Warriors",
        "Crowned Royal Moongirls",
        "Bitcoin X Kids",
        "OG Bitcoin Kids",
        "Blocktopia",
        "Hardfork Games",
        "Hard Fork Games",
    ]
    for faction in factions:
        if faction.lower() in text.lower():
            return faction
    return ""


def _detect_first_seen(text: str) -> str:
    """Extract an approximate 'first seen' date from body text (YYYY or Month YYYY)."""
    match = re.search(r"\b(20\d{2})\b", text)
    if match:
        return match.group(1)
    return ""


def _build_infobox(entity: dict, image_filename: str) -> str:
    """Build an infobox wikitext block for the entity."""
    entity_type = entity.get("type", "")
    template = _INFOBOX_TEMPLATES.get(entity_type)
    if not template:
        return ""

    title = entity.get("title", "")
    combined_text = entity.get("summary", "") + " ".join(
        s.get("body", "") for s in entity.get("content_sections", [])
    )

    lines = [f"{{{{{template}"]
    lines.append(f"| name       = {title}")
    lines.append(f"| image      = {image_filename}")

    if entity_type == "character":
        faction = _detect_faction(combined_text)
        first_seen = _detect_first_seen(combined_text)
        lines.append(f"| faction    = {faction}")
        lines.append(f"| first_seen = {first_seen}")
    elif entity_type in ("location", "place"):
        lines.append(f"| universe   = Crypto Moonboys")
    elif entity_type in ("nft_collection",):
        lines.append(f"| blockchain = WAX")
        lines.append(f"| creator    = GKniftyHEADS")
    elif entity_type == "game":
        lines.append(f"| developer  = Hard Fork Games")
    elif entity_type in ("weapon", "key", "toy"):
        lines.append(f"| rarity     =")

    lines.append("}}")
    return "\n".join(lines)


def _build_image_embed(image_filename: str, caption: str | None) -> str:
    """Build a ``[[File:…]]`` wikitext embed string."""
    if not image_filename:
        return ""
    cap = caption.strip() if caption else ""
    if cap:
        return f"[[File:{image_filename}|thumb|right|{cap}]]"
    return f"[[File:{image_filename}|thumb|right]]"


def _build_wikitext(entity: dict, keyword_map: dict[str, str], image_filename: str) -> str:
    """
    Assemble the full MediaWiki wikitext for an entity page.

    Structure:
        {{Infobox …}}          (if applicable)
        [[File:…]]             (if image available)

        '''{title}''' is a … {summary}

        == Background ==
        …

        == [section heading] ==
        …                      (keywords auto-wikilinked)

        == See Also ==
        * [[Related Page 1]]

        == External Links ==
        * [url Label]

        == References ==
        <references/>

        [[Category:X]]
        [[Category:Y]]
    """
    title = entity.get("title", "")
    summary = entity.get("summary", "")
    content_sections: list[dict] = entity.get("content_sections", [])
    categories: list[str] = list(entity.get("categories", []))
    source_urls: list[str] = entity.get("source_urls", [])
    related_pages: list[str] = entity.get("related_pages", [])
    image_caption = entity.get("image_caption")

    parts: list[str] = []

    # Infobox (character-types and mapped types)
    infobox = _build_infobox(entity, image_filename)
    if infobox:
        parts.append(infobox)

    # Image embed
    img_embed = _build_image_embed(image_filename, image_caption)
    if img_embed:
        parts.append(img_embed)
        parts.append("")

    # Lead sentence / summary
    lead = f"'''{title}''' is a {summary}" if summary else f"'''{title}'''"
    parts.append(lead)
    parts.append("")

    # Content sections (with auto-wikilinks applied to body text)
    for section in content_sections:
        heading = section.get("heading", "").strip()
        body = section.get("body", "").strip()
        if not heading:
            continue
        linked_body = _apply_wikilinks(body, keyword_map)
        parts.append(f"== {heading} ==")
        parts.append(linked_body)
        parts.append("")

    # See Also
    if related_pages:
        parts.append("== See Also ==")
        for page in related_pages:
            parts.append(f"* [[{page}]]")
        parts.append("")

    # External Links
    if source_urls:
        parts.append("== External Links ==")
        for idx, url in enumerate(source_urls, start=1):
            parts.append(f"* [{url} Source {idx}]")
        parts.append("")

    # References
    parts.append("== References ==")
    parts.append("<references/>")
    parts.append("")

    # Categories — always include the default auto-generated category
    if _DEFAULT_CATEGORY not in categories:
        categories.append(_DEFAULT_CATEGORY)
    for cat in categories:
        parts.append(f"[[Category:{cat}]]")

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_wiki_page(entity: dict) -> dict:
    """
    Create or fully refresh a structured Fandom wiki page for a Crypto Moonboys entity.

    Parameters
    ----------
    entity : dict
        Schema::

            {
              "type": str,            # "character" | "lore_event" | "nft_collection" |
                                      # "weapon" | "location" | "toy" | "game" | "key" | "place"
              "title": str,           # wiki page title (e.g. "Bitcoin Kid")
              "summary": str,         # 1–3 sentence intro
              "content_sections": [   # ordered list of {heading: str, body: str}
                  {"heading": "Background", "body": "..."},
              ],
              "categories": [str],    # e.g. ["Characters", "GraffPUNKS", "Moonboys"]
              "image_url": str|None,  # canonical image URL (can be None)
              "image_caption": str|None,
              "source_urls": [str],   # source URLs used to build this page
              "related_pages": [str]  # other wiki page titles for cross-linking
            }

    Returns
    -------
    dict
        ``{"success": bool, "page_title": str, "created": bool}``
    """
    title: str = entity.get("title", "").strip()
    if not title:
        print("[wiki-page-builder] Entity has no 'title' — aborting.")
        return {"success": False, "page_title": "", "created": False}

    if not FANDOM_USERNAME or not FANDOM_PASSWORD:
        print("[wiki-page-builder] Credentials missing — cannot build wiki page.")
        return {"success": False, "page_title": title, "created": False}

    session = requests.Session()
    if not _login(session):
        return {"success": False, "page_title": title, "created": False}

    csrf_token = _get_csrf_token(session)

    # Determine whether this is a new page or an existing one
    already_exists = _page_exists(session, title)

    # ------------------------------------------------------------------
    # 1. Upload image (if a URL is provided)
    # ------------------------------------------------------------------
    image_filename = ""
    image_url: str = entity.get("image_url") or ""
    if image_url:
        image_filename = _derive_image_filename(entity)
        try:
            _upload_image_from_url(
                session,
                csrf_token,
                image_filename,
                image_url,
                comment=f"Image for [[{title}]] — uploaded by GK BRAIN",
            )
        except Exception as exc:
            print(f"[wiki-page-builder] Image upload failed (non-fatal): {exc}")
            image_filename = ""
        time.sleep(1)

    # ------------------------------------------------------------------
    # 2. Fetch all page titles for auto-interlinking
    # ------------------------------------------------------------------
    all_page_titles: list[str] = []
    try:
        all_page_titles = _fetch_all_page_titles(session)
        print(f"[wiki-page-builder] Fetched {len(all_page_titles)} wiki page titles for interlinking.")
    except Exception as exc:
        print(f"[wiki-page-builder] Could not fetch page titles (interlinking disabled): {exc}")

    keyword_map = _build_keyword_map(all_page_titles, title)

    # ------------------------------------------------------------------
    # 3. Build wikitext and write the page
    # ------------------------------------------------------------------
    wikitext = _build_wikitext(entity, keyword_map, image_filename)

    ok = _edit_page(
        session,
        title,
        wikitext,
        f"GK BRAIN: {'update' if already_exists else 'create'} structured page for {title}",
        csrf_token,
    )

    if not ok:
        return {"success": False, "page_title": title, "created": False}

    print(f"[wiki-page-builder] {'Updated' if already_exists else 'Created'} page: {title}")
    time.sleep(1)

    # ------------------------------------------------------------------
    # 4. Inject back-links on all related pages
    # ------------------------------------------------------------------
    related_pages: list[str] = entity.get("related_pages", [])
    for related_title in related_pages:
        try:
            _inject_see_also_into_page(session, csrf_token, related_title, title)
            time.sleep(1)
        except Exception as exc:
            print(f"[wiki-page-builder] Cross-link injection failed for '{related_title}': {exc}")

    return {"success": True, "page_title": title, "created": not already_exists}


# ---------------------------------------------------------------------------
# CLI self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    test_entity = {
        "type": "character",
        "title": "Bitcoin Kid",
        "summary": (
            "member of the OG Bitcoin Kids faction inside Blocktopia, "
            "known for their legendary HODL discipline and graffiti skills."
        ),
        "content_sections": [
            {
                "heading": "Background",
                "body": (
                    "Bitcoin Kid grew up inside the walls of Blocktopia during the "
                    "Hard Fork Games era. Trained under Elder Codex-7, they mastered "
                    "the Chain Scribe techniques and became one of the youngest "
                    "HODL X Warriors to earn a Crowned Royal Moongirl escort."
                ),
            },
            {
                "heading": "Abilities & Traits",
                "body": (
                    "Expert in parkour, graffiti, and blockchain cryptography. "
                    "Often spotted at GraffPUNKS Network Radio events alongside "
                    "Lady-INK and Charlie Buster."
                ),
            },
        ],
        "categories": ["Characters", "OG Bitcoin Kids", "Moonboys", "Blocktopia"],
        "image_url": None,
        "image_caption": "Bitcoin Kid in Blocktopia",
        "source_urls": ["https://graffpunks.substack.com/p/bitcoin-kid"],
        "related_pages": ["Elder Codex-7", "Blocktopia", "Hard Fork Games"],
    }

    result = build_wiki_page(test_entity)
    print(json.dumps(result, indent=2))
