---
name: action_planning
description: "Analyse a news topic and produce a structured data-collection plan: which sources to query, in what order, with what parameters"
version: "1.0.0"
category: planning
---

# Action Planning Skill

## Overview
Given a topic or a list of topics, decide the optimal data-collection strategy. Produce a concrete, ordered list of tool calls the Researcher should execute, minimising redundancy and maximising signal quality.

## The Process

### Step 1: Classify the Topic
Determine whether the topic is:
- **Breaking news** (time-sensitive, last 6 hours) → prioritise Trends24 + SearXNG
- **Ongoing story** (days-old, evolving) → prioritise feeds + xfetch_discover
- **Background research** (context, history) → prioritise SearXNG + Google News feeds

### Step 2: Extract Keywords and Hashtags
- Convert the topic into 3–6 search keywords (remove stop words).
- Suggest likely Twitter hashtags by prepending `#` to the most prominent nouns.

### Step 3: Build the Collection Plan
Output a JSON plan with the following shape:
```json
{
  "topic": "<original topic>",
  "type": "breaking|ongoing|background",
  "steps": [
    {
      "step": 1,
      "tool": "fetch_trends24",
      "args": { "country": "india", "max_tags": 30 },
      "reason": "Check if topic has trending hashtags right now"
    },
    {
      "step": 2,
      "tool": "fetch_feeds",
      "args": { "hashtags": "#IPL,#CricketNews", "limit": 10 },
      "reason": "Gather Google News articles for top trending tags"
    },
    {
      "step": 3,
      "tool": "xfetch_discover",
      "args": { "keywords": "IPL final 2026", "limit": 40 },
      "reason": "Discover recent tweet URLs for deeper X analysis"
    },
    {
      "step": 4,
      "tool": "searxng_search",
      "args": { "query": "IPL final 2026 highlights", "limit": 10 },
      "reason": "Web search for any breaking news not yet in RSS"
    }
  ]
}
```

### Step 4: Validate the Plan
- Ensure no more than 6 steps total to keep token usage bounded.
- If Trends24 returns no relevant tags, remove the xfetch step and replace with a SearXNG step.
- Always include at least one `fetch_feeds` step so there is structured RSS data for the dashboard.

### Step 5: Output
Return the JSON plan and a one-paragraph plain-English rationale explaining why this ordering was chosen.
