import asyncio
import os
import json
import random
from datetime import datetime, timezone
from openai import OpenAI
import telegram
from telegram import BotCommand
import requests
from bs4 import BeautifulSoup

# Secrets
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROK_API_KEY = os.getenv("GROK_API_KEY")
CHANNEL_CHAT_IDS = os.getenv("CHANNEL_CHAT_IDS").split(",")

grok = OpenAI(base_url="https://api.x.ai/v1", api_key=GROK_API_KEY)

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

# Persistent bot state: tracks the last processed update_id so the bot never
# re-handles the same Telegram message across the 2-hour cron runs.
BOT_STATE_FILE = "bot-state.json"
if os.path.exists(BOT_STATE_FILE):
    with open(BOT_STATE_FILE) as f:
        bot_state = json.load(f)
else:
    bot_state = {"last_update_id": 0}


# ── Telegram command definitions ─────────────────────────────────────────────
# These are registered with BotFather so they appear in the / command menu.
TELEGRAM_COMMANDS = [
    BotCommand("start",      "Welcome to GK BRAIN — quick-start guide"),
    BotCommand("help",       "Full list of all commands"),
    BotCommand("lore",       "Show the latest lore post"),
    BotCommand("status",     "Current brain status: fame slot, mode, last post"),
    BotCommand("whosnext",   "Which characters star in the next 6-hour fame slot"),
    BotCommand("characters", "List all main characters in the Eternal Codex"),
    BotCommand("factions",   "List all factions with brief descriptions"),
    BotCommand("hardfork",   "Explain the Hardfork Games (rules, stages, prizes)"),
    BotCommand("links",      "All official GraffPunks links"),
    BotCommand("expand",     "Expand the last posted lore further"),
    BotCommand("about",      "Quick-bio for a character — usage: /about LadyINK"),
    BotCommand("artrule",    "Show the locked art creation rule and image prompt prefix"),
]

# Human-readable descriptions used in /help
COMMAND_HELP_TEXT = """🤖 *GK BRAIN — ALL COMMANDS*

📖 *LORE & CONTENT*
/lore — Latest lore post
/expand — Continue the last lore further
/about [name] — Quick-bio for any character (e.g. /about LadyINK)
/whosnext — Characters starring in the next 6-hour fame slot

📚 *WORLD INFO*
/characters — Full character list from the Eternal Codex
/factions — All factions (Crowned Royal Moongirls, HODL X Warriors, etc.)
/hardfork — The Hardfork Games: rules, 3 stages, prizes

🎨 *ART*
/artrule — The locked art creation rule (head+bonnet shape, 96% fidelity, clothing uniform lock, image prompt prefix)

🔗 *LINKS & STATUS*
/links — All official GraffPunks links (Substack, NFT, socials)
/status — Brain status: current fame slot, awake/dream mode, last post time

ℹ️ *HELP*
/start — Quick-start guide
/help — This message

━━━━━━━━━━━━━━━━━━━━
All replies are text-only. Max 20 interactions/user/day (resets midnight UTC).
Keyword triggers required — say the magic words to unlock the lore. 🌙"""

STATIC_COMMAND_RESPONSES = {
    "/start": (
        "🌙 *GK BRAIN ONLINE*\n\n"
        "I am the Crypto Moonboys lore engine — broadcasting from deep inside City Block Topia.\n\n"
        "Every 2 hours I post a new lore entry from the GraffPunks saga.\n"
        "Every 6 hours a new character gets their fame slot.\n\n"
        "Type /help for all commands.\n"
        "Type /lore to read the latest post.\n"
        "Type /links for all official GraffPunks links.\n\n"
        "The infinite saga is live. 🎨🖤"
    ),
    "/factions": (
        "🏙️ *FACTIONS OF BLOCKTOPIA*\n\n"
        "👑 *Crowned Royal Moongirls* — Elite ascended women with living neon halo crowns. "
        "Run City Block Topia alongside the HODL X Warriors.\n\n"
        "⚔️ *HODL X Warriors* — Champions who won the Hardfork Games. "
        "Defenders of Blocktopia, paired with Crowned Royal Moongirls.\n\n"
        "🚀 *Bitcoin X Kids* — Three paths: Space Programme, City Worker, or Escape. "
        "Most who escape regret it and wish to return.\n\n"
        "🏃 *OG Bitcoin Kids* — First generation to escape. "
        "Their stories are cautionary tales of regret and freedom.\n\n"
        "🎭 *Bald-headed Wannabe Moonboys (40)* — Outside Blocktopia trying to earn entry. "
        "NOT the same as bald-headed Moonboys born inside.\n\n"
        "🏢 *The Grid* — Everyday citizens of City Block Topia. Workers, residents, the backbone."
    ),
    "/hardfork": (
        "⚡ *THE HARDFORK GAMES*\n\n"
        "The ultimate competition inside Blocktopia. Three stages:\n\n"
        "1️⃣ *Parkour Gauntlet* — Navigate the city's lethal geometry at full sprint.\n"
        "2️⃣ *Spray Cipher* — Encode your identity in a living mural that the chain must verify.\n"
        "3️⃣ *Final Hardfork* — A one-on-one consensus battle — split the chain or merge it.\n\n"
        "🏆 *PRIZE*: Winners become HODL X Warriors and are paired with a Crowned Royal Moongirl.\n\n"
        "The Games run on an unpredictable schedule — no warning, no mercy."
    ),
    "/links": (
        "🔗 *OFFICIAL GRAFFPUNKS LINKS*\n\n"
        "📰 Substack (lore + art): https://substack.com/@graffpunks/posts\n"
        "🎨 GraffPunks Live: https://graffpunks.live/\n"
        "🖼️ Graffiti Kings: https://graffitikings.co.uk/\n"
        "🃏 GKniftyHEADS NFT: https://gkniftyheads.com/\n"
        "📝 Medium (GKniftyHEADS): https://medium.com/@GKniftyHEADS\n"
        "📝 Medium (GraffPunks): https://medium.com/@graffpunksuk\n"
        "🎮 NeftyBlocks: https://neftyblocks.com/collection/gkstonedboys\n"
        "▶️ YouTube: https://www.youtube.com/@GKniftyHEADS\n\n"
        "All official content crawled every 2 hours for new lore and art references. 🔄"
    ),
    "/artrule": (
        "🎨 *ART CREATION RULE (locked forever)*\n\n"
        "Before generating any image, the agent must:\n\n"
        "1️⃣ *Find the dedicated page* — Crawl all official links for a page 100% solely dedicated "
        "to the character/bonnet/theme.\n\n"
        "2️⃣ *Head + bonnet as ONE unit* — Lock in the head + bonnet silhouette together. "
        "96% shape fidelity required — all 3D elements locked. 4% creative zone for minor details only.\n\n"
        "3️⃣ *Random face expression* — Matches the lore mood of that post.\n\n"
        "4️⃣ *Clothing = main uniform always* — Unless a Uniform Exception Trigger (UF-1–UF-8) is "
        "explicitly active in the lore. Holiday, scenery change, Hardfork Games, dream mode, "
        "weather, arc milestone, or new official data can trigger an exception.\n\n"
        "5️⃣ *No dedicated page?* — Use Layer 1 (upper body base) + Layer 2 (GraffPUNKS bonnet). "
        "Still 96% fidelity. Temporary until a dedicated page is found.\n\n"
        "6️⃣ *No bonnet?* — Agent creates a unique bonnet from known bonnet inspirations (BF-3). "
        "Replaced immediately when official data is found.\n\n"
        "7️⃣ *Crawl before every post* — Official sites checked for new pages/details before any image.\n\n"
        "📋 *MANDATORY IMAGE PROMPT PREFIX*:\n"
        "_\"Use 100% Layer 1 upper body base + 100% Layer 2 bonnet shape "
        "(or the exact dedicated webpage reference if found). "
        "Head + bonnet as one unit. Random face expression to match the lore theme. "
        "96% shape fidelity. Clothing: main faction uniform (unless UF exception active). "
        "Black charcoal pencil style if requested.\"_"
    ),
    "/characters": (
        "👥 *MAIN CHARACTERS — ETERNAL CODEX*\n\n"
        "• *Lady-INK* — Artist's real girlfriend. Mixed-race, looks like Beyoncé. "
        "Black tracksuit, trainers, rucksack of paint. Bridge between real world and Blocktopia.\n"
        "• *Elder Codex-7* — Last surviving Chain Scribe. Year 3008 Grid Archives.\n"
        "• *Charlie Buster* — Legendary UK street artist. Leake Street Tunnel. NFT creator.\n"
        "• *Bone Idol Ink* — Tattoo artist. Turns skin and walls into permanent Moonboys stories.\n"
        "• *Delicious Again Peter* — Chef who turns food into narrative graffiti concepts.\n"
        "• *AI-Chunks* — AI artist merging real graffiti with Blocktopia digital art.\n"
        "• *Jodie Zoom* — Key GraffPunks crew member.\n\n"
        "Groups: Crowned Royal Moongirls, HODL X Warriors, Bitcoin X Kids (3 paths), "
        "OG Bitcoin Kids, Bald-headed Wannabe Moonboys (40), The Grid.\n\n"
        "Type /about [name] for a full character bio."
    ),
}
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

# All official links to crawl for dedicated character pages (AC-1/AC-12).
# Full list from gk-brain-complete.md — covers all GK/Moonboys properties,
# Charlie Buster & Treef Project, and real-people canon links.
# Social-media platforms that block scraping are intentionally excluded.
OFFICIAL_ART_LINKS = [
    # Core GraffPunks / GK / Moonboys properties
    "https://substack.com/@graffpunks/posts",
    "https://graffpunks.substack.com/",
    "https://graffpunks.live/",
    "https://graffitikings.co.uk/",
    "https://gkniftyheads.com/",
    "https://medium.com/@GKniftyHEADS",
    "https://medium.com/@graffpunksuk",
    "https://medium.com/@GRAFFITIKINGS",
    "https://medium.com/@games4punks",
    "https://medium.com/@HODLWARRIORS",
    "https://neftyblocks.com/collection/gkstonedboys",
    "https://neftyblocks.com/collection/noballgamess",
    "https://nfthive.io/collection/noballgamess",
    "https://dappradar.com/nft-collection/crypto-moonboys",
    "https://www.youtube.com/@GKniftyHEADS",
    # Charlie Buster & Treef Project
    "https://medium.com/@iamcharliebuster",
    "https://medium.com/@treefproject",
    "https://substack.com/@treefproject/posts",
    "https://substack.com/@noballgames/posts",
    # Real-people & extra canon
    "https://medium.com/@boneidolink",
    "https://deliciousagainpeter.com/",
    "https://www.reddit.com/user/graffpunks/",
]

# Crypto and graffiti news sites — crawled by get_news_and_weather() for
# topical references in awake lore posts (NR-1 rule).
NEWS_LINKS = [
    "https://cointelegraph.com/",
    "https://decrypt.co/",
    "https://beincrypto.com/",
    "https://theblock.co/",
    "https://bitcoinmagazine.com/",
    "https://cryptoslate.com/",
    "https://streetartnews.net/",
    "https://www.graffitistreet.com/news/",
    "https://arrestedmotion.com/",
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
    "teeth gritted in defiance",
    "soft nostalgic half-smile",
    "manic wide grin with raised eyebrows",
    "tears streaming but still smiling",
    "hollow exhausted thousand-stare after a long night",
]


# ── Infinite Variation Entropy System (IVES) axis pools ──────────────────────
# Each axis is rolled independently every post (IVES-1).
# The resulting combination is injected into the lore generation prompt as
# VARIATION_CONTEXT to maximise uniqueness across 5+ years of output.

IVES_AXES = {
    "A_perspective": [
        "First-person artist mind-log",
        "Third-person omniscient narrator",
        "Character inner monologue",
        "Overheard conversation fragment",
        "Chain Archive log entry (Elder Codex-7 voice)",
        "Dream journal entry",
        "Field report from a HODL X Warrior",
        "Letter from Lady-INK",
        "Breaking news from the GraffPunks Network",
        "Prophecy fragment from the Sacred Chain Ontology",
    ],
    "B_location": [
        "Artist's home studio",
        "Leake Street Tunnel",
        "City Block Topia central plaza",
        "Blocktopia outer walls",
        "Alien Backend hyper-space",
        "Hardfork Games arena",
        "London rooftop",
        "Night fishing spot",
        "Van touring route",
        "Festival / rave floor",
        "Underwater Blocktopia sector",
        "Space Programme launch zone",
        "OG Bitcoin Kids exile road",
        "Wannabe Moonboys' border camp",
        "GraffPunks Network HQ",
    ],
    "C_time_of_day": [
        "3am dark",
        "Dawn breaking",
        "Mid-morning",
        "Noon blaze",
        "Afternoon slant light",
        "Golden hour",
        "Dusk",
        "Midnight",
    ],
    "C_weather": [
        "Clear and sharp",
        "Light drizzle",
        "Heavy rain",
        "Thick fog",
        "Snow settling",
        "Heatwave shimmer",
        "Thunderstorm rolling in",
        "Overcast flat light",
        "Rainbow after storm",
        "Aurora / Northern Lights",
    ],
    "D_emotional_register": [
        "Triumph",
        "Loss and grief",
        "Confusion and searching",
        "Rage",
        "Peace and stillness",
        "Fear",
        "Euphoria",
        "Nostalgia",
        "Dark humour",
        "Wonder and awe",
        "Paranoia",
        "Love",
        "Bittersweet",
        "Defiance",
        "Exhausted but proud",
    ],
    "E_lore_theme": [
        "New character reveal",
        "Arc climax",
        "Arc setup — planting seeds",
        "Aftermath of battle",
        "Daily ritual or routine",
        "Reunion",
        "Betrayal hint",
        "Prophecy fulfillment",
        "Discovery of a new part of Blocktopia",
        "Real-world artist moment mirrored in lore",
        "Character growth milestone",
        "Faction politics shift",
        "Dream-bleeds-into-reality moment",
        "Hidden backstory fragment",
        "Time-jump forward or backward",
        "New bonnet or art reveal",
        "Hardfork Games moment",
        "OG Bitcoin Kids regret arc",
        "Escape attempt",
        "Return to Blocktopia",
    ],
    "F_narrative_structure": [
        "Opens in action, ends in reflection",
        "Opens calm, ends with revelation",
        "One punchy log line then expanded image description",
        "Dialogue-heavy scene",
        "Poetic or fragmented mind-log",
        "Technical chain archive format",
        "News flash style",
        "Letter or message format",
        "Stream of consciousness",
        "Two-act: daytime moment then night consequence",
    ],
    "H_art_style": [
        "Standard GraffPunks full colour",
        "Black charcoal pencil sketch",
        "Neon on black — nightlife scene",
        "Bleached overexposed midday heat",
        "Watercolour wash",
        "Blueprint schematic style — Alien Backend",
        "Grainy analogue film",
        "Ultra-vivid graffiti spray aesthetic",
        "Monochrome plus single accent colour",
        "Glitch-art digital distortion",
    ],
    "I_scene_intensity": [
        "Quiet and intimate",
        "Action and kinetic",
        "Epic and cinematic",
        "Comedic and absurdist",
        "Tense and suspenseful",
        "Mysterious and cryptic",
        "Surreal and dreamlike",
        "Documentary and real-feeling",
        "Mythic and legendary scale",
    ],
    "J_wild_card": [
        "A new GraffPunks character is implied but not named — plant a seed",
        "The lore references real-world news from the last 24 hours",
        "A Hardfork Games secret rule is hinted at",
        "Lady-INK leaves a coded message somewhere in the scene",
        "The Alien Backend glitches and leaks a future event",
        "The artist finds an unexpected GraffPunks connection in real life",
        "An OG Bitcoin Kid is spotted in the real world",
        "A forgotten character from lore-history gets a callback",
        "The bonnet of a character changes in a subtle 4% way — first time it is noticed",
        "A completely new location in Blocktopia is discovered and named for the first time",
        None,  # 'None' = skip wild card this post (roughly 1 in 11 posts)
    ],
}


def build_variation_context() -> str:
    """
    Roll all IVES axes independently and return the VARIATION_CONTEXT block
    to inject into the lore generation prompt (IVES-1).
    """
    rolls = {axis: random.choice(options) for axis, options in IVES_AXES.items()}
    lines = [
        "VARIATION_CONTEXT (IVES — roll independently for this post):",
        f"  Perspective    : {rolls['A_perspective']}",
        f"  Location       : {rolls['B_location']}",
        f"  Time of day    : {rolls['C_time_of_day']}",
        f"  Weather        : {rolls['C_weather']}",
        f"  Emotion        : {rolls['D_emotional_register']}",
        f"  Lore theme     : {rolls['E_lore_theme']}",
        f"  Narrative form : {rolls['F_narrative_structure']}",
        f"  Art style      : {rolls['H_art_style']}",
        f"  Scene intensity: {rolls['I_scene_intensity']}",
    ]
    if rolls["J_wild_card"] is not None:
        lines.append(f"  Wild card      : {rolls['J_wild_card']}")
    lines += [
        "",
        "These are SUGGESTIONS that tune the creative output — they must never override",
        "active arc continuity, RCG conflict rules, or uniform/bonnet fidelity rules.",
        "If any axis would cause a continuity break, adjust only that axis and note why.",
    ]
    return "\n".join(lines)




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
    Head + bonnet as one unit, 96% shape fidelity, random face expression.
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
        f"96% shape fidelity to reference — 4% creative zone for minor surface details only. "
        f"Clothing: main faction uniform unless uniform exception trigger active (see UF rules). "
        f"Bonnet 3D elements (all locked at 96%): name primary shape + central feature + side features + upper features + material + hair/ear integration explicitly in prompt. "
        f"Colours, textures, background, and scene elements may vary freely within the 4% zone. "
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
    """
    Crawl the primary official art/content sources and return a combined
    art-reference + new-content string for injection into the lore prompt.

    Priority sites (crawled first for the best signal):
      1. GraffPunks Substack (primary art and lore source)
      2. GraffPunks Live
      3. GKniftyHEADS (NFT collection)
      4. Graffiti Kings
    Remaining OFFICIAL_ART_LINKS are used for dedicated-page searches only.
    """
    PRIORITY_CRAWL_URLS = [
        "https://substack.com/@graffpunks/posts",
        "https://graffpunks.live/",
        "https://gkniftyheads.com/",
        "https://graffitikings.co.uk/",
    ]

    all_images: list[str] = []
    all_snippets: list[str] = []
    sources_hit: list[str] = []

    for url in PRIORITY_CRAWL_URLS:
        try:
            r = requests.get(url, timeout=8)
            soup = BeautifulSoup(r.text, "html.parser")
            images = [img["src"] for img in soup.find_all("img") if img.get("src") and not img["src"].startswith("data:")]
            snippets = [p.text.strip() for p in soup.find_all("p") if len(p.text.strip()) > 20]
            if images or snippets:
                all_images.extend(images[:3])
                all_snippets.extend(snippets[:2])
                sources_hit.append(url)
        except Exception:
            continue

    if not all_images and not all_snippets:
        return "Official site crawl failed — use existing Character Bible and make up consistent GraffPunks style until new official data appears."

    art_reference = (
        "Use exact GraffPunks artwork style for all characters and factions: shapes, uniforms, silhouettes, colours, look. "
        f"Sources checked: {', '.join(sources_hit)}. "
        "Found reference images: " + " ".join(all_images[:6])
        if all_images
        else f"Fallback to GraffPunks style from {', '.join(sources_hit)}."
    )
    new_content = (
        "New official content: " + " | ".join(all_snippets[:4])
        if all_snippets
        else "No new textual content found — continue consistent lore until official data conflicts."
    )
    return art_reference + "\n" + new_content


def get_news_and_weather():
    """
    Fetch London weather and try to pull a headline from crypto/graffiti news
    sites (NEWS_LINKS) for topical references in awake lore posts (NR-1 rule).
    """
    weather = "unknown"
    try:
        weather = requests.get("https://wttr.in/London?format=%C+%t", timeout=10).text.strip()
    except Exception:
        pass

    news_headlines: list[str] = []
    for url in NEWS_LINKS:
        if len(news_headlines) >= 3:
            break
        try:
            r = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(r.text, "html.parser")
            # Grab the first meaningful headline/paragraph from each news site
            for tag in soup.find_all(["h1", "h2", "h3"]):
                headline = tag.get_text(strip=True)
                if len(headline) > 20:
                    news_headlines.append(headline[:120])
                    break
        except Exception:
            continue

    news_str = (
        "Latest headlines: " + " | ".join(news_headlines)
        if news_headlines
        else "Latest crypto/graffiti news from the last 2 hours."
    )
    return f"Weather: {weather} | {news_str}"


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
    variation_context = build_variation_context()

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

    {variation_context}

    ART CREATION RULE (mandatory for BOTH image prompts in this post):
    Every image prompt MUST start with this exact prefix, then add the full scene description:
    "{art_prefix}"
    For each character featured, the head + bonnet must be treated as one inseparable unit.
    Use the dedicated page reference if one was found during this run's crawl, otherwise use
    Layer 1 + Layer 2 base templates. Add a random face expression matching the lore mood.
    96% shape fidelity for bonnet + all 3D elements. 4% creative zone for minor details only.
    Clothing: ALWAYS the character's main faction uniform unless a UF exception trigger is active.
    Colours and scene details may vary freely within the 4% zone.

    RULE CONFLICT GATE (run before generating):
    1. CHECK ACCURACY: does any rule below conflict with the latest crawled data? If yes, update first.
    2. CHECK CONTINUITY: does any axis in VARIATION_CONTEXT contradict the last 7 days of lore history? Adjust only that axis.
    3. CHECK FLOW: will this post feel organic and alive, or mechanical? Prioritise narrative voice.
    4. CHECK UNIFORMS: verify UF-0 — if no exception trigger is present in the lore, use main uniform.
    5. CHECK BONNET: verify BF-1/BF-2 — 96% fidelity lock, 4% creative zone only.

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


async def post_to_telegram_async(text: str) -> None:
    """Send a message to all registered channel chat IDs."""
    async with telegram.Bot(token=TELEGRAM_BOT_TOKEN) as tg:
        for chat_id in CHANNEL_CHAT_IDS:
            try:
                await tg.send_message(chat_id=chat_id.strip(), text=text)
                await asyncio.sleep(2)
            except Exception as exc:
                print(f"  ⚠️  send_message failed for {chat_id}: {exc}")


def post_to_telegram(text: str) -> None:
    """Synchronous wrapper around the async Telegram send."""
    asyncio.run(post_to_telegram_async(text))


# ── Telegram command processing ───────────────────────────────────────────────

async def register_bot_commands_async() -> None:
    """Register the command list with BotFather so it appears in the / menu."""
    async with telegram.Bot(token=TELEGRAM_BOT_TOKEN) as tg:
        await tg.set_my_commands(TELEGRAM_COMMANDS)


def register_bot_commands() -> None:
    asyncio.run(register_bot_commands_async())


def build_lore_command_reply() -> str:
    """Return the last lore post from lore-history.md (most recent entry)."""
    if not os.path.exists(LORE_HISTORY_FILE):
        return "No lore posts yet — the saga starts on the next run. 🌙"
    with open(LORE_HISTORY_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    # Find the last --- NEW POSTS block
    blocks = content.split("--- NEW POSTS")
    if len(blocks) < 2:
        return "No lore posts yet — the saga starts on the next run. 🌙"
    last_block = "--- NEW POSTS" + blocks[-1]
    # Return a trimmed excerpt (Telegram 4096 char limit)
    excerpt = last_block.strip()[:3800]
    return excerpt + "\n\n[…use /expand to continue the lore]"


def build_status_reply() -> str:
    """Return current brain status: fame slot, mode, last post time."""
    now = datetime.now(timezone.utc)
    slot = get_fame_cycle_slot(now)
    mode = get_post_mode(now)
    slot_line = slot.splitlines()[0] if slot else "Unknown slot"
    mode_line = mode.splitlines()[0] if mode else "Unknown mode"
    return (
        f"🤖 *GK BRAIN STATUS*\n\n"
        f"🕐 Time: {now.strftime('%Y-%m-%d %H:%M UTC')}\n"
        f"🎭 Mode: {mode_line}\n"
        f"⭐ Fame: {slot_line}\n\n"
        f"Posts sent every 2 hours. Lore history stored in lore-history.md.\n"
        f"Characters rotate every 6 hours. Art crawls all official links before each post. 🔄"
    )


def build_whosnext_reply() -> str:
    """Return info on the next 6-hour fame slot."""
    now = datetime.now(timezone.utc)
    next_slot_index = (now.hour // 6 + 1) % 4
    next_slot_name = FAME_SLOT_NAMES[next_slot_index]
    hours_until = (6 - (now.hour % 6)) % 6 or 6
    return (
        f"⭐ *NEXT FAME SLOT*\n\n"
        f"Coming up: *{next_slot_name}*\n"
        f"Starting in ~{hours_until} hour(s)\n\n"
        f"The agent selects 1–3 characters who haven't had a recent fame run. "
        f"Check lore-history.md for the full rotation log.\n\n"
        f"Use /lore to read the current fame-slot posts as they go live. 🌙"
    )


def build_about_reply(character_name: str) -> str:
    """Ask Grok for a quick character bio using the full canon."""
    if not character_name.strip():
        return (
            "Please tell me which character! Usage: /about LadyINK\n\n"
            "Type /characters for the full list."
        )
    prompt = (
        f"{BRAIN_RULES}\n{CHARACTER_BIBLE}\n{MASTER_CANON}\n\n"
        f"Give a 150-word punchy bio for this character from the GraffPunks / Crypto Moonboys saga: "
        f"'{character_name}'. "
        f"Use the Eternal Codex style. Text only — no images. "
        f"If the character is not in the canon, say so and suggest a similar one."
    )
    try:
        response = grok.chat.completions.create(
            model="grok-4-fast",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return f"Could not fetch bio for '{character_name}' — try again on the next run. 🌙"


def build_expand_reply() -> str:
    """Expand the most recent lore post by generating a short continuation."""
    prompt = (
        f"{BRAIN_RULES}\n{CHARACTER_BIBLE}\n{MASTER_CANON}\n\n"
        f"PREVIOUS LORE (last 4000 chars):\n{LORE_HISTORY[-4000:]}\n\n"
        "A Telegram user has asked to expand the last lore. "
        "Continue the most recent story arc naturally — 200–300 words, "
        "mind-log style, first person, as the artist expanding the saga in real time. "
        "Text only, no images."
    )
    try:
        response = grok.chat.completions.create(
            model="grok-4-fast",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return "Lore expansion failed — try again on the next run. 🌙"


def process_command(command: str, args: str, user_id: str) -> str | None:
    """
    Route a Telegram slash command to its handler and return the reply text.
    Returns None if the command is unknown.
    """
    cmd = command.lower().strip()

    if cmd == "/start":
        return STATIC_COMMAND_RESPONSES["/start"]
    if cmd in ("/help", "/commands"):
        return COMMAND_HELP_TEXT
    if cmd == "/lore":
        return build_lore_command_reply()
    if cmd == "/status":
        return build_status_reply()
    if cmd == "/whosnext":
        return build_whosnext_reply()
    if cmd == "/characters":
        return STATIC_COMMAND_RESPONSES["/characters"]
    if cmd == "/factions":
        return STATIC_COMMAND_RESPONSES["/factions"]
    if cmd == "/hardfork":
        return STATIC_COMMAND_RESPONSES["/hardfork"]
    if cmd == "/links":
        return STATIC_COMMAND_RESPONSES["/links"]
    if cmd == "/artrule":
        return STATIC_COMMAND_RESPONSES["/artrule"]
    if cmd == "/expand":
        return build_expand_reply()
    if cmd == "/about":
        return build_about_reply(args)

    return None  # unknown command — fall through to keyword handling


async def process_incoming_updates_async() -> None:
    """
    Fetch all Telegram updates received since the last run, process commands and
    user messages, and persist the new update offset so nothing is replayed.
    """
    offset = bot_state.get("last_update_id", 0) + 1

    async with telegram.Bot(token=TELEGRAM_BOT_TOKEN) as tg:
        try:
            updates = await tg.get_updates(offset=offset, timeout=5)
        except Exception as exc:
            print(f"  ⚠️  get_updates failed: {exc}")
            return

        for update in updates:
            bot_state["last_update_id"] = update.update_id

            msg = update.message
            if not msg or not msg.text:
                continue

            chat_id = str(msg.chat_id)
            user_id = str(msg.from_user.id) if msg.from_user else chat_id
            text = msg.text.strip()

            reply = None

            # ── Slash command handling ──────────────────────────────────────
            if text.startswith("/"):
                parts = text.split(maxsplit=1)
                # Strip @BotUsername suffix if present (e.g. /help@GKBrainBot)
                raw_cmd = parts[0].split("@")[0]
                args = parts[1] if len(parts) > 1 else ""
                reply = process_command(raw_cmd, args, user_id)
                if reply is None:
                    # Unknown command — treat as normal message
                    reply = handle_user_message(user_id, text)

            # ── Regular message handling ────────────────────────────────────
            else:
                reply = handle_user_message(user_id, text)

            if reply:
                try:
                    await tg.send_message(chat_id=chat_id, text=reply)
                    await asyncio.sleep(1)
                except Exception as exc:
                    print(f"  ⚠️  reply failed for {chat_id}: {exc}")

    # Persist updated offset
    with open(BOT_STATE_FILE, "w") as f:
        json.dump(bot_state, f)


def process_incoming_updates() -> None:
    asyncio.run(process_incoming_updates_async())


async def main_async() -> None:
    print("GK BRAIN running at", datetime.now(timezone.utc))

    # 1. Register commands with BotFather (so / menu is always up-to-date)
    try:
        async with telegram.Bot(token=TELEGRAM_BOT_TOKEN) as tg:
            await tg.set_my_commands(TELEGRAM_COMMANDS)
        print("✅ Bot commands registered")
    except Exception as exc:
        print(f"  ⚠️  Command registration failed: {exc}")

    # 2. Process any pending user messages / commands since the last run
    await process_incoming_updates_async()
    print("✅ Incoming updates processed")

    # 3. Generate and post the 2-hour lore pair
    post1, post2 = generate_lore_pair()

    async with telegram.Bot(token=TELEGRAM_BOT_TOKEN) as tg:
        for chat_id in CHANNEL_CHAT_IDS:
            try:
                await tg.send_message(chat_id=chat_id.strip(), text=post1)
            except Exception as exc:
                print(f"  ⚠️  Post 1 failed for {chat_id}: {exc}")
    print("✅ Post 1 sent")

    await asyncio.sleep(3)

    async with telegram.Bot(token=TELEGRAM_BOT_TOKEN) as tg:
        for chat_id in CHANNEL_CHAT_IDS:
            try:
                await tg.send_message(chat_id=chat_id.strip(), text=post2)
            except Exception as exc:
                print(f"  ⚠️  Post 2 failed for {chat_id}: {exc}")
    print("✅ Post 2 sent")

    # 4. Persist trackers
    with open(REPLIED_FILE, "w") as f:
        json.dump(reply_tracker, f)
    with open(BOT_STATE_FILE, "w") as f:
        json.dump(bot_state, f)


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
