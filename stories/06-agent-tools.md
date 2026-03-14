# Story 6: Agent Tools

## Description
As the LangGraph agent, I have tools available to take actions on behalf of the patient.

## Acceptance Criteria
- set_goal: Updates patient's goal, triggers phase transition if in ONBOARDING
- set_reminder: Creates a reminder entry for the patient
- get_program_summary: Returns the patient's HEP program summary
- get_adherence_summary: Returns exercise adherence statistics
- alert_clinician: Sends an urgent alert to the care team
- Tool invocation logic is real and tested
- Tool implementations may be stubbed but signatures are correct

## Technical Notes
- Tools are callable from within LangGraph nodes
- Each tool interacts with the database via services
- alert_clinician creates a ClinicianAlert record
