from flask import Flask, send_from_directory, jsonify, abort, Response, request
from flask_cors import CORS
import os, json, re, sys, asyncio, time
from datetime import datetime, timezone
from pathlib import Path
from typing import List

try:
    import httpx
    from bs4 import BeautifulSoup
    SCRAPE_OK = True
except ImportError:
    SCRAPE_OK = False

# ── X_fetch integration (includes poc_feeds fetcher as a tool) ─────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'X_fetch'))
try:
    from tools.feeds_fetch_tool.fetcher import fetch_all as _feeds_fetch_all
    FEEDS_OK = True
except ImportError:
    FEEDS_OK = False

try:
    from tools.discovery_tool.advanced_discovery import AdvancedDiscoveryAgent
    from tools.discovery_tool.rss_ingestion import RSSIngestion
    from tools.deduplication_tool.deduplication_agent import DeduplicationAgent
    from tools.url_prioritization_tool.prioritization_agent import URLPrioritizationAgent
    XFETCH_OK = True
    _xfetch_status = {'last_run': None, 'last_count': 0, 'searxng_url': os.getenv('SEARXNG_URL', 'http://localhost:8888')}
except ImportError as _e:
    XFETCH_OK = False
    _xfetch_status = {'last_run': None, 'last_count': 0, 'searxng_url': None, 'error': str(_e)}

ROOT     = os.path.dirname(__file__)
DATA_DIR = os.path.join(ROOT, 'data')
UI_DIR   = os.path.join(ROOT, 'ui_react', 'dist')

app = Flask(__name__, static_folder=UI_DIR, template_folder=UI_DIR)
CORS(app)

# ── static UI ────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory(UI_DIR, 'index.html')

@app.route('/assets/<path:fn>')
def static_files(fn):
    return send_from_directory(os.path.join(UI_DIR, 'assets'), fn)

# ── data endpoints ───────────────────────────────────────────────────────────

@app.route('/api/snapshot')
def api_snapshot():
    p = os.path.join(DATA_DIR, 'latest_snapshot.json')
    if not os.path.exists(p):
        abort(404)
    with open(p, 'r', encoding='utf-8') as f:
        return Response(f.read(), mimetype='application/json')

@app.route('/api/report')
def api_report():
    p = os.path.join(DATA_DIR, 'latest_report.md')
    if not os.path.exists(p):
        abort(404)
    with open(p, 'r', encoding='utf-8') as f:
        return Response(f.read(), mimetype='text/plain')

# ── tag parsing helpers ──────────────────────────────────────────────────────
def parse_hashtags(raw: str) -> List[str]:
    """
    Parse hashtags from raw input while preserving multi-word hashtags.

    Examples:
        "#congratulations rcb" → ["#congratulations rcb"]
        "#congratulations rcb, #ipl final" → ["#congratulations rcb", "#ipl final"]
        "#AI, #Modi" → ["#AI", "#Modi"]
    """
    if not raw:
        return []

    raw = raw.strip()
    if not raw:
        return []

    hashtags = []
    current = ""
    in_hashtag = False
    i = 0

    while i < len(raw):
        char = raw[i]

        if char == '#':
            # Start of a new hashtag
            if current.strip():
                hashtags.append(current.strip())
            current = "#"
            in_hashtag = True
        elif char == ',':
            # Comma ends current item
            if current.strip():
                hashtags.append(current.strip())
            current = ""
            in_hashtag = False
        elif char in ' \t\n\r':
            # Whitespace
            if in_hashtag:
                # Inside a hashtag, preserve space
                current += char
            elif current.strip():
                # End of a non-hashtag item
                hashtags.append(current.strip())
                current = ""
                in_hashtag = False
            # else: skip extra whitespace
        else:
            current += char

        i += 1

    # Add any remaining text (only if not just a lone #)
    if current.strip():
        hashtags.append(current.strip())

    # Normalize: ensure all items that don't start with # get # prefix
    # and strip whitespace from multi-word hashtags
    result = []
    for h in hashtags:
        h = re.sub(r'\s+', ' ', h).strip()  # Normalize whitespace
        if not h:
            continue
        if h.startswith('#'):
            # Only add if there's content after #
            if len(h) > 1:
                result.append(h)
        else:
            result.append(f'#{h}')

    return result


# ── on-demand location scrape ─────────────────────────────────────────────────

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) TrendsBot/1.0',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'en-US,en;q=0.9',
}

def parse_timestamp(raw):
    if not raw:
        return None
    try:
        v = float(raw)
        if v > 1e12:
            v /= 1000.0
        return datetime.fromtimestamp(v, tz=timezone.utc).isoformat()
    except Exception:
        return None

def scrape_trends24(country: str, city: str):
    slug = f"{country.lower().replace(' ', '-')}/{city.lower().replace(' ', '-')}/" if city else f"{country.lower().replace(' ', '-')}/"
    url = f"https://trends24.in/{slug}"

    resp = httpx.get(url, headers=HEADERS, timeout=20, follow_redirects=True)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, 'html.parser')

    page_title = soup.find('title')
    page_title = page_title.text.strip() if page_title else ''

    h1 = soup.find('h1')
    location_name = h1.text.strip() if h1 else f"{city or country}".title()

    trend_blocks = []
    all_tags = []

    for h3 in soup.find_all('h3'):
        ts_raw = h3.get('data-timestamp') or h3.get('data-time') or None
        title  = h3.get_text(strip=True)

        ol = h3.find_next_sibling('ol')
        if not ol:
            continue

        tags = []
        for li in ol.find_all('li', recursive=False):
            a = li.find('a')
            name = (a.get_text(strip=True) if a else li.get_text(strip=True)).strip()
            name = re.sub(r'^\d+[\.\)\-:\s]+', '', name).strip()
            if name and len(name) <= 96:
                tags.append(name)

        if not tags:
            continue

        ts_iso = parse_timestamp(ts_raw)
        trend_blocks.append({
            'title': title,
            'timestamp_raw': ts_raw,
            'timestamp_utc': ts_iso,
            'tags': tags,
        })
        all_tags.extend(tags)

    from collections import Counter
    top_tags = [t for t, _ in Counter(all_tags).most_common(30)]

    snapshot = {
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'source': {
            'trends24_url': url,
            'trends24_error': None,
        },
        'page_title': page_title,
        'location': location_name,
        'top_tags': top_tags,
        'trend_blocks': trend_blocks,
        'event_candidates': [],
        'rss': {},
    }
    return {'snapshot': snapshot}


@app.route('/api/fetch')
def api_fetch():
    if not SCRAPE_OK:
        return jsonify({'error': 'httpx/bs4 not installed'}), 500

    country = request.args.get('country', 'worldwide').strip()
    city    = request.args.get('city', '').strip()

    try:
        data = scrape_trends24(country, city)
        return jsonify(data)
    except httpx.HTTPStatusError as e:
        return jsonify({'error': f'HTTP {e.response.status_code} from trends24'}), 502
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/feeds')
def api_feeds():
    if not FEEDS_OK:
        return jsonify({'error': 'poc_feeds/fetcher.py not available'}), 500

    raw = request.args.get('tags', '').strip()
    if not raw:
        return jsonify({'error': 'tags param is required'}), 400

    hashtags = parse_hashtags(raw)
    if not hashtags:
        return jsonify({'error': 'no valid hashtags parsed'}), 400

    limit = min(int(request.args.get('limit', 8)), 20)

    try:
        data = _feeds_fetch_all(hashtags=hashtags, google_limit=limit, tweet_limit=limit, delay_sec=0.3)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ── X_fetch discovery endpoint ────────────────────────────────────────────────

_STATUS_URL_PATTERN = re.compile(r'(twitter\.com|x\.com)/[^/]+/status/\d+')
_JUNK_URLS = re.compile(
    r'^https?://(search\.twitter\.com|x\.com/?$|x\.com/explore|x\.com/home|'
    r'about\.x\.com|help\.x\.com|x\.company|mobile\.twitter\.com/?$)'
)

def _is_status_url(url: str) -> bool:
    if _JUNK_URLS.match(url):
        return False
    return bool(_STATUS_URL_PATTERN.search(url))

async def _run_discovery(keywords: list, limit: int) -> dict:
    discovery = AdvancedDiscoveryAgent()
    rss = RSSIngestion()
    dedup = DeduplicationAgent()
    prioritizer = URLPrioritizationAgent()

    for kw in keywords:
        prioritizer.high_value_keywords.append(kw.lower())

    all_found = []

    queries_per_kw = [
        'site:twitter.com "#{kw}"',
        'site:x.com "#{kw}"',
        'site:twitter.com #{kw}',
        'site:x.com #{kw}',
        '"{kw}" site:twitter.com',
        '"{kw}" site:x.com',
    ]

    for kw in keywords:
        # SearXNG patterns
        for pattern in queries_per_kw:
            query = pattern.replace('{kw}', kw)
            found = await discovery.search_searxng(query)
            all_found.extend(found)

        # RSS
        rss_found = await rss.fetch_rss(kw)
        all_found.extend(rss_found)

    # Dedup
    unique = [t for t in all_found if not dedup.is_duplicate(t.tweet_url)]

    # Filter to status URLs only
    status_only = [t for t in unique if _is_status_url(t.tweet_url)]

    # Prioritize
    prioritized = prioritizer.process_discovered_tweets(status_only)

    # Cap at limit
    prioritized = prioritized[:limit]

    # Count by source
    src_counts = {}
    for t in prioritized:
        src = t.discovered_from
        src_counts[src] = src_counts.get(src, 0) + 1

    return {
        'keywords': keywords,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'total': len(prioritized),
        'raw_discovered': len(all_found),
        'after_dedup': len(unique),
        'sources': src_counts,
        'urls': [
            {
                'url': t.tweet_url,
                'discovered_from': t.discovered_from,
                'query': t.query,
                'score': round(prioritizer.calculate_priority(t), 2),
                'discovered_at': t.timestamp.isoformat(),
            }
            for t in prioritized
        ]
    }


@app.route('/api/discover')
def api_discover():
    if not XFETCH_OK:
        return jsonify({'error': 'X_fetch agents not available', 'detail': _xfetch_status.get('error', '')}), 500

    raw = request.args.get('keywords', '').strip()
    if not raw:
        return jsonify({'error': 'keywords param is required'}), 400

    # Parse hashtags to preserve multi-word phrases
    parsed_hashtags = parse_hashtags(raw)
    
    # Convert to keywords for discovery (strip # prefix and normalize)
    keywords = [h.lstrip('#').strip() for h in parsed_hashtags if h]
    if not keywords:
        return jsonify({'error': 'no valid keywords parsed'}), 400

    limit = min(int(request.args.get('limit', 50)), 200)

    t0 = time.time()
    try:
        result = asyncio.run(_run_discovery(keywords, limit))
        result['elapsed_sec'] = round(time.time() - t0, 2)

        # Update global status
        _xfetch_status['last_run'] = datetime.now(timezone.utc).isoformat()
        _xfetch_status['last_count'] = result['total']
        _xfetch_status['last_keywords'] = keywords

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/xfetch/status')
def api_xfetch_status():
    return jsonify({
        'available': XFETCH_OK,
        'searxng_url': _xfetch_status.get('searxng_url'),
        'last_run': _xfetch_status.get('last_run'),
        'last_count': _xfetch_status.get('last_count', 0),
        'last_keywords': _xfetch_status.get('last_keywords', []),
    })


# ── Agent runtime integration ─────────────────────────────────────────────────

try:
    from agent_runtime.runtime import run_news_session
    from agent_runtime import scheduler as _scheduler
    AGENT_OK = True
except ImportError as _agent_err:
    AGENT_OK = False
    _agent_err_msg = str(_agent_err)

_agent_runs: dict = {}   # run_id -> {status, result, thread}


def _execute_run(run_id: str, topic: str):
    _agent_runs[run_id]['status'] = 'running'
    try:
        result = run_news_session(topic, run_id=run_id)
        _agent_runs[run_id]['status'] = 'done'
        _agent_runs[run_id]['result'] = result
    except Exception as exc:
        _agent_runs[run_id]['status'] = 'error'
        _agent_runs[run_id]['error'] = str(exc)


@app.route('/api/agent/run', methods=['POST'])
def api_agent_run():
    if not AGENT_OK:
        return jsonify({'error': 'agent_runtime not available', 'detail': _agent_err_msg}), 500
    body = request.get_json(silent=True) or {}
    topic = (body.get('topic') or '').strip()
    if not topic:
        topic = 'today\'s top trending news'
    run_id = str(time.time_ns())[:12]
    _agent_runs[run_id] = {'status': 'queued', 'result': None, 'error': None, 'topic': topic}
    import threading
    t = threading.Thread(target=_execute_run, args=(run_id, topic), daemon=True)
    _agent_runs[run_id]['thread'] = t
    t.start()
    return jsonify({'run_id': run_id, 'topic': topic, 'status': 'queued'})


@app.route('/api/agent/status/<run_id>')
def api_agent_status(run_id):
    run = _agent_runs.get(run_id)
    if not run:
        abort(404)
    result = run.get('result') or {}
    return jsonify({
        'run_id': run_id,
        'status': run['status'],
        'topic': run.get('topic'),
        'rounds': result.get('rounds'),
        'success': result.get('success'),
        'history_count': len(result.get('history', [])),
        'error': run.get('error'),
    })


@app.route('/api/agent/result/<run_id>')
def api_agent_result(run_id):
    run = _agent_runs.get(run_id)
    if not run:
        abort(404)
    if run['status'] != 'done':
        return jsonify({'run_id': run_id, 'status': run['status'], 'ready': False})
    result = run['result'] or {}
    html = result.get('final_answer', '')
    return jsonify({
        'run_id': run_id,
        'status': 'done',
        'ready': True,
        'has_html': bool(html and html.strip().startswith('<!')),
        'html': html,
        'run_dir': result.get('run_dir'),
        'rounds': result.get('rounds'),
    })


@app.route('/api/dashboard/latest')
def api_dashboard_latest():
    p = os.path.join(DATA_DIR, 'latest_dashboard.html')
    if not os.path.exists(p):
        return Response('<p style="color:#666;font-family:sans-serif">No dashboard generated yet. Click <b>Generate Report</b>.</p>', mimetype='text/html')
    with open(p, 'r', encoding='utf-8') as f:
        return Response(f.read(), mimetype='text/html')


@app.route('/api/runs')
def api_runs_list():
    runs_dir = os.path.join(DATA_DIR, 'runs')
    if not os.path.exists(runs_dir):
        return jsonify([])
    runs = []
    for run_id in sorted(os.listdir(runs_dir), reverse=True):
        meta_path = os.path.join(runs_dir, run_id, 'meta.json')
        html_path = os.path.join(runs_dir, run_id, 'report.html')
        if not os.path.exists(meta_path):
            continue
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        runs.append({
            'run_id': run_id,
            'topic': meta.get('topic', run_id),
            'completed_at': meta.get('completed_at'),
            'started_at': meta.get('started_at'),
            'success': meta.get('success', False),
            'has_html': os.path.exists(html_path),
            'rounds': meta.get('rounds', 0),
        })
    return jsonify(runs)


@app.route('/api/runs/<run_id>/html')
def api_run_html(run_id):
    p = os.path.join(DATA_DIR, 'runs', run_id, 'report.html')
    if not os.path.exists(p):
        abort(404)
    with open(p, 'r', encoding='utf-8') as f:
        return Response(f.read(), mimetype='text/html')


@app.route('/api/runs/<run_id>/history')
def api_run_history(run_id):
    p = os.path.join(DATA_DIR, 'runs', run_id, 'history.json')
    if not os.path.exists(p):
        abort(404)
    with open(p, 'r', encoding='utf-8') as f:
        return Response(f.read(), mimetype='application/json')


@app.route('/api/agent/scheduler')
def api_scheduler_status():
    if not AGENT_OK:
        return jsonify({'available': False})
    return jsonify({'available': True, 'scheduler': _scheduler.get_state()})


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    if AGENT_OK and os.getenv('AGENT_SCHEDULER', 'true').lower() not in ('0', 'false', 'no'):
        _scheduler.start()
    app.run(host='0.0.0.0', port=port, debug=False)
