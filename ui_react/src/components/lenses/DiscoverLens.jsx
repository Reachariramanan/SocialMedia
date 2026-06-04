import React from 'react'
import { Compass, ExternalLink, Download } from 'lucide-react'
import LensFrame from './LensFrame'
import SkeletonLens from '../shared/SkeletonLens'

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
      borderRadius: 'var(--radius-sm)', padding: '10px 12px', marginBottom: 6,
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
      </div>
      <div style={{ fontSize: 12, wordBreak: 'break-all' }}>
        <a href={item.url} target="_blank" rel="noreferrer" style={{ color: 'var(--signal-blue)' }}>
          {item.url}
        </a>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 6 }}>
        <div style={{
          flex: 1, height: 3, background: 'var(--depth-0)',
          borderRadius: 2, overflow: 'hidden',
        }}>
          <div style={{
            width: `${pct}%`, height: '100%',
            background: 'var(--signal-cyan)',
            borderRadius: 2,
          }} />
        </div>
        <span style={{ fontSize: 10, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
          {score.toFixed(2)}
        </span>
      </div>
    </div>
  )
}

export default function DiscoverLens({ discover }) {
  const { input, setInput, results, loading, error, doDiscover } = discover

  const doExport = () => {
    if (!results) return
    const slug = (results.keywords || []).join('_').replace(/[^a-zA-Z0-9_]/g, '') || 'discover'
    const date = new Date().toISOString().slice(0, 10)
    const blob = new Blob([JSON.stringify(results, null, 2)], { type: 'application/json' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = `discover_${slug}_${date}.json`
    a.click()
  }

  const urls = results?.urls || []

  return (
    <LensFrame
      title="Discover"
      icon={<Compass size={14} />}
      area="discover"
      badge={results ? `${results.total || 0} URLs` : null}
    >
      <div style={{ display: 'flex', gap: 8, marginBottom: 10 }}>
        <input
          className="input-field"
          placeholder="Keywords e.g. NEET, AI, Modi"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && doDiscover()}
          disabled={loading}
          style={{ flex: 1 }}
        />
        <button className="btn-action" onClick={() => doDiscover()} disabled={loading || !input.trim()}>
          {loading ? '...' : 'Go'}
        </button>
      </div>

      {error && <div style={{ fontSize: 12, color: 'var(--signal-amber)', marginBottom: 8 }}>{error}</div>}
      {loading && <SkeletonLens lines={4} />}

      {results && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10, flexWrap: 'wrap' }}>
          <span style={{ fontSize: 11, color: 'var(--text-secondary)' }}>
            <strong>{results.total}</strong> URLs
          </span>
          {Object.entries(results.sources || {}).map(([src, n]) => (
            <span key={src} style={{ fontSize: 10, color: 'var(--text-muted)' }}>{src}: {n}</span>
          ))}
          <span style={{ fontSize: 10, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
            {results.elapsed_sec}s
          </span>
          <button onClick={doExport} style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 4, fontSize: 11, color: 'var(--signal-blue)' }}>
            <Download size={11} /> JSON
          </button>
        </div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column' }}>
        {urls.slice(0, 50).map((item, i) => (
          <DiscoverURLCard key={i} item={item} />
        ))}
      </div>

      {!results && !loading && (
        <span className="muted">Enter keywords to discover tweet URLs via SearXNG.</span>
      )}
    </LensFrame>
  )
}
