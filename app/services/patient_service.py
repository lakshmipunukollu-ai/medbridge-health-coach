"""Patient service - business logic for patient management."""

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.models.phase_log import PhaseTransitionLog
from app.models.alert import ClinicianAlert


def create_patient(
    db: Session,
    name: str,
    email: Optional[str] = None,
    external_id: Optional[str] = None,
    consent_verified: bool = False,
) -> Patient:
    """Create a new patient in PENDING phase."""
    patient = Patient(
        name=name,
        email=email,
        external_id=external_id,
        consent_verified=consent_verified,
        phase="PENDING",
        unanswered_count=0,
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def get_patient(db: Session, patient_id: str) -> Optional[Patient]:
    """Get a patient by ID."""
    return db.query(Patient).filter(Patient.id == patient_id).first()


def update_patient(
    db: Session, patient_id: str, **kwargs
) -> Optional[Patient]:
    """Update patient fields."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        return None

    for key, value in kwargs.items():
        if value is not None and hasattr(patient, key):
            setattr(patient, key, value)

    patient.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(patient)
    return patient


def transition_phase(
    db: Session, patient: Patient, new_phase: str, reason: str
) -> Patient:
    """Transition a patient to a new phase and log it."""
    old_phase = patient.phase
    if old_phase == new_phase:
        return patient

    log = PhaseTransitionLog(
        patient_id=patient.id,
        from_phase=old_phase,
        to_phase=new_phase,
        reason=reason,
    )
    db.add(log)

    patient.phase = new_phase
    patient.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(patient)
    return patient


def increment_unanswered(db: Session, patient: Patient) -> Patient:
    """Increment the unanswered count for a patient."""
    patient.unanswered_count += 1
    patient.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(patient)
    return patient


def reset_unanswered(db: Session, patient: Patient) -> Patient:
    """Reset the unanswered count to 0."""
    patient.unanswered_count = 0
    patient.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(patient)
    return patient


def create_alert(
    db: Session, patient_id: str, alert_type: str, message: str
) -> ClinicianAlert:
    """Create a clinician alert."""
    alert = ClinicianAlert(
        patient_id=patient_id,
        alert_type=alert_type,
        message=message,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def get_phase_history(db: Session, patient_id: str) -> list:
    """Get phase transition history for a patient."""
    return (
        db.query(PhaseTransitionLog)
        .filter(PhaseTransitionLog.patient_id == patient_id)
        .order_by(PhaseTransitionLog.created_at.asc())
        .all()
    )


def get_alerts(db: Session, patient_id: str) -> list:
    """Get alerts for a patient."""
    return (
        db.query(ClinicianAlert)
        .filter(ClinicianAlert.patient_id == patient_id)
        .order_by(ClinicianAlert.created_at.desc())
        .all()
    )
