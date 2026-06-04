import React, { useState, useRef } from 'react'
import { FileText, Download, Eye } from 'lucide-react'
import LensFrame from './LensFrame'
import AgentTrace from '../shared/AgentTrace'
import { timeAgo } from '../../utils/formatters'

export default function HeroLens({ runs, selectedRun, html, runHistory, onSelectRun, loading }) {
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
    <LensFrame
      title="Intelligence Report"
      icon={<FileText size={14} />}
      area="hero"
      badge={selectedRun ? timeAgo(selectedRun.completed_at) : null}
      className="lens-body-flush"
    >
      {/* Toolbar */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: 8,
        padding: '8px 16px', borderBottom: '1px solid var(--border)',
        flexShrink: 0,
      }}>
        {/* Run selector */}
        <div style={{ display: 'flex', gap: 6, flex: 1, overflow: 'auto' }}>
          {runs.slice(0, 8).map(run => (
            <button
              key={run.run_id}
              onClick={() => onSelectRun(run)}
              style={{
                padding: '4px 10px', borderRadius: 'var(--radius-sm)',
                fontSize: 11, whiteSpace: 'nowrap',
                border: `1px solid ${selectedRun?.run_id === run.run_id ? 'var(--signal-blue)' : 'var(--border)'}`,
                color: selectedRun?.run_id === run.run_id ? 'var(--signal-blue)' : 'var(--text-muted)',
                background: selectedRun?.run_id === run.run_id ? 'rgba(59,130,246,0.08)' : 'transparent',
              }}
            >
              {run.topic?.slice(0, 30) || 'Report'}
              <span style={{ marginLeft: 6, fontFamily: 'var(--font-mono)', fontSize: 9, opacity: 0.6 }}>
                {timeAgo(run.completed_at)}
              </span>
            </button>
          ))}
        </div>

        {selectedRun && html && (
          <button className="lens-expand-btn" onClick={downloadHtml} title="Download HTML">
            <Download size={14} />
          </button>
        )}
        {selectedRun && (
          <button
            className="lens-expand-btn"
            onClick={() => setTraceOpen(o => !o)}
            title="Agent trace"
            style={traceOpen ? { color: 'var(--signal-blue)' } : {}}
          >
            <Eye size={14} />
          </button>
        )}
      </div>

      {/* Content */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Report iframe */}
        <div style={{ flex: 1, position: 'relative' }}>
          {loading && (
            <div style={{
              position: 'absolute', inset: 0,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              color: 'var(--text-muted)', fontSize: 13,
            }}>
              <span className="animate-spin" style={{ display: 'inline-block', marginRight: 8 }}>⟳</span>
              Loading report...
            </div>
          )}
          {!loading && html && (
            <iframe
              ref={iframeRef}
              srcDoc={html}
              style={{ width: '100%', height: '100%', border: 'none' }}
              sandbox="allow-scripts allow-same-origin"
              title="News Dashboard"
            />
          )}
          {!loading && !html && runs.length === 0 && (
            <div style={{
              display: 'flex', flexDirection: 'column',
              alignItems: 'center', justifyContent: 'center',
              height: '100%', color: 'var(--text-muted)', gap: 12,
            }}>
              <FileText size={32} style={{ opacity: 0.3 }} />
              <span>No reports yet. Run Yukta to generate one.</span>
            </div>
          )}
        </div>

        {/* Trace panel */}
        {traceOpen && selectedRun && (
          <div style={{
            width: 400, borderLeft: '1px solid var(--border)',
            overflow: 'auto', padding: 14, flexShrink: 0,
          }}>
            <AgentTrace history={runHistory} meta={selectedRun} />
          </div>
        )}
      </div>
    </LensFrame>
  )
}
