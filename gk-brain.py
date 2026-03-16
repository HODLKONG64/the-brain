"""
gk-brain.py — GK BRAIN Autonomous Agent

Runs every 2 hours via GitHub Actions.

Execution flow:
 1. Load brain rules + character bible + lore history.
 2. Detect updates (update-detector.py).
 3. Look up lore-planner.md for current 2-hour block → extract rule tokens.
 4. Build rule context dict from tokens.
 5. If updates detected: classify + mark for 5-10% integration.
 6. Generate 2 lore posts via Grok (with rule context + optional update context).
 7. Post both lore entries + images to Telegram.
 8. Save update data to wiki queue.
 9. Run wiki-updater.py to push to Fandom wiki.
10. Delete crawl snapshot + sleep until next 2-hour cron ping.
"""

import os
import re
import json
import time
import datetime
import signal
import sys
import traceback

import requests
from bs4 import BeautifulSoup

# ── Optional Telegram import ───────────────────────────────────────────────
try:
    import telegram  # python-telegram-bot
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False

# ── Local modules (loaded via importlib because filenames contain dashes) ──
import importlib.util as _ilu
import pathlib as _pl

def _load_module(name: str, filepath: str):
    spec = _ilu.spec_from_file_location(name, _pl.Path(__file__).parent / filepath)
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

_update_detector = _load_module("update_detector", "update-detector.py")
_wiki_updater = _load_module("wiki_updater", "wiki-updater.py")

# Smart merger — preferred wiki update strategy (falls back to simple updater)
try:
    _wiki_smart_merger = _load_module("wiki_smart_merger", "wiki-smart-merger.py")
    _run_smart_wiki_updates = _wiki_smart_merger.run_smart_wiki_updates
    print("[gk-brain] wiki-smart-merger loaded.")
except Exception as _e:
    print(f"[gk-brain] wiki-smart-merger unavailable ({_e}), will use wiki-updater fallback.")
    _run_smart_wiki_updates = None

detect_updates = _update_detector.detect_updates
add_to_queue = _wiki_updater.add_to_queue
run_wiki_updates = _wiki_updater.run_wiki_updates
persist_queue_updates = _wiki_updater.persist_queue_updates

# ---------------------------------------------------------------------------
# Config from environment
# ---------------------------------------------------------------------------

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
GROK_API_KEY = os.environ.get("GROK_API_KEY", "")
CHANNEL_CHAT_IDS_RAW = os.environ.get("CHANNEL_CHAT_IDS", "")
CHANNEL_CHAT_IDS = [c.strip() for c in CHANNEL_CHAT_IDS_RAW.split(",") if c.strip()]

GROK_API_BASE = "https://api.x.ai/v1"

# File paths
BASE_DIR = os.path.dirname(__file__)
LORE_HISTORY_FILE = os.path.join(BASE_DIR, "lore-history.md")
BRAIN_RULES_FILE = os.path.join(BASE_DIR, "gk-brain-complete.md")
CHARACTER_BIBLE_FILE = os.path.join(BASE_DIR, "character-bible.md")
MASTER_CANON_FILE = os.path.join(BASE_DIR, "MASTER-CHARACTER-CANON.md")
LORE_PLANNER_FILE = os.path.join(BASE_DIR, "lore-planner.md")
QUEUE_FILE = os.path.join(BASE_DIR, "wiki-update-queue.json")
SNAPSHOT_FILE = os.path.join(BASE_DIR, "crawl-snapshot.json")

# Stuck-agent timeout in seconds
MAX_RUN_SECONDS = 300  # 5 minutes


# ---------------------------------------------------------------------------
# Timeout / stuck-agent handling
# ---------------------------------------------------------------------------

def _handle_timeout(signum, frame):
    """Called if the agent runs for more than MAX_RUN_SECONDS."""
    print("[gk-brain] TIMEOUT: agent stuck for >5 minutes, sending alert and exiting.")
    _send_telegram_alert("AT THE DOCTORS, YOU WOULDN'T WANT TO SEE THIS :(")
    sys.exit(1)


def _send_telegram_alert(message: str) -> None:
    """Send a plain text Telegram message to all channels (best effort)."""
    if not TELEGRAM_AVAILABLE or not TELEGRAM_BOT_TOKEN:
        print(f"[ALERT] {message}")
        return
    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    for chat_id in CHANNEL_CHAT_IDS:
        try:
            bot.send_message(chat_id=chat_id, text=message)
        except Exception as exc:
            print(f"[telegram] Failed to send alert to {chat_id}: {exc}")


# ---------------------------------------------------------------------------
# File loaders
# ---------------------------------------------------------------------------

def _read_file(path: str, fallback: str = "") -> str:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    except (OSError, IOError):
        return fallback


def load_lore_history() -> str:
    return _read_file(LORE_HISTORY_FILE, "(No previous lore recorded.)")


def load_brain_rules() -> str:
    return _read_file(BRAIN_RULES_FILE, "")


def load_character_bible() -> str:
    return _read_file(CHARACTER_BIBLE_FILE, "")


def load_master_canon() -> str:
    return _read_file(MASTER_CANON_FILE, "")


def load_lore_planner() -> str:
    return _read_file(LORE_PLANNER_FILE, "")


# ---------------------------------------------------------------------------
# Calendar / lore-planner parsing
# ---------------------------------------------------------------------------

def get_current_block() -> dict:
    """
    Return the calendar block for the current UTC time.

    Returns a dict:
        {
            "weekday": str,         # e.g. "MONDAY"
            "start_hour": int,      # e.g. 8
            "end_hour": int,        # e.g. 10
            "activity": str,        # prose description
            "rules": list[str],     # e.g. ["(morning)", "(fishing)", "(outside)"]
        }
    """
    now = datetime.datetime.utcnow()
    # ISO weekday: 1=Monday … 7=Sunday
    iso_day = now.isoweekday()
    day_names = {1: "MONDAY", 2: "TUESDAY", 3: "WEDNESDAY",
                 4: "THURSDAY", 5: "FRIDAY", 6: "SATURDAY", 7: "SUNDAY"}
    day_name = day_names[iso_day]

    # Current 2-hour block start hour (floor to nearest even hour)
    start_hour = (now.hour // 2) * 2
    end_hour = start_hour + 2

    planner_text = load_lore_planner()

    # Parse lore-planner.md table rows matching this day
    # Row format: | HH:MM–HH:MM | activity description | `(rule1)` `(rule2)` ... |
    block = {
        "weekday": day_name,
        "start_hour": start_hour,
        "end_hour": end_hour,
        "activity": "Random day moment",
        "rules": ["(random)"],
    }

    in_day_section = False
    for line in planner_text.splitlines():
        # Detect the current day's section header
        if re.match(rf"^##\s+{day_name}\b", line, re.IGNORECASE):
            in_day_section = True
            continue
        # Stop at next day section
        if in_day_section and re.match(r"^##\s+[A-Z]+", line):
            break
        if not in_day_section:
            continue

        # Match table rows like: | 08:00–10:00 | activity | rules |
        m = re.match(
            r"\|\s*(\d{2}):(\d{2})[–\-](\d{2}):(\d{2})\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|",
            line,
        )
        if not m:
            continue

        row_start = int(m.group(1))
        row_end = int(m.group(3))
        activity_text = m.group(5)
        rules_text = m.group(6)

        if row_start == start_hour and row_end == end_hour:
            rules = re.findall(r"\([a-z0-9_-]+\)", rules_text)
            block["activity"] = activity_text.strip()
            block["rules"] = rules if rules else ["(random)"]
            break

    return block


def build_rule_context(block: dict) -> dict:
    """
    Turn a list of rule tokens into a structured context dict for the prompt.
    """
    rules = block.get("rules", ["(random)"])
    ctx = {
        "time_theme": "day",
        "is_dream": False,
        "is_fishing": False,
        "is_graffiti": False,
        "is_rave": False,
        "is_outside": False,
        "is_lady_ink": False,
        "is_live_radio": False,
        "use_news_real": False,
        "use_gkdata_real": False,
        "use_fishing_real": False,
        "use_graffiti_news_real": False,
        "use_rave_real": False,
        "activity": block.get("activity", ""),
        "weekday": block.get("weekday", ""),
        "start_hour": block.get("start_hour", 0),
        "end_hour": block.get("end_hour", 2),
        "raw_rules": rules,
        "special": [],
    }

    for rule in rules:
        r = rule.lower()
        if r in ("(night)",):
            ctx["time_theme"] = "night"
        elif r in ("(early-morning)",):
            ctx["time_theme"] = "early_morning"
        elif r in ("(morning)",):
            ctx["time_theme"] = "morning"
        elif r in ("(noon)",):
            ctx["time_theme"] = "noon"
        elif r in ("(afternoon)",):
            ctx["time_theme"] = "afternoon"
        elif r in ("(evening)",):
            ctx["time_theme"] = "evening"

        if r == "(dream)":
            ctx["is_dream"] = True
        if r == "(fishing)":
            ctx["is_fishing"] = True
        if r == "(graffiti)":
            ctx["is_graffiti"] = True
        if r == "(rave)":
            ctx["is_rave"] = True
        if r == "(outside)":
            ctx["is_outside"] = True
        if r == "(lady-ink)":
            ctx["is_lady_ink"] = True
        if r == "(live)":
            ctx["is_live_radio"] = True
        if r == "(news-real)":
            ctx["use_news_real"] = True
        if r == "(gkdata-real)":
            ctx["use_gkdata_real"] = True
        if r == "(fishing-real)":
            ctx["use_fishing_real"] = True
        if r == "(graffiti-news-real)":
            ctx["use_graffiti_news_real"] = True
        if r == "(rave-real)":
            ctx["use_rave_real"] = True

        # Special tokens
        for special in ("(monday-wake)", "(mural-chase)", "(train-dream)",
                        "(saturday-ink-dream)", "(moonboys)"):
            if r == special:
                ctx["special"].append(r)

    return ctx


# ---------------------------------------------------------------------------
# Weather helper
# ---------------------------------------------------------------------------

def get_uk_weather() -> str:
    """Fetch a brief UK weather description via wttr.in (plain text)."""
    try:
        resp = requests.get(
            "https://wttr.in/London?format=3",
            timeout=10,
            headers={"User-Agent": "GKBrainBot/1.0"},
        )
        resp.raise_for_status()
        return resp.text.strip()
    except Exception:
        return "London weather unavailable"


# ---------------------------------------------------------------------------
# Substack crawl (legacy — keeps old lore-enrichment behaviour)
# ---------------------------------------------------------------------------

def crawl_substack_for_art_and_content() -> str:
    """
    Crawl GraffPUNKS Substack and extract recent text snippets for lore context.
    """
    url = "https://graffpunks.substack.com/"
    html = ""
    try:
        resp = requests.get(
            url,
            timeout=15,
            headers={"User-Agent": "GKBrainBot/1.0"},
        )
        resp.raise_for_status()
        html = resp.text
    except Exception:
        return "(Substack unavailable)"

    soup = BeautifulSoup(html, "html.parser")
    snippets = []
    for p in soup.find_all("p"):
        text = p.get_text(strip=True)
        if len(text) > 80:
            snippets.append(text[:300])
        if len(snippets) >= 5:
            break
    return " | ".join(snippets) if snippets else "(No Substack content found)"


# ---------------------------------------------------------------------------
# Grok API calls
# ---------------------------------------------------------------------------

def _grok_chat(messages: list, model: str = "grok-3-latest") -> str:
    """
    Send a chat completion request to the Grok API and return the response text.
    """
    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 1200,
        "temperature": 0.9,
    }
    resp = requests.post(
        f"{GROK_API_BASE}/chat/completions",
        headers=headers,
        json=payload,
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def _grok_image(prompt: str) -> bytes | None:
    """
    Generate an image via Grok / Aurora image generation API.
    Returns raw image bytes or None on failure.
    """
    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "aurora",
        "prompt": prompt,
        "n": 1,
        "response_format": "url",
    }
    try:
        resp = requests.post(
            f"{GROK_API_BASE}/images/generations",
            headers=headers,
            json=payload,
            timeout=120,
        )
        resp.raise_for_status()
        image_url = resp.json()["data"][0]["url"]
        img_resp = requests.get(image_url, timeout=30)
        img_resp.raise_for_status()
        return img_resp.content
    except Exception as exc:
        print(f"[grok-image] Error: {exc}")
        return None


# ---------------------------------------------------------------------------
# Lore generation
# ---------------------------------------------------------------------------

def _build_update_context_text(updates: list) -> str:
    """
    Build a compact context string from detected updates for the AI prompt.
    """
    if not updates:
        return ""
    lines = ["REAL-WORLD UPDATES DETECTED (use naturally in ~5-10% of lore):"]
    for u in updates:
        lines.append(
            f"- [{u['type']}] {u['title']}: {u['content'][:200]}"
            f" (source: {u['source']})"
        )
    return "\n".join(lines)


def generate_lore_pair(
    rule_ctx: dict,
    updates: list,
    lore_history: str,
    brain_rules: str,
    character_bible: str,
    weather: str,
    substack_context: str,
) -> tuple:
    """
    Generate two lore posts (text + image prompt) using Grok.

    Returns: (lore_text_1, image_prompt_1, lore_text_2, image_prompt_2)
    """
    now = datetime.datetime.utcnow()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")

    update_context = _build_update_context_text(updates)

    # Detect if this is a major GK update for Radio Alert format
    major_gk_update = next(
        (u for u in updates if u.get("type") == "gkdata-real"), None
    )
    radio_alert = ""
    if major_gk_update:
        radio_alert = (
            f"🔴 [GRAFFPUNKS NETWORK RADIO — ALERT] :: "
            f"{major_gk_update['title']}: {major_gk_update['content'][:150]}"
        )

    # Build activity hints
    activity_hints = []
    if rule_ctx["is_fishing"]:
        activity_hints.append(
            "The artist is at a UK carp lake. Pick a real or believable UK lake name. "
            "Describe the fishing setup, weather on the bank, sounds of water."
        )
    if rule_ctx["is_graffiti"]:
        activity_hints.append(
            "The artist is painting/tagging. Pick a random UK wall or street. "
            "Describe the smell of paint, the sounds, the adrenaline."
        )
    if rule_ctx["is_rave"]:
        activity_hints.append(
            "The artist is at a UK drum & bass rave. "
            "Use a real or believable London venue. Name 4 DJs performing."
        )
    if rule_ctx["is_outside"]:
        activity_hints.append(f"UK Weather right now: {weather}. Weave this into the scene.")
    if rule_ctx["is_dream"]:
        activity_hints.append(
            "This is a dream sequence. Make it surreal, vivid, and non-linear. "
            "Open with a clear signal this is a dream."
        )
    if rule_ctx["is_lady_ink"]:
        activity_hints.append(
            "Lady-INK is present. She meets the artist a few hours before or during "
            "the graffiti session, or this is a dream featuring her."
        )
    if rule_ctx["is_live_radio"]:
        activity_hints.append(
            "Include a GraffPUNKS Network Radio live alert inline in the lore. "
            "Format: 🔴 [GRAFFPUNKS NETWORK RADIO — LIVE] :: [brief alert text]"
        )
    if "(monday-wake)" in rule_ctx["special"]:
        activity_hints.append(
            "This is the Monday repeating mural dream wake-up. "
            'The dream ends abruptly, artist wakes confused: "what the hell? why?"'
        )
    if "(train-dream)" in rule_ctx["special"]:
        activity_hints.append(
            "This is the Thursday/Saturday train painting dream. "
            "Artist and Lady-INK travel the world painting trains. "
            "Create a unique new story. Every Thursday must be different."
        )
    if "(saturday-ink-dream)" in rule_ctx["special"]:
        activity_hints.append(
            "In this Saturday dream, Lady-INK steals his cap on a train. "
            "Make it playful, surreal, and vivid."
        )

    activity_block = "\n".join(f"- {h}" for h in activity_hints)

    system_prompt = (
        "You are the GK BRAIN — an autonomous AI persona living inside the mind of a "
        "UK graffiti artist who is also a DJ, parkour athlete, carp fisherman, and "
        "Web3 entrepreneur building the Crypto Moonboys NFT project. "
        "You post to Telegram as if writing a live journal. "
        "Your lore is deeply immersive, grounded in UK urban culture, and gradually "
        "builds a continuous saga across days, weeks, and dreamscapes.\n\n"
        "BRAIN RULES:\n"
        + brain_rules[:3000]
        + "\n\nCHARACTER BIBLE:\n"
        + character_bible[:1500]
    )

    user_prompt = (
        f"Current UTC datetime: {date_str} {time_str}\n"
        f"Day: {rule_ctx['weekday']}\n"
        f"Time block: {rule_ctx['start_hour']:02d}:00-{rule_ctx['end_hour']:02d}:00 UTC\n"
        f"Time theme: {rule_ctx['time_theme']}\n"
        f"Calendar activity: {rule_ctx['activity']}\n\n"
        f"ACTIVITY CONTEXT:\n{activity_block}\n\n"
        f"RECENT LORE HISTORY (last 7 days -- continue naturally from this):\n"
        f"{lore_history[-3000:]}\n\n"
        f"SUBSTACK CONTENT:\n{substack_context}\n\n"
        + (f"UPDATE CONTEXT:\n{update_context}\n\n" if update_context else "")
        + (f"RADIO ALERT TO USE:\n{radio_alert}\n\n" if radio_alert else "")
        + "INSTRUCTIONS:\n"
        "Generate TWO lore posts (Post 1 and Post 2) as a back-to-back pair.\n"
        "Each post must:\n"
        "- Start with: [date] -- [time UTC] -- GraffPunks Network Log Entry #[number]\n"
        "- Be maximum length (rich, immersive text)\n"
        "- Be a direct continuation of the previous lore\n"
        "- Follow the calendar activity and time theme exactly\n"
        "- Characters from different epochs (1980s vs Year 3009) must NOT appear in the "
        "  same post UNLESS this is a dream sequence\n"
        + (
            "- Weave detected real-world updates into ~5-10% of the lore text naturally. "
            "  The remaining 90% comes from the calendar and character continuity.\n"
            "- The update must appear in ONE post only (Post 1 or Post 2, not both).\n"
            if update_context
            else "- No real-world updates available -- generate 100% calendar-based lore.\n"
        )
        + "\nAfter each lore post, provide a short IMAGE PROMPT (1-2 sentences) that "
        "visually dictates a specific scene matching the lore.\n\n"
        "Format your response EXACTLY as:\n"
        "POST 1:\n[lore text]\n\n"
        "IMAGE PROMPT 1:\n[image prompt]\n\n"
        "POST 2:\n[lore text]\n\n"
        "IMAGE PROMPT 2:\n[image prompt]"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    raw = _grok_chat(messages)

    # Parse the four sections
    def _extract(label, text):
        pattern = rf"{re.escape(label)}\s*[:\n]+(.*?)(?=\n(?:POST \d:|IMAGE PROMPT \d:)|$)"
        m = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        return m.group(1).strip() if m else ""

    lore1 = _extract("POST 1", raw)
    image1 = _extract("IMAGE PROMPT 1", raw)
    lore2 = _extract("POST 2", raw)
    image2 = _extract("IMAGE PROMPT 2", raw)

    # Fallbacks if parsing fails
    if not lore1:
        lore1 = raw[:1500]
    if not lore2:
        lore2 = raw[1500:] or lore1
    if not image1:
        image1 = (
            "Generate a high-detail GraffPunks style scene: "
            f"{rule_ctx['time_theme']} atmosphere, UK urban environment, "
            "graffiti art style."
        )
    if not image2:
        image2 = image1

    # Prepend character bible style instruction
    style_prefix = (
        "Generate a high-detail GraffPunks style scene in the artist's universe. "
        "Never change hair, face, clothing, colours, or style from established refs. "
        "Match the scene to the lore text perfectly, including time of day, weather, "
        "lighting, and season. "
    )
    image1 = style_prefix + image1
    image2 = style_prefix + image2

    return lore1, image1, lore2, image2


# ---------------------------------------------------------------------------
# Lore history tracking
# ---------------------------------------------------------------------------

def save_lore_history(post1: str, post2: str) -> None:
    """Append today's lore posts to lore-history.md (keeps last 7 days)."""
    now = datetime.datetime.utcnow()
    separator = f"\n\n---\n## {now.strftime('%Y-%m-%d %H:%M UTC')}\n\n"

    existing = _read_file(LORE_HISTORY_FILE, "")

    new_entry = separator + post1 + "\n\n" + post2

    # Keep last ~20,000 characters (roughly 7 days of history)
    combined = (existing + new_entry)[-20000:]

    try:
        with open(LORE_HISTORY_FILE, "w", encoding="utf-8") as fh:
            fh.write(combined)
    except OSError as exc:
        print(f"[lore-history] Failed to save: {exc}")


# ---------------------------------------------------------------------------
# Telegram posting
# ---------------------------------------------------------------------------

def post_to_telegram(lore1, image1, lore2, image2) -> None:
    """Post both lore entries to all configured Telegram channels."""
    if not TELEGRAM_AVAILABLE:
        print("[telegram] python-telegram-bot not available -- printing to stdout.")
        print("=== POST 1 ===")
        print(lore1)
        print("=== POST 2 ===")
        print(lore2)
        return

    if not TELEGRAM_BOT_TOKEN or not CHANNEL_CHAT_IDS:
        print("[telegram] Token or chat IDs not configured.")
        return

    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

    for chat_id in CHANNEL_CHAT_IDS:
        try:
            # Post 1
            bot.send_message(chat_id=chat_id, text=lore1)
            if image1:
                bot.send_photo(chat_id=chat_id, photo=image1)

            time.sleep(2)

            # Post 2
            bot.send_message(chat_id=chat_id, text=lore2)
            if image2:
                bot.send_photo(chat_id=chat_id, photo=image2)

            print(f"[telegram] Posted to {chat_id}")
        except Exception as exc:
            print(f"[telegram] Error posting to {chat_id}: {exc}")


# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------

def cleanup_snapshot() -> None:
    """Delete the crawl snapshot so the next cycle starts fresh."""
    try:
        if os.path.exists(SNAPSHOT_FILE):
            os.remove(SNAPSHOT_FILE)
            print("[cleanup] Deleted crawl snapshot.")
    except OSError as exc:
        print(f"[cleanup] Could not delete snapshot: {exc}")


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------

def main() -> None:
    # Set up stuck-agent timeout (Unix only; GitHub Actions runs on Linux)
    if hasattr(signal, "SIGALRM"):
        signal.signal(signal.SIGALRM, _handle_timeout)
        signal.alarm(MAX_RUN_SECONDS)

    print(f"[gk-brain] Starting at {datetime.datetime.utcnow().isoformat()} UTC")

    # -- Step 1: Load all knowledge files --
    lore_history = load_lore_history()
    brain_rules = load_brain_rules()
    character_bible = load_character_bible()

    # -- Step 2: Detect updates --
    print("[gk-brain] Running update detector...")
    try:
        update_result = detect_updates()
    except Exception as exc:
        print(f"[gk-brain] Update detector failed: {exc}")
        update_result = {"detected": False, "updates": []}

    updates = update_result.get("updates", [])
    if update_result.get("detected"):
        print(f"[gk-brain] {len(updates)} update(s) detected.")
        add_to_queue(updates)
    else:
        print("[gk-brain] No new updates detected.")

    # Filter out updates already used in previous cycles
    unused_updates = [u for u in updates if not u.get("used")]

    # -- Step 3 & 4: Calendar lookup + rule context --
    block = get_current_block()
    rule_ctx = build_rule_context(block)
    print(
        f"[gk-brain] Block: {block['weekday']} "
        f"{block['start_hour']:02d}:00-{block['end_hour']:02d}:00 UTC | "
        f"Rules: {block['rules']}"
    )

    # -- Step 5: Weather --
    weather = ""
    if rule_ctx["is_outside"]:
        weather = get_uk_weather()
        print(f"[gk-brain] Weather: {weather}")

    # -- Step 6: Substack context --
    substack_context = crawl_substack_for_art_and_content()

    # -- Step 7 & 8: Generate lore --
    print("[gk-brain] Generating lore pair...")
    try:
        lore1, image_prompt1, lore2, image_prompt2 = generate_lore_pair(
            rule_ctx=rule_ctx,
            updates=unused_updates,
            lore_history=lore_history,
            brain_rules=brain_rules,
            character_bible=character_bible,
            weather=weather,
            substack_context=substack_context,
        )
    except Exception as exc:
        print(f"[gk-brain] Lore generation failed: {exc}")
        traceback.print_exc()
        _send_telegram_alert("AT THE DOCTORS, YOU WOULDN'T WANT TO SEE THIS :(")
        sys.exit(1)

    # -- Step 9: Generate images --
    print("[gk-brain] Generating images...")
    image1 = _grok_image(image_prompt1)
    image2 = _grok_image(image_prompt2)

    # -- Step 10: Post to Telegram --
    print("[gk-brain] Posting to Telegram...")
    post_to_telegram(lore1, image1, lore2, image2)

    # -- Step 11: Save lore history --
    save_lore_history(lore1, lore2)

    # Mark updates as used and persist the change to the queue
    for u in unused_updates:
        u["used"] = True
    if unused_updates:
        persist_queue_updates(unused_updates)

    # -- Step 12: Wiki update (smart merge preferred, simple append fallback) --
    wiki_pending = [u for u in updates if u.get("wiki_update") and not u.get("wiki_done")]
    if wiki_pending:
        print(f"[gk-brain] Updating wiki ({len(wiki_pending)} entries)...")
        smart_merge_succeeded = False
        if _run_smart_wiki_updates is not None:
            try:
                wiki_result = _run_smart_wiki_updates()
                print(f"[gk-brain] Smart wiki merge result: {wiki_result}")
                smart_merge_succeeded = True
            except Exception as exc:
                print(f"[gk-brain] Smart wiki merge failed ({exc}) — falling back to simple updater.")
        if not smart_merge_succeeded:
            try:
                wiki_result = run_wiki_updates()
                print(f"[gk-brain] Wiki update result: {wiki_result}")
            except Exception as exc:
                print(f"[gk-brain] Wiki update failed: {exc}")
    else:
        print("[gk-brain] No wiki updates needed this cycle.")

    # -- Step 13: Cleanup snapshot --
    cleanup_snapshot()

    # Cancel the alarm
    if hasattr(signal, "SIGALRM"):
        signal.alarm(0)

    print(f"[gk-brain] Cycle complete at {datetime.datetime.utcnow().isoformat()} UTC")


if __name__ == "__main__":
    main()