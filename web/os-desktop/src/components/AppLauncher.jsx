import React, { useState } from 'react';
import { Search, Terminal, FolderOpen, Settings, Rocket, Shield, MessageSquare, Globe, Power } from 'lucide-react';

const apps = [
  { id: 'terminal', name: 'Terminal', icon: '🖥️', iconComponent: Terminal, color: '#1a1a2e' },
  { id: 'files', name: 'Files', icon: '📁', iconComponent: FolderOpen, color: '#1e3a5f' },
  { id: 'settings', name: 'Settings', icon: '⚙️', iconComponent: Settings, color: '#2d2d44' },
  { id: 'deploy', name: 'AXLE Deploy', icon: '🚀', iconComponent: Rocket, color: '#0a2540' },
  { id: 'vault', name: 'Secrets Vault', icon: '🔐', iconComponent: Shield, color: '#1a0a2e' },
  { id: 'chat', name: 'AI Copilot', icon: '🤖', iconComponent: MessageSquare, color: '#0a1a2e' },
  { id: 'browser', name: 'Browser', icon: '🌐', iconComponent: Globe, color: '#1a2a3e' },
  { id: 'monitor', name: 'System Monitor', icon: '📊', iconComponent: null, color: '#0a2e1a' },
];

export default function AppLauncher({ onLaunch, onClose }) {
  const [search, setSearch] = useState('');
  const filtered = apps.filter(a => a.name.toLowerCase().includes(search.toLowerCase()));

  return (
    <div className="app-launcher" onClick={e => e.stopPropagation()}>
      <div className="app-launcher-search">
        <input
          placeholder="Search applications..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          autoFocus
        />
      </div>
      <div className="app-launcher-grid">
        {filtered.map(app => (
          <button
            key={app.id}
            className="app-launcher-item"
            onClick={() => { onLaunch(app.id); onClose(); }}
          >
            <div
              className="app-launcher-icon"
              style={{ background: app.color, border: '1px solid rgba(255,255,255,0.06)' }}
            >
              {app.iconComponent ? <app.iconComponent size={22} color="var(--accent-blue)" /> : <span>{app.icon}</span>}
            </div>
            <span className="app-launcher-label">{app.name}</span>
          </button>
        ))}
      </div>
      <div className="app-launcher-footer">
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>AXLE OS v1.0.0</span>
        <button
          style={{
            display: 'flex', alignItems: 'center', gap: '6px',
            background: 'transparent', border: 'none', color: 'var(--accent-red)',
            cursor: 'pointer', fontSize: '0.8rem', padding: '6px 10px', borderRadius: '6px',
          }}
        >
          <Power size={14} /> Shut Down
        </button>
      </div>
    </div>
  );
}

export { apps };
