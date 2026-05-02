import React, { useState, useEffect } from 'react';
import { Zap } from 'lucide-react';

const bootMessages = [
  'Initializing kernel modules...',
  'Loading AXLE AI Engine v1.0.0...',
  'Mounting encrypted vault...',
  'Starting plugin registry...',
  'Configuring neural inference pipeline...',
  'Loading deployment orchestrator...',
  'Initializing network stack...',
  'Starting AXLE services...',
  'System ready.',
];

export default function BootScreen({ onComplete }) {
  const [progress, setProgress] = useState(0);
  const [msgIndex, setMsgIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress(p => {
        const next = p + Math.random() * 15 + 5;
        if (next >= 100) {
          clearInterval(interval);
          setTimeout(onComplete, 600);
          return 100;
        }
        return next;
      });
      setMsgIndex(i => Math.min(i + 1, bootMessages.length - 1));
    }, 350);
    return () => clearInterval(interval);
  }, [onComplete]);

  return (
    <div className="boot-screen">
      <div className="boot-logo">
        <Zap size={40} color="#fff" />
      </div>
      <div className="boot-text">AXLE OS</div>
      <div className="boot-progress">
        <div className="boot-progress-bar" style={{ width: `${Math.min(progress, 100)}%` }} />
      </div>
      <div className="boot-status">{bootMessages[msgIndex]}</div>
    </div>
  );
}
