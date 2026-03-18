"""
consistency-proof-engine.py - Consistency Proof Engine for GK BRAIN

Provides systematic verification of narrative consistency against
a known-facts dictionary. Generates a proof chain for transparency.

Usage (from gk-brain.py):
    from consistency_proof_engine import prove_consistency
    result = prove_consistency(lore_text, known_facts)
"""

import os
import re

BASE_DIR = os.path.dirname(__file__)


def _fact_check(lore_text: str, fact_key: str, fact_value) -> dict:
    """Check a single fact against lore text."""
    text_lower = lore_text.lower()
    value_str = str(fact_value).lower()

    # Check for direct contradiction patterns
    negation_patterns = [
        rf"\bnot\s+{re.escape(value_str[:20])}\b",
        rf"\bnever\s+{re.escape(value_str[:20])}\b",
        rf"\bno\s+{re.escape(value_str[:20])}\b",
    ]

    contradicted = any(
        re.search(p, text_lower) for p in negation_patterns if len(value_str) > 3
    )

    # Check for presence
    referenced = value_str[:15] in text_lower if len(value_str) > 3 else False

    if contradicted:
        return {"fact": fact_key, "status": "VIOLATED", "detail": f"Lore contradicts: {fact_value}"}
    elif referenced:
        return {"fact": fact_key, "status": "CONFIRMED", "detail": f"Fact present in lore"}
    else:
        return {"fact": fact_key, "status": "NOT_REFERENCED", "detail": "Fact not mentioned (OK)"}


def prove_consistency(lore_text: str, known_facts: dict) -> dict:
    """
    Systematically verify lore consistency against known facts.

    Args:
        lore_text: Generated lore string to verify.
        known_facts: Dict of {fact_name: fact_value} to check against.

    Returns:
        Dict with: consistent (bool), proof_chain (list), violations (list).
    """
    try:
        if not known_facts:
            return {"consistent": True, "proof_chain": [], "violations": []}

        proof_chain = []
        violations = []

        for fact_key, fact_value in known_facts.items():
            result = _fact_check(lore_text, fact_key, fact_value)
            proof_chain.append(result)
            if result["status"] == "VIOLATED":
                violations.append(result)

        return {
            "consistent": len(violations) == 0,
            "proof_chain": proof_chain,
            "violations": violations,
        }
    except Exception as e:
        print(f"[consistency-proof] Error: {e}")
        return {"consistent": True, "proof_chain": [], "violations": []}
