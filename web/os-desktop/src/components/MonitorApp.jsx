import React, { useState, useEffect } from 'react';
import { BarChart3, Cpu, HardDrive, Wifi, Activity } from 'lucide-react';

function MiniBar({ value, max, color }) {
  return (
    <div style={{ width: '100%', height: '6px', background: 'rgba(255,255,255,0.06)', borderRadius: '3px', overflow: 'hidden' }}>
      <div style={{ width: `${(value / max) * 100}%`, height: '100%', background: color, borderRadius: '3px', transition: 'width 0.8s ease' }} />
    </div>
  );
}

const SERVICES = [
  { name: 'axle-api.service', pid: 1204, cpu: '0.3%', mem: '42 MB' },
  { name: 'axle-dashboard.service', pid: 1312, cpu: '0.1%', mem: '28 MB' },
  { name: 'nginx.service', pid: 1842, cpu: '0.1%', mem: '12 MB' },
  { name: 'postgresql@16.service', pid: 980, cpu: '0.4%', mem: '86 MB' },
  { name: 'node /opt/app/server.js', pid: 2104, cpu: '1.2%', mem: '128 MB' },
  { name: 'redis-server', pid: 1560, cpu: '0.0%', mem: '8 MB' },
];

export default function MonitorApp() {
  const [cpu, setCpu] = useState(12);
  const [ram, setRam] = useState(1.2);
  const [disk, setDisk] = useState(8.2);
  const [netUp, setNetUp] = useState(2.1);
  const [netDown, setNetDown] = useState(0.54);

  useEffect(() => {
    const interval = setInterval(() => {
      setCpu(c => Math.max(2, Math.min(95, c + (Math.random() - 0.5) * 8)));
      setRam(r => Math.max(0.8, Math.min(3.8, r + (Math.random() - 0.5) * 0.3)));
      setNetUp(n => Math.max(0.1, Math.min(10, n + (Math.random() - 0.5) * 1.5)));
      setNetDown(n => Math.max(0.05, Math.min(5, n + (Math.random() - 0.5) * 0.8)));
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const cards = [
    { label: 'CPU', value: `${cpu.toFixed(1)}%`, bar: cpu, max: 100, color: 'var(--accent-blue)', icon: Cpu },
    { label: 'Memory', value: `${ram.toFixed(1)} / 4.0 GB`, bar: ram, max: 4, color: 'var(--accent-purple)', icon: Activity },
    { label: 'Disk', value: `${disk.toFixed(1)} / 30 GB`, bar: disk, max: 30, color: 'var(--accent-orange)', icon: HardDrive },
    { label: 'Network', value: `↑ ${netUp.toFixed(1)} MB/s  ↓ ${netDown.toFixed(2)} MB/s`, bar: netUp, max: 10, color: '#22d3ee', icon: Wifi },
  ];

  return (
    <div style={{ padding: '20px', height: '100%', overflow: 'auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
        <BarChart3 size={22} color="#22d3ee" />
        <h2 style={{ margin: 0, fontSize: '1.15rem' }}>System Monitor</h2>
        <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginLeft: 'auto' }}>Live • 2s interval</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '20px' }}>
        {cards.map(c => (
          <div key={c.label} style={{ padding: '14px', background: 'rgba(255,255,255,0.02)', borderRadius: '10px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <c.icon size={14} color={c.color} />
              <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>{c.label}</span>
            </div>
            <div style={{ fontSize: '1.05rem', fontWeight: 600, color: c.color, marginBottom: '8px' }}>{c.value}</div>
            <MiniBar value={c.bar} max={c.max} color={c.color} />
          </div>
        ))}
      </div>

      <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '10px' }}>
        Running Processes ({SERVICES.length})
      </div>
      <div style={{ background: 'rgba(255,255,255,0.015)', borderRadius: '8px', overflow: 'hidden' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 60px 60px 70px', gap: '0', padding: '8px 14px', borderBottom: '1px solid rgba(255,255,255,0.04)', fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
          <span>Service</span><span>PID</span><span>CPU</span><span>Memory</span>
        </div>
        {SERVICES.map((s, i) => (
          <div key={i} style={{ display: 'grid', gridTemplateColumns: '1fr 60px 60px 70px', padding: '8px 14px', borderBottom: i < SERVICES.length - 1 ? '1px solid rgba(255,255,255,0.02)' : 'none', fontSize: '0.82rem', alignItems: 'center' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '8px', fontFamily: 'var(--font-mono)', fontSize: '0.78rem' }}>
              <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#22d3ee', boxShadow: '0 0 4px #22d3ee' }} />
              {s.name}
            </span>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.78rem', color: 'var(--text-muted)' }}>{s.pid}</span>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.78rem', color: 'var(--text-muted)' }}>{s.cpu}</span>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.78rem', color: 'var(--text-muted)' }}>{s.mem}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
