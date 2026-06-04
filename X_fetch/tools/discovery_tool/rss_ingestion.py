import httpx
import feedparser
import asyncio
from datetime import datetime
from typing import List
from core.models.tweet import DiscoveredTweet
from core.utils.common import setup_logging, randomized_delay

logger = setup_logging("RSSIngestion")

class RSSIngestion:
    def __init__(self):
        self.base_url = "https://news.google.com/rss/search?q=site:x.com+"

    async def fetch_rss(self, keyword: str) -> List[DiscoveredTweet]:
        url = f"{self.base_url}{keyword}"
        logger.info(f"Fetching RSS feed for: {keyword}")
        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                feed = feedparser.parse(response.text)
                results = []
                for entry in feed.entries:
                    # Extract X.com URL from entry link or description if possible
                    # This is a simplified version
                    if "x.com" in entry.link or "twitter.com" in entry.link:
                        results.append(DiscoveredTweet(
                            tweet_url=entry.link,
                            discovered_from="Google News RSS",
                            query=keyword,
                            timestamp=datetime.now()
                        ))
                return results
            except Exception as e:
                logger.error(f"RSS fetch failed: {e}")
                return []

    async def run_rss_loop(self, keywords: List[str]):
        while True:
            for keyword in keywords:
                discovered = await self.fetch_rss(keyword)
                for tweet in discovered:
                    logger.info(f"Discovered from RSS: {tweet.tweet_url}")
                await randomized_delay(60, 120)
