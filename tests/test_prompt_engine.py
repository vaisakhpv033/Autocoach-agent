"""Unit tests for 5-layer prompt engine."""

from autocoach.metadata import SessionMetadata
from autocoach.prompt_engine import build_system_prompt


def test_build_system_prompt_default():
    meta = SessionMetadata(scenario="default", difficulty="medium")
    prompt = build_system_prompt(meta)

    # Check Layer 1 (Directives)
    assert "YOU ARE THE CALLER / CUSTOMER" in prompt
    assert "Keep most turns between 3 and 15 words" in prompt

    # Check Layer 2 (Persona)
    assert "Alex Morgan" in prompt

    # Check Layer 3 (Difficulty)
    assert "Difficulty Tier: MEDIUM" in prompt

    # Check Layer 4 (Objectives / Traps)
    assert "COMPLIANCE TRAPS" in prompt


def test_build_system_prompt_with_custom_instructions():
    meta = SessionMetadata(
        scenario="default",
        custom_instructions="The trainee must ask for two-factor authentication before proceeding.",
    )
    prompt = build_system_prompt(meta)

    assert "DYNAMIC INJECTED SCENARIO INSTRUCTIONS" in prompt
    assert "The trainee must ask for two-factor authentication" in prompt


def test_build_system_prompt_override():
    meta = SessionMetadata(
        prompt_override="You are playing a completely custom customer scenario.",
    )
    prompt = build_system_prompt(meta)

    assert "You are playing a completely custom customer scenario." in prompt
    assert "CRITICAL SPOKEN VOICE RULES" in prompt
