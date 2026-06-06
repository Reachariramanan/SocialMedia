---
name: intelligent_guy
description: "Structured editorial-grade HTML with full information hierarchy: 70/30 split, intelligence cards, scenario blocks, forecast bars, Chart.js charts"
version: "2.1.0"
category: rendering
---

# IntelligentGuy Skill

## Overview
Produce a structured, editorial-grade HTML intelligence report with a full information hierarchy. Every section serves a distinct analytical purpose — no decorative filler.

## Layout Blueprint
```
70/30 main / sidebar split (CSS Grid: 1fr 280px)

Masthead        — publication name, edition, UTC timestamp
Source Bar      — inline pill list of all sources used
Banner          — hero story: large headline + 2-sentence summary + confidence badge
Body Grid (70%) — Intelligence Cards, Pull Quotes, Scenario Blocks, Public Reaction
Sidebar (30%)   — Stats panel, Sentiment chart, Source breakdown, Forecast bars
Charts section  — Chart.js line charts for sentiment / time-series with semantic highlights
Conclusions     — Analyst summary, 3 key takeaways, forward outlook
Footer          — metadata, source count, generation timestamp
```

## Content Blocks

### Intelligence Card
- Title, confidence badge, signal count
- 3–4 sentence body
- Source attribution pills

### Pull Quote
- Large serif quote (Playfair Display, `text-xl italic`)
- Attribution line below
- Left border accent `border-l-4 border-blue-500`

### Scenario Block
- Label: BASE / RISK / UPSIDE
- One-sentence description
- Probability bar (CSS width %)

### Public Reaction
- 2–3 representative tweets (text + author + engagement)
- Sentiment label per tweet

### Forecast Bars
- Event name + probability percentage
- Styled `<progress>` element or CSS bar

## Visualisation
- Chart.js line chart: sentiment over time, smooth curves, semantic highlight points (dots at key moments)
- Colour coding: positive → green-400, negative → red-400, neutral → gray-400

## Typography
- Display: Playfair Display (headlines, pull quotes)
- Body: Source Serif 4 (`text-sm leading-relaxed`)
- Labels: font-mono `text-xs uppercase`

## Output
Emit ONLY the HTML document — no markdown, no explanations.
