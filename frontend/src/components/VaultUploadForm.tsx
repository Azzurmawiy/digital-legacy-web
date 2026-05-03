import { useState } from 'react';
import type { FormEvent } from 'react';

interface VaultUploadFormProps {
  isUploading: boolean;
  onUpload: (fd: FormData) => Promise<void>;
  onCancel: () => void;
}

export const VaultUploadForm = ({ isUploading, onUpload, onCancel }: VaultUploadFormProps) => {
  const [file, setFile] = useState<File | null>(null);
  const [form, setForm] = useState({ title: '', description: '', item_type: 'document' });

  const handleUpload = async (e: FormEvent) => {
    e.preventDefault();
    const fd = new FormData();
    if (file) fd.append('file', file);
    fd.append('title', form.title || file?.name || 'Untitled');
    fd.append('description', form.description);
    fd.append('item_type', form.item_type);

    try {
      await onUpload(fd);
      onCancel();
    } catch {
      // Error is handled by store toast
    }
  };

  return (
    <div className="card animate-fade-in" style={{ marginBottom: '40px', background: 'var(--bg-panel-light)' }}>
      <form onSubmit={handleUpload}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '11px', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '8px' }}>Asset Title</label>
            <input className="btn btn-ghost" style={{ width: '100%', background: 'var(--bg-main)', textAlign: 'left' }} placeholder="e.g. Property Deed" value={form.title} onChange={e => setForm({ ...form, title: e.target.value })} />
          </div>
          <div>
            <label style={{ display: 'block', fontSize: '11px', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '8px' }}>Asset Category</label>
            <select className="btn btn-ghost" style={{ width: '100%', background: 'var(--bg-main)', color: 'var(--text-main)' }} value={form.item_type} onChange={e => setForm({ ...form, item_type: e.target.value })}>
              <option value="document">Legal Document</option>
              <option value="photo">Photograph</option>
              <option value="video">Video Recording</option>
              <option value="other">Other Asset</option>
            </select>
          </div>
        </div>
        <div style={{ padding: '32px', border: '1px dashed var(--border)', borderRadius: '12px', textAlign: 'center', marginBottom: '20px' }}>
          <input type="file" onChange={e => setFile(e.target.files?.[0] || null)} />
        </div>
        <button type="submit" className="btn btn-primary" style={{ width: '100%', justifyContent: 'center', padding: '14px' }} disabled={isUploading}>
          {isUploading ? 'Encrypting & Storing...' : 'Finalize Encrypted Storage'}
        </button>
      </form>
    </div>
  );
};
