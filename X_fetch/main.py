import asyncio
import argparse
from tools.discovery_tool.discovery_agent import DiscoveryAgent
from tools.discovery_tool.rss_ingestion import RSSIngestion
from tools.url_prioritization_tool.prioritization_agent import URLPrioritizationAgent
from tools.browser_fetch_tool.fetch_agent import BrowserFetchAgent
from tools.graphql_interception_tool.interception_agent import GraphQLInterceptionAgent
from tools.session_identity_tool.identity_agent import SessionIdentityAgent
from tools.extraction_normalization_tool.normalization_agent import NormalizationAgent
from tools.deduplication_tool.deduplication_agent import DeduplicationAgent
from tools.persistence_tool.persistence_agent import PersistenceAgent
from tools.monitoring_telemetry_tool.monitoring_agent import MonitoringAgent
from core.utils.queue import QueueSystem
from core.utils.common import setup_logging
from core.utils.tor_control import renew_tor_identity

logger = setup_logging("Main")

async def run_discovery_agent():
    discovery_agent = DiscoveryAgent()
    queries = ["site:x.com/status/ AI", "site:x.com/status/ Crypto"]
    await discovery_agent.run_discovery_loop(queries)

async def run_rss_ingestion_agent():
    rss_ingestion = RSSIngestion()
    keywords = ["AI", "Crypto"]
    await rss_ingestion.run_rss_loop(keywords)

async def run_browser_fetch_agent():
    fetch_agent = BrowserFetchAgent()
    # In a real scenario, this would consume from a queue
    test_url = "https://x.com/TwitterDev/status/1460000000000000000" # Example URL
    result = await fetch_agent.fetch(test_url)
    if result:
        logger.info(f"Fetched data for {test_url}: {result.keys()}")

async def run_monitoring_agent():
    monitoring_agent = MonitoringAgent()
    monitoring_agent.start_monitoring_server()
    while True:
        await asyncio.sleep(60) # Keep the server running

async def run_tor_renewal_agent():
    logger.info("Testing Tor identity renewal...")
    success = await renew_tor_identity()
    if success:
        logger.info("Tor identity renewal successful.")
    else:
        logger.error("Tor identity renewal failed.")

async def main():
    parser = argparse.ArgumentParser(description="Run X/Twitter Intelligence System Agents")
    parser.add_argument("--agent", type=str, help="Specify which agent to run (discovery, rss, fetch, monitor, tor_renew)")
    args = parser.parse_args()

    if args.agent == "discovery":
        await run_discovery_agent()
    elif args.agent == "rss":
        await run_rss_ingestion_agent()
    elif args.agent == "fetch":
        await run_browser_fetch_agent()
    elif args.agent == "monitor":
        await run_monitoring_agent()
    elif args.agent == "tor_renew":
        # This agent is meant to be run within the docker-compose environment
        # where the tor-proxy service is accessible.
        await run_tor_renewal_agent()
    else:
        logger.info("No agent specified. Please use --agent [discovery|rss|fetch|monitor|tor_renew]")

if __name__ == "__main__":
    asyncio.run(main())
