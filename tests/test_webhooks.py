"""Tests for webhook endpoints."""

import pytest


class TestScheduleWebhook:
    """POST /webhooks/schedule tests."""

    def test_schedule_webhook_success(self, client, sample_patient):
        patient_id = sample_patient["id"]
        response = client.post("/webhooks/schedule", json={
            "patient_id": patient_id,
            "trigger_type": "scheduled_checkin",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processed"
        assert data["patient_id"] == patient_id

    def test_schedule_webhook_increments_unanswered(self, client, sample_patient):
        patient_id = sample_patient["id"]
        # First check-in
        client.post("/webhooks/schedule", json={
            "patient_id": patient_id,
            "trigger_type": "scheduled_checkin",
        })
        patient = client.get(f"/patients/{patient_id}").json()
        assert patient["unanswered_count"] == 1

    def test_schedule_webhook_multiple_increments(self, client, sample_patient):
        patient_id = sample_patient["id"]
        for _ in range(3):
            client.post("/webhooks/schedule", json={
                "patient_id": patient_id,
                "trigger_type": "scheduled_checkin",
            })
        patient = client.get(f"/patients/{patient_id}").json()
        assert patient["unanswered_count"] == 3

    def test_schedule_webhook_moves_to_dormant(self, client, active_patient):
        patient_id = active_patient["id"]
        for _ in range(3):
            client.post("/webhooks/schedule", json={
                "patient_id": patient_id,
                "trigger_type": "scheduled_checkin",
            })
        result = client.post("/webhooks/schedule", json={
            "patient_id": patient_id,
            "trigger_type": "scheduled_checkin",
        })
        patient = client.get(f"/patients/{patient_id}").json()
        # After 3+ unanswered, should be DORMANT
        assert patient["phase"] == "DORMANT"

    def test_schedule_webhook_no_consent(self, client, sample_patient_no_consent):
        patient_id = sample_patient_no_consent["id"]
        response = client.post("/webhooks/schedule", json={
            "patient_id": patient_id,
            "trigger_type": "scheduled_checkin",
        })
        data = response.json()
        assert data["status"] == "skipped"
        assert data["action_taken"] == "no_consent"

    def test_schedule_webhook_not_found(self, client):
        response = client.post("/webhooks/schedule", json={
            "patient_id": "nonexistent-id",
            "trigger_type": "scheduled_checkin",
        })
        assert response.status_code == 404


class TestClinicianAlertWebhook:
    """POST /webhooks/clinician-alert tests."""

    def test_clinician_alert_success(self, client, sample_patient):
        patient_id = sample_patient["id"]
        response = client.post("/webhooks/clinician-alert", json={
            "patient_id": patient_id,
            "alert_type": "clinical_concern",
            "message": "Patient reported unusual symptoms",
            "source": "safety_guard",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "received"
        assert "alert_id" in data

    def test_clinician_alert_appears_in_summary(self, client, sample_patient):
        patient_id = sample_patient["id"]
        client.post("/webhooks/clinician-alert", json={
            "patient_id": patient_id,
            "alert_type": "mental_health_crisis",
            "message": "Safety concern triggered",
            "source": "safety_guard",
        })
        summary = client.get(f"/patients/{patient_id}/summary").json()
        assert len(summary["alerts"]) >= 1
        assert summary["alerts"][0]["alert_type"] == "mental_health_crisis"

    def test_clinician_alert_not_found(self, client):
        response = client.post("/webhooks/clinician-alert", json={
            "patient_id": "nonexistent-id",
            "alert_type": "test",
            "message": "test",
            "source": "test",
        })
        assert response.status_code == 404
