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

import base64
import os
import random
import re
import json
import time
import datetime
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
_user_profile = _load_module("user_profile", "user-profile.py")

# Execution reporter
try:
    _execution_reporter_mod = _load_module("execution_reporter", "execution-reporter.py")
    ExecutionReporter = _execution_reporter_mod.ExecutionReporter
    print("[gk-brain] execution-reporter loaded.")
except Exception as _e:
    print(f"[gk-brain] execution-reporter unavailable ({_e}), reporting disabled.")
    ExecutionReporter = None

# Smart merger — preferred wiki update strategy (falls back to simple updater)
try:
    _wiki_smart_merger = _load_module("wiki_smart_merger", "wiki-smart-merger.py")
    _run_smart_wiki_updates = _wiki_smart_merger.run_smart_wiki_updates
    print("[gk-brain] wiki-smart-merger loaded.")
except Exception as _e:
    print(f"[gk-brain] wiki-smart-merger unavailable ({_e}), will use wiki-updater fallback.")
    _run_smart_wiki_updates = None

# Cross-checker — compares saved data against wiki, filters to missing entries only
try:
    _wiki_cross_checker = _load_module("wiki_cross_checker", "wiki-cross-checker.py")
    _cross_check_and_flag_missing = _wiki_cross_checker.cross_check_and_flag_missing
    print("[gk-brain] wiki-cross-checker loaded.")
except Exception as _e:
    print(f"[gk-brain] wiki-cross-checker unavailable ({_e}), will skip cross-check.")
    _cross_check_and_flag_missing = None

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
GENESIS_LORE_FILE = os.path.join(BASE_DIR, "genesis-lore.md")

# Reference art images (2 boys sets + 2 girls sets)
_ASSETS_DIR = os.path.join(BASE_DIR, "assets", "layers")
_BOY_IMAGES = [
    os.path.join(_ASSETS_DIR, "boys_set_1", "boysimagesetone.png"),
    os.path.join(_ASSETS_DIR, "bonnet_styles_boys_set_2", "boysimagesettwo.png"),
]
_GIRL_IMAGES = [
    os.path.join(_ASSETS_DIR, "females_set_1", "girlsimagesetone.png"),
    os.path.join(_ASSETS_DIR, "bonnet_styles_females_set_2", "girlsimagesettwo.png"),
]

# Maximum lore/image generation attempts before using partial data and continuing
LORE_MAX_FAILS = 50
IMAGE_MAX_FAILS = 50

# Telegram character limits and split configuration.
# MSG1 is a plain-text message (no image); MSG2 is an image caption.
# A 50-char safety buffer is subtracted from each hard limit to avoid
# off-by-one rejections from Telegram's API.
_TG_MSG1_MAX = 4096 - 50   # 4046 — text-only message
_TG_MSG2_MAX = 1024 - 50   # 974  — image caption
# Fraction of the combined lore length assigned to Message 1 (~80 %).
# This biases most narrative content to the text-only message where
# there is more space, leaving a punchy conclusion for the caption.
_TG_MSG1_RATIO = 0.8

# Minimum keyword hits required to classify a lore post as female-focused.
# Two hits reduces false positives from incidental pronoun use.
_FEMALE_DETECTION_THRESHOLD = 2

_FACE_EXPRESSIONS = [
    "surprised with wide eyes",
    "grinning wide",
    "squinting focused",
    "jaw dropped",
    "smirking sly",
    "eyes wide in awe",
    "brow furrowed serious",
    "cackling",
    "winking",
    "thousand yard stare",
    "tongue out cocky",
    "grimacing",
    "gleaming smile",
    "nostril flared furious",
    "dreamy half-closed",
    "teeth gritted",
    "soft nostalgic half-smile",
    "manic wide grin",
    "tears streaming but smiling",
    "hollow exhausted thousand-stare",
]

_OFFICIAL_CRAWL_URLS = [
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

_DEDICATED_PAGE_TOKEN_THRESHOLD = 3


# ---------------------------------------------------------------------------
# Telegram helpers
# ---------------------------------------------------------------------------

def _telegram_post(method: str, **params) -> dict:
    """Make a Telegram Bot API call using requests."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/{method}"
    resp = requests.post(url, json=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram API error: {data.get('description', data)}")
    return data


def _telegram_send_photo(chat_id: str, photo: bytes, caption: str | None = None) -> dict:
    """Send a photo (raw bytes) to Telegram using multipart form data.

    If ``caption`` is provided it is sent as the image caption (max 1024 chars).
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    form_data: dict = {"chat_id": chat_id}
    if caption:
        form_data["caption"] = caption[:1024]
    resp = requests.post(
        url,
        data=form_data,
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


def load_genesis_lore() -> str:
    return _read_file(GENESIS_LORE_FILE, "")


def seed_genesis_lore() -> None:
    """
    On first run, if lore-history.md is empty or missing, populate it from
    genesis-lore.md so all 55 systems start with rich Block Topia lore context
    instead of a cold-start placeholder.
    """
    existing = _read_file(LORE_HISTORY_FILE, "").strip()
    if existing:
        return  # Already has lore; nothing to seed

    genesis = load_genesis_lore().strip()
    if not genesis:
        print("[genesis] genesis-lore.md not found or empty — skipping seed.")
        return

    now = datetime.datetime.now(datetime.UTC)
    header = (
        f"# Block Topia Genesis Lore — Seeded {now.strftime('%Y-%m-%d %H:%M UTC')}\n\n"
        "<!-- This file was auto-seeded from genesis-lore.md on first run. -->\n\n"
    )
    try:
        with open(LORE_HISTORY_FILE, "w", encoding="utf-8") as fh:
            fh.write(header + genesis)
        print("[genesis] Seeded lore-history.md from genesis-lore.md.")
    except OSError as exc:
        print(f"[genesis] Failed to seed lore-history.md: {exc}")


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
    # Row format: | HH:MM–HH:MM | activity description | `(rule1)` `(rule2)` ... | task points |
    block = {
        "weekday": day_name,
        "start_hour": start_hour,
        "end_hour": end_hour,
        "activity": "Random day moment",
        "rules": ["(random)"],
        "task_points": [],
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

        # Match table rows: | 08:00–10:00 | activity | rules | (optional task points) |
        m = re.match(
            r"\|\s*(\d{2}):(\d{2})[–\-](\d{2}):(\d{2})\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|(?:\s*(.*?)\s*\|)?",
            line,
        )
        if not m:
            continue

        row_start = int(m.group(1))
        row_end = int(m.group(3))
        activity_text = m.group(5)
        rules_text = m.group(6)
        task_points_raw = m.group(7) or ""

        if row_start == start_hour and row_end == end_hour:
            rules = re.findall(r"\([a-z0-9_-]+\)", rules_text)
            block["activity"] = activity_text.strip()
            block["rules"] = rules if rules else ["(random)"]
            # Parse task points: split on \| (escaped pipe inside table cell)
            if task_points_raw.strip():
                points = [
                    re.sub(r"\*+", "", p).strip()
                    for p in re.split(r"\s*\\\|\s*", task_points_raw)
                    if p.strip()
                ]
                block["task_points"] = [p for p in points if p]
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
        "task_points": block.get("task_points", []),
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

def _grok_chat(messages: list, model: str = "grok-4-fast") -> str:
    """
    Send a chat completion request to the Grok API and return the response text.

    Retries up to 3 times with exponential backoff on transient errors (5xx,
    connection errors, or timeouts) before raising.  Client errors (4xx) are
    raised immediately without retrying.
    """
    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 4000,
        "temperature": 0.9,
    }
    max_attempts = 3
    last_exc: Exception = RuntimeError("No attempts made")
    for attempt in range(1, max_attempts + 1):
        try:
            resp = requests.post(
                f"{GROK_API_BASE}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60,
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"].strip()
        except requests.exceptions.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else None
            if status is not None and status < 500:
                raise  # 4xx errors are not retryable
            last_exc = exc
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as exc:
            last_exc = exc
        if attempt < max_attempts:
            wait = 2 ** attempt
            print(f"[grok-chat] Attempt {attempt}/{max_attempts} failed ({last_exc}); retrying in {wait}s…")
            time.sleep(wait)
    raise last_exc


def _detect_character_gender(lore_text: str) -> str:
    """
    Inspect lore text and return 'female' when a female character is clearly the
    focus; otherwise return 'male'.

    Female indicators: Lady-INK (or Lady INK), Jodie Zoom, moongirl, crowned royal,
    she/her/hers, queen, sarah, female.  _FEMALE_DETECTION_THRESHOLD or more hits
    → female.  Two hits required to reduce false positives from incidental pronouns.
    """
    female_keywords = [
        "lady ink", "jodie", "zoom 2000",
        "moongirl", "crowned royal",
        " she ", " her ", " hers ", "herself",
        "queen", "sarah", "female",
    ]
    # Pad with spaces so all boundary checks work consistently (including at
    # start and end of string) without requiring regex word-boundary logic.
    lore_padded = " " + lore_text.lower().replace("-", " ") + " "
    hits = sum(1 for kw in female_keywords if kw in lore_padded)
    return "female" if hits >= _FEMALE_DETECTION_THRESHOLD else "male"


def _load_reference_image(gender: str) -> bytes | None:
    """
    Load one of the two reference art files for *gender* ('male' or 'female'),
    chosen at random.  Returns raw PNG bytes or None if the file cannot be read.
    """
    paths = _GIRL_IMAGES if gender == "female" else _BOY_IMAGES
    path = random.choice(paths)
    try:
        with open(path, "rb") as fh:
            data = fh.read()
        print(f"[image-ref] Loaded reference image: {os.path.basename(path)}")
        return data
    except OSError as exc:
        print(f"[image-ref] Could not load reference image {path}: {exc}")
        return None


def _grok_image(prompt: str, reference_image: bytes | None = None) -> bytes | None:
    """
    Generate an image via Grok Imagine image generation API.

    Uses the grok-imagine-image model for text-to-image generation.
    When reference_image is provided, it is base64-encoded and passed as part of the request.

    Returns raw image bytes or None on failure.
    """
    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload: dict = {
        "model": "grok-imagine-image",
        "prompt": prompt,
        "n": 1,
        "response_format": "url",
    }
    if reference_image:
        payload["image"] = base64.b64encode(reference_image).decode("utf-8")
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


def _search_dedicated_art_page(character_tokens: list) -> str:
    """
    AC-1 through AC-4: Search for a dedicated art page for the character.

    1. Check lore-history.md for a cached URL.
    2. Crawl official URLs to find a dedicated page (≥3 token mentions).
    3. Extract up to 6 image URLs from the dedicated page.
    4. Log found URL in lore-history.md under DEDICATED ART PAGES FOUND.

    Returns a reference source string for the image prompt prefix.
    """
    if not character_tokens:
        return (
            "Layer 1 upper body base + Layer 2 GraffPUNKS bonnet shape "
            "(rounded yellow head/torso, exact eagle beak centre, eagle birds each side, "
            "white feathers above eyes, green hair pulled through, yellow leather, ears out sides)"
        )

    try:
        # AC-1: Check lore-history.md cache
        history = _read_file(LORE_HISTORY_FILE, "")
        for token in character_tokens:
            token_lower = token.lower()
            if "DEDICATED ART PAGES FOUND" in history:
                section = history.split("DEDICATED ART PAGES FOUND")[-1]
                for line in section.splitlines():
                    if token_lower in line.lower() and "http" in line:
                        url_match = re.search(r'https?://\S+', line)
                        if url_match:
                            print(f"[art-search] Cache hit for '{token}': {url_match.group()}")
                            return f"Dedicated page: {url_match.group()}"

        # AC-2: Crawl official URLs
        for url in _OFFICIAL_CRAWL_URLS:
            try:
                resp = requests.get(
                    url,
                    timeout=10,
                    headers={"User-Agent": "GKBrainBot/1.0"},
                )
                if resp.status_code != 200:
                    continue
                text = resp.text.lower()
                # AC-3: Count token mentions
                max_hits = max(text.count(t.lower()) for t in character_tokens)
                if max_hits >= _DEDICATED_PAGE_TOKEN_THRESHOLD:
                    # Extract up to 6 image URLs
                    soup = BeautifulSoup(resp.text, "html.parser")
                    img_urls = []
                    for img in soup.find_all("img", src=True):
                        src = img["src"]
                        if src.startswith("http") and any(
                            ext in src.lower() for ext in (".jpg", ".jpeg", ".png", ".webp", ".gif")
                        ):
                            img_urls.append(src)
                        if len(img_urls) >= 6:
                            break

                    # AC-4: Log in lore-history.md
                    log_entry = (
                        f"\n## DEDICATED ART PAGES FOUND\n"
                        f"- {character_tokens[0]}: {url}\n"
                    )
                    existing = _read_file(LORE_HISTORY_FILE, "")
                    if "DEDICATED ART PAGES FOUND" not in existing:
                        try:
                            with open(LORE_HISTORY_FILE, "a", encoding="utf-8") as fh:
                                fh.write(log_entry)
                        except OSError:
                            pass

                    ref_source = f"Dedicated page: {url}"
                    if img_urls:
                        ref_source += " | Reference images: " + ", ".join(img_urls)
                    print(f"[art-search] Dedicated page found for {character_tokens}: {url}")
                    return ref_source
            except Exception as crawl_exc:
                print(f"[art-search] Could not crawl {url}: {crawl_exc}")
                continue
    except Exception as exc:
        print(f"[art-search] Search failed: {exc}")

    # Fallback to Layer 1 + Layer 2
    return (
        "Layer 1 upper body base + Layer 2 GraffPUNKS bonnet shape "
        "(rounded yellow head/torso, exact eagle beak centre, eagle birds each side, "
        "white feathers above eyes, green hair pulled through, yellow leather, ears out sides)"
    )


def build_image_prompt_prefix(lore_text: str, time_theme: str = "day") -> str:
    """
    AC-7, AC-8, AC-9: Build the mandatory image prompt prefix.

    - Detects character tokens from lore text
    - Searches for a dedicated art page (AC-1 through AC-4)
    - Selects a random face expression (AC-8)
    - Always mandates black charcoal pencil on white paper (AC-9)
    - Always requires at least 1 person in the scene

    Returns the full mandatory prefix string.
    """
    try:
        # Detect character tokens from lore text
        character_keywords = [
            "graffpunks", "moonboys", "bitcoin kid", "alfie", "jodie zoom",
            "lady-ink", "lady ink", "queen p-fly", "queen sarah", "null the prophet",
            "hodl warrior", "elder codex", "moongirl", "crowned royal",
        ]
        lore_lower = lore_text.lower()
        found_tokens = [kw for kw in character_keywords if kw in lore_lower]

        # AC-1 through AC-4: Search for dedicated art page
        ref_source = _search_dedicated_art_page(found_tokens)

        # AC-8: Random face expression
        expression = random.choice(_FACE_EXPRESSIONS)

        # Determine gender hint from lore
        gender_hint = _detect_character_gender(lore_text)
        if gender_hint == "female":
            ref_files = (
                "girlsimagesetone.png (female faces/expressions), "
                "girlsimagesettwo.png (female bonnets/accessories)"
            )
        else:
            ref_files = (
                "boysimagesetone.png (male faces/expressions), "
                "boysimagesettwo.png (male bonnets/accessories)"
            )

        prefix = (
            "STRICT BLACK AND WHITE ONLY. BLACK CHARCOAL PENCIL ON WHITE PAPER. ZERO COLOUR. NO EXCEPTIONS. "
            "No colour anywhere in the image. No photorealism. No paint. No shading with colour. Pure black charcoal lines and marks on pure white paper only. "
            f"Use 100% {ref_source}. "
            "Head + bonnet as one inseparable unit. "
            f"Face expression: {expression} (matching lore mood: {time_theme}). "
            "96% shape fidelity to reference — 4% creative zone for minor surface details only. "
            "Clothing: main faction uniform unless exception trigger active. "
            "Bonnet 3D elements (all locked at 96%): eagle beak dead centre, eagle birds each side, "
            "white feathers above eyes, green hair pulled through, yellow leather material, ears visible out the sides. "
            "NO COLOUR ANYWHERE. Black charcoal lines on white paper only. Zero colour in any element including background, clothing, skin, scene. 4% creative zone applies to line weight and texture variation only — never colour. "
            f"Reference character files: {ref_files}. "
            "At least 1 person MUST be featured. "
            "Character must have rounded yellow head/torso with GraffPUNKS bonnet (non-negotiable). "
            "Scene details: "
        )
        return prefix
    except Exception as exc:
        print(f"[image-prefix] Failed to build prefix: {exc}")
        return (
            "STRICT BLACK AND WHITE ONLY. BLACK CHARCOAL PENCIL ON WHITE PAPER. ZERO COLOUR. NO EXCEPTIONS. "
            "No colour anywhere. At least 1 Crypto Moonboys character MUST appear (rounded yellow head/torso shape, GraffPUNKS bonnet). "
            "Scene details: "
        )


def generate_lore_pair(
    rule_ctx: dict,
    updates: list,
    lore_history: str,
    brain_rules: str,
    character_bible: str,
    weather: str,
    substack_context: str,
    godlike_context: str = "",
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
        + (
            "TASK POINTS (execute ALL of these in order — each point is a narrative hook "
            "you must address in the lore):\n"
            + "\n".join(
                f"{i + 1}. {point}"
                for i, point in enumerate(rule_ctx.get("task_points", []))
            )
            + "\n\n"
            if rule_ctx.get("task_points")
            else ""
        )
        + f"RECENT LORE HISTORY (last 7 days -- continue naturally from this):\n"
        f"{lore_history[-3000:]}\n\n"
        f"SUBSTACK CONTENT:\n{substack_context}\n\n"
        + (f"GODLIKE SYSTEM CONTEXT:\n{godlike_context[:2000]}\n\n" if godlike_context else "")
        + (f"UPDATE CONTEXT:\n{update_context}\n\n" if update_context else "")
        + (f"RADIO ALERT TO USE:\n{radio_alert}\n\n" if radio_alert else "")
        + "INSTRUCTIONS:\n"
        "Generate TWO lore posts (Post 1 and Post 2) as a continuous narrative "
        "that will be split across 2 Telegram messages.\n"
        "TELEGRAM SPACE CONSTRAINTS:\n"
        "- Post 1 (text only, NO image): ~3,800 characters maximum — must end at a "
        "  natural paragraph break or cliffhanger so the story continues smoothly.\n"
        "- Post 2 (sent WITH an image as caption): ~900 characters maximum — short, "
        "  punchy conclusion that fits within Telegram's 1,024-char caption limit.\n"
        "Each post must:\n"
        "- Start with: [date] -- [time UTC] -- GraffPunks Network Log Entry #[number]\n"
        "- Be a direct continuation of the previous lore\n"
        "- Follow the calendar activity and time theme exactly\n"
        "- Address ALL task points listed above — weave them into the narrative\n"
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

    # AC-7, AC-8, AC-9: Build mandatory image prompt prefix for each post
    prefix1 = build_image_prompt_prefix(lore1, rule_ctx.get("time_theme", "day"))
    prefix2 = build_image_prompt_prefix(lore2, rule_ctx.get("time_theme", "day"))
    image1 = prefix1 + image1
    image2 = prefix2 + image2

    # AC-13: Append full image prompt to lore2 so users can generate it themselves
    lore2 = (
        lore2
        + "\n\n---\n🎨 IMAGE PROMPT (generate yourself with any AI):\n"
        + image2
    )

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

def _send_photo(chat_id: str, image: bytes | str) -> dict:
    """
    Send a photo to a Telegram chat.

    If ``image`` is bytes (raw image data), upload via multipart/form-data.
    If ``image`` is a string (URL or file_id), pass it as a JSON field.
    """
    if isinstance(image, bytes):
        return _telegram_api(
            "sendPhoto",
            files={"photo": ("photo", image, "application/octet-stream")},
            chat_id=chat_id,
        )
    return _telegram_api("sendPhoto", chat_id=chat_id, photo=image)


def _calculate_telegram_split(total_lore: str) -> tuple:
    """Calculate the optimal split for 2 Telegram messages.

    Message 1 — text only:      4 096 chars max
    Message 2 — image caption:  1 024 chars max

    Splits at the nearest paragraph break (``\\n\\n``) before the target
    point.  Falls back to the nearest sentence end, then a hard cut.

    Returns: (part1, part2)
    """
    # Aim to fill ~_TG_MSG1_RATIO of the combined space with Message 1
    target_split = int(len(total_lore) * _TG_MSG1_RATIO)
    target_split = min(target_split, _TG_MSG1_MAX)

    # Prefer a natural paragraph break
    split_point = total_lore.rfind("\n\n", 0, target_split)

    if split_point == -1:
        # Fall back to a sentence boundary
        split_point = total_lore.rfind(". ", 0, target_split)

    if split_point == -1:
        # Hard cut as last resort
        split_point = target_split

    part1 = total_lore[:split_point].strip()
    part2 = total_lore[split_point:].strip()

    # Enforce hard limits
    part1 = part1[:_TG_MSG1_MAX]
    part2 = part2[:_TG_MSG2_MAX]

    return part1, part2


def post_to_telegram(lore1, image1, lore2, image2) -> dict:
    """Post both lore entries to all configured Telegram channels.

    Message 1 — plain text only (up to 4 096 chars, no image).
    Message 2 — image with caption (caption up to 1 024 chars).

    The combined lore is split intelligently at a natural paragraph or
    sentence boundary so neither message is truncated mid-sentence.

    Returns a dict with posting metadata for the execution reporter.
    """
    if not TELEGRAM_BOT_TOKEN or not CHANNEL_CHAT_IDS:
        print("[telegram] Token or chat IDs not configured -- printing to stdout.")
        print("=== POST 1 ===")
        print(lore1)
        print("=== POST 2 ===")
        print(lore2)
        return {}

    # Combine both lore parts and calculate an intelligent split
    combined_lore = lore1 + "\n\n" + lore2
    msg1_text, msg2_text = _calculate_telegram_split(combined_lore)

    posting_info: dict = {
        "msg1_text": msg1_text,
        "msg2_text": msg2_text,
        "msg1_status": "failed",
        "msg2_status": "failed",
        "msg2_has_image": bool(image2),
        "image2_size_kb": round(len(image2) / 1024, 1) if image2 else 0.0,
    }

    for chat_id in CHANNEL_CHAT_IDS:
        try:
            # Message 1: pure text — maximum lore space (_TG_MSG1_MAX chars)
            print(f"[telegram] Message 1: {len(msg1_text)} chars (max {_TG_MSG1_MAX}, no image)")
            _telegram_post("sendMessage", chat_id=chat_id, text=msg1_text)
            posting_info["msg1_status"] = "success"

            time.sleep(2)

            # Message 2: image with caption (caption max _TG_MSG2_MAX chars)
            print(f"[telegram] Message 2: {len(msg2_text)} chars caption (max {_TG_MSG2_MAX}) + image")
            if image2:
                _telegram_send_photo(chat_id, image2, caption=msg2_text)
            else:
                # No image available — send as plain text (full 4096-char limit applies)
                _telegram_post("sendMessage", chat_id=chat_id, text=msg2_text)
            posting_info["msg2_status"] = "success"

            print(f"[telegram] Posted to {chat_id} (smart split, no truncation)")
        except Exception as exc:
            print(f"[telegram] Error posting to {chat_id}: {exc}")

    return posting_info


# ---------------------------------------------------------------------------
# Telegram update processing (replies + /profile command)
# ---------------------------------------------------------------------------

# Keywords that mark a message as on-topic (Moonboys universe)
_MOONBOYS_KEYWORDS = (
    "moonboys", "gk", "graffpunks", "nft", "lore", "crypto",
    "carp", "fishing", "graffiti", "rave", "lady-ink", "lady ink",
    "parkour", "substack", "wiki", "brain", "character",
)

# Offset file stores the last processed Telegram update_id
_TELEGRAM_OFFSET_FILE = os.path.join(BASE_DIR, "telegram-offset.json")


def _load_telegram_offset() -> int:
    """Return the last processed Telegram update offset (0 if none)."""
    try:
        with open(_TELEGRAM_OFFSET_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh).get("offset", 0)
    except (OSError, json.JSONDecodeError):
        return 0


def _save_telegram_offset(offset: int) -> None:
    """Persist the latest processed Telegram update offset."""
    try:
        with open(_TELEGRAM_OFFSET_FILE, "w", encoding="utf-8") as fh:
            json.dump({"offset": offset}, fh)
    except OSError as exc:
        print(f"[telegram-updates] Failed to save offset: {exc}")


def _is_moonboys_topic(text: str) -> bool:
    """Return True if the message text references the Moonboys universe."""
    lower = text.lower()
    return any(kw in lower for kw in _MOONBOYS_KEYWORDS)


def _telegram_api(method: str, params: dict | None = None) -> dict:
    """Call a Telegram Bot API method and return the JSON response."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/{method}"
    try:
        resp = requests.post(url, json=params or {}, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        print(f"[telegram-api] {method} failed: {exc}")
        return {"ok": False}


def _send_telegram_reply(chat_id: int | str, text: str,
                         reply_to_message_id: int | None = None) -> None:
    """Send a text reply to a specific chat/message."""
    params: dict = {"chat_id": chat_id, "text": text}
    if reply_to_message_id:
        params["reply_to_message_id"] = reply_to_message_id
    _telegram_api("sendMessage", params)


def process_telegram_updates() -> None:
    """
    Fetch pending Telegram updates (messages sent to the bot since last run)
    and handle them:

    - /profile command  → reply with the user's profile card
    - Moonboys-related messages → record the reply (within 20/day cap)
    - Off-topic messages → silently record the interaction but do not reply
    """
    if not TELEGRAM_BOT_TOKEN:
        print("[telegram-updates] No bot token — skipping update processing.")
        return

    offset = _load_telegram_offset()
    data = _telegram_api("getUpdates", {"offset": offset, "limit": 100, "timeout": 0})

    if not data.get("ok"):
        print("[telegram-updates] getUpdates failed.")
        return

    updates = data.get("result", [])
    if not updates:
        print("[telegram-updates] No pending updates.")
        return

    print(f"[telegram-updates] Processing {len(updates)} update(s).")

    new_offset = offset
    for upd in updates:
        new_offset = max(new_offset, upd["update_id"] + 1)

        msg = upd.get("message") or upd.get("edited_message")
        if not msg:
            continue

        user = msg.get("from", {})
        user_id = user.get("id")
        username = user.get("username", "")
        first_name = user.get("first_name", "")
        chat_id = msg.get("chat", {}).get("id")
        message_id = msg.get("message_id")
        text = msg.get("text", "").strip()

        if not user_id or not text:
            continue

        # Always keep the profile current
        update_user(user_id, username=username, first_name=first_name)

        # ── /profile command ─────────────────────────────────────────────
        if text.lower().startswith("/profile"):
            card = format_profile_card(user_id)
            _send_telegram_reply(chat_id, card, reply_to_message_id=message_id)
            print(f"[telegram-updates] Sent profile card to user {user_id}.")
            continue

        # ── Moonboys reply handling ──────────────────────────────────────
        if _is_moonboys_topic(text):
            allowed = record_reply(user_id, topic=text.split()[0].lower())
            if not allowed:
                # Daily cap reached — send a polite notice (once)
                _send_telegram_reply(
                    chat_id,
                    "🧠 GK BRAIN says: you've hit today's reply limit (20/day). "
                    "Come back tomorrow, yeah.",
                    reply_to_message_id=message_id,
                )
                print(f"[telegram-updates] Daily limit enforced for user {user_id}.")
        # Off-topic messages are noted via update_user (already called above)
        # but do not count against the daily Moonboys reply quota.

    _save_telegram_offset(new_offset)
    print(f"[telegram-updates] Offset advanced to {new_offset}.")


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


def _safe_call_timed(mod, func_name: str, timeout_secs: int = 10, *args, **kwargs):
    """Call mod.func_name with a timeout; return None if it exceeds timeout_secs."""
    import threading
    result_container = [None]

    def _target():
        result_container[0] = _safe_call(mod, func_name, *args, **kwargs)

    t = threading.Thread(target=_target, daemon=True)
    t.start()
    t.join(timeout=timeout_secs)
    if t.is_alive():
        print(f"[godlike] {func_name} timed out after {timeout_secs}s — skipping.")
        return None
    return result_container[0]


def _run_godlike_systems(updates: list, rule_ctx: dict, lore_history: str) -> str:
    """
    Run all 55 systems in tier order and return a combined context string
    that enriches the main lore-generation prompt.
    """
    print("[godlike] Running all 55 systems...")
    ctx_parts = []

    # ── Tier 1: Data Layer ──────────────────────────────────────────────────
    validated   = _safe_call_timed(_data_validator,      "validate_updates",    10, updates)         or updates
    causal_ctx  = _safe_call_timed(_causal_inference,    "build_causal_context", 10, validated, rule_ctx) or ""
    _safe_call_timed(_knowledge_graph, "update_knowledge_graph", 10, validated, lore_history)
    fused       = _safe_call_timed(_multi_source_fusion, "fuse_updates",        10, validated)       or validated
    world_state = _safe_call_timed(_world_state_sim,     "get_world_state",     10, rule_ctx)        or {}
    anomaly_res = _safe_call_timed(_anomaly_detector,    "detect_anomalies",    10, fused)           or {"clean_updates": fused}
    clean_upd   = anomaly_res.get("clean_updates", fused)
    clean_upd   = _safe_call_timed(_temporal_alignment,  "align_timestamps",    10, clean_upd)       or clean_upd
    clean_upd   = _safe_call_timed(_source_attribution,  "attribute_updates",   10, clean_upd)       or clean_upd
    clean_upd   = _safe_call_timed(_priority_queue,      "prioritize_updates",  10, clean_upd, rule_ctx) or clean_upd
    clean_upd   = _safe_call_timed(_deduplication,       "deduplicate_updates", 10, clean_upd)       or clean_upd

    if causal_ctx:
        ctx_parts.append(f"CAUSAL CONTEXT:\n{causal_ctx}")
    if world_state:
        ctx_parts.append(
            f"WORLD STATE: fishing_season={world_state.get('fishing_season')}, "
            f"nft_trend={world_state.get('nft_market_trend')}, "
            f"crypto={world_state.get('crypto_sentiment')}"
        )

    # ── Tier 2: Planning Layer ───────────────────────────────────────────────
    narrative_plan = _safe_call_timed(_hierarchical_planning, "get_narrative_plan",  10, rule_ctx, lore_history) or {}
    adapt_weights  = _safe_call_timed(_adaptive_priority,     "get_adaptive_weights", 10, rule_ctx)              or {}
    social_ctx     = _safe_call_timed(_theory_of_mind,        "get_social_context",  10, rule_ctx, lore_history) or ""
    _safe_call_timed(_narrative_constraints, "apply_constraints", 10, {"rule_ctx": rule_ctx})
    _safe_call_timed(_symbolic_reasoning,    "validate_narrative_logic", 10, "", {})
    strategy_hint  = _safe_call_timed(_rl_optimizer,    "get_strategy_hints",  10, rule_ctx) or ""
    transfer_hint  = _safe_call_timed(_transfer_learning, "get_transfer_hints", 10)           or ""
    _safe_call_timed(_uncertainty_quant, "quantify_uncertainty", 10, clean_upd)

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
    char_memory    = _safe_call_timed(_character_memory,   "get_character_memory",   10)                         or ""
    emotional_st   = _safe_call_timed(_emotional_intel,    "get_emotional_state", 10, rule_ctx, lore_history)   or {}
    skill_levels   = _safe_call_timed(_skill_progression,  "get_skill_levels",    10)                           or {}
    relationships  = _safe_call_timed(_relationship_model, "get_relationship_context", 10)                      or ""
    active_arcs    = _safe_call_timed(_arc_tracker,        "get_active_arcs",     10)                           or []
    _safe_call_timed(_narrative_interp, "interpolate_gap", 10, "", "", rule_ctx)
    personality_h  = _safe_call_timed(_personality_amp,    "get_personality_hints", 10, rule_ctx, emotional_st) or ""
    _safe_call_timed(_world_bible,      "update_world_bible", 10, lore_history)
    arc_direction  = _safe_call_timed(_arc_planner,        "get_arc_direction",  10, rule_ctx, active_arcs)     or ""
    mem_refs       = _safe_call_timed(_memory_references,  "get_memory_references", 10, rule_ctx, lore_history) or ""

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
    emergent_hooks = _safe_call_timed(_emergent_stories, "find_emergent_hooks", 10, clean_upd, rule_ctx) or []
    lore_fuse_ctx  = _safe_call_timed(_lore_fusion,      "fuse_lore_context",   10, clean_upd, rule_ctx, emergent_hooks) or ""
    npc_dialogue   = _safe_call_timed(_dialogue_gen,     "get_npc_dialogue_context", 10, rule_ctx, {})  or ""
    sentiment_dir  = _safe_call_timed(_sentiment_analyzer, "get_sentiment_direction", 10, [lore_history]) or ""
    style_hint     = _safe_call_timed(_style_transfer,   "get_style_hints",     10, "telegram")           or ""
    tension_hint   = _safe_call_timed(_tension_curve,    "get_tension_hint",    10, rule_ctx, {})         or ""
    meta_hint      = _safe_call_timed(_meta_narrative,   "get_meta_hints",      10, rule_ctx, emotional_st) or ""
    gap_filler     = _safe_call_timed(_narrative_interp_eng, "get_gap_filler",  10, "", "")               or ""
    causal_narr    = _safe_call_timed(_causal_weaving,   "get_causal_narrative_hints", 10, clean_upd, rule_ctx, causal_ctx) or ""
    universe_hint  = _safe_call_timed(_universe_engine,  "get_universe_hints",  10, rule_ctx, active_arcs) or ""

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
    learning_hint = _safe_call_timed(_learning_loop,        "get_learning_hints", 10, rule_ctx)  or ""
    trend_pred    = _safe_call_timed(_trend_engine,         "get_trend_predictions", 10, rule_ctx) or ""
    comp_insights = _safe_call_timed(_comparative_analysis, "get_performance_insights", 10)       or ""
    _safe_call_timed(_recursive_discovery, "discover_meta_updates", 10, lore_history)

    if learning_hint:
        ctx_parts.append(f"LEARNING HINTS: {learning_hint}")
    if trend_pred:
        ctx_parts.append(f"TREND PREDICTIONS: {trend_pred}")
    if comp_insights:
        ctx_parts.append(f"PERFORMANCE INSIGHTS: {comp_insights}")

    # ── Tier 7: Integration ──────────────────────────────────────────────────
    _safe_call_timed(_health_monitor, "run_health_check", 10, [])

    print(f"[godlike] All 55 systems ran. Context parts: {len(ctx_parts)}")
    return "\n\n".join(ctx_parts)


def _run_godlike_qa(lore1: str, lore2: str, updates: list, rule_ctx: dict, lore_history: str) -> tuple:
    """
    Run Tier 5 QA checks on generated lore. Returns (lore1, lore2) — potentially
    lightly filtered — and prints any issues found.
    """
    for label, lore in [("Post 1", lore1), ("Post 2", lore2)]:
        quality = _safe_call_timed(_quality_gate,        "check_quality",        10, lore, updates) or {}
        contra  = _safe_call_timed(_contradiction_check, "check_contradictions", 10, lore, lore_history, rule_ctx) or {}
        ethical = _safe_call_timed(_ethical_filter,      "filter_content",       10, lore) or {}
        coheren = _safe_call_timed(_coherence_validator, "validate_coherence",   10, lore, rule_ctx) or {}
        plagiar = _safe_call_timed(_plagiarism_detect,   "check_originality",    10, lore, updates) or {}
        consist = _safe_call_timed(_consistency_proof,   "prove_consistency",    10, lore, {}) or {}

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
    print(f"[gk-brain] Starting at {datetime.datetime.now(datetime.UTC).isoformat()} UTC")

    # -- Initialise execution reporter --
    reporter = None
    if ExecutionReporter is not None:
        try:
            reporter = ExecutionReporter(
                workflow_run_id=os.environ.get("GITHUB_RUN_ID")
            )
        except Exception as _rep_exc:
            print(f"[reporter] Could not initialise reporter: {_rep_exc}")

    # -- Step 1: Seed genesis lore on first run --
    seed_genesis_lore()

    # -- Step 2: Load all knowledge files --
    lore_history = load_lore_history()
    brain_rules = load_brain_rules()
    character_bible = load_character_bible()

    # -- Step 3: Detect updates --
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

    # Log updates to reporter
    if reporter is not None:
        try:
            reporter.log_updates_found(updates)
        except Exception as _rep_exc:
            print(f"[reporter] log_updates_found failed: {_rep_exc}")

    # Filter out updates already used in previous cycles
    unused_updates = [u for u in updates if not u.get("used")]

    # -- Step 4 & 5: Calendar lookup + rule context --
    block = get_current_block()
    rule_ctx = build_rule_context(block)
    print(
        f"[gk-brain] Block: {block['weekday']} "
        f"{block['start_hour']:02d}:00-{block['end_hour']:02d}:00 UTC | "
        f"Rules: {block['rules']}"
    )
    if block.get("task_points"):
        print(f"[gk-brain] Task points ({len(block['task_points'])}): "
              f"{block['task_points']}")

    # -- Step 6: Weather --
    weather = ""
    if rule_ctx["is_outside"]:
        weather = get_uk_weather()
        print(f"[gk-brain] Weather: {weather}")

    # -- Step 7: Substack context --
    substack_context = crawl_substack_for_art_and_content()

    # -- Godlike: Run all 55 systems to enrich the prompt context --
    godlike_context = _run_godlike_systems(unused_updates, rule_ctx, lore_history)

    # -- Step 8: Generate lore (50-fail graceful degradation) --
    print("[gk-brain] Generating lore pair...")
    lore_fail_counter = 0
    best_lore_data: tuple | None = None
    lore1 = lore2 = image_prompt1 = image_prompt2 = ""

    while lore_fail_counter < LORE_MAX_FAILS:
        try:
            lore1, image_prompt1, lore2, image_prompt2 = generate_lore_pair(
                rule_ctx=rule_ctx,
                updates=unused_updates,
                lore_history=lore_history,
                brain_rules=brain_rules,
                character_bible=character_bible,
                weather=weather,
                substack_context=substack_context,
                godlike_context=godlike_context,
            )
            best_lore_data = (lore1, image_prompt1, lore2, image_prompt2)
            break
        except Exception as exc:
            lore_fail_counter += 1
            print(f"[lore-gen] Attempt {lore_fail_counter}/{LORE_MAX_FAILS} failed: {exc}")
            if not best_lore_data:
                # Build a minimal fallback from collected context
                now_str = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M UTC")
                fallback_text = (
                    f"{now_str} — GraffPunks Network Log Entry\n\n"
                    f"[{block['weekday']} {block['start_hour']:02d}:00 UTC — "
                    f"{rule_ctx['activity']}]\n\n"
                    "The lore is being assembled from partial data. "
                    "The block is active. The characters are present. "
                    "The chain continues."
                )
                best_lore_data = (
                    fallback_text,
                    "GraffPunks style scene, UK urban environment, graffiti art.",
                    fallback_text,
                    "GraffPunks style scene, UK urban environment, graffiti art.",
                )
            if lore_fail_counter < LORE_MAX_FAILS:
                sleep_secs = min(2 ** min(lore_fail_counter, 5), 30)
                time.sleep(sleep_secs)

    if lore_fail_counter >= LORE_MAX_FAILS:
        print(f"[lore-gen] Completed lore after {LORE_MAX_FAILS} failures using partial data")

    lore1, image_prompt1, lore2, image_prompt2 = best_lore_data  # type: ignore[misc]

    # Log lore generation to reporter
    if reporter is not None:
        try:
            reporter.log_lore_generated(lore1, lore2, image_prompt1, image_prompt2, rule_ctx)
        except Exception as _rep_exc:
            print(f"[reporter] log_lore_generated failed: {_rep_exc}")

    # -- Step 9: Generate images (50-fail graceful degradation) --
    print("[gk-brain] Generating images...")
    gender1 = _detect_character_gender(lore1)
    gender2 = _detect_character_gender(lore2)
    ref_image1 = _load_reference_image(gender1)
    ref_image2 = _load_reference_image(gender2)

    image1: bytes | None = None
    img_fail_counter_1 = 0
    _img1_start = time.monotonic()
    while img_fail_counter_1 < IMAGE_MAX_FAILS:
        image1 = _grok_image(image_prompt1, reference_image=ref_image1)
        if image1 is not None:
            break
        img_fail_counter_1 += 1
        print(f"[image-gen] Post 1 attempt {img_fail_counter_1}/{IMAGE_MAX_FAILS} failed.")
        # Alternate reference image every 5 retries
        if img_fail_counter_1 % 5 == 0:
            ref_image1 = _load_reference_image(gender1)
        if img_fail_counter_1 < IMAGE_MAX_FAILS:
            sleep_secs = min(2 ** min(img_fail_counter_1, 5), 30)
            time.sleep(sleep_secs)
    _img1_elapsed = time.monotonic() - _img1_start
    if img_fail_counter_1 >= IMAGE_MAX_FAILS:
        print(f"[image-gen] Post 1: all {IMAGE_MAX_FAILS} attempts failed — continuing text-only.")
    if reporter is not None:
        try:
            reporter.log_image_generated(
                post_num=1,
                status="success" if image1 is not None else "failed",
                attempts=img_fail_counter_1 + (1 if image1 is not None else 0),
                prompt=image_prompt1,
                image_bytes=image1,
                generation_time_seconds=_img1_elapsed,
                reference_image=f"{gender1}_set",
            )
        except Exception as _rep_exc:
            print(f"[reporter] log_image_generated(1) failed: {_rep_exc}")

    image2: bytes | None = None
    img_fail_counter_2 = 0
    _img2_start = time.monotonic()
    while img_fail_counter_2 < IMAGE_MAX_FAILS:
        image2 = _grok_image(image_prompt2, reference_image=ref_image2)
        if image2 is not None:
            break
        img_fail_counter_2 += 1
        print(f"[image-gen] Post 2 attempt {img_fail_counter_2}/{IMAGE_MAX_FAILS} failed.")
        if img_fail_counter_2 % 5 == 0:
            ref_image2 = _load_reference_image(gender2)
        if img_fail_counter_2 < IMAGE_MAX_FAILS:
            sleep_secs = min(2 ** min(img_fail_counter_2, 5), 30)
            time.sleep(sleep_secs)
    _img2_elapsed = time.monotonic() - _img2_start
    if img_fail_counter_2 >= IMAGE_MAX_FAILS:
        print(f"[image-gen] Post 2: all {IMAGE_MAX_FAILS} attempts failed — continuing text-only.")
    if reporter is not None:
        try:
            reporter.log_image_generated(
                post_num=2,
                status="success" if image2 is not None else "failed",
                attempts=img_fail_counter_2 + (1 if image2 is not None else 0),
                prompt=image_prompt2,
                image_bytes=image2,
                generation_time_seconds=_img2_elapsed,
                reference_image=f"{gender2}_set",
            )
        except Exception as _rep_exc:
            print(f"[reporter] log_image_generated(2) failed: {_rep_exc}")

    # -- Step 10: Post to Telegram --
    print("[gk-brain] Posting to Telegram...")
    telegram_info = post_to_telegram(lore1, image1, lore2, image2)

    # Log Telegram posting to reporter
    if reporter is not None and telegram_info:
        try:
            _now_iso = datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z")
            reporter.log_telegram_posted(
                message_num=1,
                msg_type="text_only",
                char_count=len(telegram_info.get("msg1_text", "")),
                max_allowed=_TG_MSG1_MAX,
                status=telegram_info.get("msg1_status", "unknown"),
                chat_ids=CHANNEL_CHAT_IDS,
                posted_at=_now_iso,
            )
            reporter.log_telegram_posted(
                message_num=2,
                msg_type="photo_with_caption" if telegram_info.get("msg2_has_image") else "text_only",
                char_count=len(telegram_info.get("msg2_text", "")),
                max_allowed=_TG_MSG2_MAX,
                status=telegram_info.get("msg2_status", "unknown"),
                chat_ids=CHANNEL_CHAT_IDS,
                has_image=telegram_info.get("msg2_has_image", False),
                image_size_kb=telegram_info.get("image2_size_kb", 0.0),
                posted_at=_now_iso,
            )
        except Exception as _rep_exc:
            print(f"[reporter] log_telegram_posted failed: {_rep_exc}")

    # -- Step 11: Save lore history --
    save_lore_history(lore1, lore2)

    # Mark updates as used and persist the change to the queue
    for u in unused_updates:
        u["used"] = True
    if unused_updates:
        persist_queue_updates(unused_updates)

    # -- Step 12: Wiki update (smart merge preferred, simple append fallback) --
    print(f"[wiki-check] FANDOM_BOT_USER set: {bool(os.environ.get('FANDOM_BOT_USER'))}")
    print(f"[wiki-check] FANDOM_BOT_PASSWORD set: {bool(os.environ.get('FANDOM_BOT_PASSWORD'))}")
    print(f"[wiki-check] FANDOM_WIKI_URL set: {bool(os.environ.get('FANDOM_WIKI_URL'))}")
    queue_content = _read_file(QUEUE_FILE, "[]")
    try:
        queue_data = json.loads(queue_content)
        print(f"[wiki-check] Queue file entries: {len(queue_data)}")
    except Exception:
        print(f"[wiki-check] Queue file empty or invalid JSON")
    if _run_smart_wiki_updates:
        print("[wiki-check] Using wiki-smart-merger strategy.")
    else:
        print("[wiki-check] wiki-smart-merger NOT available — will use wiki-updater fallback.")
    wiki_pending = [u for u in updates if u.get("wiki_update") and not u.get("wiki_done")]
    if wiki_pending and _cross_check_and_flag_missing is not None:
        print(f"[gk-brain] Cross-checking {len(wiki_pending)} entries against wiki...")
        try:
            wiki_pending = _cross_check_and_flag_missing()
            print(f"[gk-brain] {len(wiki_pending)} updates missing from wiki — will process.")
        except Exception as exc:
            print(f"[gk-brain] Cross-check failed ({exc}) — proceeding with all pending updates.")
    if wiki_pending:
        print(f"[gk-brain] Updating wiki ({len(wiki_pending)} entries)...")
        smart_merge_succeeded = False
        wiki_smart_count = 0
        wiki_append_count = 0
        wiki_failed_count = 0
        if _run_smart_wiki_updates is not None:
            try:
                wiki_result = _run_smart_wiki_updates()
                print(f"[gk-brain] Smart wiki merge result: {wiki_result}")
                smart_merge_succeeded = True
                wiki_smart_count = len(wiki_pending)
            except Exception as exc:
                print(f"[gk-brain] Smart wiki merge failed ({exc}) — falling back to simple updater.")
        if not smart_merge_succeeded:
            try:
                wiki_result = run_wiki_updates()
                print(f"[gk-brain] Wiki update result: {wiki_result}")
                wiki_append_count = len(wiki_pending)
            except Exception as exc:
                print(f"[gk-brain] Wiki update failed: {exc}")
                wiki_failed_count = len(wiki_pending)
        if reporter is not None:
            try:
                wiki_entries = [
                    {
                        "type": u.get("type", ""),
                        "title": u.get("title", ""),
                        "wiki_section": u.get("wiki_section", u.get("category", "")),
                        "status": "smart_merged" if smart_merge_succeeded else (
                            "appended" if wiki_append_count > 0 else "failed"
                        ),
                        "timestamp": datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z"),
                    }
                    for u in wiki_pending
                ]
                reporter.log_wiki_updated(
                    pending=len(wiki_pending),
                    processed=len(wiki_pending) - wiki_failed_count,
                    smart_merged=wiki_smart_count,
                    appended=wiki_append_count,
                    failed=wiki_failed_count,
                    entries=wiki_entries,
                )
            except Exception as _rep_exc:
                print(f"[reporter] log_wiki_updated failed: {_rep_exc}")
    else:
        print("[gk-brain] No wiki updates needed this cycle.")
        if reporter is not None:
            try:
                reporter.log_wiki_updated(pending=0, processed=0)
            except Exception as _rep_exc:
                print(f"[reporter] log_wiki_updated failed: {_rep_exc}")
    print("[wiki-check] Wiki update attempt complete.")

    # -- Step 13: Cleanup snapshot --
    cleanup_snapshot()

    print(f"[gk-brain] Cycle complete at {datetime.datetime.now(datetime.UTC).isoformat()} UTC")

    # -- Step 14: Generate and save execution report --
    if reporter is not None:
        try:
            reporter.finalize(status="SUCCESS")
            reporter.generate_and_save()
        except Exception as _rep_exc:
            print(f"[reporter] generate_and_save failed: {_rep_exc}")


if __name__ == "__main__":
    main()