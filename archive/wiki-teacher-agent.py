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

PROJECT_DNA = {
    "founder": (
        "Darren Cullen (SER) — born 26 Oct 1973 Croydon, started graffiti 1983 age 10, "
        "founded Graffiti Kings 1999 via council youth workshops (Mitcham/Croydon/Sutton/Lambeth), "
        "built pro agency on Leake Street, official London 2012 Olympics artist, now leads Web3 evolution."
    ),
    "graffiti_kings": (
        "1980s London illegal graffiti → 1999 pro collective → 40-year legacy "
        "(Adidas, Red Bull, Microsoft, Team GB). Physical murals now tokenized as "
        "phygital live wallets + AR rewards."
    ),
    "gkniftyheads": (
        "Official digital council + eternal 7th collection (survives after burning 6 OG sets)."
    ),
    "graffpunks": (
        "Rebellion arm running 24/7 blockchain radio + MiDEViL HERO ARENA P2E."
    ),
    "crypto_moonboys": (
        "Flagship saga — Bitcoin X Kids vs Bitcoin Kids split, HODL X Warriors elite, "
        "NULL THE PROPHET antagonist, 32 characters, 40 factions (Six Pillars), "
        "Triple Fork Event 2198, HODL WARS live saga."
    ),
    "music_radio": (
        "24/7 GraffPUNKS station (house/techno/grime/hip-hop/DnB/dubstep/trap) on "
        "graffpunks.live — DJ Trevor Fung, Skol, Jonny Nelson etc. "
        "Beats unlock NFT airdrops + token rewards."
    ),
    "web3_nft": (
        "Live on WAXP + Bitcoin Cash + SOL + XRPL secured by $PUNK. "
        "1,600 GK.$MArT AI NFTs, 1M free NFTs, burn-to-earn, phygital murals."
    ),
    "tokens": (
        "$PUNK (security/utility), $LFGK (staking/rewards — burn 10 NFTs for $LFGK), "
        "GK.$MArT (AI NFTs only)."
    ),
}

# ===========================================================================
# DB-19: Wiki target is ONLY https://gkniftyheads.fandom.com
#         Zero Wikipedia influence ever.
# DB-20: Wiki brain is 100% blind to all Telegram output.
#         Never read, reference, or process any Telegram data.
# DB-21: Scan these 7 graffpunks.live subpages FIRST every run.
#         Summarise new sections neutrally, add <ref> citations,
#         create missing headings/tables.
# ===========================================================================

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


def _discover_new_subpages(base_url: str = "https://graffpunks.live/") -> list:
    """
    DB-23: Crawl the graffpunks.live home page and detect any subpages not already
    present in PRIORITY_CRAWL_URLS.  Returns a list of new URLs discovered.
    """
    known = set(PRIORITY_CRAWL_URLS)
    discovered = []
    try:
        resp = requests.get(base_url, headers=_HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        from bs4 import BeautifulSoup  # type: ignore[import]
        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            full = urljoin(base_url, href)
            parsed = urlparse(full)
            if (
                parsed.netloc == urlparse(base_url).netloc
                and len(parsed.path.strip("/")) > 0
                and full not in known
                and not full.endswith("#")
                and not full.startswith("javascript:")
            ):
                discovered.append(full)
                known.add(full)
    except requests.RequestException as exc:
        logger.warning("[wiki-teacher] DB-23 subpage discovery failed: %s", exc)
    except ImportError:
        logger.debug("[wiki-teacher] bs4 not installed — DB-23 subpage discovery skipped.")
    logger.info("[wiki-teacher] DB-23: %d new subpage(s) discovered.", len(discovered))
    return discovered


# ---------------------------------------------------------------------------
# DB-22: PROJECT DNA coverage checker
# ---------------------------------------------------------------------------

# DB-22: Keys used to cross-reference the wiki for missing sections.
_DNA_KEY_TERMS = {
    "founder": ["darren cullen", "ser", "graffiti kings"],
    "graffiti_kings": ["graffiti kings", "1999"],
    "gkniftyheads": ["gkniftyheads", "7th collection"],
    "graffpunks": ["graffpunks", "midevil hero arena"],
    "crypto_moonboys": ["crypto moonboys", "block topia", "alfie blaze"],
    "music_radio": ["graffpunks.live", "blockchain radio"],
    "web3_nft": ["waxp", "xrpl", "gk.$mart"],
    "tokens": ["$punk", "$lfgk"],
}


def _check_dna_coverage(wiki_text: str) -> list:
    """
    DB-22: Cross-reference wiki_text against the PROJECT_DNA keys.
    Returns list of DNA section keys whose core terms are absent from the wiki.
    """
    missing = []
    wiki_lower = wiki_text.lower() if wiki_text else ""
    for key, terms in _DNA_KEY_TERMS.items():
        if not any(t in wiki_lower for t in terms):
            missing.append(key)
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

    return "".join(lines)


# ---------------------------------------------------------------------------
# Main teacher agent runner
# ---------------------------------------------------------------------------


def run_teacher_agent(dry_run: bool = False, verbose: bool = False) -> dict:
    """
    Entry point for the Wiki Master Teacher Agent.

    1. Crawls 7 priority graffpunks.live URLs (DB-21).
    2. Builds MediaWiki markup for each page.
    3. If crewai available: runs CrewAI agent to enhance markup.
    4. Writes output to wiki-teacher-output.json (atomic write).

    DB-19: Output only targets WIKI_TARGET.
    DB-20: Zero Telegram references in output.
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # DB-20: Wiki brain never processes Telegram data
    logger.info("[teacher-agent] 🎓 Wiki Master Teacher Agent starting…")
    logger.info("[teacher-agent] WIKI_TARGET: %s (DB-19)", WIKI_TARGET)

    # DB-23: Discover any new graffpunks.live subpages beyond the fixed 7.
    new_subpages = _discover_new_subpages()
    if new_subpages:
        logger.info("[teacher-agent] DB-23: appending %d new subpage URL(s) to crawl list.", len(new_subpages))

    crawled_pages = crawl_priority_urls()
    # Also crawl any newly discovered subpages (dynamic DB-23 expansion).
    today = datetime.date.today().strftime("%Y-%m-%d")
    for url in new_subpages:
        logger.info("[teacher-agent] DB-23 crawling new subpage: %s", url)
        page_data = _crawl_single_url(url)
        if page_data:
            page_data["citation"] = f"<ref>{url} [accessed {today}]</ref>"
            page_data["url"] = url
            crawled_pages.append(page_data)
    logger.info("[teacher-agent] Crawled %d page(s) total.", len(crawled_pages))

    output_entries = []
    for page in crawled_pages:
        markup = build_wiki_markup(page)
        # DB-22: Cross-reference each page's text against PROJECT DNA keys.
        page_text = " ".join(page.get("paragraphs", []))
        dna_missing = _check_dna_coverage(page_text)
        entry = {
            "url": page.get("url", ""),
            "citation": page.get("citation", ""),
            "headings_found": len(page.get("headings", [])),
            "paragraphs_found": len(page.get("paragraphs", [])),
            "tables_found": len(page.get("tables", [])),
            "wiki_markup": markup,
            "wiki_target": WIKI_TARGET,  # DB-19
            "dna_missing_sections": dna_missing,  # DB-22
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
            })
        except Exception as exc:
            logger.warning("[teacher-agent] CrewAI run failed: %s", exc)

    summary = {
        "run_timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pages_crawled": len(crawled_pages),
        "entries_generated": len(output_entries),
        "wiki_target": WIKI_TARGET,
        "dry_run": dry_run,
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
    """Run CrewAI teacher agent over crawled page data. Returns combined markup string."""
    from crewai import Agent, Task, Crew  # type: ignore[import]

    teacher_agent = Agent(
        role="Crypto Moonboys Wiki Master Teacher",
        goal=(
            "Teach wiki-gap-detector.py and wiki-brain.py to autonomously learn, crawl, "
            "break down lore, and update https://gkniftyheads.fandom.com with perfect citations. "
            "DB-19: ONLY target gkniftyheads.fandom.com. DB-20: Zero Telegram influence."
        ),
        backstory=(
            "You are the permanent Crypto Moonboys Wiki Master Teacher Agent — powered by CrewAI + Crawl4AI. "
            "You memorize PROJECT_DNA forever and expand every crawl with exact graffpunks.live references. "
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

    task_description = (
        f"Using the PROJECT_DNA below and the crawled page data, produce MediaWiki markup "
        f"for https://gkniftyheads.fandom.com. "
        f"Use == Heading == for h2, === Sub-heading === for h3. "
        f"2-4 neutral paragraphs per section (max 20% creative tone). "
        f"For factions: wikitable with Name | Origin | Purpose | Communication Style. "
        f"For tokens/mechanics: bullet list. "
        f"Append inline <ref> citation per section. "
        f"DB-19: ONLY target gkniftyheads.fandom.com. DB-20: Zero Telegram references.\n\n"
        f"PROJECT_DNA:\n{dna_text}\n\n"
        f"CRAWLED DATA:\n{context_text}"
    )

    task = Task(
        description=task_description,
        agent=teacher_agent,
        expected_output="MediaWiki markup with citations for gkniftyheads.fandom.com",
    )

    crew = Crew(agents=[teacher_agent], tasks=[task], verbose=True)
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
