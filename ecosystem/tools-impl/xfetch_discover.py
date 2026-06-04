"""Wrap X_fetch AdvancedDiscoveryAgent pipeline as a synchronous tool."""
import sys, os, asyncio, re, time
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'X_fetch'))

try:
    from tools.discovery_tool.advanced_discovery import AdvancedDiscoveryAgent
    from tools.discovery_tool.rss_ingestion import RSSIngestion
    from tools.deduplication_tool.deduplication_agent import DeduplicationAgent
    from tools.url_prioritization_tool.prioritization_agent import URLPrioritizationAgent
    _XFETCH_OK = True
except ImportError as e:
    _XFETCH_OK = False
    _XFETCH_ERR = str(e)

_STATUS_URL = re.compile(r'twitter\.com/\w+/status/\d+|x\.com/\w+/status/\d+', re.I)
_JUNK = re.compile(r'twitter\.com/(search|hashtag|explore|home|i/|intent/)')


def _is_status(url: str) -> bool:
    return not _JUNK.search(url) and bool(_STATUS_URL.search(url))


async def _discover(keywords: list, limit: int) -> dict:
    discovery = AdvancedDiscoveryAgent()
    rss = RSSIngestion()
    dedup = DeduplicationAgent()
    prio = URLPrioritizationAgent()
    for kw in keywords:
        prio.high_value_keywords.append(kw.lower())

    all_found = []
    patterns = [
        'site:twitter.com "#{kw}"', 'site:x.com "#{kw}"',
        'site:twitter.com #{kw}', 'site:x.com #{kw}',
    ]
    for kw in keywords:
        for pat in patterns:
            all_found.extend(await discovery.search_searxng(pat.replace('{kw}', kw)))
        all_found.extend(await rss.fetch_rss(kw))

    unique = [t for t in all_found if not dedup.is_duplicate(t.tweet_url)]
    status_only = [t for t in unique if _is_status(t.tweet_url)]
    prioritized = prio.process_discovered_tweets(status_only)[:limit]

    src_counts: dict = {}
    for t in prioritized:
        src_counts[t.discovered_from] = src_counts.get(t.discovered_from, 0) + 1

    return {
        "keywords": keywords,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total": len(prioritized),
        "raw_discovered": len(all_found),
        "after_dedup": len(unique),
        "sources": src_counts,
        "urls": [
            {
                "url": t.tweet_url,
                "discovered_from": t.discovered_from,
                "query": t.query,
                "score": round(prio.calculate_priority(t), 2),
                "discovered_at": t.timestamp.isoformat(),
            }
            for t in prioritized
        ],
    }


def run(keywords: str, limit: int = 50) -> dict:
    if not _XFETCH_OK:
        return {"error": f"X_fetch not available: {_XFETCH_ERR}"}
    kws = [k.strip().lstrip('#') for k in keywords.split(',') if k.strip()]
    if not kws:
        return {"error": "no keywords provided"}
    t0 = time.time()
    result = asyncio.run(_discover(kws, limit))
    result["elapsed_sec"] = round(time.time() - t0, 2)
    return result
