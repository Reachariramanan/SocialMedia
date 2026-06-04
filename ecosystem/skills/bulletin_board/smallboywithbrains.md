
# skill.md — Generating High-Fidelity Intelligence Bulletin HTML

## Purpose
This document defines how an agent should **construct rich, editorial-grade HTML reports** (like the NEET bulletin) with:
- Structured layout
- Typography hierarchy
- Data visualization
- Narrative + analytical fusion
- Pixel-level styling discipline

The goal is not just correctness, but **publication-quality presentation**.

---

## 1. Mental Model

Before generating HTML, the agent must think in layers:

1. **Document Identity**
   - What type of report? (bulletin, report, dashboard)
   - Tone: editorial / analytical / neutral

2. **Layout System**
   - Single column vs multi-column
   - Grid vs flex usage
   - Section segmentation

3. **Information Hierarchy**
   - Headline → subheadline → sections → micro-blocks

4. **Visual Rhythm**
   - Spacing consistency
   - Borders as separators
   - Typography contrast

5. **Data + Narrative Integration**
   - Charts
   - Stats
   - Quotes
   - Cards

---

## 2. Core HTML Structure

Always follow a **top-down layered container approach**:

```html
<div class="container">
  <div class="header"></div>
  <div class="source-bar"></div>
  <div class="banner"></div>
  <div class="main-grid">
    <div class="main-content"></div>
    <div class="divider"></div>
    <div class="sidebar"></div>
  </div>
  <div class="charts"></div>
  <div class="bottom-sections"></div>
  <div class="footer"></div>
</div>
````

### Key Rules

* Use **semantic grouping via divs**, not excessive nesting
* Avoid inline styles unless dynamic
* Every section must have a **class name reflecting purpose**

---

## 3. Typography System

### Fonts Strategy

Use **contrast pairing**:

* Serif for authority (headlines)
* Secondary serif for body

Example:

```css
font-family: 'Playfair Display', serif;  /* Headlines */
font-family: 'Source Serif 4', serif;    /* Body */
```

### Typography Hierarchy

| Element       | Style Characteristics            |
| ------------- | -------------------------------- |
| Masthead      | uppercase, spaced, bold          |
| Headline      | large, heavy serif               |
| Subheadline   | italic, lighter                  |
| Section Label | small, uppercase, letter-spacing |
| Body Text     | readable, line-height ~1.6–1.8   |
| Quotes        | italic, bordered emphasis        |

---

## 4. Layout System

### Grid Usage

Use **3-column grid with divider**:

```css
display: grid;
grid-template-columns: 1fr 1px 200px;
```

* Left: main narrative
* Middle: visual divider
* Right: sidebar stats

### Divider Pattern

```css
.divider {
  background: var(--color-border);
  margin: 16px 0;
}
```

---

## 5. Color System

Use restrained palette:

| Role        | Color Example      |
| ----------- | ------------------ |
| Primary     | Deep red (#B91C1C) |
| Secondary   | Muted gray         |
| Accent blue | Facebook-like      |
| Accent red  | Alert tone         |

### Rules

* Red = urgency / crisis / highlight
* Blue = informational / platform-specific
* Gray = metadata / secondary text

---

## 6. Section Design Patterns

### 6.1 Masthead

Features:

* Top and bottom borders
* Small metadata row
* Centered title

---

### 6.2 Source Bar

Compact badges:

```css
border-radius: 20px;
font-size: 10px;
padding: 3px 10px;
```

Use **color-coded platform indicators**

---

### 6.3 Banner (Hero Block)

Characteristics:

* Full-width color background
* Large headline
* Subtext italic

---

### 6.4 Main Content

#### Drop Cap Pattern

```css
.drop-cap::first-letter {
  float: left;
  font-size: 50px;
}
```

Use only on first paragraph.

---

### 6.5 Cards (Important)

Reusable pattern:

```html
<div class="card">
  <div class="card-head"></div>
  <div class="card-text"></div>
</div>
```

Use for:

* Whistleblowers
* Events
* Incidents

---

### 6.6 Pull Quotes

```css
border-top: 2px solid;
border-bottom: 2px solid;
font-style: italic;
```

Always include attribution (`cite`).

---

### 6.7 Sentiment Blocks

Use **left-border highlight style**:

```css
border-left: 3px solid red;
font-style: italic;
```

---

### 6.8 Sidebar

Contains:

* Stats
* Timeline
* Platform breakdown

#### Stat Box Pattern

```html
<div class="stat-box">
  <div class="number"></div>
  <div class="label"></div>
</div>
```

---

### 6.9 Timeline

Structure:

```html
<div class="timeline-item">
  <span class="date"></span>
  <span class="text"></span>
</div>
```

---

### 6.10 Hashtags Grid

Use flex wrap:

```css
display: flex;
flex-wrap: wrap;
gap: 5px;
```

Each tag:

* small
* pill-shaped
* category-colored

---

## 7. Data Visualization (Charts)

### Use Chart.js

Always:

* Minimal styling
* Smooth curves
* Subtle gridlines

Example:

```js
new Chart(ctx, {
  type: 'line',
  data: {...},
  options: {
    plugins: { legend: { display: false }},
    scales: {
      x: { grid: { color: 'rgba(0,0,0,0.05)' }},
      y: { min: -0.5, max: 0.05 }
    }
  }
});
```

### Key Rules

* No clutter
* Clear axis bounds
* Tooltips concise

---

## 8. Bottom Sections

Use **two-column layout**:

```css
grid-template-columns: 1fr 1fr;
```

### Left:

* Ranked demands

### Right:

* Forecast bars

---

### Progress Bars

```html
<div class="bar">
  <div class="fill" style="width:70%"></div>
</div>
```

---

## 9. Spacing System

Consistency is critical.

| Element         | Spacing                 |
| --------------- | ----------------------- |
| Section padding | 12–16px                 |
| Margins         | 8–12px                  |
| Grid gaps       | 0 (controlled manually) |

Use:

* thin borders for separation
* avoid excessive whitespace

---

## 10. Borders as Structure

Instead of spacing, use borders:

* Section separators
* Header framing
* Quote emphasis

Example:

```css
border-bottom: 1px solid var(--color-border);
```

---

## 11. Naming Conventions

Use **short but meaningful class names**:

| Type    | Example             |
| ------- | ------------------- |
| Section | `.mast`, `.banner`  |
| Text    | `.bt`, `.pq`        |
| Layout  | `.mcol`, `.scol`    |
| Utility | `.divider`, `.grid` |

Avoid:

* overly long names
* generic names like `.box`

---

## 12. Accessibility

Always include:

* `aria-label` for charts
* readable font sizes
* sufficient contrast

---

## 13. Responsiveness (Optional but Recommended)

Basic approach:

```css
@media (max-width: 768px) {
  grid-template-columns: 1fr;
}
```

Collapse sidebar below main content.

---

## 14. Content Composition Strategy

Agent must:

1. Start with **headline narrative**
2. Add **supporting evidence blocks**
3. Insert **data + stats**
4. Reinforce with **quotes and reactions**
5. Conclude with **demands + forecast**

---

## 15. Common Mistakes to Avoid

* Overusing colors
* Inconsistent spacing
* Too many font styles
* Missing hierarchy
* Flat layout (no visual separation)
* Overcrowded charts

---

## 16. Quality Checklist

Before output:

* Clear hierarchy visible at a glance
* Sections visually distinct
* Typography consistent
* Colors meaningful (not decorative)
* Data easy to scan
* Narrative readable without fatigue

---

## 17. Minimal Skeleton Template

```html
<div class="report">
  <div class="mast"></div>
  <div class="banner"></div>

  <div class="grid">
    <div class="main"></div>
    <div class="divider"></div>
    <div class="side"></div>
  </div>

  <div class="chart"></div>

  <div class="bottom-grid">
    <div></div>
    <div></div>
  </div>

  <div class="footer"></div>
</div>
```

---

## Final Principle

This is not just HTML generation.

It is **information design**.

The agent must think like:

* a journalist (narrative)
* a designer (layout)
* a data analyst (charts)
* a typographer (readability)

Only when all four align does the output reach the expected quality.

```
