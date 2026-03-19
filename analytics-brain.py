"""
analytics-brain.py — GK BRAIN Analytics Agent

Standalone analytics agent. Reads engagement-tracker.json, analyses
performance data, identifies top characters/factions, and writes:
  - reports/analytics-report-YYYY-MM-DD.json
  - recommendations.json (read by gk-brain.py on next lore run)

Usage:
    python analytics-brain.py

Required files (read-only):
    engagement-tracker.json
"""

import datetime
import json
import os
import sys
import importlib.util as _ilu
import pathlib as _pl


def _load_module(name: str, filepath: str):
    spec = _ilu.spec_from_file_location(name, _pl.Path(__file__).parent / filepath)
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _safe_load(name: str, filepath: str):
    """Load a module, returning None on failure (non-fatal)."""
    try:
        return _load_module(name, filepath)
    except Exception as exc:
        print(f"[analytics-brain] Could not load {filepath}: {exc}")
        return None


# ---------------------------------------------------------------------------
# Load analytics modules
# ---------------------------------------------------------------------------

_perf_metrics       = _safe_load("perf_metrics",       "performance-metrics-system.py")
_learning_loop      = _safe_load("learning_loop",      "learning-feedback-loop.py")
_rl_optimizer       = _safe_load("rl_optimizer",       "reinforcement-learning-optimizer.py")
_trend_engine       = _safe_load("trend_engine",       "predictive-trend-engine.py")
_sentiment_analyzer = _safe_load("sentiment_analyzer", "sentiment-analyzer.py")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

BASE_DIR              = os.path.dirname(__file__)
ENGAGEMENT_FILE       = os.path.join(BASE_DIR, "engagement-tracker.json")
RECOMMENDATIONS_FILE  = os.path.join(BASE_DIR, "recommendations.json")
REPORTS_DIR           = os.path.join(BASE_DIR, "reports")

os.makedirs(REPORTS_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------

def _load_engagement() -> dict:
    if os.path.exists(ENGAGEMENT_FILE):
        try:
            with open(ENGAGEMENT_FILE, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_json(filepath: str, data: dict) -> None:
    try:
        with open(filepath, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
        print(f"[analytics-brain] Saved: {os.path.basename(filepath)}")
    except OSError as exc:
        print(f"[analytics-brain] Could not save {filepath}: {exc}")


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

def _count_by_field(entries: list, field: str) -> list:
    """Return sorted [{name, count}] from a list of dicts."""
    counts: dict = {}
    for entry in entries:
        val = entry.get(field, "unknown")
        counts[val] = counts.get(val, 0) + 1
    return sorted(
        [{"name": k, "count": v} for k, v in counts.items()],
        key=lambda x: x["count"],
        reverse=True,
    )


def _analyse(engagement: dict) -> dict:
    """
    Analyse engagement data and return a structured report dict.
    """
    now = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    posts = engagement.get("posts", [])
    if not posts:
        posts = []

    # Top characters and factions by mention count
    top_characters = _count_by_field(posts, "featured_character")[:10]
    top_factions   = _count_by_field(posts, "faction")[:5]

    # Engagement insights
    total_posts      = len(posts)
    avg_reactions    = 0.0
    avg_replies      = 0.0
    if total_posts:
        avg_reactions = sum(p.get("reactions", 0) for p in posts) / total_posts
        avg_replies   = sum(p.get("replies", 0) for p in posts) / total_posts

    # Collect recent lore topics (last 20 posts) for recommendations
    recent_topics = list({p.get("topic", "") for p in posts[-20:] if p.get("topic")})

    # Generate recommendations
    recommendations = []
    if top_characters:
        recommendations.append(
            f"Feature {top_characters[0]['name']} — highest engagement character this period."
        )
    if top_factions:
        recommendations.append(
            f"Lean into {top_factions[0]['name']} faction lore — top performing faction."
        )
    if avg_reactions > 0:
        recommendations.append(
            f"Average post engagement: {avg_reactions:.1f} reactions, {avg_replies:.1f} replies."
        )

    report = {
        "generated_at": now,
        "period_posts": total_posts,
        "avg_reactions": round(avg_reactions, 2),
        "avg_replies": round(avg_replies, 2),
        "top_characters": top_characters,
        "top_factions": top_factions,
        "recent_topics": recent_topics[:10],
        "engagement_insights": [
            f"{total_posts} lore posts analysed.",
            f"Top character: {top_characters[0]['name'] if top_characters else 'none'}.",
            f"Top faction: {top_factions[0]['name'] if top_factions else 'none'}.",
        ],
        "recommendations": recommendations,
    }
    return report


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run() -> int:
    """
    Run analytics pipeline.
    Returns exit code (0 = success, 1 = error).
    """
    print("[analytics-brain] 🧠 Analytics Brain starting…")

    try:
        engagement = _load_engagement()
        report = _analyse(engagement)

        # Save daily report
        today = datetime.date.today().isoformat()
        report_file = os.path.join(REPORTS_DIR, f"analytics-report-{today}.json")
        _save_json(report_file, report)

        # Save recommendations for gk-brain.py to read
        recommendations_data = {
            "generated_at": report["generated_at"],
            "top_characters": report["top_characters"],
            "top_factions": report["top_factions"],
            "engagement_insights": report["engagement_insights"],
            "recommendations": report["recommendations"],
        }
        _save_json(RECOMMENDATIONS_FILE, recommendations_data)

        print(f"[analytics-brain] ✅ Analysis complete — {report['period_posts']} posts processed.")
        return 0

    except Exception as exc:
        print(f"[analytics-brain] ❌ Fatal error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(run())
