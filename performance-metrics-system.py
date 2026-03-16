"""
performance-metrics-system.py - Performance Metrics System for GK BRAIN

Tracks measurable performance metrics across all posts. Calculates
rolling averages and provides trend summaries.

Usage (from gk-brain.py):
    from performance_metrics_system import record_post_metrics, get_performance_summary
    record_post_metrics(post_id, quality_score, data_integration_pct)
    summary = get_performance_summary()
"""

import json
import os
import datetime

BASE_DIR = os.path.dirname(__file__)
METRICS_FILE = os.path.join(BASE_DIR, "performance-metrics.json")

MAX_RECORDS = 200


def _load_metrics() -> dict:
    if os.path.exists(METRICS_FILE):
        try:
            with open(METRICS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"posts": [], "summary": {}}


def _save_metrics(metrics: dict) -> None:
    try:
        metrics["posts"] = metrics["posts"][-MAX_RECORDS:]
        with open(METRICS_FILE, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)
    except Exception as e:
        print(f"[performance-metrics] Save error: {e}")


def record_post_metrics(post_id: str, quality_score: float, data_integration_pct: float) -> None:
    """
    Record performance metrics for a single post.

    Args:
        post_id: Unique post identifier.
        quality_score: Quality score 0.0-10.0.
        data_integration_pct: Fraction of updates integrated (0.0-1.0).
    """
    try:
        metrics = _load_metrics()
        metrics["posts"].append({
            "post_id": post_id,
            "quality_score": round(float(quality_score), 2),
            "data_integration_pct": round(float(data_integration_pct), 3),
            "timestamp": datetime.datetime.utcnow().isoformat(),
        })
        _save_metrics(metrics)
    except Exception as e:
        print(f"[performance-metrics] record_post_metrics error: {e}")


def get_performance_summary() -> dict:
    """
    Return rolling performance summary with trends.

    Returns:
        Dict with total_posts, avg_quality, avg_integration, trend.
    """
    try:
        metrics = _load_metrics()
        posts = metrics.get("posts", [])

        if not posts:
            return {
                "total_posts": 0,
                "avg_quality": 0.0,
                "avg_integration": 0.0,
                "trend": "no data",
            }

        recent = posts[-20:]
        older = posts[-40:-20] if len(posts) >= 40 else posts[:-20]

        avg_q = sum(p["quality_score"] for p in recent) / len(recent)
        avg_i = sum(p["data_integration_pct"] for p in recent) / len(recent)

        trend = "stable"
        if older:
            older_avg_q = sum(p["quality_score"] for p in older) / len(older)
            if avg_q > older_avg_q + 0.5:
                trend = "improving"
            elif avg_q < older_avg_q - 0.5:
                trend = "declining"

        return {
            "total_posts": len(posts),
            "avg_quality": round(avg_q, 2),
            "avg_integration": round(avg_i, 3),
            "trend": trend,
        }
    except Exception as e:
        print(f"[performance-metrics] get_performance_summary error: {e}")
        return {"total_posts": 0, "avg_quality": 0.0, "avg_integration": 0.0, "trend": "error"}
