"""Simulation tools for AutoCoach agent."""

from typing import Callable, Optional
from livekit.agents.beta.tools import EndCallTool


def build_simulation_tools(
    on_tool_called: Optional[Callable] = None,
    delete_room: bool = True,
) -> list:
    """Builds standard tools available to the simulated customer during the call.
    
    Includes the EndCallTool which allows the simulated customer to hang up when:
    1. The scenario naturally completes (after saying goodbye)
    2. The trainee representative is rude, abusive, or unresponsive
    """
    end_call = EndCallTool(
        extra_description=(
            "Call this tool to hang up and terminate the call. You should only do this when "
            "the conversation has naturally concluded (e.g., questions answered and goodbye exchanged) "
            "OR if the representative becomes rude, dismissive, or completely unresponsive."
        ),
        delete_room=delete_room,
        end_instructions="say goodbye to the representative briefly before hanging up",
        on_tool_called=on_tool_called,
    )

    return [end_call]
