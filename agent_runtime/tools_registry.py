"""Build Yukta Tool objects from the tools-impl modules."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ecosystem', 'tools-impl'))

import fetch_feeds as _ff
import fetch_trends24 as _ft
import xfetch_discover as _xd
import searxng_search as _ss
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

ALL_TOOLS = [TOOL_FETCH_FEEDS, TOOL_FETCH_TRENDS24, TOOL_XFETCH_DISCOVER, TOOL_SEARXNG_SEARCH, TOOL_TERMINAL]

# Per-agent tool sets
AGENT_TOOLS = {
    "master": [],
    "action_planner": [TOOL_FETCH_TRENDS24, TOOL_SEARXNG_SEARCH],
    "researcher": [TOOL_FETCH_FEEDS, TOOL_FETCH_TRENDS24, TOOL_XFETCH_DISCOVER, TOOL_SEARXNG_SEARCH, TOOL_TERMINAL],
    "dashboard_layout_builder": [],
    "report_writer": [],
}
