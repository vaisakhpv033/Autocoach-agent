"""AutoCoach Scenario Definitions and Dedicated Prompts."""

from autocoach.scenarios.registry import (
    is_dedicated_scenario,
    get_dedicated_system_prompt,
    get_scenario_metadata_defaults,
    normalize_scenario_name,
    normalize_scenario_type,
)

__all__ = [
    "is_dedicated_scenario",
    "get_dedicated_system_prompt",
    "get_scenario_metadata_defaults",
    "normalize_scenario_name",
    "normalize_scenario_type",
]
