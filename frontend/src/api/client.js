/**
 * API client for Medbridge Health Coach backend.
 * Connects to FastAPI on port 3007.
 */

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:3007';

async function request(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `API error: ${res.status}`);
  }
  return res.json();
}

// Health
export const getHealth = () => request('/health');

// Patients
export const createPatient = (data) =>
  request('/patients', { method: 'POST', body: JSON.stringify(data) });

export const getPatient = (id) => request(`/patients/${id}`);

export const updatePatient = (id, data) =>
  request(`/patients/${id}`, { method: 'PATCH', body: JSON.stringify(data) });

export const getPatientSummary = (id) => request(`/patients/${id}/summary`);

// Sessions
export const sendMessage = (patientId, message) =>
  request(`/patients/${patientId}/sessions`, {
    method: 'POST',
    body: JSON.stringify({ message }),
  });

// Webhooks
export const triggerScheduledCheckin = (patientId) =>
  request('/webhooks/schedule', {
    method: 'POST',
    body: JSON.stringify({ patient_id: patientId, trigger_type: 'scheduled_checkin' }),
  });

export const sendClinicianAlert = (data) =>
  request('/webhooks/clinician-alert', {
    method: 'POST',
    body: JSON.stringify(data),
  });
