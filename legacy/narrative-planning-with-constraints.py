"""
narrative-planning-with-constraints.py - Narrative Planning With Constraints for GK BRAIN
Generates narrative plans while respecting hard content and style constraints.
"""
import os
BASE_DIR = os.path.dirname(__file__)
HARD_CONSTRAINTS = ["MAX 10% of text should be direct data quotes — weave, don't paste.","PG-13 content — authentic edge allowed, explicit content not permitted.","No epoch mixing — stay in contemporary UK timeframe.","Character is the lens — all data passes through personal experience.","No corporate speak, clickbait language, or hollow hype.","Real events may be referenced but not fabricated as fact."]

def apply_constraints(prompt_context):
    """Apply hard constraints to prompt context dict. Returns enriched context."""
    try:
        enriched = dict(prompt_context)
        enriched["hard_constraints"] = HARD_CONSTRAINTS
        enriched["constraint_summary"] = "Apply all constraints. They are non-negotiable."
        flags = []
        lore = prompt_context.get("lore_text","")
        if "[INSERT]" in lore or "TODO" in lore: flags.append("placeholder_text_detected")
        enriched["constraint_flags"] = flags
        return enriched
    except Exception as e:
        print(f"[narrative-constraints] {e}"); return prompt_context
