import React, { useState, useRef, useEffect } from 'react';

const WELCOME = `\x1b[36m╔══════════════════════════════════════════════════╗
║     ⚡ AXLE OS Terminal v1.0.0                    ║
║     AI-Powered Autonomous Deployment Engine       ║
╚══════════════════════════════════════════════════╝\x1b[0m

Type 'help' for available commands.
`;

const COMMANDS = {
  help: `Available commands:
  axle status    — Show system status
  axle info      — Show system information
  axle scan      — Scan a project repository
  axle plan      — Generate deployment plan
  axle deploy    — Deploy an application
  axle secrets   — Manage encrypted secrets
  neofetch       — System info display
  ls             — List files
  pwd            — Print working directory
  clear          — Clear terminal
  help           — Show this help`,
  'axle status': `⚡ AXLE OS Status
╭──────────────────┬───────────────────────────────────╮
│  Version         │  1.0.0                            │
│  Status          │  \x1b[32m● Ready\x1b[0m                          │
│  AI Providers    │  Gemini ✓, OpenRouter ✓            │
│  axle-api        │  \x1b[32m● active\x1b[0m                         │
│  axle-dashboard  │  \x1b[32m● active\x1b[0m                         │
╰──────────────────┴───────────────────────────────────╯`,
  'axle info': `⚡ AXLE OS Info
╭──────────────────┬───────────────────────────────────╮
│  AXLE Version    │  1.0.0                            │
│  Python          │  3.12.4                           │
│  OS              │  Ubuntu 24.04 LTS                 │
│  Architecture    │  x86_64                           │
│  Hostname        │  axle-prod-01                     │
╰──────────────────┴───────────────────────────────────╯`,
  neofetch: `\x1b[36m       ___  _  ___    ____
      /   | \\/ / /   / __/
     / /| |\\  / /   / _/
    / ___ |/ / /___/ /__
   /_/  |_/_/_____/____/\x1b[0m

   \x1b[36mOS:\x1b[0m      AXLE OS 1.0.0 (Ubuntu 24.04)
   \x1b[36mKernel:\x1b[0m  6.8.0-axle
   \x1b[36mCPU:\x1b[0m     AMD EPYC 7R13 (2) @ 2.65GHz
   \x1b[36mMemory:\x1b[0m  1.2 GiB / 4.0 GiB (30%)
   \x1b[36mDisk:\x1b[0m    8.2 GB / 30 GB (27%)
   \x1b[36mUptime:\x1b[0m  3 days, 14 hours`,
  ls: `build/  docs/  axle/  web/  tests/  templates/
README.md  pyproject.toml  Makefile  CHANGELOG.md  CONTRIBUTING.md`,
  pwd: '/opt/axle',
};

function parseLine(text) {
  const parts = [];
  let current = '';
  let color = null;
  const tokens = text.split(/(\x1b\[\d+m)/);
  for (const token of tokens) {
    if (token.match(/\x1b\[(\d+)m/)) {
      if (current) parts.push({ text: current, color });
      current = '';
      const code = token.match(/\x1b\[(\d+)m/)[1];
      if (code === '0') color = null;
      else if (code === '32') color = 'var(--accent-green)';
      else if (code === '36') color = 'var(--accent-blue)';
      else if (code === '33') color = 'var(--accent-orange)';
      else if (code === '31') color = 'var(--accent-red)';
    } else {
      current += token;
    }
  }
  if (current) parts.push({ text: current, color });
  return parts;
}

export default function TerminalApp() {
  const [lines, setLines] = useState(WELCOME.split('\n'));
  const [input, setInput] = useState('');
  const endRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [lines]);

  const handleCommand = (cmd) => {
    const trimmed = cmd.trim().toLowerCase();
    const newLines = [...lines, `\x1b[36madmin@axle-os\x1b[0m:\x1b[36m~\x1b[0m$ ${cmd}`];
    if (trimmed === 'clear') {
      setLines([]);
    } else if (COMMANDS[trimmed]) {
      setLines([...newLines, ...COMMANDS[trimmed].split('\n')]);
    } else if (trimmed) {
      setLines([...newLines, `axle: command not found: ${trimmed}`]);
    } else {
      setLines(newLines);
    }
    setInput('');
  };

  return (
    <div className="terminal-body" onClick={() => inputRef.current?.focus()} style={{ cursor: 'text' }}>
      {lines.map((line, i) => (
        <div key={i} className="terminal-line">
          {parseLine(line).map((part, j) => (
            <span key={j} style={{ color: part.color || undefined }}>{part.text}</span>
          ))}
        </div>
      ))}
      <div className="terminal-line" style={{ display: 'flex', alignItems: 'center' }}>
        <span className="terminal-prompt">admin@axle-os</span>
        <span style={{ color: 'var(--text-muted)' }}>:</span>
        <span style={{ color: 'var(--accent-blue)' }}>~</span>
        <span style={{ color: 'var(--text-muted)' }}>$ </span>
        <input
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter') handleCommand(input); }}
          style={{
            background: 'transparent', border: 'none', outline: 'none',
            color: 'var(--text-primary)', fontFamily: 'var(--font-mono)',
            fontSize: '0.82rem', flex: 1, caretColor: 'var(--accent-blue)',
          }}
          autoFocus
        />
      </div>
      <div ref={endRef} />
    </div>
  );
}
