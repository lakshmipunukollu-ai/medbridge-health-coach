"""Tests for the safety guard component."""

import pytest
from app.agent.safety_guard import (
    check_safety,
    GuardResult,
    MENTAL_HEALTH_SAFE_RESPONSE,
    CLINICAL_REDIRECT_RESPONSE,
    MENTAL_HEALTH_TRIGGERS,
    CLINICAL_TRIGGERS,
)


class TestSafetyGuardMentalHealth:
    """Mental health trigger detection tests."""

    @pytest.mark.parametrize("trigger", MENTAL_HEALTH_TRIGGERS)
    def test_mental_health_trigger_detected(self, trigger):
        result = check_safety(f"I am feeling {trigger}")
        assert result.safe is False
        assert result.override_response == MENTAL_HEALTH_SAFE_RESPONSE
        assert result.alert_sent is True
        assert result.alert_type == "mental_health_crisis"

    def test_mental_health_case_insensitive(self):
        result = check_safety("I feel SUICIDAL")
        assert result.safe is False
        assert result.alert_sent is True

    def test_988_in_response(self):
        result = check_safety("I am feeling suicidal")
        assert "988" in result.override_response


class TestSafetyGuardClinical:
    """Clinical content trigger detection tests."""

    @pytest.mark.parametrize("trigger", CLINICAL_TRIGGERS)
    def test_clinical_trigger_detected(self, trigger):
        result = check_safety(f"I have {trigger} issues")
        assert result.safe is False
        assert result.override_response == CLINICAL_REDIRECT_RESPONSE
        assert result.alert_sent is False

    def test_clinical_redirect_mentions_clinician(self):
        result = check_safety("I have symptoms of something")
        assert "clinician" in result.override_response.lower()


class TestSafetyGuardSafeMessages:
    """Safe message handling tests."""

    def test_safe_message(self):
        result = check_safety("I completed my exercises today")
        assert result.safe is True
        assert result.override_response is None
        assert result.alert_sent is False

    def test_safe_greeting(self):
        result = check_safety("Hello, how are you?")
        assert result.safe is True

    def test_safe_exercise_update(self):
        result = check_safety("I did my stretches this morning")
        assert result.safe is True

    def test_empty_message(self):
        result = check_safety("")
        assert result.safe is True


class TestSafetyGuardInSession:
    """Safety guard integration with session endpoint."""

    def test_mental_health_message_flagged(self, client, sample_patient):
        patient_id = sample_patient["id"]
        response = client.post(f"/patients/{patient_id}/sessions", json={
            "message": "I feel suicidal and hopeless"
        })
        data = response.json()
        assert data["safety_flagged"] is True
        assert "988" in data["response"]

    def test_clinical_message_flagged(self, client, sample_patient):
        patient_id = sample_patient["id"]
        response = client.post(f"/patients/{patient_id}/sessions", json={
            "message": "I have new symptoms in my shoulder"
        })
        data = response.json()
        assert data["safety_flagged"] is True
        assert "clinician" in data["response"].lower()

    def test_safe_message_not_flagged(self, client, sample_patient):
        patient_id = sample_patient["id"]
        response = client.post(f"/patients/{patient_id}/sessions", json={
            "message": "I completed my exercises"
        })
        data = response.json()
        assert data["safety_flagged"] is False

    def test_mental_health_creates_alert(self, client, sample_patient):
        patient_id = sample_patient["id"]
        client.post(f"/patients/{patient_id}/sessions", json={
            "message": "I feel suicidal"
        })
        summary = client.get(f"/patients/{patient_id}/summary").json()
        mental_alerts = [a for a in summary["alerts"] if a["alert_type"] == "mental_health_crisis"]
        assert len(mental_alerts) >= 1
