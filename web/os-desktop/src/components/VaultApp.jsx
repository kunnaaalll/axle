import React, { useState, useEffect, useRef } from 'react';
import { Shield, Plus, Trash2, Eye, EyeOff, Copy, Check } from 'lucide-react';

const INITIAL_SECRETS = [
  { key: 'DATABASE_URL', value: 'postgresql://axle:s3cr3t@localhost/axle_prod', visible: false },
  { key: 'GEMINI_API_KEY', value: 'AIzaSyB-xxxxxxxxxxxxxxxxxxxxxxxxxxx', visible: false },
  { key: 'JWT_SECRET', value: 'axle_jwt_super_secret_key_2026', visible: false },
  { key: 'STRIPE_SECRET', value: 'sk_live_xxxxxxxxxxxxxxxxxxxxxxx', visible: false },
  { key: 'REDIS_URL', value: 'redis://localhost:6379/0', visible: false },
];

export default function VaultApp() {
  const [secrets, setSecrets] = useState(INITIAL_SECRETS);
  const [adding, setAdding] = useState(false);
  const [newKey, setNewKey] = useState('');
  const [newVal, setNewVal] = useState('');
  const [copied, setCopied] = useState(null);

  const toggleVisible = (idx) => {
    setSecrets(prev => prev.map((s, i) => i === idx ? { ...s, visible: !s.visible } : s));
  };

  const deleteSecret = (idx) => {
    setSecrets(prev => prev.filter((_, i) => i !== idx));
  };

  const addSecret = () => {
    if (!newKey.trim() || !newVal.trim()) return;
    setSecrets(prev => [...prev, { key: newKey.toUpperCase().replace(/\s+/g, '_'), value: newVal, visible: false }]);
    setNewKey(''); setNewVal(''); setAdding(false);
  };

  const copyKey = (val, idx) => {
    navigator.clipboard?.writeText(val);
    setCopied(idx);
    setTimeout(() => setCopied(null), 1500);
  };

  return (
    <div style={{ padding: '20px', height: '100%', overflow: 'auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Shield size={22} color="var(--accent-purple)" />
          <h2 style={{ margin: 0, fontSize: '1.15rem' }}>Secrets Vault</h2>
          <span style={{ fontSize: '0.7rem', background: 'rgba(139,92,246,0.1)', color: 'var(--accent-purple)', padding: '3px 8px', borderRadius: '10px' }}>AES-256</span>
        </div>
        <button onClick={() => setAdding(!adding)} style={{
          display: 'flex', alignItems: 'center', gap: '6px', padding: '8px 14px',
          background: 'rgba(139,92,246,0.1)', border: '1px solid rgba(139,92,246,0.25)',
          borderRadius: '8px', color: '#fff', cursor: 'pointer', fontSize: '0.82rem',
        }}>
          <Plus size={14} /> Add Secret
        </button>
      </div>

      {adding && (
        <div style={{ padding: '14px', background: 'rgba(255,255,255,0.02)', borderRadius: '8px', marginBottom: '12px', display: 'flex', gap: '8px', alignItems: 'flex-end' }}>
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Key</div>
            <input value={newKey} onChange={e => setNewKey(e.target.value)} placeholder="API_KEY_NAME"
              style={{ width: '100%', padding: '9px 12px', background: 'rgba(0,0,0,0.3)', border: '1px solid var(--panel-border)', borderRadius: '6px', color: '#fff', outline: 'none', fontSize: '0.85rem', fontFamily: 'var(--font-mono)' }} />
          </div>
          <div style={{ flex: 2 }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Value</div>
            <input value={newVal} onChange={e => setNewVal(e.target.value)} placeholder="secret_value_here" type="password"
              style={{ width: '100%', padding: '9px 12px', background: 'rgba(0,0,0,0.3)', border: '1px solid var(--panel-border)', borderRadius: '6px', color: '#fff', outline: 'none', fontSize: '0.85rem', fontFamily: 'var(--font-mono)' }} />
          </div>
          <button onClick={addSecret} style={{ padding: '9px 18px', background: 'var(--accent-purple)', border: 'none', borderRadius: '6px', color: '#fff', cursor: 'pointer', fontSize: '0.82rem', fontWeight: 600, whiteSpace: 'nowrap' }}>Save</button>
        </div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
        {secrets.map((s, i) => (
          <div key={i} style={{
            display: 'flex', alignItems: 'center', gap: '12px', padding: '11px 14px',
            background: 'rgba(255,255,255,0.02)', borderRadius: '8px',
            borderLeft: '3px solid rgba(139,92,246,0.3)',
          }}>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem', color: 'var(--accent-purple)', minWidth: '140px', fontWeight: 500 }}>{s.key}</span>
            <span style={{ flex: 1, fontFamily: 'var(--font-mono)', fontSize: '0.82rem', color: 'var(--text-muted)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {s.visible ? s.value : '•'.repeat(Math.min(s.value.length, 30))}
            </span>
            <button onClick={() => toggleVisible(i)} style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', padding: '4px' }}>
              {s.visible ? <EyeOff size={15} /> : <Eye size={15} />}
            </button>
            <button onClick={() => copyKey(s.value, i)} style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: copied === i ? '#22d3ee' : 'var(--text-muted)', padding: '4px' }}>
              {copied === i ? <Check size={15} /> : <Copy size={15} />}
            </button>
            <button onClick={() => deleteSecret(i)} style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', padding: '4px' }}>
              <Trash2 size={15} />
            </button>
          </div>
        ))}
      </div>

      <div style={{ marginTop: '16px', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
        {secrets.length} secrets • Encrypted at rest • AI-isolated
      </div>
    </div>
  );
}
