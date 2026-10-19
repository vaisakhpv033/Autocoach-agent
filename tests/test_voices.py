"""Unit tests for Gemini 3.8 voice management."""

from autocoach.voices import (
    resolve_voice,
    normalize_voice_name,
    ALL_PREBUILT_VOICES,
    GEMINI_MALE_VOICES,
    GEMINI_FEMALE_VOICES,
)


def test_normalize_voice_name():
    assert normalize_voice_name("puck") == "Puck"
    assert normalize_voice_name("AOEDE") == "Aoede"
    assert normalize_voice_name("charon") == "Charon"
    assert normalize_voice_name("voice_custom123") == "voice_custom123"
    assert normalize_voice_name("NonExistentVoice") == "NonExistentVoice"
    assert normalize_voice_name(None) is None


def test_resolve_voice_explicit():
    assert resolve_voice(voice="kore") == "Kore"
    assert resolve_voice(voice="fenrir") == "Fenrir"


def test_resolve_voice_by_gender():
    male_voice = resolve_voice(gender="male")
    assert male_voice in GEMINI_MALE_VOICES

    female_voice = resolve_voice(gender="female")
    assert female_voice in GEMINI_FEMALE_VOICES


def test_resolve_voice_temperament():
    voice = resolve_voice(gender="male", temperament="upbeat")
    assert voice in GEMINI_MALE_VOICES


def test_resolve_voice_fallback():
    voice = resolve_voice(default_fallback="Puck")
    assert voice in ALL_PREBUILT_VOICES
