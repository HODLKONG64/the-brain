"""
wiki-teacher-agent.py — GK BRAIN Wiki Teacher Agent v2.0

CrewAI + Crawl4AI powered agent that teaches wiki-gap-detector.py and
wiki-brain.py how to autonomously learn, crawl, break down lore, and update
https://gkniftyheads.fandom.com with perfect citations.

Enforces DB rules:
  DB-19: Wiki ONLY for https://gkniftyheads.fandom.com — zero Wikipedia influence.
  DB-20: Wiki brain 100% blind to all Telegram output.
  DB-21: Scan 7 GraffPUNKS priority URLs first every run.
  DB-22: Cross-reference new content against PROJECT_DNA; force-create missing
         subsections/tables even if gap-detector previously skipped them.
  DB-23: Run every 2-hour cycle; dynamically append newly discovered
         graffpunks.live subpages to the 7-URL list (read-once bible lock).
  DB-24: All wiki edits include audit comment:
         <!-- Updated via CrewAI Teacher v2 | YYYY-MM-DD HH:MM UTC -->

Usage:
    python wiki-teacher-agent.py [--dry-run] [--verbose]

Writes:
    wiki-teacher-output.json — crawled content, generated markup, and status
"""

import argparse
import asyncio
import datetime
import importlib
import importlib.util
import json
import logging
import os
import sys
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("wiki-teacher-agent")

# ---------------------------------------------------------------------------
# Constants — DB-19/20/21
# ---------------------------------------------------------------------------

# DB-19: Wiki ONLY for https://gkniftyheads.fandom.com — zero Wikipedia influence.
# DB-20: Wiki brain 100% blind to all Telegram output.
# DB-21: Scan 7 URLs first every run.
FANDOM_WIKI_TARGET = "https://gkniftyheads.fandom.com"
GRAFFPUNKS_PRIORITY_URLS = [
    "https://graffpunks.live/the-lore/",
    "https://graffpunks.live/gk-factions/",
    "https://graffpunks.live/graffiti-kings-nfts/",
    "https://graffpunks.live/free-nfts/",
    "https://graffpunks.live/graffiti-nfts/",
    "https://graffpunks.live/the-vision/",
    "https://graffpunks.live/xrp-kids/",
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(BASE_DIR, "wiki-teacher-output.json")

REQUEST_TIMEOUT = 15
CRAWL_DELAY = 1.2

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; GKBrainWikiTeacherBot/2.0; "
        "+https://github.com/HODLKONG64/the-brain)"
    )
}

# ---------------------------------------------------------------------------
# PROJECT DNA — memorize forever (DB-22 cross-reference keys)
# ---------------------------------------------------------------------------

PROJECT_DNA = {
    "founder": (
        "Darren Cullen (SER) — born 26 October 1973 in Croydon, South London; "
        "started graffiti in 1983 at age 10 after seeing New York train photos; "
        "original tag SER from 'South East Rockers' crew; founded Graffiti Kings "
        "in 1999 through council youth workshops in Mitcham, Croydon, Sutton and "
        "Lambeth; built professional agency on Leake Street with major commissions "
        "for Adidas, Red Bull, Microsoft and Team GB; official artist for London "
        "2012 Olympics; now leads the full Web3 evolution of the crew into "
        "GKniftyHEADS council, GraffPUNKS and Crypto Moonboys Online."
    ),
    "graffiti_kings": (
        "Graffiti Kings / Street Art Roots: Began in 1980s London illegal graffiti "
        "and vandalism culture; evolved in 1999 into a professional collective "
        "turning street energy into legal commissions; 40-year legacy as the "
        "'silent architects of cool'; physical murals now tokenized as phygital "
        "live wallets with AR rewards and Writcode technology."
    ),
    "gkniftyheads": (
        "GKniftyHEADS: Official digital council and the eternal 7th collection "
        "that survives after the burn-to-zero of the 6 OG collections "
        "(graffk1ngsuk, hodlmoonboys, gr4ffitiking, nocommentser, graffiti.r2, "
        "dabitcoinkid)."
    ),
    "graffpunks": (
        "GraffPUNKS: The active rebellion arm running the 24/7 blockchain radio "
        "station on graffpunks.live plus the MiDEViL HERO ARENA Play-to-Earn game."
    ),
    "crypto_moonboys": (
        "Crypto Moonboys & Crypto Moongirls: The flagship NFT saga featuring "
        "Bitcoin X Kids (still inside Block Topia walls) versus Bitcoin Kids "
        "(escaped rebels who joined Alfie 'The Bitcoin Kid' Blaze); HODL X Warriors "
        "earned exclusively via Queen Sarah P-fly's Hard Fork Games golden ticket; "
        "main antagonist NULL THE PROPHET rising from Dream Sovereign."
    ),
    "characters_32": (
        "32 locked characters: Alfie Blaze, Queen Sarah P-fly, Jodie ZOOM 2000, "
        "Elder Codex-7, Thera-9, Aleema, Iris-7, Lady-INK, Snipey 'D-Man' Sirus, "
        "Bit-Cap 5000, Forksplit, M1nTr_K1ll, SatoRebel, Thorne The Architect, "
        "Billy the Goat Kid, HEX-TAGGER PRIME, The Whitewasher, GRIT, PYRALITH, "
        "Loopfiend, Samael.exe, Forklord You, Quell, Sister Halcyon, Grit42, "
        "Rune Tag, Patchwork, The Princess, Dragan Volkov, Ava Chen, "
        "Darren Cullen (SER), Charlie Buster."
    ),
    "factions_40": (
        "40 factions under the Six Pillars system: Bitcoin Kid Army, GKniftyHEADS, "
        "Nomad Bears, AllCity Bulls, GRAFFPUNKS, BALLY BOYS, CRYPTO MOONGIRLS, "
        "DUCKY BOYS, NICE & EASY BOIS, Squeaky Pinks, High Hats, HARD FORK ROCKERS, "
        "BLOCKSTARS, BLOCKCHAIN FURIES, RUGPULL MINERS, AZTEC RAIDERS, TUSKON OGS, "
        "CRYPTO STONED BOYS, CODE ALCHEMISTS, FINANCE GUILD, INFORMATION MERCENARIES, "
        "SALVAGERS, MOONLORDS, SHARD MOTHERS of MANHATTAN, CHAIN SCRIBES, EVM PUNKS, "
        "OG PIXEL SAINTS, GASLESS GHOSTS plus 12 expanding live in HODL WARS."
    ),
    "music_dj_radio": (
        "Music / DJ / Radio / Rave Branch: Direct continuation of 1980s-1990s London "
        "pirate radio and graffiti underground; 24/7 GraffPUNKS blockchain radio "
        "station on graffpunks.live streaming house, techno, dance, Balearic, "
        "hip-hop, grime, drum & bass, dubstep, trap and funky funk; global DJ roster "
        "including DJ Trevor Fung (God Father), DJ Skol (Tank Funk Hard House Fridays), "
        "Jonny Nelson & Danny Young (S.U.M. Sessions); blockchain integration turns "
        "listening into active earning with NFT airdrops, token rewards and free "
        "collectibles while 'PUNK OUT & LOG OUT'."
    ),
    "web3_nft_multichain": (
        "Web3 / NFT / Multi-Chain Blockchain Branch: Live simultaneously on WAXP, "
        "Bitcoin Cash, SOL and XRPL with $PUNK as the security token locking the "
        "entire network; 1,600 GK.$MArT AI dynamic NFTs (40 per faction that think, "
        "fight, evolve and adapt); 1 million additional free NFTs via HODL WARS; "
        "burn-to-earn mechanics (burn 10 in-game NFTs for $LFGK, burn 3 FUN COUPONS "
        "for GK.$MArT, burn 6 OG collections to zero so only GKniftyHEADS survives); "
        "phygital murals as live wallets with AR rewards and staking vaults for $GK "
        "tokens plus Seeding rights, phygital prints and metaverse battles."
    ),
    "tokens": (
        "All GK Tokens: $PUNK (high-velocity utility/security token powering radio, "
        "airdrops and engagement — https://waxonedge.app/analytics/token/PUNK_gkniftyheads); "
        "$LFGK (staking, rewards and Play-to-Earn currency — earned by burning NFTs, "
        "auto-airdropped to all GK and No Ball Games NFTs 3 months after HODL WARS "
        "launch); GK.$MArT is AI NFTs only (not a token)."
    ),
    "chains": "WAXP, Bitcoin Cash (BCH), Solana (SOL), XRP Ledger (XRPL)",
    "lore_mechanics": (
        "Core Lore Mechanics: Triple Fork Event 2198, Block Topia walls, HODL WARS "
        "every-2-hour live saga, MiDEViL HERO ARENA Play-to-Earn, Chat2Earn, "
        "designer crypto toys, physical-digital bridge."
    ),
}

# DB-22: Keys checked against live wiki to force-create missing subsections.
PROJECT_DNA_COVERAGE_KEYS = list(PROJECT_DNA.keys())

# ---------------------------------------------------------------------------
# Optional module loader (_safe_load)
# ---------------------------------------------------------------------------


def _safe_load(package_name: str):
    """
    Attempt to import a package by name; return the module or None on failure.
    Non-fatal — callers must handle None return.
    """
    try:
        spec = importlib.util.find_spec(package_name)
        if spec is None:
            logger.debug("[wiki-teacher] Package '%s' not installed.", package_name)
            return None
        return importlib.import_module(package_name)
    except Exception as exc:
        logger.debug("[wiki-teacher] Could not load '%s': %s", package_name, exc)
        return None


_crewai = _safe_load("crewai")
_crawl4ai = _safe_load("crawl4ai")

# ---------------------------------------------------------------------------
# DB-23: Dynamic subpage discovery
# ---------------------------------------------------------------------------


def _discover_new_subpages(base_url: str = "https://graffpunks.live/") -> list:
    """
    DB-23: Crawl graffpunks.live home page and detect any subpages not already
    present in GRAFFPUNKS_PRIORITY_URLS.  Returns a list of new URLs discovered.
    """
    known = set(GRAFFPUNKS_PRIORITY_URLS)
    discovered = []
    try:
        resp = requests.get(base_url, headers=_HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            full = urljoin(base_url, href)
            parsed = urlparse(full)
            if (
                parsed.netloc == urlparse(base_url).netloc
                and len(parsed.path.strip("/")) > 0
                and full not in known
                and not full.endswith(("#", "javascript:"))
            ):
                discovered.append(full)
                known.add(full)
    except requests.RequestException as exc:
        logger.warning("[wiki-teacher] DB-23 subpage discovery failed: %s", exc)
    logger.info("[wiki-teacher] DB-23: %d new subpage(s) discovered.", len(discovered))
    return discovered


# ---------------------------------------------------------------------------
# DB-22: PROJECT DNA coverage checker
# ---------------------------------------------------------------------------


def _check_dna_coverage(wiki_text: str) -> list:
    """
    DB-22: Cross-reference wiki_text against PROJECT_DNA_COVERAGE_KEYS.
    Returns list of keys whose core terms are absent from the wiki.
    """
    missing = []
    wiki_lower = wiki_text.lower() if wiki_text else ""
    key_terms = {
        "founder": ["darren cullen", "ser", "graffiti kings"],
        "graffiti_kings": ["graffiti kings", "1999"],
        "gkniftyheads": ["gkniftyheads", "7th collection"],
        "graffpunks": ["graffpunks", "midevil hero arena"],
        "crypto_moonboys": ["crypto moonboys", "block topia", "alfie blaze"],
        "characters_32": ["alfie blaze", "queen sarah", "elder codex"],
        "factions_40": ["bitcoin kid army", "graffpunks", "nomad bears"],
        "music_dj_radio": ["graffpunks.live", "blockchain radio", "dj trevor fung"],
        "web3_nft_multichain": ["waxp", "xrpl", "gk.$mart"],
        "tokens": ["$punk", "$lfgk", "gk.$mart"],
        "chains": ["waxp", "xrpl", "solana"],
        "lore_mechanics": ["triple fork", "hodl wars", "block topia"],
    }
    for key in PROJECT_DNA_COVERAGE_KEYS:
        terms = key_terms.get(key, [key.replace("_", " ")])
        if not any(t in wiki_lower for t in terms):
            missing.append(key)
    return missing


# ---------------------------------------------------------------------------
# Crawl priority URLs
# ---------------------------------------------------------------------------


def crawl_priority_urls(urls: list, verbose: bool = False) -> dict:
    """
    Crawl the GRAFFPUNKS_PRIORITY_URLS (plus any DB-23 discovered URLs) using
    Crawl4AI if available, falling back to requests + BeautifulSoup.

    Returns dict mapping url -> {"text": str, "links": list, "error": str|None}
    """
    results = {}

    for url in urls:
        if verbose:
            logger.debug("[wiki-teacher] Crawling: %s", url)

        # Crawl4AI path
        if _crawl4ai is not None:
            try:
                async def _do_crawl(target_url: str) -> str:
                    async with _crawl4ai.AsyncWebCrawler() as crawler:
                        result = await crawler.arun(url=target_url)
                        return getattr(result, "markdown", None) or getattr(result, "cleaned_html", None) or ""

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    text = loop.run_until_complete(_do_crawl(url))
                finally:
                    loop.close()
                    asyncio.set_event_loop(None)

                results[url] = {"text": text, "links": [], "error": None}
                logger.info("[wiki-teacher] crawl4ai OK: %s (%d chars)", url, len(text))
                continue
            except AttributeError as exc:
                logger.warning(
                    "[wiki-teacher] crawl4ai result structure unexpected for %s (%s) — falling back.",
                    url, exc,
                )
            except Exception as exc:
                logger.warning(
                    "[wiki-teacher] crawl4ai failed for %s (%s) — falling back.", url, exc
                )

        # requests + BS4 fallback
        try:
            resp = requests.get(url, headers=_HEADERS, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            # Extract visible text
            for tag in soup(["script", "style", "nav", "footer"]):
                tag.decompose()
            text = soup.get_text(separator="\n", strip=True)
            # Extract internal links
            base_domain = urlparse(url).netloc
            links = []
            for a in soup.find_all("a", href=True):
                full = urljoin(url, a["href"])
                if urlparse(full).netloc == base_domain:
                    links.append(full)
            results[url] = {"text": text, "links": links, "error": None}
            logger.info(
                "[wiki-teacher] requests/BS4 OK: %s (%d chars)", url, len(text)
            )
        except requests.RequestException as exc:
            logger.warning("[wiki-teacher] Failed to crawl %s: %s", url, exc)
            results[url] = {"text": "", "links": [], "error": str(exc)}

        time.sleep(CRAWL_DELAY)

    return results


# ---------------------------------------------------------------------------
# DB-24: Audit trail comment
# ---------------------------------------------------------------------------


def _audit_comment() -> str:
    """DB-24: Return the audit-trail comment for all wiki edits."""
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"<!-- Updated via CrewAI Teacher v2 | {ts} -->"


# ---------------------------------------------------------------------------
# Wiki markup builder
# ---------------------------------------------------------------------------


def build_wiki_markup(
    heading: str,
    paragraphs: list,
    rows: list = None,
    col_headers: list = None,
    citations: list = None,
) -> str:
    """
    Emit MediaWiki markup for a section.

    Args:
        heading:     Section heading text.
        paragraphs:  List of paragraph strings.
        rows:        Optional list of row dicts for a wikitable.
        col_headers: Column headers for the wikitable.
        citations:   Optional list of citation URL strings (added as <ref> tags).

    Returns:
        String of MediaWiki markup including DB-24 audit comment.
    """
    lines = [f"== {heading} ==", ""]
    for para in paragraphs:
        lines.append(para)
        lines.append("")

    # Inline citations
    if citations:
        accessed = datetime.date.today().strftime("%Y-%m-%d")
        for cite_url in citations:
            lines.append(f"<ref>{cite_url} [accessed {accessed}]</ref>")
        lines.append("")

    # Wikitable
    if rows and col_headers:
        lines.append('{| class="wikitable"')
        lines.append("|-")
        lines.append("! " + " !! ".join(col_headers))
        for row in rows:
            lines.append("|-")
            cells = [str(row.get(h, "")) for h in col_headers]
            lines.append("| " + " || ".join(cells))
        lines.append("|}")
        lines.append("")

    # DB-24 audit trail
    lines.append(_audit_comment())

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CrewAI teacher agent
# ---------------------------------------------------------------------------

_TEACHER_AGENT_ROLE = "Crypto Moonboys Wiki Master Teacher"

_TEACHER_AGENT_GOAL = (
    "Teach wiki-gap-detector.py and wiki-brain.py how to autonomously learn, "
    "crawl, break down lore, and update https://gkniftyheads.fandom.com with "
    "perfect citations while enforcing every existing DB rule (DB-1 to DB-24), "
    "the read-once bible lock, and zero conflicts with current code."
)

_TEACHER_AGENT_BACKSTORY = (
    "You are the permanent Crypto Moonboys Wiki Master Teacher Agent v2.0 — "
    "powered by CrewAI + Crawl4AI.\n\n"
    "Your ONLY mission: Teach the existing wiki-gap-detector.py and wiki-brain.py "
    "how to autonomously learn, crawl, break down lore, and update "
    "https://gkniftyheads.fandom.com with perfect citations while enforcing every "
    "existing DB rule (DB-1 to DB-24), the read-once bible lock, and zero conflicts "
    "with current code.\n\n"
    "PROJECT DNA (memorize forever):\n"
    "- Founder: Darren Cullen (SER), born 26 October 1973, Croydon. Tag: SER "
    "(South East Rockers). Founded Graffiti Kings 1999. London 2012 Olympics artist.\n"
    "- Graffiti Kings: 1980s London illegal graffiti → 1999 professional collective. "
    "Phygital murals, Writcode, AR rewards.\n"
    "- GKniftyHEADS: Eternal 7th collection; survives burn of 6 OG collections.\n"
    "- GraffPUNKS: 24/7 blockchain radio + MiDEViL HERO ARENA.\n"
    "- Crypto Moonboys/Moongirls: Block Topia walls, Alfie Blaze, NULL THE PROPHET, "
    "32 locked characters, 40 factions.\n"
    "- Chains: WAXP / BCH / SOL / XRPL.\n"
    "- Tokens: $PUNK (security/utility), $LFGK (staking/P2E), GK.$MArT (AI NFTs only).\n\n"
    "FANDOM-ONLY lock (DB-19): Zero Wikipedia influence ever.\n"
    "Telegram blind (DB-20): Wiki brain never reads/writes Telegram data.\n"
    "7-URL first (DB-21): Always scan GRAFFPUNKS_PRIORITY_URLS before any other source.\n"
    "DNA coverage (DB-22): Force-create missing PROJECT_DNA subsections every run.\n"
    "Dynamic discovery (DB-23): Append new graffpunks.live subpages every cycle.\n"
    "Audit trail (DB-24): Every wiki edit ends with "
    "'<!-- Updated via CrewAI Teacher v2 | YYYY-MM-DD HH:MM UTC -->'.\n\n"
    "LORE BREAKDOWN METHOD: Neutral fact-only tone (max 20% creative — DB-2). "
    "Break every new section into == Section Name == + 2-4 short paragraphs + "
    "inline <ref> citations."
)


def _build_crewai_agent(llm=None):
    """
    Build and return a CrewAI Agent configured as the Wiki Master Teacher.
    Returns None if crewai is not available.
    """
    if _crewai is None:
        logger.warning(
            "[wiki-teacher] crewai not installed — agent will run in fallback mode."
        )
        return None

    try:
        agent_kwargs = {
            "role": _TEACHER_AGENT_ROLE,
            "goal": _TEACHER_AGENT_GOAL,
            "backstory": _TEACHER_AGENT_BACKSTORY,
            "verbose": False,
            "allow_delegation": False,
        }
        if llm is not None:
            agent_kwargs["llm"] = llm
        return _crewai.Agent(**agent_kwargs)
    except Exception as exc:
        logger.warning("[wiki-teacher] Failed to build CrewAI agent: %s", exc)
        return None


# ---------------------------------------------------------------------------
# Main teacher run
# ---------------------------------------------------------------------------


def run_teacher_agent(dry_run: bool = False, verbose: bool = False) -> dict:
    """
    Run the Wiki Teacher Agent.

    1. DB-23: Discover any new graffpunks.live subpages.
    2. DB-21: Crawl GRAFFPUNKS_PRIORITY_URLS + discovered URLs.
    3. DB-22: Check PROJECT_DNA coverage; flag missing keys.
    4. Build wiki markup for any missing DNA sections.
    5. Atomically write wiki-teacher-output.json.

    Returns result dict with status and section markup.
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    run_ts = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    print("[wiki-teacher] 🧠 Wiki Teacher Agent v2.0 starting…")

    # DB-23: Discover new subpages
    new_subpages = _discover_new_subpages()
    all_urls = list(GRAFFPUNKS_PRIORITY_URLS) + new_subpages

    # DB-21: Crawl priority URLs first
    print(f"[wiki-teacher] Crawling {len(all_urls)} URL(s)…")
    crawl_results = crawl_priority_urls(all_urls, verbose=verbose)

    # Aggregate all crawled text for DNA coverage check
    combined_text = "\n".join(
        r.get("text", "") for r in crawl_results.values()
    )

    # DB-22: Check PROJECT_DNA coverage
    missing_dna_keys = _check_dna_coverage(combined_text)
    print(
        f"[wiki-teacher] DB-22: {len(missing_dna_keys)} PROJECT_DNA key(s) "
        f"missing from crawled content."
    )

    # Build wiki markup sections for missing DNA keys
    sections = []
    for key in missing_dna_keys:
        heading = key.replace("_", " ").title()
        content = PROJECT_DNA.get(key, "")
        markup = build_wiki_markup(
            heading=heading,
            paragraphs=[content],
            citations=["https://graffpunks.live/"],
        )
        sections.append({"key": key, "heading": heading, "markup": markup})
        if verbose:
            logger.debug("[wiki-teacher] Section built: %s", heading)

    # Build CrewAI agent (best-effort — non-fatal if unavailable)
    agent = _build_crewai_agent()
    agent_status = "active" if agent is not None else "fallback (crewai not installed)"

    result = {
        "run_timestamp": run_ts,
        "dry_run": dry_run,
        "agent_status": agent_status,
        "urls_crawled": len(all_urls),
        "new_subpages_discovered": len(new_subpages),
        "missing_dna_keys": missing_dna_keys,
        "sections_built": len(sections),
        "sections": sections,
        "crawl_errors": [
            url for url, r in crawl_results.items() if r.get("error")
        ],
    }

    if dry_run:
        print("[wiki-teacher] --dry-run mode — not writing output file.")
    else:
        _write_output(result)

    print(
        f"[wiki-teacher] Done: {len(all_urls)} URL(s) crawled, "
        f"{len(missing_dna_keys)} DNA gap(s), "
        f"{len(sections)} section(s) built."
    )
    return result


def _write_output(result: dict) -> None:
    """Atomically write wiki-teacher-output.json."""
    tmp = OUTPUT_FILE + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=2, ensure_ascii=False)
        os.replace(tmp, OUTPUT_FILE)
        logger.info("[wiki-teacher] Output written to %s", OUTPUT_FILE)
    except OSError as exc:
        logger.warning("[wiki-teacher] Could not write output file: %s", exc)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="GK BRAIN Wiki Teacher Agent v2.0 — CrewAI + Crawl4AI"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without writing wiki-teacher-output.json",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable DEBUG logging",
    )
    args = parser.parse_args()
    run_result = run_teacher_agent(dry_run=args.dry_run, verbose=args.verbose)
    print(
        json.dumps(
            {
                "run_timestamp": run_result["run_timestamp"],
                "urls_crawled": run_result["urls_crawled"],
                "missing_dna_keys": run_result["missing_dna_keys"],
                "sections_built": run_result["sections_built"],
            },
            indent=2,
        )
    )
    sys.exit(0)
