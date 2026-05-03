import { useState, useEffect } from 'react';
import { Save, Clock, ShieldAlert, History } from 'lucide-react';
import toast from 'react-hot-toast';
import { useDmsStore } from '../store/useDmsStore';

const DMSConfig = () => {
  const { config, isLoading, fetchConfig, updateConfig } = useDmsStore();
  const [inactivityThreshold, setInactivityThreshold] = useState(90);
  const [coolingOff, setCoolingOff] = useState(7);

  useEffect(() => { fetchConfig(); }, [fetchConfig]);

  useEffect(() => {
    if (config) {
      // eslint-disable-next-line
      setInactivityThreshold(Number(config.inactivity_threshold_days));
      setCoolingOff(Number(config.cooling_off_days));
    }
  }, [config]);

  const handleSave = async () => {
    try {
      await updateConfig({
        inactivity_threshold_days: inactivityThreshold,
        cooling_off_days: coolingOff
      });
      toast.success('DMS configuration saved successfully.');
    } catch {
      toast.error('Failed to save configuration.');
    }
  };

  return (
    <div className="page-content animate-fade-in">
      <div className="topbar" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '40px' }}>
        <div>
          <h1 className="page-title">Monitoring Protocol</h1>
          <p className="page-sub">Configure the inactivity thresholds and safety release period.</p>
        </div>
        <div className="topbar-right">
           <button className="btn btn-primary" onClick={handleSave} disabled={isLoading}>
              <Save size={16} /> Save Configuration
           </button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '24px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
           {/* SYSTEM STATUS CARD */}
           <div className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                 <h3 style={{ fontSize: '18px', fontWeight: 800 }}>Protocol Execution</h3>
                 <div style={{ padding: '6px 14px', background: 'var(--success-dim)', color: 'var(--success)', borderRadius: '20px', fontSize: '11px', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '8px', border: '1px solid rgba(16,185,129,0.1)' }}>
                    <div className="pulse" style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--success)' }}></div>
                    ACTIVE MONITORING
                 </div>
              </div>
              <div style={{ display: 'flex', gap: '40px', alignItems: 'center' }}>
                 <div style={{ position: 'relative', width: '150px', height: '150px' }}>
                    <svg viewBox="0 0 140 140">
                       <circle cx="70" cy="70" r="62" fill="none" stroke="rgba(255,255,255,0.03)" strokeWidth="12"/>
                       <circle cx="70" cy="70" r="62" fill="none" stroke="url(#goldGradient2)" strokeWidth="12"
                          strokeDasharray="389.5" strokeDashoffset="120" strokeLinecap="round"
                          transform="rotate(-90 70 70)"/>
                       <defs>
                          <linearGradient id="goldGradient2" x1="0%" y1="0%" x2="100%" y2="100%">
                             <stop offset="0%" stopColor="var(--primary)" />
                             <stop offset="100%" stopColor="var(--primary-light)" />
                          </linearGradient>
                       </defs>
                    </svg>
                    <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                       <div style={{ fontSize: '32px', fontWeight: 800, color: 'var(--primary)' }}>68%</div>
                       <div style={{ fontSize: '11px', color: 'var(--text-dim)', fontWeight: 700 }}>STABLE</div>
                    </div>
                 </div>
                 <div style={{ flex: 1 }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                       <div style={{ padding: '16px', background: 'rgba(255,255,255,0.02)', borderRadius: '14px', border: '1px solid var(--border)' }}>
                          <div style={{ fontSize: '10px', color: 'var(--text-dim)', fontWeight: 700, marginBottom: '4px' }}>THRESHOLD</div>
                          <div style={{ fontSize: '16px', fontWeight: 800 }}>{inactivityThreshold} Days</div>
                       </div>
                       <div style={{ padding: '16px', background: 'rgba(255,255,255,0.02)', borderRadius: '14px', border: '1px solid var(--border)' }}>
                          <div style={{ fontSize: '10px', color: 'var(--text-dim)', fontWeight: 700, marginBottom: '4px' }}>COOLING OFF</div>
                          <div style={{ fontSize: '16px', fontWeight: 800 }}>{coolingOff} Days</div>
                       </div>
                    </div>
                    <div style={{ marginTop: '16px', fontSize: '13px', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                       <Clock size={14} /> Last heartbeat received 2 hours ago.
                    </div>
                 </div>
              </div>
           </div>

           {/* LOGS PREVIEW */}
           <div className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                 <h3 style={{ fontSize: '16px', fontWeight: 800 }}>Release Sequence</h3>
                 <History size={16} color="var(--text-dim)" />
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                 <div style={{ display: 'flex', gap: '16px', padding: '12px', borderRadius: '12px', border: '1px solid var(--border)' }}>
                    <div style={{ color: 'var(--primary)', fontWeight: 800, fontSize: '13px' }}>01</div>
                    <div style={{ fontSize: '13px' }}>Monitoring activity via all connected endpoints.</div>
                 </div>
                 <div style={{ display: 'flex', gap: '16px', padding: '12px', borderRadius: '12px', background: 'rgba(212,168,83,0.03)', border: '1px solid var(--border-gold)' }}>
                    <div style={{ color: 'var(--primary)', fontWeight: 800, fontSize: '13px' }}>02</div>
                    <div style={{ fontSize: '13px' }}>Warning notifications triggered at <strong>{Math.floor(inactivityThreshold * 0.75)} days</strong> of inactivity.</div>
                 </div>
                 <div style={{ display: 'flex', gap: '16px', padding: '12px', borderRadius: '12px', border: '1px solid var(--border)' }}>
                    <div style={{ color: 'var(--primary)', fontWeight: 800, fontSize: '13px' }}>03</div>
                    <div style={{ fontSize: '13px' }}>Final release and key distribution after the cooling-off period.</div>
                 </div>
              </div>
           </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
           {/* CONFIG SLIDERS */}
           <div className="card">
              <h3 style={{ fontSize: '18px', fontWeight: 800, marginBottom: '32px' }}>System Configuration</h3>
              
              <div style={{ marginBottom: '40px' }}>
                 <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
                    <label style={{ fontSize: '14px', fontWeight: 600 }}>Inactivity Threshold</label>
                    <span style={{ fontSize: '14px', fontWeight: 800, color: 'var(--primary)' }}>{inactivityThreshold} Days</span>
                 </div>
                 <input 
                    type="range" min="30" max="365" step="1"
                    style={{ width: '100%', height: '4px', background: 'var(--bg-main)', borderRadius: '2px', accentColor: 'var(--primary)', cursor: 'pointer' }}
                    value={inactivityThreshold}
                    onChange={(e) => setInactivityThreshold(Number(e.target.value))} 
                 />
                 <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '12px', fontSize: '11px', color: 'var(--text-dim)', fontWeight: 600 }}>
                    <span>30 DAYS</span>
                    <span>1 YEAR</span>
                 </div>
              </div>

              <div style={{ marginBottom: '40px' }}>
                 <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
                    <label style={{ fontSize: '14px', fontWeight: 600 }}>Cooling-off Period</label>
                    <span style={{ fontSize: '14px', fontWeight: 800, color: 'var(--primary)' }}>{coolingOff} Days</span>
                 </div>
                 <input 
                    type="range" min="3" max="30" step="1"
                    style={{ width: '100%', height: '4px', background: 'var(--bg-main)', borderRadius: '2px', accentColor: 'var(--primary)', cursor: 'pointer' }}
                    value={coolingOff}
                    onChange={(e) => setCoolingOff(Number(e.target.value))} 
                 />
                 <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '12px', fontSize: '11px', color: 'var(--text-dim)', fontWeight: 600 }}>
                    <span>3 DAYS</span>
                    <span>30 DAYS</span>
                 </div>
              </div>

              <div style={{ padding: '20px', background: 'rgba(255,255,255,0.02)', borderRadius: '16px', border: '1px solid var(--border)' }}>
                 <div style={{ display: 'flex', gap: '14px', alignItems: 'flex-start' }}>
                    <ShieldAlert size={20} color="var(--primary)" />
                    <div style={{ fontSize: '12px', lineHeight: 1.6, opacity: 0.8 }}>
                       <strong>Danger Zone:</strong> Reducing the threshold below 60 days may trigger false releases if you are away without internet access. We recommend at least 90 days for most users.
                    </div>
                 </div>
              </div>
           </div>
        </div>
      </div>
    </div>
  );
};

export default DMSConfig;
