import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User } from 'lucide-react';

export default function Chatbot() {
  const [messages, setMessages] = useState([
    { role: 'ai', content: 'Hello! I am the deep-integrated AXLE AI assistant. I can help you orchestrate deployments or answer questions about your environment.' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const endOfMessagesRef = useRef(null);

  const scrollToBottom = () => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = input.trim();
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch('http://localhost:4000/chat/', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': 'Bearer DUMMY_TOKEN'
        },
        body: JSON.stringify({ query: userMsg })
      });
      const data = await res.json();
      
      if (data.success) {
        setMessages(prev => [...prev, { role: 'ai', content: data.reply }]);
      } else {
        setMessages(prev => [...prev, { role: 'ai', content: `[Error: ${data.error}]` }]);
      }
    } catch(err) {
      setMessages(prev => [...prev, { role: 'ai', content: '[Connection failed: Node unreachable]' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 120px)' }}>
      {/* Header */}
      <div style={{ padding: '1rem 2rem', borderBottom: '1px solid var(--panel-border)', display: 'flex', alignItems: 'center', gap: '12px' }}>
        <Bot size={24} color="var(--accent-blue)" />
        <h2 style={{ margin: 0, fontSize: '1.2rem' }}>AXLE Copilot</h2>
      </div>

      {/* Messages Window */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '2rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        {messages.map((m, i) => (
          <div key={i} style={{ display: 'flex', justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start' }}>
            <div style={{ 
                maxWidth: '70%', 
                background: m.role === 'user' ? 'linear-gradient(135deg, rgba(0, 240, 255, 0.1), transparent)' : 'rgba(255,255,255,0.05)',
                border: m.role === 'user' ? '1px solid var(--accent-blue)' : '1px solid var(--panel-border)',
                padding: '16px 20px', 
                borderRadius: '12px',
                borderBottomRightRadius: m.role === 'user' ? '0' : '12px',
                borderBottomLeftRadius: m.role === 'ai' ? '0' : '12px',
                display: 'flex', gap: '12px'
            }}>
              {m.role === 'ai' && <Bot size={20} color="var(--accent-blue)" style={{ flexShrink: 0, marginTop: '2px' }} />}
              <div style={{ whiteSpace: 'pre-wrap', lineHeight: '1.5', color: '#e2e8f0' }}>{m.content}</div>
              {m.role === 'user' && <User size={20} color="var(--text-muted)" style={{ flexShrink: 0, marginTop: '2px' }} />}
            </div>
          </div>
        ))}
        {loading && (
          <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
            <div style={{ padding: '16px 20px', borderRadius: '12px', background: 'rgba(255,255,255,0.05)', display: 'flex', gap: '8px', alignItems: 'center' }}>
               <span className="status-indicator"></span> 
               <span style={{color: 'var(--text-muted)', fontSize: '0.9rem'}}>Copilot is thinking...</span>
            </div>
          </div>
        )}
        <div ref={endOfMessagesRef} />
      </div>

      {/* Input Form */}
      <form onSubmit={handleSend} style={{ padding: '1.5rem 2rem', borderTop: '1px solid var(--panel-border)', display: 'flex', gap: '1rem' }}>
        <input 
          type="text" 
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Ask a question about deployments or system orchestration..." 
          style={{ flex: 1, padding: '16px 20px', background: 'rgba(0,0,0,0.5)', border: '1px solid var(--panel-border)', color: '#fff', borderRadius: '12px', outline: 'none', fontSize: '1rem' }}
        />
        <button type="submit" className="btn-glow" disabled={loading} style={{ borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '0 24px' }}>
          <Send size={20} />
        </button>
      </form>
    </div>
  );
}
