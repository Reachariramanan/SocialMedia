#!/usr/bin/env python3
"""
POC: Fetch latest Google News feeds and tweets for a list of hashtags.

Google feeds  → Google News RSS (no auth)
Tweets        → Nitter RSS (no auth, best-effort) or Twitter API v2 (bearer token)
"""
from __future__ import annotations

import os
import re
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

import feedparser
import httpx

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

# ---------------------------------------------------------------------------
# Nitter instances to try in order (public mirrors, some may be down)
# ---------------------------------------------------------------------------
NITTER_INSTANCES = [
    "https://nitter.net",
    "https://nitter.privacyredirect.com",
    "https://nitter.poast.org",
    "https://nitter.cz",
]

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
GOOGLE_TRENDS_RSS = "https://trends.google.com/trending/rss?geo=IN"
SEARXNG_URL = os.getenv("SEARXNG_URL", "http://localhost:8888")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) FeedsPOC/1.0",
    "Accept": "application/rss+xml, application/xml, text/xml;q=0.9, */*;q=0.8",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean_html(raw: str, max_chars: int = 280) -> str:
    """Strip HTML tags, collapse whitespace."""
    if not raw:
        return ""
    if BeautifulSoup:
        text = BeautifulSoup(raw, "html.parser").get_text(separator=" ")
    else:
        text = re.sub(r"<[^>]+>", "", raw)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars]


# ---------------------------------------------------------------------------
# Google feeds
# ---------------------------------------------------------------------------

def _parse_feed(url: str, limit: int = 15, timeout: float = 20.0) -> List[Dict[str, str]]:
    resp = httpx.get(url, headers=HEADERS, timeout=timeout, follow_redirects=True)
    resp.raise_for_status()
    feed = feedparser.parse(resp.text)
    entries = []
    for item in feed.entries[:limit]:
        entries.append({
            "title": _clean_html(item.get("title", "")),
            "link": item.get("link", ""),
            "published": item.get("published", item.get("updated", "")),
            "source": item.get("source", {}).get("title", "") if hasattr(item.get("source", ""), "get") else "",
            "summary": _clean_html(item.get("summary", "")),
        })
    return entries


def fetch_google_news(hashtag: str, limit: int = 10) -> Dict[str, Any]:
    """Fetch Google News RSS for a single hashtag/keyword."""
    query = hashtag.lstrip("#").strip()
    url = GOOGLE_NEWS_RSS.format(query=quote_plus(query))
    try:
        entries = _parse_feed(url, limit=limit)
        return {"ok": True, "hashtag": hashtag, "source": "google_news_rss", "entries": entries, "error": None}
    except Exception as exc:
        return {"ok": False, "hashtag": hashtag, "source": "google_news_rss", "entries": [], "error": str(exc)}


def fetch_google_trends(limit: int = 20) -> Dict[str, Any]:
    """Fetch top trending topics from Google Trends RSS (India)."""
    try:
        entries = _parse_feed(GOOGLE_TRENDS_RSS, limit=limit)
        return {"ok": True, "source": "google_trends_rss", "entries": entries, "error": None}
    except Exception as exc:
        return {"ok": False, "source": "google_trends_rss", "entries": [], "error": str(exc)}


# ---------------------------------------------------------------------------
# Twitter / X  — via Nitter RSS (no auth)
# ---------------------------------------------------------------------------

def _try_nitter_rss(hashtag: str, limit: int, timeout: float) -> Optional[List[Dict[str, str]]]:
    """Try each Nitter instance until one returns results."""
    tag = hashtag.lstrip("#").strip()
    for instance in NITTER_INSTANCES:
        url = f"{instance}/search/rss?q=%23{quote_plus(tag)}&f=tweets"
        try:
            resp = httpx.get(url, headers=HEADERS, timeout=timeout, follow_redirects=True)
            if resp.status_code != 200:
                continue
            feed = feedparser.parse(resp.text)
            if not feed.entries:
                # also try hashtag path form
                url2 = f"{instance}/hashtag/{quote_plus(tag)}/rss"
                resp2 = httpx.get(url2, headers=HEADERS, timeout=timeout, follow_redirects=True)
                if resp2.status_code == 200:
                    feed = feedparser.parse(resp2.text)
            tweets = []
            for item in feed.entries[:limit]:
                author = ""
                if hasattr(item, "author"):
                    author = item.author
                tweets.append({
                    "text": _clean_html(item.get("title", "")),
                    "author": author,
                    "link": item.get("link", ""),
                    "published": item.get("published", item.get("updated", "")),
                })
            if tweets:
                return tweets
        except Exception:
            continue
    return None


def _try_twitter_api_v2(hashtag: str, bearer_token: str, limit: int, timeout: float) -> Optional[List[Dict[str, str]]]:
    """Fetch recent tweets via Twitter API v2 (requires bearer token)."""
    tag = hashtag.lstrip("#").strip()
    query = f"#{tag} -is:retweet lang:en"
    url = "https://api.twitter.com/2/tweets/search/recent"
    params = {
        "query": query,
        "max_results": min(limit, 100),
        "tweet.fields": "created_at,author_id,text,public_metrics",
        "expansions": "author_id",
        "user.fields": "username,name",
    }
    headers = {**HEADERS, "Authorization": f"Bearer {bearer_token}"}
    try:
        resp = httpx.get(url, params=params, headers=headers, timeout=timeout)
        resp.raise_for_status()
        payload = resp.json()
        users = {u["id"]: u for u in payload.get("includes", {}).get("users", [])}
        tweets = []
        for tw in payload.get("data", []):
            uid = tw.get("author_id", "")
            user = users.get(uid, {})
            tweets.append({
                "text": tw.get("text", "").strip(),
                "author": f"@{user.get('username', uid)}",
                "link": f"https://twitter.com/i/web/status/{tw.get('id', '')}",
                "published": tw.get("created_at", ""),
                "likes": tw.get("public_metrics", {}).get("like_count", 0),
                "retweets": tw.get("public_metrics", {}).get("retweet_count", 0),
            })
        return tweets if tweets else None
    except Exception:
        return None


def _try_searxng_tweets(hashtag: str, limit: int, timeout: float) -> Optional[List[Dict[str, str]]]:
    """Query local SearXNG for tweet URLs matching a hashtag."""
    tag = hashtag.lstrip("#").strip()
    STATUS_RE = re.compile(r'(twitter\.com|x\.com)/[^/]+/status/\d+')
    results = []
    for query in [
        f'site:twitter.com "#{tag}"',
        f'site:x.com "#{tag}"',
        f'site:twitter.com #{tag}',
    ]:
        try:
            resp = httpx.get(
                f"{SEARXNG_URL}/search",
                params={"q": query, "format": "json", "categories": "general"},
                headers=HEADERS,
                timeout=timeout,
                follow_redirects=True,
            )
            if resp.status_code != 200:
                continue
            data = resp.json()
            for item in data.get("results", []):
                url = item.get("url", "")
                if STATUS_RE.search(url):
                    results.append({
                        "text": item.get("title", url),
                        "author": item.get("url", "").split("/")[3] if item.get("url", "").count("/") >= 3 else "",
                        "link": url,
                        "published": item.get("publishedDate", ""),
                    })
        except Exception:
            continue
    seen = set()
    unique = []
    for r in results:
        if r["link"] not in seen:
            seen.add(r["link"])
            unique.append(r)
    return unique[:limit] if unique else None


def fetch_tweets(hashtag: str, limit: int = 10, timeout: float = 15.0) -> Dict[str, Any]:
    """
    Fetch tweets for a hashtag.
    Tries Twitter API v2 first (if TWITTER_BEARER_TOKEN is set), then Nitter RSS.
    """
    bearer = os.getenv("TWITTER_BEARER_TOKEN", "").strip()
    method = "none"
    tweets = None

    if bearer:
        tweets = _try_twitter_api_v2(hashtag, bearer, limit, timeout)
        if tweets is not None:
            method = "twitter_api_v2"

    if tweets is None:
        tweets = _try_nitter_rss(hashtag, limit, timeout)
        if tweets is not None:
            method = "nitter_rss"

    if tweets is None:
        tweets = _try_searxng_tweets(hashtag, limit, timeout)
        if tweets is not None:
            method = "searxng"

    if tweets is None:
        return {
            "ok": False,
            "hashtag": hashtag,
            "source": "none",
            "tweets": [],
            "error": "No tweet sources available (no bearer token, Nitter unreachable, SearXNG returned no results)",
        }

    return {"ok": True, "hashtag": hashtag, "source": method, "tweets": tweets, "error": None}


# ---------------------------------------------------------------------------
# Combined fetch for a list of hashtags
# ---------------------------------------------------------------------------

def fetch_all(
    hashtags: List[str],
    google_limit: int = 10,
    tweet_limit: int = 10,
    delay_sec: float = 0.5,
) -> Dict[str, Any]:
    """Fetch Google News + tweets for every hashtag and return a structured result."""
    results: Dict[str, Any] = {
        "fetched_at_utc": utc_now(),
        "hashtags": hashtags,
        "google_trends": None,
        "feeds": {},
    }

    # Always pull the broader Google Trends snapshot
    results["google_trends"] = fetch_google_trends()

    for tag in hashtags:
        google = fetch_google_news(tag, limit=google_limit)
        time.sleep(delay_sec)
        tweets = fetch_tweets(tag, limit=tweet_limit)
        time.sleep(delay_sec)
        results["feeds"][tag] = {
            "google_news": google,
            "tweets": tweets,
        }

    return results
