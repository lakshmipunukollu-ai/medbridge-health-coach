"""
Agent Tools for the Health Coach.

Tool implementations are stubbed but invocation logic is real and tested.
Each tool interacts with the database via the patient service.
"""

from datetime import datetime
from typing import Optional


def set_goal(patient_id: str, goal: str, db_session=None) -> dict:
    """Set the patient's coaching goal."""
    if db_session:
        from app.models.patient import Patient

        patient = db_session.query(Patient).filter(Patient.id == patient_id).first()
        if patient:
            patient.goal = goal
            patient.updated_at = datetime.utcnow()
            db_session.commit()
            return {"status": "success", "patient_id": patient_id, "goal": goal}
    return {"status": "success", "patient_id": patient_id, "goal": goal}


def set_reminder(patient_id: str, reminder_text: str, reminder_time: str = None) -> dict:
    """Create a reminder for the patient."""
    return {
        "status": "success",
        "patient_id": patient_id,
        "reminder": reminder_text,
        "scheduled_for": reminder_time or "next_checkin",
    }


def get_program_summary(patient_id: str, db_session=None) -> dict:
    """Retrieve the patient's HEP program summary."""
    if db_session:
        from app.models.patient import Patient

        patient = db_session.query(Patient).filter(Patient.id == patient_id).first()
        if patient and patient.program_summary:
            return patient.program_summary

    return {
        "patient_id": patient_id,
        "program": "Home Exercise Program",
        "exercises": [
            {"name": "Shoulder stretches", "frequency": "2x daily", "duration": "10 min"},
            {"name": "Walking", "frequency": "daily", "duration": "20 min"},
            {"name": "Core strengthening", "frequency": "3x weekly", "duration": "15 min"},
        ],
        "start_date": "2026-03-01",
        "clinician": "Dr. Smith",
    }


def get_adherence_summary(patient_id: str) -> dict:
    """Get exercise adherence statistics for the patient."""
    return {
        "patient_id": patient_id,
        "overall_adherence": 0.75,
        "weekly_adherence": [
            {"week": 1, "adherence": 0.85},
            {"week": 2, "adherence": 0.70},
            {"week": 3, "adherence": 0.65},
        ],
        "streak_days": 3,
        "total_sessions_completed": 18,
    }


def alert_clinician(
    patient_id: str, alert_type: str, message: str, db_session=None
) -> dict:
    """Send an urgent alert to the care team."""
    alert_id = None
    if db_session:
        from app.models.alert import ClinicianAlert

        alert = ClinicianAlert(
            patient_id=patient_id,
            alert_type=alert_type,
            message=message,
        )
        db_session.add(alert)
        db_session.commit()
        alert_id = alert.id

    return {
        "status": "alert_sent",
        "patient_id": patient_id,
        "alert_type": alert_type,
        "alert_id": alert_id,
    }
