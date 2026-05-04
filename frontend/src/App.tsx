import type { ReactElement } from 'react';
import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { Menu } from 'lucide-react';
import { useAuthStore } from './store/useAuthStore';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import Vault from './components/Vault';
import Memories from './components/Memories';
import Beneficiaries from './components/Beneficiaries';
import DMSConfig from './components/DMSConfig';
import Login from './components/Login';
import Register from './components/Register';
import AuditLog from './components/AuditLog';
import './App.css';

const PrivateRoute = ({ children }: { children: ReactElement }) => {
  const { isAuthenticated } = useAuthStore();
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

const MainLayout = () => {
  const { logout } = useAuthStore();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="shell">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <main className="main">
        <header className="topbar" style={{ padding: '16px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '16px', borderBottom: '1px solid var(--border)', position: 'sticky', top: 0, zIndex: 50, background: 'var(--bg-main)' }}>
          <button
            className="btn btn-ghost hamburger-btn"
            onClick={() => setSidebarOpen(true)}
            aria-label="Open navigation"
          >
            <Menu size={20} />
          </button>
          <button onClick={logout} className="btn btn-ghost">Logout</button>
        </header>

        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/vault" element={<Vault />} />
          <Route path="/memories" element={<Memories />} />
          <Route path="/beneficiaries" element={<Beneficiaries />} />
          <Route path="/settings" element={<DMSConfig />} />
          <Route path="/audit" element={<AuditLog />} />
        </Routes>
      </main>
    </div>
  );
};


function App() {
  const { isInitializing, checkAuth } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  if (isInitializing) {
    return (
      <div style={{ 
        height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', 
        background: 'var(--bg-main)', color: 'var(--primary)', flexDirection: 'column', gap: '20px' 
      }}>
        <div className="loading-spinner" style={{ width: '40px', height: '40px', border: '3px solid var(--primary-dim)', borderTopColor: 'var(--primary)', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></div>
        <div style={{ fontSize: '12px', letterSpacing: '2px', textTransform: 'uppercase', fontWeight: 600 }}>Initializing Vault</div>
        <style>{`
          @keyframes spin { to { transform: rotate(360deg); } }
        `}</style>
      </div>
    );
  }

  return (
    <Router>
      <Toaster position="top-right" toastOptions={{ style: { background: 'var(--bg-panel)', color: 'var(--text-main)', border: '1px solid var(--border-gold)' } }} />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/*" element={<PrivateRoute><MainLayout /></PrivateRoute>} />
      </Routes>
    </Router>
  );
}

export default App;
