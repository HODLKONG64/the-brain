"""
anomaly-detector.py - Anomaly Detector for GK BRAIN

Detects anomalous patterns in update data that may indicate spam or
unusual activity. Tracks per-source update rates.

Usage (from gk-brain.py):
    from anomaly_detector import detect_anomalies
    result = detect_anomalies(updates)
    # result: {"anomalies": list, "clean_updates": list}
"""

import json
import os
import datetime

BASE_DIR = os.path.dirname(__file__)
HISTORY_FILE = os.path.join(BASE_DIR, "anomaly-history.json")

SPIKE_MULTIPLIER = 3.0
MIN_LENGTH_CHARS = 15
MAX_HISTORY_ENTRIES = 500


def _load_history() -> dict:
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"source_counts": {}, "entries": []}


def _save_history(history: dict) -> None:
    try:
        history["entries"] = history["entries"][-MAX_HISTORY_ENTRIES:]
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"[anomaly-detector] Save error: {e}")


def _get_source_key(update: dict) -> str:
    url = update.get("url", "") or update.get("source", "") or "unknown"
    try:
        from urllib.parse import urlparse
        return urlparse(url).netloc.lower().replace("www.", "") or "unknown"
    except Exception:
        return "unknown"


def detect_anomalies(updates: list) -> dict:
    """
    Detect anomalous updates based on source rate spikes and content quality.

    Args:
        updates: List of update dicts to check.

    Returns:
        Dict with keys: anomalies (list of flagged updates), clean_updates (list).
    """
    try:
        if not updates:
            return {"anomalies": [], "clean_updates": []}

        history = _load_history()
        source_counts = history.get("source_counts", {})

        current_sources = {}
        for u in updates:
            key = _get_source_key(u)
            current_sources[key] = current_sources.get(key, 0) + 1

        anomalies = []
        clean = []

        seen_content = set()

        for u in updates:
            flags = []
            source_key = _get_source_key(u)

            content = (u.get("content", "") or u.get("title", "") or "").strip()

            if len(content) < MIN_LENGTH_CHARS:
                flags.append(f"suspiciously_short_content ({len(content)} chars)")

            content_sig = content[:60].lower()
            if content_sig in seen_content:
                flags.append("duplicate_content")
            else:
                seen_content.add(content_sig)

            historical_avg = source_counts.get(source_key, 0)
            current_count = current_sources.get(source_key, 0)
            if historical_avg > 0 and current_count > historical_avg * SPIKE_MULTIPLIER:
                flags.append(f"spike_detected ({current_count}x vs avg {historical_avg:.1f})")

            if flags:
                anomalous = dict(u)
                anomalous["anomaly_flags"] = flags
                anomalies.append(anomalous)
            else:
                clean.append(u)

        for source, count in current_sources.items():
            old = source_counts.get(source, count)
            source_counts[source] = round(old * 0.8 + count * 0.2, 1)

        history["source_counts"] = source_counts
        _save_history(history)

        if anomalies:
            print(f"[anomaly-detector] {len(anomalies)} anomalies detected, {len(clean)} clean")

        return {"anomalies": anomalies, "clean_updates": clean}
    except Exception as e:
        print(f"[anomaly-detector] Error: {e}")
        return {"anomalies": [], "clean_updates": updates}
