# Story 1: Patient Management

## Description
As a clinician, I need to create and manage patient records so that patients can be enrolled in the health coaching program.

## Acceptance Criteria
- POST /patients creates a new patient in PENDING phase
- GET /patients/{id} returns patient details
- PATCH /patients/{id} allows updating patient fields (especially consent_verified)
- Patient starts with consent_verified=False, unanswered_count=0
- All patient data persisted to PostgreSQL

## Technical Notes
- SQLAlchemy 1.4 session.query style
- UUID primary keys
- Pydantic schemas for request/response validation
