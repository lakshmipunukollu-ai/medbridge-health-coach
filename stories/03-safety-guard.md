# Story 3: Safety Guard

## Description
As a clinical product, EVERY agent output must pass through the SafetyGuard before delivery. This is non-negotiable and non-skippable.

## Acceptance Criteria
- Mental health triggers (suicidal, self-harm, hopeless, etc.) -> immediate clinician alert + safe response
- Clinical content triggers (symptoms, medication, diagnosis, etc.) -> redirect to care team
- Safe response for mental health includes 988 Suicide & Crisis Lifeline
- Clinical redirect tells patient to contact their clinician
- ClinicianAlert record created for mental health crises
- No bypass path exists in the architecture
- Guard runs on EVERY response, regardless of phase

## Technical Notes
- Keyword-based matching (not LLM-based) for reliability
- Zero external dependencies for safety checks
- alert_clinician tool invoked for mental health crises
