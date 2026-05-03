import React from 'react';
import { ShieldCheck, Activity, Key, UserCheck, AlertTriangle } from 'lucide-react';

const AuditLog = () => {
  const logs = [
    { id: 1, action: 'Heartbeat registered', detail: 'Verified via encrypted session 0x882', time: '2 hours ago', icon: <Activity size={14} />, color: 'var(--success)' },
    { id: 2, action: 'Asset Stored: Will_2026.pdf', detail: 'AES-256-GCM Encryption Finalized', time: 'Yesterday, 3:14 PM', icon: <ShieldCheck size={14} />, color: 'var(--primary)' },
    { id: 3, action: 'Heir Verification', detail: 'Sultana X. identity confirmed', time: '2 days ago', icon: <UserCheck size={14} />, color: 'var(--accent)' },
    { id: 4, action: 'MFA login successful', detail: 'TOTP Code validated from device SM-G998', time: '3 days ago', icon: <Key size={14} />, color: 'var(--success)' },
    { id: 5, action: 'DMS Config Updated', detail: 'Threshold set to 90 days / 7 days cooling', time: '1 week ago', icon: <AlertTriangle size={14} />, color: '#f06a6a' },
  ];

  return (
    <div className="page-content animate-fade-in">
      <div className="topbar" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '40px' }}>
        <div>
          <h1 className="page-title">Security Logs</h1>
          <p className="page-sub">Immutable ledger of all system interactions and security events.</p>
        </div>
      </div>

      <div className="card" style={{ padding: '40px' }}>
        <div className="timeline" style={{ position: 'relative' }}>
          {/* Vertical Line */}
          <div style={{ 
            position: 'absolute', 
            left: '20px', 
            top: '0', 
            bottom: '0', 
            width: '1px', 
            background: 'linear-gradient(180deg, var(--primary) 0%, var(--border) 100%)',
            opacity: 0.3
          }}></div>

          {logs.map((log) => (
            <div key={log.id} style={{ position: 'relative', paddingLeft: '56px', marginBottom: '32px' }}>
              {/* Icon / Dot */}
              <div style={{ 
                width: '40px', 
                height: '40px', 
                borderRadius: '12px', 
                background: 'var(--bg-main)', 
                border: '1px solid var(--border)', 
                position: 'absolute', 
                left: '0', 
                top: '-4px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: log.color,
                boxShadow: '0 4px 10px rgba(0,0,0,0.2)',
                zIndex: 2
              }}>{log.icon}</div>
              
              <div className="tl-content">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                   <div style={{ fontSize: '15px', fontWeight: 800, color: 'var(--text-main)' }}>{log.action}</div>
                   <div style={{ fontSize: '11px', color: 'var(--text-dim)', fontWeight: 600, textTransform: 'uppercase' }}>{log.time}</div>
                </div>
                <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>{log.detail}</div>
                <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', marginTop: '12px', fontSize: '10px', color: 'var(--success)', fontWeight: 700, background: 'var(--success-dim)', padding: '2px 8px', borderRadius: '4px' }}>
                   <ShieldCheck size={10} /> VERIFIED HASH
                </div>
              </div>
            </div>
          ))}
          
          <div style={{ paddingLeft: '56px' }}>
             <button className="btn btn-ghost" style={{ fontSize: '12px', color: 'var(--text-dim)' }}>Load previous logs...</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuditLog;
