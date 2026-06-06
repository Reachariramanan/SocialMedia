---
name: trend_research
description: "Execute a collection plan step-by-step using available tools, cross-reference sources, identify event candidates, and produce a structured research summary with actual tweet content"
version: "1.1.0"
category: research
---

# Trend Research Skill

## Overview
Execute the collection plan produced by ActionPlanner. For each tool call, interpret the results, cross-reference findings across sources, identify event candidates (topics with 2+ independent source signals), extract actual tweet content for the top events, and produce a structured JSON research summary ready for the DashboardLayoutBuilder.

## Available Tools

| Tool | What it does | When to use |
|------|-------------|-------------|
| `fetch_trends24` | Trending hashtags from Trends24 | Always: run first to discover trending topics |
| `fetch_feeds` | Google News RSS + articles for hashtags | For each top hashtag: get headlines and article links |
| `xfetch_discover` | Discover X/Twitter status URLs via SearXNG + RSS | For top 3–5 event candidates: get tweet URLs |
| `xfetch_extract` | Extract tweet *text* from URLs via Tor + Lightpanda | AFTER xfetch_discover: get actual tweet content |
| `searxng_search` | Targeted web search with custom site: filters | When you need site-specific results or custom engines |
| `websearch_general` | Broad web search — no platform filter | For wider context: articles, blogs, mainstream news |
| `facebook_search` | Search Facebook posts via site:facebook.com | To find public Facebook discussions about top events |
| `terminal` | Shell command (curl, etc.) | Last resort only for top 2 events |

## The Process

### Step 1: Execute the Plan
Run each tool call from the plan in order. For each step:
- Call the tool with the provided arguments.
- Record key findings: top tags, headlines, tweet count, errors.

### Step 2: Discover Tweet URLs
For each top event candidate, call `xfetch_discover` to get real tweet URLs:
```
xfetch_discover(keywords="IPL,cricket", limit=20)
```
This returns a list of `{url, score, discovered_from}` objects — URLs only, no content yet.

### Step 3: Extract Tweet Content (REQUIRED for reports)
Take the top tweet URLs from xfetch_discover and call `xfetch_extract`:
```
xfetch_extract(urls="https://x.com/user/status/123,https://x.com/user/status/456", limit=10)
```
- Pass up to 15 URLs per call (each URL costs ~3 tweets × 120 tokens = 360 tokens; 15 URLs ≈ 5 400 tokens)
- `xfetch_extract` returns `{ok, tweets_yaml, total, success, elapsed_sec}`
- `tweets_yaml` is a compact YAML block — each URL becomes a `- src:` entry with nested tweets
- Each tweet has: `by`, `at`, `eng` (engagement counts), `text` (body, up to 320 chars)
- Use `tweets_yaml` content directly as tweet evidence in event_candidates[].sample_tweets
- If extraction fails (Tor unavailable, timeout), fall back to snippet/headline-only mode

**Token budget discipline:**
- Run `xfetch_extract` once per research session, not once per event
- Bundle all priority URLs into one call: `urls="url1,url2,url3,..."`
- If `xfetch_discover` returns 30+ URLs, pass only the top 15 by score

### Step 3b: Broader Web Context
After extracting tweets, call `websearch_general` for top 2–3 events to get mainstream coverage:
```
websearch_general(query="IPL final 2024 results", limit=20)
```

### Step 3c: Facebook signals (optional)
For events with strong social media presence, call `facebook_search`:
```
facebook_search(keywords="IPL,cricket", limit=20)
```
Include any relevant Facebook results in `raw_sources.facebook` of the research summary.

### Step 4: Cross-Reference Sources
After all tools have run:
- Which hashtags appear in both Trends24 and Google News? → high confidence event
- Which headlines repeat across 2+ RSS sources? → confirmed story
- Which tweet texts cluster around the same keyword? → social signal

### Step 5: Identify Event Candidates
An event candidate requires at least two signals from different sources. Format:
```json
{
  "tag": "#IPL",
  "confidence": "high|medium|low",
  "signals": ["trends24", "google_news", "xfetch"],
  "top_headline": "...",
  "tweet_count": 12,
  "links": ["https://..."],
  "sample_tweets": [
    {"text": "...", "author": "...", "likes": 1240, "retweets": 380}
  ]
}
```

### Step 6: Produce Research Summary
Output a single JSON document:
```json
{
  "topic": "<original topic>",
  "researched_at_utc": "<ISO8601>",
  "top_tags": ["#IPL", "#Modi", ...],
  "event_candidates": [...],
  "top_headlines": [
    {"title": "...", "source": "google_news", "url": "...", "published": "..."}
  ],
  "tweet_urls": ["https://x.com/...", ...],
  "tweets_yaml": "- src: https://x.com/...\n  tweets: # N\n  - # tweet 1\n    by: ...\n    eng: ❤1.2k 🔁300\n    text: |\n      ...",
  "searxng_results": [...],
  "raw_sources": {
    "trends24": {...},
    "feeds": {...},
    "xfetch": {...},
    "searxng": {...}
  }
}
```

### Step 7: Flag Low-Confidence Signals
Add a `warnings` array for:
- Tools that returned errors or empty results
- Topics with only 1 source signal
- `xfetch_extract` failures (Tor/Lightpanda unavailable)
- Potentially stale data

### Step 8: Terminal (last resort only)
Only if a critical headline needs quick content extraction and `xfetch_extract` failed:
```
terminal("curl -s 'https://...' | python3 -c \"import sys,re; print(re.sub(r'<[^>]+>','',sys.stdin.read()))[:800]\"")
```
Limit to top 2 event candidates to stay within token budget.
