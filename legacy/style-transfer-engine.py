"""
style-transfer-engine.py — Style Transfer Engine for GK BRAIN

Adapts narrative content for different platform voices.
Each platform has distinct formatting and tone requirements.

Usage (from gk-brain.py):
    from style_transfer_engine import get_style_hints
    hints = get_style_hints("telegram")
"""

import os

BASE_DIR = os.path.dirname(__file__)

PLATFORM_STYLES = {
    "telegram": {
        "voice": "casual, personal, energetic",
        "tense": "present or past, close and immediate",
        "perspective": "first person (I, my, we)",
        "length": "2-4 short paragraphs",
        "formatting": "short punchy paragraphs, line breaks for rhythm, sparse emoji use",
        "avoid": "formal language, third person, academic tone, long dense blocks",
        "example_tone": "Like a voice note transcribed. Raw, real, alive.",
    },
    "wiki": {
        "voice": "formal, encyclopedic, neutral",
        "tense": "past tense for events, present for ongoing facts",
        "perspective": "third person (the artist, he, the character)",
        "length": "structured sections with headers",
        "formatting": "MediaWiki markup, == Section == headers, bullet points, references",
        "avoid": "casual language, first person, opinions, real-time speculation",
        "example_tone": "Like a well-sourced Wikipedia article.",
    },
    "archive": {
        "voice": "reference format, dates prominent, factual",
        "tense": "past tense throughout",
        "perspective": "third person, neutral observer",
        "length": "concise, reference-dense",
        "formatting": "date: [YYYY-MM-DD HH:MM UTC], location, event, notes",
        "avoid": "narrative flourish, emotional language, speculation",
        "example_tone": "Like an official log entry or press release.",
    },
    "default": {
        "voice": "authentic, direct, grounded",
        "tense": "flexible",
        "perspective": "first or third person as appropriate",
        "length": "medium length, well-structured",
        "formatting": "standard paragraphs",
        "avoid": "clichés, filler phrases",
        "example_tone": "Clear, real, purposeful.",
    },
}


def get_style_hints(platform: str) -> str:
    """
    Return platform-specific style hints for content adaptation.

    Args:
        platform: Target platform name ('telegram', 'wiki', 'archive').

    Returns:
        Formatted style hints string for AI prompt.
    """
    try:
        style = PLATFORM_STYLES.get(platform.lower(), PLATFORM_STYLES["default"])

        lines = [f"=== STYLE GUIDE: {platform.upper()} ==="]
        for key, value in style.items():
            lines.append(f"  {key.capitalize()}: {value}")

        return "\n".join(lines)
    except Exception as e:
        print(f"[style-transfer] Error: {e}")
        return "Write in authentic, clear, direct language appropriate to the platform."
