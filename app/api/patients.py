"""Patient management and session endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.patient import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    PatientSummaryResponse,
    PhaseTransitionResponse,
    AlertResponse,
)
from app.schemas.session import SessionMessageRequest, SessionResponse
from app.services.patient_service import (
    create_patient,
    get_patient,
    update_patient,
    get_phase_history,
    get_alerts,
)
from app.services.session_service import create_or_continue_session, get_session_count

router = APIRouter()


@router.post("/patients", response_model=PatientResponse, status_code=201)
def create_new_patient(data: PatientCreate, db: Session = Depends(get_db)):
    """Create a new patient in PENDING phase."""
    patient = create_patient(
        db=db,
        name=data.name,
        email=data.email,
        external_id=data.external_id,
        consent_verified=data.consent_verified,
    )
    return patient


@router.get("/patients/{patient_id}", response_model=PatientResponse)
def get_patient_details(patient_id: str, db: Session = Depends(get_db)):
    """Get patient details by ID."""
    patient = get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.patch("/patients/{patient_id}", response_model=PatientResponse)
def update_patient_details(
    patient_id: str, data: PatientUpdate, db: Session = Depends(get_db)
):
    """Update patient fields."""
    patient = update_patient(
        db,
        patient_id,
        name=data.name,
        email=data.email,
        consent_verified=data.consent_verified,
        goal=data.goal,
        program_summary=data.program_summary,
    )
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.post("/patients/{patient_id}/sessions", response_model=SessionResponse)
def create_session(
    patient_id: str,
    data: SessionMessageRequest,
    db: Session = Depends(get_db),
):
    """Start or continue a coaching session."""
    patient = get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    result = create_or_continue_session(db, patient, data.message)
    return SessionResponse(
        session_id=result["session_id"] or "",
        patient_id=result["patient_id"],
        phase=result["phase"],
        response=result["response"],
        safety_flagged=result["safety_flagged"],
    )


@router.get("/patients/{patient_id}/summary", response_model=PatientSummaryResponse)
def get_patient_summary(patient_id: str, db: Session = Depends(get_db)):
    """Get patient engagement summary for clinicians."""
    patient = get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    phase_history = get_phase_history(db, patient_id)
    alerts = get_alerts(db, patient_id)
    total_sessions = get_session_count(db, patient_id)

    return PatientSummaryResponse(
        patient_id=patient.id,
        name=patient.name,
        current_phase=patient.phase,
        goal=patient.goal,
        total_sessions=total_sessions,
        unanswered_count=patient.unanswered_count,
        last_interaction=patient.last_interaction,
        phase_history=[
            PhaseTransitionResponse(
                from_phase=log.from_phase,
                to_phase=log.to_phase,
                reason=log.reason,
                created_at=log.created_at,
            )
            for log in phase_history
        ],
        alerts=[
            AlertResponse(
                id=alert.id,
                alert_type=alert.alert_type,
                message=alert.message,
                resolved=alert.resolved,
                created_at=alert.created_at,
            )
            for alert in alerts
        ],
    )
