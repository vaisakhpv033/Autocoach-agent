"""Unit tests for Speech Dynamics, Turn-Taking, and Gemini 3.8 Live Configuration."""

import pytest
from google.genai import types
from livekit.agents import AgentSession, TurnHandlingOptions
from livekit.agents.voice.turn import InterruptionOptions
from livekit.plugins import google

from autocoach.config import settings


def test_speech_dynamics_settings():
    """Verify default settings reflect production-grade turn-taking and dental vocabulary."""
    assert settings.silence_duration_ms == 600
    assert settings.allow_interruptions is True
    assert settings.resume_false_interruption is True
    assert settings.min_interruption_duration == 0.5
    assert settings.min_interruption_words == 2

    # Verify dental domain biasing vocabulary
    assert isinstance(settings.dental_custom_vocabulary, list)
    assert len(settings.dental_custom_vocabulary) >= 10
    assert "root canal" in settings.dental_custom_vocabulary
    assert "crown" in settings.dental_custom_vocabulary
    assert "Delta Dental" in settings.dental_custom_vocabulary
    assert "Open Dental" in settings.dental_custom_vocabulary


@pytest.mark.asyncio
async def test_turn_handling_options():
    """Verify modern TurnHandlingOptions configuration without deprecation warnings."""
    turn_handling = TurnHandlingOptions(
        interruption=InterruptionOptions(
            enabled=settings.allow_interruptions,
            resume_false_interruption=settings.resume_false_interruption,
            min_duration=settings.min_interruption_duration,
            min_words=settings.min_interruption_words,
        )
    )

    assert "interruption" in turn_handling
    interruption = turn_handling["interruption"]
    assert interruption["enabled"] is True
    assert interruption["resume_false_interruption"] is True
    assert interruption["min_duration"] == 0.5
    assert interruption["min_words"] == 2

    # Test clean AgentSession creation with turn_handling
    session = AgentSession(turn_handling=turn_handling)
    assert session is not None


def test_realtime_model_gemini_38_configuration():
    """Verify Gemini 3.8 Live configuration adheres to Google and LiveKit specifications."""
    llm = google.realtime.RealtimeModel(
        model=settings.gemini_model,
        voice=settings.default_voice,
        temperature=settings.gemini_temperature,
        api_key="mock_test_key_for_unit_tests",
        modalities=[types.Modality.AUDIO],
        instructions="System prompt instructions",
        thinking_config=settings.resolve_thinking_config(),
        input_audio_transcription=types.AudioTranscriptionConfig(
            language_codes=["en-US"],
            custom_vocabulary=settings.dental_custom_vocabulary,
        ),
        realtime_input_config=types.RealtimeInputConfig(
            automatic_activity_detection=types.AutomaticActivityDetection(
                disabled=False,
                silence_duration_ms=settings.silence_duration_ms,
            )
        ),
    )

    # 1. Verify instructions are wired directly into RealtimeModel
    assert llm._opts.instructions == "System prompt instructions"

    # 2. Verify thinking_config is set for extended-thinking model with LOW level
    if "extended-thinking" in settings.gemini_model:
        assert llm._opts.thinking_config is not None
        assert llm._opts.thinking_config.thinking_level == types.ThinkingLevel.LOW

    # 3. Verify VAD silence detection is tuned to 600ms
    assert (
        llm._opts.realtime_input_config.automatic_activity_detection.silence_duration_ms
        == 600
    )

    # 4. Verify dental custom vocabulary is passed to input audio transcription
    assert (
        llm._opts.input_audio_transcription.custom_vocabulary
        == settings.dental_custom_vocabulary
    )

    # 5. Verify legacy enable_affective_dialog is NOT given (enabled by default in 3.8 Live)
    from livekit.agents.types import NOT_GIVEN
    assert llm._opts.enable_affective_dialog is NOT_GIVEN


def test_resolve_thinking_config_switching():
    """Verify resolve_thinking_config dynamically provides ThinkingConfig or NOT_GIVEN."""
    from livekit.agents.types import NOT_GIVEN

    # Extended thinking model requires thinking_config with thinking_level
    tc = settings.resolve_thinking_config()
    if "extended-thinking" in settings.gemini_model:
        assert tc != NOT_GIVEN
        assert tc.thinking_level == types.ThinkingLevel.LOW

    # Custom thinking level
    custom_tc = settings.resolve_thinking_config(thinking_level="MINIMAL")
    if "extended-thinking" in settings.gemini_model:
        assert custom_tc.thinking_level == types.ThinkingLevel.MINIMAL
