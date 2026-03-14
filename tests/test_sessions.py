"""Tests for coaching session endpoints."""

import pytest


class TestCreateSession:
    """POST /patients/{id}/sessions tests."""

    def test_session_with_consent(self, client, sample_patient):
        patient_id = sample_patient["id"]
        response = client.post(f"/patients/{patient_id}/sessions", json={
            "message": "Hello, I want to start my exercises"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["patient_id"] == patient_id
        assert data["response"]  # non-empty response
        assert isinstance(data["safety_flagged"], bool)
        assert "session_id" in data
        assert "phase" in data

    def test_session_without_consent(self, client, sample_patient_no_consent):
        patient_id = sample_patient_no_consent["id"]
        response = client.post(f"/patients/{patient_id}/sessions", json={
            "message": "Hello"
        })
        assert response.status_code == 200
        data = response.json()
        assert "consent" in data["response"].lower()
        assert data["safety_flagged"] is False

    def test_session_not_found(self, client):
        response = client.post("/patients/nonexistent-id/sessions", json={
            "message": "Hello"
        })
        assert response.status_code == 404

    def test_session_onboarding_welcome(self, client, sample_patient):
        patient_id = sample_patient["id"]
        response = client.post(f"/patients/{patient_id}/sessions", json={
            "message": "Hi there"
        })
        data = response.json()
        # Patient starts in PENDING, first message should trigger onboarding
        assert "welcome" in data["response"].lower() or "goal" in data["response"].lower()

    def test_session_goal_setting(self, client, sample_patient):
        patient_id = sample_patient["id"]
        # First message
        client.post(f"/patients/{patient_id}/sessions", json={
            "message": "Hello"
        })
        # Set goal
        response = client.post(f"/patients/{patient_id}/sessions", json={
            "message": "My goal is to improve my shoulder mobility"
        })
        data = response.json()
        assert data["response"]  # non-empty

    def test_session_active_phase_responses(self, client, active_patient):
        patient_id = active_patient["id"]
        # Test exercise completion response
        response = client.post(f"/patients/{patient_id}/sessions", json={
            "message": "I completed my exercises today"
        })
        data = response.json()
        assert data["response"]
        assert data["phase"] == "ACTIVE"

    def test_session_active_missed_exercise(self, client, active_patient):
        patient_id = active_patient["id"]
        response = client.post(f"/patients/{patient_id}/sessions", json={
            "message": "I skipped my exercises today"
        })
        data = response.json()
        assert "okay" in data["response"].lower() or "off day" in data["response"].lower()

    def test_session_resets_unanswered_count(self, client, sample_patient):
        patient_id = sample_patient["id"]
        # Trigger check-in to increment unanswered
        client.post("/webhooks/schedule", json={
            "patient_id": patient_id,
            "trigger_type": "scheduled_checkin",
        })
        # Now respond - should reset
        client.post(f"/patients/{patient_id}/sessions", json={
            "message": "I'm here"
        })
        patient = client.get(f"/patients/{patient_id}").json()
        assert patient["unanswered_count"] == 0
