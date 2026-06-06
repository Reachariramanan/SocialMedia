"""
Sync wrapper: extract tweet content from X/Twitter URLs via Tor + Lightpanda.
Normalises raw scrape.js DOM output and returns a compact YAML block string
so agents get dense, readable tweet content without JSON verbosity.

Token budget: ~80 tokens per tweet (YAML ~40% denser than equivalent JSON).
Max tweets per URL: MAX_TWEETS_PER_URL (default 5 — top by engagement).
"""
import sys, os, asyncio, re, time
from typing import List, Dict, Any

_XFETCH = os.path.join(os.path.dirname(__file__), '..', '..', 'X_fetch')
sys.path.insert(0, _XFETCH)

try:
    from tools.extraction_tool.torpanda_extractor import extract_from_urls
    _EXTRACT_OK = True
except ImportError as e:
    _EXTRACT_OK = False
    _EXTRACT_ERR = str(e)

# ---------------------------------------------------------------------------
# Normalisation helpers
# ---------------------------------------------------------------------------

_TAG_RE = re.compile(r'<[^>]+>')
_WS_RE  = re.compile(r'\s+')

MAX_TWEET_TEXT     = int(os.getenv('TWEET_MAX_CHARS',   '320'))
MAX_TWEETS_PER_URL = int(os.getenv('TWEET_MAX_PER_URL', '10'))


def _strip_html(raw: str) -> str:
    text = _TAG_RE.sub(' ', raw or '')
    return _WS_RE.sub(' ', text).strip()


def _normalise_tweet(raw: Dict[str, Any], source_url: str) -> Dict[str, Any]:
    """
    Map a single scrape.js tweet dict to a flat, minimal schema.

    scrape.js fields (from scrapePostsFromPage):
      text / html        — tweet body
      author / username  — display name / @handle
      time / timestamp   — ISO or human-readable
      likes / retweets / replies / views  — engagement counts
      url                — permalink (may be absent)
    """
    # Prefer plain text; fall back to stripping HTML
    text = raw.get('text') or _strip_html(raw.get('html', ''))
    text = _WS_RE.sub(' ', text).strip()[:MAX_TWEET_TEXT]

    return {
        'url':       raw.get('url') or raw.get('permalink') or source_url,
        'author':    raw.get('author') or raw.get('name') or '',
        'handle':    raw.get('username') or raw.get('screen_name') or '',
        'text':      text,
        'time':      raw.get('time') or raw.get('timestamp') or '',
        'likes':     _int(raw.get('likes') or raw.get('favorite_count')),
        'retweets':  _int(raw.get('retweets') or raw.get('retweet_count')),
        'replies':   _int(raw.get('replies') or raw.get('reply_count')),
        'views':     _int(raw.get('views') or raw.get('view_count')),
    }


def _int(v) -> int:
    if v is None:
        return 0
    try:
        return int(str(v).replace(',', '').replace('.', '').strip())
    except (ValueError, TypeError):
        return 0


def _eng(t: Dict[str, Any]) -> int:
    """Engagement score for ranking."""
    return _int(t.get('likes')) + _int(t.get('retweets')) * 2


def _fmt_count(n: int) -> str:
    """Compact count: 1200 → 1.2k, 0 → omitted (caller decides)."""
    if n >= 1000:
        return f'{n/1000:.1f}k'
    return str(n)


def _tweet_to_yaml_lines(t: Dict[str, Any], source_url: str) -> List[str]:
    """Render one normalised tweet as compact YAML lines (no leading dash)."""
    text   = (t.get('text') or _strip_html(t.get('html', '')))
    text   = _WS_RE.sub(' ', text).strip()[:MAX_TWEET_TEXT]
    handle = t.get('username') or t.get('screen_name') or ''
    author = t.get('author') or t.get('name') or handle
    when   = t.get('time') or t.get('timestamp') or ''
    url    = t.get('url') or t.get('permalink') or source_url

    likes    = _int(t.get('likes')    or t.get('favorite_count'))
    rts      = _int(t.get('retweets') or t.get('retweet_count'))
    replies  = _int(t.get('replies')  or t.get('reply_count'))
    views    = _int(t.get('views')    or t.get('view_count'))

    # Engagement summary — only include non-zero fields to save tokens
    eng_parts = []
    if likes:    eng_parts.append(f'❤{_fmt_count(likes)}')
    if rts:      eng_parts.append(f'🔁{_fmt_count(rts)}')
    if replies:  eng_parts.append(f'💬{_fmt_count(replies)}')
    if views:    eng_parts.append(f'👁{_fmt_count(views)}')
    eng_str = ' '.join(eng_parts) if eng_parts else 'no engagement'

    lines = [
        f'    url: {url}',
        f'    by: {author}{"  (@" + handle + ")" if handle and handle != author else ""}',
    ]
    if when:
        lines.append(f'    at: {when}')
    lines.append(f'    eng: {eng_str}')
    lines.append(f'    text: |')
    for line in (text or '(empty)').splitlines() or ['(empty)']:
        lines.append(f'      {line}')
    return lines


def _extraction_to_yaml(raw_result: Dict[str, Any]) -> str:
    """Render one extract_from_urls() result as a compact YAML block string."""
    url    = raw_result.get('url', '')
    status = raw_result.get('status', 'unknown')
    raw_tweets: List[Dict] = raw_result.get('tweets') or []

    if status not in ('success', 'no_tweets') or not raw_tweets:
        err = raw_result.get('error') or raw_result.get('http_status') or status
        return f'- ERR {url}  # {err}'

    top = sorted(raw_tweets, key=_eng, reverse=True)[:MAX_TWEETS_PER_URL]

    lines = [f'- src: {url}']
    lines.append(f'  tweets: # {len(top)} of {len(raw_tweets)}')
    for i, t in enumerate(top):
        lines.append(f'  - # tweet {i+1}')
        lines.extend(_tweet_to_yaml_lines(t, url))

    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# Public run() — called by Yukta tool registry
# ---------------------------------------------------------------------------

def run(urls: str, use_tor: bool = True, limit: int = 20) -> dict:
    """
    Extract tweet content from X/Twitter URLs and return compact YAML.

    Args:
        urls:    Comma-separated or newline-separated X/Twitter status URLs.
        use_tor: Route through Tor+Lightpanda (default True).
        limit:   Max URLs to extract (default 20; hard cap = 50).

    Returns dict with:
        ok          — bool
        tweets_yaml — compact YAML string (use this as agent context)
        total       — URLs processed
        success     — URLs with ≥1 tweet extracted
        elapsed_sec
    """
    if not _EXTRACT_OK:
        return {'ok': False, 'error': f'Extractor not available: {_EXTRACT_ERR}', 'tweets_yaml': ''}

    raw_urls = [u.strip() for u in re.split(r'[,\n]+', urls or '') if u.strip()]
    raw_urls = [u for u in raw_urls if re.search(r'(x\.com|twitter\.com)/\w+/status/\d+', u, re.I)]
    limit    = min(int(limit), 50)
    raw_urls = raw_urls[:limit]

    if not raw_urls:
        return {'ok': False, 'error': 'No valid X/Twitter status URLs provided', 'tweets_yaml': ''}

    t0 = time.time()
    try:
        raw_results: List[Dict] = asyncio.run(extract_from_urls(raw_urls, use_tor=use_tor))
    except Exception as exc:
        return {'ok': False, 'error': str(exc), 'tweets_yaml': ''}

    blocks    = [_extraction_to_yaml(r) for r in raw_results]
    yaml_out  = '\n'.join(blocks)
    n_success = sum(1 for r in raw_results if r.get('tweets'))

    return {
        'ok':          True,
        'tweets_yaml': yaml_out,
        'total':       len(raw_results),
        'success':     n_success,
        'elapsed_sec': round(time.time() - t0, 2),
    }
