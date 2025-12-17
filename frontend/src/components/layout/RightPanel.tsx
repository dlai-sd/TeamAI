import './RightPanel.css';

interface RightPanelProps {
  currentPage?: string;
}

export default function RightPanel({ currentPage = 'dashboard' }: RightPanelProps) {
  // Mock subscription data
  const subscription = {
    plan: 'Professional',
    agentsUsed: 1,
    agentsLimit: 5,
    tasksThisMonth: 47,
    tasksLimit: 500,
    renewalDate: 'Jan 15, 2026',
  };

  // Release notes
  const newFeatures = [
    { version: 'v1.0', date: 'Dec 17', items: ['SEO Site Audit Agent', 'Google OAuth Login', 'Team Management'] },
  ];

  const upcomingFeatures = [
    { feature: 'Social Media Scheduler', eta: 'Jan 2026' },
    { feature: 'Lead Qualifier Agent', eta: 'Jan 2026' },
    { feature: 'Custom Recipe Builder', eta: 'Feb 2026' },
    { feature: 'A/B Testing Dashboard', eta: 'Mar 2026' },
  ];

  // Context-sensitive help
  const helpTopics: Record<string, { title: string; items: string[] }> = {
    dashboard: {
      title: 'Dashboard Help',
      items: [
        'View your active agents and teams',
        'Run agent tasks from Quick Actions',
        'Monitor task completion status',
      ],
    },
    agents: {
      title: 'Agents Help',
      items: [
        'Agents are AI workers you deploy',
        'Each agent has specific skills (recipes)',
        'Allocate agents to teams for access control',
      ],
    },
    tasks: {
      title: 'Tasks Help',
      items: [
        'Tasks are agent work items',
        'View task status and results',
        'Download reports when complete',
      ],
    },
  };

  const currentHelp = helpTopics[currentPage] || helpTopics.dashboard;

  return (
    <aside className="right-panel">
      {/* Subscription Section */}
      <section className="panel-section">
        <h3 className="panel-title">📊 Subscription</h3>
        <div className="subscription-info">
          <div className="plan-badge">{subscription.plan}</div>
          
          <div className="usage-item">
            <span className="usage-label">Agents</span>
            <div className="usage-bar">
              <div 
                className="usage-fill" 
                style={{ width: `${(subscription.agentsUsed / subscription.agentsLimit) * 100}%` }}
              />
            </div>
            <span className="usage-text">{subscription.agentsUsed}/{subscription.agentsLimit}</span>
          </div>
          
          <div className="usage-item">
            <span className="usage-label">Tasks</span>
            <div className="usage-bar">
              <div 
                className="usage-fill" 
                style={{ width: `${(subscription.tasksThisMonth / subscription.tasksLimit) * 100}%` }}
              />
            </div>
            <span className="usage-text">{subscription.tasksThisMonth}/{subscription.tasksLimit}</span>
          </div>
          
          <div className="renewal-info">
            Renews: {subscription.renewalDate}
          </div>
        </div>
      </section>

      {/* What's New Section */}
      <section className="panel-section">
        <h3 className="panel-title">✨ What's New</h3>
        {newFeatures.map((release) => (
          <div key={release.version} className="release-item">
            <div className="release-header">
              <span className="release-version">{release.version}</span>
              <span className="release-date">{release.date}</span>
            </div>
            <ul className="release-list">
              {release.items.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          </div>
        ))}
      </section>

      {/* Upcoming Features Section */}
      <section className="panel-section">
        <h3 className="panel-title">🚀 Coming Soon</h3>
        <div className="upcoming-list">
          {upcomingFeatures.map((item, idx) => (
            <div key={idx} className="upcoming-item">
              <span className="upcoming-feature">{item.feature}</span>
              <span className="upcoming-eta">{item.eta}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Help Section */}
      <section className="panel-section help-section">
        <h3 className="panel-title">❓ {currentHelp.title}</h3>
        <ul className="help-list">
          {currentHelp.items.map((item, idx) => (
            <li key={idx}>{item}</li>
          ))}
        </ul>
        <a href="/docs" className="help-link">View Documentation →</a>
      </section>
    </aside>
  );
}
