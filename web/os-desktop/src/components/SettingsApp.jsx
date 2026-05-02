import React, { useState } from 'react';
import { Monitor, Palette, Shield, Wifi, Bell, User, Zap, Volume2, Sun } from 'lucide-react';

const sections = [
  { id: 'appearance', label: 'Appearance', icon: Palette },
  { id: 'display', label: 'Display', icon: Monitor },
  { id: 'network', label: 'Network', icon: Wifi },
  { id: 'notifications', label: 'Notifications', icon: Bell },
  { id: 'sound', label: 'Sound', icon: Volume2 },
  { id: 'security', label: 'Security', icon: Shield },
  { id: 'ai', label: 'AI Engine', icon: Zap },
  { id: 'account', label: 'Account', icon: User },
];

function Toggle({ on, onClick }) {
  return <button className={`toggle ${on ? 'on' : ''}`} onClick={onClick} />;
}

function SettingsRow({ label, desc, children }) {
  return (
    <div className="settings-row">
      <div>
        <div className="settings-row-label">{label}</div>
        {desc && <div className="settings-row-desc">{desc}</div>}
      </div>
      {children}
    </div>
  );
}

export default function SettingsApp() {
  const [active, setActive] = useState('appearance');
  const [darkMode, setDarkMode] = useState(true);
  const [autoUpdate, setAutoUpdate] = useState(true);
  const [notifications, setNotifications] = useState(true);
  const [aiProvider, setAiProvider] = useState('gemini');

  const content = {
    appearance: (
      <>
        <div className="settings-section">
          <h3>Theme</h3>
          <SettingsRow label="Dark Mode" desc="Use dark theme across the system">
            <Toggle on={darkMode} onClick={() => setDarkMode(!darkMode)} />
          </SettingsRow>
          <SettingsRow label="Accent Color" desc="System-wide accent color">
            <div style={{ display: 'flex', gap: '8px' }}>
              {['#00f0ff', '#8b5cf6', '#22d3ee', '#ec4899', '#f59e0b'].map(c => (
                <div key={c} style={{ width: 24, height: 24, borderRadius: '50%', background: c, cursor: 'pointer', border: '2px solid transparent' }} />
              ))}
            </div>
          </SettingsRow>
        </div>
        <div className="settings-section">
          <h3>Wallpaper</h3>
          <SettingsRow label="Desktop Background" desc="Current: axle-default.png">
            <button style={{ padding: '6px 14px', background: 'rgba(0,240,255,0.1)', border: '1px solid rgba(0,240,255,0.3)', borderRadius: '6px', color: '#fff', cursor: 'pointer', fontSize: '0.8rem' }}>
              Change
            </button>
          </SettingsRow>
        </div>
      </>
    ),
    display: (
      <div className="settings-section">
        <h3>Display Settings</h3>
        <SettingsRow label="Resolution" desc="3840 × 2160 (4K)">
          <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Recommended</span>
        </SettingsRow>
        <SettingsRow label="Scale" desc="Interface scaling factor">
          <span style={{ color: 'var(--accent-blue)', fontSize: '0.85rem' }}>200%</span>
        </SettingsRow>
        <SettingsRow label="Night Light" desc="Reduce blue light in the evening">
          <Toggle on={false} />
        </SettingsRow>
      </div>
    ),
    network: (
      <div className="settings-section">
        <h3>Network</h3>
        <SettingsRow label="Ethernet (eth0)" desc="Connected — 172.31.16.42">
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <div style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--accent-green)', boxShadow: '0 0 6px var(--accent-green)' }} />
            <span style={{ fontSize: '0.8rem', color: 'var(--accent-green)' }}>Active</span>
          </div>
        </SettingsRow>
        <SettingsRow label="Public IP" desc="Accessible from the internet">
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem' }}>54.123.45.67</span>
        </SettingsRow>
        <SettingsRow label="Firewall (UFW)" desc="Active with 3 rules">
          <Toggle on={true} />
        </SettingsRow>
      </div>
    ),
    notifications: (
      <div className="settings-section">
        <h3>Notifications</h3>
        <SettingsRow label="Enable Notifications" desc="Show system and deployment alerts">
          <Toggle on={notifications} onClick={() => setNotifications(!notifications)} />
        </SettingsRow>
        <SettingsRow label="Deployment Alerts" desc="Notify when deployments complete or fail">
          <Toggle on={true} />
        </SettingsRow>
      </div>
    ),
    sound: (
      <div className="settings-section">
        <h3>Sound</h3>
        <SettingsRow label="System Sounds" desc="Play sounds for system events">
          <Toggle on={false} />
        </SettingsRow>
        <SettingsRow label="Volume" desc="Master output volume">
          <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>75%</span>
        </SettingsRow>
      </div>
    ),
    security: (
      <div className="settings-section">
        <h3>Security</h3>
        <SettingsRow label="Vault Status" desc="AES-256 encrypted secrets storage">
          <span style={{ fontSize: '0.8rem', color: 'var(--accent-green)' }}>🔒 Locked</span>
        </SettingsRow>
        <SettingsRow label="SSH Access" desc="Key-based authentication only">
          <Toggle on={true} />
        </SettingsRow>
        <SettingsRow label="Auto Updates" desc="Automatically install security patches">
          <Toggle on={autoUpdate} onClick={() => setAutoUpdate(!autoUpdate)} />
        </SettingsRow>
      </div>
    ),
    ai: (
      <div className="settings-section">
        <h3>AI Engine Configuration</h3>
        <SettingsRow label="Active Provider" desc="Primary LLM for deployment planning">
          <select value={aiProvider} onChange={e => setAiProvider(e.target.value)} style={{
            background: 'rgba(255,255,255,0.05)', border: '1px solid var(--panel-border)',
            borderRadius: '6px', color: '#fff', padding: '6px 12px', fontSize: '0.85rem', outline: 'none',
          }}>
            <option value="gemini">Google Gemini</option>
            <option value="openai">OpenAI GPT-4</option>
            <option value="openrouter">OpenRouter</option>
            <option value="ollama">Ollama (Local)</option>
          </select>
        </SettingsRow>
        <SettingsRow label="API Key" desc="Stored in encrypted vault">
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--text-muted)' }}>••••••••••••sk-3f</span>
        </SettingsRow>
        <SettingsRow label="Fallback Provider" desc="Used when primary provider fails">
          <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>OpenRouter</span>
        </SettingsRow>
      </div>
    ),
    account: (
      <div className="settings-section">
        <h3>Account</h3>
        <SettingsRow label="Username" desc="System administrator account">
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem' }}>admin</span>
        </SettingsRow>
        <SettingsRow label="Dashboard Password" desc="Used for web dashboard access">
          <button style={{ padding: '6px 14px', background: 'rgba(255,255,255,0.05)', border: '1px solid var(--panel-border)', borderRadius: '6px', color: 'var(--text-secondary)', cursor: 'pointer', fontSize: '0.8rem' }}>
            Change
          </button>
        </SettingsRow>
      </div>
    ),
  };

  return (
    <div className="settings-layout">
      <div className="settings-sidebar">
        {sections.map(s => (
          <div key={s.id} className={`settings-item ${active === s.id ? 'active' : ''}`} onClick={() => setActive(s.id)}>
            <s.icon size={18} />
            <span>{s.label}</span>
          </div>
        ))}
      </div>
      <div className="settings-content">
        <h2 style={{ marginBottom: '1.5rem', fontSize: '1.3rem', fontWeight: 600 }}>
          {sections.find(s => s.id === active)?.label}
        </h2>
        {content[active]}
      </div>
    </div>
  );
}
