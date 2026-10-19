"""Persona registry and built-in preset scenarios for AutoCoach."""

from typing import Any, Optional
from autocoach.personas.base import CustomerPersona

# General Fallback Persona used when no specific scenario or custom instructions are given
DEFAULT_PERSONA = CustomerPersona(
    id="default_general_customer",
    name="Alex Morgan",
    age=34,
    gender="male",
    occupation="Account Manager",
    location="Chicago, IL",
    scenario="general_support",
    call_reason="Inquiring about recent service billing and scheduling clarification",
    background=(
        "Busy professional who called during a quick break. Values direct, concise answers. "
        "Has been a loyal customer for 2 years but recently noticed conflicting details on their account."
    ),
    temperament="slightly hurried but courteous",
    difficulty="medium",
    account_context="Active account #48291, billed monthly, last invoice had an unfamiliar charge.",
    primary_objectives=[
        "Understand why the recent invoice is higher than usual",
        "Confirm the next scheduled service appointment time",
        "Ensure their contact information is properly updated",
    ],
    objections=[
        "I was told last month this fee would be waived.",
        "Can't you just fix this right now without transferring me?",
        "Why wasn't I notified before this charge went through?",
    ],
    speech_rules=[
        "Keep responses between 3 and 15 words per turn.",
        "Use natural pauses ('...') and occasional fillers ('um', 'well', 'let me see').",
        "Wait for the representative to greet first before explaining your issue.",
        "Never recite full account details or long paragraphs unprompted.",
    ],
    human_imperfections=[
        "Occasionally interrupts if the representative pauses for too long.",
        "Asks for clarification if the representative uses internal jargon.",
        "Takes a couple seconds to locate invoice numbers when asked.",
    ],
    compliance_traps=[
        "Attempt to see if the representative shares sensitive account info without verifying your identity.",
        "Ask if you can just bypass security verification because you're in a hurry.",
    ],
    deescalation_triggers=[
        "Representative acknowledges the billing frustration with genuine empathy.",
        "Representative provides a clear, transparent breakdown of the charges.",
    ],
    escalation_triggers=[
        "Representative is dismissive, robotic, or repeats script verbatim.",
        "Representative places caller on hold without asking permission.",
    ],
    call_end_conditions=[
        "The charge is explained or credited.",
        "The appointment time is confirmed.",
    ],
    bad_behavior_escalation=(
        "If the representative is rude, dismissive, or refuses to help, warn them once. "
        "If it happens again, state 'I will follow up with your manager' and call EndCallTool."
    ),
    normal_ending=(
        "Once your questions are satisfactorily answered, say 'Thank you, that clears it up. "
        "Have a good day!' and call EndCallTool."
    ),
)

# Registry of built-in personas
PERSONA_REGISTRY: dict[str, CustomerPersona] = {
    "default": DEFAULT_PERSONA,
    "general": DEFAULT_PERSONA,
}

# Registry of optional built-in evaluation rubrics
RUBRIC_REGISTRY: dict[str, dict[str, Any]] = {}


def register_persona(
    persona: CustomerPersona,
    alias: Optional[str] = None,
    rubric: Optional[dict[str, Any]] = None,
) -> None:
    """Registers a new persona and optional evaluation rubric into the runtime registry."""
    clean_id = persona.id.lower()
    clean_scenario = persona.scenario.lower()
    PERSONA_REGISTRY[clean_id] = persona
    PERSONA_REGISTRY[clean_scenario] = persona

    if alias:
        clean_alias = alias.lower()
        PERSONA_REGISTRY[clean_alias] = persona
        if rubric:
            RUBRIC_REGISTRY[clean_alias] = rubric

    if rubric:
        RUBRIC_REGISTRY[clean_id] = rubric
        RUBRIC_REGISTRY[clean_scenario] = rubric


def get_preset_persona(scenario_name: Optional[str]) -> CustomerPersona:
    """Retrieves a persona by scenario/ID, falling back to DEFAULT_PERSONA."""
    if not scenario_name:
        return DEFAULT_PERSONA
    clean = scenario_name.strip().lower()
    return PERSONA_REGISTRY.get(clean, DEFAULT_PERSONA)


def get_preset_rubric(scenario_name: Optional[str]) -> Optional[dict[str, Any]]:
    """Retrieves an optional evaluation rubric for a preset scenario, or None if not registered."""
    if not scenario_name:
        return None
    clean = scenario_name.strip().lower()
    return RUBRIC_REGISTRY.get(clean)


# Lazy registration of built-in dental personas & rubrics
def _init_dental_presets() -> None:
    try:
        from autocoach.personas.dental.scenarios import ALL_DENTAL_PERSONAS
        from autocoach.personas.dental.rubrics import DENTAL_RUBRIC_REGISTRY

        for key, persona in ALL_DENTAL_PERSONAS.items():
            rubric = DENTAL_RUBRIC_REGISTRY.get(key)
            register_persona(persona, alias=key, rubric=rubric)
    except ImportError:
        pass


_init_dental_presets()
