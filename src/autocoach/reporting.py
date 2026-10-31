"""Session evaluation and reporting module for AutoCoach.

Collects full call metadata, timing metrics, and transcript history upon call
completion and dispatches a structured evaluation payload to the AutoCoach backend.
Includes SSRF validation on custom webhook targets and exponential backoff retry.
"""

import asyncio
from datetime import UTC, datetime
import ipaddress
import logging
from typing import Any, Optional
from urllib.parse import urlparse
import aiohttp
from livekit.agents import JobContext, utils
from autocoach.config import settings
from autocoach.metadata import SessionMetadata

logger = logging.getLogger("autocoach.reporting")


def is_safe_webhook_url(url: str, allow_local: bool = False) -> bool:
    """Validates that a webhook URL is safe against SSRF attacks.

    Rejects:
    - Non-HTTP(S) schemes (e.g. file://, gopher://)
    - Cloud metadata IPs (e.g. 169.254.169.254) and metadata domains
    - Loopback, link-local, and private RFC-1918 addresses unless allow_local is True.
    """
    if not url or not isinstance(url, str):
        return False

    try:
        parsed = urlparse(url.strip())
        if parsed.scheme not in ("http", "https"):
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        hostname_lower = hostname.lower()

        # Cloud metadata service endpoints
        if hostname_lower in (
            "169.254.169.254",
            "metadata.google.internal",
            "metadata.azure.internal",
            "instance-data",
        ):
            return False

        if allow_local:
            return True

        if hostname_lower in ("localhost", "127.0.0.1", "::1"):
            return False

        # If hostname is a literal IP address, verify it is publicly routable
        try:
            ip = ipaddress.ip_address(hostname_lower)
            if (
                ip.is_private
                or ip.is_loopback
                or ip.is_link_local
                or ip.is_reserved
                or ip.is_multicast
            ):
                return False
        except ValueError:
            # Domain name (e.g., translation.vaisakhpv.space)
            pass

        return True
    except Exception:
        return False


async def send_session_report(
    ctx: JobContext,
    meta: SessionMetadata,
    termination_reason: str = "normal",
) -> None:
    """Extracts session telemetry and dispatches structured evaluation report.

    Target URL Resolution:
    1. Per-session override in `meta.reports_webhook_url` (if SSRF-safe)
    2. Environment `AUTOCOACH_REPORTS_URL` / `REPORTS_API_URL`
    """
    raw_override = meta.reports_webhook_url
    target_url = None

    if raw_override:
        if is_safe_webhook_url(raw_override, allow_local=settings.allow_local_webhooks):
            target_url = raw_override
        else:
            logger.warning(
                f"Potentially unsafe reports_webhook_url rejected for SSRF prevention: '{raw_override}'. "
                f"Falling back to default configured reports URL."
            )

    if not target_url:
        target_url = settings.effective_reports_url

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
            "trainee_name": meta.trainee_name or "Citrus Smiles Representative",
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

    # Asynchronous HTTP Dispatch with Exponential Backoff Retry (3 attempts)
    timeout = aiohttp.ClientTimeout(total=settings.reports_timeout_seconds)
    max_retries = 3
    retry_delay = 1.0

    logger.info(f"Dispatching AutoCoach session report to {target_url} (room: {room_name})")

    for attempt in range(1, max_retries + 1):
        try:
            # Use LiveKit's managed shared http session if available
            http_session = utils.http_context.http_session()
            async with http_session.post(
                target_url,
                json=payload,
                timeout=timeout,
                headers={"Content-Type": "application/json"},
            ) as resp:
                if resp.status < 400:
                    logger.info(
                        f"Successfully delivered AutoCoach session report for job {job_id} on attempt {attempt}"
                    )
                    return
                logger.warning(
                    f"Reporting webhook returned HTTP error: {resp.status} {resp.reason} "
                    f"(attempt {attempt}/{max_retries})"
                )
        except (TimeoutError, asyncio.TimeoutError):
            logger.warning(
                f"Timed out after {settings.reports_timeout_seconds}s delivering session report to {target_url} "
                f"(attempt {attempt}/{max_retries})"
            )
        except aiohttp.ClientError as e:
            logger.warning(
                f"Network error delivering session report to {target_url} (attempt {attempt}/{max_retries}): {e}"
            )
        except Exception as e:
            logger.error(f"Unexpected error delivering session report: {e}", exc_info=True)
            return

        if attempt < max_retries:
            await asyncio.sleep(retry_delay)
            retry_delay *= 2.0

    logger.error(
        f"Failed to deliver AutoCoach session report for job {job_id} after {max_retries} attempts."
    )
