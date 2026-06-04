import React from 'react'
import { ChevronDown, ChevronUp } from 'lucide-react'
import { fmt } from '../../utils/formatters'

export default function TimelineBlock({ block, tag, isCategory, isExpanded, onToggle, onTagClick }) {
  const tags = block.tags || []
  return (
    <div className="timeline-block">
      <button className="timeline-block-header" onClick={onToggle}>
        {!isCategory && (
          <span className="timeline-block-time">{fmt(block.timestamp_utc)}</span>
        )}
        <span className={`timeline-block-tag ${
          tag === 'latest' ? 'timeline-block-tag-latest' :
          isCategory ? 'timeline-block-tag-category' : ''
        }`}>
          {tag === 'latest' ? 'latest' : isCategory ? tag : `${tag} ago`}
        </span>
        <span className="timeline-block-count">{tags.length} tags</span>
        <span className="timeline-block-chevron">
          {isExpanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
        </span>
      </button>
      {isExpanded && (
        <ol className="timeline-block-list">
          {tags.map((t, i) => (
            <li key={i} className="timeline-block-item">
              <span className="timeline-block-rank">{i + 1}</span>
              <button
                className={t.startsWith('#') ? 'trend-hash trend-tag-btn' : 'trend-plain trend-tag-btn'}
                onClick={() => onTagClick?.(t)}
                title={`Search all sources for ${t}`}
              >
                {t}
              </button>
            </li>
          ))}
        </ol>
      )}
    </div>
  )
}
