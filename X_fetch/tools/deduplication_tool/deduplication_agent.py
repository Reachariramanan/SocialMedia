import hashlib
from typing import Set
from core.utils.common import setup_logging

logger = setup_logging("DeduplicationAgent")

class DeduplicationAgent:
    def __init__(self):
        # In production, this would use Redis Bloom Filter or a Set
        self.seen_ids: Set[str] = set()

    def is_duplicate(self, tweet_id: str) -> bool:
        if tweet_id in self.seen_ids:
            return True
        self.seen_ids.add(tweet_id)
        return False

    def get_content_hash(self, text: str) -> str:
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def is_content_duplicate(self, text: str, existing_hashes: Set[str]) -> bool:
        content_hash = self.get_content_hash(text)
        return content_hash in existing_hashes
