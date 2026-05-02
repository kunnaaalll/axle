import React, { useState, useEffect, useRef } from 'react';
import { Rocket, CheckCircle, Clock, AlertCircle, ArrowRight, ExternalLink } from 'lucide-react';

const PLAN_STEPS = [
  { name: 'Clone repository', plugin: 'runtime', time: 3200 },
  { name: 'Detect stack: Node.js + Express', plugin: 'scanner', time: 1800 },
  { name: 'Install Node.js 20 LTS', plugin: 'runtime', time: 2400 },
  { name: 'Install PostgreSQL 16', plugin: 'database', time: 4100 },
  { name: 'npm install (148 packages)', plugin: 'runtime', time: 6800 },
  { name: 'Run database migrations', plugin: 'database', time: 3500 },
  { name: 'Configure Nginx reverse proxy', plugin: 'nginx', time: 2200 },
  { name: 'Provision SSL certificate', plugin: 'ssl', time: 5200 },
  { name: 'Create systemd service', plugin: 'systemd', time: 1500 },
  { name: 'Configure UFW firewall', plugin: 'firewall', time: 1200 },
  { name: 'Start application (PM2)', plugin: 'systemd', time: 2000 },
  { name: 'Health check — 200 OK', plugin: 'verify', time: 1400 },
];

export default function DeployApp() {
  const [url, setUrl] = useState('');
  const [phase, setPhase] = useState('input'); // input | scanning | deploying | done | error
  const [steps, setSteps] = useState([]);
  const [currentStep, setCurrentStep] = useState(-1);
  const [logs, setLogs] = useState([]);
  const logsEndRef = useRef(null);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const addLog = (msg) => setLogs(prev => [...prev, { time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }), msg }]);

  const startDeploy = () => {
    if (!url.trim()) return;
    setPhase('scanning');
    setSteps(PLAN_STEPS.map(s => ({ ...s, status: 'pending', duration: null })));
    setCurrentStep(-1);
    setLogs([]);
    addLog(`Cloning ${url}...`);

    setTimeout(() => {
      addLog('Repository cloned. Scanning project structure...');
      addLog('Detected: Node.js 20 + Express + PostgreSQL');
      addLog('AI generating deployment plan (12 steps)...');
      setTimeout(() => {
        setPhase('deploying');
        addLog('Deployment plan ready. Executing...');
        runStep(0);
      }, 1500);
    }, 2000);
  };

  const runStep = (idx) => {
    if (idx >= PLAN_STEPS.length) {
      setPhase('done');
      addLog('🎉 Deployment complete! Application is live.');
      return;
    }
    setCurrentStep(idx);
    setSteps(prev => prev.map((s, i) => i === idx ? { ...s, status: 'running' } : s));
    addLog(`[${PLAN_STEPS[idx].plugin}] ${PLAN_STEPS[idx].name}...`);

    const duration = PLAN_STEPS[idx].time * (0.6 + Math.random() * 0.8);
    setTimeout(() => {
      const secs = (duration / 1000).toFixed(1);
      setSteps(prev => prev.map((s, i) => i === idx ? { ...s, status: 'completed', duration: `${secs}s` } : s));
      addLog(`  ✓ Done (${secs}s)`);
      runStep(idx + 1);
    }, duration);
  };

  const statusIcon = (s) => {
    if (s === 'completed') return <CheckCircle size={16} color="#22d3ee" />;
    if (s === 'running') return <div style={{ width: 16, height: 16, border: '2px solid var(--accent-blue)', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />;
    if (s === 'failed') return <AlertCircle size={16} color="var(--accent-red)" />;
    return <Clock size={14} color="var(--text-muted)" style={{ opacity: 0.4 }} />;
  };

  const totalTime = steps.filter(s => s.duration).reduce((sum, s) => sum + parseFloat(s.duration), 0).toFixed(1);

  return (
    <div style={{ display: 'flex', height: '100%' }}>
      {/* Left: Pipeline */}
      <div style={{ flex: 1, padding: '20px', overflow: 'auto' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
          <Rocket size={22} color="var(--accent-blue)" />
          <h2 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 600 }}>AXLE Deploy</h2>
          {phase === 'done' && <span style={{ fontSize: '0.75rem', color: '#22d3ee', background: 'rgba(34,211,238,0.1)', padding: '4px 10px', borderRadius: '12px', fontWeight: 600 }}>LIVE</span>}
        </div>

        {/* URL Input */}
        <div style={{ display: 'flex', gap: '8px', marginBottom: '20px' }}>
          <input
            value={url}
            onChange={e => setUrl(e.target.value)}
            placeholder="https://github.com/user/repo"
            disabled={phase !== 'input'}
            style={{
              flex: 1, padding: '11px 16px', background: 'rgba(255,255,255,0.04)',
              border: '1px solid var(--panel-border)', borderRadius: '8px',
              color: '#fff', outline: 'none', fontSize: '0.88rem',
              fontFamily: 'var(--font-mono)', opacity: phase !== 'input' ? 0.5 : 1,
            }}
          />
          <button
            onClick={phase === 'input' ? startDeploy : phase === 'done' ? () => { setPhase('input'); setUrl(''); setSteps([]); setLogs([]); } : undefined}
            disabled={phase === 'scanning' || phase === 'deploying'}
            style={{
              padding: '11px 20px', background: phase === 'done' ? 'rgba(34,211,238,0.1)' : 'linear-gradient(135deg, rgba(0,240,255,0.12), rgba(139,92,246,0.12))',
              border: `1px solid ${phase === 'done' ? 'rgba(34,211,238,0.3)' : 'rgba(0,240,255,0.25)'}`,
              borderRadius: '8px', color: '#fff', cursor: phase === 'scanning' || phase === 'deploying' ? 'not-allowed' : 'pointer',
              fontWeight: 600, fontSize: '0.82rem', display: 'flex', alignItems: 'center', gap: '6px',
              opacity: phase === 'scanning' || phase === 'deploying' ? 0.5 : 1,
            }}
          >
            {phase === 'done' ? <>New Deploy</> : <><ArrowRight size={15} /> Deploy</>}
          </button>
        </div>

        {/* Steps */}
        {steps.length > 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '6px', display: 'flex', justifyContent: 'space-between' }}>
              <span>Pipeline — {steps.length} steps</span>
              {phase === 'done' && <span style={{ color: '#22d3ee' }}>Total: {totalTime}s</span>}
            </div>
            {steps.map((step, i) => (
              <div key={i} style={{
                display: 'flex', alignItems: 'center', gap: '10px',
                padding: '9px 12px',
                background: step.status === 'running' ? 'rgba(0,240,255,0.04)' : 'rgba(255,255,255,0.015)',
                borderRadius: '6px',
                borderLeft: `3px solid ${step.status === 'completed' ? '#22d3ee' : step.status === 'running' ? 'var(--accent-blue)' : 'rgba(255,255,255,0.04)'}`,
                transition: 'all 0.3s',
              }}>
                {statusIcon(step.status)}
                <span style={{ flex: 1, fontSize: '0.82rem', color: step.status === 'pending' ? 'var(--text-muted)' : 'var(--text-primary)' }}>
                  {step.name}
                </span>
                <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', minWidth: '55px', textAlign: 'right' }}>{step.plugin}</span>
                {step.duration && <span style={{ fontSize: '0.72rem', color: '#22d3ee', fontFamily: 'var(--font-mono)', minWidth: '40px', textAlign: 'right' }}>{step.duration}</span>}
              </div>
            ))}
          </div>
        )}

        {phase === 'done' && (
          <div style={{ marginTop: '16px', padding: '14px', background: 'rgba(34,211,238,0.05)', borderRadius: '8px', border: '1px solid rgba(34,211,238,0.15)', display: 'flex', alignItems: 'center', gap: '12px' }}>
            <CheckCircle size={20} color="#22d3ee" />
            <div>
              <div style={{ fontSize: '0.9rem', fontWeight: 600 }}>Application is live</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px', marginTop: '2px' }}>
                https://app.axle-os.local <ExternalLink size={12} />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Right: Live Logs */}
      <div style={{ width: '280px', borderLeft: '1px solid rgba(255,255,255,0.04)', display: 'flex', flexDirection: 'column' }}>
        <div style={{ padding: '12px 16px', borderBottom: '1px solid rgba(255,255,255,0.04)', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '1px', color: 'var(--text-muted)' }}>
          Live Logs
        </div>
        <div style={{ flex: 1, overflow: 'auto', padding: '10px', fontFamily: 'var(--font-mono)', fontSize: '0.72rem', lineHeight: 1.8 }}>
          {logs.map((log, i) => (
            <div key={i} style={{ color: log.msg.includes('✓') ? '#22d3ee' : log.msg.includes('🎉') ? '#22d3ee' : 'var(--text-muted)' }}>
              <span style={{ color: 'rgba(255,255,255,0.2)', marginRight: '6px' }}>{log.time}</span>
              {log.msg}
            </div>
          ))}
          <div ref={logsEndRef} />
        </div>
      </div>
    </div>
  );
}
