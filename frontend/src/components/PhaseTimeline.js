import React from 'react';

function PhaseTimeline({ history }) {
  if (!history || history.length === 0) {
    return <p style={{ color: '#888', fontSize: '0.9rem' }}>No phase transitions yet.</p>;
  }

  return (
    <div className="timeline">
      {history.map((entry, idx) => (
        <div className="timeline-item" key={idx}>
          <div className="timeline-date">
            {new Date(entry.created_at).toLocaleString()}
          </div>
          <div className="timeline-text">
            <span className={`phase-badge phase-${entry.from_phase}`}>{entry.from_phase}</span>
            {' '}&rarr;{' '}
            <span className={`phase-badge phase-${entry.to_phase}`}>{entry.to_phase}</span>
            <br />
            <span style={{ fontSize: '0.8rem', color: '#666' }}>{entry.reason}</span>
          </div>
        </div>
      ))}
    </div>
  );
}

export default PhaseTimeline;
