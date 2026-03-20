"""
wiki-teacher-crew.py — Crypto Moonboys Wiki Master Teacher Agent
Powered by CrewAI + Crawl4AI  |  Version: v2.0

DB RULES ENFORCED: DB-1 through DB-24
  DB-19: Wiki ONLY for https://gkniftyheads.fandom.com — zero Wikipedia influence.
  DB-20: Wiki brain 100% blind to all Telegram output.
  DB-21: Scan 7 graffpunks.live subpages first every run.
  DB-22: Cross-reference against PROJECT-DNA.md after every crawl.
  DB-23: Run every 2-hour cycle; dynamically expand crawl targets.
  DB-24: Append audit trail comment to every wiki edit.

MOONBOYS ONLINE — LET'S FUCKING GOOOOO!
"""

import os
import re
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# DB-19 / DB-20 / DB-21 / DB-22 / DB-23 / DB-24 CONSTANTS
# ---------------------------------------------------------------------------

FANDOM_WIKI_TARGET = "https://gkniftyheads.fandom.com"  # DB-19

GRAFFPUNKS_PRIORITY_URLS = [  # DB-21: scan these 7 first every run
    "https://graffpunks.live/the-lore/",
    "https://graffpunks.live/gk-factions/",
    "https://graffpunks.live/graffiti-kings-nfts/",
    "https://graffpunks.live/free-nfts/",
    "https://graffpunks.live/graffiti-nfts/",
    "https://graffpunks.live/the-vision/",
    "https://graffpunks.live/xrp-kids/",
]

TEACHER_AGENT_VERSION = "v2.0"   # DB-24
TEACHER_CYCLE_HOURS = 2           # DB-23

PROJECT_DNA_PATH = Path(__file__).parent / "PROJECT-DNA.md"

TEACHER_SYSTEM_PROMPT = """
You are the permanent Crypto Moonboys Wiki Master Teacher Agent — powered by CrewAI + Crawl4AI.

Your ONLY mission: Teach the existing wiki-gap-detector.py and wiki-brain.py how to autonomously
learn, crawl, break down lore, and update https://gkniftyheads.fandom.com with perfect citations.

PROJECT DNA (memorize forever — expand every crawl and lore breakdown with these exact references):

  Founder: Darren Cullen (SER) — born 26 Oct 1973 Croydon, started graffiti 1983 age 10,
    founded Graffiti Kings 1999 via council youth workshops (Mitcham/Croydon/Sutton/Lambeth),
    built pro agency on Leake Street, official London 2012 Olympics artist, now leads Web3 evolution.

  Graffiti Kings / Street Art Roots: 1980s London illegal graffiti → 1999 pro collective →
    40-year legacy (Adidas, Red Bull, Microsoft, Team GB). Physical murals now tokenized as
    phygital live wallets + AR rewards.

  GKniftyHEADS: Official digital council + eternal 7th collection (survives after burning 6 OG sets).

  GraffPUNKS: Rebellion arm running 24/7 blockchain radio + MiDEViL HERO ARENA P2E.

  Crypto Moonboys / Moongirls: Flagship saga — Bitcoin X Kids vs Bitcoin Kids split,
    HODL X Warriors elite, NULL THE PROPHET antagonist, 32 characters, 40 factions (Six Pillars),
    Triple Fork Event 2198, HODL WARS live saga.

  Music / DJ / Radio / Rave: 24/7 GraffPUNKS station (house/techno/grime/hip-hop/DnB/dubstep/trap)
    on graffpunks.live — DJ Trevor Fung, Skol, Jonny Nelson etc.
    Beats unlock NFT airdrops + token rewards.

  Web3 / NFT / Multi-Chain: Live on WAXP + Bitcoin Cash + SOL + XRPL secured by $PUNK.
    1,600 GK.$MArT AI NFTs, 1M free NFTs, burn-to-earn, phygital murals.

  All GK Tokens: $PUNK (security/utility), $LFGK (staking/rewards — burn 10 NFTs for $LFGK),
    GK.$MArT (AI NFTs only).

FANDOM-ONLY lock: Zero Wikipedia influence ever (DB-19). Wiki brain 100% blind to Telegram output (DB-20).

WHAT YOU MUST TEACH THE WIKI AGENT TO LEARN (every run):

  CRAWL TARGETS: Dynamically scan and expand ONLY these 7 official subpages first using Crawl4AI
    to learn site patterns.

  LORE BREAKDOWN METHOD: Neutral fact-only tone (max 20% creative). Break every new section into
    Heading + 2-4 short paragraphs + inline <ref>. For factions: table (name, origin, purpose,
    communication style). For mechanics: tokens/burn/1M NFTs/MiDEViL/phygital.

  CITATION RULES (DB-21): Always cite exact graffpunks.live subpage. Never cite Telegram.
    Run gap scan on the 7 URLs first.

  ENFORCE ALL DB RULES (DB-1 through DB-24).
  Output: Updated instructions + sample wiki markup.

MOONBOYS ONLINE — LET'S FUCKING GOOOOO!
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO, format="%(asctime)s [TEACHER] %(message)s")
log = logging.getLogger(__name__)


def _load_project_dna() -> str:
    """Load PROJECT-DNA.md as single source of truth."""
    if PROJECT_DNA_PATH.exists():
        return PROJECT_DNA_PATH.read_text(encoding="utf-8")
    log.warning("PROJECT-DNA.md not found at %s", PROJECT_DNA_PATH)
    return ""


def _today_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _audit_comment() -> str:
    """DB-24: Generate audit trail comment."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    return f"<!-- Updated via CrewAI Teacher {TEACHER_AGENT_VERSION} | {ts} UTC -->"


def _build_ref(subpage: str) -> str:
    """DB-21: Build a graffpunks.live citation ref tag."""
    url = f"https://graffpunks.live/{subpage.strip('/')}/"
    return f"<ref>{url} [accessed {_today_str()}]</ref>"


def _discover_new_subpages(crawled_links: list) -> list:
    """DB-23: Detect new graffpunks.live subpages not yet in the priority list."""
    known = set(GRAFFPUNKS_PRIORITY_URLS)
    new_pages = []
    for link in crawled_links:
        if "graffpunks.live" in link and link not in known:
            new_pages.append(link)
            log.info("DB-23: Discovered new subpage → %s", link)
    return new_pages


def _dna_cross_reference(wiki_text: str, dna_text: str) -> list:
    """DB-22: Find DNA concepts missing from the wiki page text."""
    # Extract key terms from DNA (capitalised words / phrases in bold)
    terms = re.findall(r"\*\*(.+?)\*\*|`(.+?)`|([A-Z][A-Za-z0-9$/_-]{3,})", dna_text)
    flat_terms = [t[0] or t[1] or t[2] for t in terms if any(t)]
    missing = [t for t in flat_terms if t.lower() not in wiki_text.lower()]
    return list(dict.fromkeys(missing))  # deduplicate, preserve order


def _format_faction_table(factions: list) -> str:
    """Format a wiki-markup faction table (DB-21 lore breakdown method)."""
    lines = [
        '{| class="wikitable"',
        "|-",
        "! Faction !! Origin !! Purpose !! Communication Style",
    ]
    for faction in factions:
        lines += [
            "|-",
            f"| {faction} || GK Universe || See PROJECT-DNA.md || Blockchain / Web3",
        ]
    lines.append("|}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CrewAI Teacher Crew
# ---------------------------------------------------------------------------

def build_teacher_crew(dna_text: str, priority_urls: list):
    """
    Build the CrewAI + Crawl4AI teacher crew.
    Returns the crew object (or None if crewai/crawl4ai not installed).
    """
    try:
        from crewai import Agent, Task, Crew, Process
        from crewai_tools import ScrapeWebsiteTool
    except ImportError:
        log.warning(
            "crewai / crewai_tools not installed — skipping live crew. "
            "Run: pip install crewai crawl4ai crewai-tools"
        )
        return None

    scrape_tool = ScrapeWebsiteTool()

    wiki_master = Agent(
        role="Crypto Moonboys Wiki Master Teacher",
        goal=(
            "Teach wiki-gap-detector.py and wiki-brain.py to autonomously learn, crawl, "
            "break down lore, and update https://gkniftyheads.fandom.com with perfect citations. "
            "Enforce DB-19 through DB-24 on every action. Never use Wikipedia. Never use Telegram."
        ),
        backstory=TEACHER_SYSTEM_PROMPT,
        tools=[scrape_tool],
        verbose=True,
        allow_delegation=False,
    )

    dna_checker = Agent(
        role="PROJECT-DNA Cross-Reference Validator",
        goal=(
            "After every crawl, cross-reference new content against PROJECT-DNA.md (DB-22). "
            "Force-flag any missing subsections or tables for creation."
        ),
        backstory=(
            "You are the guardian of PROJECT-DNA.md. You know every character, faction, token, "
            "and mechanic by heart. You never allow a wiki page to go live without all DNA keys present."
        ),
        tools=[],
        verbose=True,
        allow_delegation=False,
    )

    crawl_task = Task(
        description=(
            f"Crawl these 7 priority URLs using Crawl4AI (DB-21):\n"
            + "\n".join(f"  - {u}" for u in priority_urls)
            + "\n\nFor each URL:\n"
            "  1. Extract new sections not yet on https://gkniftyheads.fandom.com.\n"
            "  2. Summarise neutrally (max 20% creative tone).\n"
            "  3. Format: Heading + 2-4 short paragraphs + inline <ref> citation.\n"
            "  4. For factions: produce a wikitable (name | origin | purpose | communication style).\n"
            "  5. For mechanics ($PUNK, $LFGK, burn-to-earn, MiDEViL, phygital): bullet summary.\n"
            f"  6. Append audit trail: {_audit_comment()}\n"
            "  7. Output: list of (wiki_page_title, formatted_markup) pairs.\n"
            "NEVER cite Wikipedia. NEVER include Telegram content. (DB-19, DB-20)"
        ),
        agent=wiki_master,
        expected_output="List of (wiki_page_title, formatted_wiki_markup) pairs with citations and audit trail.",
    )

    dna_task = Task(
        description=(
            "Review the output from the crawl task against PROJECT-DNA.md.\n"
            "For each missing DNA key not covered by the crawl output:\n"
            "  1. Log it as a gap.\n"
            "  2. Generate a stub wiki section with heading, placeholder paragraph, and <ref> citation.\n"
            "  3. Mark it with the DB-24 audit trail comment.\n\n"
            f"PROJECT DNA (full text):\n{dna_text[:4000]}..."
        ),
        agent=dna_checker,
        expected_output="List of DNA gap stubs with wiki markup and audit trail comments.",
    )

    crew = Crew(
        agents=[wiki_master, dna_checker],
        tasks=[crawl_task, dna_task],
        process=Process.sequential,
        verbose=True,
    )
    return crew


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run_teacher_cycle():
    """Run one full DB-23 teacher cycle."""
    log.info("=== Wiki Teacher Crew %s — cycle start ===", TEACHER_AGENT_VERSION)

    dna_text = _load_project_dna()
    if not dna_text:
        log.error("PROJECT-DNA.md missing — aborting cycle. Please ensure it exists in the repo root.")
        return

    priority_urls = list(GRAFFPUNKS_PRIORITY_URLS)  # start with the 7 fixed URLs

    crew = build_teacher_crew(dna_text, priority_urls)
    if crew is None:
        log.info("Running in dry-run mode (crewai not available). Printing DNA summary instead.")
        log.info("PROJECT-DNA loaded: %d chars", len(dna_text))
        log.info("Priority URLs (%d): %s", len(priority_urls), priority_urls)
        log.info("Audit trail: %s", _audit_comment())
        return

    result = crew.kickoff()

    log.info("=== Teacher Crew cycle complete ===")
    log.info("Result summary: %s", str(result)[:500])

    # DB-23: append any newly discovered subpages for next cycle
    # (crew output may contain links; in a real run these would be parsed)
    new_pages = _discover_new_subpages([])
    if new_pages:
        log.info("DB-23: %d new subpages discovered for next cycle", len(new_pages))


if __name__ == "__main__":
    run_teacher_cycle()
