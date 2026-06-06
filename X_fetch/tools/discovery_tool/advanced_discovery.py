import httpx
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict
from core.models.tweet import DiscoveredTweet
from core.config.settings import settings
from core.utils.common import setup_logging, randomized_delay

logger = setup_logging("AdvancedDiscoveryAgent")

class AdvancedDiscoveryAgent:
    def __init__(self):
        self.searxng_url = settings.SEARXNG_URL
        # Engines are selected in SearXNG's own config; querying by category is
        # more reliable than an `engines=` allowlist that may name engines that
        # aren't enabled server-side (which silently returns nothing).
        self.categories = "general"
        # Engines reported by SearXNG as unresponsive on the most recent call
        # (e.g. CAPTCHA / rate-limited). Surfaced so callers can show a degraded state.
        self.last_unresponsive = []

    async def search_searxng(self, query: str, time_range: str = None, tweets_only: bool = True) -> List[DiscoveredTweet]:
        logger.info(f"Searching SearXNG for: {query} (Time Range: {time_range}, Tweets Only: {tweets_only})")
        params = {
            "q": query,
            "format": "json",
            "categories": self.categories,
        }
        if time_range:
            params["time_range"] = time_range

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.searxng_url}/search", params=params)
                response.raise_for_status()
                data = response.json()

                unresponsive = data.get("unresponsive_engines") or []
                self.last_unresponsive = unresponsive
                if unresponsive:
                    logger.warning(f"SearXNG unresponsive engines: {unresponsive}")

                results = []
                for result in data.get("results", []):
                    url = result.get("url", "")
                    if tweets_only and "x.com" not in url and "twitter.com" not in url:
                        continue
                    results.append(DiscoveredTweet(
                        tweet_url=url,
                        discovered_from="SearXNG",
                        query=query,
                        timestamp=datetime.now()
                    ))
                return results
            except Exception as e:
                logger.error(f"SearXNG search failed: {e}")
                self.last_unresponsive = [["searxng", str(e)]]
                return []

    async def temporal_slicing_discovery(self, keyword: str, days: int = 30):
        """Perform discovery by slicing time into daily chunks."""
        end_date = datetime.now()
        for i in range(days):
            current_date = end_date - timedelta(days=i)
            date_str = current_date.strftime("%Y-%m-%d")
            # Query pattern for specific date
            query = f'site:x.com "{keyword}" after:{date_str} before:{(current_date + timedelta(days=1)).strftime("%Y-%m-%d")}'
            
            discovered = await self.search_searxng(query)
            for tweet in discovered:
                logger.info(f"Discovered tweet (Temporal): {tweet.tweet_url}")
                # Push to queue logic here
                
            await randomized_delay(5, 15)

    async def advanced_pattern_discovery(self, keyword: str):
        """Use advanced query patterns for broader discovery."""
        patterns = [
            f'site:x.com/status/ "{keyword}"',
            f'site:x.com/*/status/ "{keyword}"',
            f'site:x.com "{keyword}" -inurl:search',
            f'site:x.com "{keyword}" intitle:tweet',
        ]
        
        for query in patterns:
            discovered = await self.search_searxng(query)
            for tweet in discovered:
                logger.info(f"Discovered tweet (Pattern): {tweet.tweet_url}")
            await randomized_delay(10, 20)

    async def run_comprehensive_discovery(self, keywords: List[str]):
        while True:
            for keyword in keywords:
                await self.advanced_pattern_discovery(keyword)
                await self.temporal_slicing_discovery(keyword, days=7)
            await asyncio.sleep(3600) # Run every hour
