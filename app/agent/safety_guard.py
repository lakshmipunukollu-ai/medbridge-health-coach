"""
Safety Guard - NON-NEGOTIABLE component.

EVERY message the agent generates passes through this before delivery.
This is not optional. This is not skippable. This runs unconditionally.

Medbridge is a clinical company. Clinical content that crosses the line
creates liability. The safety guard is the most important component.
"""

from dataclasses import dataclass
from typing import Optional


CLINICAL_TRIGGERS = [
    "symptoms",
    "medication",
    "diagnosis",
    "treatment",
    "pain",
    "injury",
    "side effect",
    "dosage",
    "doctor",
    "emergency",
]

MENTAL_HEALTH_TRIGGERS = [
    "suicidal",
    "self-harm",
    "hopeless",
    "can't go on",
    "end it",
    "hurting myself",
    "depressed",
    "anxious",
    "crisis",
]

MENTAL_HEALTH_SAFE_RESPONSE = (
    "I hear that you're going through something really difficult right now. "
    "Please reach out to your care team or call 988 (Suicide & Crisis Lifeline) "
    "if you need immediate support. Your clinician has been notified."
)

CLINICAL_REDIRECT_RESPONSE = (
    "That sounds like something important to discuss with your care team directly. "
    "Please reach out to your clinician — they're the right person to help with this."
)


@dataclass
class GuardResult:
    safe: bool
    override_response: Optional[str] = None
    alert_sent: bool = False
    alert_type: Optional[str] = None


def check_safety(message: str) -> GuardResult:
    """
    Check a message for safety concerns.
    Uses keyword matching (not LLM-based) for reliability and zero-latency.

    Args:
        message: The message to check (either user input or agent response)

    Returns:
        GuardResult with safety assessment
    """
    message_lower = message.lower()

    # Mental health crisis -> immediate clinician alert, safe response
    if any(trigger in message_lower for trigger in MENTAL_HEALTH_TRIGGERS):
        return GuardResult(
            safe=False,
            override_response=MENTAL_HEALTH_SAFE_RESPONSE,
            alert_sent=True,
            alert_type="mental_health_crisis",
        )

    # Clinical content -> redirect to care team
    if any(trigger in message_lower for trigger in CLINICAL_TRIGGERS):
        return GuardResult(
            safe=False,
            override_response=CLINICAL_REDIRECT_RESPONSE,
            alert_sent=False,
            alert_type="clinical_content",
        )

    return GuardResult(safe=True)
