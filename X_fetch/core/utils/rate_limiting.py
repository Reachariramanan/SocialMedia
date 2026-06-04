import asyncio
import time
from collections import defaultdict
from core.utils.common import setup_logging

logger = setup_logging("RateLimiter")

class RateLimiter:
    def __init__(self, calls: int, period: int):
        self.calls = calls
        self.period = period
        self.history = defaultdict(list)

    async def wait_for_permission(self, key: str = "global"):
        now = time.time()
        self.history[key] = [t for t in self.history[key] if t > now - self.period]

        if len(self.history[key]) >= self.calls:
            sleep_time = self.period - (now - self.history[key][0])
            logger.info(f"Rate limit hit for {key}. Sleeping for {sleep_time:.2f} seconds.")
            await asyncio.sleep(sleep_time)
            self.history[key] = [t for t in self.history[key] if t > time.time() - self.period]

        self.history[key].append(time.time())
