import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getPatientSummary, updatePatient, triggerScheduledCheckin } from '../api/client';
import PhaseTimeline from '../components/PhaseTimeline';
import AlertList from '../components/AlertList';

function PatientDetail() {
  const { id } = useParams();
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionMsg, setActionMsg] = useState(null);

  const fetchSummary = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getPatientSummary(id);
      setSummary(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchSummary();
  }, [fetchSummary]);

  const handleToggleConsent = async () => {
    if (!summary) return;
    try {
      // We need to get current patient data to toggle consent
      // Summary doesn't include consent_verified directly, so we update
      await updatePatient(id, { consent_verified: true });
      setActionMsg('Consent verified successfully.');
      fetchSummary();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleTriggerCheckin = async () => {
    try {
      const result = await triggerScheduledCheckin(id);
      setActionMsg(`Check-in triggered: ${result.action_taken}`);
      fetchSummary();
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) return <div className="loading">Loading patient details...</div>;
  if (error) return <div className="alert alert-danger">{error}</div>;
  if (!summary) return <div className="alert alert-warning">No data available.</div>;

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>{summary.name}</h1>
          <span style={{ fontSize: '0.85rem', color: '#888' }}>ID: {summary.patient_id}</span>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <Link to={`/patients/${id}/chat`} className="btn btn-primary">
            Open Chat
          </Link>
          <button className="btn btn-secondary" onClick={handleTriggerCheckin}>
            Trigger Check-in
          </button>
        </div>
      </div>

      {actionMsg && (
        <div className="alert alert-success" onClick={() => setActionMsg(null)} style={{ cursor: 'pointer' }}>
          {actionMsg}
        </div>
      )}

      <div className="stats-row">
        <div className="stat-card">
          <div className="stat-value">
            <span className={`phase-badge phase-${summary.current_phase}`}>
              {summary.current_phase}
            </span>
          </div>
          <div className="stat-label">Current Phase</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{summary.total_sessions}</div>
          <div className="stat-label">Total Sessions</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{summary.unanswered_count}</div>
          <div className="stat-label">Unanswered</div>
        </div>
        <div className="stat-card">
          <div className="stat-value" style={{ fontSize: '1rem' }}>
            {summary.last_interaction
              ? new Date(summary.last_interaction).toLocaleDateString()
              : 'Never'}
          </div>
          <div className="stat-label">Last Interaction</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
        <div className="card">
          <h3>Goal</h3>
          <p style={{ fontSize: '0.95rem', color: summary.goal ? '#333' : '#999' }}>
            {summary.goal || 'No goal set yet.'}
          </p>
        </div>

        <div className="card">
          <h3>Actions</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <button className="btn btn-success" onClick={handleToggleConsent}>
              Verify Consent
            </button>
            <button className="btn btn-secondary" onClick={fetchSummary}>
              Refresh Data
            </button>
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
        <div className="card">
          <h3>Phase History</h3>
          <PhaseTimeline history={summary.phase_history} />
        </div>

        <div className="card">
          <h3>Safety Alerts ({summary.alerts.length})</h3>
          <AlertList alerts={summary.alerts} />
        </div>
      </div>
    </div>
  );
}

export default PatientDetail;
