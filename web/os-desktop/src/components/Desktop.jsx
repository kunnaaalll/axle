import React, { useState, useCallback, useEffect } from 'react';
import Window from './Window';
import Taskbar from './Taskbar';
import AppLauncher from './AppLauncher';
import TerminalApp from './TerminalApp';
import FileManagerApp from './FileManagerApp';
import SettingsApp from './SettingsApp';
import DeployApp from './DeployApp';
import VaultApp from './VaultApp';
import ChatApp from './ChatApp';
import BrowserApp from './BrowserApp';
import MonitorApp from './MonitorApp';

const APP_DEFS = {
  terminal: { title: 'Terminal', icon: '🖥️', component: TerminalApp, size: { w: 720, h: 460 } },
  files:    { title: 'Files', icon: '📁', component: FileManagerApp, size: { w: 780, h: 500 } },
  settings: { title: 'Settings', icon: '⚙️', component: SettingsApp, size: { w: 750, h: 520 } },
  deploy:   { title: 'AXLE Deploy', icon: '🚀', component: DeployApp, size: { w: 800, h: 560 } },
  vault:    { title: 'Secrets Vault', icon: '🔐', component: VaultApp, size: { w: 680, h: 450 } },
  chat:     { title: 'AI Copilot', icon: '🤖', component: ChatApp, size: { w: 650, h: 500 } },
  browser:  { title: 'Browser', icon: '🌐', component: BrowserApp, size: { w: 900, h: 600 } },
  monitor:  { title: 'System Monitor', icon: '📊', component: MonitorApp, size: { w: 660, h: 520 } },
};

let windowCounter = 0;

export default function Desktop() {
  const [windows, setWindows] = useState([]);
  const [activeWindow, setActiveWindow] = useState(null);
  const [showLauncher, setShowLauncher] = useState(false);
  const [contextMenu, setContextMenu] = useState(null);
  const [minimizedWindows, setMinimizedWindows] = useState(new Set());
  const [notifications, setNotifications] = useState([
    { id: 1, icon: '🚀', title: 'Deployment Complete', body: 'nextjs-app deployed successfully in 34.2s' },
  ]);

  // Auto-dismiss notifications
  useEffect(() => {
    if (notifications.length === 0) return;
    const timer = setTimeout(() => {
      setNotifications(prev => prev.slice(1));
    }, 6000);
    return () => clearTimeout(timer);
  }, [notifications]);

  const launchApp = useCallback((appId) => {
    const def = APP_DEFS[appId];
    if (!def) return;

    // If already open, focus it
    const existing = windows.find(w => w.appId === appId && !minimizedWindows.has(w.id));
    if (existing) {
      setActiveWindow(existing.id);
      return;
    }

    // If minimized, restore it
    const minimized = windows.find(w => w.appId === appId && minimizedWindows.has(w.id));
    if (minimized) {
      setMinimizedWindows(prev => { const next = new Set(prev); next.delete(minimized.id); return next; });
      setActiveWindow(minimized.id);
      return;
    }

    const id = `${appId}-${++windowCounter}`;
    const offset = (windows.length % 8) * 30;
    setWindows(prev => [...prev, { id, appId, title: def.title, icon: def.icon }]);
    setActiveWindow(id);
    // Use timeout to trigger animation
    setTimeout(() => setActiveWindow(id), 10);
  }, [windows, minimizedWindows]);

  const closeWindow = useCallback((id) => {
    setWindows(prev => prev.filter(w => w.id !== id));
    setMinimizedWindows(prev => { const next = new Set(prev); next.delete(id); return next; });
    setActiveWindow(prev => prev === id ? null : prev);
  }, []);

  const minimizeWindow = useCallback((id) => {
    setMinimizedWindows(prev => { const next = new Set(prev); next.add(id); return next; });
    setActiveWindow(prev => prev === id ? null : prev);
  }, []);

  const focusWindow = useCallback((id) => {
    if (minimizedWindows.has(id)) {
      setMinimizedWindows(prev => { const next = new Set(prev); next.delete(id); return next; });
    }
    setActiveWindow(id);
  }, [minimizedWindows]);

  const handleDesktopContextMenu = (e) => {
    e.preventDefault();
    setContextMenu({ x: e.clientX, y: e.clientY });
  };

  const dismissNotification = (id) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  const desktopIcons = [
    { id: 'terminal', label: 'Terminal', icon: '🖥️' },
    { id: 'files', label: 'Files', icon: '📁' },
    { id: 'deploy', label: 'AXLE Deploy', icon: '🚀' },
    { id: 'settings', label: 'Settings', icon: '⚙️' },
    { id: 'monitor', label: 'System Monitor', icon: '📊' },
    { id: 'chat', label: 'AI Copilot', icon: '🤖' },
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
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', position: 'absolute', top: 16, left: 16 }}>
          {desktopIcons.map(di => (
            <div key={di.id} className="desktop-icon" onDoubleClick={() => launchApp(di.id)}>
              <div className="desktop-icon-img" style={{ fontSize: '2rem' }}>{di.icon}</div>
              <div className="desktop-icon-label">{di.label}</div>
            </div>
          ))}
        </div>

        {/* Notifications */}
        {notifications.length > 0 && (
          <div className="notification-area">
            {notifications.map(n => (
              <div key={n.id} className="notification animate-slideUp" onClick={() => dismissNotification(n.id)} style={{ cursor: 'pointer' }}>
                <div className="notification-icon" style={{ background: 'rgba(0,240,255,0.1)' }}>
                  <span>{n.icon}</span>
                </div>
                <div style={{ flex: 1 }}>
                  <div className="notification-title">{n.title}</div>
                  <div className="notification-body">{n.body}</div>
                </div>
                <span style={{ color: 'var(--text-muted)', fontSize: '0.7rem', cursor: 'pointer' }}>✕</span>
              </div>
            ))}
          </div>
        )}

        {/* Windows */}
        {windows.map((win, i) => {
          if (minimizedWindows.has(win.id)) return null;
          const def = APP_DEFS[win.appId];
          if (!def) return null;
          const Comp = def.component;
          const offset = (i % 8) * 30;
          return (
            <Window
              key={win.id}
              id={win.id}
              title={win.title}
              icon={win.icon}
              initialPos={{ x: 120 + offset, y: 40 + offset }}
              initialSize={def.size}
              onClose={closeWindow}
              onMinimize={minimizeWindow}
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
            <div className="context-menu-item" onClick={() => { launchApp('deploy'); setContextMenu(null); }}>🚀 New Deployment</div>
            <div className="context-menu-item" onClick={() => { launchApp('monitor'); setContextMenu(null); }}>📊 System Monitor</div>
            <div className="context-menu-divider" />
            <div className="context-menu-item" onClick={() => { launchApp('settings'); setContextMenu(null); }}>⚙️ Settings</div>
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
        minimizedWindows={minimizedWindows}
      />
    </div>
  );
}
