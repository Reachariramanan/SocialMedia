import React, { useState } from 'react'
import { Clock, Repeat, CalendarClock, Trash2 } from 'lucide-react'
import { timeUntil, timeAgo } from '../utils/formatters'

// Recurring cadence presets → interval in seconds.
const INTERVAL_PRESETS = [
  { label: 'Hourly', value: 3600 },
  { label: 'Every 6h', value: 21600 },
  { label: 'Every 12h', value: 43200 },
  { label: 'Daily', value: 86400 },
]

function cadenceLabel(s) {
  if (s.type === 'once') {
    return s.run_at ? new Date(s.run_at).toLocaleString() : 'one-time'
  }
  const preset = INTERVAL_PRESETS.find(p => p.value === s.interval_sec)
  if (preset) return preset.label.toLowerCase()
  const h = Math.round((s.interval_sec || 0) / 3600)
  return h >= 1 ? `every ${h}h` : `every ${Math.round((s.interval_sec || 0) / 60)}m`
}

export default function SchedulesPanel({ schedules, loading, error, onCreate, onDelete }) {
  const [topic, setTopic] = useState('')
  const [type, setType] = useState('recurring')
  const [interval, setInterval] = useState(3600)
  const [runAt, setRunAt] = useState('')
  const [formError, setFormError] = useState(null)

  const submit = async () => {
    setFormError(null)
    if (!topic.trim()) { setFormError('Enter a topic'); return }
    const payload = { topic: topic.trim(), type }
    if (type === 'recurring') {
      payload.interval_sec = Number(interval)
    } else {
      if (!runAt) { setFormError('Pick a date & time'); return }
      // datetime-local is local time; convert to ISO UTC.
      payload.run_at = new Date(runAt).toISOString()
    }
    try {
      await onCreate(payload)
      setTopic('')
      setRunAt('')
    } catch (e) {
      setFormError(e.message || 'Could not create schedule')
    }
  }

  // Sort: active first (by soonest next run), then completed.
  const sorted = [...(schedules || [])].sort((a, b) => {
    if (a.enabled !== b.enabled) return a.enabled ? -1 : 1
    return (a.next_run_at || '').localeCompare(b.next_run_at || '')
  })

  return (
    <div className="schedules-panel">
      {/* Create form */}
      <div className="schedule-form">
        <input
          className="input-field"
          placeholder="Topic to report on (e.g. AI policy India)…"
          value={topic}
          onChange={e => setTopic(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && submit()}
        />

        <div className="schedule-type-toggle">
          <button
            className={`schedule-type-btn${type === 'recurring' ? ' schedule-type-btn-active' : ''}`}
            onClick={() => setType('recurring')}
          >
            <Repeat size={12} /> Recurring
          </button>
          <button
            className={`schedule-type-btn${type === 'once' ? ' schedule-type-btn-active' : ''}`}
            onClick={() => setType('once')}
          >
            <CalendarClock size={12} /> One-time
          </button>
        </div>

        {type === 'recurring' ? (
          <select
            className="input-field"
            value={interval}
            onChange={e => setInterval(Number(e.target.value))}
          >
            {INTERVAL_PRESETS.map(p => (
              <option key={p.value} value={p.value}>{p.label}</option>
            ))}
          </select>
        ) : (
          <input
            className="input-field"
            type="datetime-local"
            value={runAt}
            onChange={e => setRunAt(e.target.value)}
          />
        )}

        <button className="btn-action" onClick={submit} disabled={loading}>
          {loading ? '…' : 'Schedule'}
        </button>

        {(formError || error) && (
          <div className="schedule-form-error">{formError || error}</div>
        )}
      </div>

      {/* Schedule list */}
      <div className="run-list" style={{ width: '100%', flex: 1 }}>
        <div className="run-list-header">
          <Clock size={11} style={{ display: 'inline', marginRight: 6 }} />
          Scheduled Reports
        </div>
        <div className="run-list-body">
          {sorted.length === 0 && (
            <div style={{ padding: '16px 14px' }}>
              <span className="muted">No schedules yet. Create one above.</span>
            </div>
          )}
          {sorted.map(s => (
            <div key={s.id} className="run-row">
              <div className="run-btn" style={{ cursor: 'default' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, width: '100%' }}>
                  <span className="run-btn-topic" style={{ flex: 1 }}>{s.topic}</span>
                  <span className={`schedule-badge${s.enabled ? '' : ' schedule-badge-done'}`}>
                    {s.enabled ? (s.type === 'once' ? 'one-time' : 'active') : 'completed'}
                  </span>
                </div>
                <span className="run-btn-meta">
                  {cadenceLabel(s)}
                  {s.enabled && s.next_run_at ? ` · next ${timeUntil(s.next_run_at)}` : ''}
                  {s.last_run_at ? ` · ran ${timeAgo(s.last_run_at)}` : ''}
                </span>
              </div>
              <button
                className="run-delete-btn"
                title="Delete schedule"
                onClick={() => {
                  if (window.confirm(`Delete schedule "${s.topic}"?`)) onDelete?.(s.id)
                }}
              >
                <Trash2 size={13} />
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
