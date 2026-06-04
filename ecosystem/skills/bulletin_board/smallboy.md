# Skill: Generate Editorial Intelligence Bulletin HTML

## Purpose
Create high-quality, editorial-style HTML reports that resemble modern news bulletins or intelligence dashboards. The output should feel structured, data-rich, and visually polished, combining narrative, statistics, and charts.

---

## 1. Core Principles

### 1.1 Layout Philosophy
- Think in **sections, not paragraphs**
- Use **grid-based layout** for structured reading
- Combine:
  - Narrative (text)
  - Evidence (cards, quotes)
  - Data (stats, charts)
- Maintain **visual hierarchy**:
  - Header → Banner → Body → Sidebar → Footer

---

## 2. Global Styling Rules

### 2.1 Reset and Base
Always start with:
- `box-sizing: border-box`
- Remove default margins/padding
- Define max width (~600–720px for readability)

### 2.2 Typography System

Use **two font families**:
- Serif (for headings): elegant, high contrast
- Body serif (for readability)

Example:
- Heading: `Playfair Display`
- Body: `Source Serif 4` or Georgia fallback

### 2.3 Font Hierarchy

| Element | Size | Weight | Notes |
|--------|------|--------|------|
| Main headline | 22–26px | 800–900 | Strong impact |
| Section labels | 9–11px | 600 | Uppercase |
| Body text | 12–14px | 300–400 | High readability |
| Quotes | 13–15px | 600–700 | Italic |
| Stats numbers | 24–30px | 900 | Highlight |

---

## 3. Structural Blueprint

### 3.1 Masthead (Top Bar)
Include:
- Title of report
- Date
- Metadata line

Style:
- Top and bottom borders
- Tight spacing
- Uppercase labels

---

### 3.2 Source Strip
Purpose:
- Show data sources (platforms, origin)

Style:
- Small badges
- Rounded pills
- Light background colors

---

### 3.3 Banner (Hero Section)
This is the **visual anchor**.

Include:
- Category tag
- Headline
- Subheadline

Style:
- Strong background (e.g., deep red)
- White text
- Tight padding
- Bold serif headline

---

### 3.4 Main Content Grid

Use 3-column grid:
```
Main Content | Divider | Sidebar
```

Example:
```css
display: grid;
grid-template-columns: 1fr 1px 180px;
```

---

## 4. Main Content Patterns

### 4.1 Drop Cap Paragraph
- First letter enlarged
- Serif font
- Floated left

---

### 4.2 Content Cards
Used for:
- Insights
- Events
- Entities

Structure:
- Header (small label)
- Body text

Style:
- Soft background
- Border
- Rounded corners

---

### 4.3 Pull Quotes
- Centerpiece emotional element
- Use borders top/bottom
- Italic serif text

---

### 4.4 Section Divider
- Thin horizontal rule
- Space above and below

---

### 4.5 Opinion Blocks
Use:
- Left border highlight
- Italic text
- Attribution line

---

## 5. Sidebar Design

### 5.1 Stats Boxes
Each stat includes:
- Big number
- Description

Style:
- Light background
- Compact padding
- Large serif number

---

### 5.2 Timeline
Structure:
- Date (fixed width)
- Description

Use flex layout:
```
date | text
```

---

### 5.3 Platform Comparison
- Small legend-style indicators
- Color-coded squares

---

## 6. Data Visualization (Charts)

### 6.1 Tool
Use:
- Chart.js (CDN)

### 6.2 Chart Type
Default:
- Line chart for sentiment/time series

### 6.3 Data Design Rules
- Keep labels short (dates)
- Use smooth curves (`tension`)
- Avoid clutter

### 6.4 Styling Rules
- Single primary color
- Light fill under curve
- Small font ticks
- Minimal grid lines

### 6.5 Accessibility
- Always include `aria-label`
- Provide fallback text inside `<canvas>`

---

## 7. Tag Systems

### 7.1 Hashtags / Labels
- Small rounded pills
- Color-coded by category

Example categories:
- Negative → red
- Neutral → yellow
- Positive → blue/green

---

## 8. Bottom Sections

### 8.1 Two-Column Layout
Split:
- Left: demands / insights
- Right: forecasts / probabilities

---

### 8.2 Ranked Lists
- Use numbered markers
- Highlight numbers in serif font

---

### 8.3 Forecast Bars
Structure:
- Label
- Progress bar
- Percentage

Style:
- Thin horizontal bars
- Filled portion colored

---

## 9. Footer

Include:
- Sources
- Date compiled

Style:
- Uppercase small text
- Top border
- Justified layout

---

## 10. Color System

Define consistent palette:

| Purpose | Color |
|--------|------|
| Primary | Deep red |
| Secondary text | Gray |
| Background light | Off-white |
| Borders | Light gray |
| Accent (info) | Blue |

Use variables when possible:
```
--color-text-primary
--color-text-secondary
--color-border-secondary
```

---

## 11. Spacing Rules

- Section padding: 12–16px
- Card padding: 8–12px
- Grid gaps: minimal (clean look)
- Line height: 1.5–1.7 for readability

---

## 12. Content Strategy

Always combine:
1. Narrative explanation
2. Structured evidence
3. Quantitative data
4. Emotional signal (quotes)

Avoid:
- Long unbroken text
- Overcrowded visuals
- Too many colors

---

## 13. Reusability Guidelines

When generating new reports:
- Keep structure identical
- Swap:
  - Headline
  - Data
  - Cards
  - Timeline
- Maintain consistent CSS

---

## 14. Quality Checklist

Before finalizing:

- Layout is grid-aligned
- Typography hierarchy is clear
- Sections are visually distinct
- Chart renders correctly
- No overflow or broken alignment
- Sidebar complements, not repeats main content

---

## 15. Minimal Mental Model for Agent

Think of output as:

```
[Header]
[Source strip]
[Hero banner]
[Main grid]
  ├── Narrative + cards
  ├── Divider
  └── Stats + timeline
[Chart]
[Bottom insights + forecast]
[Footer]
```

---

This structure ensures outputs are:
- Readable
- Professional
- Data-driven
- Visually balanced
- Consistent across use cases
```