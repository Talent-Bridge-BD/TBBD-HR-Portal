import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import DashboardCard from '../components/DashboardCard'
import QuickAction from '../components/QuickAction'

import { candidateDashboard } from '../data/candidateDashboard'

export default function CandidateDashboard({ onNavigate }) {
  const {
    candidate,
    stats,
    applicationOverview,
    recentApplications,
  } = candidateDashboard

  return (
    <>
      <PageHeader
        title={`Welcome, ${candidate.name}`}
        subtitle="Candidate Portal"
      />

      <div className="stats-grid">
        <StatCard
          icon="▤"
          label="Applications"
          value={stats.applications}
          detail="Total submitted"
        />
        <StatCard
          icon="◌"
          label="Active applications"
          value={stats.activeApplications}
          detail="Currently in progress"
        />
        <StatCard
          icon="◷"
          label="Upcoming interviews"
          value={stats.upcomingInterviews}
          detail="Scheduled interviews"
        />
        <StatCard
          icon="□"
          label="Documents"
          value={stats.documents}
          detail="Available documents"
        />
      </div>

      <section className="dashboard-grid">
        <DashboardCard title="Application Overview">
          <div className="overview-grid">
            <div className="overview-item">
              <span className="overview-icon">▤</span>
              <div>
                <strong>Submitted</strong>
                <span>{applicationOverview.submitted} applications</span>
              </div>
            </div>

            <div className="overview-item">
              <span className="overview-icon">◌</span>
              <div>
                <strong>Under Review</strong>
                <span>{applicationOverview.underReview} applications</span>
              </div>
            </div>

            <div className="overview-item">
              <span className="overview-icon">◷</span>
              <div>
                <strong>Interviews</strong>
                <span>{applicationOverview.interviews} scheduled</span>
              </div>
            </div>

            <div className="overview-item">
              <span className="overview-icon">✓</span>
              <div>
                <strong>Shortlisted</strong>
                <span>{applicationOverview.shortlisted} applications</span>
              </div>
            </div>
          </div>
        </DashboardCard>

        <DashboardCard title="Recent Applications">
          {recentApplications.length === 0 ? (
            <div className="empty-state">
              <strong>No applications yet</strong>
              <span>
                Your submitted job applications will appear here.
              </span>
            </div>
          ) : (
            <div className="notification-list">
              {recentApplications.map((application) => (
                <button
                  className="notification-item"
                  type="button"
                  key={application.id}
                >
                  <span className="notification-dot" />
                  <span className="notification-content">
                    <strong>{application.title}</strong>
                    <small>{application.status}</small>
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
            icon="▤"
            label="Browse Available Jobs"
            onClick={() => onNavigate('Candidate Available Jobs')}
          />
          <QuickAction
            icon="▤"
            label="My Applications"
            onClick={() => onNavigate('Candidate My Applications')}
          />
          <QuickAction
            icon="◷"
            label="Upcoming Interviews"
            onClick={() => onNavigate('Candidate Interviews')}
          />
          <QuickAction
            icon="□"
            label="My Documents"
            onClick={() => onNavigate('Candidate Documents')}
          />
        </div>
      </section>
    </>
  )
}
