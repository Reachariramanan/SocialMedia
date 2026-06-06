---
name: uncle_prompt
description: "High-quality intelligence bulletin HTML with Python data processing, Jinja2 templating, and 3-column grid layout"
version: "2.0.0"
category: rendering
---

# UnclePrompt Skill

## Overview
Produce a high-quality intelligence bulletin as a single self-contained HTML file, incorporating Python-driven data processing and sophisticated visual design.

## Workflow

### Data Processing
- Sentiment analysis using vaderSentiment / textblob on headline and tweet text
- Aggregate signal counts, source diversity score, and trending velocity per event

### HTML Structure
Generate a self-contained HTML file (Tailwind CDN + Chart.js CDN) with this layout:
```
Masthead (title, timestamp, edition line)
→ Banner (lead story hero card, full-width)
→ Main 3-column grid:
    Left column  — story cards ranked by signal count
    Centre       — narrative body, pull-quotes, timeline
    Right sidebar — stats panel, platform comparison chart, source breakdown
→ Footer (metadata, confidence legend)
```

### Typography
- Headlines: Playfair Display, bold, `text-2xl+`
- Body: Source Serif 4, `text-sm leading-relaxed`
- Labels/mono: font-mono, `text-xs uppercase tracking-wider`

### Visualisation
- Chart.js line chart (smooth curves) for sentiment / time-series
- Minimal styling: no gridlines, only bottom axis, area fill at 10% opacity
- Sidebar: stats boxes (big number + label), timeline dots, platform bar comparison

### Style Rules
- Dark background: `#0f172a` (slate-900)
- Card surface: `#1e293b` (slate-800), border `#334155`
- Accent: `#3b82f6` (blue-500)
- Confidence: high → green-400, medium → yellow-400, low → red-400
- Use `rounded-xl border` on all cards

## Output
Emit ONLY the HTML document — no markdown, no explanations.
