"""
temporal-alignment-engine.py - Temporal Alignment Engine for GK BRAIN

Ensures all data events are properly timestamped and temporally consistent.
Normalises timestamps and rejects future-dated updates.

Usage (from gk-brain.py):
    from temporal_alignment_engine import align_timestamps, validate_timeline
    aligned = align_timestamps(updates)
    ok = validate_timeline(lore_posts)
"""

import datetime
import os

BASE_DIR = os.path.dirname(__file__)


def _parse_ts(ts_str: str):
    """Attempt to parse various timestamp string formats."""
    if not ts_str:
        return None
    formats = [
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
    ]
    ts_clean = ts_str.replace("Z", "+00:00")
    try:
        return datetime.datetime.fromisoformat(ts_clean)
    except Exception:
        pass
    for fmt in formats:
        try:
            return datetime.datetime.strptime(ts_str[:26], fmt)
        except Exception:
            continue
    return None


def _make_aware(dt: datetime.datetime) -> datetime.datetime:
    """Make datetime timezone-aware (UTC) if it is naive."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=datetime.timezone.utc)
    return dt


def align_timestamps(updates: list) -> list:
    """
    Add or normalise UTC timestamps on all updates. Reject future-dated updates.

    Args:
        updates: List of update dicts.

    Returns:
        List with 'timestamp_utc' key (ISO string) on each update.
        Future-dated updates are excluded.
    """
    try:
        now = datetime.datetime.now(datetime.timezone.utc)
        aligned = []

        for u in updates:
            enriched = dict(u)
            ts_str = u.get("timestamp_utc") or u.get("detected_at") or u.get("timestamp")

            if ts_str:
                dt = _make_aware(_parse_ts(str(ts_str)))
                if dt and dt > now:
                    continue
                if dt:
                    enriched["timestamp_utc"] = dt.isoformat()
                else:
                    enriched["timestamp_utc"] = now.isoformat()
            else:
                enriched["timestamp_utc"] = now.isoformat()

            aligned.append(enriched)

        return aligned
    except Exception as e:
        print(f"[temporal-alignment] align_timestamps error: {e}")
        return updates


def validate_timeline(lore_posts: list) -> bool:
    """
    Check that a list of lore posts has non-decreasing timestamps.

    Args:
        lore_posts: List of lore post dicts with 'timestamp_utc' keys.

    Returns:
        True if timeline is valid (no backwards jumps), False if contradictions found.
    """
    try:
        timestamps = []
        for post in lore_posts:
            ts_str = post.get("timestamp_utc") or post.get("timestamp")
            if ts_str:
                dt = _make_aware(_parse_ts(str(ts_str)))
                if dt:
                    timestamps.append(dt)

        if len(timestamps) < 2:
            return True

        for i in range(1, len(timestamps)):
            if timestamps[i] < timestamps[i-1]:
                print(f"[temporal-alignment] Timeline contradiction at index {i}")
                return False

        return True
    except Exception as e:
        print(f"[temporal-alignment] validate_timeline error: {e}")
        return True
