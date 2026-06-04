-- PostgreSQL Schema for X Intelligence System

CREATE TABLE IF NOT EXISTS authors (
    author_id VARCHAR(255) PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tweets (
    tweet_id VARCHAR(255) PRIMARY KEY,
    author_id VARCHAR(255) REFERENCES authors(author_id),
    text TEXT,
    lang VARCHAR(10),
    hashtags TEXT[],
    urls TEXT[],
    likes INTEGER DEFAULT 0,
    retweets INTEGER DEFAULT 0,
    replies INTEGER DEFAULT 0,
    views INTEGER DEFAULT 0,
    quoted_tweet_id VARCHAR(255),
    reply_to_tweet_id VARCHAR(255),
    timestamp TIMESTAMP WITH TIME ZONE,
    source_url TEXT,
    discovered_from VARCHAR(255),
    priority_score FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tweets_timestamp ON tweets(timestamp);
CREATE INDEX idx_tweets_author_id ON tweets(author_id);
CREATE INDEX idx_tweets_priority_score ON tweets(priority_score);
