"""Session evaluation and reporting module for AutoCoach.

Collects full call metadata, timing metrics, and transcript history upon call
completion and dispatches a structured evaluation payload to the AutoCoach backend.
"""

import asyncio
import logging
from datetime import UTC, datetime
from typing import Any, Optional
import aiohttp
from livekit.agents import JobContext, utils
from autocoach.config import settings
from autocoach.metadata import SessionMetadata

logger = logging.getLogger("autocoach.reporting")


async def send_session_report(
    ctx: JobContext,
    meta: SessionMetadata,
    termination_reason: str = "normal",
) -> None:
    """Extracts session telemetry and dispatches structured evaluation report.
    
    Target URL Resolution:
    1. Per-session override in `meta.reports_webhook_url`
    2. Environment `AUTOCOACH_REPORTS_URL` / `REPORTS_API_URL`
    """
    target_url = meta.reports_webhook_url or settings.effective_reports_url
    if not target_url:
        logger.info("No reporting webhook URL configured. Skipping session report dispatch.")
        return

    ended_at = datetime.now(UTC)
    session = getattr(ctx, "_primary_agent_session", None)
    if not session:
        logger.warning("No primary agent session found on JobContext; generating partial report.")

    # LiveKit built-in session report
    lk_report = None
    chat_history_data: Optional[list[dict[str, Any]]] = None

    try:
        lk_report = ctx.make_session_report()
        if lk_report and lk_report.chat_history:
            chat_history_data = lk_report.chat_history.to_dict(exclude_timestamp=False)
    except Exception as e:
        logger.debug(f"Could not extract standard LiveKit session report: {e}")

    started_at_str: Optional[str] = None
    duration_seconds: Optional[float] = None
    if lk_report and lk_report.started_at:
        started_dt = datetime.fromtimestamp(lk_report.started_at, UTC)
        started_at_str = started_dt.isoformat().replace("+00:00", "Z")
        duration_seconds = (ended_at - started_dt).total_seconds()

    room_name = ctx.room.name if ctx.room else (lk_report.room if lk_report else "unknown")
    job_id = ctx.job.id if ctx.job else (lk_report.job_id if lk_report else "unknown")

    # Resolve optional evaluation rubric (metadata override or preset scenario rubric)
    rubric = meta.evaluation_rubric
    if rubric is None:
        try:
            from autocoach.personas.presets import get_preset_rubric
            rubric = get_preset_rubric(meta.scenario)
        except ImportError:
            rubric = None

    # Structured Enterprise Evaluation Payload
    payload: dict[str, Any] = {
        "job_id": job_id,
        "room_name": room_name,
        "session_id": meta.session_id or job_id,
        "started_at": started_at_str,
        "ended_at": ended_at.isoformat().replace("+00:00", "Z"),
        "duration_seconds": duration_seconds,
        "trainee": {
            "trainee_id": meta.trainee_id or "unknown",
            "trainee_name": meta.trainee_name or "Trainee",
        },
        "simulation": {
            "scenario": meta.scenario,
            "persona_name": meta.persona_name or "Simulated Customer",
            "difficulty": meta.difficulty,
            "voice": meta.voice,
            "language": meta.language,
            "compliance_traps": meta.compliance_traps,
        },
        "evaluation_rubric": rubric,
        "termination": {
            "reason": termination_reason,
            "timestamp": ended_at.isoformat().replace("+00:00", "Z"),
        },
        "chat_history": chat_history_data,
        "extra_metadata": meta.extra_metadata,
    }

    # Asynchronous HTTP Dispatch with Timeout
    timeout = aiohttp.ClientTimeout(total=settings.reports_timeout_seconds)
    logger.info(f"Dispatching AutoCoach session report to {target_url} (room: {room_name})")

    try:
        # Use LiveKit's managed shared http session if available
        http_session = utils.http_context.http_session()
        async with http_session.post(
            target_url,
            json=payload,
            timeout=timeout,
            headers={"Content-Type": "application/json"},
        ) as resp:
            if resp.status >= 400:
                logger.error(f"Reporting webhook returned HTTP error: {resp.status} {resp.reason}")
            else:
                logger.info(f"Successfully delivered AutoCoach session report for job {job_id}")
    except (TimeoutError, asyncio.TimeoutError):
        logger.error(f"Timed out after {settings.reports_timeout_seconds}s delivering session report to {target_url}")
    except aiohttp.ClientError as e:
        logger.error(f"Network error delivering session report to {target_url}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error delivering session report: {e}", exc_info=True)
