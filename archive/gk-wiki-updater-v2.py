"""
gk-wiki-updater-v2.py — GK BRAIN Fandom Wiki Updater v2

Thin wrapper around the shared fandom_auth module that provides a simple
page-update interface.  Inherits all improvements from fandom_auth.py:

    - Two-step Fandom/MediaWiki clientlogin
    - Retry with exponential backoff (3 attempts, 2 s / 4 s / 8 s)
    - Content-hash deduplication (skips unchanged pages)
    - Dry-run mode (WIKI_DRY_RUN=1)
    - Consistent logging via Python logging

Environment variables (all handled by fandom_auth.py):
    FANDOM_BOT_USER       Fandom bot username (preferred over FANDOM_USERNAME)
    FANDOM_USERNAME       Fandom username (fallback)
    FANDOM_BOT_PASSWORD   Fandom bot password (preferred over FANDOM_PASSWORD)
    FANDOM_PASSWORD       Fandom password (fallback)
    FANDOM_WIKI_URL       Wiki base URL (default: https://gkniftyheads.fandom.com)
    WIKI_DRY_RUN          Set to "1" to skip all actual writes (default: disabled)
    WIKI_API_DELAY        Seconds to sleep between API write calls (default: 1.0)
"""

import logging
from typing import Optional

import requests

import fandom_auth

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("gk-wiki-updater-v2")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def update_wiki_page(
    title: str,
    content: str,
    summary: str = "GK BRAIN automated update",
    session: Optional[requests.Session] = None,
) -> bool:
    """
    Update *title* on the Fandom wiki with *content*.

    If *session* is not provided, a new authenticated session is created.
    Passing an existing session avoids repeated logins when updating
    multiple pages in a single run.

    Returns True on success (including no-op if content is unchanged).
    """
    if session is None:
        session = fandom_auth.create_session()
        if session is None:
            logger.error("Could not create authenticated session.")
            return False

    return fandom_auth.edit_page(session, title, content, summary)


def append_wiki_page(
    title: str,
    section_wikitext: str,
    summary: str = "GK BRAIN automated append",
    session: Optional[requests.Session] = None,
) -> bool:
    """
    Append *section_wikitext* to the bottom of *title*.

    If *session* is not provided, a new authenticated session is created.

    Returns True on success.
    """
    if session is None:
        session = fandom_auth.create_session()
        if session is None:
            logger.error("Could not create authenticated session.")
            return False

    return fandom_auth.append_to_page(session, title, section_wikitext, summary)


def get_page(
    title: str,
    session: Optional[requests.Session] = None,
) -> str:
    """
    Fetch the current wikitext of *title*.

    Returns an empty string if the page does not exist.
    """
    if session is None:
        session = fandom_auth.create_session()
        if session is None:
            logger.error("Could not create authenticated session.")
            return ""

    return fandom_auth.get_page_content(session, title)


# ---------------------------------------------------------------------------
# CLI self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python gk-wiki-updater-v2.py <page_title> <content>")
        sys.exit(1)

    page_title = sys.argv[1]
    page_content = sys.argv[2]

    ok = update_wiki_page(page_title, page_content)
    print("Success:", ok)
