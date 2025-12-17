import { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import './Sidebar.css';

interface SidebarProps {
  onToggle?: (collapsed: boolean) => void;
}

export default function Sidebar({ onToggle }: SidebarProps) {
  const [collapsed, setCollapsed] = useState(false);
  const { isAdmin } = useAuth();

  const toggleSidebar = () => {
    const newState = !collapsed;
    setCollapsed(newState);
    onToggle?.(newState);
  };

  const menuItems = [
    { icon: '🏠', label: 'Dashboard', href: '/dashboard', adminOnly: false },
    { icon: '🤖', label: 'Agents', href: '/agents', adminOnly: false },
    { icon: '👥', label: 'Teams', href: '/teams', adminOnly: false },
    { icon: '📋', label: 'Tasks', href: '/tasks', adminOnly: false },
    { icon: '🏪', label: 'Marketplace', href: '/admin/marketplace', adminOnly: true },
    { icon: '✉️', label: 'Invites', href: '/admin/invites', adminOnly: true },
    { icon: '⚙️', label: 'Settings', href: '/settings', adminOnly: false },
  ];

  const filteredItems = menuItems.filter(item => !item.adminOnly || isAdmin);

  return (
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      <button className="sidebar-toggle" onClick={toggleSidebar} title={collapsed ? 'Expand' : 'Collapse'}>
        {collapsed ? '→' : '←'}
      </button>

      <nav className="sidebar-nav">
        {filteredItems.map((item) => (
          <a 
            key={item.href} 
            href={item.href} 
            className="sidebar-item"
            title={collapsed ? item.label : undefined}
          >
            <span className="sidebar-icon">{item.icon}</span>
            {!collapsed && <span className="sidebar-label">{item.label}</span>}
          </a>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-item" title={collapsed ? 'TeamAI v1.0' : undefined}>
          <span className="sidebar-icon">🚀</span>
          {!collapsed && <span className="sidebar-label version">v1.0 MVP</span>}
        </div>
      </div>
    </aside>
  );
}
