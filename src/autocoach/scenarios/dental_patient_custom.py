"""Dental-Patient-Custom scenario configuration resolver.

Validates and resolves all custom overrides for the dental-patient-custom
scenario: model selection, temperature, thinking config, voice gender,
VAD sensitivity, and system instructions.
"""

import logging
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from autocoach.metadata import SessionMetadata
from autocoach.config import settings

logger = logging.getLogger("autocoach.dental_patient_custom")

# Allowed models for dental-patient-custom
ALLOWED_MODELS = {
    "gemini-3.8-live",
    "gemini-3.8-live-extended-thinking",
    "gemini-3.1-flash-live-preview",
}

# Models that support configurable thinking levels (low/medium/high)
# Standard gemini-3.8-live only supports MINIMAL — thinking_config is NOT_GIVEN for it.
THINKING_CAPABLE_MODELS = {
    "gemini-3.8-live-extended-thinking",
    "gemini-3.1-flash-live-preview",
}

ALLOWED_THINKING_LEVELS = {"minimal", "low", "medium", "high"}

# VAD sensitivity bounds (milliseconds)
VAD_MIN_MS = 300
VAD_MAX_MS = 2000


class DentalPatientCustomConfig(BaseModel):
    """Validated configuration for a dental-patient-custom session."""

    instructions: str
    gender: str
    model: str = "gemini-3.8-live"
    temperature: float = Field(default_factory=lambda: settings.gemini_temperature)
    thinking_level: str = "high"
    vad_sensitivity_ms: int = Field(default_factory=lambda: settings.silence_duration_ms)
    language: str = Field(default_factory=lambda: settings.default_language)
    code_mixing: bool = False

    @field_validator("instructions")
    @classmethod
    def validate_instructions(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("instructions must be a non-empty string")
        if len(stripped.encode("utf-8")) > 32 * 1024:
            raise ValueError("instructions exceeds maximum size of 32KB")
        return stripped

    @field_validator("model")
    @classmethod
    def validate_model(cls, v: str) -> str:
        normalized = v.strip().lower()
        if normalized not in ALLOWED_MODELS:
            raise ValueError(
                f"Invalid model '{v}'. Allowed: {sorted(ALLOWED_MODELS)}"
            )
        return normalized

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        normalized = v.strip().lower()
        if normalized not in {"male", "female", "m", "f", "man", "woman"}:
            raise ValueError(
                f"Invalid gender '{v}'. Allowed: 'male', 'female', 'm', 'f'"
            )
        return normalized

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        if not (0.0 <= v <= 2.0):
            raise ValueError(
                f"Temperature {v} out of range. Must be between 0.0 and 2.0"
            )
        return v

    @field_validator("thinking_level")
    @classmethod
    def validate_thinking_level(cls, v: str) -> str:
        normalized = v.strip().lower()
        if normalized not in ALLOWED_THINKING_LEVELS:
            raise ValueError(
                f"Invalid thinking_level '{v}'. Allowed: {sorted(ALLOWED_THINKING_LEVELS)}"
            )
        return normalized

    @field_validator("vad_sensitivity_ms")
    @classmethod
    def validate_vad_sensitivity(cls, v: int) -> int:
        if not (VAD_MIN_MS <= v <= VAD_MAX_MS):
            raise ValueError(
                f"vad_sensitivity_ms {v} out of range. Must be {VAD_MIN_MS}–{VAD_MAX_MS}ms"
            )
        return v


def resolve_dental_patient_custom_config(
    meta: SessionMetadata,
) -> DentalPatientCustomConfig:
    """Extracts and validates dental-patient-custom config from session metadata.

    Resolution priority:
    1. Explicit top-level metadata fields (instructions, model, etc.)
    2. Fields nested inside optional_data
    3. Defaults
    """
    opt = meta.optional_data or {}

    # --- Instructions ---
    instructions = meta.instructions or opt.get("instructions")
    instructions_source = "meta.instructions" if meta.instructions else ("optional_data" if opt.get("instructions") else "MISSING")
    if not instructions:
        raise ValueError(
            "dental-patient-custom scenario requires 'instructions' "
            "(the full system prompt for the simulated patient)"
        )

    # --- Gender ---
    gender = meta.gender or opt.get("gender")
    gender_source = "meta.gender" if meta.gender else ("optional_data" if opt.get("gender") else "MISSING")
    if not gender:
        raise ValueError(
            "dental-patient-custom scenario requires 'gender' ('male' or 'female')"
        )

    # --- Model ---
    model = meta.model or opt.get("model", "gemini-3.8-live")
    model_source = "meta.model" if meta.model else ("optional_data" if "model" in opt else "DEFAULT")

    # --- Temperature ---
    temperature = meta.temperature if meta.temperature is not None else opt.get("temperature")
    temperature_source = "meta.temperature" if meta.temperature is not None else ("optional_data" if "temperature" in opt else "DEFAULT")

    # --- VAD ---
    vad_ms = meta.vad_sensitivity_ms if meta.vad_sensitivity_ms is not None else opt.get("vad_sensitivity_ms")
    vad_source = "meta.vad_sensitivity_ms" if meta.vad_sensitivity_ms is not None else ("optional_data" if "vad_sensitivity_ms" in opt else "DEFAULT")

    # --- Language & Code-Mixing ---
    raw_lang = meta.language or opt.get("language") or settings.default_language
    code_mixing = meta.code_mixing or bool(opt.get("code_mixing", False))
    # Detect code-mixing aliases
    if str(raw_lang).strip().lower() in ["spanglish", "code-mix", "code_mix", "code-mixed", "es-en", "en-es"]:
        code_mixing = True
        language = "es-US"
    else:
        language = str(raw_lang)

    language_source = (
        "meta.language"
        if meta.language and meta.language != settings.default_language
        else ("optional_data" if "language" in opt else "DEFAULT")
    )

    # --- Thinking Level (model-aware defaults) ---
    raw_thinking = meta.thinking_level or opt.get("thinking_level")
    if raw_thinking:
        thinking_level = raw_thinking
        thinking_source = "meta.thinking_level" if meta.thinking_level else "optional_data"
    elif model.strip().lower() == "gemini-3.1-flash-live-preview":
        thinking_level = "minimal"
        thinking_source = "DEFAULT (minimal for 3.1-flash-live)"
    else:
        thinking_level = "high"
        thinking_source = "DEFAULT (high for extended-thinking)"

    # Log the resolution sources so we can verify the right parameters are being used
    instructions_preview = instructions[:80].replace("\n", " ") + "..." if len(instructions) > 80 else instructions.replace("\n", " ")
    logger.info(
        f"[dental-patient-custom] Config resolution:\n"
        f"  instructions : [{instructions_source}] ({len(instructions)} chars) \"{instructions_preview}\"\n"
        f"  gender       : [{gender_source}] {gender}\n"
        f"  model        : [{model_source}] {model}\n"
        f"  temperature  : [{temperature_source}] {temperature if temperature is not None else f'DEFAULT ({settings.gemini_temperature})'}\n"
        f"  thinking_lvl : [{thinking_source}] {thinking_level}\n"
        f"  vad_ms       : [{vad_source}] {vad_ms if vad_ms is not None else f'DEFAULT ({settings.silence_duration_ms})'}\n"
        f"  language     : [{language_source}] {language} (code_mixing={code_mixing})"
    )

    config_data: dict = {
        "instructions": instructions,
        "gender": gender,
        "model": model,
        "thinking_level": thinking_level,
        "language": language,
        "code_mixing": code_mixing,
    }
    if temperature is not None:
        config_data["temperature"] = temperature
    if vad_ms is not None:
        config_data["vad_sensitivity_ms"] = vad_ms

    config = DentalPatientCustomConfig(**config_data)

    # Log the final validated config to confirm Pydantic didn't silently change anything
    logger.info(
        f"[dental-patient-custom] Validated config: "
        f"model='{config.model}', gender='{config.gender}', "
        f"language='{config.language}', code_mixing={config.code_mixing}, "
        f"temperature={config.temperature}, thinking_level='{config.thinking_level}', "
        f"vad_sensitivity_ms={config.vad_sensitivity_ms}, instructions_len={len(config.instructions)}"
    )

    return config

