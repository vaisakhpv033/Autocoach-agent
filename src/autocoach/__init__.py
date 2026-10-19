"""AutoCoach Speech-to-Speech (STS) LiveKit Agent.

An enterprise customer simulation agent built with LiveKit Agents and Google Gemini 3.8 Live.
"""

from autocoach.config import settings
from autocoach.metadata import SessionMetadata, extract_session_metadata
from autocoach.voices import resolve_voice, ALL_PREBUILT_VOICES
from autocoach.prompt_engine import build_system_prompt
from autocoach.personas.base import CustomerPersona
from autocoach.agent import server, entrypoint, main

__version__ = "0.1.0"

__all__ = [
    "settings",
    "SessionMetadata",
    "extract_session_metadata",
    "resolve_voice",
    "ALL_PREBUILT_VOICES",
    "build_system_prompt",
    "CustomerPersona",
    "server",
    "entrypoint",
    "main",
]
