import React, { useState } from 'react'
import { Cpu } from 'lucide-react'
import LensFrame from './LensFrame'
import ProgressArc from '../shared/ProgressArc'
import StatusOrb from '../shared/StatusOrb'

export default function YuktaLens({ agentRun }) {
  const { start, runId, status, rounds, isRunning, error } = agentRun
  const [topic, setTopic] = useState('')

  const statusColor = {
    queued: 'warn',
    running: 'ok',
    done: 'ok',
    error: 'error',
  }[status] || 'idle'

  return (
    <LensFrame
      title="Yukta"
      icon={<Cpu size={14} />}
      area="yukta"
      badge={status ? status.toUpperCase() : 'READY'}
    >
      <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
        <input
          className="input-field"
          placeholder="Topic or leave blank for top trends..."
          value={topic}
          onChange={e => setTopic(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !isRunning && start(topic)}
          disabled={isRunning}
          style={{ flex: 1 }}
        />
        <button
          className="btn-action"
          onClick={() => start(topic)}
          disabled={isRunning}
        >
          {isRunning ? 'Running...' : 'Generate'}
        </button>
      </div>

      {error && (
        <div style={{ fontSize: 12, color: 'var(--signal-rose)', marginBottom: 8 }}>
          {error}
        </div>
      )}

      {status && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <ProgressArc current={rounds.length} total={5} size={56} />
          <div>
            <div className="status-label" style={{ marginBottom: 4 }}>
              <StatusOrb status={statusColor} />
              <span style={{ color: `var(--signal-${statusColor === 'ok' ? 'emerald' : statusColor === 'warn' ? 'amber' : statusColor === 'error' ? 'rose' : 'blue'})` }}>
                {status.toUpperCase()}
              </span>
            </div>
            {runId && (
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--text-muted)' }}>
                #{runId}
              </div>
            )}
            {rounds.length > 0 && (
              <div style={{ display: 'flex', gap: 4, marginTop: 6 }}>
                {rounds.map(r => (
                  <span key={r} style={{
                    width: 20, height: 20, borderRadius: '50%',
                    background: 'var(--depth-2)', border: '1px solid var(--signal-blue)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: 9, fontFamily: 'var(--font-mono)', color: 'var(--signal-blue)',
                  }}>
                    {r}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {!status && (
        <span className="muted">Enter a topic and click Generate to run the Yukta agent pipeline.</span>
      )}
    </LensFrame>
  )
}
