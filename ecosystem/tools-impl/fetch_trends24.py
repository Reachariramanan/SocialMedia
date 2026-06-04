"""Extract Trends24 scraping from bot.py and expose as a standalone tool."""
import sys, os, time
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

LIGHTPANDA_CDP = os.getenv("LIGHTPANDA_CDP_URL", "http://127.0.0.1:9222")


def run(country: str = "worldwide", max_tags: int = 30) -> dict:
    from bot import scrape_trends24, gather_tags

    try:
        payload = scrape_trends24(cdp_url=LIGHTPANDA_CDP, timeout_ms=30000)
        tags = gather_tags(payload, max_tags=max_tags)
        return {
            "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
            "country": country,
            "tags": tags,
            "blocks": payload.get("blocks", [])[:20],
            "total_blocks": len(payload.get("blocks", [])),
        }
    except Exception as exc:
        return {
            "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
            "country": country,
            "error": str(exc),
            "tags": [],
            "blocks": [],
        }
