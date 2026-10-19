"""Multi-source metadata resolution module for AutoCoach.

Extracts, normalizes, and cascades configuration from:
1. Remote Participant attributes / metadata (Trainee specifics)
2. Room metadata (Set by backend room creation API)
3. Job dispatch metadata (Set by LiveKit Job Dispatch API)
4. Environment / System defaults
"""

import json
import logging
from typing import Any, Optional
from pydantic import BaseModel, Field
from livekit.agents import JobContext
from autocoach.config import settings

logger = logging.getLogger("autocoach.metadata")


class SessionMetadata(BaseModel):
    """Normalized, validated session configuration model."""

    # Scenario & Persona
    scenario: str = Field(default_factory=lambda: settings.default_scenario)
    persona_name: Optional[str] = None
    persona_age: Optional[int] = None
    gender: Optional[str] = None
    temperament: Optional[str] = None
    difficulty: str = Field(default_factory=lambda: settings.default_difficulty)

    # Audio & Voice
    voice: Optional[str] = None
    language: str = Field(default_factory=lambda: settings.default_language)

    # Custom Prompts & Dynamic Injection
    custom_instructions: Optional[str] = None
    prompt_override: Optional[str] = None
    compliance_traps: list[str] = Field(default_factory=list)

    # AutoCoach Trainee & LMS Tracking
    trainee_id: Optional[str] = None
    trainee_name: Optional[str] = None
    session_id: Optional[str] = None

    # Reporting / Webhook Override
    reports_webhook_url: Optional[str] = None

    # Unmapped arbitrary attributes
    extra_metadata: dict[str, Any] = Field(default_factory=dict)


def _safe_parse_json(raw: Any) -> dict[str, Any]:
    """Safely converts string, dict, or None into a Python dictionary."""
    if not raw:
        return {}
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                return parsed
            return {"raw_value": parsed}
        except (json.JSONDecodeError, TypeError) as e:
            logger.debug(f"Could not parse string as JSON, treating as raw string: {e}")
            return {"raw_value": raw}
    return {}


def extract_session_metadata(ctx: JobContext) -> SessionMetadata:
    """Cascades and resolves metadata from all LiveKit sources.
    
    Priority Order (Highest to Lowest):
    1. Participant attributes / metadata (if trainee participant is present)
    2. Room metadata
    3. Job metadata
    4. Environment defaults
    """
    merged_data: dict[str, Any] = {}

    # 1. Job Dispatch metadata (Base)
    if ctx.job and ctx.job.metadata:
        job_data = _safe_parse_json(ctx.job.metadata)
        merged_data.update(job_data)

    # 2. Room metadata (Overrides job metadata if set)
    if ctx.room and ctx.room.metadata:
        room_data = _safe_parse_json(ctx.room.metadata)
        merged_data.update(room_data)

    # 3. Remote Participant attributes / metadata (Highest priority)
    # Check remote participants in the room
    if ctx.room and ctx.room.remote_participants:
        for participant in ctx.room.remote_participants.values():
            if participant.attributes:
                merged_data.update(participant.attributes)
            if participant.metadata:
                participant_data = _safe_parse_json(participant.metadata)
                merged_data.update(participant_data)
            # Use participant identity as fallback trainee_id if not present
            if "trainee_id" not in merged_data and participant.identity:
                merged_data["trainee_id"] = participant.identity
            if "trainee_name" not in merged_data and participant.name:
                merged_data["trainee_name"] = participant.name

    # Handle alias and synonym normalizations
    if "custom_gender" in merged_data and "gender" not in merged_data:
        merged_data["gender"] = merged_data["custom_gender"]

    if "name" in merged_data and "persona_name" not in merged_data:
        merged_data["persona_name"] = merged_data["name"]

    if "mood" in merged_data and "temperament" not in merged_data:
        merged_data["temperament"] = merged_data["mood"]

    if "system_prompt" in merged_data and "prompt_override" not in merged_data:
        merged_data["prompt_override"] = merged_data["system_prompt"]

    # Separate known fields from extra_metadata
    known_fields = SessionMetadata.model_fields.keys()
    extra_fields = {k: v for k, v in merged_data.items() if k not in known_fields}
    valid_data = {k: v for k, v in merged_data.items() if k in known_fields}
    valid_data["extra_metadata"] = extra_fields

    try:
        resolved = SessionMetadata(**valid_data)
        logger.info(
            f"Resolved session metadata: scenario='{resolved.scenario}', "
            f"persona='{resolved.persona_name}', voice='{resolved.voice}', "
            f"difficulty='{resolved.difficulty}', language='{resolved.language}'"
        )
        return resolved
    except Exception as e:
        logger.error(f"Validation error creating SessionMetadata: {e}, falling back to defaults")
        return SessionMetadata(extra_metadata=merged_data)
