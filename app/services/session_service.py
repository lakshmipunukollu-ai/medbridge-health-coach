"""Session service - business logic for coaching sessions."""

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session as DBSession

from app.models.session import Session
from app.models.patient import Patient
from app.agent.workflow import run_workflow
from app.agent.safety_guard import check_safety
from app.services.patient_service import (
    transition_phase,
    reset_unanswered,
    create_alert,
)


def create_or_continue_session(
    db: DBSession, patient: Patient, user_message: str
) -> dict:
    """
    Create or continue a coaching session.

    This is the main entry point for patient interactions:
    1. Builds the patient state
    2. Runs the LangGraph workflow
    3. Updates the database with results
    4. Returns the session response
    """
    # Check consent first
    if not patient.consent_verified:
        return {
            "session_id": None,
            "patient_id": patient.id,
            "phase": patient.phase,
            "response": "Unable to interact — patient consent has not been verified.",
            "safety_flagged": False,
        }

    # Build state from patient record
    state = {
        "patient_id": patient.id,
        "phase": patient.phase,
        "messages": [],
        "goal": patient.goal,
        "unanswered_count": patient.unanswered_count,
        "last_interaction": (
            patient.last_interaction.isoformat() if patient.last_interaction else None
        ),
        "consent_verified": patient.consent_verified,
        "program_summary": patient.program_summary,
        "user_message": user_message,
        "agent_response": "",
        "safety_flagged": False,
    }

    # Load existing session messages
    existing_session = (
        db.query(Session)
        .filter(Session.patient_id == patient.id)
        .order_by(Session.created_at.desc())
        .first()
    )
    if existing_session:
        state["messages"] = existing_session.messages or []

    # Run the workflow
    result = run_workflow(state)

    # Handle phase transition if the workflow changed it
    new_phase = result.get("phase", patient.phase)
    if new_phase != patient.phase:
        transition_phase(db, patient, new_phase, f"Workflow transition from {patient.phase}")

    # Update goal if set during workflow
    new_goal = result.get("goal")
    if new_goal and new_goal != patient.goal:
        patient.goal = new_goal
        db.commit()

    # Reset unanswered count since patient responded
    if patient.unanswered_count > 0:
        reset_unanswered(db, patient)

    # Update last interaction
    patient.last_interaction = datetime.utcnow()
    db.commit()

    # Create alert if safety guard flagged
    if result.get("safety_flagged"):
        safety_result = check_safety(user_message)
        if safety_result.alert_sent:
            create_alert(
                db,
                patient.id,
                safety_result.alert_type or "safety_concern",
                user_message,
            )

    # Create or update session record
    session = Session(
        patient_id=patient.id,
        phase=new_phase,
        messages=result.get("messages", []),
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return {
        "session_id": session.id,
        "patient_id": patient.id,
        "phase": new_phase,
        "response": result.get("agent_response", ""),
        "safety_flagged": result.get("safety_flagged", False),
    }


def get_session_count(db: DBSession, patient_id: str) -> int:
    """Get total number of sessions for a patient."""
    return db.query(Session).filter(Session.patient_id == patient_id).count()
