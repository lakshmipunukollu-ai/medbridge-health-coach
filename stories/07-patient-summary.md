# Story 7: Patient Summary for Clinicians

## Description
As a clinician, I can view a patient's engagement summary to understand their coaching progress.

## Acceptance Criteria
- GET /patients/{id}/summary returns comprehensive engagement data
- Includes: current phase, goal, total sessions, unanswered count
- Includes: last interaction timestamp
- Includes: phase transition history
- Includes: active alerts
- Invalid patient_id returns 404

## Technical Notes
- Aggregates data from Patient, Session, PhaseTransitionLog, and ClinicianAlert tables
- Read-only endpoint
