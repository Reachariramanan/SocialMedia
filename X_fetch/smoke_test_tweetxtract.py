"""
Smoke test for the tweetxtract tool.

Exercises the discovery pipeline (SearXNG + RSS + feeds → dedup → prioritization)
WITHOUT the Tor + Lightpanda extraction phase, so it can run without Tor/Lightpanda.
Pass --extract to additionally run the Tor extraction phase (needs Lightpanda + Tor).

Run from the X_fetch/ directory:
    python smoke_test_tweetxtract.py
    python smoke_test_tweetxtract.py --query "#NEET" --limit 5 --extract
"""
import argparse
import asyncio
import json

from core.utils.common import setup_logging
from tools.tweetxtract_tool.tweetxtract_agent import TweetXtract

logger = setup_logging("TweetXtractSmoke")


async def main():
    parser = argparse.ArgumentParser(description="Smoke test the tweetxtract tool")
    parser.add_argument("--query", default="#AI", help="Query/hashtag (default: #AI)")
    parser.add_argument("--limit", type=int, default=5, help="Max tweets to discover")
    parser.add_argument("--extract", action="store_true",
                        help="Also run Tor + Lightpanda extraction (needs Tor + Lightpanda)")
    args = parser.parse_args()

    xtract = TweetXtract()

    logger.info(f"=== Discovery phase: {args.query} (limit={args.limit}) ===")
    discovered = await xtract.discover_tweets(args.query, args.limit)
    logger.info(f"Discovered {len(discovered)} tweets")
    for i, t in enumerate(discovered, 1):
        logger.info(f"  {i:2d}. [{t['score']}] {t['url']}  (via {t['discovered_from']})")

    if not discovered:
        logger.warning(
            "No tweets discovered. SearXNG may be down (docker compose up) and/or "
            "RSS/feeds returned nothing. RSS does not need docker — if that is also "
            "empty, check network connectivity."
        )

    result = {
        "query": args.query,
        "discovered_tweets": discovered,
        "total_discovered": len(discovered),
    }

    if args.extract and discovered:
        logger.info("=== Extraction phase (Tor + Lightpanda) ===")
        urls = [t["url"] for t in discovered]
        extractions = await xtract.extract_via_tor_lightpanda(urls)
        result["extractions"] = extractions
        result["extraction_success"] = sum(1 for e in extractions if e.get("tweets"))
        logger.info(f"Extraction succeeded for {result['extraction_success']}/{len(urls)} URLs")

    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
