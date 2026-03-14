import React from 'react';

function AlertList({ alerts }) {
  if (!alerts || alerts.length === 0) {
    return <p style={{ color: '#888', fontSize: '0.9rem' }}>No alerts.</p>;
  }

  return (
    <div>
      {alerts.map((alert) => (
        <div
          key={alert.id}
          className={`alert ${alert.resolved ? 'alert-info' : 'alert-danger'}`}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <strong>{alert.alert_type.replace(/_/g, ' ')}</strong>
            <span style={{ fontSize: '0.75rem' }}>
              {new Date(alert.created_at).toLocaleString()}
            </span>
          </div>
          <p style={{ marginTop: 4, fontSize: '0.85rem' }}>{alert.message}</p>
          {alert.resolved && (
            <span style={{ fontSize: '0.75rem', fontStyle: 'italic' }}>Resolved</span>
          )}
        </div>
      ))}
    </div>
  );
}

export default AlertList;
