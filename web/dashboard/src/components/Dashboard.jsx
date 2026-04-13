import React, { useEffect, useState } from 'react';

export default function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const [error, setError] = useState("");

  const fetchMetrics = async () => {
    try {
      const res = await fetch('http://localhost:4000/monitor/metrics', {
        headers: { 'Authorization': 'Bearer DUMMY_TOKEN' } // Using dummy token for now, needs real auth flow
      });
      const data = await res.json();
      if (data.success) setMetrics(data.metrics);
    } catch (err) {
      console.error(err);
      setError("Failed to fetch engine metrics.");
    }
  };

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="glass-panel" style={{ padding: '2rem' }}>
      <h1>System Status</h1>
      {error && <p style={{color: 'var(--accent-red)'}}>{error}</p>}
      
      {!metrics ? (
        <p style={{ color: 'var(--text-muted)' }}>Waiting for engine telemetry...</p>
      ) : (
        <div style={{ display: 'flex', gap: '20px', marginTop: '20px' }}>
          <div className="glass-panel" style={{ flex: 1, padding: '1.5rem', textAlign: 'center' }}>
            <h3>CPU Load</h3>
            <div style={{ fontSize: '2rem', color: 'var(--accent-blue)', textShadow: '0 0 10px rgba(0,240,255,0.5)' }}>
              {metrics.cpu_percent.toFixed(1)}%
            </div>
          </div>
          <div className="glass-panel" style={{ flex: 1, padding: '1.5rem', textAlign: 'center' }}>
            <h3>RAM Usage</h3>
            <div style={{ fontSize: '2rem', color: 'var(--accent-purple)', textShadow: '0 0 10px rgba(139,92,246,0.5)' }}>
              {metrics.ram_used_mb.toFixed(0)} MB / {metrics.ram_total_mb.toFixed(0)} MB
            </div>
          </div>
          <div className="glass-panel" style={{ flex: 1, padding: '1.5rem', textAlign: 'center' }}>
            <h3>Disk</h3>
            <div style={{ fontSize: '2rem', color: '#ffcc00', textShadow: '0 0 10px rgba(255,204,0,0.5)' }}>
              {metrics.disk_used_gb.toFixed(1)} GB / {metrics.disk_total_gb.toFixed(0)} GB
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
