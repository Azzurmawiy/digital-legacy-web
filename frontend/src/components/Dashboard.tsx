import { useEffect } from 'react';
import { Clock, FileText, Users, Heart, ArrowUpRight } from 'lucide-react';
import { useDmsStore } from '../store/useDmsStore';
import { useAuthStore } from '../store/useAuthStore';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';

const Dashboard = () => {
  const { isLoading: dmsLoading, fetchConfig, sendHeartbeat } = useDmsStore();
  const { stats, fetchStats } = useAuthStore();

  useEffect(() => { 
    fetchConfig(); 
    fetchStats();
  }, [fetchConfig, fetchStats]);

  const handleHeartbeat = async () => {
    try {
      await sendHeartbeat();
      toast.success("Heartbeat successfully sent. Timer reset.");
      fetchStats(); // Refresh stats after heartbeat
    } catch {
      toast.error("Failed to send heartbeat.");
    }
  };

  const statItems = [
    { 
      label: 'Vault Assets', 
      value: String(stats?.vault_count ?? 0), 
      detail: `${stats?.vault_size_mb ?? 0} MB Secured`, 
      icon: <FileText size={20} color="var(--primary)" />, 
      color: 'var(--primary)' 
    },
    { 
      label: 'Verified Heirs', 
      value: String(stats?.beneficiary_count ?? 0), 
      detail: 'Authorized', 
      icon: <Users size={20} color="var(--success)" />, 
      color: 'var(--success)' 
    },
    { 
      label: 'DMS Status', 
      value: stats?.dms_status || 'Inactive', 
      detail: `${stats?.dms_days_left ?? 0} Days Left`, 
      icon: <Clock size={20} color="var(--accent)" />, 
      color: 'var(--accent)' 
    },
    { 
      label: 'Memories', 
      value: String(stats?.memories_count ?? 0), 
      detail: 'Encrypted', 
      icon: <Heart size={20} color="#f06a6a" />, 
      color: '#f06a6a' 
    },
  ];

  const formatTime = (timeStr: string) => {
    try {
      const date = new Date(timeStr);
      if (isNaN(date.getTime())) return 'Just now';
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return 'Just now';
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
            {stats?.dms_status === 'Active' ? 'SYSTEM SECURE' : 'SYSTEM INACTIVE'}
          </div>
          <button className="btn btn-primary" onClick={handleHeartbeat} disabled={dmsLoading}>
             Send Heartbeat
          </button>
        </div>
      </div>

      <div className="stats-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px', marginBottom: '32px' }}>
        {statItems.map((stat, i) => (
          <div key={i} className="card" style={{ padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
               <div style={{ padding: '10px', background: 'rgba(255,255,255,0.02)', borderRadius: '12px', border: '1px solid var(--border)' }}>{stat.icon}</div>
               <ArrowUpRight size={16} color="var(--text-dim)" />
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{stat.label}</div>
            <div style={{ fontSize: '32px', fontWeight: 800, margin: '4px 0', fontFamily: 'var(--font-heading)' }}>{stat.value}</div>
            <div style={{ fontSize: '11px', color: stat.color, fontWeight: 700 }}>{stat.detail}</div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px' }}>
        {/* Monitoring Status */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column' }}>
           <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
              <h3 style={{ fontSize: '16px', fontWeight: 800 }}>Monitoring</h3>
              <Link to="/settings" className="btn btn-ghost" style={{ fontSize: '10px', padding: '4px 8px' }}>Config</Link>
           </div>
           <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '20px', flex: 1 }}>
              <div style={{ position: 'relative', width: '100px', height: '100px' }}>
                 <svg viewBox="0 0 100 100">
                    <circle cx="50" cy="50" r="44" fill="none" stroke="rgba(255,255,255,0.03)" strokeWidth="8"/>
                    <circle cx="50" cy="50" r="44" fill="none" stroke="url(#goldGradient)" strokeWidth="8"
                       strokeDasharray="276.5" strokeDashoffset={276.5 - (276.5 * (stats?.safety_score ?? 0) / 100)} strokeLinecap="round"
                       transform="rotate(-90 50 50)"/>
                 </svg>
                 <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                    <div style={{ fontSize: '20px', fontWeight: 800, color: 'var(--primary)' }}>{stats?.safety_score ?? 0}%</div>
                 </div>
              </div>
              <div style={{ width: '100%' }}>
                 <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '12px' }}>
                    <span style={{ color: 'var(--text-dim)' }}>DMS Status</span>
                    <span style={{ fontWeight: 700 }}>{stats?.dms_days_left ?? 0}d Left</span>
                 </div>
                 <div style={{ height: '6px', background: 'rgba(255,255,255,0.05)', borderRadius: '10px', overflow: 'hidden' }}>
                    <div style={{ width: `${Math.min(100, ((stats?.dms_days_left ?? 0) / (stats?.dms_threshold ?? 90)) * 100)}%`, height: '100%', background: 'linear-gradient(90deg, var(--primary), var(--primary-light))', borderRadius: '10px' }}></div>
                 </div>
              </div>
           </div>
        </div>

        {/* Recent Vault Assets */}
        <div className="card">
           <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
              <h3 style={{ fontSize: '16px', fontWeight: 800 }}>Recent Vault</h3>
              <Link to="/vault" className="btn btn-ghost" style={{ fontSize: '10px', padding: '4px 8px' }}>View All</Link>
           </div>
           <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {stats?.recent_vault && stats.recent_vault.length > 0 ? (
                stats.recent_vault.map((item: any) => (
                  <div key={item.id} style={{ display: 'flex', gap: '12px', alignItems: 'center', padding: '10px', borderRadius: '10px', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border)' }}>
                     <div style={{ width: '32px', height: '32px', background: 'var(--bg-main)', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <FileText size={14} color="var(--primary)" />
                     </div>
                     <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ fontSize: '12px', fontWeight: 700, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{item.title}</div>
                        <div style={{ fontSize: '10px', color: 'var(--text-dim)' }}>{item.type}</div>
                     </div>
                  </div>
                ))
              ) : (
                <div style={{ textAlign: 'center', padding: '20px', color: 'var(--text-dim)', fontSize: '12px' }}>No items found.</div>
              )}
           </div>
        </div>

        {/* Recent Activity */}
        <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
               <h3 style={{ fontSize: '16px', fontWeight: 800 }}>Security Logs</h3>
               <Link to="/audit" className="btn btn-ghost" style={{ fontSize: '10px', padding: '4px 8px' }}>Logs</Link>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
               {stats?.recent_activity && stats.recent_activity.length > 0 ? (
                 stats.recent_activity.map((item: any, i: number) => (
                   <div key={i} style={{ display: 'flex', gap: '12px', alignItems: 'center', padding: '10px', borderRadius: '10px', background: 'rgba(255,255,255,0.02)' }}>
                      <div style={{ fontSize: '14px' }}>{item.icon || '🔔'}</div>
                      <div style={{ flex: 1, minWidth: 0 }}>
                         <div style={{ fontSize: '12px', fontWeight: 700, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{item.title}</div>
                         <div style={{ fontSize: '10px', color: 'var(--text-dim)' }}>{formatTime(item.time)}</div>
                      </div>
                   </div>
                 ))
               ) : (
                 <div style={{ textAlign: 'center', padding: '20px', color: 'var(--text-dim)', fontSize: '12px' }}>No recent activity.</div>
               )}
            </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
