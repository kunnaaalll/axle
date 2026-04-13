import React, { useState, useEffect } from 'react';
import { EyeOff, Trash2, Plus } from 'lucide-react';

export default function SecretsVault() {
  const [keys, setKeys] = useState([]);
  const [newKey, setNewKey] = useState('');
  const [newVal, setNewVal] = useState('');
  const [error, setError] = useState(null);

  const fetchKeys = async () => {
    try {
      const res = await fetch('http://localhost:4000/secrets/', {
        headers: { 'Authorization': 'Bearer DUMMY_TOKEN' }
      });
      const data = await res.json();
      if (data.success) {
        setKeys(data.keys);
      }
    } catch(err) {
      setError("Failed to connect to Vault API.");
    }
  };

  useEffect(() => {
    fetchKeys();
  }, []);

  const handleAdd = async (e) => {
    e.preventDefault();
    try {
      await fetch('http://localhost:4000/secrets/', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': 'Bearer DUMMY_TOKEN'
        },
        body: JSON.stringify({ key: newKey, value: newVal })
      });
      setNewKey('');
      setNewVal('');
      fetchKeys(); // Refresh
    } catch(err) {
      setError("Failed to add secret.");
    }
  };

  const handleDelete = async (k) => {
    try {
      await fetch(`http://localhost:4000/secrets/${k}`, {
        method: 'DELETE',
        headers: { 'Authorization': 'Bearer DUMMY_TOKEN' }
      });
      fetchKeys();
    } catch(err) {
      setError("Failed to delete secret.");
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '2rem' }}>
      <h1>Secrets Vault</h1>
      <p style={{ color: 'var(--text-muted)' }}>Secure environment variables injected into the deployment pipeline via AES-256.</p>
      
      {error && <p style={{color: 'var(--accent-red)'}}>{error}</p>}

      <div style={{ marginTop: '2rem', display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
        {/* Secrets List */}
        <div style={{ flex: 2, minWidth: '300px' }}>
          <h3 style={{ borderBottom: '1px solid var(--panel-border)', paddingBottom: '0.5rem' }}>Active Vault Keys</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '1rem' }}>
            {keys.length === 0 ? <p style={{ color: 'var(--text-muted)' }}>Vault is empty.</p> : null}
            {keys.map((k, i) => (
              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(255,255,255,0.05)', padding: '12px 16px', borderRadius: '6px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                  <span style={{ fontFamily: 'monospace', fontWeight: 'bold', color: 'var(--accent-purple)' }}>{k}</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                    <EyeOff size={16} /> <span>••••••••••••••••</span>
                  </div>
                </div>
                <button 
                  onClick={() => handleDelete(k)}
                  style={{ background: 'transparent', border: 'none', color: 'var(--accent-red)', cursor: 'pointer' }}
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
              onChange={(e) => setNewKey(e.target.value.toUpperCase().replace(/\s+/g, '_'))}
              required
              style={{ padding: '12px', background: 'rgba(0,0,0,0.5)', border: '1px solid var(--panel-border)', color: '#fff', borderRadius: '6px', fontFamily: 'monospace' }}
            />
            <input 
              type="password" 
              placeholder="Value" 
              value={newVal}
              onChange={(e) => setNewVal(e.target.value)}
              required
              style={{ padding: '12px', background: 'rgba(0,0,0,0.5)', border: '1px solid var(--panel-border)', color: '#fff', borderRadius: '6px' }}
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
