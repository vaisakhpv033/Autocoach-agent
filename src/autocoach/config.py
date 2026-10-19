"""Configuration module for AutoCoach Agent.

Provides strongly typed, validated settings loaded from environment variables
and .env files using Pydantic Settings.
"""

from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve AutoCoach project root directory and .env location
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_PATH = PROJECT_ROOT / ".env"

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()


# Comprehensive mapping of standard ISO language codes to Gemini Live BCP-47 tags
LANGUAGE_BCP47_MAP: dict[str, str] = {
    "en": "en-US",
    "en-us": "en-US",
    "en-in": "en-IN",
    "en-gb": "en-GB",
    "english": "en-US",
    "es": "es-US",
    "es-us": "es-US",
    "es-es": "es-ES",
    "es-mx": "es-MX",
    "spanish": "es-US",
    "spanglish": "es-US",
    "code-mix": "es-US",
    "code-mixed": "es-US",
    "code_mix": "es-US",
    "code_mixed": "es-US",
    "es-en": "es-US",
    "en-es": "es-US",
    "hi": "hi-IN",
    "ml": "ml-IN",
    "ta": "ta-IN",
    "te": "te-IN",
    "kn": "kn-IN",
    "mr": "mr-IN",
    "bn": "bn-IN",
    "gu": "gu-IN",
    "pa": "pa-IN",
    "ur": "ur-IN",
    "fr": "fr-FR",
    "de": "de-DE",
    "it": "it-IT",
    "pt": "pt-BR",
    "zh": "zh-CN",
    "ja": "ja-JP",
    "ko": "ko-KR",
    "ar": "ar-AE",
}


class Settings(BaseSettings):
    """Application settings for AutoCoach Agent."""

    model_config = SettingsConfigDict(
        env_file=(".env", str(ENV_PATH)),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LiveKit Server Connection (Self-Hosted SFU or LiveKit Cloud)
    livekit_url: str = Field(default="ws://127.0.0.1:7880", alias="LIVEKIT_URL")
    livekit_api_key: str = Field(default="", alias="LIVEKIT_API_KEY")
    livekit_api_secret: str = Field(default="", alias="LIVEKIT_API_SECRET")

    # Google Gemini 3.8 Live API
    google_api_key: str = Field(default="", alias="GOOGLE_API_KEY")
    gemini_model: str = Field(default="gemini-3.8-live", alias="GEMINI_MODEL")
    gemini_temperature: float = Field(default=0.8, alias="GEMINI_TEMPERATURE")

    # LiveKit Agent Worker & Server Lifecycle
    agent_name: str = Field(default="autocoach-customer-sts", alias="AGENT_NAME")
    health_check_host: str = Field(default="0.0.0.0", alias="HEALTH_CHECK_HOST")
    health_check_port: int = Field(default=8085, alias="HEALTH_CHECK_PORT")
    shutdown_timeout_seconds: float = Field(default=60.0, alias="SHUTDOWN_TIMEOUT_SECONDS")
    worker_load_threshold: float = Field(default=0.7, alias="WORKER_LOAD_THRESHOLD")

    # Post-Session Evaluation & Reporting Webhook
    autocoach_reports_url: Optional[str] = Field(default=None, alias="AUTOCOACH_REPORTS_URL")
    reports_api_url: Optional[str] = Field(default=None, alias="REPORTS_API_URL")
    reports_timeout_seconds: float = Field(default=10.0, alias="AUTOCOACH_REPORTS_TIMEOUT_SECONDS")

    # Default Scenario & Simulation Presets (used when no metadata is provided)
    default_scenario: str = Field(default="default", alias="DEFAULT_SCENARIO")
    default_voice: str = Field(default="Puck", alias="DEFAULT_VOICE")
    default_language: str = Field(default="en", alias="DEFAULT_LANGUAGE")
    default_difficulty: str = Field(default="medium", alias="DEFAULT_DIFFICULTY")

    @property
    def effective_reports_url(self) -> Optional[str]:
        """Resolves the primary reporting URL, supporting backwards compatibility."""
        return self.autocoach_reports_url or self.reports_api_url

    def resolve_bcp47_language(self, language_code: Optional[str]) -> str:
        """Resolves a raw language code or BCP-47 tag into a verified BCP-47 tag for Gemini."""
        if not language_code:
            language_code = self.default_language
        clean = language_code.strip().lower()
        # Direct lookup
        if clean in LANGUAGE_BCP47_MAP:
            return LANGUAGE_BCP47_MAP[clean]
        # Base code lookup if formatted like en_US or en-US
        base_code = clean.split("-")[0].split("_")[0]
        return LANGUAGE_BCP47_MAP.get(base_code, "en-US")


# Global singleton settings instance
settings = Settings()
