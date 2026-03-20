"""
web-lore-agent.py — Brain 3: Web Lore Agent

Standalone agent that crawls official sources, validates canon names,
and generates 30% real-data + 70% AI lore posts for Telegram.

Usage: python web-lore-agent.py

Rules:
  - WEBLORERULES.md         (lore composition rules)
  - OFFICIAL-SOURCE-AUTHORITY-RULES.md  (canon source authority)
  - brain-rules.md / character-bible.md (universe lore rules — same as Brain 2)
"""

import hashlib
import json
import logging
import os
import re
import time
import datetime
import traceback

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
_log = logging.getLogger("web-lore-agent")

# ---------------------------------------------------------------------------
# File paths
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SOURCES_FILE       = os.path.join(BASE_DIR, "gkandcryptomoonboywebsitestosave.md")
BRAIN_RULES_FILE   = os.path.join(BASE_DIR, "gk-brain-complete.md")
CHARACTER_FILE     = os.path.join(BASE_DIR, "character-bible.md")
WEBLORE_RULES_FILE = os.path.join(BASE_DIR, "WEBLORERULES.md")
CACHE_FILE         = os.path.join(BASE_DIR, "web-lore-cache.json")
OUTPUT_FILE        = os.path.join(BASE_DIR, "web-lore-output.json")
ERROR_LOG_FILE     = os.path.join(BASE_DIR, "web-lore-errors.log")
NON_CANON_LOG_FILE = os.path.join(BASE_DIR, "non-canon-names.log")

# ---------------------------------------------------------------------------
# Environment / API config
# ---------------------------------------------------------------------------

GROK_API_KEY    = os.environ.get("GROK_API_KEY", "")
GROK_API_BASE   = "https://api.x.ai/v1"
GROK_TEXT_MODEL = os.environ.get("GROK_TEXT_MODEL", "grok-3-latest")

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL   = "claude-3-5-sonnet-20241022"

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHANNEL_CHAT_IDS   = [
    c.strip()
    for c in os.environ.get("CHANNEL_CHAT_IDS", "").split(",")
    if c.strip()
]
WEB_LORE_TELEGRAM_ENABLED = os.environ.get("WEB_LORE_TELEGRAM_ENABLED", "false").lower() == "true"

# Crawl limits
MAX_URLS_PER_RUN        = 50
CRAWL_TIMEOUT_SEC       = 10
CRAWL_DELAY_SEC         = 1
BACKOFF_WAIT_SEC        = 30
CACHE_COOLDOWN_HRS      = 48

# Snippet / corpus size limits
MAX_SNIPPET_CHARS           = 2000   # chars stored per crawled page in new_snippets
PROMPT_SNIPPET_CHARS        = 400    # chars per snippet injected into the LLM prompt
MAX_CORPUS_CHARS_PER_SOURCE = 5000   # chars fetched from each official source during canon guard

# ---------------------------------------------------------------------------
# Error helpers
# ---------------------------------------------------------------------------


def _log_error(msg: str) -> None:
    """Append timestamped error to web-lore-errors.log."""
    ts = datetime.datetime.utcnow().isoformat()
    line = f"[{ts}] {msg}\n"
    try:
        with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line)
    except OSError:
        pass
    _log.error(msg)


def _log_non_canon(name: str, source_url: str) -> None:
    """Append rejected non-canon name to non-canon-names.log."""
    ts = datetime.datetime.utcnow().isoformat()
    line = f"[{ts}] NON-CANON: {name!r} | source: {source_url}\n"
    try:
        with open(NON_CANON_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line)
    except OSError:
        pass
    _log.info("[canon-guard] Non-canon name logged: %r", name)


# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------


def _load_cache() -> dict:
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {"hashes": {}, "last_crawled": {}}


def _save_cache(cache: dict) -> None:
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)


def _content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _is_cache_cooled_down(cache: dict, url: str) -> bool:
    """Return True if the URL hasn't been crawled within the cooldown period."""
    last = cache.get("last_crawled", {}).get(url)
    if not last:
        return True
    try:
        last_dt = datetime.datetime.fromisoformat(last)
        elapsed = (datetime.datetime.utcnow() - last_dt).total_seconds() / 3600
        return elapsed >= CACHE_COOLDOWN_HRS
    except (ValueError, TypeError):
        return True


# ---------------------------------------------------------------------------
# Source list parser
# ---------------------------------------------------------------------------


def _extract_official_sources(md_text: str) -> list[str]:
    """Extract all https:// URLs from gkandcryptomoonboywebsitestosave.md."""
    return re.findall(r"https?://[^\s\)\]>\"']+", md_text)


def _extract_gkdata_real_sources(md_text: str) -> list[str]:
    """Extract only URLs from the gkdata-real section (highest authority)."""
    gkdata_section = re.search(
        r"## CATEGORY: gkdata-real(.*?)## CATEGORY:",
        md_text,
        re.DOTALL,
    )
    if not gkdata_section:
        return _extract_official_sources(md_text)
    return re.findall(r"https?://[^\s\)\]>\"']+", gkdata_section.group(1))


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

_SESSION = requests.Session()
_SESSION.headers.update(
    {
        "User-Agent": (
            "Mozilla/5.0 (compatible; GKBrain3-WebLoreAgent/1.0; "
            "+https://github.com/HODLKONG64/the-brain)"
        )
    }
)


def _safe_get(url: str) -> requests.Response | None:
    """HTTP GET with timeout, backoff on 429/503, returns None on failure."""
    for attempt in range(2):
        try:
            resp = _SESSION.get(url, timeout=CRAWL_TIMEOUT_SEC, allow_redirects=True)
            if resp.status_code in (429, 503):
                if attempt == 0:
                    _log.warning("[crawl] %s → HTTP %s — backing off %ss", url, resp.status_code, BACKOFF_WAIT_SEC)
                    time.sleep(BACKOFF_WAIT_SEC)
                    continue
                _log.warning("[crawl] %s → HTTP %s after retry — skipping", url, resp.status_code)
                _log_error(f"HTTP {resp.status_code} (after retry): {url}")
                return None
            return resp
        except requests.RequestException as exc:
            if attempt == 0:
                _log.warning("[crawl] %s → %s — retrying once", url, exc)
                time.sleep(BACKOFF_WAIT_SEC)
                continue
            _log_error(f"Request error (after retry): {url} — {exc}")
            return None
    return None


def _extract_text(html: str) -> str:
    """Strip HTML tags and return cleaned text."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    return " ".join(soup.get_text(" ", strip=True).split())


# ---------------------------------------------------------------------------
# Crawl phase
# ---------------------------------------------------------------------------


def crawl_sources(official_urls: list[str], cache: dict) -> list[dict]:
    """
    Crawl up to MAX_URLS_PER_RUN URLs.
    Returns list of new-content snippets not previously seen in cache.
    Each entry: {url, category, text, hash}
    """
    results: list[dict] = []
    crawled = 0
    failed = 0

    urls_to_crawl = official_urls[:MAX_URLS_PER_RUN]

    for url in urls_to_crawl:
        if not _is_cache_cooled_down(cache, url):
            _log.info("[crawl] Skipping %s (cooldown active)", url)
            continue

        time.sleep(CRAWL_DELAY_SEC)
        _log.info("[crawl] GET %s", url)
        resp = _safe_get(url)
        crawled += 1

        if resp is None:
            failed += 1
            continue
        if resp.status_code < 200 or resp.status_code >= 300:
            _log.warning("[crawl] %s → HTTP %s", url, resp.status_code)
            failed += 1
            continue

        try:
            text = _extract_text(resp.text)
        except Exception as exc:
            _log_error(f"Text extraction failed for {url}: {exc}")
            failed += 1
            continue

        if not text.strip():
            continue

        content_hash = _content_hash(text)
        prev_hash = cache.get("hashes", {}).get(url)

        if content_hash == prev_hash:
            _log.info("[crawl] %s — no new content (hash unchanged)", url)
        else:
            snippet = text[:MAX_SNIPPET_CHARS]  # keep first MAX_SNIPPET_CHARS as the usable snippet
            results.append({"url": url, "text": snippet, "hash": content_hash})
            _log.info("[crawl] %s — new content found (%d chars)", url, len(text))

        # Update cache regardless so we track last-crawl time
        cache.setdefault("hashes", {})[url] = content_hash
        cache.setdefault("last_crawled", {})[url] = datetime.datetime.utcnow().isoformat()

    if crawled > 0 and failed / float(crawled) > 0.5:
        _log_error(f"CRAWL_FAILURE: {failed}/{crawled} URLs failed (>50% threshold)")
        _log.error("[crawl] Aborting — too many failures.")
        return []

    return results


# ---------------------------------------------------------------------------
# Canon Name Guard
# ---------------------------------------------------------------------------


def _extract_candidate_names(text: str) -> list[str]:
    """
    Extract candidate proper nouns from text.
    Uses two signals:
      1. Title-cased multi-word sequences appearing ≥3 times
      2. Capitalised words appearing in headline positions (first 300 chars)
    Returns a deduplicated list of candidate names.
    """
    # Find all title-cased words / short phrases
    # Match sequences like "Crypto Moonboys", "GraffPUNKS", "Lady-INK", etc.
    pattern = re.compile(r"\b[A-Z][A-Za-z0-9_\-]{1,}(?:\s+[A-Z][A-Za-z0-9_\-]{1,}){0,3}\b")
    matches = pattern.findall(text)

    # Count occurrences
    from collections import Counter
    counts = Counter(matches)

    frequent = {name for name, count in counts.items() if count >= 3}

    # Also grab capitalised words/phrases from headline positions
    headline_text = text[:300]
    headline_names = set(pattern.findall(headline_text))

    candidates = frequent | headline_names

    # Filter out common English stop words that happen to be capitalised
    stop_words = {
        "The", "This", "That", "With", "From", "For", "And", "But", "Not",
        "Are", "Was", "Were", "Has", "Have", "Had", "Will", "Can", "May",
        "More", "Some", "Any", "All", "New", "Also", "Just", "Its", "Their",
        "When", "Then", "Into", "Over", "After", "Before", "About", "During",
        "While", "Because", "However", "Therefore", "Although",
    }
    candidates = {c for c in candidates if c not in stop_words and len(c) > 2}

    return sorted(candidates)


def canon_guard(names: list[str], official_sources: list[str]) -> dict:
    """
    For each candidate name, check whether it appears on any official source.

    Strategy: check cached page text already fetched during crawl phase by
    comparing against the official_sources list. For names not resolved via
    local cache, we fetch the source pages on-demand (with rate limiting).

    Returns:
        {
            "canon_name":    {"canon": True,  "source": url},
            "non_canon_name": {"canon": False, "source": None},
            ...
        }
    """
    result: dict[str, dict] = {}

    # We'll do a lightweight re-fetch of gkdata-real pages to build a combined
    # corpus for name matching. To keep this cheap we only fetch up to 10 pages.
    corpus = ""
    source_texts: dict[str, str] = {}
    for url in official_sources[:10]:
        time.sleep(CRAWL_DELAY_SEC)
        resp = _safe_get(url)
        if resp and 200 <= resp.status_code < 300:
            try:
                page_text = _extract_text(resp.text)[:MAX_CORPUS_CHARS_PER_SOURCE]
                source_texts[url] = page_text
                corpus += " " + page_text
            except Exception:
                pass

    corpus_lower = corpus.lower()

    for name in names:
        name_lower = name.lower()
        found_url = None
        if name_lower in corpus_lower:
            # Identify which specific source URL contains the name
            for url, text in source_texts.items():
                if name_lower in text.lower():
                    found_url = url
                    break

        if found_url is not None:
            result[name] = {"canon": True, "source": found_url}
        else:
            result[name] = {"canon": False, "source": None}

    return result


# ---------------------------------------------------------------------------
# LLM call helpers
# ---------------------------------------------------------------------------


def _call_grok(system_prompt: str, user_prompt: str) -> str:
    """Call Grok API. Raises RuntimeError on failure."""
    if not GROK_API_KEY:
        raise RuntimeError("GROK_API_KEY not set")

    payload = {
        "model": GROK_TEXT_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        "temperature": 0.85,
        "max_tokens": 1200,
    }
    for attempt in range(3):
        try:
            resp = requests.post(
                f"{GROK_API_BASE}/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROK_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as exc:
            if attempt < 2:
                wait = 2 ** (attempt + 1)
                _log.warning("[llm] Grok attempt %d failed: %s — retrying in %ds", attempt + 1, exc, wait)
                time.sleep(wait)
            else:
                raise RuntimeError(f"Grok call failed after 3 attempts: {exc}") from exc
    raise RuntimeError("Grok call failed unexpectedly")


def _call_anthropic(system_prompt: str, user_prompt: str) -> str:
    """Call Anthropic Claude API. Raises RuntimeError on failure."""
    if not ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY not set")

    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    message = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=1200,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return message.content[0].text.strip()


def _llm_generate(system_prompt: str, user_prompt: str) -> str:
    """Try Grok first, fall back to Anthropic."""
    if GROK_API_KEY:
        try:
            return _call_grok(system_prompt, user_prompt)
        except RuntimeError as exc:
            _log_error(f"Grok failed, trying Anthropic: {exc}")

    if ANTHROPIC_API_KEY:
        try:
            return _call_anthropic(system_prompt, user_prompt)
        except RuntimeError as exc:
            _log_error(f"Anthropic also failed: {exc}")
            raise

    raise RuntimeError("No LLM API key available (GROK_API_KEY or ANTHROPIC_API_KEY required)")


# ---------------------------------------------------------------------------
# Lore composition (30/70 split)
# ---------------------------------------------------------------------------


def _load_text_file(path: str) -> str:
    """Load a text file, returning empty string on failure."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def _build_system_prompt(brain_rules: str, character_bible: str, weblore_rules: str) -> str:
    return f"""You are Brain 3 — the Web Lore Agent for the Crypto Moonboys universe.

You generate lore posts for Telegram using a strict 30% real data / 70% AI-creative formula.

UNIVERSE RULES (Brain 2 rules apply):
{brain_rules[:3000]}

CHARACTER BIBLE (excerpt):
{character_bible[:2000]}

WEB LORE RULES:
{weblore_rules[:2000]}

STRICT REQUIREMENTS:
- Generate TWO lore posts (post1 and post2), each 120–180 words.
- Generate TWO image prompts (image_prompt1 and image_prompt2) for corresponding posts.
- Present-tense, mind-log voice. Vivid sensory detail. No hashtags. No emojis except optional single fire (🔥) or lightning (⚡) at end.
- Open each post with a strong in-universe hook sentence.
- Never break the fourth wall. Never say "real world", "IRL", "today in real life".
- Translate any real-world references fully into in-universe language.
- Never invent new canon characters, factions, or locations — use only established ones.
- Return ONLY a valid JSON object with exactly these keys:
  post1, post2, image_prompt1, image_prompt2
No markdown fences, no extra text outside the JSON."""


def _build_user_prompt(snippets: list[dict], canon_names: list[str]) -> str:
    has_real_data = bool(snippets)

    if has_real_data:
        snippet_block = "\n\n".join(
            f"SOURCE ({s['url']}):\n{s['text'][:PROMPT_SNIPPET_CHARS]}" for s in snippets[:3]
        )
        real_data_instruction = f"""REAL DATA (30% anchoring — weave into lore, translated to in-universe language):
{snippet_block}

CANON NAMES available for use: {', '.join(canon_names[:20]) if canon_names else 'none confirmed this cycle'}

Use up to 3 of the real snippets above as concrete in-universe events, discoveries, or artefacts.
The real-world language must be fully disguised — translate to Crypto Moonboys universe terminology."""
    else:
        real_data_instruction = """NO NEW REAL DATA this cycle — generate 100% AI lore using established universe continuity.
Use calendar, character arcs, and faction dynamics to create vivid narrative."""

    return f"""{real_data_instruction}

Now generate the two Telegram lore posts and their image prompts. Return valid JSON only."""


def compose_lore(
    snippets: list[dict],
    canon_names: list[str],
    brain_rules: str,
    character_bible: str,
    weblore_rules: str,
) -> dict:
    """
    Generate a lore post pair using the 30/70 formula.
    Returns dict with post1, post2, image_prompt1, image_prompt2.
    """
    system_prompt = _build_system_prompt(brain_rules, character_bible, weblore_rules)
    user_prompt   = _build_user_prompt(snippets, canon_names)

    raw = _llm_generate(system_prompt, user_prompt)

    # Strip potential markdown code fences
    raw = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    raw = re.sub(r"\s*```$", "", raw.strip())

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Attempt to extract JSON object from raw text
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise RuntimeError(f"LLM returned non-JSON output: {raw[:200]}")


# ---------------------------------------------------------------------------
# Telegram sender
# ---------------------------------------------------------------------------


def _send_telegram(post1: str, post2: str) -> None:
    """Send two lore posts to all configured Telegram channels."""
    if not TELEGRAM_BOT_TOKEN or not CHANNEL_CHAT_IDS:
        _log.info("[telegram] No credentials configured — skipping send.")
        return

    for chat_id in CHANNEL_CHAT_IDS:
        for idx, text in enumerate((post1, post2), 1):
            try:
                resp = requests.post(
                    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                    json={"chat_id": chat_id, "text": text[:4096]},
                    timeout=15,
                )
                resp.raise_for_status()
                _log.info("[telegram] Post %d sent to %s", idx, chat_id)
            except Exception as exc:
                _log_error(f"Telegram send failed for chat {chat_id} post {idx}: {exc}")


# ---------------------------------------------------------------------------
# Wiki update queue helper
# ---------------------------------------------------------------------------


def _queue_wiki_update(canon_names_used: list[str]) -> None:
    """
    Queue wiki update entries for any canon names not yet on the wiki.
    Writes to wiki-update-queue.json using the same format as Brain 2.
    """
    if not canon_names_used:
        return

    queue_file = os.path.join(BASE_DIR, "wiki-update-queue.json")
    try:
        with open(queue_file, "r", encoding="utf-8") as f:
            queue = json.load(f)
    except (OSError, json.JSONDecodeError):
        queue = []

    # Build a set of already-queued names (O(1) lookup) to avoid duplicates
    existing_names: set[str] = {
        item.get("name", "")
        for item in queue
        if isinstance(item, dict) and item.get("source") == "web-lore-agent"
    }

    ts = datetime.datetime.utcnow().isoformat()
    added_count = 0
    for name in canon_names_used:
        if name not in existing_names:
            queue.append({
                "type":   "canon-name-discovery",
                "source": "web-lore-agent",
                "name":   name,
                "added":  ts,
            })
            existing_names.add(name)
            added_count += 1

    with open(queue_file, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2)
    _log.info("[wiki-queue] Queued %d new canon name(s)", added_count)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    _log.info("=== Brain 3 — Web Lore Agent starting ===")

    # ── Load rules files ──────────────────────────────────────────────────
    sources_md     = _load_text_file(SOURCES_FILE)
    brain_rules    = _load_text_file(BRAIN_RULES_FILE)
    character_bible = _load_text_file(CHARACTER_FILE)
    weblore_rules  = _load_text_file(WEBLORE_RULES_FILE)

    if not sources_md:
        _log_error("Cannot find gkandcryptomoonboywebsitestosave.md — aborting.")
        raise SystemExit(1)

    # ── Parse official source URLs ────────────────────────────────────────
    all_official_urls = _extract_official_sources(sources_md)
    gkdata_real_urls  = _extract_gkdata_real_sources(sources_md)
    _log.info("[sources] %d total official URLs; %d gkdata-real", len(all_official_urls), len(gkdata_real_urls))

    # ── Load cache ────────────────────────────────────────────────────────
    cache = _load_cache()

    # ── A. Crawl phase ────────────────────────────────────────────────────
    _log.info("[crawl] Starting crawl phase …")
    new_snippets = crawl_sources(all_official_urls, cache)
    _log.info("[crawl] %d new content snippets found", len(new_snippets))

    # ── B. Canon name guard ───────────────────────────────────────────────
    _log.info("[canon] Running canon name guard …")
    all_candidate_names: list[str] = []
    for snippet in new_snippets:
        candidates = _extract_candidate_names(snippet["text"])
        all_candidate_names.extend(candidates)

    # Deduplicate
    all_candidate_names = list(dict.fromkeys(all_candidate_names))

    canon_results = canon_guard(all_candidate_names, gkdata_real_urls)

    canon_names_used: list[str] = []
    for name, info in canon_results.items():
        if info["canon"]:
            canon_names_used.append(name)
        else:
            _log_non_canon(name, info.get("source") or "unknown")

    _log.info("[canon] %d canon names; %d non-canon names logged",
              len(canon_names_used),
              sum(1 for v in canon_results.values() if not v["canon"]))

    # Filter snippets: only retain snippets whose source is an official URL
    # (all snippets from our crawl already are official; this is belt-and-braces)
    verified_snippets = [s for s in new_snippets if s["url"] in all_official_urls]

    # ── C. Lore composition ───────────────────────────────────────────────
    _log.info("[lore] Composing lore posts (30/70 split) …")
    try:
        lore = compose_lore(
            snippets=verified_snippets[:3],
            canon_names=canon_names_used,
            brain_rules=brain_rules,
            character_bible=character_bible,
            weblore_rules=weblore_rules,
        )
    except Exception as exc:
        _log_error(f"LLM lore generation failed: {exc}\n{traceback.format_exc()}")
        _log.error("[lore] Generation failed — see web-lore-errors.log")
        raise SystemExit(1)

    post1        = lore.get("post1", "")
    post2        = lore.get("post2", "")
    img_prompt1  = lore.get("image_prompt1", "")
    img_prompt2  = lore.get("image_prompt2", "")

    # ── D. Save output ────────────────────────────────────────────────────
    output = {
        "post1":            post1,
        "post2":            post2,
        "image_prompt1":    img_prompt1,
        "image_prompt2":    img_prompt2,
        "sources_used":     [s["url"] for s in verified_snippets[:3]],
        "canon_names_used": canon_names_used,
        "generated_at":     datetime.datetime.utcnow().isoformat(),
    }
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    _log.info("[output] Saved to %s", OUTPUT_FILE)

    # ── Update cache ──────────────────────────────────────────────────────
    _save_cache(cache)
    _log.info("[cache] Cache updated at %s", CACHE_FILE)

    # ── Optional Telegram send ────────────────────────────────────────────
    if WEB_LORE_TELEGRAM_ENABLED:
        _log.info("[telegram] WEB_LORE_TELEGRAM_ENABLED=true — sending posts …")
        _send_telegram(post1, post2)
    else:
        _log.info("[telegram] WEB_LORE_TELEGRAM_ENABLED=false — skipping send.")

    # ── Queue wiki updates for new canon names ────────────────────────────
    _queue_wiki_update(canon_names_used)

    _log.info("=== Brain 3 complete ===")


if __name__ == "__main__":
    main()
