"""Scenario registry for custom dedicated AutoCoach scenarios.

Maintains standalone, fully self-contained system prompts for specific scenario workflows.
Dedicated scenarios bypass generic 5-layer prompt assembly, ensuring the AI strictly
operates from the patient's perspective with zero extra wrapping.
"""

from typing import Any, Optional
from autocoach.scenarios.prompts.first_time_appointment import (
    FIRST_TIME_APPOINTMENT_SELF_SYSTEM_PROMPT,
    get_personal_first_time_appointment_prompt,
)


def normalize_scenario_name(scenario: Optional[str]) -> str:
    """Normalizes scenario strings to canonical lowercase snake_case."""
    if not scenario:
        return ""
    return scenario.strip().lower().replace("-", "_").replace(" ", "_")


def normalize_scenario_type(scenario_type: Optional[str]) -> str:
    """Normalizes scenario type strings to canonical lowercase snake_case."""
    if not scenario_type:
        return ""
    return scenario_type.strip().lower().replace("-", "_").replace(" ", "_")


# Registry of dedicated scenario canonical names
DEDICATED_SCENARIOS = {
    "first_time_appointment",
    "first_time_appointments",
}


def is_dedicated_scenario(scenario: Optional[str]) -> bool:
    """Checks whether a scenario name corresponds to a registered dedicated scenario."""
    return normalize_scenario_name(scenario) in DEDICATED_SCENARIOS


def get_scenario_metadata_defaults(
    scenario: Optional[str],
    scenario_type: Optional[str] = "",
) -> dict[str, Any]:
    """Returns scenario-specific metadata defaults (e.g. caller gender, name).

    For personal first-time appointments (Raul Laredo), gender defaults to 'male'
    so that any Gemini Live male voice is selected.
    """
    norm_scenario = normalize_scenario_name(scenario)
    norm_type = normalize_scenario_type(scenario_type)

    if norm_scenario in ["first_time_appointment", "first_time_appointments"]:
        if norm_type in ["", "personal", "self", "individual"]:
            return {
                "gender": "male",
                "persona_name": "Raul Laredo",
            }
        elif norm_type in ["family", "children"]:
            return {
                "gender": "male",  # Brandon Reiser
                "persona_name": "Brandon Reiser",
            }

    return {}


def get_dedicated_system_prompt(
    scenario: str,
    scenario_type: Optional[str] = "",
    optional_data: Optional[dict[str, Any]] = None,
) -> Optional[str]:
    """Resolves and returns the standalone full system prompt for a dedicated scenario.

    Args:
        scenario: The scenario name (e.g. "first time appointment").
        scenario_type: The sub-type (e.g. "personal", "family", or "" for default).
        optional_data: Optional dictionary containing custom patient/appointment fields.

    Returns:
        The complete standalone system prompt string, or None if scenario is not dedicated.
    """
    norm_scenario = normalize_scenario_name(scenario)
    norm_type = normalize_scenario_type(scenario_type)
    data = optional_data or {}

    if norm_scenario in ["first_time_appointment", "first_time_appointments"]:
        # Default / Personal workflow
        if norm_type in ["", "personal", "self", "individual"]:
            if data:
                return get_personal_first_time_appointment_prompt(**data)
            return FIRST_TIME_APPOINTMENT_SELF_SYSTEM_PROMPT.strip()

        elif norm_type in ["family", "children"]:
            # Family workflow placeholder (to be wired when family prompt is added)
            raise NotImplementedError(
                f"Family workflow for '{scenario}' is being designed next."
            )
        else:
            raise ValueError(
                f"Unknown type '{scenario_type}' for scenario '{scenario}'. "
                f"Supported types: '', 'personal', 'self', 'individual', 'family'."
            )

    return None
