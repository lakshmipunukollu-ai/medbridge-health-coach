"""
Main LangGraph Workflow for the Health Coach Agent.

This builds the state graph with deterministic routing and safety guard.
Phase transitions are APPLICATION LOGIC, not LLM decisions.
"""

from app.agent.state import PatientState
from app.agent.router import route_to_phase
from app.agent.safety_guard import check_safety
from app.agent.graphs.onboarding import handle_onboarding
from app.agent.graphs.active import handle_active
from app.agent.graphs.re_engaging import handle_re_engaging
from app.agent.graphs.dormant import handle_dormant


def safety_guard_node(state: PatientState) -> dict:
    """
    Safety guard node - ALL outputs pass through this before delivery.
    This is non-negotiable and runs unconditionally.
    """
    response = state.get("agent_response", "")
    user_message = state.get("user_message", "")

    # Check user message for safety concerns
    user_result = check_safety(user_message)
    if not user_result.safe:
        return {
            "agent_response": user_result.override_response,
            "safety_flagged": True,
        }

    # Check agent response for safety concerns
    agent_result = check_safety(response)
    if not agent_result.safe:
        return {
            "agent_response": agent_result.override_response,
            "safety_flagged": True,
        }

    return {
        "safety_flagged": False,
    }


def no_consent_node(state: PatientState) -> dict:
    """Handle the case where consent is not verified."""
    return {
        "agent_response": "Unable to interact — patient consent has not been verified.",
        "safety_flagged": False,
    }


def run_workflow(state: PatientState) -> PatientState:
    """
    Execute the health coach workflow for a given patient state.

    This is the main entry point that:
    1. Routes to the correct phase handler (deterministic)
    2. Runs the phase handler
    3. Passes the result through the safety guard

    Returns the updated state.
    """
    # Step 1: Deterministic routing
    target_phase = route_to_phase(state)

    # Step 2: Run phase handler
    if target_phase == "end":
        result = no_consent_node(state)
    elif target_phase == "onboarding":
        result = handle_onboarding(state)
    elif target_phase == "active":
        result = handle_active(state)
    elif target_phase == "re_engaging":
        result = handle_re_engaging(state)
    elif target_phase == "dormant":
        result = handle_dormant(state)
    else:
        # Fallback to active
        result = handle_active(state)

    # Apply phase handler results to state
    updated_state = {**state, **result}

    # Step 3: Safety guard (NON-NEGOTIABLE - runs on every response)
    safety_result = safety_guard_node(updated_state)
    updated_state.update(safety_result)

    return updated_state
