import React, { useState } from 'react'
import { ChevronDown, ChevronUp } from 'lucide-react'
import { AGENT_COLORS } from '../../data/agentColors'
import { parseOutput } from '../../utils/formatters'

function OutputPreview({ raw }) {
  const [open, setOpen] = useState(false)
  const parsed = parseOutput(raw)

  if (parsed.type === 'html') {
    return (
      <div style={{ marginTop: 8 }}>
        <button className="feed-block-tab" onClick={() => setOpen(o => !o)}>
          {open ? '▾' : '▸'} HTML Report ({Math.round(parsed.value.length / 1024)}KB)
        </button>
        {open && (
          <iframe
            srcDoc={parsed.value}
            style={{ width: '100%', height: 300, border: '1px solid var(--border)', borderRadius: 'var(--radius-sm)', marginTop: 8, background: '#fff' }}
            sandbox="allow-scripts allow-same-origin"
            title="report preview"
          />
        )}
      </div>
    )
  }

  const str = parsed.type === 'json' ? JSON.stringify(parsed.value, null, 2) : parsed.value
  const preview = str.slice(0, 300)

  return (
    <div style={{ marginTop: 8 }}>
      <button className="feed-block-tab" onClick={() => setOpen(o => !o)}>
        {open ? '▾' : '▸'} {parsed.type === 'json' ? 'JSON' : 'Text'} ({str.length} chars)
      </button>
      <pre style={{
        fontSize: 11,
        fontFamily: 'var(--font-mono)',
        color: open ? 'var(--text-secondary)' : 'var(--text-muted)',
        whiteSpace: 'pre-wrap',
        wordBreak: 'break-word',
        maxHeight: open ? 400 : 60,
        overflow: 'auto',
        marginTop: 4,
        padding: 8,
        background: 'var(--depth-0)',
        borderRadius: 'var(--radius-sm)',
      }}>
        {open ? str : preview}{!open && str.length > 300 ? '...' : ''}
      </pre>
    </div>
  )
}

function RoundCard({ entry }) {
  const [open, setOpen] = useState(true)
  const brief = entry.brief || {}
  const assignments = brief.assignments || []
  const reports = entry.reports || []

  return (
    <div style={{ border: '1px solid var(--border)', borderRadius: 'var(--radius-md)', marginBottom: 8, overflow: 'hidden' }}>
      <button
        onClick={() => setOpen(o => !o)}
        style={{
          width: '100%', display: 'flex', alignItems: 'center', gap: 8,
          padding: '10px 14px', textAlign: 'left', background: 'var(--depth-2)',
        }}
      >
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-muted)' }}>
          R{entry.round}
        </span>
        <div style={{ display: 'flex', gap: 6, flex: 1, flexWrap: 'wrap' }}>
          {assignments.map(a => (
            <span key={a.agent_id} style={{
              fontSize: 10, padding: '2px 8px',
              border: `1px solid ${AGENT_COLORS[a.agent_id] || '#475569'}`,
              color: AGENT_COLORS[a.agent_id] || '#94a3b8',
              borderRadius: 12, textTransform: 'uppercase', letterSpacing: '0.04em',
            }}>
              {a.agent_id.replace(/_/g, ' ')}
            </span>
          ))}
        </div>
        {open ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
      </button>

      {open && (
        <div style={{ padding: 14 }}>
          {brief.context && (
            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 12, fontStyle: 'italic' }}>
              {brief.context}
            </div>
          )}

          {assignments.map(a => (
            <div key={a.agent_id} style={{
              borderLeft: `2px solid ${AGENT_COLORS[a.agent_id] || '#334155'}`,
              paddingLeft: 12, marginBottom: 12,
            }}>
              <div style={{
                fontSize: 10, fontWeight: 600, textTransform: 'uppercase',
                letterSpacing: '0.08em', color: AGENT_COLORS[a.agent_id] || '#94a3b8', marginBottom: 4,
              }}>
                {a.agent_id.replace(/_/g, ' ')}
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{a.task}</div>
              {a.expected_output && (
                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
                  Expected: {a.expected_output}
                </div>
              )}
            </div>
          ))}

          {reports.map((r, i) => (
            <div key={i} style={{
              borderLeft: `2px solid ${AGENT_COLORS[r.agent_id] || '#334155'}`,
              paddingLeft: 12, marginBottom: 12,
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                <span style={{
                  fontSize: 10, fontWeight: 600, textTransform: 'uppercase',
                  letterSpacing: '0.08em', color: AGENT_COLORS[r.agent_id] || '#94a3b8',
                }}>
                  {r.agent_id?.replace(/_/g, ' ')}
                </span>
                <span style={{
                  fontSize: 10, padding: '1px 6px', borderRadius: 4,
                  background: r.status === 'done' ? 'rgba(16,185,129,0.15)' : 'rgba(245,158,11,0.15)',
                  color: r.status === 'done' ? 'var(--signal-emerald)' : 'var(--signal-amber)',
                }}>
                  {r.status}
                </span>
                {r.confidence != null && (
                  <span style={{ fontSize: 10, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                    {Math.round(r.confidence * 100)}%
                  </span>
                )}
              </div>
              <OutputPreview raw={r.output} />
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default function AgentTrace({ history, meta }) {
  if (!history) return <span className="muted">Loading trace...</span>

  const stats = computeStats(history)

  return (
    <div>
      <div style={{
        display: 'flex', gap: 16, padding: '12px 0', marginBottom: 12,
        borderBottom: '1px solid var(--border)', flexWrap: 'wrap',
      }}>
        <Stat label="Rounds" value={stats.totalRounds} />
        {Object.entries(stats.agentCalls).map(([agent, n]) => (
          <Stat key={agent} label={agent.split('_')[0]} value={n} color={AGENT_COLORS[agent]} />
        ))}
        {stats.sources.length > 0 && <Stat label="Sources" value={stats.sources.length} />}
        {meta?.started_at && meta?.completed_at && (
          <Stat label="Duration" value={`${Math.round((new Date(meta.completed_at) - new Date(meta.started_at)) / 1000)}s`} />
        )}
      </div>

      {history.map(entry => (
        <RoundCard key={entry.round} entry={entry} />
      ))}
      {history.length === 0 && <span className="muted">No trace data for this run.</span>}
    </div>
  )
}

function Stat({ label, value, color }) {
  return (
    <div style={{ textAlign: 'center' }}>
      <div style={{ fontFamily: 'var(--font-mono)', fontSize: 14, fontWeight: 600, color: color || 'var(--text-primary)' }}>
        {value}
      </div>
      <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
        {label}
      </div>
    </div>
  )
}

function computeStats(history) {
  const agentCalls = {}
  const sources = new Set()
  for (const entry of history) {
    for (const r of entry.reports || []) {
      agentCalls[r.agent_id] = (agentCalls[r.agent_id] || 0) + 1
      try {
        const parsed = typeof r.output === 'string' ? JSON.parse(r.output) : r.output
        if (parsed?.raw_sources) Object.keys(parsed.raw_sources).forEach(s => sources.add(s))
        if (parsed?.sources) parsed.sources.forEach(s => sources.add(typeof s === 'string' ? s : s.name))
      } catch {}
    }
  }
  return { totalRounds: history.length, agentCalls, sources: [...sources] }
}
