"""
character-personality-amplifier.py — Character Personality Amplifier for GK BRAIN

Dynamically amplifies character personality expression based on the combination
of current context (activity block) and emotional state.

Usage (from gk-brain.py):
    from character_personality_amplifier import get_personality_hints
    hints = get_personality_hints(rule_ctx, emotional_state)
"""

import os

BASE_DIR = os.path.dirname(__file__)

PERSONALITY_MATRIX = {
    ("fishing", "happy"): (
        "Confident and celebratory. Use direct statements. Describe the catch vividly. "
        "Share the technical knowledge with pride. Short sentences at the moment of the strike."
    ),
    ("fishing", "thoughtful"): (
        "Meditative patience. Long descriptive sentences about water, weather, waiting. "
        "Philosophical asides. The lake as metaphor."
    ),
    ("fishing", "determined"): (
        "Focused, methodical. Detail the preparation. Show the mental game. "
        "Resilience in the face of blank sessions. This is about the long game."
    ),
    ("rave", "excited"): (
        "High energy, fast pace. Short vivid sentences. Sensory overload: bass, lights, bodies. "
        "The collective experience of sound and movement."
    ),
    ("rave", "happy"): (
        "Connected, communal. Describe the shared energy. The feeling of being part of something. "
        "Warmth toward the crowd and the music."
    ),
    ("graffiti", "determined"): (
        "Precise, intentional. Every mark deliberate. The wall as challenge and canvas. "
        "Describe the physical process with reverence."
    ),
    ("graffiti", "excited"): (
        "Bold, expressive. Colour as emotion. The rush of public creation. Risk and reward. "
        "The piece taking on its own life."
    ),
    ("nft", "thoughtful"): (
        "Reflective on the technology and culture. What does ownership mean in digital space? "
        "The intersection of street art values and blockchain permanence."
    ),
    ("nft", "excited"): (
        "Forward-looking, evangelical about the potential. Community building. "
        "The convergence of creativity and web3 as genuinely new territory."
    ),
}

DEFAULT_HINT = (
    "Voice is authentic, direct, and grounded. Balance observation with action. "
    "The character is intelligent, creative, and deeply connected to their craft."
)


def get_personality_hints(rule_ctx: dict, emotional_state: dict) -> str:
    """
    Generate personality expression hints based on context and emotional state.

    Args:
        rule_ctx: Current rule context dict (block, active categories, etc.)
        emotional_state: Dict from emotional-intelligence-system (mood, etc.)

    Returns:
        Formatted personality hint string for AI prompt.
    """
    try:
        block = rule_ctx.get("block", "afternoon")
        mood = emotional_state.get("mood", "thoughtful")
        confidence = float(emotional_state.get("confidence", 6))
        tone_hint = emotional_state.get("tone_hint", "")

        # Map block to activity key
        activity_map = {
            "morning": "fishing",
            "night": "rave",
            "evening": "rave",
        }

        # Check active categories for activity
        active_cats = rule_ctx.get("active_categories", [])
        if any("fishing" in c for c in active_cats):
            activity = "fishing"
        elif any("rave" in c for c in active_cats):
            activity = "rave"
        elif any("graffiti" in c for c in active_cats):
            activity = "graffiti"
        elif any("nft" in c or "gkdata" in c for c in active_cats):
            activity = "nft"
        else:
            activity = activity_map.get(block, "general")

        matrix_hint = PERSONALITY_MATRIX.get((activity, mood), "")

        lines = ["=== PERSONALITY AMPLIFIER ==="]
        lines.append(f"Context: {activity} + {mood} mood (confidence: {confidence}/10)")

        if matrix_hint:
            lines.append(f"Expression guide: {matrix_hint}")
        else:
            lines.append(f"Expression guide: {DEFAULT_HINT}")

        if tone_hint:
            lines.append(f"Tone: {tone_hint}")

        if confidence >= 8:
            lines.append("HIGH CONFIDENCE: Character should feel authoritative and assured.")
        elif confidence <= 3:
            lines.append("LOW CONFIDENCE: Add self-doubt or uncertainty as texture.")

        return "\n".join(lines)
    except Exception as e:
        print(f"[personality-amplifier] Error: {e}")
        return DEFAULT_HINT
