import React, { useState, useMemo, useCallback } from 'react'
import { Radio } from 'lucide-react'
import LensFrame from './LensFrame'
import SignalTag from '../shared/SignalTag'
import TimelineBlock from '../shared/TimelineBlock'
import EventCard from '../shared/EventCard'
import { relTime } from '../../utils/formatters'

// The last 4 blocks from the API are category summaries, not time-based
const CATEGORY_LABELS = [
  'Longest Trending',
  'Max Tweets',
  'New Trends',
  'Popular Active',
]

function getBlockTag(block, idx, allBlocks) {
  // Check if block has an explicit label/category field
  if (block.label) return block.label
  if (block.category) return block.category

  // The last 4 blocks are category summaries
  const categoryStartIdx = Math.max(0, allBlocks.length - 4)
  if (idx >= categoryStartIdx) {
    return CATEGORY_LABELS[idx - categoryStartIdx]
  }

  // Time-based blocks
  if (idx === 0) return 'latest'
  const prevBlock = allBlocks[idx - 1]
  return relTime(prevBlock?.timestamp_utc, block.timestamp_utc)
}

export default function SignalStream({ snapshot, loading, onTagClick }) {
  const [expandedIdx, setExpandedIdx] = useState(0)
  const [search, setSearch] = useState('')

  const topTags = snapshot?.top_tags || []
  const blocks = snapshot?.trend_blocks || []
  const events = snapshot?.event_candidates || []

  const toggle = useCallback(i => setExpandedIdx(p => p === i ? -1 : i), [])

  const filteredBlocks = useMemo(() => {
    if (!search.trim()) return blocks.map((b, i) => ({ ...b, _origIdx: i }))
    const q = search.toLowerCase()
    return blocks
      .map((b, i) => ({ ...b, _origIdx: i }))
      .filter(b => (b.tags || []).some(t => t.toLowerCase().includes(q)))
  }, [blocks, search])

  const highEvents = useMemo(() =>
    events.filter(ev => (ev.headlines || []).length >= 2).slice(0, 5),
  [events])

  if (loading && !snapshot) {
    return (
      <LensFrame title="Signal Stream" icon={<Radio size={14} />} area="stream" badge="...">
        <div className="skeleton-lens">
          <div className="skeleton-line" />
          <div className="skeleton-line skeleton-line-medium" />
          <div className="skeleton-line skeleton-line-short" />
        </div>
      </LensFrame>
    )
  }

  return (
    <LensFrame
      title="Signal Stream"
      icon={<Radio size={14} />}
      area="stream"
      badge={`${topTags.length} tags`}
    >
      {/* Top tags — click triggers unified 3-source search */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 14 }}>
        {topTags.slice(0, 20).map(t => (
          <SignalTag key={t} name={t} onClick={() => onTagClick?.(t)} />
        ))}
      </div>

      {/* Filter input */}
      <input
        className="input-field"
        type="text"
        placeholder="Filter trends..."
        value={search}
        onChange={e => setSearch(e.target.value)}
        style={{ marginBottom: 12 }}
      />

      {/* Timeline blocks — time-based + category summary blocks */}
      <div style={{ marginBottom: 16 }}>
        <div style={{
          fontSize: 10, textTransform: 'uppercase', letterSpacing: '0.1em',
          color: 'var(--text-muted)', marginBottom: 8,
        }}>
          Trends ({filteredBlocks.length})
        </div>
        {filteredBlocks.map((block, i) => {
          const origIdx = block._origIdx ?? i
          const tag = getBlockTag(block, origIdx, blocks)
          const isCategory = origIdx >= Math.max(0, blocks.length - 4)
          return (
            <TimelineBlock
              key={block.timestamp_raw || origIdx}
              block={block}
              tag={tag}
              isCategory={isCategory}
              isExpanded={expandedIdx === i}
              onToggle={() => toggle(i)}
              onTagClick={onTagClick}
            />
          )
        })}
      </div>

      {/* High-signal events */}
      {highEvents.length > 0 && (
        <div>
          <div style={{
            fontSize: 10, textTransform: 'uppercase', letterSpacing: '0.1em',
            color: 'var(--text-muted)', marginBottom: 8,
          }}>
            Alerts ({highEvents.length})
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {highEvents.map((ev, i) => (
              <EventCard key={ev.tag || i} ev={ev} onTagClick={onTagClick} />
            ))}
          </div>
        </div>
      )}
    </LensFrame>
  )
}
