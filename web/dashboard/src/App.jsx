import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Activity, Rocket, KeyRound, MessageSquare, Menu } from 'lucide-react';
import './index.css';

import Dashboard from './components/Dashboard';
import DeployWizard from './components/DeployWizard';
import SecretsVault from './components/SecretsVault';
import Chatbot from './components/Chatbot';

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
        marginBottom: '8px'
      }}>
        {icon}
        <span style={{ fontWeight: isActive ? '600' : '400' }}>{label}</span>
      </div>
    </Link>
  );
};

function Layout() {
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
        padding: '1.5rem 0'
      }}>
        <div style={{ padding: '0 20px', marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ width: '32px', height: '32px', background: 'var(--accent-blue)', borderRadius: '8px', boxShadow: '0 0 15px rgba(0,240,255,0.5)' }}></div>
          <h2 style={{ margin: 0, letterSpacing: '2px' }}>AXLE OS</h2>
        </div>
        
        <div style={{ paddingRight: '1rem' }}>
          <NavItem to="/" icon={<Activity size={20} />} label="Dashboard" />
          <NavItem to="/deploy" icon={<Rocket size={20} />} label="Deploy" />
          <NavItem to="/secrets" icon={<KeyRound size={20} />} label="Secrets Vault" />
          <NavItem to="/chat" icon={<MessageSquare size={20} />} label="AI Assistant" />
        </div>
      </div>

      {/* Main Content */}
      <div style={{ flex: 1, padding: '2rem 3rem', overflowY: 'auto' }}>
        <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span className="status-indicator"></span>
            <span style={{ color: 'var(--accent-blue)', fontSize: '0.85rem', fontWeight: '600', letterSpacing: '1px' }}>SYSTEM ONLINE</span>
          </div>
          <div className="glass-panel" style={{ padding: '8px 16px', borderRadius: '20px', fontSize: '0.85rem' }}>
            admin workspace
          </div>
        </header>

        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/deploy" element={<DeployWizard />} />
          <Route path="/secrets" element={<SecretsVault />} />
          <Route path="/chat" element={<Chatbot />} />
        </Routes>
      </div>
    </div>
  );
}

function App() {
  return (
    <Router>
      <Layout />
    </Router>
  );
}

export default App;
