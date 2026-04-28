import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Activity, Rocket, KeyRound, MessageSquare, History, LogOut } from 'lucide-react';
import './index.css';

import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import DeployWizard from './components/DeployWizard';
import SecretsVault from './components/SecretsVault';
import DeployHistory from './components/DeployHistory';
import Chatbot from './components/Chatbot';

/* ——— Error Boundary ——— */
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', color: '#fff', flexDirection: 'column', gap: '1rem' }}>
          <h2 style={{ color: 'var(--accent-red)' }}>Something went wrong</h2>
          <p style={{ color: 'var(--text-muted)' }}>{this.state.error?.message}</p>
          <button className="btn-glow" onClick={() => window.location.reload()}>Reload Dashboard</button>
        </div>
      );
    }
    return this.props.children;
  }
}

/* ——— Sidebar Navigation Item ——— */
const NavItem = ({ to, icon, label }) => {
  const location = useLocation();
  const isActive = location.pathname === to;

  return (
    <Link to={to} style={{ textDecoration: 'none' }}>
      <div style={{
        display: 'flex', alignItems: 'center', gap: '12px',
        padding: '12px 20px',
        borderRadius: '8px',
        color: isActive ? '#fff' : 'var(--text-muted)',
        background: isActive ? 'linear-gradient(90deg, rgba(0,240,255,0.1) 0%, transparent 100%)' : 'transparent',
        borderLeft: isActive ? '3px solid var(--accent-blue)' : '3px solid transparent',
        transition: 'all 0.2s',
        marginBottom: '4px',
      }}>
        {icon}
        <span style={{ fontWeight: isActive ? '600' : '400', fontSize: '0.95rem' }}>{label}</span>
      </div>
    </Link>
  );
};

/* ——— Main Layout (Authenticated) ——— */
function Layout() {
  const { logout } = useAuth();

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', overflow: 'hidden' }}>
      {/* Sidebar */}
      <div className="glass-panel" style={{
        width: '260px',
        height: '100vh',
        borderRadius: '0',
        borderTop: 'none',
        borderBottom: 'none',
        borderLeft: 'none',
        display: 'flex',
        flexDirection: 'column',
        padding: '1.5rem 0',
        justifyContent: 'space-between',
      }}>
        <div>
          <div style={{ padding: '0 20px', marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{
              width: '32px', height: '32px',
              background: 'linear-gradient(135deg, var(--accent-blue), var(--accent-purple))',
              borderRadius: '8px',
              boxShadow: '0 0 15px rgba(0,240,255,0.4)',
            }} />
            <h2 style={{ margin: 0, letterSpacing: '2px', fontSize: '1.2rem' }}>AXLE OS</h2>
          </div>

          <div style={{ paddingRight: '1rem' }}>
            <NavItem to="/" icon={<Activity size={20} />} label="Dashboard" />
            <NavItem to="/deploy" icon={<Rocket size={20} />} label="Deploy" />
            <NavItem to="/history" icon={<History size={20} />} label="History" />
            <NavItem to="/secrets" icon={<KeyRound size={20} />} label="Secrets Vault" />
            <NavItem to="/chat" icon={<MessageSquare size={20} />} label="AI Copilot" />
          </div>
        </div>

        <div style={{ padding: '0 12px' }}>
          <button
            onClick={logout}
            style={{
              width: '100%', padding: '10px',
              background: 'transparent', border: '1px solid var(--panel-border)',
              borderRadius: '8px', color: 'var(--text-muted)',
              cursor: 'pointer', display: 'flex', alignItems: 'center',
              justifyContent: 'center', gap: '8px', fontSize: '0.9rem',
              transition: 'all 0.2s',
            }}
            onMouseEnter={e => { e.target.style.borderColor = 'var(--accent-red)'; e.target.style.color = 'var(--accent-red)'; }}
            onMouseLeave={e => { e.target.style.borderColor = 'var(--panel-border)'; e.target.style.color = 'var(--text-muted)'; }}
          >
            <LogOut size={16} /> Sign Out
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div style={{ flex: 1, padding: '2rem 3rem', overflowY: 'auto' }}>
        <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span className="status-indicator"></span>
            <span style={{ color: 'var(--accent-blue)', fontSize: '0.85rem', fontWeight: '600', letterSpacing: '1px' }}>
              SYSTEM ONLINE
            </span>
          </div>
          <div className="glass-panel" style={{ padding: '8px 16px', borderRadius: '20px', fontSize: '0.85rem' }}>
            v1.0.0
          </div>
        </header>

        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/deploy" element={<DeployWizard />} />
          <Route path="/history" element={<DeployHistory />} />
          <Route path="/secrets" element={<SecretsVault />} />
          <Route path="/chat" element={<Chatbot />} />
        </Routes>
      </div>
    </div>
  );
}

/* ——— Auth Gate ——— */
function AuthGate() {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <Layout /> : <Login />;
}

/* ——— Root App ——— */
function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Router>
          <AuthGate />
        </Router>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;
