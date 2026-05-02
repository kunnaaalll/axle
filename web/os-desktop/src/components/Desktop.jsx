import React, { useState, useCallback } from 'react';
import Window from './Window';
import Taskbar from './Taskbar';
import AppLauncher from './AppLauncher';
import TerminalApp from './TerminalApp';
import FileManagerApp from './FileManagerApp';
import SettingsApp from './SettingsApp';
import DeployApp from './DeployApp';
import { Terminal, FolderOpen, Settings, Rocket, Shield, MessageSquare, Globe, BarChart3 } from 'lucide-react';

const APP_DEFS = {
  terminal:  { title: 'Terminal', icon: '🖥️', component: TerminalApp, size: { w: 720, h: 460 } },
  files:     { title: 'Files', icon: '📁', component: FileManagerApp, size: { w: 780, h: 500 } },
  settings:  { title: 'Settings', icon: '⚙️', component: SettingsApp, size: { w: 750, h: 520 } },
  deploy:    { title: 'AXLE Deploy', icon: '🚀', component: DeployApp, size: { w: 700, h: 550 } },
  vault:     { title: 'Secrets Vault', icon: '🔐', component: VaultStub, size: { w: 600, h: 400 } },
  chat:      { title: 'AI Copilot', icon: '🤖', component: ChatStub, size: { w: 650, h: 480 } },
  browser:   { title: 'Browser', icon: '🌐', component: BrowserStub, size: { w: 900, h: 600 } },
  monitor:   { title: 'System Monitor', icon: '📊', component: MonitorStub, size: { w: 660, h: 440 } },
};

function VaultStub() {
  return (
    <div style={{ padding: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
        <Shield size={24} color="var(--accent-purple)" />
        <h2 style={{ margin: 0, fontSize: '1.2rem' }}>Secrets Vault</h2>
      </div>
      <p style={{ color: 'var(--text-muted)', marginBottom: '20px', fontSize: '0.9rem' }}>AES-256 encrypted environment variables</p>
      {['DATABASE_URL', 'GEMINI_API_KEY', 'STRIPE_SECRET', 'JWT_SECRET', 'REDIS_URL'].map(k => (
        <div key={k} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 16px', background: 'rgba(255,255,255,0.02)', borderRadius: '8px', marginBottom: '6px' }}>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem', color: 'var(--accent-purple)' }}>{k}</span>
          <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>••••••••••••</span>
        </div>
      ))}
    </div>
  );
}

function ChatStub() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ padding: '16px 20px', borderBottom: '1px solid rgba(255,255,255,0.04)', display: 'flex', alignItems: 'center', gap: '10px' }}>
        <MessageSquare size={20} color="var(--accent-blue)" />
        <span style={{ fontWeight: 600 }}>AXLE Copilot</span>
      </div>
      <div style={{ flex: 1, padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px', overflow: 'auto' }}>
        <div style={{ alignSelf: 'flex-start', maxWidth: '70%', padding: '14px 18px', background: 'rgba(255,255,255,0.04)', borderRadius: '12px 12px 12px 0', fontSize: '0.9rem', lineHeight: 1.6 }}>
          Hello! I'm the AXLE AI Copilot. I can help you with deployments, infrastructure debugging, and server configuration. What would you like to do?
        </div>
        <div style={{ alignSelf: 'flex-end', maxWidth: '70%', padding: '14px 18px', background: 'rgba(0,240,255,0.08)', border: '1px solid rgba(0,240,255,0.2)', borderRadius: '12px 12px 0 12px', fontSize: '0.9rem', lineHeight: 1.6 }}>
          Can you check if my PostgreSQL database is healthy?
        </div>
        <div style={{ alignSelf: 'flex-start', maxWidth: '70%', padding: '14px 18px', background: 'rgba(255,255,255,0.04)', borderRadius: '12px 12px 12px 0', fontSize: '0.9rem', lineHeight: 1.6 }}>
          I've checked your PostgreSQL instance. Here's the status:<br/><br/>
          <span style={{ color: 'var(--accent-green)' }}>● Active</span> — 3 connections, 0.2% CPU<br/>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--text-muted)' }}>Version: 16.2, Uptime: 72h, DB Size: 142MB</span>
        </div>
      </div>
      <div style={{ padding: '16px', borderTop: '1px solid rgba(255,255,255,0.04)', display: 'flex', gap: '10px' }}>
        <input placeholder="Ask about your infrastructure..." style={{ flex: 1, padding: '12px 16px', background: 'rgba(255,255,255,0.04)', border: '1px solid var(--panel-border)', borderRadius: '10px', color: '#fff', outline: 'none', fontSize: '0.9rem' }} />
      </div>
    </div>
  );
}

function BrowserStub() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ padding: '8px 12px', background: 'rgba(0,0,0,0.3)', display: 'flex', alignItems: 'center', gap: '8px', borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
        <div style={{ flex: 1, padding: '8px 14px', background: 'rgba(255,255,255,0.04)', borderRadius: '20px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          🔒 https://dashboard.axle-os.local:4000
        </div>
      </div>
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: '16px' }}>
        <Globe size={48} color="var(--accent-blue)" style={{ opacity: 0.3 }} />
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>AXLE Dashboard running at localhost:4000</p>
      </div>
    </div>
  );
}

function MonitorStub() {
  return (
    <div style={{ padding: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
        <BarChart3 size={24} color="var(--accent-green)" />
        <h2 style={{ margin: 0, fontSize: '1.2rem' }}>System Monitor</h2>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
        {[
          { label: 'CPU', value: '12%', color: 'var(--accent-blue)' },
          { label: 'Memory', value: '1.2 / 4.0 GB', color: 'var(--accent-purple)' },
          { label: 'Disk', value: '8.2 / 30 GB', color: 'var(--accent-orange)' },
          { label: 'Network', value: '↑ 2.1 MB/s  ↓ 540 KB/s', color: 'var(--accent-green)' },
        ].map(m => (
          <div key={m.label} style={{ padding: '16px', background: 'rgba(255,255,255,0.02)', borderRadius: '10px', borderLeft: `3px solid ${m.color}` }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '1px' }}>{m.label}</div>
            <div style={{ fontSize: '1.1rem', fontWeight: 600, color: m.color }}>{m.value}</div>
          </div>
        ))}
      </div>
      <div style={{ marginTop: '20px', padding: '14px', background: 'rgba(255,255,255,0.02)', borderRadius: '10px' }}>
        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '1px' }}>Running Services</div>
        {['axle-api.service', 'axle-dashboard.service', 'nginx.service', 'postgresql.service'].map(s => (
          <div key={s} style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '6px 0', fontSize: '0.85rem' }}>
            <div style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--accent-green)', boxShadow: '0 0 6px var(--accent-green)' }} />
            <span style={{ fontFamily: 'var(--font-mono)' }}>{s}</span>
            <span style={{ marginLeft: 'auto', color: 'var(--accent-green)', fontSize: '0.8rem' }}>active</span>
          </div>
        ))}
      </div>
    </div>
  );
}

let windowCounter = 0;

export default function Desktop() {
  const [windows, setWindows] = useState([]);
  const [activeWindow, setActiveWindow] = useState(null);
  const [showLauncher, setShowLauncher] = useState(false);
  const [contextMenu, setContextMenu] = useState(null);

  const launchApp = useCallback((appId) => {
    const def = APP_DEFS[appId];
    if (!def) return;
    const id = `${appId}-${++windowCounter}`;
    const offset = (windows.length % 6) * 30;
    setWindows(prev => [...prev, {
      id, appId, title: def.title, icon: def.icon,
      pos: { x: 100 + offset, y: 50 + offset },
      size: def.size,
    }]);
    setActiveWindow(id);
  }, [windows.length]);

  const closeWindow = useCallback((id) => {
    setWindows(prev => prev.filter(w => w.id !== id));
    setActiveWindow(prev => prev === id ? null : prev);
  }, []);

  const focusWindow = useCallback((id) => setActiveWindow(id), []);

  const handleDesktopContextMenu = (e) => {
    e.preventDefault();
    setContextMenu({ x: e.clientX, y: e.clientY });
  };

  const desktopIcons = [
    { id: 'terminal', label: 'Terminal', icon: '🖥️' },
    { id: 'files', label: 'Files', icon: '📁' },
    { id: 'deploy', label: 'AXLE Deploy', icon: '🚀' },
    { id: 'settings', label: 'Settings', icon: '⚙️' },
  ];

  return (
    <div
      className="desktop"
      style={{ backgroundImage: 'url(/wallpaper.png)' }}
      onClick={() => { setShowLauncher(false); setContextMenu(null); }}
      onContextMenu={handleDesktopContextMenu}
    >
      <div className="desktop-area">
        {/* Desktop Icons */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', position: 'absolute', top: 20, left: 20 }}>
          {desktopIcons.map(di => (
            <div key={di.id} className="desktop-icon" onDoubleClick={() => launchApp(di.id)}>
              <div className="desktop-icon-img" style={{ fontSize: '2rem' }}>{di.icon}</div>
              <div className="desktop-icon-label">{di.label}</div>
            </div>
          ))}
        </div>

        {/* Notification area */}
        <div className="notification-area">
          <div className="notification animate-slideUp" style={{ animationDelay: '1s', animationFillMode: 'both' }}>
            <div className="notification-icon" style={{ background: 'rgba(0,240,255,0.1)' }}>
              <span>🚀</span>
            </div>
            <div>
              <div className="notification-title">Deployment Complete</div>
              <div className="notification-body">nextjs-app deployed successfully in 34.2s</div>
            </div>
          </div>
        </div>

        {/* Windows */}
        {windows.map((win, i) => {
          const def = APP_DEFS[win.appId];
          if (!def) return null;
          const Comp = def.component;
          return (
            <Window
              key={win.id}
              id={win.id}
              title={win.title}
              icon={win.icon}
              initialPos={win.pos}
              initialSize={win.size}
              onClose={closeWindow}
              onFocus={focusWindow}
              zIndex={activeWindow === win.id ? 200 : 100 + i}
            >
              <Comp />
            </Window>
          );
        })}

        {/* Context Menu */}
        {contextMenu && (
          <div className="context-menu" style={{ left: contextMenu.x, top: contextMenu.y }} onClick={e => e.stopPropagation()}>
            <div className="context-menu-item" onClick={() => { launchApp('terminal'); setContextMenu(null); }}>🖥️ Open Terminal</div>
            <div className="context-menu-item" onClick={() => { launchApp('files'); setContextMenu(null); }}>📁 Open Files</div>
            <div className="context-menu-divider" />
            <div className="context-menu-item" onClick={() => { launchApp('settings'); setContextMenu(null); }}>⚙️ Settings</div>
            <div className="context-menu-item" onClick={() => { launchApp('deploy'); setContextMenu(null); }}>🚀 New Deployment</div>
            <div className="context-menu-divider" />
            <div className="context-menu-item" onClick={() => setContextMenu(null)}>🖼️ Change Wallpaper</div>
          </div>
        )}

        {/* App Launcher */}
        {showLauncher && (
          <AppLauncher onLaunch={launchApp} onClose={() => setShowLauncher(false)} />
        )}
      </div>

      <Taskbar
        openWindows={windows}
        activeWindow={activeWindow}
        showStart={showLauncher}
        onStartClick={() => setShowLauncher(!showLauncher)}
        onWindowClick={focusWindow}
      />
    </div>
  );
}
