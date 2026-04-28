import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { EyeOff, Trash2, Plus } from 'lucide-react';

export default function SecretsVault() {
  const { authFetch } = useAuth();
  const [keys, setKeys] = useState([]);
  const [newKey, setNewKey] = useState('');
  const [newVal, setNewVal] = useState('');
  const [error, setError] = useState(null);

  const fetchKeys = async () => {
    try {
      const res = await authFetch('/secrets/');
      const data = await res.json();
      if (data.success) {
        setKeys(data.keys);
      }
    } catch (err) {
      setError("Failed to connect to Vault API.");
    }
  };

  useEffect(() => {
    fetchKeys();
  }, []);

  const handleAdd = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      const res = await authFetch('/secrets/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key: newKey, value: newVal }),
      });
      const data = await res.json();
      if (data.success) {
        setNewKey('');
        setNewVal('');
        fetchKeys();
      } else {
        setError(data.error);
      }
    } catch (err) {
      setError("Failed to add secret.");
    }
  };

  const handleDelete = async (k) => {
    if (!confirm(`Delete secret "${k}"?`)) return;
    try {
      await authFetch(`/secrets/${k}`, { method: 'DELETE' });
      fetchKeys();
    } catch (err) {
      setError("Failed to delete secret.");
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '2rem' }}>
      <h1>Secrets Vault</h1>
      <p style={{ color: 'var(--text-muted)' }}>Secure environment variables injected into the deployment pipeline via AES-256.</p>

      {error && (
        <div style={{
          color: 'var(--accent-red)', marginTop: '1rem', padding: '10px 14px',
          background: 'rgba(255,51,102,0.1)', borderRadius: '6px',
          border: '1px solid rgba(255,51,102,0.3)',
        }}>
          {error}
        </div>
      )}

      <div style={{ marginTop: '2rem', display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
        {/* Secrets List */}
        <div style={{ flex: 2, minWidth: '300px' }}>
          <h3 style={{ borderBottom: '1px solid var(--panel-border)', paddingBottom: '0.5rem' }}>Active Vault Keys</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '1rem' }}>
            {keys.length === 0 ? (
              <p style={{ color: 'var(--text-muted)' }}>Vault is empty. Add secrets using the form.</p>
            ) : null}
            {keys.map((k, i) => (
              <div key={i} style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                background: 'rgba(255,255,255,0.05)', padding: '12px 16px', borderRadius: '6px',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                  <span style={{ fontFamily: 'monospace', fontWeight: 'bold', color: 'var(--accent-purple)' }}>{k}</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                    <EyeOff size={16} /> <span>••••••••••••••••</span>
                  </div>
                </div>
                <button
                  onClick={() => handleDelete(k)}
                  style={{ background: 'transparent', border: 'none', color: 'var(--accent-red)', cursor: 'pointer', padding: '4px' }}
                  title={`Delete ${k}`}
                >
                  <Trash2 size={20} />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Add Secret Form */}
        <div className="glass-panel" style={{ flex: 1, minWidth: '300px', padding: '1.5rem', height: 'fit-content' }}>
          <h3>Inject Secret</h3>
          <form onSubmit={handleAdd} style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '1rem' }}>
            <input
              type="text"
              placeholder="SECRET_KEY_NAME"
              value={newKey}
              onChange={(e) => setNewKey(e.target.value.toUpperCase().replace(/[^A-Z0-9_]/g, '_'))}
              required
              style={{
                padding: '12px', background: 'rgba(0,0,0,0.5)',
                border: '1px solid var(--panel-border)', color: '#fff',
                borderRadius: '6px', fontFamily: 'monospace', outline: 'none',
              }}
            />
            <input
              type="password"
              placeholder="Value"
              value={newVal}
              onChange={(e) => setNewVal(e.target.value)}
              required
              style={{
                padding: '12px', background: 'rgba(0,0,0,0.5)',
                border: '1px solid var(--panel-border)', color: '#fff',
                borderRadius: '6px', outline: 'none',
              }}
            />
            <button type="submit" className="btn-glow" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px' }}>
              <Plus size={18} /> Add to Vault
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
