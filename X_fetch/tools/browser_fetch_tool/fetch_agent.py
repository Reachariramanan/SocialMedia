import asyncio
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright
from core.utils.common import setup_logging, get_random_user_agent
from core.config.settings import settings

logger = setup_logging("BrowserFetchAgent")

class BrowserFetchAgent:
    def __init__(self, use_lightpanda: bool = True):
        self.use_lightpanda = use_lightpanda
        self.lightpanda_cdp_url = settings.LIGHTPANDA_CDP_URL

    async def fetch_with_playwright(self, url: str) -> Optional[Dict[str, Any]]:
        logger.info(f"Fetching with Playwright (Fallback): {url}")
        async with async_playwright() as p:
            # Fallback uses local playwright but still routes through Tor if configured
            proxy = {"server": settings.TOR_HTTP_PROXY} if settings.TOR_HTTP_PROXY else None
            browser = await p.chromium.launch(headless=True, proxy=proxy)
            context = await browser.new_context(user_agent=get_random_user_agent())
            page = await context.new_page()
            
            graphql_data = []

            async def intercept_response(response):
                if "/i/api/graphql/" in response.url:
                    try:
                        data = await response.json()
                        graphql_data.append({
                            "url": response.url,
                            "data": data
                        })
                    except Exception:
                        pass

            page.on("response", intercept_response)
            
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(5)
                return {"url": url, "graphql": graphql_data}
            except Exception as e:
                logger.error(f"Playwright fetch failed for {url}: {e}")
                if graphql_data:
                    return {"url": url, "graphql": graphql_data}
                return None
            finally:
                await browser.close()

    async def fetch_with_lightpanda(self, url: str) -> Optional[Dict[str, Any]]:
        logger.info(f"Fetching with Lightpanda CDP: {url} via {self.lightpanda_cdp_url}")
        async with async_playwright() as p:
            try:
                # Connect to the remote Lightpanda browser
                browser = await p.chromium.connect_over_cdp(self.lightpanda_cdp_url)
                # Lightpanda context already has Tor proxy configured at the browser level
                context = await browser.new_context(user_agent=get_random_user_agent())
                page = await context.new_page()
                
                graphql_data = []

                async def intercept_response(response):
                    if "/i/api/graphql/" in response.url:
                        try:
                            data = await response.json()
                            graphql_data.append({
                                "url": response.url,
                                "data": data
                            })
                        except Exception:
                            pass

                page.on("response", intercept_response)
                
                await page.goto(url, wait_until="domcontentloaded", timeout=20000)
                await asyncio.sleep(3)
                
                return {"url": url, "graphql": graphql_data}
            except Exception as e:
                logger.error(f"Lightpanda fetch failed for {url}: {e}")
                return None
            finally:
                if 'browser' in locals():
                    await browser.close()

    async def fetch(self, url: str) -> Optional[Dict[str, Any]]:
        if self.use_lightpanda and self.lightpanda_cdp_url:
            result = await self.fetch_with_lightpanda(url)
            if result:
                return result
        
        return await self.fetch_with_playwright(url)
