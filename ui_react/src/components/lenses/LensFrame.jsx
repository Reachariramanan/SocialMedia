import React, { useState } from 'react'
import { Maximize2, Minimize2 } from 'lucide-react'

export default function LensFrame({ title, icon, area, badge, expandable = true, children, className = '' }) {
  const [expanded, setExpanded] = useState(false)

  if (expanded) {
    return (
      <>
        <div className="lens-overlay-backdrop" onClick={() => setExpanded(false)} />
        <div className="lens-overlay">
          <div className="lens-header">
            {icon && <span className="lens-header-icon">{icon}</span>}
            <span className="lens-header-title">{title}</span>
            {badge && <span className="lens-header-badge">{badge}</span>}
            <span className="lens-header-spacer" />
            <button className="lens-expand-btn" onClick={() => setExpanded(false)}>
              <Minimize2 size={14} />
            </button>
          </div>
          <div className={`lens-body ${className}`}>
            {children}
          </div>
        </div>
      </>
    )
  }

  return (
    <div className={`lens lens-${area}`}>
      <div className="lens-header">
        {icon && <span className="lens-header-icon">{icon}</span>}
        <span className="lens-header-title">{title}</span>
        {badge && <span className="lens-header-badge">{badge}</span>}
        <span className="lens-header-spacer" />
        {expandable && (
          <button className="lens-expand-btn" onClick={() => setExpanded(true)}>
            <Maximize2 size={14} />
          </button>
        )}
      </div>
      <div className={`lens-body ${className}`}>
        {children}
      </div>
    </div>
  )
}
