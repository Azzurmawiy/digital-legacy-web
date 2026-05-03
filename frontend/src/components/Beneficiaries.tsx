import React, { useEffect, useState } from 'react';
import { UserPlus, Mail, ShieldAlert, Trash2, X, MoreVertical, ShieldCheck } from 'lucide-react';
import { useBeneficiaryStore } from '../store/useBeneficiaryStore';

const Beneficiaries = () => {
  const { beneficiaries, fetch, add, remove } = useBeneficiaryStore();
  const [isAdding, setIsAdding] = useState(false);
  const [form, setForm] = useState({ name: '', email: '', relationship: '', permissions: { can_view_vault: true } });

  useEffect(() => { fetch(); }, [fetch]);

  const getInitials = (name: string) => name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await add(form);
      setIsAdding(false);
      setForm({ name: '', email: '', relationship: '', permissions: { can_view_vault: true } });
    } catch {
      // Error handled by store
    }
  };

  return (
    <div className="page-content animate-fade-in">
      <div className="topbar" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '40px' }}>
        <div>
          <h1 className="page-title">Heir Management</h1>
          <p className="page-sub">Authorized individuals who will receive your legacy assets.</p>
        </div>
        <div className="topbar-right">
           <button className="btn btn-primary" onClick={() => setIsAdding(!isAdding)}>
              {isAdding ? <X size={16} /> : <UserPlus size={16} />}
              {isAdding ? 'Cancel' : 'Authorize New Heir'}
           </button>
        </div>
      </div>

      {isAdding && (
        <div className="card animate-fade-in" style={{ marginBottom: '40px', background: 'var(--bg-panel-light)' }}>
          <h3 style={{ fontSize: '18px', fontWeight: 800, marginBottom: '24px' }}>New Heir Authorization</h3>
          <form onSubmit={handleSubmit} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            <div>
               <label style={{ display: 'block', fontSize: '11px', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '8px' }}>Legal Name</label>
               <input className="btn btn-ghost" style={{ width: '100%', background: 'var(--bg-main)', textAlign: 'left' }} placeholder="Full legal name" value={form.name} onChange={e => setForm({...form, name: e.target.value})} />
            </div>
            <div>
               <label style={{ display: 'block', fontSize: '11px', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '8px' }}>Relationship</label>
               <input className="btn btn-ghost" style={{ width: '100%', background: 'var(--bg-main)', textAlign: 'left' }} placeholder="e.g. Spouse, Child, Solicitor" value={form.relationship} onChange={e => setForm({...form, relationship: e.target.value})} />
            </div>
            <div style={{ gridColumn: 'span 2' }}>
               <label style={{ display: 'block', fontSize: '11px', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '8px' }}>Secure Email Address</label>
               <input className="btn btn-ghost" style={{ width: '100%', background: 'var(--bg-main)', textAlign: 'left' }} placeholder="heir@example.com" value={form.email} onChange={e => setForm({...form, email: e.target.value})} />
            </div>
            <div style={{ gridColumn: 'span 2', display: 'flex', justifyContent: 'flex-end', marginTop: '10px' }}>
               <button type="submit" className="btn btn-primary" style={{ padding: '12px 24px' }}>Generate Authorization Grant</button>
            </div>
          </form>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '20px' }}>
        {beneficiaries.map((b) => (
          <div key={b.id} className="card" style={{ padding: '24px' }}>
             <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px' }}>
                <div style={{ 
                  width: '56px', height: '56px', borderRadius: '16px', 
                  background: 'linear-gradient(135deg, var(--bg-main), var(--bg-panel-light))',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '18px', fontWeight: 800, color: 'var(--primary)',
                  border: '1px solid var(--border)'
                }}>{getInitials(b.name)}</div>
                <div style={{ textAlign: 'right' }}>
                   <div style={{ 
                     fontSize: '10px', color: 'var(--success)', background: 'var(--success-dim)', 
                     padding: '2px 10px', borderRadius: '20px', fontWeight: 800, border: '1px solid rgba(16,185,129,0.1)'
                   }}>VERIFIED HEIR</div>
                   <button style={{ background: 'none', border: 'none', color: 'var(--text-dim)', marginTop: '8px', cursor: 'pointer' }}><MoreVertical size={16} /></button>
                </div>
             </div>
             <h3 style={{ fontSize: '18px', fontWeight: 800, marginBottom: '4px' }}>{b.name}</h3>
             <div style={{ fontSize: '13px', color: 'var(--primary)', fontWeight: 600, marginBottom: '16px' }}>{b.relationship}</div>
             
             <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '24px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: 'var(--text-muted)' }}>
                   <Mail size={14} color="var(--text-dim)" /> {b.email}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: 'var(--success)', fontWeight: 600 }}>
                   <ShieldCheck size={14} /> Full Access Authorized
                </div>
             </div>
             
             <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '16px', borderTop: '1px solid var(--border)' }}>
                <span style={{ fontSize: '11px', color: 'var(--text-dim)', fontWeight: 600 }}>ID: DL-882-{b.id.slice(0,4).toUpperCase()}</span>
                <button onClick={() => remove(b.id)} style={{ color: 'var(--error)', background: 'none', border: 'none', cursor: 'pointer', fontSize: '12px', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '6px' }}>
                   <Trash2 size={14} /> Revoke
                </button>
             </div>
          </div>
        ))}
      </div>

      <div className="card" style={{ 
        marginTop: '40px', display: 'flex', gap: '20px', alignItems: 'center', 
        background: 'var(--accent-dim)', borderColor: 'rgba(91,156,246,0.2)',
        padding: '20px 30px'
      }}>
         <div style={{ padding: '12px', background: 'rgba(91,156,246,0.1)', borderRadius: '12px' }}>
            <ShieldAlert size={28} color="var(--accent)" />
         </div>
         <div>
            <h4 style={{ fontSize: '14px', fontWeight: 800, marginBottom: '4px', color: 'var(--accent)' }}>Legal Protection Protocol</h4>
            <p style={{ fontSize: '12px', color: 'var(--text-main)', opacity: 0.8, lineHeight: 1.6 }}>
               Beneficiaries are only granted decryption keys once the <strong>Dead Man's Switch</strong> reaches the release state. 
               All access attempts are logged and require dual-factor verification.
            </p>
         </div>
      </div>
    </div>
  );
};

export default Beneficiaries;
