"""General web search via SearXNG — no site: filter, broad results."""
import os
import httpx

SEARXNG_URL = os.getenv("SEARXNG_URL", "http://localhost:8888")


def run(query: str, categories: str = "general,news", limit: int = 50) -> dict:
    all_results = []
    page = 1

    try:
        while len(all_results) < limit:
            params = {
                "q": query,
                "format": "json",
                "safesearch": "0",
                "categories": categories,
                "pageno": page,
            }
            resp = httpx.get(
                f"{SEARXNG_URL}/search",
                params=params,
                timeout=20.0,
                headers={"User-Agent": "NewsReporterBot/1.0"},
            )
            resp.raise_for_status()
            data = resp.json()
            page_results = data.get("results", [])

            if not page_results:
                break

            all_results.extend(page_results)
            page += 1

        results = all_results[:limit]
        return {
            "query": query,
            "total_results": data.get("number_of_results", len(results)),
            "results": [
                {
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "content": r.get("content", "")[:500],
                    "score": r.get("score", 0),
                    "engine": r.get("engine", ""),
                }
                for r in results
            ],
        }
    except Exception as exc:
        return {"query": query, "error": str(exc), "results": []}
