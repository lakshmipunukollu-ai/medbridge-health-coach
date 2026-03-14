"""Re-engaging phase handler - warm re-engagement after silence."""

from app.agent.state import PatientState


def handle_re_engaging(state: PatientState) -> dict:
    """
    Handle re-engaging phase interactions.
    Warm re-engagement after patient has been unresponsive.
    """
    user_message = state.get("user_message", "")
    messages = list(state.get("messages", []))
    unanswered = state.get("unanswered_count", 1)

    if user_message:
        # Patient responded - move back to active
        response = (
            "Welcome back! It's great to hear from you. "
            "Your exercise program is still here waiting for you. "
            "Would you like to ease back in with a lighter routine today?"
        )
        messages.append({"role": "user", "content": user_message})
        messages.append({"role": "assistant", "content": response})
        return {
            "agent_response": response,
            "messages": messages,
            "unanswered_count": 0,
            "phase": "ACTIVE",
        }
    else:
        # Generating a check-in message (from webhook)
        if unanswered == 1:
            response = (
                "Hi there! I noticed we haven't chatted in a bit. "
                "How are your exercises going? Even a quick update helps me support you better."
            )
        else:
            response = (
                "Just checking in — I'm still here whenever you're ready to continue "
                "your exercise program. No pressure, just know your goals are waiting for you."
            )

        messages.append({"role": "assistant", "content": response})
        return {
            "agent_response": response,
            "messages": messages,
        }
