"""Unit tests for initiating the agent with dedicated scenarios, types, and optional_data."""

from unittest.mock import MagicMock
from autocoach.metadata import (
    SessionMetadata,
    create_session_metadata,
    resolve_session_metadata_from_dict,
    extract_session_metadata,
)
from autocoach.prompt_engine import build_system_prompt
from autocoach.voices import resolve_voice, GEMINI_MALE_VOICES
from autocoach.scenarios.prompts.first_time_appointment import FIRST_TIME_APPOINTMENT_SELF_SYSTEM_PROMPT


def test_init_with_first_time_appointment_default():
    """Verify initiation format: {scenario: 'first time appointment', type: '', optional_data: {}}."""
    config = {
        "scenario": "first time appointment",
        "type": "",
        "optional_data": {},
    }
    meta = resolve_session_metadata_from_dict(config)

    assert meta.scenario == "first time appointment"
    assert meta.type == ""
    assert meta.optional_data == {}
    # Default gender must be male for Raul Laredo
    assert meta.gender == "male"
    assert meta.persona_name == "Raul Laredo"

    prompt = build_system_prompt(meta)

    # Must be the dedicated prompt
    assert prompt == FIRST_TIME_APPOINTMENT_SELF_SYSTEM_PROMPT.strip()
    assert "Raul Laredo" in prompt
    assert "Blue Cross Blue Shield" in prompt
    assert "ZKR605436482" in prompt

    # Must NOT contain prompt engine 5-layer components or generic persona
    assert "Citrus Smiles" not in prompt
    assert "Alex Morgan" not in prompt
    assert "IMMUTABLE CLOSING CLAMP" not in prompt


def test_first_time_appointment_male_voice_resolution():
    """Verify that default initiation selects a male voice from the Gemini catalog."""
    config = {
        "scenario": "first time appointment",
        "type": "",
        "optional_data": {},
    }
    meta = resolve_session_metadata_from_dict(config)

    # Multiple voice resolutions must all select from the male voice pool
    for _ in range(10):
        voice = resolve_voice(
            voice=meta.voice,
            gender=meta.gender,
            temperament=meta.temperament,
        )
        assert voice in GEMINI_MALE_VOICES


def test_first_time_appointment_explicit_voice_in_optional_data():
    """Verify that an explicit male voice in optional_data is honored."""
    config = {
        "scenario": "first time appointment",
        "type": "",
        "optional_data": {
            "voice": "Charon",
        },
    }
    meta = resolve_session_metadata_from_dict(config)

    assert meta.voice == "Charon"
    assert meta.gender == "male"

    voice = resolve_voice(voice=meta.voice, gender=meta.gender)
    assert voice == "Charon"


def test_init_with_personal_type_and_optional_data():
    """Verify initiation with custom optional_data overrides."""
    config = {
        "scenario": "first time appointment",
        "type": "personal",
        "optional_data": {
            "caller_name": "Marcus Vance",
            "phone_number": "555-888-9999",
            "dob": "08/12/1980",
            "insurance_carrier": "Delta Dental",
            "plan_type": "PPO",
            "member_id": "DELTA998877",
            "group_number": "GRP-12345",
            "after_hours_constraint": "4:30 PM",
            "voice": "Umbriel",
        },
    }
    meta = resolve_session_metadata_from_dict(config)

    assert meta.scenario == "first time appointment"
    assert meta.type == "personal"
    assert meta.optional_data["caller_name"] == "Marcus Vance"
    assert meta.persona_name == "Marcus Vance"
    assert meta.gender == "male"
    assert meta.voice == "Umbriel"

    prompt = build_system_prompt(meta)

    # Must reflect all custom optional_data fields
    assert "Marcus Vance" in prompt
    assert "M A R C U S" in prompt
    assert "555-888-9999" in prompt
    assert "08/12/1980" in prompt
    assert "Delta Dental" in prompt
    assert "DELTA998877" in prompt
    assert "GRP-12345" in prompt
    assert "4:30 PM" in prompt

    # Preserves patient epistemic boundaries
    assert "WHAT YOU DO NOT KNOW (STRICT CLINIC BOUNDARIES)" in prompt
    assert "CONVERSATIONAL WORKFLOW & BEHAVIORAL STAGES" in prompt


def test_extract_session_metadata_from_job_context():
    """Verify LiveKit JobContext metadata JSON extraction with scenario, type, and optional_data."""
    ctx = MagicMock()
    ctx.job.metadata = '{"scenario": "first time appointment", "type": "", "optional_data": {"caller_name": "David Miller"}}'
    ctx.room.metadata = None
    ctx.room.remote_participants = {}

    meta = extract_session_metadata(ctx)

    assert meta.scenario == "first time appointment"
    assert meta.type == ""
    assert isinstance(meta.optional_data, dict)
    assert meta.optional_data["caller_name"] == "David Miller"
    assert meta.persona_name == "David Miller"
    assert meta.gender == "male"

    prompt = build_system_prompt(meta)
    assert "David Miller" in prompt


def test_create_session_metadata_helper():
    """Verify create_session_metadata helper function."""
    meta = create_session_metadata(
        scenario="first time appointment",
        type="",
        optional_data={},
    )
    assert meta.scenario == "first time appointment"
    assert meta.type == ""
    assert meta.gender == "male"
    assert meta.optional_data == {}

    prompt = build_system_prompt(meta)
    assert prompt == FIRST_TIME_APPOINTMENT_SELF_SYSTEM_PROMPT.strip()
