"""
Background scheduler that fires the news reporter agent team on a fixed interval.
Replaces the bot.py polling loop. Started from server.py on boot.
"""
import threading
import logging
import os
import time

from .runtime import run_news_session

logger = logging.getLogger(__name__)

_INTERVAL = int(os.getenv("AGENT_RUN_INTERVAL_SEC", "300"))
_DEFAULT_TOPIC = os.getenv("AGENT_DEFAULT_TOPIC", "today's top trending news India worldwide")

_lock = threading.Lock()
_state = {
    "running": False,
    "last_run_id": None,
    "last_run_at": None,
    "last_success": None,
    "error": None,
}


def get_state() -> dict:
    with _lock:
        return dict(_state)


def _run_once():
    with _lock:
        _state["running"] = True
        _state["error"] = None

    try:
        result = run_news_session(_DEFAULT_TOPIC)
        with _lock:
            _state["last_run_id"] = result.get("run_id")
            _state["last_run_at"] = result.get("started_at")
            _state["last_success"] = result.get("success", False)
    except Exception as exc:
        logger.exception("Scheduled news run failed: %s", exc)
        with _lock:
            _state["error"] = str(exc)
            _state["last_success"] = False
    finally:
        with _lock:
            _state["running"] = False


def _loop():
    while True:
        try:
            _run_once()
        except Exception as exc:
            logger.exception("Scheduler loop error: %s", exc)
        time.sleep(_INTERVAL)


def start(daemon: bool = True) -> threading.Thread:
    t = threading.Thread(target=_loop, name="agent-scheduler", daemon=daemon)
    t.start()
    logger.info("Agent scheduler started (interval=%ss, topic=%r)", _INTERVAL, _DEFAULT_TOPIC)
    return t
