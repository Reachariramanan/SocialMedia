---
name: dashboarder
description: "Convert a bulletin board into a dashboard layout specification (JSON grid of typed cards) that the ReportWriter will render as HTML"
version: "1.0.0"
category: layout
---

# Dashboarder Skill

## Overview
Take the bulletin board and produce a JSON layout specification describing the dashboard grid. The layout must be renderable as a self-contained HTML file with Tailwind CSS (CDN) + Chart.js (CDN). Each section maps to a typed card component.

## The Process

### Step 1: Determine Grid Structure
Use a 12-column responsive grid. Standard layout:
```
[  HERO BANNER (full width)                    ]
[  TOP STORY (8 col)   | METRICS (4 col)       ]
[  TIMELINE (12 col)                           ]
[  STORIES GRID (4 col each, up to 3 per row) ]
[  X/TWEET SUMMARY (6 col) | SOURCES (6 col)  ]
```

### Step 2: Map Bulletin to Cards
Produce a `cards` array. Each card has:
```json
{
  "id": "unique-slug",
  "type": "hero|story|timeline|metrics|tweet_summary|sources|watch",
  "cols": 12,
  "data": { ... type-specific payload ... }
}
```

**Card type payloads:**

`hero`:
```json
{ "headline": "...", "subline": "...", "tag": "#...", "timestamp": "..." }
```

`story`:
```json
{ "rank": 1, "title": "...", "summary": "...", "link": "...", "tag": "#...", "confidence": "high" }
```

`timeline`:
```json
{ "label": "Trend Timeline", "entries": [{ "time": "...", "tag": "#...", "count": 5 }] }
```

`metrics`:
```json
{ "label": "Signal Metrics", "items": [{ "name": "Total Events", "value": 7 }, { "name": "Sources Used", "value": 4 }] }
```

`tweet_summary`:
```json
{ "label": "X/Twitter Signals", "total_urls": 42, "top_keywords": ["IPL", "Modi"], "sample_urls": ["..."] }
```

`sources`:
```json
{ "label": "Data Sources", "sources": [{ "name": "Google News", "count": 18 }, { "name": "Trends24", "count": 30 }] }
```

`watch`:
```json
{ "label": "Watch List", "items": [{ "tag": "#...", "reason": "..." }] }
```

### Step 3: Output the Layout Spec
Return:
```json
{
  "layout_version": "1.0",
  "topic": "...",
  "generated_at_utc": "...",
  "theme": "dark",
  "cards": [ ... ]
}
```

### Step 4: Validation
- Every layout must have exactly 1 `hero` card.
- Stories are capped at 6 (3×2 grid).
- Timeline entries are capped at 20.
- No card's `data` payload should exceed 2000 characters JSON-encoded.
