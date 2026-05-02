import React, { useState, useEffect } from 'react';
import { Zap, Wifi, Volume2, Battery } from 'lucide-react';

export default function Taskbar({ openWindows, activeWindow, onStartClick, onWindowClick, showStart }) {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  const timeStr = time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
  const dateStr = time.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });

  return (
    <div className="taskbar">
      <div className="taskbar-start">
        <button
          className={`taskbar-btn ${showStart ? 'active' : ''}`}
          onClick={onStartClick}
          title="Applications"
        >
          <Zap size={20} color="var(--accent-blue)" />
        </button>
      </div>

      <div className="taskbar-center">
        {openWindows.map(win => (
          <button
            key={win.id}
            className={`taskbar-btn ${activeWindow === win.id ? 'active' : ''}`}
            onClick={() => onWindowClick(win.id)}
            title={win.title}
          >
            <span style={{ fontSize: '1rem' }}>{win.icon}</span>
          </button>
        ))}
      </div>

      <div className="taskbar-end">
        <div className="taskbar-tray-dot" />
        <Wifi size={15} color="var(--text-muted)" />
        <Volume2 size={15} color="var(--text-muted)" />
        <Battery size={15} color="var(--text-muted)" />
        <div className="taskbar-time">
          <div>{timeStr}</div>
          <div style={{ fontSize: '0.7rem' }}>{dateStr}</div>
        </div>
      </div>
    </div>
  );
}
