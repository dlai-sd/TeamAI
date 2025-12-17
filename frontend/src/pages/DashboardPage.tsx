import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import Header from '../components/layout/Header';
import Sidebar from '../components/layout/Sidebar';
import RightPanel from '../components/layout/RightPanel';
import './DashboardPage.css';

// API URL injected at build time
declare const __API_BASE_URL__: string;
const API_BASE_URL = __API_BASE_URL__;

interface Agent {
  id: string;
  name: string;
  role: string;
  status: 'active' | 'idle' | 'error';
  team: string;
}

interface Team {
  id: string;
  name: string;
  agents: Agent[];
}

export default function DashboardPage() {
  const { user, isAdmin } = useAuth();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [runningAudit, setRunningAudit] = useState(false);
  const [auditResult, setAuditResult] = useState<any>(null);
  const [auditError, setAuditError] = useState<string | null>(null);

  // Mock data for agents and teams hierarchy
  const teams: Team[] = [
    {
      id: '1',
      name: 'SEO Department',
      agents: [
        { id: 'a1', name: 'Rover', role: 'SEO Specialist', status: 'active', team: 'SEO Department' },
      ],
    },
    {
      id: '2',
      name: 'Content Team',
      agents: [
        { id: 'a2', name: 'WriterBot', role: 'Content Writer', status: 'idle', team: 'Content Team' },
      ],
    },
  ];

  const runSEOAudit = async () => {
    setRunningAudit(true);
    setAuditResult(null);
    setAuditError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/v1/agents/test-live`);
      const data = await response.json();
      
      if (data.success) {
        setAuditResult(data);
      } else {
        setAuditError(data.message || 'Audit failed');
      }
    } catch (error) {
      setAuditError('Failed to connect to agent service');
    } finally {
      setRunningAudit(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return '#10b981';
      case 'idle': return '#f59e0b';
      case 'error': return '#ef4444';
      default: return '#6b7280';
    }
  };

  return (
    <>
      <Header />
      <Sidebar onToggle={setSidebarCollapsed} />
      <RightPanel currentPage="dashboard" />
      
      <main className={`dashboard-main ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
        <div className="welcome-section">
          <h1>Welcome back, {user?.full_name}! 👋</h1>
          <p className="subtitle">Here's your AI workforce overview</p>
        </div>

        {/* Quick Stats */}
        <div className="stats-row">
          <div className="mini-stat">
            <span className="mini-stat-value">{teams.reduce((acc, t) => acc + t.agents.length, 0)}</span>
            <span className="mini-stat-label">Agents</span>
          </div>
          <div className="mini-stat">
            <span className="mini-stat-value">{teams.length}</span>
            <span className="mini-stat-label">Teams</span>
          </div>
          <div className="mini-stat">
            <span className="mini-stat-value">47</span>
            <span className="mini-stat-label">Tasks Done</span>
          </div>
        </div>

        {/* Run SEO Audit Card */}
        <div className="action-section">
          <div className="run-audit-card">
            <div className="audit-header">
              <span className="audit-icon">🔍</span>
              <div>
                <h3>Run SEO Site Audit</h3>
                <p>Analyze any website for SEO issues using AI</p>
              </div>
            </div>
            <button 
              className={`audit-button ${runningAudit ? 'running' : ''}`}
              onClick={runSEOAudit}
              disabled={runningAudit}
            >
              {runningAudit ? '⏳ Running...' : '▶️ Run Audit'}
            </button>
          </div>

          {/* Audit Result */}
          {auditResult && (
            <div className="audit-result success">
              <h4>✅ Audit Complete</h4>
              <div className="result-metrics">
                <span>⏱️ {auditResult.metrics.execution_time_ms}ms</span>
                <span>🎯 {auditResult.metrics.tokens_used} tokens</span>
                <span>💰 ${auditResult.metrics.total_cost.toFixed(6)}</span>
                <span>📊 {auditResult.metrics.nodes_executed} nodes</span>
              </div>
              {auditResult.output_preview?.content && (
                <pre className="result-preview">{auditResult.output_preview.content}</pre>
              )}
            </div>
          )}

          {auditError && (
            <div className="audit-result error">
              <h4>❌ Audit Failed</h4>
              <p>{auditError}</p>
            </div>
          )}
        </div>

        {/* Teams & Agents Hierarchy */}
        <div className="hierarchy-section">
          <h2>🏢 Teams & Agents</h2>
          <div className="hierarchy-tree">
            {teams.map((team) => (
              <div key={team.id} className="team-node">
                <div className="team-header">
                  <span className="team-icon">👥</span>
                  <span className="team-name">{team.name}</span>
                  <span className="agent-count">{team.agents.length} agent(s)</span>
                </div>
                <div className="agents-list">
                  {team.agents.map((agent) => (
                    <div key={agent.id} className="agent-node">
                      <span className="agent-avatar">🤖</span>
                      <div className="agent-info">
                        <span className="agent-name">{agent.name}</span>
                        <span className="agent-role">{agent.role}</span>
                      </div>
                      <span 
                        className="status-dot" 
                        style={{ backgroundColor: getStatusColor(agent.status) }}
                        title={agent.status}
                      />
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions for Admin */}
        {isAdmin && (
          <div className="admin-actions">
            <h2>⚡ Admin Actions</h2>
            <div className="action-buttons">
              <a href="/admin/marketplace" className="action-btn">🏪 Marketplace</a>
              <a href="/admin/invites" className="action-btn">✉️ Invite Users</a>
              <a href="/agents" className="action-btn">🤖 Manage Agents</a>
            </div>
          </div>
        )}
      </main>
    </>
  );
}
