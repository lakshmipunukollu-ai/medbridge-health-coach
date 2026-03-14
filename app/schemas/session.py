from typing import Optional

from pydantic import BaseModel


class SessionMessageRequest(BaseModel):
    message: str


class SessionResponse(BaseModel):
    session_id: str
    patient_id: str
    phase: str
    response: str
    safety_flagged: bool

    class Config:
        from_attributes = True
