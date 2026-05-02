import React, { useState, useEffect } from 'react';
import { User } from 'lucide-react';

export default function LoginScreen({ onLogin }) {
  const [password, setPassword] = useState('');
  const [time, setTime] = useState(new Date());
  const [error, setError] = useState(false);
  const [shaking, setShaking] = useState(false);

  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (password.length > 0) {
      onLogin();
    } else {
      setError(true);
      setShaking(true);
      setTimeout(() => setShaking(false), 500);
    }
  };

  const formatTime = (d) => d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
  const formatDate = (d) => d.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' });

  return (
    <div className="login-screen" style={{ backgroundImage: 'url(/wallpaper.png)' }}>
      <div className="login-overlay" />
      <div className="login-card">
        <div className="login-time">{formatTime(time)}</div>
        <div className="login-date">{formatDate(time)}</div>
        <div className="login-avatar">
          <User size={44} color="#fff" />
        </div>
        <div className="login-username">admin</div>
        <form onSubmit={handleSubmit}>
          <input
            className="login-input"
            type="password"
            placeholder="Enter password"
            value={password}
            onChange={(e) => { setPassword(e.target.value); setError(false); }}
            autoFocus
            style={{
              animation: shaking ? 'shake 0.4s ease' : 'none',
              borderColor: error ? 'var(--accent-red)' : undefined,
            }}
          />
        </form>
        <p style={{ marginTop: '1rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          Press Enter to sign in
        </p>
      </div>
      <style>{`
        @keyframes shake {
          0%,100% { transform: translateX(0); }
          20%,60% { transform: translateX(-8px); }
          40%,80% { transform: translateX(8px); }
        }
      `}</style>
    </div>
  );
}
