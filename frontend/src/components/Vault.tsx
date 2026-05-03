import { useEffect, useState } from 'react';
import { FileUp, X, Search } from 'lucide-react';
import { useVaultStore } from '../store/useVaultStore';
import { VaultItemCard } from './VaultItemCard';
import { VaultUploadForm } from './VaultUploadForm';

const Vault = () => {
  const { items, isUploading, fetch, upload, remove } = useVaultStore();
  const [isAdding, setIsAdding] = useState(false);

  useEffect(() => { fetch(); }, [fetch]);

  return (
    <div className="page-content animate-fade-in">
      <div className="topbar" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '40px' }}>
        <div>
          <h1 className="page-title">Digital Vault</h1>
          <p className="page-sub">Military-grade AES-256 encryption for your vital assets.</p>
        </div>
        <div className="topbar-right" style={{ display: 'flex', gap: '12px' }}>
          <div style={{ position: 'relative' }}>
            <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-dim)' }} />
            <input className="btn btn-ghost" style={{ paddingLeft: '36px', width: '240px', background: 'var(--bg-panel)', textAlign: 'left' }} placeholder="Search vault..." />
          </div>
          <button className="btn btn-primary" onClick={() => setIsAdding(!isAdding)}>
            {isAdding ? <X size={16} /> : <FileUp size={16} />}
            {isAdding ? 'Cancel' : 'Upload Asset'}
          </button>
        </div>
      </div>

      {!isAdding ? (
        <div
          className="card"
          onClick={() => setIsAdding(true)}
          style={{
            border: '1px dashed var(--border-gold)', textAlign: 'center',
            padding: '60px 40px', cursor: 'pointer', marginBottom: '40px',
            background: 'var(--primary-dim)'
          }}
        >
          <div style={{
            width: '64px', height: '64px', background: 'rgba(212,168,83,0.1)',
            borderRadius: '20px', border: '1px solid var(--border-gold)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 20px', fontSize: '32px'
          }}>🛡️</div>
          <h3 style={{ fontSize: '20px', marginBottom: '8px' }}>Secure Deposit Box</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '14px', maxWidth: '400px', margin: '0 auto' }}>
            Click or drag files here to encrypt them. Assets are strictly private until release protocol is triggered.
          </p>
        </div>
      ) : (
        <VaultUploadForm 
          isUploading={isUploading} 
          onUpload={upload} 
          onCancel={() => setIsAdding(false)} 
        />
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '20px' }}>
        {items.map((item) => (
          <VaultItemCard 
            key={item.id} 
            item={item} 
            onRemove={remove} 
          />
        ))}
      </div>
    </div>
  );
};

export default Vault;
