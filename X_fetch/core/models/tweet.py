from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class Metrics(BaseModel):
    likes: int = 0
    retweets: int = 0
    replies: int = 0
    views: int = 0

class Tweet(BaseModel):
    tweet_id: str
    author_id: str
    author_username: str
    author_name: str
    text: str
    lang: str
    hashtags: List[str] = []
    urls: List[str] = []
    media: List[Dict[str, Any]] = []
    metrics: Metrics = Field(default_factory=Metrics)
    quoted_tweet: Optional[Dict[str, Any]] = None
    reply_to: Optional[str] = None
    timestamp: datetime
    source_url: str
    discovered_from: str
    priority_score: float = 0.0

class DiscoveredTweet(BaseModel):
    tweet_url: str
    discovered_from: str
    query: str
    timestamp: datetime
