"""Direct SearXNG JSON search tool."""
import os
import httpx

SEARXNG_URL = os.getenv("SEARXNG_URL", "http://localhost:8888")


def run(query: str, engines: str = "", limit: int = 10) -> dict:
    params = {"q": query, "format": "json", "safesearch": "0"}
    if engines:
        params["engines"] = engines

    try:
        resp = httpx.get(
            f"{SEARXNG_URL}/search",
            params=params,
            timeout=20.0,
            headers={"User-Agent": "NewsReporterBot/1.0"},
        )
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results", [])[:limit]
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
