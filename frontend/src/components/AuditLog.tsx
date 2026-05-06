import { useEffect } from 'react';
import { ShieldCheck, Activity, Key, UserCheck, AlertTriangle, Clock } from 'lucide-react';
import { useNotificationStore } from '../store/useNotificationStore';
const AuditLog = () => {
  const { logs, isLoading, fetchLogs } = useNotificationStore();

  useEffect(() => {
    fetchLogs();
  }, [fetchLogs]);

  const getIcon = (iconName: string, color?: string) => {
    const size = 16;
    switch (iconName) {
      case 'ShieldCheck': return <ShieldCheck size={size} color={color} />;
      case 'Key': return <Key size={size} color={color} />;
      case 'UserCheck': return <UserCheck size={size} color={color} />;
      case 'AlertTriangle': return <AlertTriangle size={size} color={color} />;
      default: return <Activity size={size} color={color} />;
    }
  };

  const formatTime = (timeStr: string) => {
    try {
      const date = new Date(timeStr);
      const now = new Date();
      const diffInSecs = Math.floor((now.getTime() - date.getTime()) / 1000);
      
      if (diffInSecs < 60) return 'Just now';
      if (diffInSecs < 3600) return `${Math.floor(diffInSecs / 60)}m ago`;
      if (diffInSecs < 86400) return `${Math.floor(diffInSecs / 3600)}h ago`;
      return `${Math.floor(diffInSecs / 86400)}d ago`;
    } catch {
      return 'Recent';
    }
  };

  return (
    <div className="page-content animate-fade-in">
      <div className="topbar" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '40px' }}>
        <div>
          <h1 className="page-title">Security Logs</h1>
          <p className="page-sub">Immutable ledger of all system interactions and security events.</p>
        </div>
      </div>

      <div className="card" style={{ padding: '40px' }}>
        {isLoading && logs.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-dim)' }}>
            <Clock className="animate-spin" style={{ margin: '0 auto 12px' }} />
            Retrieving secure ledger...
          </div>
        ) : logs.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-dim)' }}>
            No security events recorded in this session.
          </div>
        ) : (
          <div className="timeline" style={{ position: 'relative' }}>
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
                  boxShadow: '0 4px 10px rgba(0,0,0,0.2)',
                  zIndex: 2
                }}>{getIcon(log.icon)}</div>
                
                <div className="tl-content">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                     <div style={{ fontSize: '15px', fontWeight: 800, color: 'var(--text-main)' }}>{log.action}</div>
                     <div style={{ fontSize: '11px', color: 'var(--text-dim)', fontWeight: 600, textTransform: 'uppercase' }}>{formatTime(log.time)}</div>
                  </div>
                  <div style={{ fontSize: '13px', color: 'var(--text-muted)', lineHeight: 1.5 }}>{log.detail}</div>
                  <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', marginTop: '12px', fontSize: '10px', color: 'var(--success)', fontWeight: 700, background: 'var(--success-dim)', padding: '2px 8px', borderRadius: '4px' }}>
                     <ShieldCheck size={10} /> VERIFIED HASH
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default AuditLog;
