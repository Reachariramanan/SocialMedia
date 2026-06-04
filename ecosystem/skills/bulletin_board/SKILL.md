  ---
name: bulletin_board
description: "Structure raw research findings into a bulletin-board format: prioritised story cards with headlines, tags, signals, and source attribution"
version: "1.0.0"
category: formatting
---

# Bulletin Board Skill

## Overview
Transform the research summary into a human-readable bulletin board — an ordered list of story cards ranked by confidence and signal strength. This is the intermediate representation consumed by the DashboardLayoutBuilder.

## The Process

### Step 1: Rank Stories
Sort event candidates by:
1. Signal count (more sources = higher rank)
2. Recency (newer timestamps rank higher)
3. Hashtag trending velocity (Trends24 blocks appearing in multiple time slots)

### Step 2: Format Each Story Card
```json
{
  "rank": 1,
  "title": "Short punchy headline (max 12 words)",
  "tag": "#PrimaryHashtag",
  "summary": "2-sentence plain-English summary of the event",
  "confidence": "high|medium|low",
  "signals": ["trends24", "google_news", "xfetch"],
  "top_headline": "Full headline from the most authoritative source",
  "top_link": "https://...",
  "tweet_sample": "https://x.com/... (optional, first tweet URL if available)",
  "published_approx": "ISO8601 or 'recent'"
}
```

### Step 3: Add a Lede Card
The top story gets a special **lede** treatment:
- A 3-sentence summary (who, what, why it matters).
- Pull-quote: the single most informative sentence from all headlines.

### Step 4: Add a "Watch" Section
List 3–5 emerging signals that don't yet meet the 2-source threshold. Format as:
```json
{ "tag": "#Emerging", "reason": "Only one source, but 18 tweets in last hour" }
```

### Step 5: Output
Return a JSON `bulletin` object with `lede`, `stories` (ranked cards), and `watching` (emerging list), plus metadata: `topic`, `generated_at_utc`, `total_events`.
