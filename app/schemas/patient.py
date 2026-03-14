from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class PatientCreate(BaseModel):
    name: str
    email: Optional[str] = None
    external_id: Optional[str] = None
    consent_verified: bool = False


class PatientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    consent_verified: Optional[bool] = None
    goal: Optional[str] = None
    program_summary: Optional[dict] = None


class PatientResponse(BaseModel):
    id: str
    external_id: Optional[str] = None
    name: str
    email: Optional[str] = None
    phase: str
    goal: Optional[str] = None
    consent_verified: bool
    unanswered_count: int
    last_interaction: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PhaseTransitionResponse(BaseModel):
    from_phase: str
    to_phase: str
    reason: str
    created_at: datetime

    class Config:
        from_attributes = True


class AlertResponse(BaseModel):
    id: str
    alert_type: str
    message: str
    resolved: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PatientSummaryResponse(BaseModel):
    patient_id: str
    name: str
    current_phase: str
    goal: Optional[str] = None
    total_sessions: int
    unanswered_count: int
    last_interaction: Optional[datetime] = None
    phase_history: List[PhaseTransitionResponse]
    alerts: List[AlertResponse]
