import os
import json
import time
import random
from datetime import datetime, timezone
from openai import OpenAI
import telegram
import requests
from bs4 import BeautifulSoup

# Secrets
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROK_API_KEY = os.getenv("GROK_API_KEY")
CHANNEL_CHAT_IDS = os.getenv("CHANNEL_CHAT_IDS").split(",")

grok = OpenAI(base_url="https://api.x.ai/v1", api_key=GROK_API_KEY)
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# Load all locked content (100% of conversation)
with open("brain-rules.md", "r", encoding="utf-8") as f:
    BRAIN_RULES = f.read()
with open("character-bible.md", "r", encoding="utf-8") as f:
    CHARACTER_BIBLE = f.read()
try:
    with open("MASTER-CHARACTER-CANON.md", "r", encoding="utf-8") as f:
        MASTER_CANON = f.read()
except FileNotFoundError:
    MASTER_CANON = "MASTER-CHARACTER-CANON.md not found — using brain-rules.md and character-bible.md as full canon reference."

try:
    with open("lore-planner.md", "r", encoding="utf-8") as f:
        LORE_PLANNER = f.read()
except FileNotFoundError:
    LORE_PLANNER = "Lore planner not found — agent improvises based on weekly routine and locked rules."

# Persistent lore history for true 7-day continuity
LORE_HISTORY_FILE = "lore-history.md"
if os.path.exists(LORE_HISTORY_FILE):
    with open(LORE_HISTORY_FILE, "r", encoding="utf-8") as f:
        LORE_HISTORY = f.read()
else:
    LORE_HISTORY = "No previous lores yet — starting the infinite saga."

# Reply tracker (20 per user per 24h + keyword fail tracking)
REPLIED_FILE = "reply-tracker.json"
if os.path.exists(REPLIED_FILE):
    with open(REPLIED_FILE) as f:
        reply_tracker = json.load(f)
else:
    reply_tracker = {}

# ── Hidden keyword trigger list ──────────────────────────────────────────────
TRIGGER_KEYWORDS = [
    "expand", "continue", "more about", "storyline", "what happens next",
    "tell me more", "crypto moonboys", "moonboys", "moonboy", "lore",
    "graffpunk", "graffpunks", "lady-ink", "lady ink", "hardfork",
    "bonnet", "blocktopia", "hodl", "graffiti", "bitcoin x kids",
    "graffpunks network", "substack", "nft drop", "arc", "character",
    "gknifty", "gk", "gkbrain", "jodie zoom", "elder codex",
]


def has_trigger_keywords(text: str) -> bool:
    """Return True if the message contains at least one trigger keyword."""
    lower = text.lower()
    return any(kw in lower for kw in TRIGGER_KEYWORDS)


def get_user_record(user_id: str, today: str) -> dict:
    """Return (and auto-reset if stale) a user's daily record."""
    record = reply_tracker.get(user_id, {})
    if record.get("date") != today:
        # Midnight UTC reset
        record = {"date": today, "count": 0, "failed_attempts": 0}
    return record


def save_user_record(user_id: str, record: dict) -> None:
    reply_tracker[user_id] = record
    with open(REPLIED_FILE, "w") as f:
        json.dump(reply_tracker, f)


def handle_user_message(user_id: str, message_text: str) -> str | None:
    """
    Process a user message and return the reply text, or None for no reply.

    Rules (from TELEGRAM USER INTERACTION & LORE EXPANSION RULES):
    - Max 20 interactions per user per 24h (midnight UTC reset).
    - Only replies on Condition 1 (Moonboys/GK topic) or Condition 2 (lore expansion).
    - Hidden keyword trigger required — 2 fails max per day then silence.
    - All replies text-only (no images). Links allowed.
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    record = get_user_record(user_id, today)

    # Hard limit: no more replies after 20 per day
    if record["count"] >= 20:
        return None

    # Hard limit: no more keyword-fail replies after 2 per day
    if record["failed_attempts"] >= 2:
        return None

    # Check keyword triggers
    if not has_trigger_keywords(message_text):
        record["failed_attempts"] += 1
        save_user_record(user_id, record)
        if record["failed_attempts"] == 1:
            return "sorry please say the magic words"
        else:
            return "\U0001f4a9"

    # Keywords found — generate an organic lore reply via Grok
    record["count"] += 1
    save_user_record(user_id, record)

    prompt = f"""
    {BRAIN_RULES}
    {CHARACTER_BIBLE}
    {MASTER_CANON}

    PREVIOUS LORE HISTORY (last 7 days):
    {LORE_HISTORY[-4000:]}

    A Telegram user has sent this message: "{message_text}"

    Reply as the GK BRAIN in the artist's mind-log style.
    Stay 100% inside the first-person narrative voice.
    Text-based reply only — no images. Links to official GraffPunks/Substack/NFT pages are allowed.
    If expanding a lore: treat it as the artist expanding the saga in real time at home.
    Keep it organic, in-character, and reference the last 7 days of awake life for continuity.
    Maximum 500 words.
    """

    try:
        response = grok.chat.completions.create(
            model="grok-4-fast",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return None


# ── Fame Cycle ────────────────────────────────────────────────────────────────

# 24-hour UTC day has 4 × 6-hour fame slots: 00–06, 06–12, 12–18, 18–24
FAME_SLOT_NAMES = ["SLOT-A (00–06 UTC)", "SLOT-B (06–12 UTC)", "SLOT-C (12–18 UTC)", "SLOT-D (18–24 UTC)"]


def get_fame_cycle_slot(now: datetime) -> str:
    """
    Return the active 6-hour fame slot info for injection into the prompt.
    The agent picks 1–3 headliner characters from the canon for this slot.
    Actual character selection is delegated to the LLM based on lore-history.md rotation.
    """
    slot_index = now.hour // 6  # 0=00–06, 1=06–12, 2=12–18, 3=18–24
    slot_name = FAME_SLOT_NAMES[slot_index]
    return (
        f"ACTIVE 6-HOUR FAME SLOT: {slot_name}\n"
        "Assign 1, 2, or maximum 3 main Crypto Moonboys characters for this slot's fame run. "
        "Check lore-history.md for recently featured characters and do NOT repeat them. "
        "80% of this slot's content must focus on those characters (their thoughts, powers, arc, current situation). "
        "20% may weave in real-world news, sensory moments, or the artist's reactions. "
        "Deliver the fame run inside the correct lore window (WINDOW 1 = awake at home writing, WINDOW 2 = asleep dreaming)."
    )


def get_day_type() -> str:
    """Randomly assign one of three day types for today."""
    roll = random.random()
    if roll < 0.4:
        return "DAY TYPE: STRICT ROUTINE — Follow the weekly schedule tightly today."
    elif roll < 0.7:
        return "DAY TYPE: MULTI-RANDOM — Several unexpected things happen today (surprise rave invite, sudden fishing trip, unexpected Moonboys news, random London adventure)."
    else:
        return "DAY TYPE: SINGLE-FOCUS — He does mostly 1 or 2 things all day (all-day writing at home, or all-day fishing, or all-day van tour). Make the immersion deep."


# ── Art creation — dedicated page search ─────────────────────────────────────

# All official links to crawl for dedicated character pages (AC-1/AC-12)
OFFICIAL_ART_LINKS = [
    "https://substack.com/@graffpunks/posts",
    "https://graffpunks.substack.com/",
    "https://graffpunks.live/",
    "https://graffitikings.co.uk/",
    "https://gkniftyheads.com/",
    "https://medium.com/@GKniftyHEADS",
    "https://medium.com/@graffpunksuk",
    "https://neftyblocks.com/collection/gkstonedboys",
    "https://www.youtube.com/@GKniftyHEADS",
]

# Random face expressions for AC-8
FACE_EXPRESSIONS = [
    "surprised with wide eyes",
    "grinning wide showing teeth",
    "squinting focused intense stare",
    "jaw dropped in disbelief",
    "smirking sly half-grin",
    "eyes wide in pure awe",
    "brow furrowed serious and determined",
    "cackling head thrown back",
    "winking one eye closed",
    "thousand yard stare dead-eyed",
    "tongue out sideways cocky",
    "grimacing under pressure",
    "gleaming smile full confidence",
    "nostril flared furious",
    "dreamy eyes half-closed",
]



# Named thresholds for art page detection (AC-1 through AC-4)
MIN_MENTION_COUNT_FOR_DEDICATED_PAGE = 3   # page must mention the subject at least this many times
MAX_IMAGES_FROM_PAGE = 6                    # maximum reference images to extract from a dedicated page
MIN_TOKEN_LENGTH = 2                        # character names shorter than this are ignored when tokenising

def find_character_dedicated_page(character_name: str) -> dict:
    """
    Search official links for a page solely dedicated to the given character/subject.
    Returns a dict: {found: bool, url: str|None, images: list[str], description: str}

    AC-1, AC-2, AC-3, AC-4 — see brain-rules.md ART CREATION RULE.
    """
    name_lower = character_name.lower().replace("-", " ").replace("_", " ")
    name_tokens = [t for t in name_lower.split() if len(t) > MIN_TOKEN_LENGTH]

    result = {"found": False, "url": None, "images": [], "description": ""}

    for link in OFFICIAL_ART_LINKS:
        try:
            r = requests.get(link, timeout=8)
            soup = BeautifulSoup(r.text, "html.parser")

            # Score this page: how much of its visible text is about the character?
            page_text = soup.get_text(separator=" ").lower()
            match_count = sum(page_text.count(token) for token in name_tokens)

            # Require at least 3 mentions to treat it as "dedicated"
            if match_count >= MIN_MENTION_COUNT_FOR_DEDICATED_PAGE:
                images = [
                    img["src"]
                    for img in soup.find_all("img")
                    if img.get("src") and not img["src"].startswith("data:")
                ]
                result = {
                    "found": True,
                    "url": link,
                    "images": images[:MAX_IMAGES_FROM_PAGE],
                    "description": f"Dedicated page found for '{character_name}' at {link} ({match_count} mentions).",
                }
                return result
        except Exception:
            continue

    result["description"] = (
        f"No dedicated page found for '{character_name}' — using Layer 1 + Layer 2 base templates (AC-9)."
    )
    return result


def build_image_prompt_prefix(character_name: str, lore_mood: str, dedicated_page: dict) -> str:
    """
    Build the mandatory image prompt prefix per the ART CREATION RULE (AC-5 through AC-8).
    Head + bonnet as one unit, 90% shape fidelity, random face expression.
    """
    expression = random.choice(FACE_EXPRESSIONS)

    if dedicated_page["found"]:
        ref_note = (
            f"exact dedicated webpage reference for {character_name} from {dedicated_page['url']}"
        )
        if dedicated_page["images"]:
            ref_note += f" (key images: {' '.join(dedicated_page['images'][:3])})"
    else:
        ref_note = (
            f"Layer 1 upper body base + Layer 2 GraffPUNKS bonnet shape "
            f"(rounded yellow head/torso, exact eagle beak centre, eagle birds each side, "
            f"white feathers above eyes, green hair pulled through, yellow leather, ears out sides)"
        )

    return (
        f"Use 100% {ref_note}. "
        f"Head + bonnet as one inseparable unit. "
        f"Face expression: {expression} (matching lore mood: {lore_mood}). "
        f"90% shape fidelity to reference — colours, textures, and scene elements may vary freely. "
        f"Scene details:"
    )


def log_dedicated_page(character_name: str, url: str) -> None:
    """Append a newly found dedicated art page to lore-history.md (AC-14)."""
    entry = f"\n[DEDICATED ART PAGE] {character_name}: {url}\n"
    try:
        with open(LORE_HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception:
        pass


def crawl_substack_for_art_and_content():
    try:
        r = requests.get("https://substack.com/@graffpunks/posts", timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        images = [img["src"] for img in soup.find_all("img") if img.get("src")]
        text_snippets = [p.text.strip() for p in soup.find_all("p") if len(p.text.strip()) > 20]

        art_reference = (
            "Use exact GraffPunks Substack artwork style for all characters and factions: shapes, uniforms, silhouettes, colours, look. Found images: "
            + " ".join(images[:5])
            if images
            else "Fallback to GraffPunks Substack style from all posts."
        )
        new_content = (
            "New Substack content: " + " | ".join(text_snippets[:3])
            if text_snippets
            else "No new content — make up consistent lore until official data conflicts."
        )
        return art_reference + "\n" + new_content
    except Exception:
        return "Substack crawl failed — use existing Character Bible and make up consistent GraffPunks style until new official data appears."


def get_news_and_weather():
    try:
        weather = requests.get("https://wttr.in/London?format=%C+%t", timeout=10).text.strip()
        return f"Weather: {weather} | Latest crypto/political/graffiti news from last 2 hours."
    except Exception:
        return "Weather and news checked."


def get_post_mode(now: datetime) -> str:
    """
    Determine whether the current run is AWAKE or DREAM (and which dream type)
    based on the real UTC time and day of week.

    DREAM window: 23:00–06:00 UTC each night.
    - Monday 06:00 UTC                             → Monday wake-up dream (repeating mural chase)
    - Thursday 23:00–00:00 or Friday 00:00–06:00   → Lady-INK world train adventure dream
    - All other nights                             → Crypto Moonboys lore dream only

    Outside the dream window → AWAKE post.
    """
    weekday = now.weekday()  # 0=Mon … 6=Sun
    hour = now.hour

    in_dream_window = hour >= 23 or hour < 6

    # Thursday night spans Thursday 23:00 into Friday 06:00
    is_thursday_night = (weekday == 3 and hour >= 23) or (weekday == 4 and hour < 6)

    if weekday == 0 and hour == 6:
        return (
            "POST MODE: DREAM — MONDAY 6AM WAKE-UP\n"
            "This is the Monday 6am repeating unfinished mural chase dream (MR-D5). "
            "He wakes with 'what the hell? why?' Generate the recurring chase dream then the wake-up moment. "
            "After the wake-up, the next awake post continues directly from lore-history.md."
        )
    elif is_thursday_night:
        return (
            "POST MODE: DREAM — THURSDAY NIGHT LADY-INK WORLD TRAIN ADVENTURE (MR-D2)\n"
            "Generate a completely new, unique dream about him and Lady-INK travelling the world "
            "and painting graffiti on trains. Check lore-history.md for previously used Thursday adventures "
            "and use the next unused one from the 25-adventure library in brain-rules.md (LIB-1 through LIB-5). "
            "No Crypto Moonboys lore in this dream — it is ONLY the real-world travel painting adventure."
        )
    elif in_dream_window:
        return (
            "POST MODE: DREAM — CRYPTO MOONBOYS LORE ONLY (MR-D3/MR-D4)\n"
            "Generate a unique Crypto Moonboys dream featuring 1 or 2 main characters as headliners. "
            "Rotate through all characters — check lore-history.md for previously used pairings and do NOT repeat them. "
            "80% completely unique fantasy. No real-world daily-life content in this dream."
        )
    else:
        # Determine if this is a "working on lore at home" window or general awake
        # Between 09:00–17:00 UTC on non-travel days has the highest chance of home writing
        if 9 <= hour < 17 and weekday == 3:  # Thursday is the heavy Moonboys writing day (MR-D2/WINDOW 1)
            lore_window = (
                "AWAKE LORE WINDOW (WINDOW 1 — ARTIST AT HOME WORKING ON MOONBOYS LORE): "
                "This is one of the 2 daily windows where a full Crypto Moonboys fame run can be told. "
                "Write as if he is at his desk, actively working on the Moonboys saga — thoughts flowing, "
                "speaking lore out loud, expanding the infinity lores. Include the active fame cycle character(s). "
                "Weave in sensory details (MR-A6), live GraffPunks alerts (MR-A7), and news reactions (NR-1)."
            )
        else:
            lore_window = (
                "AWAKE REAL-LIFE WINDOW: "
                "This is a real-life daily habits window. No full Moonboys fame run unless he is explicitly "
                "shown sitting at home writing. Focus on: real daily life, weather, news reactions, sensory details, "
                "GraffPunks alerts, and the 30% out-of-home thought moments rule (MR-A8) if he is out."
            )

        return (
            f"POST MODE: AWAKE\n"
            f"Generate real-time awake posts (MR-A1 through MR-A8). "
            f"Write in first-person present tense — the reader is literally inside his head right now. "
            f"MUST include: (1) at least one current world news event, weather update, or holiday/seasonal reference, "
            f"(2) at least one real daily life moment (van tour, parkour, fishing, rave, painting night, Lady-INK meet, etc.), "
            f"(3) at least one sensory detail (MR-A6), "
            f"(4) real-life reactions to things happening around him right now. "
            f"Continue directly from the last 7 days of awake life in lore-history.md — no resets.\n"
            f"{lore_window}"
        )


def generate_lore_pair():
    substack_info = crawl_substack_for_art_and_content()
    now = datetime.now(timezone.utc)
    post_mode = get_post_mode(now)
    fame_slot = get_fame_cycle_slot(now)
    day_type = get_day_type()

    # ── Art creation: find dedicated pages for active characters (AC-1 through AC-14) ──
    # Use a generic "GraffPunks character" search if we don't know the exact characters yet;
    # the LLM will use specific names it picks for the fame slot.  We also try the main
    # Substack so at least Substack images are always available.
    substack_page = find_character_dedicated_page("GraffPunks Moonboys")
    art_prefix = build_image_prompt_prefix(
        character_name="the featured character(s)",
        lore_mood="matching the current lore post theme and time of day",
        dedicated_page=substack_page,
    )
    if substack_page["found"]:
        log_dedicated_page("GraffPunks Moonboys (general)", substack_page["url"])

    prompt = f"""
    {BRAIN_RULES}
    {CHARACTER_BIBLE}
    {MASTER_CANON}
    {substack_info}

    30-DAY LORE PLANNER (use the matching 2-hour slot for today as context seed):
    {LORE_PLANNER[:3000]}

    PREVIOUS LORE HISTORY (last 7 days - continue directly from here):
    {LORE_HISTORY[-8000:]}

    Current time: {now.strftime('%Y-%m-%d %H:%M:%S UTC')}
    {get_news_and_weather()}

    {post_mode}

    {fame_slot}

    {day_type}

    ART CREATION RULE (mandatory for BOTH image prompts in this post):
    Every image prompt MUST start with this exact prefix, then add the full scene description:
    "{art_prefix}"
    For each character featured, the head + bonnet must be treated as one inseparable unit.
    Use the dedicated page reference if one was found during this run's crawl, otherwise use
    Layer 1 + Layer 2 base templates. Add a random face expression matching the lore mood.
    90% shape fidelity. Colours and scene details may vary freely.

    Generate the next 2 back-to-back lore posts exactly as the rules say.
    Each post MUST start with the exact UTC time and log entry number:
    [Current Date] — [Current Time] UTC — GraffPunks Network Log Entry #[number]
    Use the Eternal Codex for all characters.
    For each post, generate a detailed image prompt using the ART CREATION RULE prefix above.
    Separate with ---POST-2---
    """

    response = grok.chat.completions.create(
        model="grok-4-fast",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4000,
    )

    text = response.choices[0].message.content
    parts = text.split("---POST-2---")
    post1 = parts[0].strip()
    post2 = parts[1].strip() if len(parts) > 1 else "Continuation of the lore..."

    # Append new posts to history for next run
    new_entry = (
        f"\n\n--- NEW POSTS {now.strftime('%Y-%m-%d %H:%M UTC')} "
        f"| MODE: {post_mode.splitlines()[0]} "
        f"| {fame_slot.splitlines()[0]} "
        f"| {day_type} ---\n"
        f"Post 1:\n{post1}\nPost 2:\n{post2}\n"
    )
    with open(LORE_HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(new_entry)

    return post1, post2


def post_to_telegram(text):
    for chat_id in CHANNEL_CHAT_IDS:
        try:
            bot.send_message(chat_id=chat_id.strip(), text=text)
            time.sleep(2)
        except Exception:
            pass


def main():
    print("GK BRAIN running at", datetime.now(timezone.utc))
    post1, post2 = generate_lore_pair()

    post_to_telegram(post1)
    print("✅ Post 1 sent")

    post_to_telegram(post2)
    print("✅ Post 2 sent")

    with open(REPLIED_FILE, "w") as f:
        json.dump(reply_tracker, f)


if __name__ == "__main__":
    main()
