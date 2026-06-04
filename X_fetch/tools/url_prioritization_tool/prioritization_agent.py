from typing import List
from core.models.tweet import DiscoveredTweet
from core.utils.common import setup_logging

logger = setup_logging("URLPrioritizationAgent")

class URLPrioritizationAgent:
    def __init__(self):
        # High-value keywords
        self.high_value_keywords = ["AI", "Crypto", "Breaking", "Tech", "Research"]

    def calculate_priority(self, tweet: DiscoveredTweet) -> float:
        score = 0.0
        # Simple scoring logic
        for keyword in self.high_value_keywords:
            if keyword.lower() in tweet.query.lower():
                score += 0.5
        
        # Recency (higher score for more recent discoveries)
        # Simplified for now
        score += 0.2
        
        # Source quality
        if tweet.discovered_from == "Google News RSS":
            score += 0.3
            
        return min(score, 1.0)

    def process_discovered_tweets(self, tweets: List[DiscoveredTweet]) -> List[DiscoveredTweet]:
        scored_tweets = []
        for tweet in tweets:
            priority = self.calculate_priority(tweet)
            # Filter low priority if needed
            if priority > 0.3:
                scored_tweets.append(tweet)
        return scored_tweets
