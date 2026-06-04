import React, { useState, useRef } from 'react'
import {
  FileText, Compass, Download, Eye, EyeOff,
  Cpu, RefreshCw, Search, X as XIcon, Rss,
} from 'lucide-react'
import AgentTrace from './shared/AgentTrace'
import ProgressArc from './shared/ProgressArc'
import StatusOrb from './shared/StatusOrb'
import SkeletonLens from './shared/SkeletonLens'
import HashtagFeedBlock from './shared/HashtagFeedBlock'
import NewsCard from './shared/NewsCard'
import TweetCard from './shared/TweetCard'
import { timeAgo } from '../utils/formatters'

// ─── Discover URL card ────────────────────────────────────────
function DiscoverURLCard({ item }) {
  const host = (() => {
    try { return new URL(item.url).hostname.replace('www.', '') } catch { return '' }
  })()
  const src = (item.discovered_from || '').toLowerCase()
  const score = typeof item.score === 'number' ? item.score : 0
  const pct = Math.round(score * 100)

  return (
    <div style={{
      background: 'var(--depth-2)', border: '1px solid var(--border)',
      borderRadius: 'var(--radius-sm)', padding: '10px 12px',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
        <span style={{
          fontSize: 9, padding: '2px 6px', borderRadius: 4,
          background: src.includes('searx') ? 'rgba(6,182,212,0.12)' : 'rgba(139,92,246,0.12)',
          color: src.includes('searx') ? 'var(--signal-cyan)' : 'var(--signal-violet)',
          textTransform: 'uppercase', letterSpacing: '0.04em', fontWeight: 600,
        }}>
          {item.discovered_from || 'Unknown'}
        </span>
        <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>{host}</span>
        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 6 }}>
          <div style={{ width: 50, height: 3, background: 'var(--depth-0)', borderRadius: 2, overflow: 'hidden' }}>
            <div style={{ width: `${pct}%`, height: '100%', background: 'var(--signal-cyan)', borderRadius: 2 }} />
          </div>
          <span style={{ fontSize: 10, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
            {score.toFixed(2)}
          </span>
        </div>
      </div>
      <div style={{ fontSize: 12, wordBreak: 'break-all' }}>
        <a href={item.url} target="_blank" rel="noreferrer" style={{ color: 'var(--signal-blue)' }}>
          {item.url}
        </a>
      </div>
    </div>
  )
}

// ─── Discover panel ───────────────────────────────────────────
function DiscoverPanel({ discover, feeds, activeQuery }) {
  const { input, setInput, results: discResults, loading: discLoading, error: discErr, doDiscover } = discover
  const { results: feedResults, loading: feedLoading, error: feedErr, doFetch } = feeds

  const discUrls = discResults?.urls || []
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

        {/* SearXNG discover URLs */}
        <div className="discover-source-section">
          <div className="discover-source-header">
            <Compass size={12} style={{ color: 'var(--signal-cyan)' }} />
            <span className="discover-source-label" style={{ color: 'var(--signal-cyan)' }}>
              SearXNG Discovery
            </span>
            <span className="discover-source-count">
              {discResults?.total || 0} URLs
              {discResults?.elapsed_sec ? ` · ${discResults.elapsed_sec}s` : ''}
            </span>
          </div>
          <div className="discover-source-body">
            {discLoading && <SkeletonLens lines={4} />}
            {!discLoading && discUrls.length === 0 && (
              <span className="muted">Search to discover tweet URLs via SearXNG</span>
            )}
            {discUrls.slice(0, 50).map((item, i) => (
              <DiscoverURLCard key={i} item={item} />
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

// ─── Reports panel ────────────────────────────────────────────
function ReportsPanel({ runs, selectedRun, html, runHistory, onSelectRun, runsLoading }) {
  const [traceOpen, setTraceOpen] = useState(false)
  const iframeRef = useRef(null)

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
          {!runsLoading && runs.length === 0 && (
            <div style={{ padding: '16px 14px' }}>
              <span className="muted">No reports yet. Use the Generate button above.</span>
            </div>
          )}
          {runs.map(run => (
            <button
              key={run.run_id}
              className={`run-btn ${selectedRun?.run_id === run.run_id ? 'run-btn-active' : ''}`}
              onClick={() => onSelectRun(run)}
            >
              <span className="run-btn-topic">
                {run.topic || 'Report'}
              </span>
              <span className="run-btn-meta">
                {timeAgo(run.completed_at)} · #{run.run_id?.slice(-6)}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Report HTML viewer */}
      <div className="report-viewer">
        <div className="report-viewer-toolbar">
          <span className="report-viewer-title">
            {selectedRun ? (selectedRun.topic || 'Intelligence Report') : 'Select a report'}
          </span>
          {selectedRun && (
            <span style={{ fontSize: 10, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
              {timeAgo(selectedRun.completed_at)}
            </span>
          )}
          {selectedRun && html && (
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
            {!runsLoading && !html && runs.length > 0 && (
              <div style={{
                display: 'flex', flexDirection: 'column',
                alignItems: 'center', justifyContent: 'center',
                height: '100%', color: 'var(--text-muted)', gap: 8,
              }}>
                <span style={{ fontSize: 13 }}>Select a report from the list</span>
              </div>
            )}
          </div>

          {traceOpen && selectedRun && (
            <div className="trace-panel">
              <AgentTrace history={runHistory} meta={selectedRun} />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// ─── Yukta inline bar ─────────────────────────────────────────
function YuktaBar({ agentRun }) {
  const { start, runId, status, rounds, isRunning, error } = agentRun
  const [topic, setTopic] = useState('')

  return (
    <div className="yukta-inline">
      <Cpu size={13} style={{ color: 'var(--text-muted)', flexShrink: 0 }} />
      <input
        placeholder="Topic for Yukta agent (blank = top trends)..."
        value={topic}
        onChange={e => setTopic(e.target.value)}
        onKeyDown={e => e.key === 'Enter' && !isRunning && start(topic)}
        disabled={isRunning}
      />
      <button onClick={() => start(topic)} disabled={isRunning}>
        {isRunning ? 'Running...' : 'Generate'}
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
  runs, selectedRun, html, runHistory, onSelectRun, runsLoading,
  agentRun,
  discover,
  feeds,
  activeQuery,
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

        <div className="mode-bar-spacer" />

        <YuktaBar agentRun={agentRun} />
      </div>

      {/* Content area */}
      {mode === 'reports' && (
        <ReportsPanel
          runs={runs}
          selectedRun={selectedRun}
          html={html}
          runHistory={runHistory}
          onSelectRun={onSelectRun}
          runsLoading={runsLoading}
        />
      )}

      {mode === 'discover' && (
        <DiscoverPanel
          discover={discover}
          feeds={feeds}
          activeQuery={activeQuery}
        />
      )}
    </div>
  )
}
