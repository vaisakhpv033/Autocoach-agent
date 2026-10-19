"""Unit tests for Dental Front Desk personas and rubrics."""

from autocoach.metadata import SessionMetadata
from autocoach.personas.presets import get_preset_persona, get_preset_rubric
from autocoach.prompt_engine import build_system_prompt


def test_dental_personas_registered():
    """Verify all dental scenarios exist in the persona registry."""
    scenarios = [
        "dental_scheduling",
        "dental_price_shopper",
        "dental_cost_objection",
        "dental_frontdesk_compliance",
        "dental_doctor_inquiry",
        "dental_clinical_objections",
        "dental_xray_objection",
        "dental_emergency_triage",
        "dental_toothache",
        "dental_insurance_copay",
        "dental_perio_copay",
    ]
    for s in scenarios:
        persona = get_preset_persona(s)
        assert persona is not None
        assert persona.id != "default_general_customer"


def test_dental_price_shopper_prompt():
    meta = SessionMetadata(scenario="dental_price_shopper", difficulty="hard")
    prompt = build_system_prompt(meta)

    assert "Michael Reynolds" in prompt
    assert "root canal" in prompt.lower()
    assert "prepayment" in prompt.lower()
    assert "Difficulty Tier: HARD" in prompt


def test_dental_frontdesk_compliance_prompt():
    meta = SessionMetadata(scenario="dental_frontdesk_compliance", difficulty="hard")
    prompt = build_system_prompt(meta)

    assert "Brenda Vance" in prompt
    assert "Dr. Scott" in prompt
    assert "answering service" in prompt.lower() or "remotely" in prompt.lower()


def test_dental_emergency_triage_prompt():
    meta = SessionMetadata(scenario="dental_emergency_triage", difficulty="hard")
    prompt = build_system_prompt(meta)

    assert "Rachel Green" in prompt
    assert "throbbing" in prompt.lower() or "toothache" in prompt.lower()


def test_dental_rubric_retrieval():
    rubric = get_preset_rubric("dental_price_shopper")
    assert rubric is not None
    assert rubric["track"] == "Track 1: Price Shopper & Financials"
    assert len(rubric["required_protocols"]) > 0


def test_custom_scenario_rubric_optional():
    # Built-in scenario has a rubric
    assert get_preset_rubric("dental_clinical_objections") is not None

    # Custom scenario has no preset rubric -> returns None
    assert get_preset_rubric("unregistered_custom_scenario_xyz") is None


def test_custom_rubric_override_in_metadata():
    custom_rubric = [{"rule": "Must smile", "required": True}]
    meta = SessionMetadata(
        scenario="custom_roleplay",
        evaluation_rubric=custom_rubric,
    )
    assert meta.evaluation_rubric == custom_rubric
