"""
Deterministic Phase Router.

CRITICAL: Phase transitions are APPLICATION LOGIC, not LLM decisions.
The LLM handles conversation. The app handles state transitions.
This prevents the LLM from accidentally moving patients to wrong phases.
"""

from app.agent.state import PatientState


def route_to_phase(state: PatientState) -> str:
    """
    Deterministic routing function that decides which phase handler to use.

    Rules:
    1. No consent -> END (no interaction allowed)
    2. PENDING -> onboarding
    3. ONBOARDING with goal set -> active
    4. unanswered_count >= 3 -> dormant
    5. unanswered_count >= 1 -> re_engaging
    6. Otherwise -> current phase handler
    """
    if not state.get("consent_verified", False):
        return "end"

    phase = state.get("phase", "PENDING")
    unanswered = state.get("unanswered_count", 0)
    goal = state.get("goal")

    if phase == "PENDING":
        return "onboarding"
    elif phase == "ONBOARDING" and goal:
        return "active"
    elif unanswered >= 3:
        return "dormant"
    elif unanswered >= 1:
        return "re_engaging"
    else:
        return phase.lower()
