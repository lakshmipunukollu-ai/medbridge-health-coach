# Story 4: Coaching Sessions

## Description
As a patient, I can interact with the health coach through sessions that track my conversation history and guide me through my exercise program.

## Acceptance Criteria
- POST /patients/{id}/sessions starts or continues a coaching session
- Each session stores conversation messages as JSON
- Phase-appropriate responses (onboarding asks for goals, active does check-ins, etc.)
- unanswered_count increments when patient doesn't respond to check-ins
- unanswered_count resets when patient responds
- Session response includes current phase and safety flag status

## Technical Notes
- LangGraph workflow processes each message
- Response passes through SafetyGuard
- Session linked to patient via foreign key
