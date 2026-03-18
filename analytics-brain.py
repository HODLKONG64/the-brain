"""
analytics-brain.py — GK BRAIN Standalone Analytics Brain

Reads engagement-tracker.json, generates recommendations and saves
analytics reports to recommendations.json and reports/analytics-report-YYYY-MM-DD.json.

Usage:
    python analytics-brain.py
"""

import json
import os
import datetime

BASE_DIR = os.path.dirname(__file__)
ENGAGEMENT_FILE = os.path.join(BASE_DIR, "engagement-tracker.json")
RECOMMENDATIONS_FILE = os.path.join(BASE_DIR, "recommendations.json")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")


def _load_engagement() -> dict:
    if os.path.exists(ENGAGEMENT_FILE):
        try:
            with open(ENGAGEMENT_FILE, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_recommendations(data: dict) -> None:
    with open(RECOMMENDATIONS_FILE, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def _save_report(report: dict) -> str:
    os.makedirs(REPORTS_DIR, exist_ok=True)
    date_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    report_path = os.path.join(REPORTS_DIR, f"analytics-report-{date_str}.json")
    with open(report_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    return report_path


def _analyse(engagement: dict) -> dict:
    """
    Derive simple engagement insights from engagement-tracker.json.
    Returns a dict with top_categories, avg_engagement, and recommendations.
    """
    posts = engagement.get("posts", [])
    if not posts:
        return {
            "top_categories": [],
            "avg_engagement": 0,
            "recommendations": ["No engagement data available yet."],
            "total_posts_analysed": 0,
        }

    category_scores: dict = {}
    total_score = 0
    for post in posts:
        cat = post.get("category", "unknown")
        score = post.get("engagement_score", 0)
        category_scores.setdefault(cat, []).append(score)
        total_score += score

    avg = total_score / len(posts) if posts else 0

    top_cats = sorted(
        category_scores.items(),
        key=lambda x: sum(x[1]) / len(x[1]),
        reverse=True,
    )[:5]

    recommendations = []
    if top_cats:
        recommendations.append(
            f"Prioritise '{top_cats[0][0]}' content — highest average engagement."
        )
    if avg < 10:
        recommendations.append("Overall engagement is low — consider varying post times.")

    return {
        "top_categories": [{"category": c, "avg_score": sum(s) / len(s)} for c, s in top_cats],
        "avg_engagement": round(avg, 2),
        "recommendations": recommendations,
        "total_posts_analysed": len(posts),
    }


def run() -> dict:
    """Run analytics and persist results."""
    engagement = _load_engagement()
    analysis = _analyse(engagement)

    now = datetime.datetime.now(datetime.timezone.utc)
    report = {
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        **analysis,
    }

    _save_recommendations({"generated_at": report["generated_at"], **analysis})
    report_path = _save_report(report)

    print(f"[analytics-brain] Report saved to {report_path}")
    print(f"[analytics-brain] Posts analysed: {analysis['total_posts_analysed']}")
    print(f"[analytics-brain] Avg engagement: {analysis['avg_engagement']}")

    return report


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2))
