"""
learning-feedback-loop.py - Learning Feedback Loop for GK BRAIN

Self-improvement cycle that accumulates wisdom from post outcomes
and adjusts generation guidance over time.

Usage (from gk-brain.py):
    from learning_feedback_loop import get_learning_hints, record_feedback
    hints = get_learning_hints(rule_ctx)
    record_feedback(post_id, score)
"""

import json
import os
import datetime

BASE_DIR = os.path.dirname(__file__)
MEMORY_FILE = os.path.join(BASE_DIR, "learning-memory.json")

MAX_FEEDBACK_RECORDS = 100

DEFAULT_WISDOM = [
    "Morning fishing posts score highest for authenticity.",
    "Night rave posts generate strongest emotional engagement.",
    "Combining activity description + philosophical reflection = best results.",
    "Specific sensory details (smell, sound, texture) elevate all post types.",
    "Short, punchy sentences during action; longer during reflection.",
]


def _load_memory() -> dict:
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"feedback": [], "wisdom": list(DEFAULT_WISDOM), "cycle_count": 0}


def _save_memory(memory: dict) -> None:
    try:
        memory["feedback"] = memory["feedback"][-MAX_FEEDBACK_RECORDS:]
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=2)
    except Exception as e:
        print(f"[learning-feedback] Save error: {e}")


def get_learning_hints(rule_ctx: dict) -> str:
    """
    Return accumulated wisdom as generation hints.

    Args:
        rule_ctx: Current rule context dict.

    Returns:
        Learning hints string for AI prompt inclusion.
    """
    try:
        memory = _load_memory()
        wisdom = memory.get("wisdom", DEFAULT_WISDOM)
        total = memory.get("cycle_count", 0)

        lines = [f"=== LEARNING HINTS (from {total} cycles) ==="]
        for w in wisdom[:5]:
            lines.append(f"• {w}")

        block = rule_ctx.get("block", "afternoon")
        if block == "morning":
            lines.append("Context tip: Morning cycle — lean into the fishing/dawn narrative.")
        elif block in ("evening", "night"):
            lines.append("Context tip: Evening/night cycle — rave, art, and reflective tones perform best.")

        return "\n".join(lines)
    except Exception as e:
        print(f"[learning-feedback] get_learning_hints error: {e}")
        return "Apply authentic voice, sensory detail, and real-world data integration."


def record_feedback(post_id: str, score: float) -> None:
    """
    Record a post outcome score to update the learning memory.

    Args:
        post_id: Unique identifier for the post.
        score: Quality score 0.0-10.0.
    """
    try:
        memory = _load_memory()
        memory["feedback"].append({
            "post_id": post_id,
            "score": float(score),
            "timestamp": datetime.datetime.utcnow().isoformat(),
        })
        memory["cycle_count"] = memory.get("cycle_count", 0) + 1

        # Periodically distil new wisdom from feedback
        if len(memory["feedback"]) % 10 == 0:
            recent = memory["feedback"][-10:]
            avg = sum(f["score"] for f in recent) / len(recent)
            if avg >= 8.0:
                memory["wisdom"].append(
                    f"Recent 10-cycle avg score: {avg:.1f}/10 - current strategy is effective"
                )
                memory["wisdom"] = memory["wisdom"][-10:]

        _save_memory(memory)
    except Exception as e:
        print(f"[learning-feedback] record_feedback error: {e}")
