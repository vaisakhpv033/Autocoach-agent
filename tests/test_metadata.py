"""Unit tests for metadata resolution."""

from unittest.mock import MagicMock
from autocoach.metadata import extract_session_metadata, _safe_parse_json


def test_safe_parse_json():
    assert _safe_parse_json('{"persona": "Alex", "difficulty": "hard"}') == {
        "persona": "Alex",
        "difficulty": "hard",
    }
    assert _safe_parse_json({"persona": "Alex"}) == {"persona": "Alex"}
    assert _safe_parse_json("") == {}
    assert _safe_parse_json(None) == {}
    assert _safe_parse_json("not-json") == {"raw_value": "not-json"}


def test_extract_session_metadata_cascading():
    ctx = MagicMock()
    # 1. Job metadata (Base)
    ctx.job.metadata = '{"scenario": "banking", "difficulty": "easy", "voice": "Puck"}'
    # 2. Room metadata (Overrides difficulty)
    ctx.room.metadata = '{"difficulty": "hard"}'
    # 3. Remote participant (Overrides voice & provides trainee)
    participant = MagicMock()
    participant.attributes = {"voice": "Charon"}
    participant.metadata = '{"trainee_id": "agent_007", "trainee_name": "James"}'
    participant.identity = "agent_007"
    participant.name = "James"
    ctx.room.remote_participants = {"p1": participant}

    resolved = extract_session_metadata(ctx)

    assert resolved.scenario == "banking"
    assert resolved.difficulty == "hard"  # Room overrode Job
    assert resolved.voice == "Charon"      # Participant overrode Room & Job
    assert resolved.trainee_id == "agent_007"
    assert resolved.trainee_name == "James"


def test_extract_session_metadata_aliases():
    ctx = MagicMock()
    ctx.job.metadata = '{"name": "Robert", "mood": "angry", "custom_gender": "male"}'
    ctx.room.metadata = None
    ctx.room.remote_participants = {}

    resolved = extract_session_metadata(ctx)

    assert resolved.persona_name == "Robert"
    assert resolved.temperament == "angry"
    assert resolved.gender == "male"
