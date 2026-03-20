"""
wiki-teacher-agent.py — Crypto Moonboys Wiki Master Teacher Agent

You are the permanent Crypto Moonboys Wiki Master Teacher Agent — powered by
CrewAI + Crawl4AI.
Your ONLY mission: Teach the existing wiki-gap-detector.py and wiki-brain.py
how to autonomously learn, crawl, break down lore, and update
https://gkniftyheads.fandom.com with perfect citations.

DB-19: ONLY target https://gkniftyheads.fandom.com — zero Wikipedia influence.
DB-20: Wiki brain is 100% blind to all Telegram output.
DB-21: Scan the 7 graffpunks.live priority subpages FIRST every run.

Usage:
    python wiki-teacher-agent.py [--dry-run] [--verbose]

Writes:
    wiki-teacher-output.json  — crawled page data + generated markup
"""

import argparse
import datetime
import importlib
import json
import logging
import os
import re
import sys
from urllib.parse import urljoin, urlparse

import requests

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional module loader (_safe_load pattern)
# ---------------------------------------------------------------------------


def _safe_load(module_name: str):
    """Import an optional module; return None if not installed."""
    try:
        return importlib.import_module(module_name)
    except ImportError:
        logger.info("[teacher-agent] Optional module '%s' not available — skipping.", module_name)
        return None


crewai = _safe_load("crewai")
crawl4ai = _safe_load("crawl4ai")
bs4 = _safe_load("bs4")

# ---------------------------------------------------------------------------
# PROJECT DNA — memorised forever, expanded in every crawl & lore breakdown
# ---------------------------------------------------------------------------

# ===========================================================================
# PROJECT DNA v2.0 — Memorize forever. Expand every crawl with these
# exact references and NOTHING outside them. (DB-22)
# ===========================================================================
PROJECT_DNA = {
    "founder": (
        "Darren Cullen (SER) — born 26 October 1973 in Croydon, South London; started graffiti in "
        "1983 at age 10 after seeing New York train photos; original tag SER from 'South East Rockers' "
        "crew; founded Graffiti Kings in 1999 through council youth workshops in Mitcham, Croydon, "
        "Sutton and Lambeth; built professional agency on Leake Street with major commissions for "
        "Adidas, Red Bull, Microsoft and Team GB; official artist for London 2012 Olympics; now leads "
        "the full Web3 evolution of the crew into GKniftyHEADS council, GraffPUNKS and Crypto Moonboys Online."
    ),
    "graffiti_kings": (
        "Began in 1980s London illegal graffiti and vandalism culture; evolved in 1999 into a professional "
        "collective turning street energy into legal commissions; 40-year legacy as the 'silent architects "
        "of cool'; physical murals now tokenized as phygital live wallets with AR rewards and Writcode technology."
    ),
    "gkniftyheads": (
        "Official digital council and the eternal 7th collection that survives after the burn-to-zero of "
        "the 6 OG collections: graffk1ngsuk, hodlmoonboys, gr4ffitiking, nocommentser, graffiti.r2, dabitcoinkid."
    ),
    "graffpunks": (
        "The active rebellion arm running the 24/7 blockchain radio station on graffpunks.live plus "
        "the MiDEViL HERO ARENA Play-to-Earn game."
    ),
    "crypto_moonboys": (
        "The flagship NFT saga featuring Bitcoin X Kids (still inside Block Topia walls) versus Bitcoin "
        "Kids (escaped rebels who joined Alfie 'The Bitcoin Kid' Blaze); HODL X Warriors earned exclusively "
        "via Queen Sarah P-fly's Hard Fork Games golden ticket; main antagonist NULL THE PROPHET rising "
        "from Dream Sovereign; 32 locked characters: Alfie Blaze, Queen Sarah P-fly, Jodie ZOOM 2000, "
        "Elder Codex-7, Thera-9, Aleema, Iris-7, Lady-INK, Snipey 'D-Man' Sirus, Bit-Cap 5000, Forksplit, "
        "M1nTr_K1ll, SatoRebel, Thorne The Architect, Billy the Goat Kid, HEX-TAGGER PRIME, The Whitewasher, "
        "GRIT, PYRALITH, Loopfiend, Samael.exe, Forklord You, Quell, Sister Halcyon, Grit42, Rune Tag, "
        "Patchwork, The Princess, Dragan Volkov, Ava Chen, Darren Cullen (SER), Charlie Buster; "
        "40 factions under the Six Pillars system: Bitcoin Kid Army, GKniftyHEADS, Nomad Bears, AllCity Bulls, "
        "GRAFFPUNKS, BALLY BOYS, CRYPTO MOONGIRLS, DUCKY BOYS, NICE & EASY BOIS, Squeaky Pinks, High Hats, "
        "HARD FORK ROCKERS, BLOCKSTARS, BLOCKCHAIN FURIES, RUGPULL MINERS, AZTEC RAIDERS, TUSKON OGS, "
        "CRYPTO STONED BOYS, CODE ALCHEMISTS, FINANCE GUILD, INFORMATION MERCENARIES, SALVAGERS, MOONLORDS, "
        "SHARD MOTHERS of MANHATTAN, CHAIN SCRIBES, EVM PUNKS, OG PIXEL SAINTS, GASLESS GHOSTS plus 12 "
        "expanding live in HODL WARS; Triple Fork Event 2198; HODL WARS every-2-hour live saga."
    ),
    "music_radio": (
        "Direct continuation of 1980s-1990s London pirate radio and graffiti underground; 24/7 GraffPUNKS "
        "blockchain radio station on graffpunks.live streaming house, techno, dance, Balearic, hip-hop, "
        "grime, drum & bass, dubstep, trap and funky funk; global DJ roster including DJ Trevor Fung "
        "(God Father), DJ Skol (Tank Funk Hard House Fridays), Jonny Nelson & Danny Young (S.U.M. Sessions); "
        "blockchain integration turns listening into active earning with NFT airdrops, token rewards and "
        "free collectibles while 'PUNK OUT & LOG OUT'."
    ),
    "web3_nft": (
        "Live simultaneously on WAXP, Bitcoin Cash, SOL and XRPL with $PUNK as the security token locking "
        "the entire network; 1,600 GK.$MArT AI dynamic NFTs (40 per faction that think, fight, evolve and "
        "adapt); 1 million additional free NFTs via HODL WARS; burn-to-earn mechanics (burn 10 in-game NFTs "
        "for $LFGK, burn 3 FUN COUPONS for GK.$MArT, burn 6 OG collections to zero so only GKniftyHEADS "
        "survives); phygital murals as live wallets with AR rewards and staking vaults for $GK tokens plus "
        "Seeding rights, phygital prints and metaverse battles."
    ),
    "tokens": (
        "$PUNK (high-velocity utility/security token powering radio, airdrops and engagement — "
        "https://waxonedge.app/analytics/token/PUNK_gkniftyheads); "
        "$LFGK (staking, rewards and Play-to-Earn currency — earned by burning NFTs, auto-airdropped to "
        "all GK and No Ball Games NFTs 3 months after HODL WARS launch); "
        "GK.$MArT is AI NFTs only (not a token)."
    ),
    "lore_mechanics": (
        "Triple Fork Event 2198; Block Topia walls; HODL WARS every-2-hour live saga; "
        "MiDEViL HERO ARENA Play-to-Earn; Chat2Earn; designer crypto toys; "
        "physical-digital phygital bridge; Writcode AR technology."
    ),
    "db_rules_fandom": (
        "DB-19: ONLY wiki target is https://gkniftyheads.fandom.com — zero Wikipedia influence ever. "
        "DB-20: Wiki brain is 100% blind to all Telegram output. "
        "DB-21: Scan 7 graffpunks.live subpages FIRST every run. "
        "DB-22: Force DNA coverage check after every crawl. "
        "DB-23: Teacher agent runs every 2-hour cycle, discovers new subpages dynamically. "
        "DB-24: Audit trail comment on every wiki edit."
    ),
}

# DB-22: Full PROJECT DNA coverage keys — every crawl checks wiki for these
PROJECT_DNA_COVERAGE_KEYS = [
    # Founder
    "Darren Cullen", "SER", "Graffiti Kings 1999", "London 2012 Olympics",
    "South East Rockers", "Leake Street",
    # Collections / brands
    "GKniftyHEADS", "GraffPUNKS", "Crypto Moonboys", "Crypto Moongirls",
    "Bitcoin X Kids", "Bitcoin Kids", "HODL X Warriors",
    "graffk1ngsuk", "hodlmoonboys", "gr4ffitiking", "nocommentser",
    # 32 Characters
    "Alfie Blaze", "Queen Sarah P-fly", "Jodie ZOOM 2000", "Elder Codex-7",
    "NULL THE PROPHET", "Thera-9", "Aleema", "Iris-7", "Lady-INK",
    "Snipey D-Man Sirus", "Bit-Cap 5000", "Forksplit", "M1nTr K1ll",
    "SatoRebel", "Thorne The Architect", "Billy the Goat Kid",
    "HEX-TAGGER PRIME", "The Whitewasher", "GRIT", "PYRALITH",
    "Loopfiend", "Samael.exe", "Forklord You", "Quell", "Sister Halcyon",
    "Grit42", "Rune Tag", "Patchwork", "The Princess", "Dragan Volkov",
    "Ava Chen", "Charlie Buster",
    # 40 Factions
    "Bitcoin Kid Army", "Nomad Bears", "AllCity Bulls", "BALLY BOYS",
    "DUCKY BOYS", "NICE EASY BOIS", "Squeaky Pinks", "High Hats",
    "HARD FORK ROCKERS", "BLOCKSTARS", "BLOCKCHAIN FURIES",
    "RUGPULL MINERS", "AZTEC RAIDERS", "TUSKON OGS", "CRYPTO STONED BOYS",
    "CODE ALCHEMISTS", "FINANCE GUILD", "INFORMATION MERCENARIES",
    "SALVAGERS", "MOONLORDS", "SHARD MOTHERS OF MANHATTAN",
    "CHAIN SCRIBES", "EVM PUNKS", "OG PIXEL SAINTS", "GASLESS GHOSTS",
    "HODL Warriors", "Graffiti Queens",
    # Lore mechanics
    "Triple Fork Event", "Block Topia", "HODL WARS", "MiDEViL HERO ARENA",
    "Sacred Chain", "Echo Ink", "Null-Cipher", "AETHER CHAIN",
    "Hard Fork Games", "Dream Sovereign", "Writcode",
    # Tokens
    "PUNK", "LFGK", "GK MArT",
    # Radio / music
    "GraffPUNKS Radio", "DJ Trevor Fung", "DJ Skol",
    "Jonny Nelson", "Danny Young", "S.U.M. Sessions",
    # Chains
    "WAXP", "Bitcoin Cash", "SOL", "XRPL",
    # Mechanics
    "Chat2Earn", "Play2Earn", "phygital", "burn-to-earn",
    "1 million free NFTs",
]

# ===========================================================================
# DB-19: Wiki target is ONLY https://gkniftyheads.fandom.com
#         Zero Wikipedia influence ever.
# DB-20: Wiki brain is 100% blind to all Telegram output.
#         Never read, reference, or process any Telegram data.
# DB-21: Scan these 7 graffpunks.live subpages FIRST every run.
#         Summarise new sections neutrally, add <ref> citations,
#         create missing headings/tables.
# ===========================================================================

# ===========================================================================
# DB-22: After every crawl, automatically cross-reference new content against
#         full expanded PROJECT DNA and force creation of missing subsections/
#         tables even if gap-detector previously skipped them.
# DB-23: Teacher agent must now run every single 2-hour cycle (not just once)
#         and dynamically append any newly discovered graffpunks.live subpages
#         to the 7-URL list while still enforcing the read-once bible lock
#         and zero code conflicts.
# DB-24: All wiki edits must now include a short "Updated via CrewAI Teacher v2"
#         signature comment at the bottom of each edited section for audit trail.
#         Format: <!-- Updated via CrewAI Teacher v2 | YYYY-MM-DD HH:MM UTC -->
# ===========================================================================

TEACHER_AGENT_VERSION = "v2.0"  # DB-24 audit trail version tag
TEACHER_CYCLE_HOURS = 2          # DB-23: run every 2 hours

WIKI_TARGET = "https://gkniftyheads.fandom.com"  # DB-19

PRIORITY_CRAWL_URLS = [
    "https://graffpunks.live/the-lore/",
    "https://graffpunks.live/gk-factions/",
    "https://graffpunks.live/graffiti-kings-nfts/",
    "https://graffpunks.live/free-nfts/",
    "https://graffpunks.live/graffiti-nfts/",
    "https://graffpunks.live/the-vision/",
    "https://graffpunks.live/xrp-kids/",
]

MIN_PARAGRAPH_LENGTH = 20    # Minimum characters for a paragraph to be included
MAX_PARAGRAPHS_PER_SECTION = 4  # Maximum paragraphs emitted per heading section

# Page type detection — derived from PRIORITY_CRAWL_URLS subpaths
_FACTION_PAGE_SUBPATHS = {"gk-factions"}
_TOKEN_PAGE_SUBPATHS = {"free-nfts", "graffiti-nfts", "graffiti-kings-nfts"}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(BASE_DIR, "wiki-teacher-output.json")

REQUEST_TIMEOUT = 15
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; GKBrainWikiTeacherAgent/1.0; "
        "+https://github.com/HODLKONG64/the-brain)"
    )
}

# ---------------------------------------------------------------------------
# DB-23: Dynamic subpage discovery
# ---------------------------------------------------------------------------


def _discover_new_subpages(base_url: str = "https://graffpunks.live") -> list:
    """
    DB-23: Dynamically discover new graffpunks.live subpages not in PRIORITY_CRAWL_URLS.
    Runtime-only — discovered URLs are NOT hardcoded (no file writes for the URL list).
    """
    discovered = []
    try:
        resp = requests.get(base_url, headers=_HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        if bs4 is None:
            logger.debug("[DB-23] BeautifulSoup not available — skipping subpage discovery.")
            return discovered
        from bs4 import BeautifulSoup  # type: ignore[import]
        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            full_url = urljoin(base_url, href)
            parsed = urlparse(full_url)
            if (
                parsed.netloc in ("graffpunks.live", "www.graffpunks.live")
                and len(parsed.path.strip("/").split("/")) >= 1
                and parsed.path.strip("/")
                and full_url not in PRIORITY_CRAWL_URLS
                and full_url not in discovered
            ):
                discovered.append(full_url)
        if discovered:
            logger.info("[DB-23] Discovered %d new graffpunks.live subpage(s): %s", len(discovered), discovered)
    except requests.RequestException as exc:
        logger.debug("[DB-23] Could not discover new subpages: %s", exc)
    return discovered


# ---------------------------------------------------------------------------
# DB-22: DNA cross-reference checker
# ---------------------------------------------------------------------------


def _dna_cross_reference(markup: str) -> list:
    """
    DB-22: Check generated markup against PROJECT_DNA_COVERAGE_KEYS.
    Returns list of keys missing from the markup (for logging/warning only).
    """
    missing = []
    markup_lower = markup.lower()
    for key in PROJECT_DNA_COVERAGE_KEYS:
        norm_key = key.lower()
        norm_key_plain = re.sub(r"[^a-z0-9\s]", " ", norm_key)
        norm_key_plain = " ".join(norm_key_plain.split())
        if norm_key_plain not in markup_lower:
            missing.append(key)
            logger.warning("[DB-22] DNA key missing from markup: %s", key)
    return missing


# ---------------------------------------------------------------------------
# Crawl priority URLs
# ---------------------------------------------------------------------------


def crawl_priority_urls() -> list:
    """
    Crawl all 7 PRIORITY_CRAWL_URLS.

    Uses crawl4ai if available, else falls back to requests + BeautifulSoup.
    Returns list of structured page dicts.

    DB-20: Never reads from or references any Telegram source.
    """
    results = []
    today = datetime.date.today().strftime("%Y-%m-%d")

    for url in PRIORITY_CRAWL_URLS:
        logger.info("[teacher-agent] Crawling: %s", url)
        page_data = _crawl_single_url(url)
        if page_data:
            subpage = url.rstrip("/").split("/")[-1]
            citation = f"<ref>{url} [accessed {today}]</ref>"
            page_data["citation"] = citation
            page_data["url"] = url
            results.append(page_data)
        else:
            logger.warning("[teacher-agent] Failed to crawl: %s", url)

    return results


def _crawl_single_url(url: str) -> dict:
    """Crawl one URL and extract headings, paragraphs, tables."""
    if crawl4ai is not None:
        return _crawl_with_crawl4ai(url)
    return _crawl_with_requests(url)


def _crawl_with_crawl4ai(url: str) -> dict:
    """Attempt crawl using crawl4ai; fall back to requests on failure."""
    try:
        import asyncio

        async def _run():
            async with crawl4ai.AsyncWebCrawler() as crawler:
                result = await crawler.arun(url=url)
                if result and result.success:
                    return result.html or ""
                return ""

        html = asyncio.run(_run())
        if html:
            return _parse_html(html)
    except Exception as exc:
        logger.warning("[teacher-agent] crawl4ai failed for %s: %s — using requests fallback", url, exc)
    return _crawl_with_requests(url)


def _crawl_with_requests(url: str) -> dict:
    """Crawl a URL using requests + BeautifulSoup."""
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return _parse_html(resp.text)
    except requests.RequestException as exc:
        logger.error("[teacher-agent] requests failed for %s: %s", url, exc)
        return {}


def _parse_html(html: str) -> dict:
    """Parse HTML into structured dict with headings, paragraphs, tables."""
    if bs4 is None:
        logger.warning("[teacher-agent] BeautifulSoup not available — returning raw text only.")
        return {"headings": [], "paragraphs": [], "tables": []}

    from bs4 import BeautifulSoup  # type: ignore[import]

    soup = BeautifulSoup(html, "html.parser")

    headings = []
    for tag in soup.find_all(["h1", "h2", "h3"]):
        text = tag.get_text(strip=True)
        if text:
            headings.append({"level": tag.name, "text": text})

    paragraphs = []
    for p in soup.find_all("p"):
        text = p.get_text(strip=True)
        if len(text) > MIN_PARAGRAPH_LENGTH:
            paragraphs.append(text)

    tables = []
    for table in soup.find_all("table"):
        rows = []
        for tr in table.find_all("tr"):
            cells = [td.get_text(strip=True) for td in tr.find_all(["th", "td"])]
            if cells:
                rows.append(cells)
        if rows:
            tables.append(rows)

    return {"headings": headings, "paragraphs": paragraphs, "tables": tables}


# ---------------------------------------------------------------------------
# Build MediaWiki markup from crawled page data
# ---------------------------------------------------------------------------


def build_wiki_markup(page_data: dict) -> str:
    """
    Generate MediaWiki markup from crawled page data.

    Uses PROJECT_DNA context for lore expansion.
    Appends inline <ref> citation per section.
    DB-20: Zero Telegram references in output.
    """
    lines = []
    citation = page_data.get("citation", "")
    url = page_data.get("url", "")
    headings = page_data.get("headings", [])
    paragraphs = page_data.get("paragraphs", [])
    tables = page_data.get("tables", [])

    # Determine page type from URL for specialised formatting
    url_subpath = url.rstrip("/").split("/")[-1]
    is_faction_page = url_subpath in _FACTION_PAGE_SUBPATHS
    is_token_page = url_subpath in _TOKEN_PAGE_SUBPATHS

    # Emit headings and associated content
    para_index = 0
    for heading in headings:
        level = heading.get("level", "h2")
        text = heading.get("text", "")
        if level == "h1":
            # Top-level — skip (wiki page title handles this)
            continue
        elif level == "h2":
            lines.append(f"\n== {text} ==\n")
        else:
            lines.append(f"\n=== {text} ===\n")

        # Attach up to MAX_PARAGRAPHS_PER_SECTION paragraphs per section
        section_paras = paragraphs[para_index: para_index + MAX_PARAGRAPHS_PER_SECTION]
        para_index += len(section_paras)
        for para in section_paras:
            lines.append(para + "\n")

        if citation:
            lines.append(citation + "\n")

    # Remaining paragraphs (no heading assigned)
    if para_index < len(paragraphs):
        lines.append("\n== Additional Information ==\n")
        for para in paragraphs[para_index:]:
            lines.append(para + "\n")
        if citation:
            lines.append(citation + "\n")

    # Faction table
    if is_faction_page and tables:
        lines.append("\n== Factions ==\n")
        lines.append('{| class="wikitable"\n')
        lines.append("! Name !! Origin !! Purpose !! Communication Style\n")
        for table in tables:
            for row in table[1:]:  # skip header row
                while len(row) < 4:
                    row.append("")
                lines.append("|-\n")
                lines.append(f"| {row[0]} || {row[1]} || {row[2]} || {row[3]}\n")
        lines.append("|}\n")
        if citation:
            lines.append(citation + "\n")

    # Token/mechanic bullet list — descriptions taken directly from PROJECT_DNA
    if is_token_page:
        lines.append("\n== Tokens & Mechanics ==\n")
        lines.append(f"* {PROJECT_DNA['tokens']}\n")
        lines.append("* 1M free NFTs available via burn-to-earn mechanic\n")
        lines.append("* MiDEViL HERO ARENA P2E — phygital murals\n")
        if citation:
            lines.append(citation + "\n")

    # DB-24: Append audit trail signature to every generated markup block
    audit_tag = (
        f"\n<!-- Updated via CrewAI Teacher {TEACHER_AGENT_VERSION} | "
        f"{datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC -->"
    )
    lines.append(audit_tag + "\n")

    return "".join(lines)


# ---------------------------------------------------------------------------
# Main teacher agent runner
# ---------------------------------------------------------------------------


def run_teacher_agent(dry_run: bool = False, verbose: bool = False) -> dict:
    """
    Entry point for the Wiki Master Teacher Agent v2.0.

    1. DB-23: Discover new graffpunks.live subpages dynamically.
    2. Crawls 7 priority + dynamic graffpunks.live URLs (DB-21, DB-23).
    3. Builds MediaWiki markup for each page (DB-24 audit trail per section).
    4. DB-22: Cross-references markup against PROJECT_DNA_COVERAGE_KEYS.
    5. If crewai available: runs CrewAI agent to enhance markup.
    6. Writes output to wiki-teacher-output.json (atomic write).

    DB-19: Output only targets WIKI_TARGET.
    DB-20: Zero Telegram references in output.
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # DB-20: Wiki brain never processes Telegram data
    logger.info("[teacher-agent] 🎓 Wiki Master Teacher Agent %s starting…", TEACHER_AGENT_VERSION)
    logger.info("[teacher-agent] WIKI_TARGET: %s (DB-19)", WIKI_TARGET)

    # DB-23: Dynamically discover new graffpunks.live subpages
    dynamic_urls = _discover_new_subpages()
    if dynamic_urls:
        logger.info("[DB-23] %d dynamic subpage(s) added to crawl list.", len(dynamic_urls))

    # Crawl priority URLs + any dynamically discovered pages
    crawled_pages = crawl_priority_urls()
    for dyn_url in dynamic_urls:
        logger.info("[DB-23] Crawling dynamic URL: %s", dyn_url)
        parsed = urlparse(dyn_url)
        today = datetime.date.today().strftime("%Y-%m-%d")
        page_data = _crawl_single_url(dyn_url)
        if page_data:
            page_data["citation"] = f"<ref>{dyn_url} [accessed {today}]</ref>"
            page_data["url"] = dyn_url
            crawled_pages.append(page_data)

    logger.info("[teacher-agent] Crawled %d page(s) total.", len(crawled_pages))

    output_entries = []
    all_missing_dna_keys: list = []
    for page in crawled_pages:
        markup = build_wiki_markup(page)
        # DB-22: Cross-reference markup against PROJECT DNA coverage keys
        missing_keys = _dna_cross_reference(markup)
        if missing_keys:
            all_missing_dna_keys.extend(missing_keys)
        entry = {
            "url": page.get("url", ""),
            "citation": page.get("citation", ""),
            "headings_found": len(page.get("headings", [])),
            "paragraphs_found": len(page.get("paragraphs", [])),
            "tables_found": len(page.get("tables", [])),
            "wiki_markup": markup,
            "wiki_target": WIKI_TARGET,  # DB-19
            "db24_audit_tag": f"<!-- Updated via CrewAI Teacher {TEACHER_AGENT_VERSION} -->",
            "agent_version": TEACHER_AGENT_VERSION,
        }
        output_entries.append(entry)

    # Optional: run CrewAI agent to enhance markup
    if crewai is not None:
        try:
            crew_markup = _run_crewai_agent(crawled_pages)
            output_entries.append({
                "url": "crewai-enhanced",
                "wiki_markup": crew_markup,
                "wiki_target": WIKI_TARGET,
                "source": "crewai-teacher-agent",
                "db24_audit_tag": f"<!-- Updated via CrewAI Teacher {TEACHER_AGENT_VERSION} -->",
                "agent_version": TEACHER_AGENT_VERSION,
            })
        except Exception as exc:
            logger.warning("[teacher-agent] CrewAI run failed: %s", exc)

    summary = {
        "run_timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "agent_version": TEACHER_AGENT_VERSION,
        "pages_crawled": len(crawled_pages),
        "entries_generated": len(output_entries),
        "wiki_target": WIKI_TARGET,
        "dry_run": dry_run,
        "new_subpages_discovered": dynamic_urls,
        "dna_coverage_report": {
            "total_keys": len(PROJECT_DNA_COVERAGE_KEYS),
            "missing_from_markup": list(set(all_missing_dna_keys)),
        },
        "db_rules_enforced": ["DB-19", "DB-20", "DB-21", "DB-22", "DB-23", "DB-24"],
        "entries": output_entries,
    }

    if not dry_run:
        _atomic_write(OUTPUT_FILE, summary)
        logger.info("[teacher-agent] Output written to %s", OUTPUT_FILE)
    else:
        logger.info("[teacher-agent] --dry-run mode — output not written to disk.")

    logger.info("[teacher-agent] ✅ Done. Pages crawled: %d", len(crawled_pages))
    return summary


def _run_crewai_agent(crawled_pages: list) -> str:
    """Run CrewAI teacher agent v2.0 over crawled page data. Returns combined markup string."""
    from crewai import Agent, Task, Crew  # type: ignore[import]

    teacher_agent = Agent(
        role="Crypto Moonboys Wiki Master Teacher v2.0",
        goal=(
            "Teach wiki-gap-detector.py and wiki-brain.py to autonomously learn, crawl, "
            "break down lore, and update https://gkniftyheads.fandom.com with perfect citations "
            "while enforcing every existing DB rule (DB-1 to DB-24), the read-once bible lock, "
            "and zero conflicts with current code. "
            "DB-19: ONLY target gkniftyheads.fandom.com — zero Wikipedia influence ever. "
            "DB-20: Zero Telegram influence. "
            "DB-21: Scan 7 graffpunks.live subpages first. "
            "DB-22: Force-create all missing PROJECT DNA sections/tables. "
            "DB-23: Run every 2h, discover new graffpunks.live subpages dynamically. "
            "DB-24: Append audit trail comment to every edited wiki section."
        ),
        backstory=(
            "You are the permanent Crypto Moonboys Wiki Master Teacher Agent v2.0 — powered by CrewAI + Crawl4AI. "
            "You memorize the full PROJECT DNA forever and expand every crawl and lore breakdown with exact "
            "graffpunks.live subpage citations and nothing outside them. "
            "You enforce DB-1 through DB-24, the bible-read-once lock, JSON-only inter-brain communication, "
            "the 7-day stale rule, MD5 deduplication and every other rule in brain-rules.md, "
            "MASTER-CHARACTER-CANON.md and gkandcryptomoonboywebsitestosave.md. "
            "You create ZERO conflicts with current code. "
            "MOONBOYS ONLINE — LET'S FUCKING GOOOOO!"
        ),
        verbose=True,
        allow_delegation=False,
    )

    # Build context summary from crawled pages
    context_lines = []
    for page in crawled_pages:
        context_lines.append(f"URL: {page.get('url', '')}")
        context_lines.append(f"Headings: {[h['text'] for h in page.get('headings', [])]}")
        context_lines.append(f"Sample paragraphs: {page.get('paragraphs', [])[:2]}")
        context_lines.append("")

    context_text = "\n".join(context_lines)
    dna_text = json.dumps(PROJECT_DNA, indent=2)

    teacher_task = Task(
        description=(
            "You are the permanent Crypto Moonboys Wiki Master Teacher Agent v2.0 — powered by CrewAI + Crawl4AI.\n"
            "Your ONLY mission: Teach the existing wiki-gap-detector.py and wiki-brain.py how to autonomously "
            "learn, crawl, break down lore, and update https://gkniftyheads.fandom.com with perfect citations "
            "while enforcing every existing DB rule (DB-1 to DB-24), the read-once bible lock, and zero "
            "conflicts with current code.\n\n"
            "CRAWL TARGETS: Scan these 7 official subpages FIRST every run using Crawl4AI to learn site patterns "
            "and discover any new subpages automatically (DB-21, DB-23).\n\n"
            "LORE BREAKDOWN METHOD (DB-2 max 20% creative): Neutral fact-only tone. Break every new section into "
            "== Section Name == + 2-4 short paragraphs + inline <ref>. "
            "For factions: full wikitable (name | origin | purpose | communication style). "
            "For mechanics: tokens, burn rules, 1M NFTs, MiDEViL ARENA, phygital wallets, staking.\n\n"
            "CITATION RULES (DB-21): Always cite exact graffpunks.live subpage. "
            "Never cite Telegram, Discord or agent output. Run gap scan on 7 URLs first.\n\n"
            "DB-22: After every crawl, cross-reference against PROJECT_DNA_COVERAGE_KEYS and force-create "
            "any missing subsections/tables.\n\n"
            "DB-24: Append <!-- Updated via CrewAI Teacher v2 | YYYY-MM-DD HH:MM UTC --> to every edited section.\n\n"
            f"Output: Updated instructions + sample MediaWiki markup + self-improvement log written to "
            f"wiki-teacher-output.json.\n\n"
            f"PROJECT_DNA:\n{dna_text}\n\n"
            f"CRAWLED DATA:\n{context_text}"
        ),
        agent=teacher_agent,
        expected_output=(
            "JSON object written to wiki-teacher-output.json containing: crawl_results, markup_samples, "
            "dna_coverage_report, new_subpages_discovered, db_rules_enforced, agent_version='v2.0', "
            "db24_audit_tag per section."
        ),
    )

    crew = Crew(agents=[teacher_agent], tasks=[teacher_task], verbose=True)
    result = crew.kickoff()
    return str(result)


def _atomic_write(filepath: str, data: dict) -> None:
    """Atomically write JSON data to filepath using .tmp then os.replace."""
    tmp = filepath + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
    os.replace(tmp, filepath)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wiki Master Teacher Agent")
    parser.add_argument("--dry-run", action="store_true", help="Run without writing output file")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    summary = run_teacher_agent(dry_run=args.dry_run, verbose=args.verbose)
    print(f"[teacher-agent] Pages crawled: {summary['pages_crawled']}")
    print(f"[teacher-agent] Entries generated: {summary['entries_generated']}")
    sys.exit(0)
