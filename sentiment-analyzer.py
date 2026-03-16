"""
sentiment-analyzer.py — Sentiment Analyzer for GK BRAIN

Analyses and controls the emotional arc across multiple posts.
Tracks sentiment history to prevent sustained negative or positive runs.

Usage (from gk-brain.py):
    from sentiment_analyzer import analyze_sentiment, get_sentiment_direction
    sentiment = analyze_sentiment(lore_text)
    direction = get_sentiment_direction(recent_posts)
"""

import json
import os

BASE_DIR = os.path.dirname(__file__)
HISTORY_FILE = os.path.join(BASE_DIR, "sentiment-history.json")

POSITIVE_WORDS = [
    "beautiful", "amazing", "perfect", "caught", "success", "love", "great",
    "brilliant", "connected", "peaceful", "proud", "excited", "won", "achieved",
    "laughed", "smiled", "vibrant", "alive", "powerful", "clear", "crisp",
]
NEGATIVE_WORDS = [
    "blank", "missed", "failed", "cold", "tired", "lost", "nothing", "empty",
    "grey", "rain", "difficult", "struggling", "problem", "frustrating", "alone",
    "dark", "heavy", "broke", "gone", "quiet",
]
NEUTRAL_WORDS = [
    "then", "next", "after", "before", "while", "still", "back", "set up",
    "moved", "checked", "arrived", "left",
]

MAX_HISTORY = 10


def _load_history() -> dict:
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"posts": []}


def _save_history(history: dict) -> None:
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"[sentiment-analyzer] Save error: {e}")


def analyze_sentiment(lore_text: str) -> str:
    """
    Perform keyword-based sentiment analysis on lore text.

    Args:
        lore_text: The lore string to analyse.

    Returns:
        Sentiment label: 'positive', 'negative', or 'neutral'.
    """
    try:
        text_lower = lore_text.lower()
        pos = sum(1 for w in POSITIVE_WORDS if w in text_lower)
        neg = sum(1 for w in NEGATIVE_WORDS if w in text_lower)

        if pos > neg + 1:
            sentiment = "positive"
        elif neg > pos + 1:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        # Update history
        history = _load_history()
        history["posts"].append(sentiment)
        history["posts"] = history["posts"][-MAX_HISTORY:]
        _save_history(history)

        return sentiment
    except Exception as e:
        print(f"[sentiment-analyzer] analyze_sentiment error: {e}")
        return "neutral"


def get_sentiment_direction(recent_posts: list) -> str:
    """
    Analyse recent post sentiments and recommend a sentiment direction.

    Args:
        recent_posts: List of lore text strings from recent posts.

    Returns:
        Direction string: 'needs_positive', 'needs_variety', 'needs_depth',
        or 'balanced'.
    """
    try:
        history = _load_history()
        saved = history.get("posts", [])

        # Analyse passed posts
        for post in recent_posts:
            if isinstance(post, str):
                analyze_sentiment(post)

        history = _load_history()
        recent = history.get("posts", [])[-10:]

        if not recent:
            return "balanced"

        pos_count = recent.count("positive")
        neg_count = recent.count("negative")

        if neg_count >= 5:
            return "needs_positive"
        elif pos_count >= 7:
            return "needs_variety"
        elif neg_count >= 3 and pos_count <= 1:
            return "needs_depth"
        else:
            return "balanced"
    except Exception as e:
        print(f"[sentiment-analyzer] get_sentiment_direction error: {e}")
        return "balanced"
