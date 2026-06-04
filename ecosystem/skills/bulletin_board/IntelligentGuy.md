```md
# skill.md — Generating High-Fidelity Intelligence Bulletin HTML Reports

## Overview

This skill enables an agent to generate structured, editorial-grade HTML reports that combine:
- Data storytelling
- Multi-source synthesis
- Visual hierarchy
- Embedded analytics (charts, stats, timelines)

The output should resemble a premium intelligence bulletin or investigative media layout, not a generic webpage.

Focus areas:
- Typography and readability
- Structured information density
- Visual separation of content layers
- Narrative + data integration

---

## Core Principles

### 1. Information Hierarchy First
Every report must guide the reader visually:

Order of importance:
1. Masthead (identity)
2. Headline (crisis/event)
3. Subheadline (context + stakes)
4. Lead narrative
5. Supporting intelligence blocks
6. Data panels (stats, timelines)
7. Analytical visuals (charts)
8. Conclusions / projections

Use:
- Font size variation
- Weight (bold vs light)
- Spacing
- Borders and dividers

---

### 2. Layout Architecture

Use a **modular grid system**.

#### Primary Structure
```

.container
├── masthead
├── source-bar
├── headline-banner
├── body-grid
│     ├── main-column
│     ├── divider
│     └── side-column
├── chart-section
├── bottom-dual-sections
└── footer

```

#### Grid Pattern
- 2-column layout:
  - Main content (~70%)
  - Sidebar (~30%)
- Use a vertical divider for clarity

---

### 3. Typography System

Use layered typography for editorial feel.

#### Font Pairing
- Headings: serif display (e.g. Playfair Display)
- Body: readable serif (e.g. Source Serif)

#### Scale
- Banner headline: large, bold
- Section labels: small uppercase
- Body text: medium, high line-height
- Metadata: small, muted

#### Key Techniques
- Drop caps for lead paragraph
- Uppercase tracking for labels
- Italics for quotes and commentary

---

### 4. Color System

Use a restrained palette with one strong accent.

#### Roles
- Primary text: dark neutral
- Secondary text: muted gray
- Accent: deep red (crisis emphasis)
- Info tags: soft colored backgrounds

#### Usage
- Red: alerts, emphasis, key numbers
- Blue: informational blocks
- Yellow/green: categorization tags

Avoid overuse — color should signal meaning.

---

### 5. Content Blocks

#### A. Masthead
Purpose: identity + credibility

Includes:
- Report type label
- Date
- Title
- Metadata row

---

#### B. Source Bar
Purpose: show data origin

Elements:
- Platform badges
- Small icons
- Short description

---

#### C. Banner (Critical Section)
Purpose: immediate context

Structure:
- Tag (breaking / category)
- Headline
- Subheadline

Styling:
- Solid background (accent color)
- High contrast text

---

#### D. Main Narrative

Use:
- Drop cap opening
- Paragraph spacing
- Embedded modules between text

---

#### E. Intelligence Cards

Used for:
- Whistleblowers
- Network exposure
- Key findings

Structure:
- Header (label + icon)
- Body (short insight)

Style:
- Light background
- Rounded corners
- Subtle borders

---

#### F. Pull Quotes

Purpose: emotional anchor

Design:
- Serif font
- Bold + italic
- Top/bottom borders
- Attribution line

---

#### G. Scenario / View Blocks

Used for:
- Opinion splits
- Contrasting viewpoints

Style:
- Left border accent
- Italic text
- Compact format

---

#### H. Sidebar (Data Column)

Must include:

1. **Stats**
   - Large numbers
   - Short labels

2. **Timeline**
   - Date + event format

3. **Platform Analysis**
   - Comparative insights

Keep dense but readable.

---

### 6. Data Visualization (Charts)

#### Tooling
Use Chart.js via CDN.

#### Chart Type
- Line chart for sentiment/time-series

#### Requirements
- Minimal styling
- Smooth curves (tension)
- Highlight key points
- Small font ticks

#### Data Preparation
Agent must:
- Normalize time-series data
- Ensure consistent intervals
- Map values clearly

#### Accessibility
- Add aria-label
- Include textual summary below

---

### 7. Section Dividers

Use subtle separators:
- Thin horizontal lines
- Slight margins
- Avoid clutter

Purpose:
- Break cognitive load
- Signal transitions

---

### 8. Hashtags / Tags Grid

Display as:
- Pills (rounded)
- Color-coded categories

Used for:
- Trend mapping
- Topic clustering

---

### 9. Bottom Sections

#### A. Public Demands
- Numbered list
- Clear phrasing
- Action-oriented

#### B. Forecast / Probabilities

Structure:
- Label
- Progress bar
- Percentage

Style:
- Horizontal bars
- Consistent width
- Accent color fill

---

### 10. Footer

Include:
- Data sources
- Methodology references
- Compilation date

Use:
- Small uppercase text
- Light borders

---

## Styling Best Practices

### Spacing
- Consistent padding (8px / 16px system)
- Avoid crowding
- Use whitespace as structure

### Borders
- Thin, subtle lines
- Use for grouping, not decoration

### Alignment
- Left-aligned text
- Consistent grid edges

---

## Data Handling Guidelines

Agent must:
- Aggregate multi-source input
- Extract key signals (events, actors, sentiment)
- Avoid raw dumps — always summarize

### Transformations
- Convert numbers into highlights
- Convert events into timelines
- Convert opinions into structured viewpoints

---

## Narrative Construction

Flow:
1. What happened
2. What was discovered
3. Human impact
4. Systemic implications
5. Public reaction
6. What happens next

Blend:
- Data
- Quotes
- Analysis

---

## Interactivity Guidelines

Minimal but meaningful:
- Charts (primary interaction)
- Hover tooltips
- No heavy animations

---

## Accessibility

- Use semantic HTML
- Provide alt/aria descriptions
- Maintain color contrast
- Ensure readable font sizes

---

## Output Expectations

The generated HTML should:
- Feel like a premium editorial product
- Be readable without external explanation
- Combine narrative + data seamlessly
- Scale across screen sizes (basic responsiveness)

---

## Agent Execution Checklist

Before generating output:

- [ ] Structured layout defined
- [ ] Typography hierarchy applied
- [ ] Data transformed into visuals
- [ ] Sections logically ordered
- [ ] Colors used with meaning
- [ ] Charts integrated cleanly
- [ ] No visual clutter
- [ ] Narrative flows clearly

---

## Final Goal

Produce a document that:
- Informs like a report
- Reads like journalism
- Looks like a magazine
- Feels like intelligence analysis
```
