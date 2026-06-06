"""Facebook-filtered search via SearXNG using site:facebook.com queries."""
import os
import httpx

SEARXNG_URL = os.getenv("SEARXNG_URL", "http://localhost:8888")

_QUERY_PATTERNS = [
    'site:facebook.com "{kw}"',
    'site:facebook.com {kw}',
    '"{kw}" site:facebook.com',
]


def run(keywords: str, limit: int = 30) -> dict:
    kw_list = [k.strip().lstrip('#') for k in keywords.split(',') if k.strip()]
    all_results = []

    try:
        for kw in kw_list:
            for pattern in _QUERY_PATTERNS:
                query = pattern.replace('{kw}', kw)
                params = {
                    "q": query,
                    "format": "json",
                    "safesearch": "0",
                    "categories": "general,social media",
                    "pageno": 1,
                }
                resp = httpx.get(
                    f"{SEARXNG_URL}/search",
                    params=params,
                    timeout=20.0,
                    headers={"User-Agent": "NewsReporterBot/1.0"},
                )
                resp.raise_for_status()
                data = resp.json()
                for r in data.get("results", []):
                    url = r.get("url", "")
                    if "facebook.com" in url:
                        all_results.append({
                            "title": r.get("title", ""),
                            "url": url,
                            "content": r.get("content", "")[:500],
                            "score": r.get("score", 0),
                            "engine": r.get("engine", ""),
                            "keyword": kw,
                        })
                if len(all_results) >= limit:
                    break
            if len(all_results) >= limit:
                break

        seen = set()
        unique = []
        for r in all_results:
            if r["url"] not in seen:
                seen.add(r["url"])
                unique.append(r)

        return {
            "keywords": kw_list,
            "total_results": len(unique),
            "results": unique[:limit],
        }
    except Exception as exc:
        return {"keywords": kw_list, "error": str(exc), "results": []}
