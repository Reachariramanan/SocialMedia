import React, { useState, useEffect, useCallback } from 'react'
import { X, Terminal, Package, BookOpen, Check } from 'lucide-react'

// Skill definitions from ecosystem/skills/bulletin_board/
const SKILLS = [
  {
    id: 'bulletin_board',
    name: 'Bulletin Board',
    tag: 'formatting v1.0',
    desc: `Transforms research findings into ranked story cards with headlines, tags, signals, and source attribution.

Steps:
1. Rank stories by signal count, recency, and trending velocity
2. Format each card: title, tag, summary (2 sentences), confidence, signals array, top headline + link, tweet sample
3. Add a Lede card for the top story — 3-sentence summary + pull-quote
4. Add a Watch section: 3-5 emerging signals below the 2-source threshold
5. Output JSON bulletin with lede, stories, watching, and metadata`,
  },
  {
    id: 'uncle_prompt',
    name: 'UnclePrompt',
    tag: 'html-report v2.0',
    desc: `High-quality intelligence bulletin HTML with Python data processing.

Workflow:
• Sentiment analysis via vaderSentiment/textblob
• Jinja2 HTML templating with 3-column grid layout
• Typography: Playfair Display (headlines) + Source Serif 4 (body)
• Chart.js CDN — smooth curves, minimal styling
• Sidebar: stats, timeline, platform comparison
• Masthead → Banner → Main narrative → Sidebar intelligence`,
  },
  {
    id: 'intelligent_guy',
    name: 'IntelligentGuy',
    tag: 'editorial v2.1',
    desc: `Structured, editorial-grade HTML reports with full information hierarchy.

Layout: 70/30 main/sidebar split — Masthead → Source Bar → Banner → Body Grid → Charts → Conclusions
Content blocks: Intelligence Cards, Pull Quotes, Scenario Blocks, Public Reaction, Forecast Bars
Data: Chart.js line charts for sentiment/time-series with semantic highlight points
Typography pairing: Playfair Display serif display + Source Serif 4 readable body`,
  },
  {
    id: 'smallboy',
    name: 'SmallBoy',
    tag: 'html-core v1.5',
    desc: `Core editorial HTML skill — clean, structured, minimal.

Blueprint: Masthead → Source Strip → Banner → 3-column grid (Main | Divider | Sidebar)
Font system: 22-26px 900-weight headline / 9-11px uppercase labels / 12-14px body
Sidebar: Stats boxes (big number + description), Timeline, Platform Comparison
Bottom: 2-column split — Demands (left) + Forecast bars (right)`,
  },
  {
    id: 'smallboywithbrains',
    name: 'SmallBoyWithBrains',
    tag: 'html-advanced v2.5',
    desc: `Publication-quality HTML with layered mental model approach.

Mental model: Document Identity → Layout System → Information Hierarchy → Visual Rhythm → Data+Narrative Integration
Layout: container → header, source-bar, banner, main-grid (1fr | 1px divider | 200px sidebar), charts, footer
Drop-cap pattern via CSS ::first-letter, progress bars for forecast probabilities
Spacing system: 12-16px section padding, 8-12px margins, 1.5-1.7 line-height
Quality checklist: hierarchy at glance, distinct sections, consistent typography, meaningful colors, scannable data`,
  },
]

const SANDBOX_ITEMS = [
  {
    icon: '🐍',
    cls: 'sandbox-icon-ok',
    name: 'Python Runtime',
    desc: 'subprocess shell — 30s timeout, 4000 char stdout',
  },
  {
    icon: '📊',
    cls: 'sandbox-icon-ok',
    name: 'Data Stack',
    desc: 'pandas, numpy, scikit-learn, statsmodels, scipy',
  },
  {
    icon: '📝',
    cls: 'sandbox-icon-ok',
    name: 'Templating',
    desc: 'jinja2, vaderSentiment, textblob, beautifulsoup4',
  },
  {
    icon: '🌐',
    cls: 'sandbox-icon-ok',
    name: 'HTTP / Search',
    desc: 'httpx, SearXNG, Google News RSS, xfetch discover',
  },
  {
    icon: '📈',
    cls: 'sandbox-icon-ok',
    name: 'Visualisation',
    desc: 'Chart.js CDN + Tailwind CDN (self-contained HTML)',
  },
  {
    icon: '🤖',
    cls: 'sandbox-icon-ok',
    name: 'LLM Backend',
    desc: 'qwen3-6-27b via vLLM — temp 0.4, thinking off',
  },
]

const THEMES = [
  { id: 'z',     label: 'Z',     previewClass: 'theme-preview-z' },
  { id: 'dark',  label: 'Dark',  previewClass: 'theme-preview-dark' },
  { id: 'light', label: 'Light', previewClass: 'theme-preview-light' },
]

export default function SettingsPanel({ onClose }) {
  const [activeSkill, setActiveSkill] = useState('bulletin_board')
  const [theme, setTheme] = useState(() => localStorage.getItem('z-theme') || 'z')

  const applyTheme = useCallback((t) => {
    document.documentElement.setAttribute('data-theme', t)
    localStorage.setItem('z-theme', t)
    setTheme(t)
  }, [])

  // Close on Escape
  useEffect(() => {
    const handler = (e) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [onClose])

  const skill = SKILLS.find(s => s.id === activeSkill)

  return (
    <>
      <div className="settings-backdrop" onClick={onClose} />
      <div className="settings-panel">
        <div className="settings-header">
          <span className="settings-title">Settings</span>
          <button className="settings-close" onClick={onClose} title="Close">
            <X size={14} />
          </button>
        </div>

        <div className="settings-body">
          {/* Theme */}
          <div className="settings-section">
            <div className="settings-section-label">UI Theme</div>
            <div className="theme-options">
              {THEMES.map(t => (
                <button
                  key={t.id}
                  className={`theme-option${theme === t.id ? ' theme-option-active' : ''}`}
                  onClick={() => applyTheme(t.id)}
                >
                  <div className={`theme-preview ${t.previewClass}`}>
                    <div className="theme-preview-stripe" />
                    {theme === t.id && (
                      <div style={{
                        position: 'absolute', top: 4, right: 4, zIndex: 2,
                        width: 16, height: 16, borderRadius: '50%',
                        background: 'var(--signal-blue)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                      }}>
                        <Check size={10} color="white" />
                      </div>
                    )}
                  </div>
                  <span className="theme-option-label">{t.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Sandbox */}
          <div className="settings-section">
            <div className="settings-section-label" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <Terminal size={11} />
              Sandbox Environment
            </div>
            <div className="sandbox-status">
              {SANDBOX_ITEMS.map(item => (
                <div key={item.name} className="sandbox-row">
                  <div className={`sandbox-icon ${item.cls}`}>{item.icon}</div>
                  <div className="sandbox-info">
                    <div className="sandbox-name">{item.name}</div>
                    <div className="sandbox-desc">{item.desc}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Skills viewer */}
          <div className="settings-section">
            <div className="settings-section-label" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <BookOpen size={11} />
              Report Generation Skills
            </div>

            <div className="skills-tabs">
              {SKILLS.map(s => (
                <button
                  key={s.id}
                  className={`skills-tab${activeSkill === s.id ? ' skills-tab-active' : ''}`}
                  onClick={() => setActiveSkill(s.id)}
                >
                  {s.name}
                </button>
              ))}
            </div>

            {skill && (
              <div className="skill-doc">
                <div className="skill-doc-title">{skill.name}</div>
                <span className="skill-doc-tag">{skill.tag}</span>
                <div className="skill-doc-desc">{skill.desc}</div>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  )
}
