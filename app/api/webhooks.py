"""Webhook endpoints for external integrations."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.webhook import (
    ScheduleWebhookRequest,
    ScheduleWebhookResponse,
    ClinicianAlertWebhookRequest,
    ClinicianAlertWebhookResponse,
)
from app.services.patient_service import (
    get_patient,
    increment_unanswered,
    transition_phase,
    create_alert,
)
from app.agent.router import route_to_phase

router = APIRouter()


@router.post("/webhooks/schedule", response_model=ScheduleWebhookResponse)
def handle_schedule_webhook(
    data: ScheduleWebhookRequest, db: Session = Depends(get_db)
):
    """
    Handle scheduled check-in webhook.
    Called by external scheduler to trigger time-based check-ins.
    Increments unanswered_count and handles phase transitions.
    """
    patient = get_patient(db, data.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    if not patient.consent_verified:
        return ScheduleWebhookResponse(
            status="skipped",
            patient_id=patient.id,
            action_taken="no_consent",
        )

    # Increment unanswered count
    patient = increment_unanswered(db, patient)

    # Determine if phase transition is needed
    action_taken = "checkin_sent"

    if patient.unanswered_count >= 3 and patient.phase != "DORMANT":
        transition_phase(db, patient, "DORMANT", "3+ unanswered check-ins")
        action_taken = "moved_to_dormant"
    elif patient.unanswered_count >= 1 and patient.phase == "ACTIVE":
        transition_phase(db, patient, "RE_ENGAGING", "Unanswered check-in")
        action_taken = "moved_to_re_engaging"

    return ScheduleWebhookResponse(
        status="processed",
        patient_id=patient.id,
        action_taken=action_taken,
    )


@router.post("/webhooks/clinician-alert", response_model=ClinicianAlertWebhookResponse)
def handle_clinician_alert_webhook(
    data: ClinicianAlertWebhookRequest, db: Session = Depends(get_db)
):
    """
    Handle clinician alert webhook.
    Receives and stores urgent escalation alerts.
    """
    patient = get_patient(db, data.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    alert = create_alert(
        db=db,
        patient_id=data.patient_id,
        alert_type=data.alert_type,
        message=data.message,
    )

    return ClinicianAlertWebhookResponse(
        status="received",
        alert_id=alert.id,
    )
