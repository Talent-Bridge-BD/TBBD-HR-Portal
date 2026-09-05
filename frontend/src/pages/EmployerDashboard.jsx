import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import DashboardCard from '../components/DashboardCard'
import QuickAction from '../components/QuickAction'
import { employerDashboard } from '../data/employerDashboard'

export default function EmployerDashboard({ onNavigate }) {
  const {
    employer,
    stats,
    hiringOverview,
    recentRequests,
  } = employerDashboard

  return (
    <>
      <PageHeader
        title={`Welcome, ${employer.name}`}
        subtitle={`${employer.organization} · Employer Portal`}
      />

      <div className="stats-grid">
        <StatCard
          icon="▤"
          label="Open jobs"
          value={stats.openJobs}
          detail="Currently open"
        />
        <StatCard
          icon="♙"
          label="Active candidates"
          value={stats.activeCandidates}
          detail="In hiring pipeline"
        />
        <StatCard
          icon="＋"
          label="Pending requests"
          value={stats.pendingRequests}
          detail="Awaiting action"
        />
      </div>

      <section className="dashboard-grid">
        <DashboardCard title="Hiring Overview">
          <div className="overview-grid">
            <div className="overview-item">
              <span className="overview-icon">＋</span>
              <div>
                <strong>Job Requests</strong>
                <span>{hiringOverview.jobRequests} active requests</span>
              </div>
            </div>

            <div className="overview-item">
              <span className="overview-icon">▤</span>
              <div>
                <strong>Open Positions</strong>
                <span>{hiringOverview.openPositions} open positions</span>
              </div>
            </div>

            <div className="overview-item">
              <span className="overview-icon">♙</span>
              <div>
                <strong>Applications</strong>
                <span>{hiringOverview.applications} applications</span>
              </div>
            </div>

            <div className="overview-item">
              <span className="overview-icon">◷</span>
              <div>
                <strong>Interviews</strong>
                <span>{hiringOverview.interviews} scheduled</span>
              </div>
            </div>
          </div>
        </DashboardCard>

        <DashboardCard title="Recent Job Requests">
          {recentRequests.length === 0 ? (
            <div className="empty-state">
              <strong>No job requests yet</strong>
              <span>
                Authorized employer requests will appear here.
              </span>
            </div>
          ) : (
            <div className="notification-list">
              {recentRequests.map((request) => (
                <button
                  className="notification-item"
                  type="button"
                  key={request.id}
                >
                  <span className="notification-dot" />
                  <span className="notification-content">
                    <strong>{request.title}</strong>
                    <small>{request.status}</small>
                  </span>
                  <span className="notification-arrow">→</span>
                </button>
              ))}
            </div>
          )}
        </DashboardCard>
      </section>

      <section className="dashboard-card">
        <div className="card-heading">
          <h2>Quick Actions</h2>
        </div>

        <div className="quick-actions">
          <QuickAction
            icon="+"
            label="Create Job Request"
            onClick={() => onNavigate('Employer Job Requests')}
          />

          <QuickAction
            icon="▤"
            label="View Job Openings"
            onClick={() => onNavigate('Employer Job Openings')}
          />

          <QuickAction
            icon="♙"
            label="Review Applications"
            onClick={() => onNavigate('Employer Applications')}
          />

          <QuickAction
            icon="✓"
            label="Hiring Activity"
            onClick={() => onNavigate('Employer Hiring')}
          />
        </div>
      </section>
    </>
  )
}
