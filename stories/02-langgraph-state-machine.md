# Story 2: LangGraph State Machine

## Description
As the system, I need a deterministic state machine that routes patients through coaching phases based on application logic, never LLM decisions.

## Acceptance Criteria
- Phase transitions: PENDING -> ONBOARDING -> ACTIVE -> RE_ENGAGING -> DORMANT
- Router function is purely deterministic (no LLM calls)
- consent_verified=False -> no interaction (END)
- PENDING + consent -> ONBOARDING
- ONBOARDING + goal set -> ACTIVE
- unanswered_count >= 1 -> RE_ENGAGING
- unanswered_count >= 3 -> DORMANT
- Patient response resets to ACTIVE (from RE_ENGAGING) or RE_ENGAGING (from DORMANT)
- All transitions logged in PhaseTransitionLog

## Technical Notes
- LangGraph StateGraph with PatientState TypedDict
- Deterministic routing function
- Phase nodes: onboarding, active, re_engaging, dormant
- All phase outputs flow through safety_guard node
