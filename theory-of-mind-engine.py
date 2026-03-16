"""
theory-of-mind-engine.py - Theory of Mind Engine for GK BRAIN
Models social dynamics and how others perceive the artist.
"""
import os
BASE_DIR = os.path.dirname(__file__)
KEYWORDS = {"fishing":["carp","lake","fish","session","catch"],"rave":["rave","bass","crowd","warehouse"],"art":["mural","graffiti","gallery","paint"],"nft":["nft","token","mint","blockchain"]}

def get_social_context(rule_ctx, lore_history=""):
    """Return string describing current social perception state."""
    try:
        lh = lore_history.lower()
        lines = ["=== SOCIAL CONTEXT (how others perceive the artist) ==="]
        if any(w in lh for w in KEYWORDS["fishing"]): lines.append("• Fishing community: respectful — the artist has put in the hours and it shows.")
        if any(w in lh for w in KEYWORDS["rave"]): lines.append("• Rave crowd: familiar — a known face in the underground circuit.")
        if any(w in lh for w in KEYWORDS["art"]): lines.append("• Art collective: interested — the work is being noticed by other creatives.")
        if any(w in lh for w in KEYWORDS["nft"]): lines.append("• NFT community: engaged — collectors and holders are paying attention.")
        lines.append("• Lady-INK: curious — watching the artist's evolution with genuine interest.")
        lines.append("\nINSTRUCTION: Let these social perceptions subtly shape how the character carries themselves.")
        return "\n".join(lines)
    except Exception as e:
        print(f"[theory-of-mind] {e}"); return "The character moves through the world with earned respect."
