"""Tests for patient management endpoints."""

import pytest


class TestCreatePatient:
    """POST /patients tests."""

    def test_create_patient_success(self, client):
        response = client.post("/patients", json={
            "name": "Jane Doe",
            "email": "jane@example.com",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Jane Doe"
        assert data["email"] == "jane@example.com"
        assert data["phase"] == "PENDING"
        assert data["consent_verified"] is False
        assert data["unanswered_count"] == 0
        assert data["goal"] is None
        assert "id" in data

    def test_create_patient_with_consent(self, client):
        response = client.post("/patients", json={
            "name": "John Smith",
            "consent_verified": True,
        })
        assert response.status_code == 201
        data = response.json()
        assert data["consent_verified"] is True
        assert data["phase"] == "PENDING"

    def test_create_patient_with_external_id(self, client):
        response = client.post("/patients", json={
            "name": "Alice",
            "external_id": "EXT-123",
        })
        assert response.status_code == 201
        assert response.json()["external_id"] == "EXT-123"

    def test_create_patient_minimal(self, client):
        response = client.post("/patients", json={"name": "Minimal"})
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Minimal"
        assert data["email"] is None

    def test_create_patient_missing_name(self, client):
        response = client.post("/patients", json={"email": "no-name@test.com"})
        assert response.status_code == 422


class TestGetPatient:
    """GET /patients/{id} tests."""

    def test_get_patient_success(self, client, sample_patient):
        patient_id = sample_patient["id"]
        response = client.get(f"/patients/{patient_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == patient_id
        assert data["name"] == "Jane Doe"

    def test_get_patient_not_found(self, client):
        response = client.get("/patients/nonexistent-id")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestUpdatePatient:
    """PATCH /patients/{id} tests."""

    def test_update_consent(self, client, sample_patient_no_consent):
        patient_id = sample_patient_no_consent["id"]
        response = client.patch(f"/patients/{patient_id}", json={
            "consent_verified": True,
        })
        assert response.status_code == 200
        assert response.json()["consent_verified"] is True

    def test_update_name(self, client, sample_patient):
        patient_id = sample_patient["id"]
        response = client.patch(f"/patients/{patient_id}", json={
            "name": "Jane Updated",
        })
        assert response.status_code == 200
        assert response.json()["name"] == "Jane Updated"

    def test_update_goal(self, client, sample_patient):
        patient_id = sample_patient["id"]
        response = client.patch(f"/patients/{patient_id}", json={
            "goal": "Walk 30 minutes daily",
        })
        assert response.status_code == 200
        assert response.json()["goal"] == "Walk 30 minutes daily"

    def test_update_patient_not_found(self, client):
        response = client.patch("/patients/nonexistent-id", json={
            "name": "Nope",
        })
        assert response.status_code == 404


class TestPatientSummary:
    """GET /patients/{id}/summary tests."""

    def test_summary_success(self, client, sample_patient):
        patient_id = sample_patient["id"]
        response = client.get(f"/patients/{patient_id}/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["patient_id"] == patient_id
        assert data["name"] == "Jane Doe"
        assert data["current_phase"] == "PENDING"
        assert data["total_sessions"] == 0
        assert data["unanswered_count"] == 0
        assert isinstance(data["phase_history"], list)
        assert isinstance(data["alerts"], list)

    def test_summary_not_found(self, client):
        response = client.get("/patients/nonexistent-id/summary")
        assert response.status_code == 404

    def test_summary_after_sessions(self, client, sample_patient):
        patient_id = sample_patient["id"]
        # Send a message
        client.post(f"/patients/{patient_id}/sessions", json={
            "message": "Hello"
        })
        response = client.get(f"/patients/{patient_id}/summary")
        data = response.json()
        assert data["total_sessions"] >= 1
        assert data["last_interaction"] is not None
