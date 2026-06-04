#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

import feedparser
import httpx
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

TRENDS24_URL = "https://trends24.in/"

EXTRACTION_SCRIPT = r"""
() => {
  const clean = (value) => (value || '').replace(/\s+/g, ' ').trim();
  const unique = (values) => Array.from(new Set(values.filter(Boolean)));

  const location = clean(document.querySelector('#location-menu-button span')?.textContent) || null;
  const blocks = [];

  const containers = Array.from(document.querySelectorAll('.list-container'));
  for (const node of containers) {
    const titleNode = node.querySelector('h3.title, h3');
    const title = clean(titleNode?.textContent);
    const timestamp = titleNode?.getAttribute('data-timestamp') || null;
    const tags = unique(Array.from(node.querySelectorAll('a')).map((a) => clean(a.textContent)));
    if (title || tags.length) {
      blocks.push({ title, timestamp, tags });
    }
  }

  if (!blocks.length) {
    const fallbackContainers = Array.from(
      document.querySelectorAll('.trend-card, .trend-card__list, ol.trend-card__list, .trend-list, .trend-card__content')
    );
    for (const node of fallbackContainers) {
      const title = clean(node.querySelector('h3, h2, .trend-card__header')?.textContent);
      const tags = unique(Array.from(node.querySelectorAll('a')).map((a) => clean(a.textContent)));
      if (title || tags.length) {
        blocks.push({ title, timestamp: null, tags });
      }
    }
  }

  const looseHashtags = unique(
    Array.from(document.querySelectorAll('a'))
      .map((a) => clean(a.textContent))
      .filter((value) => value.startsWith('#'))
  );

  return {
    title: document.title,
    location,
    url: window.location.href,
    blocks,
    looseHashtags,
  };
}
"""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_timestamp(raw_value: Optional[str]) -> Optional[str]:
    if not raw_value:
        return None

    try:
        value = float(raw_value)
        if value > 1e12:
            value /= 1000.0
        return datetime.fromtimestamp(value, tz=timezone.utc).isoformat()
    except Exception:
        return None


def normalize_tag(raw_value: str) -> Optional[str]:
    value = re.sub(r"\s+", " ", raw_value).strip()
    if not value:
        return None

    value = re.sub(r"^[0-9]+[\.)\-: ]+", "", value).strip()
    if not value:
        return None

    if len(value) > 96:
        return None

    return value


def to_hashtag(raw_value: str) -> Optional[str]:
    value = normalize_tag(raw_value)
    if not value:
        return None

    compact = re.sub(r"[^\w]+", "", value, flags=re.UNICODE)
    if not compact:
        return None

    return f"#{compact[:50]}"


def _evaluate_with_retry(page: Any, attempts: int = 3) -> Dict[str, Any]:
    last_error: Optional[Exception] = None

    for _ in range(attempts):
        try:
            return page.evaluate(EXTRACTION_SCRIPT)
        except Exception as exc:
            last_error = exc
            if "Execution context was destroyed" in str(exc):
                page.wait_for_timeout(900)
                continue
            raise

    if last_error:
        raise last_error

    raise RuntimeError("Failed to evaluate Trends24 extraction script")


def scrape_trends24(cdp_url: str, timeout_ms: int) -> Dict[str, Any]:
    with sync_playwright() as playwright:
        browser = playwright.chromium.connect_over_cdp(cdp_url)
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.new_page()

        last_error: Optional[Exception] = None

        try:
            for _ in range(3):
                try:
                    page.goto(TRENDS24_URL, wait_until="domcontentloaded", timeout=timeout_ms)

                    try:
                        page.wait_for_load_state("networkidle", timeout=min(timeout_ms, 12000))
                    except PlaywrightTimeoutError:
                        pass

                    page.wait_for_timeout(1500)

                    if "trends24.in" not in page.url:
                        last_error = RuntimeError(f"Unexpected redirect while loading Trends24: {page.url}")
                        page.wait_for_timeout(1200)
                        continue

                    return _evaluate_with_retry(page, attempts=3)
                except Exception as exc:
                    last_error = exc
                    page.wait_for_timeout(1200)

            if last_error:
                raise last_error

            raise RuntimeError("Failed to scrape Trends24 after multiple attempts")
        finally:
            page.close()
            browser.close()


def sanitize_llm_summary(raw_text: str) -> str:
    text = raw_text or ""

    text = re.sub(r"<think>.*?</think>", "", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"</think>", "", text, flags=re.IGNORECASE)

    heading_match = re.search(r"(?im)^#{2,6}\s*Overview\b", text)
    if heading_match:
        text = text[heading_match.start():]

    text = text.strip()

    lowered = text.lower()
    invalid_markers = [
        "thinking process",
        "analyze user input",
        "identify key constraints",
        "draft - section by section",
        "self-correction",
        "final check against constraints",
    ]
    if any(marker in lowered for marker in invalid_markers):
        return ""

    return text


def deterministic_summary(location: str, tags: List[str], events: List[Dict[str, Any]]) -> str:
    lines: List[str] = []

    lines.append("### Overview")
    if tags:
        tag_preview = ", ".join(tags[:6])
        lines.append(
            f"Location: {location}. Active trend signals detected across hashtags such as {tag_preview}."
        )
    else:
        lines.append(f"Location: {location}. No stable hashtag signals were detected in this cycle.")

    lines.append("")
    lines.append("### Active Events")
    if events:
        for event in events[:5]:
            tag = event.get("tag", "")
            headlines = event.get("headlines", [])
            if headlines:
                lines.append(f"- {tag}: {headlines[0]}")
            else:
                lines.append(f"- {tag}: Event signal detected")
    else:
        lines.append("- No event candidates with linked headlines in this cycle.")

    lines.append("")
    lines.append("### Watch Next")
    lines.append("- Monitor changes in top hashtags in the next polling cycle.")
    lines.append("- Track whether current event headlines persist or rotate.")
    lines.append("- Cross-check event spikes with additional regional feeds if available.")

    return "\n".join(lines)


def fallback_tags_from_rss(rss_payload: Dict[str, Any], max_tags: int) -> List[str]:
    tags: List[str] = []

    trend_entries = (
        rss_payload.get("google_trends_in", {})
        .get("data", {})
        .get("entries", [])
    )
    for entry in trend_entries:
        title = entry.get("title", "")
        hashtag = to_hashtag(title)
        if hashtag:
            tags.append(hashtag)

    if len(tags) < max_tags:
        news_entries = (
            rss_payload.get("google_news_top", {})
            .get("data", {})
            .get("entries", [])
        )
        for entry in news_entries:
            title = entry.get("title", "")
            hashtag = to_hashtag(title)
            if hashtag:
                tags.append(hashtag)

    deduped: List[str] = []
    seen = set()
    for value in tags:
        if value in seen:
            continue
        seen.add(value)
        deduped.append(value)
        if len(deduped) >= max_tags:
            break

    return deduped


def parse_rss_feed(url: str, limit: int = 20) -> Dict[str, Any]:
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) TrendsBot/1.0",
        "Accept": "application/rss+xml, application/xml, text/xml;q=0.9, */*;q=0.8",
    }
    response = httpx.get(url, headers=headers, timeout=30.0, follow_redirects=True)
    response.raise_for_status()

    feed = feedparser.parse(response.text)
    entries: List[Dict[str, str]] = []

    for item in feed.entries[:limit]:
        entries.append(
            {
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "published": item.get("published", item.get("updated", "")),
                "summary": re.sub(r"\s+", " ", item.get("summary", "")).strip(),
            }
        )

    return {
        "feed_title": feed.feed.get("title", ""),
        "feed_link": feed.feed.get("link", ""),
        "entries": entries,
    }


def collect_rss_sources(tags: List[str], max_tag_queries: int) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "google_trends_in": {"error": None, "data": None},
        "google_news_top": {"error": None, "data": None},
        "google_news_by_tag": {},
    }

    try:
        result["google_trends_in"]["data"] = parse_rss_feed("https://trends.google.com/trending/rss?geo=IN", limit=20)
    except Exception as exc:
        result["google_trends_in"]["error"] = str(exc)

    try:
        result["google_news_top"]["data"] = parse_rss_feed(
            "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en",
            limit=20,
        )
    except Exception as exc:
        result["google_news_top"]["error"] = str(exc)

    for tag in tags[:max_tag_queries]:
        query = tag.lstrip("#").strip()
        if not query:
            continue

        feed_url = (
            "https://news.google.com/rss/search?q="
            f"{quote_plus(query)}&hl=en-IN&gl=IN&ceid=IN:en"
        )

        try:
            data = parse_rss_feed(feed_url, limit=8)
            result["google_news_by_tag"][tag] = {"error": None, "data": data}
        except Exception as exc:
            result["google_news_by_tag"][tag] = {"error": str(exc), "data": None}

    return result


def gather_tags(trends_payload: Dict[str, Any], max_tags: int) -> List[str]:
    counter: Counter[str] = Counter()

    for block in trends_payload.get("blocks", []):
        for raw_tag in block.get("tags", []):
            normalized = normalize_tag(raw_tag)
            if normalized:
                counter[normalized] += 1

    for raw_tag in trends_payload.get("looseHashtags", []):
        normalized = normalize_tag(raw_tag)
        if normalized:
            counter[normalized] += 1

    return [item for item, _ in counter.most_common(max_tags)]


def create_event_candidates(tags: List[str], rss_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    candidates: List[Dict[str, Any]] = []

    for tag in tags:
        tag_feed = rss_payload.get("google_news_by_tag", {}).get(tag, {})
        feed_data = tag_feed.get("data") if isinstance(tag_feed, dict) else None
        if not feed_data:
            continue

        headlines = feed_data.get("entries", [])[:3]
        if not headlines:
            continue

        candidates.append(
            {
                "tag": tag,
                "headlines": [item.get("title", "") for item in headlines],
                "links": [item.get("link", "") for item in headlines],
            }
        )

    return candidates


def summarize_with_vllm(
    base_url: str,
    model_name: str,
    location: str,
    tags: List[str],
    events: List[Dict[str, Any]],
) -> Dict[str, Any]:
    endpoint = base_url.rstrip("/") + "/chat/completions"
    system_prompt = (
        "You are a real-time trend analyst. "
        "Summarize active social events from hashtags and headlines. "
        "Return compact markdown with sections: Overview, Active Events, Watch Next. "
        "Do not include chain-of-thought, hidden reasoning, analysis steps, or <think> tags. "
        "Return only final answer content."
    )

    user_payload = {
        "location": location,
        "hashtags": tags,
        "event_candidates": events,
        "generated_at_utc": utc_now(),
    }

    request_body = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": "Analyze this data and provide an event-focused update:\n"
                + json.dumps(user_payload, ensure_ascii=True),
            },
        ],
        "temperature": 0.2,
        "max_tokens": 700,
    }

    try:
        response = httpx.post(endpoint, json=request_body, timeout=120.0)
        response.raise_for_status()
        payload = response.json()

        content = ""
        choices = payload.get("choices", [])
        if choices:
            content = choices[0].get("message", {}).get("content", "")

        if isinstance(content, list):
            content = "\n".join(str(item) for item in content)

        sanitized_summary = sanitize_llm_summary(str(content))
        if not sanitized_summary:
            sanitized_summary = deterministic_summary(location, tags, events)

        return {
            "ok": True,
            "summary": sanitized_summary,
            "error": None,
            "raw": payload,
        }
    except Exception as exc:
        return {
            "ok": False,
            "summary": "",
            "error": str(exc),
            "raw": None,
        }


def trends_blocks_with_timestamps(trends_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    blocks: List[Dict[str, Any]] = []

    for block in trends_payload.get("blocks", []):
        tags = [normalize_tag(value) for value in block.get("tags", [])]
        cleaned_tags = [value for value in tags if value]

        blocks.append(
            {
                "title": (block.get("title") or "").strip(),
                "timestamp_raw": block.get("timestamp"),
                "timestamp_utc": parse_timestamp(block.get("timestamp")),
                "tags": cleaned_tags,
            }
        )

    return blocks


def render_markdown_report(snapshot: Dict[str, Any], llm_result: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# Live Trend Event Report")
    lines.append("")
    lines.append(f"Generated at (UTC): {snapshot.get('generated_at_utc', '')}")
    lines.append(f"Location: {snapshot.get('location', 'Unknown')}")
    lines.append("")

    lines.append("## Top Tags")
    top_tags = snapshot.get("top_tags", [])
    if top_tags:
        for value in top_tags:
            lines.append(f"- {value}")
    else:
        lines.append("- No tags captured")

    lines.append("")
    lines.append("## Trend Buckets")
    trend_blocks = snapshot.get("trend_blocks", [])
    if trend_blocks:
        for block in trend_blocks[:12]:
            title = block.get("title") or "Untitled bucket"
            timestamp = block.get("timestamp_utc") or block.get("timestamp_raw") or "n/a"
            lines.append(f"- {title} ({timestamp})")
            tags = block.get("tags", [])
            if tags:
                lines.append(f"  tags: {', '.join(tags[:10])}")
    else:
        lines.append("- No trend buckets captured")

    lines.append("")
    lines.append("## Event Candidates")
    events = snapshot.get("event_candidates", [])
    if events:
        for event in events[:10]:
            lines.append(f"- {event.get('tag', '')}")
            for title in event.get("headlines", [])[:3]:
                lines.append(f"  - {title}")
    else:
        lines.append("- No event candidates yet")

    lines.append("")
    lines.append("## LLM Summary")
    if llm_result.get("ok") and llm_result.get("summary"):
        lines.append(llm_result["summary"])
    elif llm_result.get("error"):
        lines.append(f"LLM call failed: {llm_result['error']}")
    else:
        lines.append("LLM summary is disabled")

    return "\n".join(lines) + "\n"


def run_once(args: argparse.Namespace) -> Dict[str, str]:
    trends_payload: Dict[str, Any] = {
        "location": "Unknown",
        "blocks": [],
        "looseHashtags": [],
        "title": "",
        "url": TRENDS24_URL,
    }
    trends_error: Optional[str] = None

    try:
        trends_payload = scrape_trends24(args.cdp_url, args.timeout_ms)
    except PlaywrightTimeoutError as exc:
        trends_error = f"Playwright timeout: {exc}"
    except Exception as exc:
        trends_error = str(exc)

    top_tags = gather_tags(trends_payload, args.max_tags)
    trend_blocks = trends_blocks_with_timestamps(trends_payload)

    rss_payload = collect_rss_sources(top_tags, args.max_tag_queries)
    if not top_tags:
        top_tags = fallback_tags_from_rss(rss_payload, args.max_tags)
        if top_tags:
            rss_payload = collect_rss_sources(top_tags, args.max_tag_queries)

    event_candidates = create_event_candidates(top_tags, rss_payload)

    llm_result = {
        "ok": False,
        "summary": "",
        "error": None,
        "raw": None,
    }
    if not args.disable_llm:
        llm_result = summarize_with_vllm(
            args.vllm_base_url,
            args.vllm_model,
            trends_payload.get("location") or "Unknown",
            top_tags,
            event_candidates,
        )

    snapshot = {
        "generated_at_utc": utc_now(),
        "source": {
            "trends24_url": trends_payload.get("url", TRENDS24_URL),
            "trends24_error": trends_error,
        },
        "page_title": trends_payload.get("title", ""),
        "location": trends_payload.get("location") or "Unknown",
        "top_tags": top_tags,
        "trend_blocks": trend_blocks,
        "event_candidates": event_candidates,
        "rss": rss_payload,
    }

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    snapshot_path = output_dir / "latest_snapshot.json"
    report_path = output_dir / "latest_report.md"

    snapshot_payload = {
        "snapshot": snapshot,
        "llm": {
            "ok": llm_result.get("ok"),
            "error": llm_result.get("error"),
            "summary": llm_result.get("summary"),
        },
    }
    snapshot_path.write_text(json.dumps(snapshot_payload, indent=2, ensure_ascii=True), encoding="utf-8")

    report = render_markdown_report(snapshot, llm_result)
    report_path.write_text(report, encoding="utf-8")

    print(f"[{utc_now()}] Snapshot written: {snapshot_path}")
    print(f"[{utc_now()}] Report written:   {report_path}")

    if trends_error:
        print(f"[{utc_now()}] Trends24 scrape warning: {trends_error}")

    if llm_result.get("ok"):
        print(f"[{utc_now()}] LLM summary created with model: {args.vllm_model}")
    elif not args.disable_llm:
        print(f"[{utc_now()}] LLM warning: {llm_result.get('error')}")

    return {
        "snapshot_path": str(snapshot_path),
        "report_path": str(report_path),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Live trend bot: scrape Trends24 with Playwright (Lightpanda), "
            "enrich with RSS feeds, and summarize with local vLLM."
        )
    )

    parser.add_argument(
        "--cdp-url",
        default=os.getenv("LIGHTPANDA_CDP_URL", "http://127.0.0.1:9222"),
        help="CDP endpoint exposed by Lightpanda browser",
    )
    parser.add_argument(
        "--vllm-base-url",
        default=os.getenv("VLLM_BASE_URL", "http://200.23:11642/v1"),
        help="OpenAI-compatible vLLM base URL",
    )
    parser.add_argument(
        "--vllm-model",
        default=os.getenv("VLLM_MODEL", "qwen36-35b"),
        help="Served model name exposed by vLLM",
    )

    parser.add_argument(
        "--output-dir",
        default="data",
        help="Directory where JSON and markdown outputs are written",
    )
    parser.add_argument(
        "--timeout-ms",
        type=int,
        default=60000,
        help="Playwright page timeout in milliseconds",
    )

    parser.add_argument(
        "--max-tags",
        type=int,
        default=20,
        help="Maximum number of top tags retained",
    )
    parser.add_argument(
        "--max-tag-queries",
        type=int,
        default=8,
        help="Maximum hashtag-specific Google News RSS queries",
    )

    parser.add_argument(
        "--run-once",
        action="store_true",
        help="Run a single collection cycle and exit",
    )
    parser.add_argument(
        "--interval-sec",
        type=int,
        default=int(os.getenv("POLL_INTERVAL_SEC", "300")),
        help="Polling interval when running continuously",
    )
    parser.add_argument(
        "--disable-llm",
        action="store_true",
        help="Skip vLLM summarization and only produce raw snapshot/report",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.run_once:
        run_once(args)
        return

    print(
        f"Starting trend bot loop. interval={args.interval_sec}s, cdp={args.cdp_url}, "
        f"vllm_model={args.vllm_model}"
    )

    while True:
        started = time.time()
        run_once(args)
        elapsed = time.time() - started
        sleep_for = max(args.interval_sec - int(elapsed), 1)
        print(f"[{utc_now()}] Sleeping for {sleep_for}s")
        time.sleep(sleep_for)


if __name__ == "__main__":
    main()
