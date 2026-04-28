import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

const API_BASE = 'http://localhost:4000';

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('axle_token'));
  const [isAuthenticated, setIsAuthenticated] = useState(!!token);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (token) {
      localStorage.setItem('axle_token', token);
      setIsAuthenticated(true);
    } else {
      localStorage.removeItem('axle_token');
      setIsAuthenticated(false);
    }
  }, [token]);

  const login = async (password) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password }),
      });
      const data = await res.json();
      if (data.success) {
        setToken(data.token);
        return true;
      } else {
        setError(data.error || 'Login failed');
        return false;
      }
    } catch (err) {
      setError('Connection failed. Is the API server running?');
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await fetch(`${API_BASE}/auth/logout`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
      });
    } catch (_) {
      // Logout silently even if API is unreachable
    }
    setToken(null);
  };

  const authFetch = async (url, options = {}) => {
    const headers = {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
    };
    const res = await fetch(`${API_BASE}${url}`, { ...options, headers });

    if (res.status === 401) {
      setToken(null);
      throw new Error('Session expired');
    }
    return res;
  };

  return (
    <AuthContext.Provider value={{ token, isAuthenticated, loading, error, login, logout, authFetch }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
