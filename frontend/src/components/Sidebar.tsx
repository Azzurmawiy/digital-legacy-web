import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Lock, Users, Clock, History, Heart, Hexagon, X } from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const Sidebar = ({ isOpen, onClose }: SidebarProps) => {
  return (
    <>
      {/* Mobile overlay backdrop */}
      {isOpen && (
        <div
          className="sidebar-backdrop"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      <aside className={`sidebar ${isOpen ? 'sidebar-open' : ''}`}>
        <div className="logo-area" style={{ padding: '32px 24px', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div className="logo" style={{ display: 'flex', alignItems: 'center', gap: '12px', overflow: 'hidden' }}>
            <div style={{
              width: '36px', height: '36px', background: 'var(--primary-dim)',
              border: '1px solid var(--border-gold)', borderRadius: '10px',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              flexShrink: 0
            }}>
              <Hexagon size={20} color="var(--primary)" />
            </div>
            <div className="sidebar-logo-text" style={{ overflow: 'hidden' }}>
              <div style={{ fontFamily: 'var(--font-heading)', fontSize: '16px', fontWeight: 800, color: 'var(--primary)', letterSpacing: '-0.02em', whiteSpace: 'nowrap' }}>Digital Legacy</div>
              <div style={{ fontSize: '10px', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em', whiteSpace: 'nowrap' }}>Group 16 · ABU Zaria</div>
            </div>
          </div>
          <button className="sidebar-close-btn" onClick={onClose} aria-label="Close navigation">
            <X size={18} />
          </button>
        </div>

        <nav className="nav-links" style={{ padding: '24px 0', display: 'flex', flexDirection: 'column', gap: '4px', flex: 1, overflowY: 'auto' }}>
          <div className="nav-section-label">Management</div>
          <NavLink to="/dashboard" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`} onClick={onClose}>
            <LayoutDashboard size={18} /> <span className="nav-link-text">Dashboard</span>
          </NavLink>
          <NavLink to="/settings" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`} onClick={onClose}>
            <Clock size={18} /> <span className="nav-link-text">Dead Man Switch</span>
          </NavLink>

          <div className="nav-section-label" style={{ paddingTop: '24px' }}>Assets &amp; Heirs</div>
          <NavLink to="/vault" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`} onClick={onClose}>
            <Lock size={18} /> <span className="nav-link-text">Encrypted Vault</span>
          </NavLink>
          <NavLink to="/memories" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`} onClick={onClose}>
            <Heart size={18} /> <span className="nav-link-text">Legacy Messages</span>
          </NavLink>
          <NavLink to="/beneficiaries" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`} onClick={onClose}>
            <Users size={18} /> <span className="nav-link-text">Heir Management</span>
          </NavLink>

          <div className="nav-section-label" style={{ paddingTop: '24px' }}>System</div>
          <NavLink to="/audit" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`} onClick={onClose}>
            <History size={18} /> <span className="nav-link-text">Security Logs</span>
          </NavLink>
        </nav>

        <div className="sidebar-footer" style={{ padding: '24px', background: 'rgba(0,0,0,0.2)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              width: '36px', height: '36px', borderRadius: '50%',
              background: 'linear-gradient(135deg, var(--primary), var(--primary-light))',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: '13px', fontWeight: 800, color: '#1a1408',
              boxShadow: '0 4px 10px rgba(212,168,83,0.3)',
              flexShrink: 0
            }}>UA</div>
            <div className="sidebar-logo-text">
              <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-main)', whiteSpace: 'nowrap' }}>Usman A.</div>
              <div style={{ fontSize: '11px', color: 'var(--text-dim)', whiteSpace: 'nowrap' }}>Administrator</div>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
