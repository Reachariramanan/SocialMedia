"""
Integration layer: use Tor + Lightpanda (via torpanda) to extract content from discovered URLs.
Injects scrapePostsFromPage() from scrape.js via page.evaluate() for structured tweet data.

Run from the X_fetch/ directory so `core.*` imports resolve.
"""
import asyncio
import os
from typing import List, Dict, Optional
from pathlib import Path

from playwright.async_api import async_playwright, Browser, BrowserContext

from core.utils.common import setup_logging

logger = setup_logging("TorPandaExtractor")

# Lightpanda runs inside Docker — "tor" hostname resolves within Docker network.
# Playwright connects to Lightpanda via CDP from host; proxy config is applied by Lightpanda.
TOR_SOCKS_HOST = os.getenv("TOR_HOST", "tor")
TOR_SOCKS_PORT = int(os.getenv("TOR_PORT", "9050"))
CDP_ENDPOINT = os.getenv("CDP_ENDPOINT", "http://127.0.0.1:9222")
GOTO_TIMEOUT_MS = 30000
TWEET_WAIT_MS = 15000


def _load_scrape_fn() -> str:
    """Extract scrapePostsFromPage() body from scrape.js for use in page.evaluate()."""
    js_path = Path(__file__).parent / "scrape.js"
    src = js_path.read_text()

    marker = "function scrapePostsFromPage()"
    start = src.find(marker)
    if start == -1:
        raise RuntimeError("scrapePostsFromPage() not found in scrape.js")

    # Find the opening brace
    brace_start = src.index("{", start)
    depth = 0
    i = brace_start
    for i, ch in enumerate(src[brace_start:], brace_start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                break

    fn_source = src[start : i + 1]
    return fn_source


# Load once at import time
try:
    _SCRAPE_FN = _load_scrape_fn()
except Exception as e:
    _SCRAPE_FN = None
    logger.warning(f"Could not load scrape.js: {e}")


class TorPandaExtractor:
    """Extract tweet data via Tor + Lightpanda using the scrape.js DOM scraper."""

    def __init__(self, use_tor: bool = True):
        self.use_tor = use_tor
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None

    async def connect(self):
        """Connect to Chromium via CDP."""
        try:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.connect_over_cdp(CDP_ENDPOINT)
            logger.info(f"Connected to browser via CDP: {CDP_ENDPOINT}")

            if self.use_tor:
                logger.info(f"Creating context with Tor proxy: {TOR_SOCKS_HOST}:{TOR_SOCKS_PORT}")
                self.context = await self.browser.new_context(
                    proxy={
                        "server": f"socks5://{TOR_SOCKS_HOST}:{TOR_SOCKS_PORT}",
                        "username": "",
                        "password": "",
                    }
                )
            else:
                self.context = await self.browser.new_context()

            return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False

    async def disconnect(self):
        """Close browser and context."""
        if self.context:
            try:
                await self.context.close()
            except Exception:
                pass
        if self.browser:
            try:
                await self.browser.close()
            except Exception:
                pass
        logger.info("Disconnected from browser")

    async def scrape_tweet(self, url: str) -> Dict:
        """
        Navigate to tweet URL via Tor, wait for DOM, inject scrapePostsFromPage(),
        and return structured tweet data.
        """
        if not self.context:
            return {"url": url, "status": "error", "error": "Not connected", "tweets": []}

        if not _SCRAPE_FN:
            return {"url": url, "status": "error", "error": "scrape.js not loaded", "tweets": []}

        logger.info(f"Scraping: {url}")
        page = None

        try:
            page = await self.context.new_page()

            response = await asyncio.wait_for(
                page.goto(url, wait_until="networkidle", timeout=GOTO_TIMEOUT_MS),
                timeout=GOTO_TIMEOUT_MS / 1000 + 5,
            )

            if response is None or not response.ok:
                status_code = response.status if response else "unknown"
                logger.warning(f"  -> HTTP {status_code}")
                return {"url": url, "status": "error", "http_status": status_code, "tweets": []}

            # Wait for tweet articles to render
            try:
                await page.wait_for_selector(
                    'article[data-testid="tweet"]',
                    timeout=TWEET_WAIT_MS,
                )
            except Exception:
                logger.warning(f"  -> No tweet articles found in DOM (JS may not have rendered)")
                return {"url": url, "status": "no_tweets", "tweets": []}

            # Inject the scraper function and run it in page context
            tweets = await page.evaluate(f"({_SCRAPE_FN})()")

            logger.info(f"  ✓ Scraped {len(tweets)} tweet(s) from {url}")

            return {
                "url": url,
                "status": "success" if tweets else "no_tweets",
                "tweets": tweets,
                "tor_verified": False,  # skip verification to keep page context clean
            }

        except asyncio.TimeoutError:
            logger.warning(f"  -> Timeout after {GOTO_TIMEOUT_MS / 1000}s")
            return {"url": url, "status": "timeout", "error": f"Timeout after {GOTO_TIMEOUT_MS / 1000}s", "tweets": []}
        except Exception as e:
            logger.error(f"  -> Error: {type(e).__name__}: {e}")
            return {"url": url, "status": "error", "error": str(e), "tweets": []}
        finally:
            if page:
                try:
                    await page.close()
                except Exception:
                    pass


async def extract_from_urls(urls: List[str], use_tor: bool = True) -> List[Dict]:
    """Extract structured tweet data from a list of URLs via Tor + Lightpanda.

    Connects to the browser once and reuses the context across all URLs
    (scrape_tweet closes its own per-URL page), reconnecting once if the
    connection is lost mid-batch. This avoids a full CDP connect/disconnect
    per tweet.
    """
    results: List[Dict] = []
    if not urls:
        return results

    extractor = TorPandaExtractor(use_tor=use_tor)
    connected = await extractor.connect()

    try:
        for url in urls:
            if not connected:
                # Try to recover the session once before giving up on this URL.
                await extractor.disconnect()
                extractor = TorPandaExtractor(use_tor=use_tor)
                connected = await extractor.connect()
                if not connected:
                    logger.warning(f"Failed to (re)connect for {url}")
                    results.append({"url": url, "status": "error", "error": "Connection failed", "tweets": []})
                    continue

            result = await extractor.scrape_tweet(url)
            results.append(result)

            # A connection-level failure (vs. a page-level one) means the shared
            # context is likely dead — force a reconnect before the next URL.
            if result.get("status") == "error" and "connect" in str(result.get("error", "")).lower():
                connected = False

            await asyncio.sleep(0.5)
    finally:
        await extractor.disconnect()

    return results
