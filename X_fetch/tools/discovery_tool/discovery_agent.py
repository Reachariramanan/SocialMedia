import httpx
import asyncio
from datetime import datetime
from typing import List, Dict
from core.models.tweet import DiscoveredTweet
from core.config.settings import settings
from core.utils.common import setup_logging, randomized_delay
from tools.discovery_tool.advanced_discovery import AdvancedDiscoveryAgent

logger = setup_logging("DiscoveryAgent")

class DiscoveryAgent:
    def __init__(self):
        self.advanced_agent = AdvancedDiscoveryAgent()

    async def run_discovery_loop(self, keywords: List[str]):
        logger.info(f"Starting comprehensive discovery for keywords: {keywords}")
        await self.advanced_agent.run_comprehensive_discovery(keywords)
