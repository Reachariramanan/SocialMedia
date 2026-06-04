import React from 'react'
import { Activity } from 'lucide-react'
import LensFrame from './LensFrame'
import StatusOrb from '../shared/StatusOrb'

export default function SystemPulse({ systemStatus }) {
  const { xfetch, scheduler, healthy } = systemStatus

  return (
    <LensFrame
      title="System"
      icon={<Activity size={14} />}
      area="system"
      badge={healthy ? 'OK' : 'WARN'}
      expandable={false}
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {/* SearXNG / X_fetch */}
        <Row
          label="X Discovery"
          value={xfetch?.available ? 'Online' : 'Offline'}
          status={xfetch?.available ? 'ok' : 'warn'}
        />
        {xfetch?.last_run && (
          <Row
            label="Last Scan"
            value={new Date(xfetch.last_run).toLocaleTimeString()}
            sub={`${xfetch.last_count || 0} URLs`}
          />
        )}

        {/* Scheduler */}
        <Row
          label="Auto-Run"
          value={scheduler?.scheduler?.running ? 'Active' : 'Idle'}
          status={scheduler?.scheduler?.running ? 'ok' : 'idle'}
        />
        {scheduler?.scheduler?.last_run_at && (
          <Row
            label="Last Auto"
            value={new Date(scheduler.scheduler.last_run_at).toLocaleTimeString()}
          />
        )}

        {/* Keywords */}
        {xfetch?.last_keywords?.length > 0 && (
          <div>
            <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 4 }}>
              Tracked Keywords
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
              {xfetch.last_keywords.map(kw => (
                <span key={kw} style={{
                  fontSize: 10, padding: '2px 7px',
                  borderRadius: 10, background: 'var(--depth-2)',
                  border: '1px solid var(--border)',
                  color: 'var(--signal-violet)',
                }}>
                  #{kw}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </LensFrame>
  )
}

function Row({ label, value, status, sub }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
      <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>{label}</span>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        {status && <StatusOrb status={status} />}
        <span style={{ fontSize: 12, fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>
          {value}
        </span>
        {sub && <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>{sub}</span>}
      </div>
    </div>
  )
}
