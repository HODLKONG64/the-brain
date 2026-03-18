"""
execution-reporter.py — GK BRAIN Execution Reporter

Collects data from all stages of the execution pipeline, structures it into
an organized JSON report, saves a timestamped report file, and prints a
human-readable summary to console.
"""

import datetime
import json
import os
import time


class ExecutionReporter:
    """Collect and report on a single GK BRAIN execution run."""

    def __init__(self, workflow_run_id: str | None = None):
        now = datetime.datetime.now(datetime.UTC)
        self._start_time = time.monotonic()
        self._execution_id = now.strftime("%Y%m%d-%H%M%S")
        self._timestamp = now.isoformat().replace("+00:00", "Z")

        workflow_run_id = workflow_run_id or ""
        if workflow_run_id:
            self._workflow_run_url = (
                f"https://github.com/HODLKONG64/the-brain/actions/runs/{workflow_run_id}"
            )
        else:
            self._workflow_run_url = ""

        # Stage timing
        self._stage_start: dict[str, float] = {}
        self._stage_durations: dict[str, float] = {}

        # Data buckets
        self._updates_found: list[dict] = []
        self._lore_generation: dict = {}
        self._image_generation: dict = {}
        self._telegram_posting: dict = {}
        self._wiki_updates: dict = {}
        self._quality_checks: dict = {}
        self._errors: list[str] = []
        self._warnings: list[str] = []
        self._final_status: str = "UNKNOWN"

    # ------------------------------------------------------------------
    # Stage timing helpers
    # ------------------------------------------------------------------

    def start_stage(self, stage: str) -> None:
        """Mark the start of a named pipeline stage."""
        self._stage_start[stage] = time.monotonic()

    def end_stage(self, stage: str) -> float:
        """Mark the end of a named stage and return elapsed seconds.

        Returns 0.0 if the stage was never started via start_stage().
        """
        if stage not in self._stage_start:
            self._stage_durations[stage] = 0.0
            return 0.0
        elapsed = time.monotonic() - self._stage_start[stage]
        self._stage_durations[stage] = round(elapsed, 2)
        return elapsed

    # ------------------------------------------------------------------
    # Logging methods
    # ------------------------------------------------------------------

    def log_updates_found(self, updates: list) -> None:
        """Record detected updates."""
        self._updates_found = []
        for i, u in enumerate(updates):
            self._updates_found.append({
                "id": f"update-{i + 1:03d}",
                "type": u.get("type", ""),
                "category": u.get("category", ""),
                "title": u.get("title", ""),
                "content": u.get("content", "")[:200],
                "source": u.get("source", ""),
                "confidence": u.get("confidence", 0),
                "used_in_lore": bool(u.get("used_in_lore")),
            })

    def log_lore_generated(
        self,
        lore1: str,
        lore2: str,
        image_prompt1: str,
        image_prompt2: str,
        rule_ctx: dict,
    ) -> None:
        """Record lore generation details."""
        emotional_state = rule_ctx.get("emotional_state", {})
        self._lore_generation = {
            "mode": rule_ctx.get("mode", ""),
            "time_block": rule_ctx.get("time_block", ""),
            "calendar_activity": rule_ctx.get("activity", ""),
            "featured_character": rule_ctx.get("featured_character", "main artist"),
            "emotional_state": {
                "mood": emotional_state.get("mood", rule_ctx.get("mood", "")),
                "stress_level": emotional_state.get("stress_level", ""),
                "confidence": emotional_state.get("confidence", ""),
                "tone_hint": emotional_state.get("tone_hint", rule_ctx.get("tone_hint", "")),
            },
            "narrative_tension": rule_ctx.get("narrative_tension", ""),
            "arc_direction": rule_ctx.get("arc_direction", ""),
            "personality_tone": rule_ctx.get("personality_tone", ""),
            "task_points_addressed": len(rule_ctx.get("task_points", [])),
            "post1": {
                "full_text": lore1,
                "char_count": len(lore1),
                "summary": lore1[:120].replace("\n", " ") + ("..." if len(lore1) > 120 else ""),
            },
            "post2": {
                "full_text": lore2,
                "char_count": len(lore2),
                "summary": lore2[:120].replace("\n", " ") + ("..." if len(lore2) > 120 else ""),
            },
            "image_prompt1": image_prompt1,
            "image_prompt2": image_prompt2,
        }

    def log_image_generated(
        self,
        post_num: int,
        status: str,
        attempts: int,
        prompt: str = "",
        image_bytes: bytes | None = None,
        generation_time_seconds: float = 0.0,
        reference_image: str = "",
    ) -> None:
        """Record image generation result for one post."""
        key = f"post{post_num}"
        file_size_kb = round(len(image_bytes) / 1024, 1) if image_bytes else 0
        self._image_generation[key] = {
            "status": status,
            "attempts": attempts,
            "endpoint": "https://api.x.ai/v1/images/generations",
            "model": "grok-imagine-image",
            "prompt": prompt[:300] if prompt else "",
            "reference_image": reference_image,
            "response_format": "url",
            "file_size_kb": file_size_kb,
            "generation_time_seconds": round(generation_time_seconds, 2),
        }

    def log_telegram_posted(
        self,
        message_num: int,
        msg_type: str,
        char_count: int,
        max_allowed: int,
        status: str,
        chat_ids: list | None = None,
        message_ids: list | None = None,
        has_image: bool = False,
        image_size_kb: float = 0.0,
        posted_at: str = "",
    ) -> None:
        """Record a Telegram posting result."""
        key = f"message{message_num}"
        entry: dict = {
            "platform": "telegram",
            "type": msg_type,
            "chat_ids": chat_ids or [],
            "character_count": char_count,
            "max_allowed": max_allowed,
            "status": status,
            "message_ids": message_ids or [],
            "posted_at": posted_at or datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z"),
        }
        if has_image:
            entry["image_file_size_kb"] = image_size_kb
            entry["image_format"] = "jpeg"
        self._telegram_posting[key] = entry

        # Update aggregates
        total = sum(1 for k in self._telegram_posting if k.startswith("message"))
        failures = sum(
            1 for v in self._telegram_posting.values()
            if isinstance(v, dict) and v.get("status") != "success"
        )
        self._telegram_posting["total_messages_sent"] = total
        self._telegram_posting["total_attempts"] = total
        self._telegram_posting["failures"] = failures

    def log_wiki_updated(
        self,
        pending: int = 0,
        processed: int = 0,
        smart_merged: int = 0,
        appended: int = 0,
        failed: int = 0,
        skipped: int = 0,
        entries: list | None = None,
    ) -> None:
        """Record wiki update results."""
        self._wiki_updates = {
            "pending_updates": pending,
            "processed": processed,
            "smart_merged": smart_merged,
            "appended": appended,
            "failed": failed,
            "skipped": skipped,
            "entries": entries or [],
        }

    def log_quality_checks(
        self,
        post1_coherence: float = 0.0,
        post2_coherence: float = 0.0,
        updates_woven: int = 0,
        total_updates: int = 0,
        consistency_violations: int = 0,
        is_unique: bool = True,
    ) -> None:
        """Record quality check results."""
        non_zero = [v for v in (post1_coherence, post2_coherence) if v > 0]
        avg_coherence = round(sum(non_zero) / len(non_zero), 1) if non_zero else 0.0
        coverage = round((updates_woven / total_updates * 100) if total_updates else 0)
        self._quality_checks = {
            "lore_coherence": {
                "post1": post1_coherence,
                "post2": post2_coherence,
                "average": avg_coherence,
                "passed": avg_coherence >= 7.0 or (post1_coherence == 0 and post2_coherence == 0),
            },
            "data_integration": {
                "updates_woven": updates_woven,
                "total_updates": total_updates,
                "coverage_percent": coverage,
                "passed": coverage >= 50 or total_updates == 0,
            },
            "consistency": {
                "violations": consistency_violations,
                "passed": consistency_violations == 0,
            },
            "plagiarism": {
                "unique": is_unique,
                "passed": is_unique,
            },
        }

    def add_error(self, message: str) -> None:
        """Record an error."""
        self._errors.append(message)

    def add_warning(self, message: str) -> None:
        """Record a warning."""
        self._warnings.append(message)

    # ------------------------------------------------------------------
    # Finalize + save
    # ------------------------------------------------------------------

    def finalize(self, status: str = "SUCCESS") -> None:
        """Set the final execution status."""
        self._final_status = status

    def _build_report(self) -> dict:
        """Assemble the full report dictionary."""
        total_duration = round(time.monotonic() - self._start_time, 2)

        # Build system_stats
        try:
            import resource
            import sys as _sys
            raw = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            # Linux returns kilobytes; macOS returns bytes
            mem_mb = round(raw / 1024 if _sys.platform != "darwin" else raw / (1024 * 1024), 1)
        except Exception:
            mem_mb = 0

        system_stats = {
            "total_duration_seconds": total_duration,
            "stage_durations": self._stage_durations,
            "memory_usage_mb": mem_mb,
        }

        report = {
            "execution_id": self._execution_id,
            "timestamp": self._timestamp,
        }
        if self._workflow_run_url:
            report["workflow_run_url"] = self._workflow_run_url

        report["updates_found"] = self._updates_found
        report["lore_generation"] = self._lore_generation
        report["image_generation"] = self._image_generation
        report["telegram_posting"] = self._telegram_posting
        report["wiki_updates"] = self._wiki_updates
        report["system_stats"] = system_stats
        report["quality_checks"] = self._quality_checks
        report["final_status"] = self._final_status
        report["errors"] = self._errors
        report["warnings"] = self._warnings

        return report

    def generate_and_save(self, output_dir: str | None = None) -> str:
        """Write the JSON report to disk and print a console summary.

        Returns the path of the saved report file.
        Never raises — always returns a (possibly empty) path.
        """
        try:
            report = self._build_report()
        except Exception as exc:
            print(f"[reporter] Failed to build report ({exc}); saving partial report.")
            report = {
                "execution_id": getattr(self, "_execution_id", "unknown"),
                "timestamp": getattr(self, "_timestamp", ""),
                "final_status": getattr(self, "_final_status", "ERROR"),
                "errors": getattr(self, "_errors", []) + [str(exc)],
                "warnings": getattr(self, "_warnings", []),
                "updates_found": [],
                "lore_generation": {},
                "image_generation": {},
                "telegram_posting": {},
                "wiki_updates": {},
                "system_stats": {},
                "quality_checks": {},
            }

        # Determine output path
        filename = f"execution-report-{self._execution_id}.json"
        if output_dir is None:
            output_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(output_dir, filename)

        try:
            with open(filepath, "w", encoding="utf-8") as fh:
                json.dump(report, fh, indent=2, ensure_ascii=False)
        except OSError as exc:
            print(f"[reporter] Could not save report to {filepath}: {exc}")
            filepath = ""

        try:
            self._print_summary(report, filepath)
        except Exception as exc:
            print(f"[reporter] Summary print failed ({exc}); report still saved.")
        return filepath

    # ------------------------------------------------------------------
    # Console summary
    # ------------------------------------------------------------------

    def _print_summary(self, report: dict, filepath: str) -> None:
        """Print the human-readable execution summary to stdout."""
        W = 76  # inner width between ║ borders

        def _pad(text: str) -> str:
            """Left-justify *text* inside the box column."""
            return f"║ {text:<{W - 2}} ║"

        def _div() -> str:
            return "╠" + "═" * W + "╣"

        status = report.get("final_status", "UNKNOWN")
        status_icon = "✅" if status == "SUCCESS" else "❌"
        ts = report.get("timestamp", "")[:19].replace("T", " ")

        total_secs = report.get("system_stats", {}).get("total_duration_seconds", 0)
        mins, secs = divmod(int(total_secs), 60)
        duration_str = f"{total_secs} seconds ({mins} min {secs} sec)"

        lines = []
        # Header
        header_text = f"GK BRAIN EXECUTION REPORT — {ts} UTC"
        lines.append("╔" + "═" * W + "╗")
        lines.append(_pad(f"{header_text:^{W - 2}}"))
        lines.append(_div())

        # Status + duration
        lines.append(_pad(f"STATUS: {status_icon} {status}"))
        lines.append(_pad(f"DURATION: {duration_str}"))
        lines.append(_div())

        # Updates found
        updates = report.get("updates_found", [])
        lines.append(_pad(f"UPDATES FOUND: {len(updates)}"))
        for u in updates:
            conf = u.get("confidence", 0)
            conf_str = f"({conf:.2f} confidence)" if conf else ""
            raw_title = u.get("title", "")
            title = (raw_title[:47] + "...") if len(raw_title) > 50 else raw_title
            lines.append(_pad(f"  • {u.get('type', '')}: {title} {conf_str}"))
        lines.append(_div())

        # Lore generation
        lg = report.get("lore_generation", {})
        mode = lg.get("mode", "")
        activity = lg.get("calendar_activity", "")
        es = lg.get("emotional_state", {})
        mood = es.get("mood", "")
        tension = lg.get("narrative_tension", "")
        featured = lg.get("featured_character", "")
        p1 = lg.get("post1", {})
        p2 = lg.get("post2", {})
        lore_status = "✅" if p1.get("char_count", 0) > 0 else "⚠️"
        lines.append(_pad(f"LORE GENERATION: {lore_status} {mode} mode, {activity}"))
        if mood or tension or featured:
            lines.append(_pad(f"  • Mood: {mood} | Tension: {tension}/10 | Featured: {featured}"))
        if p1.get("char_count"):
            lines.append(_pad(f"  • Post 1: {p1['char_count']:,} chars"))
        if p2.get("char_count"):
            lines.append(_pad(f"  • Post 2: {p2['char_count']:,} chars"))
        lines.append(_div())

        # Image generation
        ig = report.get("image_generation", {})
        img_entries = {k: v for k, v in ig.items() if k.startswith("post")}
        img_ok = sum(1 for v in img_entries.values() if v.get("status") == "success")
        img_total = len(img_entries)
        img_status = "✅" if img_ok == img_total and img_total > 0 else ("⚠️" if img_ok > 0 else "❌")
        img_attempts = " ".join(
            f"({v.get('attempts', 0)} attempt{'s' if v.get('attempts', 1) != 1 else ''} {k})"
            for k, v in sorted(img_entries.items())
        )
        lines.append(_pad(f"IMAGE GENERATION: {img_status} {img_ok}/{img_total} images {img_attempts}"))
        for key, v in sorted(img_entries.items()):
            st = v.get("status", "")
            t = v.get("generation_time_seconds", 0)
            kb = v.get("file_size_kb", 0)
            lines.append(_pad(f"  • {key}: {st} ({t} sec, {kb} KB)"))
        lines.append(_div())

        # Telegram posting
        tp = report.get("telegram_posting", {})
        tg_total = tp.get("total_messages_sent", 0)
        tg_failures = tp.get("failures", 0)
        tg_status = "✅" if tg_failures == 0 and tg_total > 0 else ("⚠️" if tg_total > 0 else "❌")
        chat_ids = set()
        for k, v in tp.items():
            if isinstance(v, dict):
                chat_ids.update(v.get("chat_ids", []))
        lines.append(_pad(
            f"TELEGRAM POSTING: {tg_status} {tg_total} message{'s' if tg_total != 1 else ''} "
            f"sent to {len(chat_ids)} channel{'s' if len(chat_ids) != 1 else ''}"
        ))
        for k, v in sorted((k, v) for k, v in tp.items() if isinstance(v, dict)):
            chars = v.get("character_count", 0)
            max_c = v.get("max_allowed", 0)
            st = v.get("status", "")
            ok = "✅" if st == "success" else "❌"
            mtype = v.get("type", "")
            lines.append(_pad(f"  • {k} ({mtype}): {chars}/{max_c} chars {ok}"))
        lines.append(_div())

        # Wiki updates
        wu = report.get("wiki_updates", {})
        w_processed = wu.get("processed", 0)
        w_merged = wu.get("smart_merged", 0)
        w_appended = wu.get("appended", 0)
        w_failed = wu.get("failed", 0)
        wiki_status = "✅" if w_failed == 0 else "⚠️"
        lines.append(_pad(
            f"WIKI UPDATES: {wiki_status} {w_processed} processed "
            f"({w_merged} smart-merged, {w_appended} appended)"
        ))
        for entry in wu.get("entries", [])[:5]:
            lines.append(_pad(f"  • {entry.get('wiki_section', entry.get('title', ''))}: 1 entry"))
        lines.append(_div())

        # Quality checks
        qc = report.get("quality_checks", {})
        all_passed = all(
            v.get("passed", True) for v in qc.values() if isinstance(v, dict)
        )
        qc_status = "✅ ALL PASSED" if all_passed else "⚠️ SOME FAILED"
        lines.append(_pad(f"QUALITY CHECKS: {qc_status}"))
        if "lore_coherence" in qc:
            lc = qc["lore_coherence"]
            p1s = lc.get("post1", 0)
            p2s = lc.get("post2", 0)
            avg = lc.get("average", 0)
            lines.append(_pad(f"  • Lore coherence: {avg}/10 (Post 1: {p1s}, Post 2: {p2s})"))
        if "data_integration" in qc:
            di = qc["data_integration"]
            lines.append(_pad(
                f"  • Data integration: {di.get('coverage_percent', 0)}% "
                f"({di.get('updates_woven', 0)}/{di.get('total_updates', 0)} updates woven)"
            ))
        if "consistency" in qc:
            lines.append(_pad(f"  • Consistency: {qc['consistency'].get('violations', 0)} violations"))
        if "plagiarism" in qc:
            uniq = "unique" if qc["plagiarism"].get("unique", True) else "not unique"
            lines.append(_pad(f"  • Plagiarism: {uniq}"))
        lines.append(_div())

        # Footer
        if filepath:
            lines.append(_pad(f"REPORT SAVED: {os.path.basename(filepath)}"))
        errors = report.get("errors", [])
        warnings = report.get("warnings", [])
        if errors:
            lines.append(_pad(f"ERRORS ({len(errors)}): {'; '.join(errors[:3])}"))
        if warnings:
            lines.append(_pad(f"WARNINGS ({len(warnings)}): {'; '.join(warnings[:3])}"))
        if report.get("workflow_run_url"):
            lines.append(_pad(f"WORKFLOW: {report['workflow_run_url']}"))
        lines.append("╚" + "═" * W + "╝")

        print("\n".join(lines))
