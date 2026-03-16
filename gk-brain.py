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

detect_updates = _update_detector.detect_updates
add_to_queue = _wiki_updater.add_to_queue
run_wiki_updates = _wiki_updater.run_wiki_updates
persist_queue_updates = _wiki_updater.persist_queue_updates

# ── 55-System Godlike Module Loader ───────────────────────────────────────

def _safe_load(name: str, filepath: str):
    """Load a module, returning None on failure (non-fatal)."""
    try:
        return _load_module(name, filepath)
    except Exception as exc:
        print(f"[godlike] Could not load {filepath}: {exc}")
        return None

# Tier 1 — Data Layer
_data_validator        = _safe_load("data_validator",         "data-validator.py")
_causal_inference      = _safe_load("causal_inference",       "causal-inference-engine.py")
_knowledge_graph       = _safe_load("knowledge_graph",        "knowledge-graph-builder.py")
_multi_source_fusion   = _safe_load("multi_source_fusion",    "multi-source-fusion.py")
_world_state_sim       = _safe_load("world_state_sim",        "world-state-simulator.py")
_anomaly_detector      = _safe_load("anomaly_detector",       "anomaly-detector.py")
_temporal_alignment    = _safe_load("temporal_alignment",     "temporal-alignment-engine.py")
_source_attribution    = _safe_load("source_attribution",     "source-attribution-system.py")
_priority_queue        = _safe_load("priority_queue",         "update-priority-queue.py")
_deduplication         = _safe_load("deduplication",          "deduplication-engine.py")

# Tier 2 — Planning Layer
_hierarchical_planning = _safe_load("hierarchical_planning",  "hierarchical-planning-system.py")
_adaptive_priority     = _safe_load("adaptive_priority",      "adaptive-data-prioritization.py")
_theory_of_mind        = _safe_load("theory_of_mind",         "theory-of-mind-engine.py")
_narrative_constraints = _safe_load("narrative_constraints",  "narrative-planning-with-constraints.py")
_symbolic_reasoning    = _safe_load("symbolic_reasoning",     "symbolic-reasoning-engine.py")
_rl_optimizer          = _safe_load("rl_optimizer",           "reinforcement-learning-optimizer.py")
_transfer_learning     = _safe_load("transfer_learning",      "transfer-learning-module.py")
_uncertainty_quant     = _safe_load("uncertainty_quant",      "uncertainty-quantification.py")

# Tier 3 — Character Layer
_character_memory      = _safe_load("character_memory",       "character-memory-bank.py")
_emotional_intel       = _safe_load("emotional_intel",        "emotional-intelligence-system.py")
_skill_progression     = _safe_load("skill_progression",      "skill-progression-tracker.py")
_relationship_model    = _safe_load("relationship_model",     "relationship-modeling-system.py")
_arc_tracker           = _safe_load("arc_tracker",            "narrative-arc-tracker.py")
_narrative_interp      = _safe_load("narrative_interp",       "narrative-interpolation-system.py")
_personality_amp       = _safe_load("personality_amp",        "character-personality-amplifier.py")
_world_bible           = _safe_load("world_bible",            "generative-world-bible.py")
_arc_planner           = _safe_load("arc_planner",            "character-arc-planner.py")
_memory_references     = _safe_load("memory_references",      "lore-memory-reference-system.py")

# Tier 4 — Generation Layer
_emergent_stories      = _safe_load("emergent_stories",       "emergent-storytelling-system.py")
_lore_fusion           = _safe_load("lore_fusion",            "lore-fusion-engine.py")
_dialogue_gen          = _safe_load("dialogue_gen",           "dialogue-generator.py")
_sentiment_analyzer    = _safe_load("sentiment_analyzer",     "sentiment-analyzer.py")
_style_transfer        = _safe_load("style_transfer",         "style-transfer-engine.py")
_tension_curve         = _safe_load("tension_curve",          "narrative-tension-curve.py")
_meta_narrative        = _safe_load("meta_narrative",         "meta-narrative-layer.py")
_narrative_interp_eng  = _safe_load("narrative_interp_eng",   "narrative-interpolation-engine.py")
_causal_weaving        = _safe_load("causal_weaving",         "causal-narrative-weaving.py")
_universe_engine       = _safe_load("universe_engine",        "cross-media-universe-engine.py")

# Tier 5 — Quality Assurance
_quality_gate          = _safe_load("quality_gate",           "quality-gate.py")
_contradiction_check   = _safe_load("contradiction_check",    "contradiction-checker.py")
_ethical_filter        = _safe_load("ethical_filter",         "ethical-filter.py")
_source_verify         = _safe_load("source_verify",          "source-verification-system.py")
_coherence_validator   = _safe_load("coherence_validator",    "narrative-coherence-validator.py")
_plagiarism_detect     = _safe_load("plagiarism_detect",      "plagiarism-detector.py")
_consistency_proof     = _safe_load("consistency_proof",      "consistency-proof-engine.py")

# Tier 6 — Analytics
_perf_metrics          = _safe_load("perf_metrics",           "performance-metrics-system.py")
_learning_loop         = _safe_load("learning_loop",          "learning-feedback-loop.py")
_recursive_discovery   = _safe_load("recursive_discovery",    "recursive-update-discovery.py")
_trend_engine          = _safe_load("trend_engine",           "predictive-trend-engine.py")
_comparative_analysis  = _safe_load("comparative_analysis",   "comparative-analysis-system.py")
_debug_report          = _safe_load("debug_report",           "debug-report-generator.py")

# Tier 7 — Orchestration
_platform_orchestrator = _safe_load("platform_orchestrator",  "multi-platform-orchestrator.py")
_health_monitor        = _safe_load("health_monitor",         "system-health-monitor.py")

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


def _telegram_post(method: str, **params) -> dict:
    """Make a Telegram Bot API call using requests."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/{method}"
    resp = requests.post(url, json=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram API error: {data.get('description', data)}")
    return data


def _telegram_send_photo(chat_id: str, photo: bytes) -> dict:
    """Send a photo (raw bytes) to Telegram using multipart form data."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    resp = requests.post(
        url,
        data={"chat_id": chat_id},
        files={"photo": ("image.jpg", photo, "image/jpeg")},
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram API error: {data.get('description', data)}")
    return data


def _send_telegram_alert(message: str) -> None:
    """Send a plain text Telegram message to all channels (best effort)."""
    if not TELEGRAM_BOT_TOKEN:
        print(f"[ALERT] {message}")
        return
    for chat_id in CHANNEL_CHAT_IDS:
        try:
            _telegram_post("sendMessage", chat_id=chat_id, text=message)
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
    now = datetime.datetime.now(datetime.UTC)
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
    now = datetime.datetime.now(datetime.UTC)
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
    now = datetime.datetime.now(datetime.UTC)
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
    if not TELEGRAM_BOT_TOKEN or not CHANNEL_CHAT_IDS:
        print("[telegram] Token or chat IDs not configured -- printing to stdout.")
        print("=== POST 1 ===")
        print(lore1)
        print("=== POST 2 ===")
        print(lore2)
        return

    # Telegram messages have a 4096-character limit
    MAX_MSG_LEN = 4096

    for chat_id in CHANNEL_CHAT_IDS:
        try:
            # Post 1
            text1 = lore1[:MAX_MSG_LEN]
            if len(lore1) > MAX_MSG_LEN:
                print(f"[telegram] Post 1 truncated from {len(lore1)} to {MAX_MSG_LEN} chars.")
            _telegram_post("sendMessage", chat_id=chat_id, text=text1)
            if image1:
                _telegram_send_photo(chat_id, image1)

            time.sleep(2)

            # Post 2
            text2 = lore2[:MAX_MSG_LEN]
            if len(lore2) > MAX_MSG_LEN:
                print(f"[telegram] Post 2 truncated from {len(lore2)} to {MAX_MSG_LEN} chars.")
            _telegram_post("sendMessage", chat_id=chat_id, text=text2)
            if image2:
                _telegram_send_photo(chat_id, image2)

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
# Godlike: orchestrate all 55 systems
# ---------------------------------------------------------------------------

def _safe_call(mod, func_name: str, *args, **kwargs):
    """Call mod.func_name safely; return None on any error."""
    if mod is None:
        return None
    fn = getattr(mod, func_name, None)
    if fn is None:
        return None
    try:
        return fn(*args, **kwargs)
    except Exception as exc:
        print(f"[godlike] {func_name} failed: {exc}")
        return None


def _run_godlike_systems(updates: list, rule_ctx: dict, lore_history: str) -> str:
    """
    Run all 55 systems in tier order and return a combined context string
    that enriches the main lore-generation prompt.
    """
    print("[godlike] Running all 55 systems...")
    ctx_parts = []

    # ── Tier 1: Data Layer ──────────────────────────────────────────────────
    validated   = _safe_call(_data_validator,      "validate_updates",    updates)         or updates
    causal_ctx  = _safe_call(_causal_inference,    "build_causal_context", validated, rule_ctx) or ""
    _safe_call(_knowledge_graph, "update_knowledge_graph", validated, lore_history)
    fused       = _safe_call(_multi_source_fusion, "fuse_updates",        validated)       or validated
    world_state = _safe_call(_world_state_sim,     "get_world_state",     rule_ctx)        or {}
    anomaly_res = _safe_call(_anomaly_detector,    "detect_anomalies",    fused)           or {"clean_updates": fused}
    clean_upd   = anomaly_res.get("clean_updates", fused)
    clean_upd   = _safe_call(_temporal_alignment,  "align_timestamps",    clean_upd)       or clean_upd
    clean_upd   = _safe_call(_source_attribution,  "attribute_updates",   clean_upd)       or clean_upd
    clean_upd   = _safe_call(_priority_queue,      "prioritize_updates",  clean_upd, rule_ctx) or clean_upd
    clean_upd   = _safe_call(_deduplication,       "deduplicate_updates", clean_upd)       or clean_upd

    if causal_ctx:
        ctx_parts.append(f"CAUSAL CONTEXT:\n{causal_ctx}")
    if world_state:
        ctx_parts.append(
            f"WORLD STATE: fishing_season={world_state.get('fishing_season')}, "
            f"nft_trend={world_state.get('nft_market_trend')}, "
            f"crypto={world_state.get('crypto_sentiment')}"
        )

    # ── Tier 2: Planning Layer ───────────────────────────────────────────────
    narrative_plan = _safe_call(_hierarchical_planning, "get_narrative_plan",  rule_ctx, lore_history) or {}
    adapt_weights  = _safe_call(_adaptive_priority,     "get_adaptive_weights", rule_ctx)              or {}
    social_ctx     = _safe_call(_theory_of_mind,        "get_social_context",  rule_ctx, lore_history) or ""
    _safe_call(_narrative_constraints, "apply_constraints", {"rule_ctx": rule_ctx})
    _safe_call(_symbolic_reasoning,    "validate_narrative_logic", "", {})
    strategy_hint  = _safe_call(_rl_optimizer,    "get_strategy_hints",  rule_ctx) or ""
    transfer_hint  = _safe_call(_transfer_learning, "get_transfer_hints")           or ""
    _safe_call(_uncertainty_quant, "quantify_uncertainty", clean_upd)

    if narrative_plan:
        ctx_parts.append(
            f"NARRATIVE PLAN: immediate={narrative_plan.get('immediate_goal','')}, "
            f"weekly={narrative_plan.get('weekly_theme','')}"
        )
    if social_ctx:
        ctx_parts.append(f"SOCIAL CONTEXT:\n{social_ctx}")
    if strategy_hint:
        ctx_parts.append(f"STRATEGY: {strategy_hint}")
    if transfer_hint:
        ctx_parts.append(f"LEARNED PATTERNS: {transfer_hint}")

    # ── Tier 3: Character Layer ──────────────────────────────────────────────
    char_memory    = _safe_call(_character_memory,   "get_character_memory")                          or ""
    emotional_st   = _safe_call(_emotional_intel,    "get_emotional_state", rule_ctx, lore_history)   or {}
    skill_levels   = _safe_call(_skill_progression,  "get_skill_levels")                              or {}
    relationships  = _safe_call(_relationship_model, "get_relationship_context")                      or ""
    active_arcs    = _safe_call(_arc_tracker,        "get_active_arcs")                               or []
    _safe_call(_narrative_interp, "interpolate_gap", "", "", rule_ctx)
    personality_h  = _safe_call(_personality_amp,    "get_personality_hints", rule_ctx, emotional_st) or ""
    _safe_call(_world_bible,      "update_world_bible", lore_history)
    arc_direction  = _safe_call(_arc_planner,        "get_arc_direction",  rule_ctx, active_arcs)     or ""
    mem_refs       = _safe_call(_memory_references,  "get_memory_references", rule_ctx, lore_history) or ""

    if char_memory:
        ctx_parts.append(f"CHARACTER MEMORY:\n{char_memory}")
    if emotional_st:
        ctx_parts.append(
            f"EMOTIONAL STATE: mood={emotional_st.get('mood','')}, "
            f"confidence={emotional_st.get('confidence',5)}/10"
        )
    if skill_levels:
        ctx_parts.append(
            f"SKILLS: fishing={skill_levels.get('fishing',1)}, "
            f"art={skill_levels.get('art',1)}, dj={skill_levels.get('dj',1)}"
        )
    if relationships:
        ctx_parts.append(f"RELATIONSHIPS:\n{relationships}")
    if arc_direction:
        ctx_parts.append(f"ARC DIRECTION: {arc_direction}")
    if mem_refs:
        ctx_parts.append(f"MEMORY REFERENCES:\n{mem_refs}")
    if personality_h:
        ctx_parts.append(f"PERSONALITY TONE: {personality_h}")

    # ── Tier 4: Generation Layer ─────────────────────────────────────────────
    emergent_hooks = _safe_call(_emergent_stories, "find_emergent_hooks", clean_upd, rule_ctx) or []
    lore_fuse_ctx  = _safe_call(_lore_fusion,      "fuse_lore_context",   clean_upd, rule_ctx, emergent_hooks) or ""
    npc_dialogue   = _safe_call(_dialogue_gen,     "get_npc_dialogue_context", rule_ctx, {})  or ""
    sentiment_dir  = _safe_call(_sentiment_analyzer, "get_sentiment_direction", [lore_history]) or ""
    style_hint     = _safe_call(_style_transfer,   "get_style_hints",     "telegram")           or ""
    tension_hint   = _safe_call(_tension_curve,    "get_tension_hint",    rule_ctx, {})         or ""
    meta_hint      = _safe_call(_meta_narrative,   "get_meta_hints",      rule_ctx, emotional_st) or ""
    gap_filler     = _safe_call(_narrative_interp_eng, "get_gap_filler",  "", "")               or ""
    causal_narr    = _safe_call(_causal_weaving,   "get_causal_narrative_hints", clean_upd, rule_ctx, causal_ctx) or ""
    universe_hint  = _safe_call(_universe_engine,  "get_universe_hints",  rule_ctx, active_arcs) or ""

    if lore_fuse_ctx:
        ctx_parts.append(f"LORE FUSION:\n{lore_fuse_ctx}")
    if npc_dialogue:
        ctx_parts.append(f"NPC CONTEXT:\n{npc_dialogue}")
    if sentiment_dir:
        ctx_parts.append(f"SENTIMENT DIRECTION: {sentiment_dir}")
    if tension_hint:
        ctx_parts.append(f"TENSION: {tension_hint}")
    if causal_narr:
        ctx_parts.append(f"CAUSALITY HINTS:\n{causal_narr}")
    if meta_hint:
        ctx_parts.append(f"META: {meta_hint}")
    if universe_hint:
        ctx_parts.append(f"UNIVERSE: {universe_hint}")

    # ── Tier 5: QA (post-generation checks run separately after generation) ──
    # Tier 5 checks are applied in _run_godlike_qa below.

    # ── Tier 6: Analytics ───────────────────────────────────────────────────
    learning_hint = _safe_call(_learning_loop,        "get_learning_hints", rule_ctx)  or ""
    trend_pred    = _safe_call(_trend_engine,         "get_trend_predictions", rule_ctx) or ""
    comp_insights = _safe_call(_comparative_analysis, "get_performance_insights")       or ""
    _safe_call(_recursive_discovery, "discover_meta_updates", lore_history)

    if learning_hint:
        ctx_parts.append(f"LEARNING HINTS: {learning_hint}")
    if trend_pred:
        ctx_parts.append(f"TREND PREDICTIONS: {trend_pred}")
    if comp_insights:
        ctx_parts.append(f"PERFORMANCE INSIGHTS: {comp_insights}")

    # ── Tier 7: Integration ──────────────────────────────────────────────────
    _safe_call(_health_monitor, "run_health_check", [])

    print(f"[godlike] All 55 systems ran. Context parts: {len(ctx_parts)}")
    return "\n\n".join(ctx_parts)


def _run_godlike_qa(lore1: str, lore2: str, updates: list, rule_ctx: dict, lore_history: str) -> tuple:
    """
    Run Tier 5 QA checks on generated lore. Returns (lore1, lore2) — potentially
    lightly filtered — and prints any issues found.
    """
    for label, lore in [("Post 1", lore1), ("Post 2", lore2)]:
        quality = _safe_call(_quality_gate,        "check_quality",        lore, updates) or {}
        contra  = _safe_call(_contradiction_check, "check_contradictions", lore, lore_history, rule_ctx) or {}
        ethical = _safe_call(_ethical_filter,      "filter_content",       lore) or {}
        coheren = _safe_call(_coherence_validator, "validate_coherence",   lore, rule_ctx) or {}
        plagiar = _safe_call(_plagiarism_detect,   "check_originality",    lore, updates) or {}
        consist = _safe_call(_consistency_proof,   "prove_consistency",    lore, {}) or {}

        issues = []
        if quality.get("issues"):
            issues += quality["issues"]
        if contra.get("contradictions"):
            issues += contra["contradictions"]
        if not ethical.get("safe", True):
            issues += ethical.get("warnings", [])
        if not coheren.get("coherent", True):
            issues += coheren.get("suggestions", [])

        if issues:
            print(f"[godlike-qa] {label} issues: {issues}")
        else:
            score = quality.get("score", "n/a")
            print(f"[godlike-qa] {label} passed QA. Score: {score}/10")

        # Apply ethical filter text replacement if available
        if ethical.get("filtered_text"):
            if label == "Post 1":
                lore1 = ethical["filtered_text"]
            else:
                lore2 = ethical["filtered_text"]

    return lore1, lore2


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------

def main() -> None:
    # Set up stuck-agent timeout (Unix only; GitHub Actions runs on Linux)
    if hasattr(signal, "SIGALRM"):
        signal.signal(signal.SIGALRM, _handle_timeout)
        signal.alarm(MAX_RUN_SECONDS)

    print(f"[gk-brain] Starting at {datetime.datetime.now(datetime.UTC).isoformat()} UTC")

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

    # -- Godlike: Run all 55 systems to enrich the prompt context --
    godlike_context = _run_godlike_systems(unused_updates, rule_ctx, lore_history)

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

    # -- Step 12: Wiki update --
    wiki_pending = [u for u in updates if u.get("wiki_update") and not u.get("wiki_done")]
    if wiki_pending:
        print(f"[gk-brain] Updating wiki ({len(wiki_pending)} entries)...")
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

    print(f"[gk-brain] Cycle complete at {datetime.datetime.now(datetime.UTC).isoformat()} UTC")


if __name__ == "__main__":
    main()