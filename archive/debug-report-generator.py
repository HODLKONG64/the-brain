"""
debug-report-generator.py - Debug Report Generator for GK BRAIN

Generates comprehensive debug reports for full transparency into agent
operations. All decisions, scores, and data sources are logged.

Usage (from gk-brain.py):
    from debug_report_generator import generate_debug_report, save_debug_report
    report = generate_debug_report(cycle_data)
    save_debug_report(report)
"""

import datetime
import json
import os

BASE_DIR = os.path.dirname(__file__)
REPORTS_FILE = os.path.join(BASE_DIR, "debug-reports.json")

MAX_REPORTS = 50


def _load_reports() -> list:
    if os.path.exists(REPORTS_FILE):
        try:
            with open(REPORTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                return data.get("reports", [])
        except Exception:
            pass
    return []


def generate_debug_report(cycle_data: dict) -> str:
    """
    Format a comprehensive debug report from cycle data.

    Args:
        cycle_data: Dict containing cycle information such as:
            - rule_ctx, updates_count, quality_score, modules_used,
              generation_time, issues, etc.

    Returns:
        Formatted report string for console output or logging.
    """
    try:
        now = datetime.datetime.utcnow().isoformat()
        lines = [
            "=" * 60,
            f"GK BRAIN DEBUG REPORT — {now}",
            "=" * 60,
        ]

        # Rule context section
        rule_ctx = cycle_data.get("rule_ctx", {})
        if rule_ctx:
            lines.append("\n[RULE CONTEXT]")
            for k, v in rule_ctx.items():
                lines.append(f"  {k}: {v}")

        # Data section
        lines.append("\n[DATA PIPELINE]")
        lines.append(f"  Updates detected: {cycle_data.get('updates_detected', 'N/A')}")
        lines.append(f"  Updates after validation: {cycle_data.get('updates_validated', 'N/A')}")
        lines.append(f"  Updates after dedup: {cycle_data.get('updates_deduplicated', 'N/A')}")
        lines.append(f"  Final updates used: {cycle_data.get('updates_used', 'N/A')}")

        # Quality section
        lines.append("\n[QUALITY METRICS]")
        lines.append(f"  Quality score: {cycle_data.get('quality_score', 'N/A')}")
        lines.append(f"  Data integration: {cycle_data.get('data_integration_pct', 'N/A')}")
        lines.append(f"  Coherence score: {cycle_data.get('coherence_score', 'N/A')}")
        lines.append(f"  Plagiarism check: {cycle_data.get('plagiarism_check', 'N/A')}")

        # Modules used
        modules = cycle_data.get("modules_used", [])
        if modules:
            lines.append("\n[MODULES ACTIVE]")
            for m in modules:
                lines.append(f"  + {m}")

        # Issues
        issues = cycle_data.get("issues", [])
        if issues:
            lines.append("\n[ISSUES DETECTED]")
            for issue in issues:
                lines.append(f"  ! {issue}")

        # Generation
        lines.append("\n[GENERATION]")
        lines.append(f"  Generation time: {cycle_data.get('generation_time_s', 'N/A')}s")
        lines.append(f"  Post length: {cycle_data.get('post_length', 'N/A')} chars")
        lines.append(f"  Platforms posted: {cycle_data.get('platforms_posted', 'N/A')}")

        lines.append("=" * 60)

        return "\n".join(lines)
    except Exception as e:
        print(f"[debug-report] generate_debug_report error: {e}")
        return f"Debug report generation failed: {e}"


def save_debug_report(report: str) -> None:
    """
    Save a debug report to the persistent reports log.

    Args:
        report: Formatted report string.
    """
    try:
        reports = _load_reports()
        reports.append({
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "report": report,
        })
        reports = reports[-MAX_REPORTS:]
        with open(REPORTS_FILE, "w", encoding="utf-8") as f:
            json.dump(reports, f, indent=2)
    except Exception as e:
        print(f"[debug-report] save_debug_report error: {e}")
