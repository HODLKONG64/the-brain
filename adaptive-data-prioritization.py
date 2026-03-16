"""
adaptive-data-prioritization.py - Adaptive Data Prioritization for GK BRAIN
Dynamically adjusts data importance weights based on real-time context.
"""
import os
BASE_DIR = os.path.dirname(__file__)
BLOCK_WEIGHTS = {"morning":{"fishing-real":10,"gkdata-real":5,"news-real":1,"rave-real":1,"graffiti-news-real":2},"afternoon":{"news-real":5,"gkdata-real":7,"crypto-real":5,"art-real":3,"fishing-real":2},"evening":{"rave-real":7,"graffiti-news-real":6,"gkdata-real":5,"art-real":4},"night":{"rave-real":10,"gkdata-real":5,"graffiti-news-real":4}}

def get_adaptive_weights(rule_ctx):
    """Return category weight dict for the current rule context."""
    try:
        block = rule_ctx.get("block","afternoon")
        return BLOCK_WEIGHTS.get(block, {"gkdata-real":5,"news-real":3,"fishing-real":3})
    except Exception as e:
        print(f"[adaptive-prioritization] {e}"); return {}
