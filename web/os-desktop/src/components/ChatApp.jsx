import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, Send } from 'lucide-react';

const AI_RESPONSES = {
  default: "I'm the AXLE Copilot. I can help with deployments, infrastructure, and server management. Try asking about your services, database, or deployment status.",
  status: "Here's your current system status:\n\n● axle-api.service — active (running)\n● axle-dashboard — active (running)\n● nginx.service — active (running)\n● postgresql.service — active (running)\n\nAll 4 services healthy. Uptime: 72h 14m.",
  deploy: "To deploy a new application:\n\n1. Use `axle deploy <github-url>` from the CLI\n2. Or open AXLE Deploy from the app launcher\n3. AXLE will scan your repo, detect the stack, and generate a deployment plan\n\nSupported stacks: Node.js, Python, Go, Java, Static HTML",
  database: "PostgreSQL 16 Status:\n\n● Status: Active\n● Connections: 3 active / 100 max\n● CPU: 0.2%\n● DB Size: 142 MB\n● Uptime: 72 hours\n● Last backup: 2 hours ago\n\nNo performance issues detected.",
  nginx: "Nginx Configuration:\n\n● Status: Active (PID 1842)\n● Upstream: 127.0.0.1:3000\n● SSL: Let's Encrypt (expires in 78 days)\n● Requests/sec: 42 avg\n● Active connections: 8\n\nNo errors in access.log.",
  secrets: "You have 5 encrypted secrets in the vault:\n\n• DATABASE_URL\n• GEMINI_API_KEY\n• JWT_SECRET\n• STRIPE_SECRET\n• REDIS_URL\n\nAll secrets are AES-256 encrypted at rest. Values are never exposed to AI context.",
  help: "Here's what I can help with:\n\n• System status and health checks\n• Deployment guidance and troubleshooting\n• Database monitoring\n• Nginx/SSL configuration\n• Secrets management\n• Firewall rules\n• Service management\n\nJust ask naturally!",
};

function getResponse(query) {
  const q = query.toLowerCase();
  if (q.includes('status') || q.includes('health')) return AI_RESPONSES.status;
  if (q.includes('deploy') || q.includes('deployment')) return AI_RESPONSES.deploy;
  if (q.includes('database') || q.includes('postgres') || q.includes('db')) return AI_RESPONSES.database;
  if (q.includes('nginx') || q.includes('proxy') || q.includes('ssl')) return AI_RESPONSES.nginx;
  if (q.includes('secret') || q.includes('vault') || q.includes('key')) return AI_RESPONSES.secrets;
  if (q.includes('help') || q.includes('what can')) return AI_RESPONSES.help;
  return AI_RESPONSES.default;
}

export default function ChatApp() {
  const [messages, setMessages] = useState([
    { role: 'ai', content: "Hello! I'm the AXLE AI Copilot. I can help you with deployments, infrastructure debugging, and server configuration. What would you like to do?" },
  ]);
  const [input, setInput] = useState('');
  const [typing, setTyping] = useState(false);
  const endRef = useRef(null);

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages, typing]);

  const handleSend = () => {
    if (!input.trim()) return;
    const q = input.trim();
    setMessages(prev => [...prev, { role: 'user', content: q }]);
    setInput('');
    setTyping(true);

    setTimeout(() => {
      setTyping(false);
      setMessages(prev => [...prev, { role: 'ai', content: getResponse(q) }]);
    }, 800 + Math.random() * 1200);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ padding: '14px 18px', borderBottom: '1px solid rgba(255,255,255,0.04)', display: 'flex', alignItems: 'center', gap: '10px' }}>
        <MessageSquare size={18} color="var(--accent-blue)" />
        <span style={{ fontWeight: 600, fontSize: '0.95rem' }}>AXLE Copilot</span>
        <span style={{ fontSize: '0.7rem', color: 'var(--accent-green)', marginLeft: 'auto' }}>● Online</span>
      </div>

      <div style={{ flex: 1, padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px', overflow: 'auto' }}>
        {messages.map((m, i) => (
          <div key={i} style={{ display: 'flex', justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start' }}>
            <div style={{
              maxWidth: '75%', padding: '12px 16px',
              background: m.role === 'user' ? 'rgba(0,240,255,0.08)' : 'rgba(255,255,255,0.03)',
              border: `1px solid ${m.role === 'user' ? 'rgba(0,240,255,0.15)' : 'rgba(255,255,255,0.04)'}`,
              borderRadius: m.role === 'user' ? '12px 12px 2px 12px' : '12px 12px 12px 2px',
              fontSize: '0.88rem', lineHeight: 1.7, whiteSpace: 'pre-wrap',
              color: 'var(--text-secondary)',
            }}>
              {m.content}
            </div>
          </div>
        ))}
        {typing && (
          <div style={{ display: 'flex', gap: '6px', padding: '12px 16px', background: 'rgba(255,255,255,0.03)', borderRadius: '12px', width: 'fit-content' }}>
            {[0, 1, 2].map(i => (
              <div key={i} style={{
                width: 7, height: 7, borderRadius: '50%', background: 'var(--accent-blue)',
                animation: `pulse 1s ease ${i * 0.2}s infinite`,
              }} />
            ))}
          </div>
        )}
        <div ref={endRef} />
      </div>

      <form onSubmit={e => { e.preventDefault(); handleSend(); }} style={{
        padding: '12px 16px', borderTop: '1px solid rgba(255,255,255,0.04)', display: 'flex', gap: '8px',
      }}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Ask about infrastructure, deployments..."
          style={{
            flex: 1, padding: '11px 16px', background: 'rgba(255,255,255,0.04)',
            border: '1px solid var(--panel-border)', borderRadius: '10px',
            color: '#fff', outline: 'none', fontSize: '0.88rem',
          }}
        />
        <button type="submit" disabled={typing} style={{
          width: '40px', height: '40px', borderRadius: '10px',
          background: 'rgba(0,240,255,0.1)', border: '1px solid rgba(0,240,255,0.25)',
          color: '#fff', cursor: typing ? 'not-allowed' : 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <Send size={16} />
        </button>
      </form>
    </div>
  );
}
