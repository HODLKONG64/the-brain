"""
system-health-monitor.py - System Health Monitor for GK BRAIN

Monitors all systems and reports health status. Tracks last successful
run times and detects module failures.

Usage (from gk-brain.py):
    from system_health_monitor import run_health_check, get_health_summary
    health = run_health_check(module_names)
    summary_str = get_health_summary()
"""

import importlib.util
import json
import os
import datetime

BASE_DIR = os.path.dirname(__file__)
HEALTH_FILE = os.path.join(BASE_DIR, "system-health.json")


def _load_health() -> dict:
    if os.path.exists(HEALTH_FILE):
        try:
            with open(HEALTH_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"modules": {}, "last_full_check": None, "total_checks": 0}


def _save_health(health: dict) -> None:
    try:
        with open(HEALTH_FILE, "w", encoding="utf-8") as f:
            json.dump(health, f, indent=2)
    except Exception as e:
        print(f"[health-monitor] Save error: {e}")


def _check_module(module_filename: str) -> dict:
    """Check if a Python module file exists and is syntactically valid."""
    filepath = os.path.join(BASE_DIR, module_filename)
    if not os.path.exists(filepath):
        return {"status": "missing", "error": "File not found"}

    try:
        import ast
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
        ast.parse(source)
        return {"status": "healthy", "error": None}
    except SyntaxError as e:
        return {"status": "syntax_error", "error": str(e)}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def run_health_check(modules: list) -> dict:
    """
    Run a health check on a list of module filenames.

    Args:
        modules: List of Python filename strings (e.g. ['data-validator.py']).

    Returns:
        Dict with: healthy_systems (int), failed_systems (list),
        overall_status (str), uptime_pct (float).
    """
    try:
        health = _load_health()
        now = datetime.datetime.utcnow().isoformat()

        healthy = 0
        failed = []

        for module in modules:
            result = _check_module(module)
            health["modules"][module] = {
                **result,
                "last_checked": now,
            }
            if result["status"] == "healthy":
                healthy += 1
            else:
                failed.append(f"{module}: {result['status']} — {result.get('error', '')}")

        total = len(modules)
        uptime_pct = round((healthy / total * 100) if total > 0 else 0.0, 1)
        overall = "GREEN" if uptime_pct >= 90 else "YELLOW" if uptime_pct >= 70 else "RED"

        health["last_full_check"] = now
        health["total_checks"] = health.get("total_checks", 0) + 1
        _save_health(health)

        return {
            "healthy_systems": healthy,
            "total_systems": total,
            "failed_systems": failed,
            "overall_status": overall,
            "uptime_pct": uptime_pct,
        }
    except Exception as e:
        print(f"[health-monitor] run_health_check error: {e}")
        return {"healthy_systems": 0, "failed_systems": [], "overall_status": "UNKNOWN", "uptime_pct": 0.0}


def get_health_summary() -> str:
    """
    Return a human-readable health summary string.

    Returns:
        Formatted health status string.
    """
    try:
        health = _load_health()
        modules = health.get("modules", {})

        total = len(modules)
        healthy = sum(1 for m in modules.values() if m.get("status") == "healthy")
        uptime = round((healthy / total * 100) if total > 0 else 0.0, 1)
        last_check = health.get("last_full_check", "never")

        status = "GREEN" if uptime >= 90 else "YELLOW" if uptime >= 70 else "RED"

        return (
            f"SYSTEM HEALTH [{status}]: {healthy}/{total} modules healthy "
            f"({uptime}% uptime) | Last check: {last_check}"
        )
    except Exception as e:
        print(f"[health-monitor] get_health_summary error: {e}")
        return "SYSTEM HEALTH: Unknown"
