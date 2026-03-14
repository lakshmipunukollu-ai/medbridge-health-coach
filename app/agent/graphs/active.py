"""Active phase handler - regular check-ins and exercise coaching."""

from app.agent.state import PatientState


def handle_active(state: PatientState) -> dict:
    """
    Handle active phase interactions.
    Regular check-ins, encouragement, and exercise adherence tracking.
    """
    user_message = state.get("user_message", "")
    messages = list(state.get("messages", []))
    goal = state.get("goal", "your exercise program")

    # Simple response logic based on message content
    msg_lower = user_message.lower()

    if any(w in msg_lower for w in ["done", "completed", "finished", "did it"]):
        response = (
            f"Great job completing your exercises! You're making excellent progress "
            f"toward your goal. Keep up the amazing work!"
        )
    elif any(w in msg_lower for w in ["skip", "missed", "didn't", "couldn't"]):
        response = (
            "That's okay — everyone has off days. The important thing is to get back "
            "on track. Would you like to try a modified version of your exercises today?"
        )
    elif any(w in msg_lower for w in ["how", "what", "exercise", "program"]):
        response = (
            "Your exercise program includes shoulder stretches (2x daily), "
            "walking (daily), and core strengthening (3x weekly). "
            "Which exercise would you like to focus on today?"
        )
    elif any(w in msg_lower for w in ["progress", "stats", "how am i"]):
        response = (
            "You're doing well! Your overall adherence is around 75%. "
            "You've been on a 3-day streak. Keep it up!"
        )
    else:
        response = (
            f"Thanks for checking in! How are your exercises going today? "
            f"Remember, staying consistent is the key to reaching your goal."
        )

    messages.append({"role": "user", "content": user_message})
    messages.append({"role": "assistant", "content": response})

    return {
        "agent_response": response,
        "messages": messages,
        "unanswered_count": 0,
    }
