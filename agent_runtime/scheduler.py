"""
Background scheduler that fires the news reporter agent team for user-defined
schedules (recurring and one-time). Schedules persist to data/schedules.json so
they survive page refreshes and server restarts. Started from server.py on boot.
"""
import threading
import logging
import os
import json
import time
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path

from .runtime import run_news_session

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
STORE_PATH = DATA_DIR / "schedules.json"

# How often the runner loop wakes up to check for due schedules.
_TICK_SEC = int(os.getenv("AGENT_SCHEDULER_TICK_SEC", "30"))

# Optional seeded default (replaces the old hidden fixed-interval loop). When the
# store is empty on first start, seed a single visible, deletable recurring
# schedule from these env vars so behaviour is discoverable instead of magic.
_SEED_INTERVAL = int(os.getenv("AGENT_RUN_INTERVAL_SEC", "0"))
_SEED_TOPIC = os.getenv("AGENT_DEFAULT_TOPIC", "today's top trending news India worldwide")

_lock = threading.RLock()

# Back-compat status fields (consumed by /api/agent/scheduler + SystemPulse) plus
# the live schedule list.
_state = {
    "running": False,
    "running_run_id": None,
    "last_run_id": None,
    "last_run_at": None,
    "last_success": None,
    "error": None,
}

_schedules: list[dict] = []
_loaded = False
_started = False


# ── helpers ────────────────────────────────────────────────────────────────

def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.isoformat()


def _parse_iso(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None


def _new_id() -> str:
    return str(time.time_ns())[:12]


def _persist() -> None:
    """Write the schedule list to disk. Caller must hold _lock."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp = STORE_PATH.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(_schedules, indent=2), encoding="utf-8")
    tmp.replace(STORE_PATH)


def _load() -> None:
    """Load schedules from disk into memory. Caller must hold _lock."""
    global _schedules, _loaded
    if STORE_PATH.exists():
        try:
            _schedules = json.loads(STORE_PATH.read_text(encoding="utf-8"))
            if not isinstance(_schedules, list):
                _schedules = []
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Could not read schedules.json (%s); starting empty", exc)
            _schedules = []
    else:
        _schedules = []
    _loaded = True


def _ensure_loaded() -> None:
    """Lazy-load schedules from disk on first access.

    Decouples reading persisted schedules from starting the runner thread, so the
    REST API returns the right data even when AGENT_SCHEDULER is disabled or the
    runner hasn't started yet. Caller must hold _lock.
    """
    if not _loaded:
        _load()


def _compute_next(sched: dict, *, base: datetime | None = None) -> str | None:
    """Compute next_run_at for a schedule. Returns ISO string or None (once, done)."""
    base = base or _now()
    if sched["type"] == "once":
        return sched.get("run_at")
    # recurring: roll forward past `base` to avoid catch-up bursts after downtime
    interval = max(int(sched.get("interval_sec") or 0), 1)
    nxt = _parse_iso(sched.get("next_run_at")) or base
    while nxt <= base:
        nxt = nxt + timedelta(seconds=interval)
    return _iso(nxt)


# ── public API (lock-guarded) ───────────────────────────────────────────────

def get_state() -> dict:
    with _lock:
        _ensure_loaded()
        s = dict(_state)
        s["schedules"] = [dict(x) for x in _schedules]
        s["count"] = len(_schedules)
        return s


def list_schedules() -> list[dict]:
    with _lock:
        _ensure_loaded()
        return [dict(x) for x in _schedules]


def add_schedule(
    topic: str,
    type: str,
    interval_sec: int | None = None,
    run_at: str | None = None,
) -> dict:
    """Validate and persist a new schedule. Raises ValueError on bad input."""
    topic = (topic or "").strip()
    if not topic:
        raise ValueError("topic is required")
    if type not in ("recurring", "once"):
        raise ValueError("type must be 'recurring' or 'once'")

    now = _now()
    if type == "recurring":
        interval_sec = int(interval_sec or 0)
        if interval_sec <= 0:
            raise ValueError("interval_sec must be a positive integer for recurring schedules")
        run_at = None
        next_run_at = _iso(now + timedelta(seconds=interval_sec))
    else:  # once
        when = _parse_iso(run_at)
        if when is None:
            raise ValueError("run_at must be a valid ISO-8601 datetime for one-time schedules")
        if when <= now:
            raise ValueError("run_at must be in the future")
        interval_sec = None
        run_at = _iso(when)
        next_run_at = run_at

    sched = {
        "id": _new_id(),
        "topic": topic,
        "type": type,
        "interval_sec": interval_sec,
        "run_at": run_at,
        "enabled": True,
        "created_at": _iso(now),
        "last_run_at": None,
        "last_run_id": None,
        "next_run_at": next_run_at,
    }
    with _lock:
        _ensure_loaded()
        _schedules.append(sched)
        try:
            _persist()
        except OSError:
            # Don't leak an in-memory schedule that never made it to disk —
            # it would silently vanish on the next restart.
            _schedules.pop()
            raise
        return dict(sched)


def delete_schedule(schedule_id: str) -> bool:
    with _lock:
        _ensure_loaded()
        kept = [s for s in _schedules if s.get("id") != schedule_id]
        if len(kept) == len(_schedules):
            return False
        removed = list(_schedules)
        _schedules[:] = kept
        try:
            _persist()
        except OSError:
            _schedules[:] = removed
            raise
        return True


# ── runner ───────────────────────────────────────────────────────────────────

def _fire(sched: dict) -> None:
    """Run a schedule's news session in a daemon thread; record results."""
    topic = sched["topic"]
    sched_id = sched["id"]
    run_id = str(uuid.uuid4())[:8]

    def _job():
        with _lock:
            _state["running"] = True
            _state["running_run_id"] = run_id
            _state["error"] = None
            for s in _schedules:
                if s.get("id") == sched_id:
                    s["running_run_id"] = run_id
                    break
            _persist()
        try:
            result = run_news_session(topic, run_id=run_id)
            success = result.get("success", False)
            with _lock:
                _state["last_run_id"] = run_id
                _state["last_run_at"] = result.get("started_at")
                _state["last_success"] = success
                for s in _schedules:
                    if s.get("id") == sched_id:
                        s["last_run_id"] = run_id
                        s["last_run_at"] = _iso(_now())
                        break
                _persist()
        except Exception as exc:
            logger.exception("Scheduled news run failed (schedule=%s): %s", sched_id, exc)
            with _lock:
                _state["error"] = str(exc)
                _state["last_success"] = False
        finally:
            with _lock:
                _state["running"] = False
                _state["running_run_id"] = None
                for s in _schedules:
                    if s.get("id") == sched_id:
                        s["running_run_id"] = None
                        break
                _persist()

    threading.Thread(target=_job, name=f"sched-{sched_id}", daemon=True).start()


def _tick() -> None:
    """Check every schedule once; fire any that are due and advance them."""
    now = _now()
    due: list[dict] = []
    with _lock:
        changed = False
        for s in _schedules:
            if not s.get("enabled"):
                continue
            nxt = _parse_iso(s.get("next_run_at"))
            if nxt is None or nxt > now:
                continue
            due.append(dict(s))
            if s["type"] == "once":
                s["enabled"] = False
                s["next_run_at"] = None
            else:
                s["next_run_at"] = _compute_next(s, base=now)
            changed = True
        if changed:
            _persist()
    for s in due:
        logger.info("Firing schedule id=%s topic=%r type=%s", s["id"], s["topic"], s["type"])
        _fire(s)


def _loop() -> None:
    while True:
        try:
            _tick()
        except Exception as exc:
            logger.exception("Scheduler loop error: %s", exc)
        time.sleep(_TICK_SEC)


def _maybe_seed() -> None:
    """Seed a default recurring schedule if store is empty and seed interval set."""
    if _schedules:
        return
    if _SEED_INTERVAL <= 0:
        return
    try:
        add_schedule(_SEED_TOPIC, "recurring", interval_sec=_SEED_INTERVAL)
        logger.info("Seeded default recurring schedule (interval=%ss)", _SEED_INTERVAL)
    except ValueError as exc:
        logger.warning("Could not seed default schedule: %s", exc)


def start(daemon: bool = True) -> threading.Thread:
    global _started
    with _lock:
        _load()
        _maybe_seed()
        _started = True
    t = threading.Thread(target=_loop, name="agent-scheduler", daemon=daemon)
    t.start()
    logger.info(
        "Agent scheduler started (tick=%ss, %d schedule(s))",
        _TICK_SEC, len(_schedules),
    )
    return t
