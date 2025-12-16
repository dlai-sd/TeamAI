import { useAuth } from '../../contexts/AuthContext';
import './Header.css';

export default function Header() {
  const { user, logout, isAdmin } = useAuth();

  return (
    <header className="app-header">
      <div className="header-content">
        <div className="header-left">
          <h1 className="logo">🤖 TeamAI</h1>
          <nav className="main-nav">
            <a href="/dashboard">Dashboard</a>
            {isAdmin && <a href="/admin/marketplace">Marketplace</a>}
            {isAdmin && <a href="/admin/invites">Invites</a>}
          </nav>
        </div>

        <div className="header-right">
          {user && (
            <div className="user-menu">
              <div className="user-info">
                <span className="user-name">{user.full_name}</span>
                <span className="user-role">{user.role.replace('_', ' ')}</span>
              </div>
              <button className="logout-btn" onClick={logout}>
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
