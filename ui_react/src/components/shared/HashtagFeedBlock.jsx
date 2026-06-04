import React, { useState } from 'react'
import NewsCard from './NewsCard'
import TweetCard from './TweetCard'

export default function HashtagFeedBlock({ tag, data }) {
  const [tab, setTab] = useState('news')
  const news = data?.google_news?.entries || []
  const tweets = data?.tweets?.tweets || []
  const tweetSrc = data?.tweets?.source || ''
  const tweetErr = data?.tweets?.error || ''
  const tweetsOk = data?.tweets?.ok !== false

  return (
    <div style={{ marginBottom: 16 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
        <span style={{ color: 'var(--signal-violet)', fontWeight: 600, fontSize: 13 }}>{tag}</span>
        <div className="feed-block-tabs">
          <button
            className={`feed-block-tab ${tab === 'news' ? 'feed-block-tab-active' : ''}`}
            onClick={() => setTab('news')}
          >
            News ({news.length})
          </button>
          <button
            className={`feed-block-tab ${tab === 'tweets' ? 'feed-block-tab-active' : ''}`}
            onClick={() => setTab('tweets')}
          >
            {tweetsOk ? `Tweets (${tweets.length})` : 'Tweets (via SearXNG)'}
          </button>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {tab === 'news' && (
          news.length === 0
            ? <span className="muted">No Google News results</span>
            : news.map((e, i) => <NewsCard key={i} entry={e} />)
        )}
        {tab === 'tweets' && (
          tweetErr && tweets.length === 0
            ? <span className="muted">Tweet sources unavailable. Use Discover for SearXNG-based search.</span>
            : <>
                {tweetSrc && <span className="muted">via {tweetSrc}</span>}
                {tweets.length === 0
                  ? <span className="muted">No tweets found</span>
                  : tweets.map((t, i) => <TweetCard key={i} tweet={t} />)
                }
              </>
        )}
      </div>
    </div>
  )
}
