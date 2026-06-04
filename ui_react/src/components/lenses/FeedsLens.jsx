import React from 'react'
import { Rss } from 'lucide-react'
import LensFrame from './LensFrame'
import HashtagFeedBlock from '../shared/HashtagFeedBlock'
import SkeletonLens from '../shared/SkeletonLens'

export default function FeedsLens({ feeds }) {
  const { input, setInput, results, loading, error, doFetch } = feeds

  return (
    <LensFrame
      title="Feeds"
      icon={<Rss size={14} />}
      area="feeds"
      badge={results ? `${Object.keys(results.feeds || {}).length} tags` : null}
    >
      <div style={{ display: 'flex', gap: 8, marginBottom: 10 }}>
        <input
          className="input-field"
          placeholder="#IPL #AI #Modi"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && doFetch()}
          disabled={loading}
          style={{ flex: 1 }}
        />
        <button className="btn-action" onClick={() => doFetch()} disabled={loading || !input.trim()}>
          {loading ? '...' : 'Fetch'}
        </button>
      </div>

      {error && <div style={{ fontSize: 12, color: 'var(--signal-amber)', marginBottom: 8 }}>{error}</div>}
      {loading && <SkeletonLens lines={3} />}

      {results && Object.entries(results.feeds || {}).map(([tag, data]) => (
        <HashtagFeedBlock key={tag} tag={tag} data={data} />
      ))}

      {!results && !loading && (
        <span className="muted">Enter hashtags to fetch live Google News and tweets.</span>
      )}
    </LensFrame>
  )
}
