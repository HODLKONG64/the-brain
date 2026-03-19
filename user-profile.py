"""
user-profile.py — GK BRAIN User Profile Manager

Tracks Telegram user interactions and provides a formatted profile card.

Profile data is stored in user-profiles.json (gitignored).
"""

import json
import os
import datetime

BASE_DIR = os.path.dirname(__file__)
PROFILES_FILE = os.path.join(BASE_DIR, "user-profiles.json")

# Max replies per user per calendar day (UTC)
DAILY_REPLY_LIMIT = 20


# ---------------------------------------------------------------------------
# Persistence helpers
# ---------------------------------------------------------------------------

def _load_profiles() -> dict:
    """Load user profiles from disk, returning an empty dict on missing/corrupt file."""
    try:
        with open(PROFILES_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return {}


def _save_profiles(profiles: dict) -> None:
    """Persist user profiles to disk."""
    try:
        with open(PROFILES_FILE, "w", encoding="utf-8") as fh:
            json.dump(profiles, fh, indent=2, ensure_ascii=False)
    except OSError as exc:
        print(f"[user-profile] Failed to save profiles: {exc}")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def update_user(user_id: int | str, username: str = "", first_name: str = "") -> dict:
    """
    Create or update a user's profile entry.

    Returns the updated profile dict for the user.
    """
    profiles = _load_profiles()
    uid = str(user_id)
    now = datetime.datetime.now(datetime.timezone.utc)
    today = now.strftime("%Y-%m-%d")

    if uid not in profiles:
        profiles[uid] = {
            "user_id": uid,
            "username": username or "",
            "first_name": first_name or "",
            "first_seen": today,
            "last_seen": now.isoformat(),
            "total_replies": 0,
            "daily_replies": 0,
            "daily_replies_date": today,
            "topics_engaged": [],
        }
        print(f"[user-profile] New profile created for user {uid} ({first_name or username})")
    else:
        profile = profiles[uid]
        # Refresh editable fields
        if username:
            profile["username"] = username
        if first_name:
            profile["first_name"] = first_name
        profile["last_seen"] = now.isoformat()
        # Reset daily counter if it's a new day
        if profile.get("daily_replies_date") != today:
            profile["daily_replies"] = 0
            profile["daily_replies_date"] = today

    _save_profiles(profiles)
    return profiles[uid]


def record_reply(user_id: int | str, topic: str = "") -> bool:
    """
    Record a reply from the user and increment their daily counter.

    Returns True if the reply was recorded (within the daily limit),
    or False if the user has hit the 20-reply daily cap.
    """
    profiles = _load_profiles()
    uid = str(user_id)
    now = datetime.datetime.now(datetime.timezone.utc)
    today = now.strftime("%Y-%m-%d")

    if uid not in profiles:
        # Auto-create a minimal profile
        update_user(uid)
        profiles = _load_profiles()

    profile = profiles[uid]

    # Reset if new day
    if profile.get("daily_replies_date") != today:
        profile["daily_replies"] = 0
        profile["daily_replies_date"] = today

    if profile["daily_replies"] >= DAILY_REPLY_LIMIT:
        print(f"[user-profile] Daily limit reached for user {uid}")
        return False

    profile["daily_replies"] += 1
    profile["total_replies"] = profile.get("total_replies", 0) + 1
    profile["last_seen"] = now.isoformat()

    # Track unique topics
    if topic and topic not in profile.get("topics_engaged", []):
        topics = profile.setdefault("topics_engaged", [])
        topics.append(topic)
        # Keep only the last 20 unique topics
        profile["topics_engaged"] = topics[-20:]

    _save_profiles(profiles)
    return True


def check_reply_limit(user_id: int | str) -> bool:
    """
    Check whether the user has remaining replies today.

    Returns True if they can still reply, False if capped.
    """
    profiles = _load_profiles()
    uid = str(user_id)
    today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

    if uid not in profiles:
        return True  # No profile yet → not capped

    profile = profiles[uid]
    if profile.get("daily_replies_date") != today:
        return True  # New day → reset

    return profile.get("daily_replies", 0) < DAILY_REPLY_LIMIT


def get_profile(user_id: int | str) -> dict | None:
    """Return the raw profile dict for a user, or None if not found."""
    profiles = _load_profiles()
    return profiles.get(str(user_id))


def format_profile_card(user_id: int | str) -> str:
    """
    Format a user's profile as a Telegram-ready text card.

    Uses plain text with emoji decoration for maximum compatibility
    across all Telegram clients (no MarkdownV2 special chars).
    """
    profile = get_profile(user_id)
    if profile is None:
        return (
            "👤 PROFILE NOT FOUND\n"
            "──────────────────\n"
            "No profile data yet.\n"
            "Interact with the GK BRAIN channel to build your Moonboys record."
        )

    today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

    uid = profile.get("user_id", "?")
    username = profile.get("username", "")
    first_name = profile.get("first_name", "Anonymous")
    first_seen = profile.get("first_seen", "unknown")
    last_seen_raw = profile.get("last_seen", "")
    total_replies = profile.get("total_replies", 0)
    daily_replies = profile.get("daily_replies", 0)
    daily_date = profile.get("daily_replies_date", "")
    topics = profile.get("topics_engaged", [])

    # Reset daily counter display if it's a new day
    if daily_date != today:
        daily_replies = 0

    remaining = max(0, DAILY_REPLY_LIMIT - daily_replies)

    # Format last_seen as a compact timestamp
    if last_seen_raw:
        try:
            last_seen_dt = datetime.datetime.fromisoformat(last_seen_raw)
            last_seen = last_seen_dt.strftime("%Y-%m-%d %H:%M UTC")
        except ValueError:
            last_seen = last_seen_raw[:16]
    else:
        last_seen = "never"

    display_name = first_name
    if username:
        display_name = f"{first_name} (@{username})"

    topics_line = (
        ", ".join(topics[-5:]) if topics else "none yet"
    )

    card = (
        "┌─────────────────────────────┐\n"
        "│   🧠 MOONBOYS BRAIN DOSSIER  │\n"
        "└─────────────────────────────┘\n"
        f"\n"
        f"👤  {display_name}\n"
        f"🆔  User #{uid}\n"
        f"\n"
        f"📅  {'First contact':<14}: {first_seen}\n"
        f"🕐  {'Last seen':<14}: {last_seen}\n"
        f"\n"
        f"💬  {'Total replies':<14}: {total_replies}\n"
        f"📊  {'Today\'s usage':<14}: {daily_replies}/{DAILY_REPLY_LIMIT}\n"
        f"🎟️  {'Replies left':<14}: {remaining}\n"
        f"\n"
        f"🏷️  Topics engaged:\n"
        f"    {topics_line}\n"
        f"\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"GraffPunks Network — stay up."
    )

    return card
