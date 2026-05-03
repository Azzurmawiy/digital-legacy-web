import React, { useEffect } from 'react';
import { Clock, FileText, Users, Heart, ArrowUpRight } from 'lucide-react';
import { useDmsStore } from '../store/useDmsStore';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';

const Dashboard = () => {
  const { isLoading, fetchConfig, sendHeartbeat } = useDmsStore();

  useEffect(() => { fetchConfig(); }, [fetchConfig]);

  const handleHeartbeat = async () => {
    try {
      await sendHeartbeat();
      toast.success("Heartbeat successfully sent. Timer reset.");
    } catch {
      toast.error("Failed to send heartbeat.");
    }
  };

  return (
    <div className="page-content animate-fade-in">
      <div className="topbar" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '40px' }}>
        <div>
          <h1 className="page-title">Legacy Overview</h1>
          <p className="page-sub">Your digital assets are encrypted and monitored.</p>
        </div>
        <div className="topbar-right" style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <div className="heartbeat-badge" style={{ 
            display: 'flex', alignItems: 'center', gap: '10px', 
            padding: '8px 16px', background: 'var(--success-dim)', 
            border: '1px solid rgba(16,185,129,0.2)', borderRadius: '30px', 
            fontSize: '12px', color: 'var(--success)', fontWeight: 700 
          }}>
            <div className="pulse" style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--success)', boxShadow: '0 0 10px var(--success)' }}></div>
            SYSTEM SECURE
          </div>
          <button className="btn btn-primary" onClick={handleHeartbeat} disabled={isLoading}>
             Send Heartbeat
          </button>
        </div>
      </div>

      <div className="stats-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px', marginBottom: '32px' }}>
        {[
          { label: 'Vault Assets', value: '24', detail: '1.2 GB Secured', icon: <FileText size={20} color="var(--primary)" />, color: 'var(--primary)' },
          { label: 'Verified Heirs', value: '4', detail: 'Authorized', icon: <Users size={20} color="var(--success)" />, color: 'var(--success)' },
          { label: 'DMS Status', value: 'Active', detail: '68 Days Left', icon: <Clock size={20} color="var(--accent)" />, color: 'var(--accent)' },
          { label: 'Memories', value: '7', detail: 'Encrypted', icon: <Heart size={20} color="#f06a6a" />, color: '#f06a6a' },
        ].map((stat, i) => (
          <div key={i} className="card" style={{ padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
               <div style={{ padding: '10px', background: 'rgba(255,255,255,0.03)', borderRadius: '12px', border: '1px solid var(--border)' }}>{stat.icon}</div>
               <ArrowUpRight size={16} color="var(--text-dim)" />
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{stat.label}</div>
            <div style={{ fontSize: '32px', fontWeight: 800, margin: '4px 0', fontFamily: 'var(--font-heading)' }}>{stat.value}</div>
            <div style={{ fontSize: '11px', color: stat.color, fontWeight: 700 }}>{stat.detail}</div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '20px' }}>
        <div className="card" style={{ display: 'flex', flexDirection: 'column' }}>
           <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
              <h3 style={{ fontSize: '18px', fontWeight: 800 }}>Monitoring Status</h3>
              <Link to="/settings" className="btn btn-ghost" style={{ fontSize: '12px', padding: '6px 12px' }}>Settings</Link>
           </div>
           <div style={{ display: 'flex', alignItems: 'center', gap: '40px', flex: 1 }}>
              <div style={{ position: 'relative', width: '140px', height: '140px' }}>
                 <svg viewBox="0 0 140 140">
                    <circle cx="70" cy="70" r="62" fill="none" stroke="rgba(255,255,255,0.03)" strokeWidth="12"/>
                    <circle cx="70" cy="70" r="62" fill="none" stroke="url(#goldGradient)" strokeWidth="12"
                       strokeDasharray="389.5" strokeDashoffset="120" strokeLinecap="round"
                       transform="rotate(-90 70 70)"/>
                    <defs>
                       <linearGradient id="goldGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                          <stop offset="0%" stopColor="var(--primary)" />
                          <stop offset="100%" stopColor="var(--primary-light)" />
                       </linearGradient>
                    </defs>
                 </svg>
                 <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                    <div style={{ fontSize: '28px', fontWeight: 800, color: 'var(--primary)' }}>68%</div>
                    <div style={{ fontSize: '10px', color: 'var(--text-dim)', fontWeight: 700, textTransform: 'uppercase' }}>Safety</div>
                 </div>
              </div>
              <div style={{ flex: 1 }}>
                 <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                    <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>Time Until Release</span>
                    <span style={{ fontSize: '13px', fontWeight: 700 }}>68 / 90 Days</span>
                 </div>
                 <div style={{ height: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '10px', overflow: 'hidden' }}>
                    <div style={{ width: '68%', height: '100%', background: 'linear-gradient(90deg, var(--primary), var(--primary-light))', borderRadius: '10px' }}></div>
                 </div>
                 <div style={{ marginTop: '20px', padding: '16px', background: 'rgba(0,0,0,0.2)', borderRadius: '12px', border: '1px solid var(--border)' }}>
                    <div style={{ fontSize: '11px', color: 'var(--text-dim)', fontWeight: 700, textTransform: 'uppercase', marginBottom: '4px' }}>Security Protocol</div>
                    <div style={{ fontSize: '13px', color: 'var(--text-main)' }}>Automatic release to <strong>4 heirs</strong> if inactive for 90 days.</div>
                 </div>
              </div>
           </div>
        </div>

        <div className="card">
           <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
              <h3 style={{ fontSize: '18px', fontWeight: 800 }}>Recent Activity</h3>
              <Link to="/audit" className="btn btn-ghost" style={{ fontSize: '12px', padding: '6px 12px' }}>Logs</Link>
           </div>
           <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {[
                { title: 'Heartbeat Check', sub: 'Verified via Web Portal', time: '2h ago', icon: '🟢' },
                { title: 'Vault Access', sub: 'Will_Updated_2026.pdf', time: 'Yesterday', icon: '🔵' },
                { title: 'Identity Verification', sub: 'Sultana X. Authorized', time: '2d ago', icon: '🟡' },
              ].map((item, i) => (
                <div key={i} style={{ display: 'flex', gap: '16px', alignItems: 'center', padding: '12px', borderRadius: '12px', background: 'rgba(255,255,255,0.02)', border: '1px solid transparent', transition: '0.2s' }}>
                   <div style={{ fontSize: '16px' }}>{item.icon}</div>
                   <div style={{ flex: 1 }}>
                      <div style={{ fontSize: '13px', fontWeight: 700 }}>{item.title}</div>
                      <div style={{ fontSize: '11px', color: 'var(--text-dim)' }}>{item.sub}</div>
                   </div>
                   <div style={{ fontSize: '10px', color: 'var(--text-dim)', fontWeight: 600 }}>{item.time}</div>
                </div>
              ))}
           </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
