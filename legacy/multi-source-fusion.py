"""
multi-source-fusion.py - Multi-Source Fusion for GK BRAIN

Fuses data from multiple sources into a unified, conflict-resolved narrative
context. Deduplicates across sources and resolves conflicts by confidence.

Usage (from gk-brain.py):
    from multi_source_fusion import fuse_updates
    fused = fuse_updates(updates)
"""

import os

BASE_DIR = os.path.dirname(__file__)

SIMILARITY_THRESHOLD = 0.60


def _content_fingerprint(update: dict) -> str:
    """Short fingerprint based on title/content for grouping similar updates."""
    text = (update.get("title", "") or update.get("content", "") or "")[:80]
    words = set(text.lower().split())
    significant = sorted(w for w in words if len(w) > 4)[:8]
    return "|".join(significant)


def _jaccard(fp_a: str, fp_b: str) -> float:
    """Jaccard similarity between two pipe-separated fingerprints."""
    try:
        set_a = set(fp_a.split("|"))
        set_b = set(fp_b.split("|"))
        if not set_a or not set_b:
            return 0.0
        intersection = set_a & set_b
        union = set_a | set_b
        return len(intersection) / len(union)
    except Exception:
        return 0.0


def _merge_group(group: list) -> dict:
    """Merge a group of similar updates into the highest-confidence one."""
    if not group:
        return {}
    best = max(group, key=lambda u: float(u.get("confidence", 0.5)))
    merged = dict(best)
    merged["merged_count"] = len(group)
    merged["sources"] = list({
        u.get("url", "") or u.get("source", "") for u in group if u.get("url") or u.get("source")
    })
    return merged


def fuse_updates(updates: list) -> list:
    """
    Deduplicate and conflict-resolve updates from multiple sources.

    Groups updates by topic similarity. When multiple sources report the same
    event, keeps the highest-confidence version. Returns fused list.

    Args:
        updates: List of validated update dicts.

    Returns:
        Fused, deduplicated list of update dicts.
    """
    if not updates:
        return []

    try:
        fingerprints = [_content_fingerprint(u) for u in updates]
        n = len(updates)
        assigned = [False] * n
        groups = []

        for i in range(n):
            if assigned[i]:
                continue
            group = [updates[i]]
            assigned[i] = True
            for j in range(i + 1, n):
                if assigned[j]:
                    continue
                similarity = _jaccard(fingerprints[i], fingerprints[j])
                if similarity >= SIMILARITY_THRESHOLD:
                    group.append(updates[j])
                    assigned[j] = True
            groups.append(group)

        fused = [_merge_group(g) for g in groups if g]
        print(f"[multi-source-fusion] Fused {n} updates into {len(fused)} unique items")
        return fused
    except Exception as e:
        print(f"[multi-source-fusion] Error: {e}")
        return updates
