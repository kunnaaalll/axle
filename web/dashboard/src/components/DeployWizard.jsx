import React, { useState, useEffect } from 'react';
import { io } from 'socket.io-client';

export default function DeployWizard() {
  const [repoUrl, setRepoUrl] = useState('');
  const [provider, setProvider] = useState('Google Gemini');
  const [status, setStatus] = useState('idle');
  const [plan, setPlan] = useState(null);
  const [error, setError] = useState(null);
  const [logs, setLogs] = useState([]);

  // Setup WebSocket for live logs
  useEffect(() => {
    const socket = io('http://localhost:4000');
    socket.on('server_message', (msg) => {
      setLogs((prev) => [...prev, `[system] ${msg.data}`]);
    });
    socket.on('log_stream', (msg) => {
      setLogs((prev) => [...prev, msg.line]);
    });
    return () => socket.disconnect();
  }, []);

  const handleDeploy = async (e) => {
    e.preventDefault();
    setStatus('planning');
    setError(null);
    setLogs([]);

    try {
      const res = await fetch('http://localhost:4000/deploy/', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': 'Bearer DUMMY_TOKEN'
        },
        body: JSON.stringify({ url: repoUrl, provider })
      });
      const data = await res.json();
      if (!data.success) {
        setError(data.error);
        setStatus('idle');
      } else {
        pollStatus();
      }
    } catch (err) {
      setError(String(err));
      setStatus('idle');
    }
  };

  const pollStatus = async () => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch('http://localhost:4000/deploy/status', {
          headers: { 'Authorization': 'Bearer DUMMY_TOKEN' }
        });
        const data = await res.json();
        
        if (data.success) {
          setStatus(data.status);
          setPlan(data.plan);
          if (data.error) setError(data.error);
          
          if (data.status === 'completed' || data.status === 'failed') {
            clearInterval(interval);
          }
        }
      } catch(err) {
        console.error(err);
      }
    }, 2000);
  };

  return (
    <div className="glass-panel" style={{ padding: '2rem' }}>
      <h1>Deployment Wizard</h1>
      <p style={{ color: 'var(--text-muted)' }}>Provide a GitHub repository URL to initiate an autonomous deployment.</p>
      
      <form onSubmit={handleDeploy} style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem', flexWrap: 'wrap' }}>
        <input 
          type="text" 
          placeholder="https://github.com/kunnaaalll/repo" 
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          style={{ flex: '1', minWidth: '300px', padding: '12px', background: 'rgba(0,0,0,0.5)', border: '1px solid var(--panel-border)', color: '#fff', borderRadius: '6px' }}
          disabled={status !== 'idle' && status !== 'completed' && status !== 'failed'}
          required
        />
        <select 
          value={provider}
          onChange={(e) => setProvider(e.target.value)}
          style={{ padding: '12px', background: 'rgba(0,0,0,0.5)', border: '1px solid var(--panel-border)', color: '#fff', borderRadius: '6px' }}
          disabled={status !== 'idle' && status !== 'completed' && status !== 'failed'}
        >
          <option>Google Gemini</option>
          <option>OpenAI</option>
          <option>Local (Ollama)</option>
        </select>
        <button type="submit" className="btn-glow" disabled={status !== 'idle' && status !== 'completed' && status !== 'failed'}>
          {status === 'idle' ? 'START DEPLOYMENT' : 'DEPLOYING...'}
        </button>
      </form>

      {error && <div style={{ color: 'var(--accent-red)', marginTop: '1rem', padding: '1rem', background: 'rgba(255,0,0,0.1)', borderRadius: '6px' }}>Error: {error}</div>}

      <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem', flexWrap: 'wrap' }}>
        {/* Plan Section */}
        <div className="glass-panel" style={{ flex: 1, minWidth: '300px', padding: '1.5rem' }}>
          <h3>Deployment Plan</h3>
          {status === 'idle' && !plan && <p style={{ color: 'var(--text-muted)' }}>Waiting for AI execution engine...</p>}
          {status === 'planning' && <p style={{ color: 'var(--accent-blue)' }}><span className="status-indicator"></span> AI Analyzing Repository...</p>}
          {plan && (
            <div>
              <p><strong>Stack:</strong> {plan.profile?.stack}</p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '1rem' }}>
                {plan.steps && plan.steps.map((step, idx) => (
                  <div key={idx} style={{ 
                    padding: '8px 12px', 
                    background: 'rgba(255,255,255,0.05)', 
                    borderRadius: '6px',
                    borderLeft: step.status === 'completed' ? '3px solid var(--accent-blue)' : step.status === 'failed' ? '3px solid var(--accent-red)' : '3px solid var(--text-muted)'
                  }}>
                    <strong style={{ display: 'block' }}>{step.name}</strong>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)'}}>{step.action} </span>
                    <span style={{ fontSize: '0.8rem', color: step.status === 'pending' ? 'var(--text-muted)' : step.status === 'failed' ? 'var(--accent-red)' : 'var(--accent-blue)'}}>[{step.status}]</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Live Logs Terminal */}
        <div className="glass-panel" style={{ flex: 1, minWidth: '300px', padding: '1.5rem', background: '#000' }}>
          <h3 style={{ borderBottom: '1px solid #333', paddingBottom: '0.5rem', marginBottom: '1rem' }}>Live Console</h3>
          <div style={{ fontFamily: 'monospace', fontSize: '0.85rem', color: '#0f0', height: '300px', overflowY: 'auto' }}>
            {logs.length === 0 ? <span style={{ color: '#555' }}>Waiting for output...</span> : null}
            {logs.map((log, i) => <div key={i}>{log}</div>)}
          </div>
        </div>
      </div>
    </div>
  );
}
