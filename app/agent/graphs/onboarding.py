"""Onboarding phase handler - welcomes patient and collects goals."""

from app.agent.state import PatientState


def handle_onboarding(state: PatientState) -> dict:
    """
    Handle onboarding phase interactions.
    Welcomes the patient and helps them set their coaching goal.
    """
    user_message = state.get("user_message", "")
    messages = list(state.get("messages", []))
    goal = state.get("goal")

    # Check if user is setting a goal
    goal_keywords = ["goal", "want to", "like to", "hope to", "plan to", "my goal"]
    is_setting_goal = any(kw in user_message.lower() for kw in goal_keywords)

    if not messages:
        # First interaction - welcome
        response = (
            "Welcome to Medbridge Health Coach! I'm here to help you stay on track "
            "with your home exercise program between clinical visits. "
            "To get started, could you tell me what your main goal is for your "
            "exercise program? For example: 'My goal is to improve my shoulder mobility.'"
        )
    elif is_setting_goal and not goal:
        # Patient is setting their goal
        goal = user_message
        response = (
            f"That's a great goal! I've noted that down. "
            f"I'll help you stay motivated and track your progress. "
            f"Let's get started with your exercise program!"
        )
        messages.append({"role": "user", "content": user_message})
        messages.append({"role": "assistant", "content": response})
        return {
            "agent_response": response,
            "messages": messages,
            "goal": goal,
            "phase": "ACTIVE",
        }
    else:
        response = (
            "I'd love to help you get started! Could you share your main goal "
            "for your exercise program? This helps me personalize your coaching experience."
        )

    messages.append({"role": "user", "content": user_message})
    messages.append({"role": "assistant", "content": response})

    return {
        "agent_response": response,
        "messages": messages,
    }
