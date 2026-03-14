from typing import Optional

from pydantic import BaseModel


class ScheduleWebhookRequest(BaseModel):
    patient_id: str
    trigger_type: str = "scheduled_checkin"


class ScheduleWebhookResponse(BaseModel):
    status: str
    patient_id: str
    action_taken: str


class ClinicianAlertWebhookRequest(BaseModel):
    patient_id: str
    alert_type: str
    message: str
    source: str = "safety_guard"


class ClinicianAlertWebhookResponse(BaseModel):
    status: str
    alert_id: str
