import React, { useState } from 'react';
import './index.css';
import BootScreen from './components/BootScreen';
import LoginScreen from './components/LoginScreen';
import Desktop from './components/Desktop';

export default function App() {
  const [phase, setPhase] = useState('boot'); // boot → login → desktop

  if (phase === 'boot') {
    return <BootScreen onComplete={() => setPhase('login')} />;
  }

  if (phase === 'login') {
    return <LoginScreen onLogin={() => setPhase('desktop')} />;
  }

  return <Desktop />;
}
