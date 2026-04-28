import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { RotateCcw, CheckCircle, XCircle, Clock } from 'lucide-react';

export default function DeployHistory() {
  const { authFetch } = useAuth();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const res = await authFetch('/deploy/history');
      const data = await res.json();
      if (data.success) {
        setHistory(data.history || []);
      }
    } catch (err) {
      console.error('Failed to fetch history:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRollback = async (deployId) => {
    if (!confirm('Are you sure you want to rollback to this deployment?')) return;
    try {
      await authFetch(`/deploy/rollback/${deployId}`, { method: 'POST' });
      fetchHistory();
    } catch (err) {
      console.error('Rollback failed:', err);
    }
  };

  const statusIcon = (status) => {
    switch (status) {
      case 'completed': return <CheckCircle size={18} color="var(--accent-blue)" />;
      case 'failed': return <XCircle size={18} color="var(--accent-red)" />;
      default: return <Clock size={18} color="var(--text-muted)" />;
    }
  };

  const statusColor = (status) => {
    switch (status) {
      case 'completed': return 'var(--accent-blue)';
      case 'failed': return 'var(--accent-red)';
      default: return 'var(--text-muted)';
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '2rem' }}>
      <h1>Deployment History</h1>
      <p style={{ color: 'var(--text-muted)' }}>Previous deployments with rollback capability.</p>

      <div style={{ marginTop: '2rem' }}>
        {loading ? (
          <p style={{ color: 'var(--text-muted)' }}>Loading history...</p>
        ) : history.length === 0 ? (
          <div style={{
            textAlign: 'center',
            padding: '3rem',
            color: 'var(--text-muted)',
            border: '1px dashed var(--panel-border)',
            borderRadius: '8px',
          }}>
            <Clock size={48} style={{ opacity: 0.3, marginBottom: '1rem' }} />
            <p>No deployments yet. Start one from the Deploy tab.</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {history.map((deploy, i) => (
              <div
                key={deploy.id || i}
                className="glass-panel"
                style={{
                  padding: '16px 20px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                  {statusIcon(deploy.status)}
                  <div>
                    <div style={{ fontWeight: '600' }}>{deploy.project_name}</div>
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                      {deploy.github_url || 'Local deployment'} • {new Date(deploy.started_at).toLocaleString()}
                    </div>
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <span style={{
                    fontSize: '0.85rem',
                    fontWeight: '600',
                    color: statusColor(deploy.status),
                    textTransform: 'uppercase',
                  }}>
                    {deploy.status}
                  </span>
                  {deploy.rollback_available && deploy.status === 'completed' && (
                    <button
                      onClick={() => handleRollback(deploy.id)}
                      className="btn-glow"
                      style={{ padding: '6px 14px', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '6px' }}
                    >
                      <RotateCcw size={14} /> Rollback
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
