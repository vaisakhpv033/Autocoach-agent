"""Personas package for AutoCoach simulation."""

from autocoach.personas.base import CustomerPersona
from autocoach.personas.presets import (
    CustomerPersona,
    DEFAULT_PERSONA,
    PERSONA_REGISTRY,
    get_preset_persona,
    register_persona,
)

__all__ = [
    "CustomerPersona",
    "DEFAULT_PERSONA",
    "PERSONA_REGISTRY",
    "get_preset_persona",
    "register_persona",
]
