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

    # Scenario & Sub-type (for dedicated custom scenarios)
    scenario: str = Field(default_factory=lambda: settings.default_scenario)
    type: Optional[str] = None
    optional_data: dict[str, Any] = Field(default_factory=dict)

    # Persona Attributes
    persona_name: Optional[str] = None
    persona_age: Optional[int] = None
    gender: Optional[str] = None
    temperament: Optional[str] = None
    difficulty: str = Field(default_factory=lambda: settings.default_difficulty)

    # Audio & Voice
    voice: Optional[str] = None
    language: str = Field(default_factory=lambda: settings.default_language)
    code_mixing: bool = False

    # Custom Prompts & Dynamic Injection
    custom_instructions: Optional[str] = None
    prompt_override: Optional[str] = None
    compliance_traps: list[str] = Field(default_factory=list)
    evaluation_rubric: Optional[Any] = None

    # Dental-Patient-Custom scenario overrides
    instructions: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    thinking_level: Optional[str] = None
    vad_sensitivity_ms: Optional[int] = None

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
    if not raw or not isinstance(raw, (str, dict)):
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


def _normalize_metadata_dict(merged_data: dict[str, Any]) -> SessionMetadata:
    """Normalizes raw dictionary into a validated SessionMetadata object."""
    # Handle scenario_type alias
    if "scenario_type" in merged_data and "type" not in merged_data:
        merged_data["type"] = merged_data["scenario_type"]

    # Parse optional_data if passed as JSON string or ensure dict
    if "optional_data" in merged_data:
        raw_opt = merged_data["optional_data"]
        if isinstance(raw_opt, str):
            parsed_opt = _safe_parse_json(raw_opt)
            merged_data["optional_data"] = parsed_opt if isinstance(parsed_opt, dict) else {}
        elif not isinstance(raw_opt, dict):
            merged_data["optional_data"] = {}
    else:
        merged_data["optional_data"] = {}

    opt = merged_data.get("optional_data", {})
    if isinstance(opt, dict):
        if "voice" in opt and ("voice" not in merged_data or not merged_data["voice"]):
            merged_data["voice"] = opt["voice"]
        if "gender" in opt and ("gender" not in merged_data or not merged_data["gender"]):
            merged_data["gender"] = opt["gender"]
        if "persona_name" not in merged_data:
            if "caller_name" in opt:
                merged_data["persona_name"] = opt["caller_name"]
            elif "name" in opt:
                merged_data["persona_name"] = opt["name"]

    # Check dedicated scenario defaults (e.g. gender="male", persona_name="Marcus Turner")
    from autocoach.scenarios.registry import get_scenario_metadata_defaults
    scenario_defaults = get_scenario_metadata_defaults(
        scenario=merged_data.get("scenario"),
        scenario_type=merged_data.get("type"),
    )
    for k, v in scenario_defaults.items():
        if k not in merged_data or not merged_data[k]:
            merged_data[k] = v

    # Handle alias and synonym normalizations
    if "custom_gender" in merged_data and "gender" not in merged_data:
        merged_data["gender"] = merged_data["custom_gender"]

    if "name" in merged_data and "persona_name" not in merged_data:
        merged_data["persona_name"] = merged_data["name"]

    if "mood" in merged_data and "temperament" not in merged_data:
        merged_data["temperament"] = merged_data["mood"]

    if "system_prompt" in merged_data and "prompt_override" not in merged_data:
        merged_data["prompt_override"] = merged_data["system_prompt"]

    # Normalize Spanglish and Code-Mixing settings
    raw_lang = str(merged_data.get("language", "")).strip().lower()
    if raw_lang in ["spanglish", "code-mix", "code_mix", "code-mixed", "es-en", "en-es"]:
        merged_data["code_mixing"] = True
        merged_data["language"] = "es-US"
    elif merged_data.get("code_mixing") in [True, "true", "True", "1", 1]:
        merged_data["code_mixing"] = True

    # Separate known fields from extra_metadata
    known_fields = SessionMetadata.model_fields.keys()
    extra_fields = {k: v for k, v in merged_data.items() if k not in known_fields}
    valid_data = {k: v for k, v in merged_data.items() if k in known_fields}
    valid_data["extra_metadata"] = extra_fields

    try:
        resolved = SessionMetadata(**valid_data)
        logger.info(
            f"Resolved session metadata: scenario='{resolved.scenario}', "
            f"type='{resolved.type}', persona='{resolved.persona_name}', "
            f"voice='{resolved.voice}', difficulty='{resolved.difficulty}', language='{resolved.language}'"
        )
        return resolved
    except Exception as e:
        logger.error(f"Validation error creating SessionMetadata: {e}, falling back to defaults")
        return SessionMetadata(extra_metadata=merged_data)


def resolve_session_metadata_from_dict(data: dict[str, Any]) -> SessionMetadata:
    """Normalizes and constructs a SessionMetadata instance directly from a dictionary."""
    return _normalize_metadata_dict(dict(data))


def create_session_metadata(
    scenario: str = settings.default_scenario,
    type: Optional[str] = "",
    optional_data: Optional[dict[str, Any]] = None,
    **kwargs: Any,
) -> SessionMetadata:
    """Helper to initialize SessionMetadata with the custom scenario format:

    {
        "scenario": "first time appointment",
        "type": "",
        "optional_data": { ... }
    }
    """
    merged: dict[str, Any] = {
        "scenario": scenario,
        "type": type,
        "optional_data": optional_data or {},
    }
    merged.update(kwargs)
    return resolve_session_metadata_from_dict(merged)


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
    if ctx.job and getattr(ctx.job, "metadata", None):
        job_data = _safe_parse_json(ctx.job.metadata)
        merged_data.update(job_data)

    # 2. Room metadata (Overrides job metadata if set)
    if ctx.room and getattr(ctx.room, "metadata", None):
        room_data = _safe_parse_json(ctx.room.metadata)
        merged_data.update(room_data)

    # 3. Remote Participant attributes / metadata (Highest priority)
    if ctx.room and getattr(ctx.room, "remote_participants", None):
        for participant in ctx.room.remote_participants.values():
            if isinstance(getattr(participant, "attributes", None), dict):
                merged_data.update(participant.attributes)
            if getattr(participant, "metadata", None):
                participant_data = _safe_parse_json(participant.metadata)
                merged_data.update(participant_data)
            # Use participant identity as fallback trainee_id if not present
            p_identity = getattr(participant, "identity", None)
            if "trainee_id" not in merged_data and isinstance(p_identity, str):
                merged_data["trainee_id"] = p_identity
            p_name = getattr(participant, "name", None)
            if "trainee_name" not in merged_data and isinstance(p_name, str):
                merged_data["trainee_name"] = p_name

    return _normalize_metadata_dict(merged_data)
