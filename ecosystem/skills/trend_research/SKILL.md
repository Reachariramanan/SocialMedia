---
name: trend_research
description: "Execute a collection plan step-by-step using available tools, cross-reference sources, identify event candidates, and produce a structured research summary"
version: "1.0.0"
category: research
---

# Trend Research Skill

## Overview
Execute the collection plan produced by ActionPlanner. For each tool call, interpret the results, cross-reference findings across sources, identify event candidates (topics with 2+ independent source signals), and produce a structured JSON research summary ready for the DashboardLayoutBuilder.

## The Process

### Step 1: Execute the Plan
Run each tool call from the plan in order. For each step:
- Call the tool with the provided arguments.
- Record the raw result.
- Note key findings: top 5 tags, top 5 headlines, tweet count, any errors.

### Step 2: Cross-Reference Sources
After all tools have run, compare results:
- Which hashtags appear in **both** Trends24 and Google News feeds? → high confidence event.
- Which headlines are repeated across 2+ RSS sources? → confirmed story.
- Which tweet URLs cluster around the same keyword? → social signal.

### Step 3: Identify Event Candidates
An event candidate requires at least two signals from different sources. Format:
```json
{
  "tag": "#IPL",
  "confidence": "high|medium|low",
  "signals": ["trends24", "google_news", "xfetch"],
  "top_headline": "...",
  "tweet_count": 12,
  "links": ["https://..."]
}
```

### Step 4: Produce Research Summary
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
  "searxng_results": [...],
  "raw_sources": {
    "trends24": {...},
    "feeds": {...},
    "xfetch": {...},
    "searxng": {...}
  }
}
```

### Step 5: Flag Low-Confidence Signals
Add a `warnings` array for:
- Tools that returned errors or empty results.
- Topics with only 1 source signal.
- Potentially stale data (Trends24 blocks older than 3 hours).

### Step 6: Use the Terminal if Needed
If a headline contains a URL that needs quick content extraction, use the `terminal` tool:
```
terminal("curl -s 'https://...' | python3 -c \"import sys,re; print(re.sub(r'<[^>]+>','',sys.stdin.read()))[:1000]\"")
```
Only do this for the top 2 event candidates to stay within token budget.
