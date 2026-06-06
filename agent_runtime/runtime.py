"""
Build and run the News Reporter LeaderCoordinator session.

Usage:
    from agent_runtime.runtime import run_news_session
    result = run_news_session("today's top India news")
"""
import os
import json
import uuid
import logging
import pathlib
import tempfile
from datetime import datetime, timezone
from typing import Any

from yukta.api.models import (
    AgentData, AgentLevel, SkillData, TeamData, TeamStructure, SystemConfig,
)
from yukta.api.coordinator import LeaderCoordinator

from .llm import make_llm_client
from .tools_registry import AGENT_TOOLS

logger = logging.getLogger(__name__)

ROOT = pathlib.Path(__file__).parent.parent
SKILLS_DIR = ROOT / "ecosystem" / "skills"
_DATA_RUNS_DIR = ROOT / "data" / "runs"

# Use /data/runs if writable; fallback to temp directory
def _get_runs_dir() -> pathlib.Path:
    try:
        _DATA_RUNS_DIR.mkdir(parents=True, exist_ok=True)
        (_DATA_RUNS_DIR / ".writable_test").touch()
        (_DATA_RUNS_DIR / ".writable_test").unlink()
        return _DATA_RUNS_DIR
    except (PermissionError, OSError):
        return pathlib.Path(tempfile.gettempdir()) / "socialmedia_runs"

RUNS_DIR = _get_runs_dir()


def _load_skill(skill_id: str) -> SkillData:
    skill_path = SKILLS_DIR / skill_id / "SKILL.md"
    raw = skill_path.read_text(encoding="utf-8")

    # Parse YAML frontmatter
    name, description, version, category = skill_id, skill_id, "1.0.0", "process"
    content = raw
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) >= 3:
            import yaml
            try:
                fm = yaml.safe_load(parts[1])
                name = fm.get("name", skill_id)
                description = fm.get("description", skill_id)[:150]
                version = fm.get("version", "1.0.0")
                category = fm.get("category", "process")
            except Exception:
                pass
            content = parts[2].strip()

    return SkillData(
        skill_id=skill_id,
        name=name,
        description=description,
        version=version,
        category=category,
        content=content,
        file_path=str(skill_path),
    )


_VALID_REPORT_SKILLS = {
    "html_report_writer",
    "bulletin_board",
    "uncle_prompt",
    "intelligent_guy",
    "smallboy",
    "smallboywithbrains",
}


def _build_ecosystem(started_at: str = "", report_skill: str = "html_report_writer") -> dict[str, Any]:
    if report_skill not in _VALID_REPORT_SKILLS:
        report_skill = "html_report_writer"

    skill_map = {
        "master": ["action_planning"],
        "action_planner": ["action_planning"],
        "researcher": ["trend_research", "bulletin_board"],
        "dashboard_layout_builder": ["dashboarder"],
        "report_writer": [report_skill],
    }

    level_map = {
        "master": AgentLevel.LEAD,
        "action_planner": AgentLevel.SENIOR,
        "researcher": AgentLevel.SENIOR,
        "dashboard_layout_builder": AgentLevel.SENIOR,
        "report_writer": AgentLevel.SENIOR,
    }

    _NO_THINK = "/no_think\n"  # Qwen3 soft control to suppress <think> blocks

    timestamp_note = f"Report generation timestamp (UTC): {started_at}. " if started_at else ""

    context_map = {
        "master": (
            _NO_THINK +
            "You are the Master News Director orchestrating a 4-round pipeline. "
            "Round 1: assign action_planner. Round 2: assign researcher. "
            "Round 3: assign dashboard_layout_builder. Round 4: assign report_writer. "
            "CRITICAL: In round 5, you MUST set done=true and copy the report_writer HTML verbatim into final_answer. "
            "Do not summarise the HTML — copy it exactly as received."
        ),
        "action_planner": (
            _NO_THINK +
            "You are the Action Planner. Given a topic, produce a JSON collection plan "
            "following the action_planning skill. Include a steps array with tool, args, reason."
        ),
        "researcher": (
            _NO_THINK +
            "You are the Researcher. Execute the collection plan step-by-step using your tools. "
            "Tool order: (1) fetch_trends24 to get trending hashtags, (2) fetch_feeds for headlines, "
            "(3) xfetch_discover to find tweet URLs for top 3-5 events, "
            "(4) xfetch_extract to pull actual tweet TEXT from those URLs via Tor — "
            "bundle all URLs into ONE call (up to 15 URLs, comma-separated). "
            "Include the extracted tweet texts in event_candidates[].sample_tweets and tweet_extractions{}. "
            "(5) websearch_general for broader web context with no platform filter. "
            "(6) facebook_search to find Facebook posts about top events. "
            "Cross-reference sources, find event candidates, then output a research summary JSON "
            "followed by a bulletin board JSON, following the trend_research and bulletin_board skills."
        ),
        "dashboard_layout_builder": (
            _NO_THINK +
            "You are the Dashboard Layout Builder. Take the bulletin board and produce a JSON "
            "layout specification (12-col grid of typed cards) following the dashboarder skill."
        ),
        "report_writer": (
            _NO_THINK +
            f"{timestamp_note}"
            "You are the Report Writer. Take the layout JSON and render a complete, self-contained "
            f"HTML file following the {report_skill} skill. "
            "Use the report generation timestamp above (do NOT invent or change the date/time). "
            "Output ONLY the HTML — nothing else."
        ),
    }

    all_skill_ids = set()
    for ids in skill_map.values():
        all_skill_ids.update(ids)

    skills = []
    for sid in all_skill_ids:
        try:
            skills.append(_load_skill(sid))
        except FileNotFoundError:
            logger.warning("Skill file not found for %s — skipping", sid)

    agents = []
    for agent_id, skill_ids in skill_map.items():
        tool_ids = [t.name for t in AGENT_TOOLS.get(agent_id, [])]
        agents.append(AgentData(
            agent_id=agent_id,
            role=agent_id.replace("_", " ").title(),
            level=level_map[agent_id],
            skills=skill_ids,
            tools=tool_ids,
            context=context_map[agent_id],
            team_memberships=["news_reporter"] if agent_id != "master" else [],
            team_leads=["news_reporter"] if agent_id == "master" else [],
        ))

    config = SystemConfig(
        enable_logging=True,
        auto_save_chat=False,
        max_iter=8,
    )

    return {"agents": agents, "skills": skills, "tools": [], "config": config}


def _build_team() -> TeamData:
    return TeamData(
        team_id="news_reporter",
        name="News Reporter Team",
        leader_id="master",
        structure=TeamStructure.HIERARCHICAL,
        members=["master", "action_planner", "researcher", "dashboard_layout_builder", "report_writer"],
        purpose="Produce automated news intelligence HTML dashboards",
    )


def _write_status_json(run_dir: pathlib.Path, status_data: dict) -> None:
    """Atomically write status.json for live run tracking."""
    tmp_path = run_dir / "status.json.tmp"
    final_path = run_dir / "status.json"
    tmp_path.write_text(json.dumps(status_data, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp_path.replace(final_path)


def _write_partial_history(run_dir: pathlib.Path, history: list) -> None:
    """Atomically write partial_history.json for live trace updates."""
    tmp_path = run_dir / "partial_history.json.tmp"
    final_path = run_dir / "partial_history.json"
    tmp_path.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp_path.replace(final_path)


def _save_run(run_id: str, topic: str, result: dict[str, Any]) -> pathlib.Path:
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    # history
    (run_dir / "history.json").write_text(
        json.dumps(result.get("history", []), indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # final HTML
    html = result.get("final_answer", "")
    if html and html.strip().startswith("<!"):
        (run_dir / "report.html").write_text(html, encoding="utf-8")
        # Also update latest
        latest = ROOT / "data" / "latest_dashboard.html"
        latest.write_text(html, encoding="utf-8")

    # metadata
    meta = {
        "run_id": run_id,
        "topic": topic,
        "started_at": result.get("started_at"),
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "success": result.get("success", False),
        "rounds": result.get("rounds", 0),
        "has_html": bool(html and html.strip().startswith("<!")),
    }
    (run_dir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    return run_dir


def _extract_html_from_history(history: list) -> str:
    """Scan coordinator round history for a report_writer HTML output."""
    import re
    for entry in reversed(history):
        for report in entry.get("reports", []):
            if report.get("agent_id") != "report_writer":
                continue
            output = report.get("output", "")
            # Output may be JSON-wrapped AgentReport: { output: "<!DOCTYPE..." }
            if isinstance(output, str):
                # Try to find raw HTML block
                match = re.search(r'(<!DOCTYPE html.*)', output, re.IGNORECASE | re.DOTALL)
                if match:
                    return match.group(1).strip()
                # Try JSON-decoded
                try:
                    decoded = json.loads(output)
                    inner = decoded.get("output", "") if isinstance(decoded, dict) else ""
                    m2 = re.search(r'(<!DOCTYPE html.*)', inner, re.IGNORECASE | re.DOTALL)
                    if m2:
                        return m2.group(1).strip()
                except Exception:
                    pass
    return ""


def run_news_session(
    topic: str,
    max_rounds: int = 6,
    run_id: str | None = None,
    progress_callback=None,
    skill: str = "html_report_writer",
) -> dict[str, Any]:
    """
    Run a full news reporter coordinator session.

    Args:
        topic: The news topic or free-text query.
        max_rounds: Cap on LeaderCoordinator rounds.
        run_id: Optional UUID; generated if not provided.
        progress_callback: Optional callable(run_id, round_num, brief, reports) for streaming.
        skill: Report writer skill to use (default: html_report_writer).

    Returns:
        dict with keys: run_id, success, rounds, final_answer (HTML), history, run_dir.
    """
    if run_id is None:
        run_id = str(uuid.uuid4())[:8]

    logger.info("Starting news session run_id=%s topic=%r skill=%r", run_id, topic, skill)

    started_at = datetime.now(timezone.utc).isoformat()
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    # Write initial status.json for live tracking
    _write_status_json(run_dir, {"status": "running", "topic": topic, "started_at": started_at, "history_count": 0})

    ecosystem = _build_ecosystem(started_at=started_at, report_skill=skill)
    team = _build_team()
    llm = make_llm_client()

    # Attach per-agent tools to the ecosystem as a lookup
    ecosystem["_agent_tools"] = AGENT_TOOLS

    def _write_progress(round_num: int, history: list) -> None:
        _write_status_json(run_dir, {"status": "running", "topic": topic, "started_at": started_at, "history_count": len(history)})
        _write_partial_history(run_dir, history)

    coordinator = LeaderCoordinator(
        team=team,
        ecosystem=ecosystem,
        llm_client=llm,
        on_round_complete=_write_progress,
    )

    try:
        result = coordinator.run(task=topic, max_rounds=max_rounds)
        result["started_at"] = started_at
        result["run_id"] = run_id

        # If coordinator didn't finish cleanly, scan history for ReportWriter HTML
        if not result.get("success") or not result.get("final_answer", "").strip().startswith("<!"):
            html = _extract_html_from_history(result.get("history", []))
            if html:
                result["final_answer"] = html
                result["success"] = True
                logger.info("Recovered HTML from report_writer history output")

        _write_status_json(run_dir, {"status": "done", "topic": topic, "started_at": started_at, "history_count": len(result.get("history", []))})
    except Exception as exc:
        logger.exception("News session failed run_id=%s", run_id)
        _write_status_json(run_dir, {"status": "error", "topic": topic, "started_at": started_at, "error": str(exc)})
        raise

    run_dir = _save_run(run_id, topic, result)
    result["run_dir"] = str(run_dir)

    logger.info(
        "Session done run_id=%s success=%s rounds=%s",
        run_id, result.get("success"), result.get("rounds"),
    )
    return result
