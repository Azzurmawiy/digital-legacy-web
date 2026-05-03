import { Trash2, Edit3 } from 'lucide-react';

const formatBytes = (bytes: number) => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

import type { VaultItem } from '../store/useVaultStore';

interface VaultItemCardProps {
  item: VaultItem;
  onRemove: (id: string) => void;
}

export const VaultItemCard = ({ item, onRemove }: VaultItemCardProps) => {
  return (
    <div className="card" style={{ padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
        <div style={{
          width: '48px', height: '48px', borderRadius: '14px',
          background: item.item_type === 'photo' ? 'var(--primary-dim)' : 'var(--accent-dim)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '24px', border: '1px solid var(--border)'
        }}>
          {item.item_type === 'photo' ? '🖼️' : '📄'}
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '10px', color: 'var(--success)', fontWeight: 700, background: 'var(--success-dim)', padding: '2px 8px', borderRadius: '20px' }}>SECURED</div>
          <div style={{ fontSize: '10px', color: 'var(--text-dim)', marginTop: '4px' }}>AES-256-GCM</div>
        </div>
      </div>
      <h4 style={{ fontSize: '15px', fontWeight: 700, marginBottom: '4px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{item.title}</h4>
      <div style={{ fontSize: '12px', color: 'var(--text-muted)', display: 'flex', justifyContent: 'space-between' }}>
        <span>{formatBytes(item.file_size || 0)}</span>
        <span>{new Date(item.uploaded_at).toLocaleDateString()}</span>
      </div>
      <div style={{ marginTop: '20px', paddingTop: '16px', borderTop: '1px solid var(--border)', display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
        <button onClick={() => onRemove(item.id)} style={{ color: 'var(--error)', background: 'none', border: 'none', cursor: 'pointer', opacity: 0.7 }} title="Purge Asset"><Trash2 size={16} /></button>
        <button style={{ color: 'var(--text-dim)', background: 'none', border: 'none', cursor: 'pointer' }}><Edit3 size={16} /></button>
      </div>
    </div>
  );
};
