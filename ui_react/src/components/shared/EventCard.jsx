import React, { useState } from 'react'
import { ChevronDown, ChevronUp, ExternalLink } from 'lucide-react'

export default function EventCard({ ev, onTagClick }) {
  const [open, setOpen] = useState(false)
  const headlines = Array.isArray(ev.headlines) ? ev.headlines : []
  const links = Array.isArray(ev.links) ? ev.links : []
  const label = ev.tag || ev.title || 'Signal'

  return (
    <div className="event-card">
      <button className="event-card-toggle" onClick={() => setOpen(v => !v)}>
        <span
          className="event-card-title"
          onClick={e => { if (onTagClick) { e.stopPropagation(); onTagClick(label) } }}
          style={onTagClick ? { cursor: 'pointer', textDecoration: 'underline dotted' } : {}}
        >
          {label}
        </span>
        {open ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
      </button>
      <div className="event-card-preview">{headlines[0] || 'No headline captured'}</div>
      {open && (
        <div className="event-card-detail">
          {headlines.map((h, i) => (
            <div key={i} className="event-headline">
              <span className="event-headline-num">{i + 1}</span>
              <span>{h}</span>
              {links[i] && (
                <a className="event-link" href={links[i]} target="_blank" rel="noreferrer">
                  <ExternalLink size={11} />
                </a>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
