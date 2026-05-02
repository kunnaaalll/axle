import React, { useState } from 'react';
import { Folder, File, Home, HardDrive, Image, Music, Film, Download, ChevronRight } from 'lucide-react';

const fileSystem = {
  Home: [
    { name: 'Documents', type: 'folder', icon: Folder },
    { name: 'Downloads', type: 'folder', icon: Download },
    { name: 'Pictures', type: 'folder', icon: Image },
    { name: 'Music', type: 'folder', icon: Music },
    { name: 'Videos', type: 'folder', icon: Film },
    { name: '.env', type: 'file', size: '0.3 KB', icon: File },
    { name: 'README.md', type: 'file', size: '3.0 KB', icon: File },
  ],
  Documents: [
    { name: 'AXLE_Whitepaper.md', type: 'file', size: '23 KB', icon: File },
    { name: 'architecture.md', type: 'file', size: '4.2 KB', icon: File },
    { name: 'deployment-logs', type: 'folder', icon: Folder },
  ],
  '/opt/axle': [
    { name: 'axle/', type: 'folder', icon: Folder },
    { name: 'web/', type: 'folder', icon: Folder },
    { name: 'tests/', type: 'folder', icon: Folder },
    { name: 'docs/', type: 'folder', icon: Folder },
    { name: 'build/', type: 'folder', icon: Folder },
    { name: 'pyproject.toml', type: 'file', size: '1.0 KB', icon: File },
    { name: 'Makefile', type: 'file', size: '0.4 KB', icon: File },
    { name: 'CHANGELOG.md', type: 'file', size: '1.8 KB', icon: File },
  ],
};

const sidebarItems = [
  { label: 'Home', icon: Home, key: 'Home' },
  { label: 'Documents', icon: Folder, key: 'Documents' },
  { label: '/opt/axle', icon: HardDrive, key: '/opt/axle' },
];

export default function FileManagerApp() {
  const [currentDir, setCurrentDir] = useState('Home');

  const files = fileSystem[currentDir] || [];

  return (
    <div style={{ display: 'flex', height: '100%' }}>
      <div className="fm-sidebar">
        <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', padding: '4px 12px 8px', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: 600 }}>
          Places
        </div>
        {sidebarItems.map(item => (
          <div
            key={item.key}
            className={`fm-sidebar-item ${currentDir === item.key ? 'active' : ''}`}
            onClick={() => setCurrentDir(item.key)}
          >
            <item.icon size={16} />
            <span>{item.label}</span>
          </div>
        ))}
      </div>
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Breadcrumb */}
        <div style={{
          padding: '10px 16px', borderBottom: '1px solid rgba(255,255,255,0.04)',
          display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', color: 'var(--text-muted)',
        }}>
          <Home size={14} />
          <ChevronRight size={12} />
          <span style={{ color: 'var(--text-primary)' }}>{currentDir}</span>
          <span style={{ marginLeft: 'auto', fontSize: '0.75rem' }}>{files.length} items</span>
        </div>
        {/* Grid */}
        <div className="fm-grid">
          {files.map((f, i) => (
            <div
              key={i}
              className="fm-item"
              onDoubleClick={() => { if (f.type === 'folder' && fileSystem[f.name.replace('/', '')]) setCurrentDir(f.name.replace('/', '')); }}
            >
              <div className="fm-item-icon">
                <f.icon size={32} color={f.type === 'folder' ? 'var(--accent-blue)' : 'var(--text-muted)'} />
              </div>
              <div className="fm-item-name">{f.name}</div>
              {f.size && <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>{f.size}</div>}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
