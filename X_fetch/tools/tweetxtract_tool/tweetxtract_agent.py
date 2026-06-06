"""
Discover tweets from X via hashtag/query, then extract content via Tor + Lightpanda.
Composes the existing X_fetch tools (discovery, RSS, dedup, prioritization) with the
extraction_tool's Tor+Lightpanda browser.

Run from the X_fetch/ directory so `tools.*` / `core.*` imports resolve.
"""
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict

from tools.discovery_tool.advanced_discovery import AdvancedDiscoveryAgent
from tools.discovery_tool.rss_ingestion import RSSIngestion
from tools.deduplication_tool.deduplication_agent import DeduplicationAgent
from tools.url_prioritization_tool.prioritization_agent import URLPrioritizationAgent
from tools.extraction_tool.torpanda_extractor import extract_from_urls
from core.utils.common import setup_logging

from .html_cleaner import clean_html

try:
    from tools.feeds_fetch_tool.fetcher import fetch_tweets as fetch_tweets_from_feeds
except ImportError:
    fetch_tweets_from_feeds = None

logger = setup_logging("TweetXtract")


class _MinimalTweet:
    """Minimal tweet object for feeds_tool results (mirrors DiscoveredTweet attrs)."""
    def __init__(self, tweet_url, source, query_str, text):
        self.tweet_url = tweet_url
        self.discovered_from = source
        self.query = query_str
        self.timestamp = datetime.now()
        self.snippet = clean_html(text)


class TweetXtract:
    """Discover tweets and extract content via Tor + Lightpanda."""

    def __init__(self):
        self.discovery = AdvancedDiscoveryAgent()
        self.rss = RSSIngestion()
        self.dedup = DeduplicationAgent()
        self.prio = URLPrioritizationAgent()
        self.results_dir = Path("tweetxtract_results")
        self.results_dir.mkdir(exist_ok=True)

    async def discover_tweets(self, query: str, limit: int = 10) -> List[Dict]:
        """Discover tweets using X_fetch discovery tools + feeds tool."""
        logger.info(f"Discovering tweets for query: {query}")

        all_found = []

        # Normalize query (remove # if present for flexible pattern building)
        query_clean = query.lstrip("#").strip()

        # Expand SearXNG patterns: quoted, unquoted, site-specific, broader queries
        patterns = [
            f'site:twitter.com "#{query_clean}"',
            f'site:x.com "#{query_clean}"',
            f'site:twitter.com #{query_clean}',
            f'site:x.com #{query_clean}',
            f'"{query_clean}" site:twitter.com',
            f'"{query_clean}" site:x.com',
            f'#{query_clean} (verified OR popular)',
            f'from:{query_clean} OR #{query_clean}',
        ]

        for pattern in patterns:
            try:
                results = await self.discovery.search_searxng(pattern)
                logger.info(f"  Pattern '{pattern}' → {len(results)} results")
                all_found.extend(results)
                await asyncio.sleep(0.2)
            except Exception as e:
                logger.warning(f"  Pattern '{pattern}' failed: {e}")

        # RSS ingestion (Google News RSS → DiscoveredTweet objects)
        try:
            rss_results = await self.rss.fetch_rss(query_clean)
            logger.info(f"  RSS → {len(rss_results)} results")
            all_found.extend(rss_results)
        except Exception as e:
            logger.warning(f"  RSS failed: {e}")

        # Try feeds_fetch_tool (Nitter + Twitter API + SearXNG variant)
        if fetch_tweets_from_feeds:
            try:
                logger.info(f"  Fetching via feeds_tool...")
                feeds_result = fetch_tweets_from_feeds(query_clean, limit=20, timeout=10.0)
                if feeds_result.get("ok") and feeds_result.get("tweets"):
                    logger.info(f"  Feeds tool ({feeds_result['source']}) → {len(feeds_result['tweets'])} results")
                    for tweet in feeds_result["tweets"]:
                        url = tweet.get("link", "")
                        if url and ("twitter.com" in url or "x.com" in url):
                            all_found.append(_MinimalTweet(url, feeds_result['source'], query, tweet.get("text", "")))
            except Exception as e:
                logger.warning(f"  Feeds tool failed: {e}")

        # Dedup
        unique = []
        seen_urls = set()
        for t in all_found:
            url = getattr(t, 'tweet_url', '')
            if url and url not in seen_urls and not self.dedup.is_duplicate(url):
                unique.append(t)
                seen_urls.add(url)

        logger.info(f"After dedup: {len(unique)} unique tweets")

        # Prioritize — increase limit to get more results before filtering
        self.prio.high_value_keywords.append(query_clean.lower())
        prioritized = self.prio.process_discovered_tweets(unique)[: limit * 2]  # Get 2x to account for spam

        logger.info(f"After prioritization: {len(prioritized)} results (returning top {limit})")

        return [
            {
                "url": t.tweet_url,
                "discovered_from": t.discovered_from,
                "query": t.query,
                "timestamp": t.timestamp.isoformat(),
                "score": round(self.prio.calculate_priority(t), 2),
                "snippet": getattr(t, "snippet", ""),
            }
            for t in prioritized[:limit]
        ]

    async def extract_via_tor_lightpanda(self, urls: List[str]) -> List[Dict]:
        """
        Open each URL via Tor + Lightpanda and extract content.
        """
        logger.info(f"Extracting content from {len(urls)} URLs via Tor + Lightpanda")

        results = await extract_from_urls(urls, use_tor=True)

        for r in results:
            r["extracted_at"] = datetime.now().isoformat()

        return results

    async def run(self, query: str, limit: int = 10) -> Dict:
        """Main flow: discover tweets via SearXNG/RSS/feeds, then extract via Tor.

        Architecture:
        - Discovery (SearXNG/RSS/feeds_tool) → direct HTTP (fast, many sources unavailable over Tor)
        - Extraction (all X URLs) → Tor + Lightpanda (anonymous content access)

        Any X.com/twitter.com URLs found during discovery are anonymously extracted
        in the extraction phase, ensuring content retrieval is private even if
        discovery was via direct HTTP.
        """
        logger.info(f"=== TweetXtract: {query} ===")

        discovered = await self.discover_tweets(query, limit)
        logger.info(f"Discovered {len(discovered)} tweets")

        urls = [t["url"] for t in discovered]
        extractions = await self.extract_via_tor_lightpanda(urls)

        result = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "discovered_tweets": discovered,
            "extractions": extractions,
            "total_discovered": len(discovered),
            "extraction_success": sum(1 for e in extractions if e.get("tweets")),
        }

        return result

    def save_results(self, result: Dict) -> str:
        """Save results to JSON."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        query_safe = result["query"].replace("#", "").replace(" ", "_")
        filename = self.results_dir / f"tweetxtract_{query_safe}_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(result, f, indent=2)

        logger.info(f"Results saved to {filename}")
        return str(filename)
