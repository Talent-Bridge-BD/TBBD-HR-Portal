import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import DashboardCard from '../components/DashboardCard'
import QuickAction from '../components/QuickAction'
import { candidateDashboard } from '../data/candidateDashboard'
import candidatePortalBanner from '../assets/Candidate-portal-banner.jpeg'

const Icon = ({ name, size = 22 }) => {
  const common = {
    width: size,
    height: size,
    viewBox: '0 0 24 24',
    fill: 'none',
    stroke: 'currentColor',
    strokeWidth: 1.8,
    strokeLinecap: 'round',
    strokeLinejoin: 'round',
    'aria-hidden': true,
  }

  const paths = {
    applications: (
      <>
        <rect x="5" y="3" width="14" height="18" rx="2" />
        <path d="M9 3.5h6" />
        <path d="M8 8h8M8 12h8M8 16h5" />
      </>
    ),
    active: (
      <>
        <path d="M20 11a8 8 0 1 1-2.34-5.66" />
        <path d="M20 4v5h-5" />
        <path d="M12 7v5l3 2" />
      </>
    ),
    interviews: (
      <>
        <rect x="3.5" y="5" width="17" height="15" rx="2" />
        <path d="M7 3v4M17 3v4M3.5 9h17" />
        <path d="M8 13h2M14 13h2M8 17h2" />
      </>
    ),
    documents: (
      <>
        <path d="M6 3.5h8l4 4V20.5H6z" />
        <path d="M14 3.5v5h4M9 13h6M9 16.5h6" />
      </>
    ),
    review: (
      <>
        <circle cx="11" cy="11" r="6.5" />
        <path d="m16 16 4 4M8.5 11h5M11 8.5v5" />
      </>
    ),
    shortlisted: (
      <>
        <path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2L12 17.3 6.4 20.2l1.1-6.2L3 9.6l6.2-.9z" />
      </>
    ),
    jobs: (
      <>
        <rect x="3" y="6" width="18" height="14" rx="2" />
        <path d="M8 6V4.5h8V6M3 11h18M10 11v2h4v-2" />
      </>
    ),
    arrow: (
      <>
        <path d="M5 12h14M13 6l6 6-6 6" />
      </>
    ),
  }

  return <svg {...common}>{paths[name]}</svg>
}

export default function CandidateDashboard({ onNavigate }) {
  const {
    candidate,
    stats,
    applicationOverview,
    recentApplications,
  } = candidateDashboard

  const overviewItems = [
    {
      key: 'submitted',
      label: 'Submitted',
      value: applicationOverview.submitted,
      detail: 'applications',
      icon: 'applications',
    },
    {
      key: 'under-review',
      label: 'Under Review',
      value: applicationOverview.underReview,
      detail: 'applications',
      icon: 'review',
    },
    {
      key: 'interviews',
      label: 'Interviews',
      value: applicationOverview.interviews,
      detail: 'scheduled',
      icon: 'interviews',
    },
    {
      key: 'shortlisted',
      label: 'Shortlisted',
      value: applicationOverview.shortlisted,
      detail: 'applications',
      icon: 'shortlisted',
    },
  ]

  return (
    <div className="candidate-portal-page">
      <PageHeader
        title={`Welcome, ${candidate.name}`}
        subtitle="Candidate Portal"
      />

      <section className="candidate-hero-banner">
        <img
          src={candidatePortalBanner}
          alt="Welcome to Talent Bridge BD's Candidate Portal"
        />
      </section>

      <section className="candidate-stats-grid">
        <StatCard
          icon={<Icon name="applications" />}
          label="Applications"
          value={stats.applications}
          detail="Total submitted"
        />
        <StatCard
          icon={<Icon name="active" />}
          label="Active applications"
          value={stats.activeApplications}
          detail="Currently in progress"
        />
        <StatCard
          icon={<Icon name="interviews" />}
          label="Upcoming interviews"
          value={stats.upcomingInterviews}
          detail="Scheduled interviews"
        />
        <StatCard
          icon={<Icon name="documents" />}
          label="Documents"
          value={stats.documents}
          detail="Available documents"
        />
      </section>

      <section className="candidate-dashboard-grid">
        <DashboardCard title="Application Overview">
          <div className="candidate-overview-grid">
            {overviewItems.map((item) => (
              <div
                className={`candidate-overview-card candidate-overview-card-${item.key}`}
                key={item.key}
              >
                <span className="candidate-overview-icon">
                  <Icon name={item.icon} size={21} />
                </span>
                <div className="candidate-overview-value">
                  {item.value}
                </div>
                <strong>{item.label}</strong>
                <span>{item.detail}</span>
              </div>
            ))}
          </div>
        </DashboardCard>

        <DashboardCard title="Recent Applications">
          {recentApplications.length === 0 ? (
            <div className="candidate-empty-state">
              <span className="candidate-empty-icon">
                <Icon name="applications" size={24} />
              </span>
              <strong>No applications yet</strong>
              <span>
                Your submitted job applications will appear here.
              </span>
            </div>
          ) : (
            <div className="candidate-application-list">
              {recentApplications.map((application) => (
                <button
                  className="candidate-application-item"
                  type="button"
                  key={application.id}
                >
                  <span className="candidate-application-icon">
                    <Icon name="applications" size={19} />
                  </span>

                  <span className="candidate-application-content">
                    <strong>{application.title}</strong>
                    <small>Recent application</small>
                  </span>

                  <span className="candidate-application-status">
                    {application.status}
                  </span>

                  <span className="candidate-application-arrow">
                    <Icon name="arrow" size={18} />
                  </span>
                </button>
              ))}
            </div>
          )}
        </DashboardCard>
      </section>

      <section className="dashboard-card candidate-quick-actions-card">
        <div className="card-heading">
          <div>
            <h2>Quick Actions</h2>
            <p className="candidate-card-description">
              Continue your job search and manage your candidate profile.
            </p>
          </div>
        </div>

        <div className="candidate-quick-actions">
          <QuickAction
            icon={<Icon name="jobs" />}
            label="Browse Available Jobs"
            onClick={() => onNavigate('Candidate Available Jobs')}
          />
          <QuickAction
            icon={<Icon name="applications" />}
            label="My Applications"
            onClick={() => onNavigate('Candidate My Applications')}
          />
          <QuickAction
            icon={<Icon name="interviews" />}
            label="Upcoming Interviews"
            onClick={() => onNavigate('Candidate Interviews')}
          />
          <QuickAction
            icon={<Icon name="documents" />}
            label="My Documents"
            onClick={() => onNavigate('Candidate Documents')}
          />
        </div>
      </section>
    </div>
  )
}
