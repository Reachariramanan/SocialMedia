from typing import Dict, Any
from datetime import datetime
from core.models.tweet import Tweet, Metrics
from core.utils.common import setup_logging

logger = setup_logging("NormalizationAgent")

class NormalizationAgent:
    def normalize_tweet(self, raw_data: Dict[str, Any], source_url: str, discovered_from: str) -> Tweet:
        # Map raw GraphQL data to the standardized Tweet model
        # This is a mapping logic based on X's GraphQL schema
        
        # Example mapping (highly simplified)
        legacy = raw_data.get("legacy", {})
        user_results = raw_data.get("core", {}).get("user_results", {}).get("result", {})
        
        tweet = Tweet(
            tweet_id=raw_data.get("rest_id", ""),
            author_id=user_results.get("rest_id", ""),
            author_username=user_results.get("legacy", {}).get("screen_name", ""),
            author_name=user_results.get("legacy", {}).get("name", ""),
            text=legacy.get("full_text", ""),
            lang=legacy.get("lang", ""),
            hashtags=[h.get("text") for h in legacy.get("entities", {}).get("hashtags", [])],
            urls=[u.get("expanded_url") for u in legacy.get("entities", {}).get("urls", [])],
            metrics=Metrics(
                likes=legacy.get("favorite_count", 0),
                retweets=legacy.get("retweet_count", 0),
                replies=legacy.get("reply_count", 0),
                views=int(raw_data.get("views", {}).get("count", 0))
            ),
            timestamp=self._parse_timestamp(legacy.get("created_at")),
            source_url=source_url,
            discovered_from=discovered_from
        )
        return tweet

    def _parse_timestamp(self, ts_str: str) -> datetime:
        if not ts_str:
            return datetime.now()
        # X timestamp format: "Wed Oct 10 20:19:24 +0000 2018"
        try:
            return datetime.strptime(ts_str, "%a %b %d %H:%M:%S %z %Y")
        except ValueError:
            return datetime.now()
