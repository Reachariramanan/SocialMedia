import React, { useState, useRef, useEffect } from 'react'
import {
  FileText, Compass, Download, Eye, EyeOff,
  Cpu, RefreshCw, Search, X as XIcon, Rss, Trash2, Clock, Globe,
} from 'lucide-react'
import AgentTrace from './shared/AgentTrace'
import SchedulesPanel from './SchedulesPanel'
import ChatDock from './shared/ChatDock'
import ProgressArc from './shared/ProgressArc'
import StatusOrb from './shared/StatusOrb'
import SkeletonLens from './shared/SkeletonLens'
import HashtagFeedBlock from './shared/HashtagFeedBlock'
import NewsCard from './shared/NewsCard'
import TweetCard from './shared/TweetCard'
import { timeAgo } from '../utils/formatters'
import useScheduledRunTrace from '../hooks/useScheduledRunTrace'

// ─── Discover URL card ────────────────────────────────────────
const PLATFORM_META = {
  x:        { color: 'var(--signal-cyan)',    bg: 'rgba(6,182,212,0.12)',   label: 'X / Twitter' },
  facebook: { color: 'var(--signal-blue)',    bg: 'rgba(59,130,246,0.12)',  label: 'Facebook' },
  web:      { color: 'var(--signal-violet)',  bg: 'rgba(139,92,246,0.12)', label: 'Web' },
}

function DiscoverURLCard({ item }) {
  const host = (() => {
    try { return new URL(item.url).hostname.replace('www.', '') } catch { return '' }
  })()
  const platform = item.platform || 'web'
  const meta = PLATFORM_META[platform] || PLATFORM_META.web
  const score = typeof item.score === 'number' ? item.score : 0
  const pct = Math.min(100, Math.round(score * 100))

  return (
    <div style={{
      background: 'var(--depth-2)', border: '1px solid var(--border)',
      borderRadius: 'var(--radius-sm)', padding: '10px 12px',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
        <span style={{
          fontSize: 9, padding: '2px 6px', borderRadius: 4,
          background: meta.bg, color: meta.color,
          textTransform: 'uppercase', letterSpacing: '0.04em', fontWeight: 600,
        }}>
          {item.discovered_from || meta.label}
        </span>
        <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>{host}</span>
        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 6 }}>
          <div style={{ width: 50, height: 3, background: 'var(--depth-0)', borderRadius: 2, overflow: 'hidden' }}>
            <div style={{ width: `${pct}%`, height: '100%', background: meta.color, borderRadius: 2 }} />
          </div>
          <span style={{ fontSize: 10, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
            {score.toFixed(2)}
          </span>
        </div>
      </div>
      {item.title && (
        <div style={{ fontSize: 11, color: 'var(--text-secondary)', marginBottom: 3, fontWeight: 500 }}>
          {item.title}
        </div>
      )}
      <div style={{ fontSize: 12, wordBreak: 'break-all' }}>
        <a href={item.url} target="_blank" rel="noreferrer" style={{ color: 'var(--signal-blue)' }}>
          {item.url}
        </a>
      </div>
      {item.content && (
        <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4, lineHeight: 1.4 }}>
          {item.content.slice(0, 180)}{item.content.length > 180 ? '…' : ''}
        </div>
      )}
    </div>
  )
}

// ─── SearXNG tabbed block ─────────────────────────────────────
const PLATFORM_TABS = [
  { id: 'x',        label: 'X / Twitter', color: 'var(--signal-cyan)'   },
  { id: 'facebook', label: 'Facebook',    color: 'var(--signal-blue)'   },
  { id: 'web',      label: 'Web',         color: 'var(--signal-violet)' },
]

function SearxngTabbedBlock({ discResults, discLoading }) {
  const [activeTab, setActiveTab] = useState('x')
  const buckets = discResults?.buckets || {}
  const items = buckets[activeTab] || []
  const tab = PLATFORM_TABS.find(t => t.id === activeTab)

  const totalAll = (buckets.x?.length || 0) + (buckets.facebook?.length || 0) + (buckets.web?.length || 0)

  return (
    <div className="discover-source-section">
      <div className="discover-source-header">
        <Compass size={12} style={{ color: 'var(--signal-cyan)' }} />
        <span className="discover-source-label" style={{ color: 'var(--signal-cyan)' }}>
          SearXNG Discovery
        </span>
        <span className="discover-source-count">
          {totalAll} URLs
          {discResults?.elapsed_sec ? ` · ${discResults.elapsed_sec}s` : ''}
        </span>
      </div>

      {/* Platform tabs */}
      <div style={{
        display: 'flex', gap: 0, borderBottom: '1px solid var(--border)',
        background: 'var(--depth-1)',
      }}>
        {PLATFORM_TABS.map(t => {
          const count = (buckets[t.id] || []).length
          const active = activeTab === t.id
          return (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id)}
              style={{
                flex: 1, padding: '7px 8px', fontSize: 10, fontWeight: 700,
                fontFamily: 'var(--font-display)', textTransform: 'uppercase',
                letterSpacing: '0.07em', border: 'none', cursor: 'pointer',
                borderBottom: active ? `2px solid ${t.color}` : '2px solid transparent',
                color: active ? t.color : 'var(--text-muted)',
                background: active ? 'rgba(255,255,255,0.03)' : 'transparent',
                transition: 'all 0.15s',
              }}
            >
              {t.label}
              {count > 0 && (
                <span style={{
                  marginLeft: 5, fontSize: 9, padding: '1px 5px', borderRadius: 8,
                  background: active ? 'rgba(255,255,255,0.08)' : 'var(--depth-2)',
                  color: active ? t.color : 'var(--text-muted)',
                }}>
                  {count}
                </span>
              )}
            </button>
          )
        })}
      </div>

      <div className="discover-source-body">
        {discLoading && <SkeletonLens lines={4} />}

        {!discLoading && discResults?.degraded && activeTab === 'x' && (() => {
          const engines = discResults.unresponsive_engines || []
          const names = engines.map(e => e.engine)
          const serviceDown = names.length > 0 && names.every(n => n === 'searxng')
          return (
            <div style={{ fontSize: 12, color: 'var(--signal-amber)', lineHeight: 1.5 }}>
              {serviceDown
                ? 'Search service unreachable — check that SearXNG is running, then try again.'
                : `Search degraded — engine(s) unavailable: ${names.join(', ') || 'unknown'}. Try again shortly.`}
            </div>
          )
        })()}

        {!discLoading && items.length === 0 && (
          <span className="muted">
            {discResults
              ? `No ${tab?.label} results found`
              : `Search to discover ${tab?.label} URLs`}
          </span>
        )}

        {items.slice(0, 50).map((item, i) => (
          <DiscoverURLCard key={i} item={item} />
        ))}
      </div>
    </div>
  )
}

// ─── Discover panel ───────────────────────────────────────────
function DiscoverPanel({ discover, feeds, activeQuery }) {
  const { input, setInput, results: discResults, loading: discLoading, error: discErr, doDiscover } = discover
  const { results: feedResults, loading: feedLoading, error: feedErr, doFetch } = feeds

  const feedTags = feedResults ? Object.entries(feedResults.feeds || {}) : []

  const handleSearch = () => {
    if (!input.trim()) return
    doDiscover()
    doFetch()
  }

  return (
    <div className="discover-panel">
      {/* Search bar */}
      <div className="discover-search-bar">
        <Search size={14} style={{ color: 'var(--text-muted)', flexShrink: 0 }} />
        <input
          className="input-field"
          placeholder="Search all sources: RSS, SearXNG, Tweets..."
          value={input}
          onChange={e => {
            setInput(e.target.value)
            feeds.setInput(e.target.value)
          }}
          onKeyDown={e => e.key === 'Enter' && handleSearch()}
          style={{ flex: 1 }}
        />
        {input && (
          <button
            style={{ color: 'var(--text-muted)', padding: '0 4px' }}
            onClick={() => { setInput(''); feeds.setInput('') }}
          >
            <XIcon size={13} />
          </button>
        )}
        <button className="btn-action" onClick={handleSearch} disabled={discLoading || !input.trim()}>
          {discLoading || feedLoading ? '...' : 'Search All'}
        </button>
      </div>

      {activeQuery && (
        <div>
          <span className="discover-query-badge">
            <Search size={11} /> {activeQuery}
          </span>
        </div>
      )}

      {(discErr || feedErr) && (
        <div style={{ fontSize: 12, color: 'var(--signal-amber)' }}>{discErr || feedErr}</div>
      )}

      <div className="discover-results">
        {/* RSS + Google News feeds */}
        <div className="discover-source-section">
          <div className="discover-source-header">
            <Rss size={12} style={{ color: 'var(--signal-emerald)' }} />
            <span className="discover-source-label" style={{ color: 'var(--signal-emerald)' }}>
              RSS &amp; Google News
            </span>
            <span className="discover-source-count">
              {feedTags.reduce((a, [, d]) => a + (d?.google_news?.entries?.length || 0), 0)} articles
            </span>
          </div>
          <div className="discover-source-body">
            {feedLoading && <SkeletonLens lines={3} />}
            {!feedLoading && feedTags.length === 0 && (
              <span className="muted">Search to see RSS and Google News results</span>
            )}
            {feedTags.map(([tag, data]) => (
              <HashtagFeedBlock key={tag} tag={tag} data={data} />
            ))}
          </div>
        </div>

        {/* SearXNG tabbed: X / Facebook / Web */}
        <SearxngTabbedBlock discResults={discResults} discLoading={discLoading} />
      </div>
    </div>
  )
}

// ─── Reports panel ────────────────────────────────────────────
function ReportsPanel({ runs, selectedRun, html, runHistory, onSelectRun, onDeleteRun, reloadRuns, runsLoading, activeScheduledRun }) {
  const [traceOpen, setTraceOpen] = useState(false)
  const iframeRef = useRef(null)
  const scheduledTrace = useScheduledRunTrace(activeScheduledRun?.running_run_id, {
    onComplete: () => reloadRuns?.(),
  })

  // Auto-select the in-progress run when it starts
  useEffect(() => {
    if (activeScheduledRun?.running_run_id && !selectedRun) {
      onSelectRun?.({
        run_id: activeScheduledRun.running_run_id,
        topic: activeScheduledRun.topic,
        is_in_progress: true,
      })
    }
  }, [activeScheduledRun?.running_run_id, selectedRun, onSelectRun])

  const downloadHtml = () => {
    if (!html || !selectedRun) return
    const blob = new Blob([html], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `news-report-${selectedRun.run_id}.html`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="reports-panel">
      {/* Run list sidebar */}
      <div className="run-list">
        <div className="run-list-header">
          <FileText size={11} style={{ display: 'inline', marginRight: 6 }} />
          Intelligence Reports
        </div>
        <div className="run-list-body">
          {runsLoading && <SkeletonLens lines={4} />}
          {/* In-progress scheduled run */}
          {activeScheduledRun?.running_run_id && (
            <div
              className={`run-row ${selectedRun?.run_id === activeScheduledRun.running_run_id ? 'run-row-active' : ''}`}
              style={{ animation: 'pulse 2s infinite' }}
            >
              <button
                className="run-btn"
                onClick={() => onSelectRun({
                  run_id: activeScheduledRun.running_run_id,
                  topic: activeScheduledRun.topic,
                  is_in_progress: true,
                })}
              >
                <span className="run-btn-topic" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <RefreshCw size={12} className="animate-spin" />
                  Running: {activeScheduledRun.topic || 'Report'}
                </span>
                <span className="run-btn-meta">
                  <ProgressArc current={scheduledTrace.roundsComplete} total={5} size={14} style={{ display: 'inline-block' }} />
                  {' '}{scheduledTrace.roundsComplete}/5
                </span>
              </button>
            </div>
          )}
          {!runsLoading && !activeScheduledRun?.running_run_id && runs.length === 0 && (
            <div style={{ padding: '16px 14px' }}>
              <span className="muted">No reports yet. Use the Generate button above.</span>
            </div>
          )}
          {runs.map(run => (
            <div
              key={run.run_id}
              className={`run-row ${selectedRun?.run_id === run.run_id ? 'run-row-active' : ''}`}
            >
              <button
                className="run-btn"
                onClick={() => onSelectRun(run)}
              >
                <span className="run-btn-topic">
                  {run.topic || 'Report'}
                </span>
                <span className="run-btn-meta">
                  {timeAgo(run.completed_at)} · #{run.run_id?.slice(-6)}
                </span>
              </button>
              <button
                className="run-delete-btn"
                title="Delete report"
                onClick={(e) => {
                  e.stopPropagation()
                  if (window.confirm(`Delete report "${run.topic || run.run_id}"? This cannot be undone.`)) {
                    onDeleteRun?.(run.run_id)
                  }
                }}
              >
                <Trash2 size={13} />
              </button>
            </div>
          ))}
        </div>
        <ChatDock
          selectedRun={selectedRun}
          onDeleteRun={onDeleteRun}
          reloadRuns={reloadRuns}
        />
      </div>

      {/* Report HTML viewer */}
      <div className="report-viewer">
        <div className="report-viewer-toolbar">
          <span className="report-viewer-title">
            {selectedRun?.is_in_progress ? (
              <>
                <RefreshCw size={13} className="animate-spin" style={{ display: 'inline', marginRight: 6 }} />
                In progress…
              </>
            ) : (
              selectedRun ? (selectedRun.topic || 'Intelligence Report') : 'Select a report'
            )}
          </span>
          {selectedRun && !selectedRun?.is_in_progress && (
            <span style={{ fontSize: 10, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
              {timeAgo(selectedRun.completed_at)}
            </span>
          )}
          {selectedRun && html && !selectedRun?.is_in_progress && (
            <button className="lens-expand-btn" onClick={downloadHtml} title="Download HTML">
              <Download size={13} />
            </button>
          )}
          {selectedRun && (
            <button
              className="lens-expand-btn"
              onClick={() => setTraceOpen(o => !o)}
              title="Toggle agent trace"
              style={traceOpen ? { color: 'var(--signal-blue)' } : {}}
            >
              {traceOpen ? <EyeOff size={13} /> : <Eye size={13} />}
            </button>
          )}
        </div>

        <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
          <div className="report-viewer-body">
            {runsLoading && (
              <div style={{
                position: 'absolute', inset: 0, display: 'flex',
                alignItems: 'center', justifyContent: 'center',
                color: 'var(--text-muted)', fontSize: 13,
              }}>
                <RefreshCw size={16} style={{ marginRight: 8 }} className="animate-spin" />
                Loading report...
              </div>
            )}
            {!runsLoading && html && (
              <iframe
                ref={iframeRef}
                srcDoc={html}
                style={{ width: '100%', height: '100%', border: 'none' }}
                sandbox="allow-scripts allow-same-origin"
                title="News Dashboard"
              />
            )}
            {!runsLoading && !html && runs.length === 0 && (
              <div style={{
                display: 'flex', flexDirection: 'column',
                alignItems: 'center', justifyContent: 'center',
                height: '100%', color: 'var(--text-muted)', gap: 12,
              }}>
                <FileText size={36} style={{ opacity: 0.2 }} />
                <span style={{ fontSize: 13 }}>No reports yet</span>
                <span style={{ fontSize: 12, opacity: 0.7 }}>Enter a topic above and click Generate</span>
              </div>
            )}
            {!runsLoading && !html && !selectedRun?.is_in_progress && runs.length > 0 && (
              <div style={{
                display: 'flex', flexDirection: 'column',
                alignItems: 'center', justifyContent: 'center',
                height: '100%', color: 'var(--text-muted)', gap: 8,
              }}>
                <span style={{ fontSize: 13 }}>Select a report from the list</span>
              </div>
            )}
            {selectedRun?.is_in_progress && !scheduledTrace.isRunning && (
              <div style={{
                display: 'flex', flexDirection: 'column',
                alignItems: 'center', justifyContent: 'center',
                height: '100%', color: 'var(--text-muted)', gap: 8,
              }}>
                <RefreshCw size={24} className="animate-spin" style={{ opacity: 0.5 }} />
                <span style={{ fontSize: 13 }}>Agent is working…</span>
              </div>
            )}
          </div>

          {traceOpen && selectedRun && (
            <div className="trace-panel">
              {selectedRun?.is_in_progress ? (
                <AgentTrace history={scheduledTrace.partialHistory} meta={selectedRun} />
              ) : (
                <AgentTrace history={runHistory} meta={selectedRun} />
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

const SKILL_LABELS = {
  html_report_writer: 'Default',
  bulletin_board: 'Bulletin',
  uncle_prompt: 'Uncle',
  intelligent_guy: 'Intel',
  smallboy: 'SmallBoy',
  smallboywithbrains: 'SmallBoy+',
}

// ─── Yukta inline bar ─────────────────────────────────────────
function YuktaBar({ agentRun, activeSkill }) {
  const { start, runId, status, rounds, isRunning, error } = agentRun
  const [topic, setTopic] = useState('')

  return (
    <div className="yukta-inline">
      <Cpu size={13} style={{ color: 'var(--text-muted)', flexShrink: 0 }} />
      <input
        placeholder="Topic for Yukta agent (blank = top trends)..."
        value={topic}
        onChange={e => setTopic(e.target.value)}
        onKeyDown={e => e.key === 'Enter' && !isRunning && start(topic, activeSkill)}
        disabled={isRunning}
      />
      <button onClick={() => start(topic, activeSkill)} disabled={isRunning}>
        {isRunning ? 'Running...' : `Generate${activeSkill && activeSkill !== 'html_report_writer' ? ` [${SKILL_LABELS[activeSkill] || activeSkill}]` : ''}`}
      </button>
      {isRunning && (
        <div className="yukta-progress">
          <ProgressArc current={rounds.length} total={5} size={22} />
          <span>{rounds.length}/5 rounds</span>
        </div>
      )}
      {status === 'done' && !isRunning && (
        <span style={{ fontSize: 11, color: 'var(--signal-emerald)', fontFamily: 'var(--font-mono)' }}>
          Done ✓
        </span>
      )}
      {error && (
        <span style={{ fontSize: 11, color: 'var(--signal-rose)' }}>{error}</span>
      )}
    </div>
  )
}

// ─── Main LeftPane export ─────────────────────────────────────
export default function LeftPane({
  mode, setMode,
  runs, selectedRun, html, runHistory, onSelectRun, onDeleteRun, reloadRuns, runsLoading,
  agentRun,
  activeSkill,
  discover,
  feeds,
  activeQuery,
  schedules,
}) {
  return (
    <div className="canvas-main">
      {/* Mode toggle bar + Yukta generator */}
      <div className="main-mode-bar">
        <button
          className={`main-mode-btn mode-reports ${mode === 'reports' ? 'main-mode-btn-active' : ''}`}
          onClick={() => setMode('reports')}
        >
          <FileText size={13} />
          Reports
          {runs.length > 0 && (
            <span style={{
              fontSize: 9, padding: '1px 5px', borderRadius: 8,
              background: mode === 'reports' ? 'rgba(59,130,246,0.2)' : 'var(--depth-2)',
              color: mode === 'reports' ? 'var(--signal-blue)' : 'var(--text-muted)',
            }}>
              {runs.length}
            </span>
          )}
        </button>
        <button
          className={`main-mode-btn mode-discover ${mode === 'discover' ? 'main-mode-btn-active' : ''}`}
          onClick={() => setMode('discover')}
        >
          <Compass size={13} />
          Discover
        </button>
        <button
          className={`main-mode-btn mode-schedules ${mode === 'schedules' ? 'main-mode-btn-active' : ''}`}
          onClick={() => setMode('schedules')}
        >
          <Clock size={13} />
          Schedules
          {schedules?.schedules?.length > 0 && (
            <span style={{
              fontSize: 9, padding: '1px 5px', borderRadius: 8,
              background: mode === 'schedules' ? 'rgba(245,158,11,0.2)' : 'var(--depth-2)',
              color: mode === 'schedules' ? 'var(--signal-amber)' : 'var(--text-muted)',
            }}>
              {schedules.schedules.length}
            </span>
          )}
        </button>

        <div className="mode-bar-spacer" />

        <YuktaBar agentRun={agentRun} activeSkill={activeSkill} />
      </div>

      {/* Content area */}
      {mode === 'reports' && (
        <ReportsPanel
          runs={runs}
          selectedRun={selectedRun}
          html={html}
          runHistory={runHistory}
          onSelectRun={onSelectRun}
          onDeleteRun={onDeleteRun}
          reloadRuns={reloadRuns}
          runsLoading={runsLoading}
          activeScheduledRun={schedules?.activeRun}
        />
      )}

      {mode === 'discover' && (
        <DiscoverPanel
          discover={discover}
          feeds={feeds}
          activeQuery={activeQuery}
        />
      )}

      {mode === 'schedules' && (
        <SchedulesPanel
          schedules={schedules?.schedules || []}
          loading={schedules?.loading}
          error={schedules?.error}
          onCreate={schedules?.create}
          onDelete={schedules?.remove}
        />
      )}
    </div>
  )
}
