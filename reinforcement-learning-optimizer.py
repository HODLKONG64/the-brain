"""
reinforcement-learning-optimizer.py — RL-Style Strategy Optimizer for GK BRAIN

Learns from post outcome scores to recommend generation strategies that
have historically produced higher-quality narrative output.

Usage (from gk-brain.py):
    from reinforcement_learning_optimizer import get_strategy_hints, record_outcome
    hints = get_strategy_hints(rule_ctx)
    record_outcome(post_id, quality_score)
"""

import json
import os

BASE_DIR = os.path.dirname(__file__)
RL_FILE = os.path.join(BASE_DIR, "rl-memory.json")

MAX_HISTORY = 100


def _load_memory() -> dict:
    if os.path.exists(RL_FILE):
        try:
            with open(RL_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"outcomes": [], "pattern_scores": {}}


def _save_memory(memory: dict) -> None:
    try:
        memory["outcomes"] = memory["outcomes"][-MAX_HISTORY:]
        with open(RL_FILE, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=2)
    except Exception as e:
        print(f"[rl-optimizer] Save error: {e}")


def _get_pattern_for_context(rule_ctx: dict) -> str:
    """Derive a pattern key from the current rule context."""
    block = rule_ctx.get("block", "afternoon")
    categories = rule_ctx.get("active_categories", [])
    cat_key = "+".join(sorted(categories[:2])) if categories else "general"
    return f"{block}::{cat_key}"


def get_strategy_hints(rule_ctx: dict) -> str:
    """
    Return strategy hints based on what has historically performed well.

    Args:
        rule_ctx: Current rule context dict.

    Returns:
        Strategy hint string for inclusion in the AI prompt.
    """
    try:
        memory = _load_memory()
        pattern_scores = memory.get("pattern_scores", {})

        if not pattern_scores:
            return (
                "STRATEGY: No historical data yet. Focus on sensory detail, "
                "authentic voice, and weaving real data naturally into narrative."
            )

        # Find top patterns
        sorted_patterns = sorted(pattern_scores.items(), key=lambda x: x[1], reverse=True)
        top = sorted_patterns[:3]
        bottom = sorted_patterns[-2:] if len(sorted_patterns) > 4 else []

        lines = ["=== STRATEGY HINTS (learned from past posts) ==="]
        for pattern, score in top:
            lines.append(f"✓ HIGH SCORE ({score:.1f}/10): {pattern}")
        for pattern, score in bottom:
            lines.append(f"✗ LOW SCORE ({score:.1f}/10): {pattern} — avoid this pattern")

        current_pattern = _get_pattern_for_context(rule_ctx)
        if current_pattern in pattern_scores:
            cs = pattern_scores[current_pattern]
            lines.append(f"Current context pattern '{current_pattern}' scored {cs:.1f}/10 historically.")

        return "\n".join(lines)
    except Exception as e:
        print(f"[rl-optimizer] get_strategy_hints error: {e}")
        return "STRATEGY: Use authentic voice, real data integration, sensory detail."


def record_outcome(post_id: str, quality_score: float) -> None:
    """
    Record a post outcome to update the learning memory.

    Args:
        post_id: Unique identifier for the post (e.g. timestamp string).
        quality_score: Quality score 0.0-10.0 for the post.
    """
    try:
        memory = _load_memory()

        memory["outcomes"].append({
            "post_id": post_id,
            "score": quality_score,
        })

        # Simple running average per pattern key (pattern inferred from post_id prefix if structured)
        pattern = post_id.split(":")[0] if ":" in post_id else "general"
        existing = memory["pattern_scores"].get(pattern, quality_score)
        memory["pattern_scores"][pattern] = round(existing * 0.8 + quality_score * 0.2, 2)

        _save_memory(memory)
    except Exception as e:
        print(f"[rl-optimizer] record_outcome error: {e}")
