"""
Smoke test: #neet discovery via RSS + SearXNG, then prioritization.
Run from X_fetch/ directory:
    python smoke_test.py

Results saved to:
  - smoke_test_results.json (structured data)
  - smoke_test_results.txt (human readable)
"""
import asyncio
import sys
import json
from datetime import datetime
from pathlib import Path
from core.utils.common import setup_logging
from tools.discovery_tool.rss_ingestion import RSSIngestion
from tools.discovery_tool.advanced_discovery import AdvancedDiscoveryAgent
from tools.url_prioritization_tool.prioritization_agent import URLPrioritizationAgent
from tools.deduplication_tool.deduplication_agent import DeduplicationAgent

logger = setup_logging("SmokeTest")

KEYWORD = "neet"
RESULTS_DIR = Path("smoke_test_results")
RESULTS_DIR.mkdir(exist_ok=True)

async def smoke_rss():
    logger.info("=== [1/3] RSS Ingestion (Google News RSS) ===")
    rss = RSSIngestion()
    results = await rss.fetch_rss(KEYWORD)
    logger.info(f"RSS found {len(results)} tweet URLs")
    for t in results[:5]:
        logger.info(f"  RSS -> {t.tweet_url}")
    return results

async def smoke_searxng():
    logger.info("=== [2/3] SearXNG Discovery ===")
    agent = AdvancedDiscoveryAgent()
    results = []

    queries = [
        f'site:twitter.com "#{KEYWORD}"',
        f'site:x.com "#{KEYWORD}"',
        f'site:twitter.com #{KEYWORD}',
        f'site:x.com #{KEYWORD}',
        f'twitter #{KEYWORD}',
        f'x.com #{KEYWORD}',
        f'"{KEYWORD}" site:twitter.com',
        f'"{KEYWORD}" site:x.com',
    ]

    for query in queries:
        found = await agent.search_searxng(query)
        logger.info(f"  '{query}' -> {len(found)} results")
        results.extend(found)
        await asyncio.sleep(0.5)

    logger.info(f"SearXNG total (pre-dedup): {len(results)} tweet URLs")
    for t in results[:5]:
        logger.info(f"  SearXNG -> {t.tweet_url}")
    return results

def smoke_prioritization(all_discovered):
    logger.info("=== [3/3] URL Prioritization + Deduplication ===")
    dedup = DeduplicationAgent()
    unique = []
    for t in all_discovered:
        if not dedup.is_duplicate(t.tweet_url):
            unique.append(t)

    logger.info(f"After dedup: {len(unique)} unique URLs (from {len(all_discovered)} total)")

    prioritizer = URLPrioritizationAgent()
    # Temporarily add 'neet' to high-value keywords
    prioritizer.high_value_keywords.append("neet")
    prioritized = prioritizer.process_discovered_tweets(unique)
    logger.info(f"After prioritization filter: {len(prioritized)} high-value URLs")
    for i, t in enumerate(prioritized, 1):
        score = prioritizer.calculate_priority(t)
        logger.info(f"  {i:2d}. [{score:.2f}] {t.tweet_url}  (via {t.discovered_from})")
    return prioritized

def save_results(prioritized_urls):
    timestamp = datetime.now().isoformat()

    # Save as JSON (structured)
    json_file = RESULTS_DIR / f"smoke_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    json_data = {
        "keyword": KEYWORD,
        "timestamp": timestamp,
        "total_urls": len(prioritized_urls),
        "urls": [
            {
                "url": t.tweet_url,
                "discovered_from": t.discovered_from,
                "query": t.query,
                "discovered_at": t.timestamp.isoformat()
            }
            for t in prioritized_urls
        ]
    }
    with open(json_file, "w") as f:
        json.dump(json_data, f, indent=2)
    logger.info(f"✓ Saved JSON results to {json_file}")

    # Save as human-readable text
    txt_file = RESULTS_DIR / f"smoke_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(txt_file, "w") as f:
        f.write(f"X/Twitter Discovery Smoke Test Results\n")
        f.write(f"{'='*60}\n")
        f.write(f"Keyword: #{KEYWORD}\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Total Unique URLs: {len(prioritized_urls)}\n")
        f.write(f"{'='*60}\n\n")

        prioritizer = URLPrioritizationAgent()
        prioritizer.high_value_keywords.append(KEYWORD)

        for i, t in enumerate(prioritized_urls, 1):
            score = prioritizer.calculate_priority(t)
            f.write(f"{i:2d}. [{score:.2f}] {t.tweet_url}\n")
            f.write(f"    From: {t.discovered_from} | Query: {t.query}\n")
            f.write(f"    Time: {t.timestamp.isoformat()}\n\n")

    logger.info(f"✓ Saved text results to {txt_file}")
    return json_file, txt_file

async def main():
    logger.info(f"Starting smoke test for keyword: #{KEYWORD}")

    rss_results = await smoke_rss()
    searxng_results = await smoke_searxng()

    all_results = rss_results + searxng_results
    if not all_results:
        logger.warning("No URLs discovered. Check if SearXNG is running (docker compose up).")
        logger.info("RSS test does not need docker. If RSS also returned 0, check network.")
        sys.exit(1)

    prioritized = smoke_prioritization(all_results)
    json_file, txt_file = save_results(prioritized)

    logger.info(f"=== Smoke test complete ===")
    logger.info(f"Results saved to:")
    logger.info(f"  JSON: {json_file}")
    logger.info(f"  Text: {txt_file}")

if __name__ == "__main__":
    asyncio.run(main())
