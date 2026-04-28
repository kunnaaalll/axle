import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Lock, Zap } from 'lucide-react';

export default function Login() {
  const { login, loading, error } = useAuth();
  const [password, setPassword] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    await login(password);
  };

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: '100vh',
      width: '100vw',
      background: 'var(--bg-dark)',
      backgroundImage: `
        radial-gradient(circle at 30% 40%, rgba(139, 92, 246, 0.08) 0%, transparent 50%),
        radial-gradient(circle at 70% 60%, rgba(0, 240, 255, 0.08) 0%, transparent 50%)
      `,
    }}>
      <div className="glass-panel" style={{
        padding: '3rem',
        width: '100%',
        maxWidth: '420px',
        textAlign: 'center',
      }}>
        {/* Logo */}
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          gap: '12px',
          marginBottom: '2rem',
        }}>
          <div style={{
            width: '48px',
            height: '48px',
            background: 'linear-gradient(135deg, var(--accent-blue), var(--accent-purple))',
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 30px rgba(0,240,255,0.3)',
          }}>
            <Zap size={28} color="#fff" />
          </div>
          <h1 style={{
            margin: 0,
            fontSize: '1.8rem',
            letterSpacing: '3px',
            background: 'linear-gradient(to right, #fff, var(--accent-blue))',
            WebkitBackgroundClip: 'text',
            backgroundClip: 'text',
            color: 'transparent',
          }}>
            AXLE OS
          </h1>
        </div>

        <p style={{ color: 'var(--text-muted)', marginBottom: '2rem', fontSize: '0.95rem' }}>
          Authenticate to access the deployment engine
        </p>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ position: 'relative' }}>
            <Lock size={18} style={{
              position: 'absolute',
              left: '14px',
              top: '50%',
              transform: 'translateY(-50%)',
              color: 'var(--text-muted)',
            }} />
            <input
              type="password"
              placeholder="Enter admin password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoFocus
              style={{
                width: '100%',
                padding: '14px 14px 14px 44px',
                background: 'rgba(0,0,0,0.4)',
                border: '1px solid var(--panel-border)',
                borderRadius: '8px',
                color: '#fff',
                fontSize: '1rem',
                outline: 'none',
                transition: 'border-color 0.2s',
              }}
              onFocus={(e) => e.target.style.borderColor = 'var(--accent-blue)'}
              onBlur={(e) => e.target.style.borderColor = 'var(--panel-border)'}
            />
          </div>

          {error && (
            <div style={{
              padding: '10px 14px',
              background: 'rgba(255,51,102,0.1)',
              border: '1px solid rgba(255,51,102,0.3)',
              borderRadius: '6px',
              color: 'var(--accent-red)',
              fontSize: '0.9rem',
            }}>
              {error}
            </div>
          )}

          <button
            type="submit"
            className="btn-glow"
            disabled={loading}
            style={{
              padding: '14px',
              fontSize: '1rem',
              width: '100%',
              opacity: loading ? 0.7 : 1,
            }}
          >
            {loading ? 'AUTHENTICATING...' : 'SIGN IN'}
          </button>
        </form>

        <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: '2rem', opacity: 0.5 }}>
          AXLE OS v1.0.0 — Autonomous Deployment Engine
        </p>
      </div>
    </div>
  );
}
