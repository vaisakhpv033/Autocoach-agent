"""Unit tests for English, Spanish, and Spanglish code-mixing modes."""

from unittest.mock import MagicMock
from autocoach.config import settings
from autocoach.metadata import SessionMetadata, extract_session_metadata
from autocoach.prompt_engine import build_system_prompt


def test_pure_english_mode():
    meta = SessionMetadata(language="en-US", code_mixing=False)
    prompt = build_system_prompt(meta)
    bcp47 = settings.resolve_bcp47_language(meta.language)
    asr_codes = settings.resolve_asr_language_codes(meta.language, meta.code_mixing)

    assert "AMERICAN ENGLISH" in prompt
    assert bcp47 == "en-US"
    assert asr_codes == ["en-US"]


def test_pure_spanish_mode():
    meta = SessionMetadata(language="es-US", code_mixing=False)
    prompt = build_system_prompt(meta)
    bcp47 = settings.resolve_bcp47_language(meta.language)
    asr_codes = settings.resolve_asr_language_codes(meta.language, meta.code_mixing)

    assert "PURE US SPANISH" in prompt
    assert "Lo siento muchísimo. Yo no hablo español" in prompt
    assert bcp47 == "es-US"
    assert asr_codes == ["es-US"]


def test_spanglish_code_mix_mode():
    meta = SessionMetadata(language="es-US", code_mixing=True)
    prompt = build_system_prompt(meta)
    bcp47 = settings.resolve_bcp47_language(meta.language)
    asr_codes = settings.resolve_asr_language_codes(meta.language, meta.code_mixing)

    assert "SPANGLISH / CODE-MIXING" in prompt
    assert "code-switches between conversational American English and Spanish" in prompt
    assert bcp47 == "es-US"
    assert asr_codes == ["en-US", "es-US"]


def test_extract_session_metadata_spanglish_detection():
    ctx = MagicMock()
    ctx.job.metadata = '{"language": "spanglish", "scenario": "dental_scheduling"}'
    ctx.room.metadata = None
    ctx.room.remote_participants = {}

    meta = extract_session_metadata(ctx)
    asr_codes = settings.resolve_asr_language_codes(meta.language, meta.code_mixing)

    assert meta.code_mixing is True
    assert meta.language == "es-US"
    assert asr_codes == ["en-US", "es-US"]


def test_extract_session_metadata_explicit_code_mixing():
    ctx = MagicMock()
    ctx.job.metadata = '{"language": "es-US", "code_mixing": true}'
    ctx.room.metadata = None
    ctx.room.remote_participants = {}

    meta = extract_session_metadata(ctx)
    asr_codes = settings.resolve_asr_language_codes(meta.language, meta.code_mixing)

    assert meta.code_mixing is True
    assert meta.language == "es-US"
    assert asr_codes == ["en-US", "es-US"]
