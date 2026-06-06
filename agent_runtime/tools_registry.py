"""Build Yukta Tool objects from the tools-impl modules."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ecosystem', 'tools-impl'))

import fetch_feeds as _ff
import fetch_trends24 as _ft
import xfetch_discover as _xd
import xfetch_extract as _xe
import searxng_search as _ss
import websearch_general as _wg
import facebook_search as _fb
import terminal as _term

from yukta.tools.tool import Tool, ToolParameter, ToolType


def _tool(name, description, params, fn, trust="trusted"):
    return Tool(
        name=name,
        description=description,
        parameters=params,
        tool_type=ToolType.CUSTOM,
        function=fn,
        trust_level=trust,
    )


TOOL_FETCH_FEEDS = _tool(
    "fetch_feeds",
    "Fetch Google News RSS and tweets for a list of hashtags",
    [
        ToolParameter("hashtags", "string", "Comma-separated hashtags e.g. '#IPL,#Modi'", required=True),
        ToolParameter("limit", "integer", "Max articles per source per hashtag", required=False, default=8),
    ],
    lambda hashtags, limit=8: _ff.run(hashtags, limit),
)

TOOL_FETCH_TRENDS24 = _tool(
    "fetch_trends24",
    "Scrape Trends24.in via Lightpanda CDP to get trending hashtags",
    [
        ToolParameter("country", "string", "Country slug e.g. 'india','worldwide'", required=False, default="worldwide"),
        ToolParameter("max_tags", "integer", "Maximum hashtags to return", required=False, default=30),
    ],
    lambda country="worldwide", max_tags=30: _ft.run(country, max_tags),
)

TOOL_XFETCH_DISCOVER = _tool(
    "xfetch_discover",
    "Discover and prioritize tweet URLs for keywords via SearXNG + RSS",
    [
        ToolParameter("keywords", "string", "Comma-separated keywords e.g. 'IPL,Modi'", required=True),
        ToolParameter("limit", "integer", "Max prioritized URLs to return", required=False, default=50),
    ],
    lambda keywords, limit=50: _xd.run(keywords, limit),
)

TOOL_XFETCH_EXTRACT = _tool(
    "xfetch_extract",
    (
        "Extract tweet content from X/Twitter status URLs via Tor + Lightpanda. "
        "Returns normalised tweet text, author, engagement counts (likes/retweets/replies/views). "
        "Pass the tweet_urls discovered by xfetch_discover. "
        "Each URL yields up to 3 top tweets (~120 tokens each). "
        "Use AFTER xfetch_discover to get actual tweet text for reports."
    ),
    [
        ToolParameter("urls", "string", "Comma-separated X/Twitter status URLs to extract", required=True),
        ToolParameter("limit", "integer", "Max URLs to extract (default 20, cap 50)", required=False, default=20),
    ],
    lambda urls, limit=20: _xe.run(urls, use_tor=True, limit=limit),
)

TOOL_SEARXNG_SEARCH = _tool(
    "searxng_search",
    "Run a web search through local SearXNG metasearch engine",
    [
        ToolParameter("query", "string", "Search query", required=True),
        ToolParameter("engines", "string", "Comma-separated engine names (optional)", required=False, default=""),
        ToolParameter("limit", "integer", "Max results", required=False, default=10),
    ],
    lambda query, engines="", limit=10: _ss.run(query, engines, limit),
)

TOOL_WEBSEARCH_GENERAL = _tool(
    "websearch_general",
    "General web search via SearXNG — no platform filter, broad results from all engines",
    [
        ToolParameter("query", "string", "Search query", required=True),
        ToolParameter("categories", "string", "Comma-separated SearXNG categories", required=False, default="general,news"),
        ToolParameter("limit", "integer", "Max results", required=False, default=50),
    ],
    lambda query, categories="general,news", limit=50: _wg.run(query, categories, limit),
)

TOOL_FACEBOOK_SEARCH = _tool(
    "facebook_search",
    "Search Facebook posts and pages for keywords via site:facebook.com filter in SearXNG",
    [
        ToolParameter("keywords", "string", "Comma-separated keywords e.g. 'IPL,Modi'", required=True),
        ToolParameter("limit", "integer", "Max results", required=False, default=30),
    ],
    lambda keywords, limit=30: _fb.run(keywords, limit),
)

TOOL_TERMINAL = _tool(
    "terminal",
    "Execute a shell command in a sandboxed subprocess (Researcher only)",
    [
        ToolParameter("command", "string", "Shell command to execute", required=True),
        ToolParameter("cwd", "string", "Working directory (optional)", required=False, default=""),
        ToolParameter("timeout", "integer", "Timeout in seconds", required=False, default=30),
    ],
    lambda command, cwd="", timeout=30: _term.run(command, cwd, timeout),
    trust="sandbox",
)

ALL_TOOLS = [
    TOOL_FETCH_FEEDS, TOOL_FETCH_TRENDS24, TOOL_XFETCH_DISCOVER, TOOL_XFETCH_EXTRACT,
    TOOL_SEARXNG_SEARCH, TOOL_WEBSEARCH_GENERAL, TOOL_FACEBOOK_SEARCH, TOOL_TERMINAL,
]

# Per-agent tool sets
AGENT_TOOLS = {
    "master": [],
    "action_planner": [TOOL_FETCH_TRENDS24, TOOL_SEARXNG_SEARCH, TOOL_WEBSEARCH_GENERAL],
    "researcher": [
        TOOL_FETCH_FEEDS, TOOL_FETCH_TRENDS24, TOOL_XFETCH_DISCOVER, TOOL_XFETCH_EXTRACT,
        TOOL_SEARXNG_SEARCH, TOOL_WEBSEARCH_GENERAL, TOOL_FACEBOOK_SEARCH, TOOL_TERMINAL,
    ],
    "dashboard_layout_builder": [],
    "report_writer": [],
}
