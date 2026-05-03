import { useEffect, useState, type FormEvent } from 'react';
import { Heart, Plus, Trash2, X, Send, Lock } from 'lucide-react';
import { useVaultStore } from '../store/useVaultStore';

const Memories = () => {
   const { items, fetch, upload, remove } = useVaultStore();
   const [isAdding, setIsAdding] = useState(false);
   const [formData, setFormData] = useState({ title: '', description: '', item_type: 'note' });

   useEffect(() => { fetch(); }, [fetch]);

   const memoryItems = items.filter(item => item.item_type === 'note' || item.item_type === 'memory' || item.item_type === 'message');

   const handleSubmit = async (e: FormEvent) => {
      e.preventDefault();
      const blob = new Blob([formData.description], { type: 'text/plain' });
      const file = new File([blob], `${formData.title}.txt`, { type: 'text/plain' });
      const data = new FormData();
      data.append('file', file);
      data.append('title', formData.title);
      data.append('description', formData.description);
      data.append('item_type', 'note');
      await upload(data);
      setIsAdding(false);
      setFormData({ title: '', description: '', item_type: 'note' });
   };

   return (
      <div className="page-content animate-fade-in">
         <div className="topbar" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '40px' }}>
            <div>
               <h1 className="page-title">Legacy Messages</h1>
               <p className="page-sub">Heartfelt letters encrypted and stored for your loved ones.</p>
            </div>
            <div className="topbar-right">
               <button className="btn btn-primary" onClick={() => setIsAdding(!isAdding)}>
                  {isAdding ? <X size={16} /> : <Plus size={16} />}
                  {isAdding ? 'Close Composer' : 'Compose Message'}
               </button>
            </div>
         </div>

         {isAdding && (
            <div className="card animate-fade-in" style={{ marginBottom: '40px', background: 'var(--bg-panel-light)', border: '1px solid var(--border-gold)' }}>
               <h3 style={{ fontSize: '18px', fontWeight: 800, marginBottom: '24px' }}>Draft Legacy Message</h3>
               <form onSubmit={handleSubmit}>
                  <div style={{ marginBottom: '20px' }}>
                     <label style={{ display: 'block', fontSize: '11px', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '8px' }}>Recipient / Subject</label>
                     <input className="btn btn-ghost" style={{ width: '100%', background: 'var(--bg-main)', textAlign: 'left', fontSize: '15px' }} placeholder="To my daughter, Sarah..." value={formData.title} onChange={e => setFormData({ ...formData, title: e.target.value })} />
                  </div>
                  <div style={{ marginBottom: '24px' }}>
                     <label style={{ display: 'block', fontSize: '11px', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '8px' }}>The Message</label>
                     <textarea className="btn btn-ghost" style={{ width: '100%', minHeight: '200px', background: 'var(--bg-main)', textAlign: 'left', paddingTop: '16px', lineHeight: 1.8, resize: 'vertical' }} placeholder="Start writing your legacy message..." value={formData.description} onChange={e => setFormData({ ...formData, description: e.target.value })} />
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                     <div style={{ fontSize: '12px', color: 'var(--text-dim)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <Lock size={12} /> Message will be AES-256 encrypted
                     </div>
                     <button type="submit" className="btn btn-primary" style={{ padding: '12px 28px' }}>
                        <Send size={16} /> Seal & Encrypt
                     </button>
                  </div>
               </form>
            </div>
         )}

         <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '20px' }}>
            {memoryItems.map((item) => (
               <div key={item.id} className="card" style={{ display: 'flex', flexDirection: 'column', minHeight: '280px', padding: '30px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px' }}>
                     <div style={{
                        width: '44px', height: '44px', borderRadius: '50%',
                        background: 'rgba(239,68,68,0.1)', color: '#ef4444',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        boxShadow: '0 0 15px rgba(239,68,68,0.1)'
                     }}><Heart size={22} fill="#ef4444" /></div>
                     <div style={{ textAlign: 'right' }}>
                        <div style={{ fontSize: '10px', color: 'var(--text-dim)', fontWeight: 700, letterSpacing: '0.05em' }}>SEALED DATE</div>
                        <div style={{ fontSize: '11px', fontWeight: 600 }}>{new Date(item.uploaded_at).toLocaleDateString()}</div>
                     </div>
                  </div>
                  <h3 style={{ fontSize: '19px', fontWeight: 800, marginBottom: '12px', color: 'var(--primary)' }}>{item.title}</h3>
                  <p style={{
                     fontSize: '14px', color: 'var(--text-muted)', lineHeight: 1.7,
                     display: '-webkit-box', WebkitLineClamp: 5, WebkitBoxOrient: 'vertical',
                     overflow: 'hidden', marginBottom: '24px', flex: 1
                  }}>
                     {item.description}
                  </p>
                  <div style={{ paddingTop: '20px', borderTop: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                     <div style={{ fontSize: '11px', color: 'var(--text-dim)', fontWeight: 700, textTransform: 'uppercase' }}>Encrypted Note</div>
                     <button onClick={() => remove(item.id)} style={{ color: 'var(--text-dim)', background: 'none', border: 'none', cursor: 'pointer', transition: '0.2s' }} onMouseEnter={(e) => e.currentTarget.style.color = 'var(--error)'} onMouseLeave={(e) => e.currentTarget.style.color = 'var(--text-dim)'}>
                        <Trash2 size={16} />
                     </button>
                  </div>
               </div>
            ))}
         </div>
      </div>
   );
};

export default Memories;
