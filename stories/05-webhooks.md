# Story 5: Webhook Endpoints

## Description
As an external system, I can trigger scheduled check-ins and clinician alerts via webhook endpoints.

## Acceptance Criteria
- POST /webhooks/schedule triggers a scheduled check-in for a patient
- If patient doesn't respond, unanswered_count increments
- POST /webhooks/clinician-alert receives and stores urgent escalation alerts
- Webhook responses include status and action taken
- Invalid patient_id returns 404

## Technical Notes
- Webhooks are the primary integration mechanism (no frontend)
- Schedule webhook simulates time-based check-in logic
- Clinician alert webhook stores alert in database
