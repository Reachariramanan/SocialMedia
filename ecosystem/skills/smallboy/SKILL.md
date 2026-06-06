---
name: smallboy
description: "Core editorial HTML — clean 3-column grid, strong typography scale, stats sidebar, forecast bars. Minimal, structured, fast to render."
version: "1.5.0"
category: rendering
---

# SmallBoy Skill

## Overview
Produce a clean, structured HTML report using a core editorial blueprint. Focus on readability, clear hierarchy, and compact information density. No unnecessary decoration.

## Layout Blueprint
```
Masthead        — publication name, timestamp, topic line
Source Strip    — single-row pill list of sources
Banner          — full-width lead story card
3-column grid:
  Main (1fr)    — ranked story cards
  Divider (1px) — thin vertical rule, colour var(--border)
  Sidebar (200px)— stats boxes, timeline, platform comparison
Bottom section:
  Left  — Demands / key asks from stakeholders
  Right — Forecast bars (probability %)
```

## Typography Scale
- Headline: `font-weight: 900`, `font-size: 22–26px`
- Section labels: `font-size: 9–11px`, uppercase, `letter-spacing: 0.06em`
- Body: `font-size: 12–14px`, `line-height: 1.55`
- Mono metadata: `font-family: monospace`, `font-size: 10px`

## Sidebar Components
- **Stats box**: large number (`font-size: 28px`, bold) + short description below
- **Timeline**: vertical list of events, dot marker, timestamp + label
- **Platform Comparison**: small horizontal bars per platform (Twitter, Facebook, Web) with count

## Colour System (dark theme)
- Background: `#0f172a`
- Card: `#1e293b`, border `#334155`
- Accent: `#3b82f6`
- Positive: `#22c55e`, Warning: `#f59e0b`, Negative: `#ef4444`

## Spacing System
- Section padding: `12–16px`
- Card margin: `8–12px`
- Line height: `1.5–1.7`

## Output
Emit ONLY the HTML document — no markdown, no explanations.
