"""Thin wrapper over poc_feeds.fetcher.fetch_all."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'poc_feeds'))

from fetcher import fetch_all


def run(hashtags: str, limit: int = 8) -> dict:
    tags = [t.strip() for t in hashtags.split(',') if t.strip()]
    if not tags:
        return {"error": "no hashtags provided"}
    return fetch_all(tags, google_limit=limit, tweet_limit=limit)
