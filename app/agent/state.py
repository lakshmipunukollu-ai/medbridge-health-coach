from typing import TypedDict, Literal, Optional, List


class PatientState(TypedDict):
    """State object for the LangGraph patient coaching workflow."""

    patient_id: str
    phase: Literal["PENDING", "ONBOARDING", "ACTIVE", "RE_ENGAGING", "DORMANT"]
    messages: List[dict]
    goal: Optional[str]
    unanswered_count: int
    last_interaction: Optional[str]  # ISO datetime
    consent_verified: bool
    program_summary: Optional[dict]
    user_message: str
    agent_response: str
    safety_flagged: bool
