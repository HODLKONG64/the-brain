"""
gk-brain-recovery.py — GK BRAIN Recovery Agent

Runs 30 minutes after the main brain on the same 2-hour cycle to detect and
recover from Telegram posting failures.

If post-recovery-state.json is absent → exits immediately (main brain succeeded).
If recovery_attempted is true → exits immediately (already tried this cycle).
Otherwise → attempts to complete any unsent Telegram posts.
"""

import base64
import datetime
import json
import os
import sys
import time

import requests

# ---------------------------------------------------------------------------
# Config from environment (same vars as gk-brain.py)
# ---------------------------------------------------------------------------

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
GROK_API_KEY = os.environ.get("GROK_API_KEY", "")
GROK_TEXT_MODEL = os.environ.get("GROK_TEXT_MODEL", "grok-3-latest")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
CHANNEL_CHAT_IDS_RAW = os.environ.get("CHANNEL_CHAT_IDS", "")
CHANNEL_CHAT_IDS = [c.strip() for c in CHANNEL_CHAT_IDS_RAW.split(",") if c.strip()]
GROK_API_BASE = os.environ.get("GROK_API_BASE", "https://api.x.ai/v1")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RECOVERY_STATE_FILE = os.path.join(BASE_DIR, "post-recovery-state.json")
LORE_HISTORY_FILE = os.path.join(BASE_DIR, "lore-history.md")

# Telegram character limits (match gk-brain.py)
_TG_MSG1_MAX = 4096 - 50
_TG_MSG2_MAX = 1024 - 50
_TG_MSG1_RATIO = 0.8

# Female detection threshold (matches gk-brain.py)
_FEMALE_DETECTION_THRESHOLD = 2

# Reference art image paths (matches gk-brain.py)
_ASSETS_DIR = os.path.join(BASE_DIR, "assets", "layers")
_BOY_IMAGES = [
    os.path.join(_ASSETS_DIR, "boys_set_1", "boysimagesetone.png"),
    os.path.join(_ASSETS_DIR, "bonnet_styles_boys_set_2", "boysimagesettwo.png"),
]
_GIRL_IMAGES = [
    os.path.join(_ASSETS_DIR, "females_set_1", "girlsimagesetone.png"),
    os.path.join(_ASSETS_DIR, "bonnet_styles_females_set_2", "girlsimagesettwo.png"),
]

# Logic files (read-only — never deleted by this agent)
_LOGIC_FILES = [
    os.path.join(BASE_DIR, "brain-rules.md"),
    os.path.join(BASE_DIR, "character-bible.md"),
    os.path.join(BASE_DIR, "MASTER-CHARACTER-CANON.md"),
    os.path.join(BASE_DIR, "lore-planner.md"),
    os.path.join(BASE_DIR, "update-integration-rules.md"),
    os.path.join(BASE_DIR, "gk-brain-complete.md"),
    os.path.join(BASE_DIR, "lore-history.md"),
    os.path.join(BASE_DIR, "genesis-lore.md"),
]

# ---------------------------------------------------------------------------
# Minimal inline helpers (copied from gk-brain.py — kept self-contained)
# ---------------------------------------------------------------------------

def _telegram_post(method: str, **params) -> dict:
    """Make a Telegram Bot API call."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/{method}"
    resp = requests.post(url, json=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram API error: {data.get('description', data)}")
    return data


def _telegram_send_photo(chat_id: str, photo: bytes, caption: str | None = None) -> dict:
    """Send a photo (raw bytes) to Telegram via multipart upload."""
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


def _grok_image(prompt: str, reference_image: bytes | None = None) -> bytes | None:
    """Generate an image via Grok Imagine and return raw bytes, or None on failure."""
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
        print(f"[recovery][grok-image] Error: {exc}")
        return None


def _detect_character_gender(lore_text: str) -> str:
    """Return 'female' if female keywords meet the threshold; else 'male'."""
    female_keywords = [
        "lady ink", "jodie", "zoom 2000",
        "moongirl", "crowned royal",
        " she ", " her ", " hers ", "herself",
        "queen", "sarah", "female",
    ]
    lore_padded = " " + lore_text.lower().replace("-", " ") + " "
    hits = sum(1 for kw in female_keywords if kw in lore_padded)
    return "female" if hits >= _FEMALE_DETECTION_THRESHOLD else "male"


def _load_reference_image(gender: str) -> bytes | None:
    """Load a reference art image for the given gender; returns None on failure."""
    import random
    paths = _GIRL_IMAGES if gender == "female" else _BOY_IMAGES
    path = random.choice(paths)
    try:
        with open(path, "rb") as fh:
            return fh.read()
    except OSError as exc:
        print(f"[recovery][image-ref] Could not load reference image {path}: {exc}")
        return None


def _grok_chat(messages: list) -> str:
    """Send a chat completion to Grok with up to 3 retries."""
    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROK_TEXT_MODEL,
        "messages": messages,
        "max_tokens": 4000,
        "temperature": 0.9,
    }
    last_exc: Exception = RuntimeError("No attempts made")
    for attempt in range(1, 4):
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
                raise
            last_exc = exc
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as exc:
            last_exc = exc
        if attempt < 3:
            time.sleep(2 ** attempt)
    raise RuntimeError(f"[recovery][grok-chat] All 3 attempts failed: {last_exc}")


def _calculate_telegram_split(total_lore: str) -> tuple:
    """Split combined lore into (msg1, msg2) at a natural boundary."""
    target1 = int(len(total_lore) * _TG_MSG1_RATIO)
    split_pos = -1
    for sep in ["\n\n", "\n", ". ", " "]:
        idx = total_lore.rfind(sep, 0, target1 + len(sep))
        if idx > 0:
            split_pos = idx + len(sep)
            break
    if split_pos <= 0:
        split_pos = target1
    part1 = total_lore[:split_pos].rstrip()
    part2 = total_lore[split_pos:].lstrip()
    if not part2:
        midpoint = len(total_lore) // 2
        part1 = total_lore[:midpoint]
        part2 = total_lore[midpoint:]
    part1 = part1[:_TG_MSG1_MAX]
    part2 = part2[:_TG_MSG2_MAX]
    return part1, part2


# ---------------------------------------------------------------------------
# Recovery state helpers
# ---------------------------------------------------------------------------

def _load_state() -> dict | None:
    """Load post-recovery-state.json; return None if absent or unreadable."""
    if not os.path.exists(RECOVERY_STATE_FILE):
        return None
    try:
        with open(RECOVERY_STATE_FILE, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as exc:
        print(f"[recovery] Failed to load state file: {exc}")
        return None


def _save_state(state: dict) -> None:
    """Persist recovery state back to disk."""
    try:
        with open(RECOVERY_STATE_FILE, "w", encoding="utf-8") as fh:
            json.dump(state, fh, indent=2)
    except Exception as exc:
        print(f"[recovery] Failed to save state: {exc}")


def _delete_state() -> None:
    """Remove recovery state file after successful completion."""
    try:
        if os.path.exists(RECOVERY_STATE_FILE):
            os.remove(RECOVERY_STATE_FILE)
            print("[recovery] Deleted post-recovery-state.json (both posts succeeded).")
    except Exception as exc:
        print(f"[recovery] Failed to delete state file: {exc}")


# ---------------------------------------------------------------------------
# Logic file loader
# ---------------------------------------------------------------------------

def _load_logic_files() -> str:
    """Read all logic/rules files and return their combined contents."""
    parts = []
    for path in _LOGIC_FILES:
        try:
            with open(path, encoding="utf-8") as fh:
                parts.append(f"=== {os.path.basename(path)} ===\n{fh.read()}")
        except Exception as exc:
            print(f"[recovery] Could not read {path}: {exc}")
    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Lore regeneration (simplified single-shot with 3 retries)
# ---------------------------------------------------------------------------

def _regenerate_lore(cycle_block: dict, rule_ctx: dict, logic_context: str) -> tuple:
    """
    Regenerate lore using the saved cycle_block and rule_ctx.
    Returns (lore1, image_prompt1, lore2, image_prompt2).
    Raises on all 3 failures.
    """
    block_desc = (
        f"{cycle_block.get('weekday', 'Unknown')} "
        f"{cycle_block.get('start_hour', 0):02d}:00-{cycle_block.get('end_hour', 2):02d}:00 UTC"
    )
    activity = rule_ctx.get("activity", "unknown")
    system_prompt = (
        "You are the GK BRAIN autonomous lore agent. "
        "Generate two distinct lore posts for the GraffPunks/Moonboys universe.\n\n"
        f"{logic_context[:8000]}"
    )
    user_prompt = (
        f"Current block: {block_desc}\n"
        f"Activity: {activity}\n\n"
        "Generate two lore posts. Format EXACTLY as:\n"
        "POST 1:\n[lore text]\n\n"
        "IMAGE PROMPT 1:\n[image prompt]\n\n"
        "POST 2:\n[lore text]\n\n"
        "IMAGE PROMPT 2:\n[image prompt]"
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    last_exc: Exception = RuntimeError("No attempts")
    for attempt in range(1, 4):
        try:
            raw = _grok_chat(messages)

            def _extract(label: str, text: str) -> str:
                marker = f"{label}:"
                idx = text.find(marker)
                if idx == -1:
                    return ""
                start = idx + len(marker)
                next_labels = ["POST 1:", "IMAGE PROMPT 1:", "POST 2:", "IMAGE PROMPT 2:"]
                end = len(text)
                for nl in next_labels:
                    ni = text.find(nl, start)
                    if ni != -1 and ni < end:
                        end = ni
                return text[start:end].strip()

            lore1 = _extract("POST 1", raw)
            prompt1 = _extract("IMAGE PROMPT 1", raw)
            lore2 = _extract("POST 2", raw)
            prompt2 = _extract("IMAGE PROMPT 2", raw)

            if lore1 and lore2:
                return lore1, prompt1, lore2, prompt2
            raise ValueError("Incomplete lore generation response")
        except Exception as exc:
            last_exc = exc
            print(f"[recovery] Lore regen attempt {attempt}/3 failed: {exc}")
            if attempt < 3:
                time.sleep(2 ** attempt)

    raise RuntimeError(f"[recovery] Lore regeneration failed after 3 attempts: {last_exc}")


# ---------------------------------------------------------------------------
# Post a single lore entry (text + optional image) to Telegram
# ---------------------------------------------------------------------------

def _post_single(msg_text: str, image_prompt: str, lore_text: str, post_num: int) -> bool:
    """
    Generate image (with 50-fail graceful degradation) and post to Telegram.
    Returns True on success for at least one channel.
    """
    gender = _detect_character_gender(lore_text)
    ref_image = _load_reference_image(gender)

    image: bytes | None = None
    for attempt in range(1, 51):
        image = _grok_image(image_prompt, reference_image=ref_image)
        if image is not None:
            break
        print(f"[recovery][image-gen] Post {post_num} attempt {attempt}/50 failed.")
        if attempt % 5 == 0:
            ref_image = _load_reference_image(gender)
        if attempt < 50:
            time.sleep(min(2 ** min(attempt, 5), 30))

    success = False
    for chat_id in CHANNEL_CHAT_IDS:
        try:
            if image:
                _telegram_send_photo(chat_id, image, caption=msg_text[:_TG_MSG2_MAX])
            else:
                _telegram_post("sendMessage", chat_id=chat_id, text=msg_text[:_TG_MSG1_MAX])
            print(f"[recovery] Post {post_num} sent to {chat_id}.")
            success = True
        except Exception as exc:
            print(f"[recovery] Failed to post {post_num} to {chat_id}: {exc}")
    return success


# ---------------------------------------------------------------------------
# Main recovery entry point
# ---------------------------------------------------------------------------

def main() -> None:
    state = _load_state()

    if state is None:
        print("[recovery] No pending recovery state. Sleeping.")
        return

    if state.get("recovery_attempted"):
        print("[recovery] Already attempted this cycle. Skipping.")
        return

    # Mark recovery as attempted immediately to prevent looping on crash
    state["recovery_attempted"] = True
    _save_state(state)

    print("[recovery] Recovery state found. Attempting to complete unsent posts...")

    cycle_block = state.get("cycle_block", {})
    rule_ctx = state.get("rule_ctx", {})
    lore1 = state.get("lore1", "")
    image_prompt1 = state.get("image_prompt1", "")
    lore2 = state.get("lore2", "")
    image_prompt2 = state.get("image_prompt2", "")
    post1_sent = state.get("post1_sent", False)
    post2_sent = state.get("post2_sent", False)

    # If lore was never generated, regenerate it now
    if not lore1 or not lore2:
        print("[recovery] Lore not present in state — regenerating...")
        try:
            logic_context = _load_logic_files()
            lore1, image_prompt1, lore2, image_prompt2 = _regenerate_lore(
                cycle_block, rule_ctx, logic_context
            )
        except Exception as exc:
            print(f"[recovery] Recovery failed — could not regenerate lore: {exc}")
            return

    # Compute split once for both messages (mirrors gk-brain.py logic)
    combined_lore = lore1 + "\n\n" + lore2
    msg1_text, msg2_text = _calculate_telegram_split(combined_lore)

    recovery_ok = True

    # Attempt post 1
    if not post1_sent:
        print("[recovery] Attempting Post 1...")
        ok = False
        for chat_id in CHANNEL_CHAT_IDS:
            try:
                _telegram_post("sendMessage", chat_id=chat_id, text=msg1_text)
                print(f"[recovery] Post 1 sent to {chat_id}.")
                ok = True
            except Exception as exc:
                print(f"[recovery] Post 1 failed for {chat_id}: {exc}")
        if ok:
            post1_sent = True
            state["post1_sent"] = True
            _save_state(state)
            time.sleep(2)
        else:
            recovery_ok = False

    # Attempt post 2
    if not post2_sent:
        print("[recovery] Attempting Post 2 (with image)...")
        ok = _post_single(msg2_text, image_prompt2, lore2, post_num=2)
        if ok:
            post2_sent = True
            state["post2_sent"] = True
            _save_state(state)
        else:
            recovery_ok = False

    if recovery_ok and post1_sent and post2_sent:
        # Success — clean up
        _delete_state()
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
        try:
            with open(LORE_HISTORY_FILE, "a", encoding="utf-8") as fh:
                fh.write(f"\n[RECOVERY] Cycle completed by recovery agent at {timestamp}\n")
        except Exception as exc:
            print(f"[recovery] Could not append to lore-history.md: {exc}")
        print("[recovery] Recovery complete. State file deleted.")
    else:
        print("[recovery] Recovery failed. State retained for next attempt.")


if __name__ == "__main__":
    main()
