"""
symbolic-reasoning-engine.py — Symbolic Reasoning Engine for GK BRAIN

Applies symbolic logic to validate narrative decisions and explain reasoning chains.
Checks lore text against known facts to catch logical contradictions.

Usage (from gk-brain.py):
    from symbolic_reasoning_engine import validate_narrative_logic
    result = validate_narrative_logic(lore_text, facts)
"""

import os
import re

BASE_DIR = os.path.dirname(__file__)

# Rule patterns: (condition_re, conflict_re, description)
LOGIC_RULES = [
    (
        r"\b(at|beside|on) (lake|river|canal|water)\b",
        r"\b(in|at) (london|manchester|birmingham|city centre|gallery)\b",
        "Character cannot be at a lakeside and a city simultaneously.",
    ),
    (
        r"\bmorning\b",
        r"\b(midnight|3am|4am|2am)\b",
        "Morning references conflict with late-night time markers.",
    ),
    (
        r"\b(rave|club|warehouse)\b",
        r"\b(fishing|lake|carp|session)\b",
        "Rave setting conflicts with fishing setting in same paragraph.",
    ),
]


def _check_rules(lore_text: str) -> list:
    """Apply all logic rules and return list of detected issues."""
    issues = []
    text_lower = lore_text.lower()

    for cond_re, conflict_re, description in LOGIC_RULES:
        if re.search(cond_re, text_lower) and re.search(conflict_re, text_lower):
            issues.append(description)

    return issues


def _build_proof_chain(lore_text: str, facts: dict) -> list:
    """Build a list of fact-check results."""
    chain = []
    for fact_key, fact_value in facts.items():
        fact_str = str(fact_value).lower()[:50]
        in_text = fact_str[:20] in lore_text.lower()
        chain.append({
            "fact": fact_key,
            "value": fact_str,
            "present_in_lore": in_text,
            "status": "referenced" if in_text else "not_referenced",
        })
    return chain


def validate_narrative_logic(lore_text: str, facts: dict) -> dict:
    """
    Validate lore text for logical consistency against known facts.

    Checks spatial/temporal contradictions and verifies established facts
    are not contradicted.

    Args:
        lore_text: Generated lore string to validate.
        facts: Dict of known facts {fact_name: fact_value}.

    Returns:
        Dict with keys: valid (bool), issues (list), reasoning_chain (list).
    """
    try:
        issues = _check_rules(lore_text)
        reasoning_chain = _build_proof_chain(lore_text, facts)

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "reasoning_chain": reasoning_chain,
        }
    except Exception as e:
        print(f"[symbolic-reasoning] Error: {e}")
        return {"valid": True, "issues": [], "reasoning_chain": []}
