"""Thin wrapper over the X_fetch feeds fetcher's fetch_all."""
import sys, os

# Reuse the maintained fetcher at X_fetch/tools/feeds_fetch_tool/fetcher.py.
# Prefer the package import (server.py puts X_fetch on sys.path); fall back to
# inserting the directory so this also works when run standalone.
try:
    from tools.feeds_fetch_tool.fetcher import fetch_all
except ImportError:
    _XFETCH = os.path.join(os.path.dirname(__file__), '..', '..', 'X_fetch')
    sys.path.insert(0, _XFETCH)
    sys.path.insert(0, os.path.join(_XFETCH, 'tools', 'feeds_fetch_tool'))
    try:
        from tools.feeds_fetch_tool.fetcher import fetch_all
    except ImportError:
        from fetcher import fetch_all


def run(hashtags: str, limit: int = 8) -> dict:
    tags = [t.strip() for t in hashtags.split(',') if t.strip()]
    if not tags:
        return {"error": "no hashtags provided"}
    return fetch_all(tags, google_limit=limit, tweet_limit=limit)
