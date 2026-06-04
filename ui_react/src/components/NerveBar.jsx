import React from 'react'
import { Search, RefreshCw, MapPin, Settings } from 'lucide-react'
import { fmt } from '../utils/formatters'

export default function NerveBar({ location, lastRefresh, onRefresh, loading, onOpenPalette, systemHealth, onOpenSettings, settingsOpen }) {
  return (
    <header className="nerve-bar">
      <span className="nerve-logo">Z</span>
      <span className="nerve-pulse" />
      <span className="nerve-location">
        <MapPin size={10} style={{ flexShrink: 0 }} />
        {location || 'Worldwide'}
      </span>

      <button className="nerve-search-trigger" onClick={onOpenPalette}>
        <Search className="search-icon" size={14} />
        <span>Search locations, actions...</span>
        <span className="search-hint">⌘K</span>
      </button>

      <span className="nerve-spacer" />

      <div className="nerve-orbs">
        <span className="status-label">
          <span className={`status-orb ${systemHealth?.healthy ? 'status-orb-ok' : 'status-orb-warn'}`} />
          {systemHealth?.healthy ? 'LIVE' : 'DEGRADED'}
        </span>
      </div>

      <button className="nerve-refresh" onClick={onRefresh} disabled={loading}>
        <RefreshCw size={12} className={loading ? 'animate-spin' : ''} />
        <span className="nerve-time">{lastRefresh ? fmt(lastRefresh.toISOString()) : '—'}</span>
      </button>

      <button
        className={`nerve-settings-btn${settingsOpen ? ' nerve-settings-btn-active' : ''}`}
        onClick={onOpenSettings}
        title="Settings"
      >
        <Settings size={14} />
      </button>
    </header>
  )
}
