import { useAuth } from '../contexts/AuthContext';
import Header from '../components/layout/Header';
import './DashboardPage.css';

export default function DashboardPage() {
  const { user, isAdmin } = useAuth();

  return (
    <>
      <Header />
      <div className="dashboard-page">
        <div className="welcome-section">
          <h1>Welcome back, {user?.full_name}! 👋</h1>
          <p className="subtitle">Here's what's happening with your AI agents</p>
        </div>

        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">🤖</div>
            <div className="stat-content">
              <div className="stat-value">0</div>
              <div className="stat-label">Active Agents</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">📊</div>
            <div className="stat-content">
              <div className="stat-value">0</div>
              <div className="stat-label">Tasks Completed</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">⚡</div>
            <div className="stat-content">
              <div className="stat-value">0</div>
              <div className="stat-label">Active Tasks</div>
            </div>
          </div>

          {isAdmin && (
            <div className="stat-card">
              <div className="stat-icon">👥</div>
              <div className="stat-content">
                <div className="stat-value">3</div>
                <div className="stat-label">Team Members</div>
              </div>
            </div>
          )}
        </div>

        <div className="quick-actions">
          <h2>Quick Actions</h2>
          <div className="actions-grid">
            {isAdmin && (
              <>
                <a href="/admin/marketplace" className="action-card">
                  <div className="action-icon">🏪</div>
                  <div className="action-title">Browse Marketplace</div>
                  <div className="action-desc">Discover and deploy new AI agents</div>
                </a>
                <a href="/admin/invites" className="action-card">
                  <div className="action-icon">✉️</div>
                  <div className="action-title">Invite Team Members</div>
                  <div className="action-desc">Add new users to your agency</div>
                </a>
              </>
            )}
            <a href="/agents" className="action-card">
              <div className="action-icon">⚙️</div>
              <div className="action-title">Manage Agents</div>
              <div className="action-desc">Configure and monitor your AI workforce</div>
            </a>
            <a href="/tasks" className="action-card">
              <div className="action-icon">📋</div>
              <div className="action-title">View Tasks</div>
              <div className="action-desc">Track ongoing and completed work</div>
            </a>
          </div>
        </div>

        <div className="recent-activity">
          <h2>Recent Activity</h2>
          <div className="activity-list">
            <div className="empty-state">
              <p>No recent activity. Deploy an agent to get started!</p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
