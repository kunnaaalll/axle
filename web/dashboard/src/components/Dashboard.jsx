import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Cpu, HardDrive, MemoryStick } from 'lucide-react';

export default function Dashboard() {
  const { authFetch } = useAuth();
  const [metrics, setMetrics] = useState(null);
  const [error, setError] = useState("");

  const fetchMetrics = async () => {
    try {
      const res = await authFetch('/monitor/metrics');
      const data = await res.json();
      if (data.success) setMetrics(data.metrics);
    } catch (err) {
      setError("Failed to fetch engine metrics.");
    }
  };

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000);
    return () => clearInterval(interval);
  }, []);

  const MetricCard = ({ title, value, unit, color, icon }) => (
    <div className="glass-panel" style={{ flex: 1, padding: '1.5rem', minWidth: '200px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
        <h3 style={{ margin: 0, fontSize: '0.95rem', color: 'var(--text-muted)' }}>{title}</h3>
        {icon}
      </div>
      <div style={{
        fontSize: '2.2rem',
        fontWeight: '700',
        color,
        textShadow: `0 0 20px ${color}40`,
        letterSpacing: '-1px',
      }}>
        {value}
        <span style={{ fontSize: '0.9rem', fontWeight: '400', marginLeft: '4px', color: 'var(--text-muted)' }}>{unit}</span>
      </div>
    </div>
  );

  return (
    <div>
      <h1>System Dashboard</h1>
      {error && <p style={{ color: 'var(--accent-red)' }}>{error}</p>}

      {!metrics ? (
        <div className="glass-panel" style={{ padding: '2rem', textAlign: 'center' }}>
          <p style={{ color: 'var(--text-muted)' }}>Connecting to engine telemetry...</p>
        </div>
      ) : (
        <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
          <MetricCard
            title="CPU Load"
            value={metrics.cpu_percent.toFixed(1)}
            unit="%"
            color="var(--accent-blue)"
            icon={<Cpu size={20} color="var(--accent-blue)" />}
          />
          <MetricCard
            title="RAM Usage"
            value={(metrics.ram_used_mb / 1024).toFixed(1)}
            unit={`GB / ${(metrics.ram_total_mb / 1024).toFixed(0)} GB`}
            color="var(--accent-purple)"
            icon={<MemoryStick size={20} color="var(--accent-purple)" />}
          />
          <MetricCard
            title="Disk Usage"
            value={metrics.disk_used_gb.toFixed(1)}
            unit={`GB / ${metrics.disk_total_gb.toFixed(0)} GB`}
            color="#ffcc00"
            icon={<HardDrive size={20} color="#ffcc00" />}
          />
        </div>
      )}
    </div>
  );
}
