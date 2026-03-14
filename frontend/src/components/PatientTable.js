import React from 'react';
import { Link } from 'react-router-dom';

function PatientTable({ patients }) {
  if (!patients || patients.length === 0) {
    return (
      <div className="empty-state">
        <h3>No patients found</h3>
        <p>Create a new patient to get started.</p>
      </div>
    );
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Phase</th>
            <th>Consent</th>
            <th>Goal</th>
            <th>Unanswered</th>
            <th>Last Interaction</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {patients.map((p) => (
            <tr key={p.id}>
              <td>
                <Link to={`/patients/${p.id}`} style={{ color: '#1a1a2e', fontWeight: 500, textDecoration: 'none' }}>
                  {p.name}
                </Link>
              </td>
              <td>
                <span className={`phase-badge phase-${p.phase}`}>{p.phase}</span>
              </td>
              <td>{p.consent_verified ? 'Yes' : 'No'}</td>
              <td style={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {p.goal || '-'}
              </td>
              <td>{p.unanswered_count}</td>
              <td>
                {p.last_interaction
                  ? new Date(p.last_interaction).toLocaleDateString()
                  : 'Never'}
              </td>
              <td>
                <Link to={`/patients/${p.id}/chat`} className="btn btn-primary" style={{ fontSize: '0.8rem', padding: '6px 12px' }}>
                  Chat
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default PatientTable;
