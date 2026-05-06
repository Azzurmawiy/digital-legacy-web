import React, { useState } from 'react';
import { useAuthStore } from '../store/useAuthStore';
import { useNavigate, Link } from 'react-router-dom';
import { Hexagon, ShieldCheck } from 'lucide-react';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const { login, isLoading, error } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login({ username, password });
      navigate('/dashboard');
    } catch {
      // Error is handled by store
    }
  };

  return (
    <div style={{ display: 'flex', height: '100vh', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-main)' }}>
      <div className="card animate-fade-in" style={{ padding: '40px', width: '100%', maxWidth: '420px', background: 'var(--bg-panel)' }}>
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div style={{ 
            width: '48px', height: '48px', background: 'var(--primary-dim)', 
            border: '1px solid var(--primary)', borderRadius: '12px', 
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 16px'
          }}>
            <Hexagon size={24} color="var(--primary)" />
          </div>
          <h1 style={{ fontSize: '24px', fontWeight: 800, color: 'var(--primary)', marginBottom: '8px' }}>Digital Legacy</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '14px' }}>Secure vault access portal</p>
        </div>

        {error && (
          <div style={{ background: 'var(--error-dim)', color: 'var(--error)', padding: '12px', borderRadius: '8px', marginBottom: '20px', textAlign: 'center', fontSize: '13px', border: '1px solid rgba(240,106,106,0.2)' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontSize: '12px', fontWeight: 600, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Email or Phone</label>
            <input 
              type="text" 
              className="input-field" 
              placeholder="Email or Phone Number"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required 
            />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontSize: '12px', fontWeight: 600, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Password</label>
            <input 
              type="password" 
              className="input-field" 
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required 
            />
          </div>
          <button type="submit" className="btn btn-primary" disabled={isLoading} style={{ width: '100%', justifyContent: 'center', padding: '12px', fontSize: '14px', marginTop: '8px' }}>
            {isLoading ? 'Decrypting...' : 'Sign In to Vault'}
          </button>
        </form>

        <div style={{ marginTop: '24px', textAlign: 'center', fontSize: '13px' }}>
          <span style={{ color: 'var(--text-muted)' }}>First time here? </span>
          <Link to="/register" style={{ color: 'var(--primary)', textDecoration: 'none', fontWeight: 600 }}>Create an account</Link>
        </div>
        
        <div style={{ marginTop: '32px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', opacity: 0.5 }}>
           <ShieldCheck size={14} color="var(--success)" />
           <span style={{ fontSize: '10px', color: 'var(--text-dim)' }}>End-to-End Encrypted</span>
        </div>
      </div>
    </div>
  );
};

export default Login;
