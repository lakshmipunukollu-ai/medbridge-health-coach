"""Dormant phase handler - minimal contact after extended silence."""

from app.agent.state import PatientState


def handle_dormant(state: PatientState) -> dict:
    """
    Handle dormant phase interactions.
    Minimal contact - patient has been unresponsive for extended period.
    """
    user_message = state.get("user_message", "")
    messages = list(state.get("messages", []))

    if user_message:
        # Patient reached out - move to re-engaging
        response = (
            "It's wonderful to hear from you! I'm glad you're thinking about "
            "your exercise program. There's no judgment here — let's start fresh. "
            "Would you like to review your current program or set a new goal?"
        )
        messages.append({"role": "user", "content": user_message})
        messages.append({"role": "assistant", "content": response})
        return {
            "agent_response": response,
            "messages": messages,
            "unanswered_count": 0,
            "phase": "RE_ENGAGING",
        }
    else:
        # Periodic minimal contact (from webhook)
        response = (
            "Your health coach is still here for you whenever you're ready. "
            "Your exercise program is available anytime."
        )
        messages.append({"role": "assistant", "content": response})
        return {
            "agent_response": response,
            "messages": messages,
        }
