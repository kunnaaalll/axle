import React, { useState } from 'react';
import { Globe, ArrowLeft, ArrowRight, RotateCcw, Lock, Star, Zap, Activity, Rocket, Shield, BarChart3 } from 'lucide-react';

const PAGES = {
  'dashboard': {
    url: 'https://dashboard.axle-os.local:4000',
    title: 'AXLE Dashboard',
    content: (
      <div style={{ padding: '30px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
          <Zap size={28} color="#00f0ff" />
          <h1 style={{ margin: 0, fontSize: '1.5rem' }}>AXLE Dashboard</h1>
          <span style={{ fontSize: '0.75rem', background: 'rgba(0,240,255,0.1)', color: '#00f0ff', padding: '3px 10px', borderRadius: '10px' }}>v1.0.0</span>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '24px' }}>
          {[
            { label: 'CPU Load', value: '12.4%', color: '#00f0ff', icon: Activity },
            { label: 'RAM Usage', value: '1.2 GB', color: '#8b5cf6', icon: BarChart3 },
            { label: 'Active Deploys', value: '3', color: '#22d3ee', icon: Rocket },
          ].map(m => (
            <div key={m.label} style={{ padding: '20px', background: 'rgba(255,255,255,0.03)', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.05)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                <m.icon size={16} color={m.color} /> {m.label}
              </div>
              <div style={{ fontSize: '1.8rem', fontWeight: 700, color: m.color }}>{m.value}</div>
            </div>
          ))}
        </div>
        <div style={{ padding: '16px', background: 'rgba(34,211,238,0.05)', borderRadius: '10px', border: '1px solid rgba(34,211,238,0.15)' }}>
          <div style={{ fontSize: '0.85rem', fontWeight: 600, marginBottom: '8px' }}>Recent Deployments</div>
          {['nextjs-app → Completed (34.2s)', 'express-api → Completed (28.1s)', 'static-site → Completed (12.0s)'].map((d, i) => (
            <div key={i} style={{ fontSize: '0.82rem', color: 'var(--text-muted)', padding: '6px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#22d3ee' }} /> {d}
            </div>
          ))}
        </div>
      </div>
    ),
  },
  'blank': {
    url: '',
    title: 'New Tab',
    content: (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', gap: '16px' }}>
        <Globe size={56} color="var(--accent-blue)" style={{ opacity: 0.2 }} />
        <p style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>AXLE Browser</p>
        <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
          {['Dashboard', 'Docs', 'GitHub'].map(label => (
            <div key={label} style={{ padding: '10px 18px', background: 'rgba(255,255,255,0.03)', borderRadius: '8px', fontSize: '0.85rem', color: 'var(--text-secondary)', cursor: 'pointer' }}>
              {label}
            </div>
          ))}
        </div>
      </div>
    ),
  },
};

export default function BrowserApp() {
  const [page, setPage] = useState('dashboard');
  const [urlInput, setUrlInput] = useState(PAGES.dashboard.url);

  const currentPage = PAGES[page] || PAGES.blank;

  const navigate = (key) => {
    setPage(key);
    setUrlInput(PAGES[key]?.url || '');
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Toolbar */}
      <div style={{ padding: '6px 10px', background: 'rgba(0,0,0,0.25)', borderBottom: '1px solid rgba(255,255,255,0.04)', display: 'flex', alignItems: 'center', gap: '6px' }}>
        <button onClick={() => navigate('blank')} style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', padding: '4px' }}><ArrowLeft size={16} /></button>
        <button style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', padding: '4px' }}><ArrowRight size={16} /></button>
        <button onClick={() => navigate(page)} style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', padding: '4px' }}><RotateCcw size={14} /></button>
        <div style={{
          flex: 1, display: 'flex', alignItems: 'center', gap: '6px',
          padding: '7px 14px', background: 'rgba(255,255,255,0.04)',
          borderRadius: '20px', fontSize: '0.8rem', color: 'var(--text-muted)',
        }}>
          <Lock size={12} color="#22d3ee" />
          <input
            value={urlInput}
            onChange={e => setUrlInput(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') navigate(urlInput.includes('dashboard') ? 'dashboard' : 'blank'); }}
            style={{ flex: 1, background: 'transparent', border: 'none', outline: 'none', color: 'var(--text-secondary)', fontSize: '0.8rem' }}
          />
        </div>
        <button onClick={() => navigate('dashboard')} style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', padding: '4px' }}><Star size={14} /></button>
      </div>

      {/* Tab bar */}
      <div style={{ padding: '0 10px', background: 'rgba(0,0,0,0.15)', display: 'flex', alignItems: 'center', gap: '2px', borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
        <div style={{
          padding: '8px 16px', fontSize: '0.78rem', color: 'var(--text-secondary)',
          background: 'rgba(255,255,255,0.04)', borderRadius: '8px 8px 0 0',
          display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer',
        }}>
          <Globe size={12} /> {currentPage.title}
          <span style={{ color: 'var(--text-muted)', marginLeft: '8px', cursor: 'pointer' }}>×</span>
        </div>
      </div>

      {/* Content */}
      <div style={{ flex: 1, overflow: 'auto', background: 'var(--panel-bg-solid)' }}>
        {currentPage.content}
      </div>
    </div>
  );
}
