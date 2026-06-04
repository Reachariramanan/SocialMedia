# skill.md — Generating High-Quality Intelligence Bulletin HTML with Python

## Overview
This skill defines how an agent should **analyze data, structure insights, and generate a polished HTML intelligence bulletin** similar to the provided example. The emphasis is on:

- Clean editorial layout (magazine / newspaper style)
- Strong typography and spacing
- Modular CSS architecture
- Data visualization integration (charts)
- Structured narrative + sidebar intelligence

The agent must combine **data processing (Python)** with **presentation (HTML + CSS + JS)**.

---

## Core Workflow

### 1. Data Ingestion
The agent should:
- Accept structured or semi-structured inputs:
  - Social media data (CSV / JSON)
  - Sentiment scores
  - Timeline events
  - Key highlights
- Normalize data into Python dictionaries/lists

Example:
```python
data = {
    "headline": "...",
    "subheadline": "...",
    "stats": [],
    "timeline": [],
    "sentiment": [],
    "quotes": [],
    "sections": []
}
````

---

### 2. Data Processing (Python)

#### Sentiment Analysis

* Use libraries like:

  * `vaderSentiment`
  * `textblob`
* Output normalized scores between `-1` and `1`

#### Aggregation

* Compute:

  * Mean sentiment
  * Peak negativity
  * Volume counts
* Generate summary metrics:

```python
stats = {
    "total_posts": 5000,
    "negative_pct": 72,
    "peak_sentiment": -0.35
}
```

#### Timeline Structuring

Sort events chronologically:

```python
timeline = sorted(events, key=lambda x: x["date"])
```

---

### 3. HTML Generation Strategy

The HTML should be **template-driven**, not manually concatenated.

Use:

* Python string templates (`f-strings`)
* OR templating engines (preferred):

  * `Jinja2`

---

## Layout Architecture

### Grid System

Use a **3-column grid**:

```css
.body-grid {
  display: grid;
  grid-template-columns: 1fr 1px 200px;
}
```

* Left: Main narrative
* Center: Divider
* Right: Sidebar intelligence

---

### Typography System

Use **serif-heavy editorial fonts**:

```css
font-family: 'Playfair Display', serif;   /* Headlines */
font-family: 'Source Serif 4', serif;     /* Body */
```

Hierarchy:

* Headline: bold, uppercase, wide letter spacing
* Subhead: italic, lighter
* Body: readable line-height (1.6–1.8)

---

### Color System

Define variables:

```css
:root {
  --primary: #B91C1C;
  --secondary: #1A56B0;
  --text-primary: #111;
  --text-secondary: #666;
  --border: #ddd;
}
```

Guidelines:

* Red = urgency / crisis
* Blue = informational blocks
* Neutral greys for structure

---

## Key Components

### 1. Masthead

Structure:

* Label (small caps)
* Date (italic)
* Title (centered, uppercase)

```html
<div class="mast">
  <div class="mast-top">
    <div class="label">...</div>
    <div class="date">...</div>
  </div>
  <div class="title">...</div>
</div>
```

---

### 2. Banner (Hero Section)

Purpose:

* Immediate visual impact
* Highlight breaking news

Style:

```css
.banner {
  background: var(--primary);
  color: white;
}
```

---

### 3. Main Article Column

Features:

* Drop cap for first paragraph
* Paragraph spacing
* Pull quotes

Drop cap:

```css
.drop-cap::first-letter {
  float: left;
  font-size: 48px;
  font-weight: bold;
}
```

---

### 4. Sidebar (Intelligence Panel)

Contains:

* Stats
* Timeline
* Platform comparison

Stat box:

```css
.stat-box {
  border: 1px solid var(--border);
  padding: 10px;
}
```

---

### 5. Cards (Modular Content)

Reusable block:

```css
.card {
  border-radius: 8px;
  padding: 10px;
}
```

Variants:

* Blue: informational
* Red: alerts
* Neutral: quotes

---

### 6. Quote Blocks

```css
.pull-quote {
  border-top: 2px solid var(--primary);
  border-bottom: 2px solid var(--primary);
  font-style: italic;
}
```

---

### 7. Hashtag / Tag Pills

```css
.tag {
  border-radius: 20px;
  padding: 4px 10px;
  font-size: 10px;
}
```

Color-coded sentiment:

* Red: negative
* Yellow: mixed
* Blue: neutral
* Green: positive

---

## Chart Integration

### Chart.js Usage

Embed via CDN:

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
```

Python prepares data:

```python
labels = ["May 11", "May 12"]
values = [-0.3, -0.4]
```

Inject into JS:

```html
<script>
new Chart(ctx, {
  type: 'line',
  data: {
    labels: {{ labels }},
    datasets: [{
      data: {{ values }}
    }]
  }
});
</script>
```

Guidelines:

* Smooth curves (`tension: 0.4`)
* Light fill background
* Minimal legend
* Subtle gridlines

---

## Visual Hierarchy Rules

1. **Top → Bottom flow**

   * Headline
   * Summary
   * Deep detail

2. **Contrast**

   * Use borders and spacing, not heavy colors

3. **Whitespace**

   * Minimum 12–16px spacing between blocks

4. **Consistency**

   * Same padding across all cards

---

## Python → HTML Pipeline

### Step 1: Process Data

```python
processed_data = transform(raw_data)
```

### Step 2: Render Template

```python
from jinja2 import Template

html = Template(template_string).render(processed_data)
```

### Step 3: Save Output

```python
with open("report.html", "w") as f:
    f.write(html)
```

---

## Responsiveness (Optional)

Use:

```css
@media (max-width: 768px) {
  .body-grid {
    grid-template-columns: 1fr;
  }
}
```

---

## Styling Principles

* Avoid clutter
* Use thin borders instead of heavy separators
* Prefer **subtlety over decoration**
* Maintain **editorial seriousness**

---

## Common Mistakes to Avoid

* Overusing colors
* Inconsistent spacing
* Mixing font families excessively
* Large blocks of unbroken text
* Unstructured data dumps

---

## Extension Capabilities

The agent should be able to:

* Add interactive filters
* Generate multiple reports dynamically
* Export to PDF
* Embed additional charts (bar, pie)
* Add maps (if geospatial data exists)

---

## Final Goal

Produce an output that:

* Reads like a professional intelligence bulletin
* Feels like a newspaper + data report hybrid
* Balances **storytelling + analytics**
* Maintains **visual clarity and authority**


