"""Personas package for AutoCoach simulation."""

from autocoach.personas.base import CustomerPersona
from autocoach.personas.presets import (
    CustomerPersona,
    DEFAULT_PERSONA,
    PERSONA_REGISTRY,
    RUBRIC_REGISTRY,
    get_preset_persona,
    get_preset_rubric,
    register_persona,
)

__all__ = [
    "CustomerPersona",
    "DEFAULT_PERSONA",
    "PERSONA_REGISTRY",
    "RUBRIC_REGISTRY",
    "get_preset_persona",
    "get_preset_rubric",
    "register_persona",
]
