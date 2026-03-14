import React, { useState, useEffect } from 'react';
import { getHealth } from '../api/client';

function HealthStatus() {
  const [health, setHealth] = useState(null);

  useEffect(() => {
    getHealth()
      .then(setHealth)
      .catch(() => setHealth({ status: 'unreachable' }));
  }, []);

  if (!health) return null;

  const isHealthy = health.status === 'healthy';

  return (
    <div
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 6,
        padding: '4px 12px',
        borderRadius: 20,
        fontSize: '0.75rem',
        fontWeight: 600,
        background: isHealthy ? '#dcfce7' : '#fee2e2',
        color: isHealthy ? '#15803d' : '#b91c1c',
      }}
    >
      <span
        style={{
          width: 8,
          height: 8,
          borderRadius: '50%',
          background: isHealthy ? '#15803d' : '#b91c1c',
        }}
      />
      {isHealthy ? 'API Connected' : 'API Disconnected'}
    </div>
  );
}

export default HealthStatus;
