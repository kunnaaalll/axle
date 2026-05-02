import React, { useState } from 'react';
import { Rocket, CheckCircle, Clock, AlertCircle, ArrowRight } from 'lucide-react';

const mockPlan = [
  { name: 'Install Node.js 20', status: 'completed', plugin: 'runtime', duration: '2.4s' },
  { name: 'Install PostgreSQL 16', status: 'completed', plugin: 'database', duration: '5.1s' },
  { name: 'Clone repository', status: 'completed', plugin: 'runtime', duration: '3.2s' },
  { name: 'npm install', status: 'completed', plugin: 'runtime', duration: '12.8s' },
  { name: 'Database migration', status: 'running', plugin: 'database', duration: '...' },
  { name: 'Configure Nginx reverse proxy', status: 'pending', plugin: 'nginx', duration: '' },
  { name: 'SSL certificate (Let\'s Encrypt)', status: 'pending', plugin: 'ssl', duration: '' },
  { name: 'Create systemd service', status: 'pending', plugin: 'systemd', duration: '' },
  { name: 'Configure firewall rules', status: 'pending', plugin: 'firewall', duration: '' },
  { name: 'Start application', status: 'pending', plugin: 'systemd', duration: '' },
];

export default function DeployApp() {
  const [url, setUrl] = useState('https://github.com/user/nextjs-app');
  const [deploying, setDeploying] = useState(false);

  const statusIcon = (s) => {
    if (s === 'completed') return <CheckCircle size={16} color="var(--accent-green)" />;
    if (s === 'running') return <div style={{ width: 16, height: 16, border: '2px solid var(--accent-blue)', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />;
    if (s === 'failed') return <AlertCircle size={16} color="var(--accent-red)" />;
    return <Clock size={16} color="var(--text-muted)" />;
  };

  return (
    <div style={{ padding: '24px', height: '100%', overflow: 'auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
        <Rocket size={24} color="var(--accent-blue)" />
        <h2 style={{ margin: 0, fontSize: '1.2rem' }}>AXLE Deploy</h2>
      </div>

      <div style={{ display: 'flex', gap: '10px', marginBottom: '24px' }}>
        <input
          value={url}
          onChange={e => setUrl(e.target.value)}
          placeholder="https://github.com/user/repo"
          style={{
            flex: 1, padding: '12px 16px', background: 'rgba(255,255,255,0.04)',
            border: '1px solid var(--panel-border)', borderRadius: '8px',
            color: '#fff', outline: 'none', fontSize: '0.9rem',
          }}
        />
        <button
          onClick={() => setDeploying(true)}
          style={{
            padding: '12px 24px', background: 'linear-gradient(135deg, rgba(0,240,255,0.15), rgba(139,92,246,0.15))',
            border: '1px solid rgba(0,240,255,0.3)', borderRadius: '8px', color: '#fff',
            cursor: 'pointer', fontWeight: 600, fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '8px',
          }}
        >
          <ArrowRight size={16} /> Deploy
        </button>
      </div>

      {deploying && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '1px' }}>
            Deployment Pipeline — 10 steps
          </div>
          {mockPlan.map((step, i) => (
            <div key={i} style={{
              display: 'flex', alignItems: 'center', gap: '12px',
              padding: '10px 14px', background: step.status === 'running' ? 'rgba(0,240,255,0.04)' : 'rgba(255,255,255,0.02)',
              borderRadius: '8px', borderLeft: `3px solid ${step.status === 'completed' ? 'var(--accent-green)' : step.status === 'running' ? 'var(--accent-blue)' : 'rgba(255,255,255,0.06)'}`,
            }}>
              {statusIcon(step.status)}
              <span style={{ flex: 1, fontSize: '0.85rem', color: step.status === 'pending' ? 'var(--text-muted)' : 'var(--text-primary)' }}>
                {step.name}
              </span>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                {step.plugin}
              </span>
              {step.duration && <span style={{ fontSize: '0.75rem', color: 'var(--accent-blue)', fontFamily: 'var(--font-mono)' }}>{step.duration}</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
