import React, { useState } from 'react';
import { useAuthStore } from '../store/useAuthStore';
import { useNavigate, Link } from 'react-router-dom';
import { UserPlus } from 'lucide-react';

const Register = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    first_name: '',
    last_name: ''
  });
  const [success, setSuccess] = useState(false);
  const { register, isLoading, error } = useAuthStore();
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await register(formData);
      setSuccess(true);
      setTimeout(() => navigate('/login'), 3000);
    } catch {
      // Error handled by store
    }
  };

  if (success) {
    return (
      <div style={{ display: 'flex', height: '100vh', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-main)' }}>
        <div className="card animate-fade-in" style={{ padding: '40px', width: '100%', maxWidth: '400px', textAlign: 'center' }}>
          <h2 style={{ color: 'var(--primary)', marginBottom: '16px' }}>Account Created!</h2>
          <p style={{ color: 'var(--text-muted)' }}>Registration successful. Redirecting you to login...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', height: '100vh', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-main)' }}>
      <div className="card animate-fade-in" style={{ padding: '40px', width: '100%', maxWidth: '480px', background: 'var(--bg-panel)' }}>
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div style={{ 
            width: '48px', height: '48px', background: 'var(--primary-dim)', 
            border: '1px solid var(--primary)', borderRadius: '12px', 
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 16px'
          }}>
            <UserPlus size={24} color="var(--primary)" />
          </div>
          <h1 style={{ fontSize: '24px', fontWeight: 800, color: 'var(--primary)', marginBottom: '8px' }}>Create Account</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '14px' }}>Begin your digital legacy journey</p>
        </div>

        {error && (
          <div style={{ background: 'var(--error-dim)', color: 'var(--error)', padding: '12px', borderRadius: '8px', marginBottom: '20px', textAlign: 'center', fontSize: '13px', border: '1px solid rgba(240,106,106,0.2)' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '8px', fontSize: '12px', fontWeight: 600, color: 'var(--text-dim)', textTransform: 'uppercase' }}>First Name</label>
              <input type="text" name="first_name" className="input-field" value={formData.first_name} onChange={handleChange} required />
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '8px', fontSize: '12px', fontWeight: 600, color: 'var(--text-dim)', textTransform: 'uppercase' }}>Last Name</label>
              <input type="text" name="last_name" className="input-field" value={formData.last_name} onChange={handleChange} required />
            </div>
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontSize: '12px', fontWeight: 600, color: 'var(--text-dim)', textTransform: 'uppercase' }}>Email Address</label>
            <input type="email" name="email" className="input-field" value={formData.email} onChange={handleChange} required />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontSize: '12px', fontWeight: 600, color: 'var(--text-dim)', textTransform: 'uppercase' }}>Master Password</label>
            <input type="password" name="password" className="input-field" value={formData.password} onChange={handleChange} required placeholder="Min 12 characters" minLength={12} />
          </div>
          <button type="submit" className="btn btn-primary" disabled={isLoading} style={{ width: '100%', justifyContent: 'center', padding: '12px', fontSize: '14px', marginTop: '16px' }}>
            {isLoading ? 'Securing Identity...' : 'Register Secure Account'}
          </button>
        </form>

        <div style={{ marginTop: '24px', textAlign: 'center', fontSize: '13px' }}>
          <span style={{ color: 'var(--text-muted)' }}>Already a member? </span>
          <Link to="/login" style={{ color: 'var(--primary)', textDecoration: 'none', fontWeight: 600 }}>Sign in</Link>
        </div>
      </div>
    </div>
  );
};

export default Register;
