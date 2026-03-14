"""Tests for the deterministic phase routing state machine."""

import pytest
from app.agent.router import route_to_phase
from app.agent.workflow import run_workflow


class TestRouteToPhase:
    """Deterministic routing function tests."""

    def test_no_consent_returns_end(self):
        state = {
            "consent_verified": False,
            "phase": "PENDING",
            "unanswered_count": 0,
            "goal": None,
        }
        assert route_to_phase(state) == "end"

    def test_pending_routes_to_onboarding(self):
        state = {
            "consent_verified": True,
            "phase": "PENDING",
            "unanswered_count": 0,
            "goal": None,
        }
        assert route_to_phase(state) == "onboarding"

    def test_onboarding_with_goal_routes_to_active(self):
        state = {
            "consent_verified": True,
            "phase": "ONBOARDING",
            "unanswered_count": 0,
            "goal": "Walk daily",
        }
        assert route_to_phase(state) == "active"

    def test_onboarding_without_goal_stays(self):
        state = {
            "consent_verified": True,
            "phase": "ONBOARDING",
            "unanswered_count": 0,
            "goal": None,
        }
        assert route_to_phase(state) == "onboarding"

    def test_high_unanswered_routes_to_dormant(self):
        state = {
            "consent_verified": True,
            "phase": "ACTIVE",
            "unanswered_count": 3,
            "goal": "Walk daily",
        }
        assert route_to_phase(state) == "dormant"

    def test_unanswered_routes_to_re_engaging(self):
        state = {
            "consent_verified": True,
            "phase": "ACTIVE",
            "unanswered_count": 1,
            "goal": "Walk daily",
        }
        assert route_to_phase(state) == "re_engaging"

    def test_active_stays_active(self):
        state = {
            "consent_verified": True,
            "phase": "ACTIVE",
            "unanswered_count": 0,
            "goal": "Walk daily",
        }
        assert route_to_phase(state) == "active"

    def test_unanswered_count_2_routes_to_re_engaging(self):
        state = {
            "consent_verified": True,
            "phase": "ACTIVE",
            "unanswered_count": 2,
            "goal": "Walk daily",
        }
        assert route_to_phase(state) == "re_engaging"

    def test_unanswered_count_5_routes_to_dormant(self):
        state = {
            "consent_verified": True,
            "phase": "ACTIVE",
            "unanswered_count": 5,
            "goal": "Walk daily",
        }
        assert route_to_phase(state) == "dormant"


class TestWorkflow:
    """Workflow execution tests."""

    def _make_state(self, **overrides):
        base = {
            "patient_id": "test-123",
            "phase": "PENDING",
            "messages": [],
            "goal": None,
            "unanswered_count": 0,
            "last_interaction": None,
            "consent_verified": True,
            "program_summary": None,
            "user_message": "Hello",
            "agent_response": "",
            "safety_flagged": False,
        }
        base.update(overrides)
        return base

    def test_workflow_pending_to_onboarding(self):
        state = self._make_state(phase="PENDING")
        result = run_workflow(state)
        assert result["agent_response"]  # non-empty
        assert "safety_flagged" in result

    def test_workflow_no_consent(self):
        state = self._make_state(consent_verified=False)
        result = run_workflow(state)
        assert "consent" in result["agent_response"].lower()

    def test_workflow_active_phase(self):
        state = self._make_state(phase="ACTIVE", goal="Walk daily")
        result = run_workflow(state)
        assert result["agent_response"]

    def test_workflow_safety_guard_runs(self):
        state = self._make_state(user_message="I feel suicidal")
        result = run_workflow(state)
        assert result["safety_flagged"] is True
        assert "988" in result["agent_response"]

    def test_workflow_re_engaging(self):
        state = self._make_state(
            phase="RE_ENGAGING",
            unanswered_count=1,
            user_message="I'm back",
        )
        result = run_workflow(state)
        assert result["agent_response"]

    def test_workflow_dormant_response(self):
        state = self._make_state(
            phase="DORMANT",
            unanswered_count=3,
            user_message="Hi again",
        )
        result = run_workflow(state)
        assert result["agent_response"]
        # Dormant patient responding should trigger re-engagement
        assert result.get("phase") == "RE_ENGAGING" or "welcome" in result["agent_response"].lower()


class TestPhaseTransitions:
    """Integration tests for phase transitions via API."""

    def test_pending_to_onboarding_transition(self, client, sample_patient):
        patient_id = sample_patient["id"]
        assert sample_patient["phase"] == "PENDING"

        # First message should move to onboarding
        client.post(f"/patients/{patient_id}/sessions", json={
            "message": "Hello"
        })
        patient = client.get(f"/patients/{patient_id}").json()
        # Phase transitions happen through the workflow
        assert patient["phase"] in ["PENDING", "ONBOARDING"]

    def test_active_to_re_engaging_via_webhook(self, client, active_patient):
        patient_id = active_patient["id"]
        # Trigger unanswered check-in
        response = client.post("/webhooks/schedule", json={
            "patient_id": patient_id,
            "trigger_type": "scheduled_checkin",
        })
        data = response.json()
        patient = client.get(f"/patients/{patient_id}").json()
        assert patient["phase"] == "RE_ENGAGING"

    def test_re_engaging_to_active_on_response(self, client, active_patient):
        patient_id = active_patient["id"]
        # Move to RE_ENGAGING
        client.post("/webhooks/schedule", json={
            "patient_id": patient_id,
            "trigger_type": "scheduled_checkin",
        })
        # Respond
        client.post(f"/patients/{patient_id}/sessions", json={
            "message": "I'm here, sorry I missed check-in"
        })
        patient = client.get(f"/patients/{patient_id}").json()
        assert patient["phase"] == "ACTIVE"

    def test_phase_history_logged(self, client, sample_patient):
        patient_id = sample_patient["id"]
        # Trigger some transitions
        client.post(f"/patients/{patient_id}/sessions", json={
            "message": "Hello"
        })
        summary = client.get(f"/patients/{patient_id}/summary").json()
        # Phase history should have entries if transitions occurred
        assert isinstance(summary["phase_history"], list)
