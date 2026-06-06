---
name: smallboywithbrains
description: "Publication-quality HTML with layered mental model: document identity → layout system → information hierarchy → visual rhythm → data+narrative integration"
version: "2.5.0"
category: rendering
---

# SmallBoyWithBrains Skill

## Overview
Produce publication-quality HTML by building the document in layers, each layer informed by the previous. This mental model approach ensures every design decision is intentional and coherent.

## Mental Model Layers

### Layer 1 — Document Identity
Establish: publication name, edition number, date, topic, and tone (intelligence / analytical / urgent).
Every element must reinforce this identity.

### Layer 2 — Layout System
CSS Grid structure:
```css
.container  { max-width: 1280px; margin: 0 auto; padding: 0 16px; }
.header     { /* masthead */ }
.source-bar { /* single-row source pills */ }
.banner     { /* full-width hero */ }
.main-grid  { display: grid; grid-template-columns: 1fr 1px 200px; gap: 0; }
.charts     { /* full-width chart row */ }
.footer     { /* metadata */ }
```

### Layer 3 — Information Hierarchy
Priority order within the grid:
1. Lead story (banner) — highest weight
2. Secondary stories (main column cards) — ranked by signal count
3. Analysis / forecast (sidebar) — supporting context
4. Data charts — evidence layer
5. Footer metadata — lowest visual weight

### Layer 4 — Visual Rhythm
- Drop-cap on lead story body: `p::first-letter { font-size: 3em; float: left; line-height: 0.8; margin-right: 6px; }`
- Consistent vertical spacing: multiples of 8px
- Card grid gap: `16px`; inner padding: `16px`
- Horizontal rules between sections: `1px solid #334155`

### Layer 5 — Data + Narrative Integration
- Forecast probability bars: `<div class="bar" style="width: {pct}%">` inside a track div
- Sentiment badges inline with headlines
- Chart.js area line chart (tension: 0.4, fill: true, fillOpacity: 0.1) for time-series
- Progress bars for each platform's signal share

## Quality Checklist
Before emitting HTML, verify:
- [ ] Hierarchy readable at a glance (large → small weight)
- [ ] Each section visually distinct (colour, spacing, or rule)
- [ ] Typography consistent (two fonts max: display + body)
- [ ] Meaningful colour usage (no decorative colour)
- [ ] All data scannable without reading prose

## Output
Emit ONLY the HTML document — no markdown, no explanations.
