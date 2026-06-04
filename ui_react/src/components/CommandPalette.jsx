import React, { useRef, useEffect } from 'react'
import { Search, MapPin, Play, Compass, Rss, FileText } from 'lucide-react'

export default function CommandPalette({
  isOpen, search, setSearch, close,
  filteredLocations, filteredRuns, actions,
  selectLocation, onSelectRun,
}) {
  const inputRef = useRef(null)

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 50)
    }
  }, [isOpen])

  if (!isOpen) return null

  return (
    <>
      <div className="palette-backdrop" onClick={close} />
      <div className="palette">
        <div className="palette-search">
          <Search size={16} className="palette-search-icon" />
          <input
            ref={inputRef}
            className="palette-input"
            placeholder="Search locations, actions, reports..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            onKeyDown={e => e.key === 'Escape' && close()}
          />
          <span className="palette-esc">ESC</span>
        </div>

        <div className="palette-body">
          {/* Actions */}
          {actions.length > 0 && (
            <div className="palette-section">
              <div className="palette-section-label">Actions</div>
              {actions.map(a => (
                <button key={a.id} className="palette-item" onClick={a.action}>
                  <Play size={12} className="palette-item-icon" />
                  <span>{a.label}</span>
                  <span className="palette-item-hint">{a.hint}</span>
                </button>
              ))}
            </div>
          )}

          {/* Locations */}
          {filteredLocations.length > 0 && (
            <div className="palette-section">
              <div className="palette-section-label">Locations</div>
              {filteredLocations.map(p => (
                <button
                  key={`${p.country}/${p.city}`}
                  className="palette-item"
                  onClick={() => selectLocation(p)}
                >
                  <MapPin size={12} className="palette-item-icon" />
                  <span>{p.label}</span>
                  {p.city && <span className="palette-item-sub">{p.country}</span>}
                </button>
              ))}
            </div>
          )}

          {/* Reports */}
          {filteredRuns.length > 0 && (
            <div className="palette-section">
              <div className="palette-section-label">Recent Reports</div>
              {filteredRuns.map(r => (
                <button
                  key={r.run_id}
                  className="palette-item"
                  onClick={() => { onSelectRun?.(r); close() }}
                >
                  <FileText size={12} className="palette-item-icon" />
                  <span>{r.topic?.slice(0, 50) || 'Report'}</span>
                  <span className="palette-item-hint">{r.rounds}R</span>
                </button>
              ))}
            </div>
          )}

          {filteredLocations.length === 0 && actions.length === 0 && filteredRuns.length === 0 && (
            <div style={{ padding: 20, textAlign: 'center', color: 'var(--text-muted)', fontSize: 13 }}>
              No matches
            </div>
          )}
        </div>
      </div>
    </>
  )
}
