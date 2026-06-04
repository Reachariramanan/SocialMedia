import React from 'react'
import { ExternalLink } from 'lucide-react'

export default function NewsCard({ entry }) {
  return (
    <div className="news-card">
      <div className="news-card-title">
        <span>{entry.title}</span>
        {entry.link && (
          <a className="event-link" href={entry.link} target="_blank" rel="noreferrer">
            <ExternalLink size={11} />
          </a>
        )}
      </div>
      {entry.source && <div className="news-card-source">{entry.source}</div>}
    </div>
  )
}
