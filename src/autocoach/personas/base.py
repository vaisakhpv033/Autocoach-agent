"""Persona definition schema for AutoCoach customer simulation."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CustomerPersona:
    """Structure representing a simulated caller / customer profile and behavior."""

    id: str
    name: str
    age: int
    gender: str  # "male", "female"
    occupation: str
    location: str
    scenario: str
    call_reason: str
    background: str

    # Personality and Behavioral Dynamics
    temperament: str = "neutral"  # e.g., "angry", "skeptical", "hurried", "polite", "confused"
    difficulty: str = "medium"  # "easy", "medium", "hard", "nightmare"

    # Context & Objectives
    account_context: str = ""
    primary_objectives: list[str] = field(default_factory=list)
    objections: list[str] = field(default_factory=list)

    # Conversational Behavior & Speech Pacing
    speech_rules: list[str] = field(default_factory=list)
    human_imperfections: list[str] = field(default_factory=list)

    # Dynamic Training Traps & Triggers
    compliance_traps: list[str] = field(default_factory=list)
    deescalation_triggers: list[str] = field(default_factory=list)
    escalation_triggers: list[str] = field(default_factory=list)

    # Termination Conditions
    call_end_conditions: list[str] = field(default_factory=list)
    bad_behavior_escalation: str = ""
    normal_ending: str = ""
