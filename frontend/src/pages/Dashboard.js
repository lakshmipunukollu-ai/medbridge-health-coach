import React, { useState, useEffect, useCallback } from 'react';
import PatientTable from '../components/PatientTable';
import HealthStatus from '../components/HealthStatus';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:3007';

function Dashboard() {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  const fetchPatients = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // The backend doesn't have a list endpoint, so we'll show a message
      // In production, we'd add GET /patients to the backend
      // For now, show instructions to use patient IDs directly
      setPatients([]);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPatients();
  }, [fetchPatients]);

  const handleSearch = async () => {
    if (!searchTerm.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/patients/${searchTerm.trim()}`);
      if (!res.ok) {
        if (res.status === 404) {
          setError('Patient not found. Check the ID and try again.');
          setPatients([]);
          return;
        }
        throw new Error(`Error: ${res.status}`);
      }
      const patient = await res.json();
      setPatients([patient]);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Compute stats from loaded patients
  const stats = {
    total: patients.length,
    active: patients.filter((p) => p.phase === 'ACTIVE').length,
    reEngaging: patients.filter((p) => p.phase === 'RE_ENGAGING').length,
    dormant: patients.filter((p) => p.phase === 'DORMANT').length,
  };

  return (
    <div>
      <div className="page-header">
        <h1>Dashboard</h1>
        <HealthStatus />
      </div>

      <div className="stats-row">
        <div className="stat-card">
          <div className="stat-value">{stats.total}</div>
          <div className="stat-label">Patients Loaded</div>
        </div>
        <div className="stat-card">
          <div className="stat-value" style={{ color: '#15803d' }}>{stats.active}</div>
          <div className="stat-label">Active</div>
        </div>
        <div className="stat-card">
          <div className="stat-value" style={{ color: '#b45309' }}>{stats.reEngaging}</div>
          <div className="stat-label">Re-Engaging</div>
        </div>
        <div className="stat-card">
          <div className="stat-value" style={{ color: '#b91c1c' }}>{stats.dormant}</div>
          <div className="stat-label">Dormant</div>
        </div>
      </div>

      <div className="card">
        <h3>Find Patient</h3>
        <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
          <input
            type="text"
            placeholder="Enter patient ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            style={{
              flex: 1,
              padding: '10px 14px',
              border: '1px solid #ddd',
              borderRadius: 8,
              fontSize: '0.95rem',
            }}
          />
          <button className="btn btn-primary" onClick={handleSearch}>
            Search
          </button>
        </div>

        {error && <div className="alert alert-danger">{error}</div>}
        {loading ? (
          <div className="loading">Loading...</div>
        ) : (
          <PatientTable patients={patients} />
        )}
      </div>
    </div>
  );
}

export default Dashboard;
