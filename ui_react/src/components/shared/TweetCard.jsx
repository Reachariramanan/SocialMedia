import React from 'react'
import { ExternalLink } from 'lucide-react'

export default function TweetCard({ tweet }) {
  return (
    <div className="tweet-card">
      <div className="tweet-card-header">
        {tweet.author && <span className="tweet-card-author">@{tweet.author}</span>}
      </div>
      <div className="tweet-card-text">
        {tweet.text}
        {tweet.link && (
          <a className="event-link" href={tweet.link} target="_blank" rel="noreferrer" style={{ marginLeft: 6 }}>
            <ExternalLink size={11} />
          </a>
        )}
      </div>
      {tweet.published && <div className="tweet-card-time">{tweet.published}</div>}
    </div>
  )
}
