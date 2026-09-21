import { useEffect, useState } from 'react'
import StatCard from '../components/StatCard'
import DashboardCard from '../components/DashboardCard'
import QuickAction from '../components/QuickAction'
import { authenticatedFetch } from '../utils/auth'
import employerPortalBanner from '../assets/Employer-portal-banner.jpeg'


function DashboardIcon({ name, size = 20 }) {
  const paths = {
    briefcase: (
      <>
        <rect x="3" y="7" width="18" height="13" rx="2" />
        <path d="M8 7V5.5A1.5 1.5 0 0 1 9.5 4h5A1.5 1.5 0 0 1 16 5.5V7" />
        <path d="M3 12h18" />
        <path d="M10 12v2h4v-2" />
      </>
    ),
    document: (
      <>
        <path d="M6 3h8l4 4v14H6z" />
        <path d="M14 3v5h5" />
        <path d="M9 13h6" />
        <path d="M9 17h6" />
      </>
    ),
    users: (
      <>
        <circle cx="9" cy="8" r="3" />
        <path d="M3.5 20a5.5 5.5 0 0 1 11 0" />
        <path d="M16 5.5a3 3 0 0 1 0 5.8" />
        <path d="M17 14a4.5 4.5 0 0 1 4 4.5" />
      </>
    ),
    calendar: (
      <>
        <rect x="3" y="5" width="18" height="16" rx="2" />
        <path d="M16 3v4M8 3v4M3 10h18" />
        <path d="M8 14h.01M12 14h.01M16 14h.01M8 18h.01M12 18h.01" />
      </>
    ),
    inbox: (
      <>
        <path d="M4 5h16l2 10v4a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-4z" />
        <path d="M2 15h5l2 3h6l2-3h5" />
      </>
    ),
    search: (
      <>
        <circle cx="10.5" cy="10.5" r="6.5" />
        <path d="m16 16 5 5" />
      </>
    ),
    interview: (
      <>
        <rect x="3" y="5" width="18" height="14" rx="2" />
        <path d="M8 9h8M8 13h5" />
        <path d="M16 19v2" />
      </>
    ),
    tools: (
      <>
        <path d="m14.5 6.5 3-3 3 3-3 3" />
        <path d="m17.5 6.5-7 7" />
        <path d="M7 5a4 4 0 0 0 5 5l-7 7a2.1 2.1 0 1 0 3 3l7-7a4 4 0 0 0 5-5" />
      </>
    ),
    medical: (
      <>
        <path d="M12 21s-7-4.5-7-10a4 4 0 0 1 7-2.5A4 4 0 0 1 19 11c0 5.5-7 10-7 10z" />
        <path d="M12 9v5M9.5 11.5h5" />
      </>
    ),
    passport: (
      <>
        <rect x="4" y="3" width="16" height="18" rx="2" />
        <circle cx="12" cy="10" r="3" />
        <path d="M7 17h10" />
      </>
    ),
    plane: (
      <>
        <path d="m3 12 18-7-5 14-4-6z" />
        <path d="m12 13-3 6" />
        <path d="m12 13 7-5" />
      </>
    ),
    clipboard: (
      <>
        <rect x="5" y="4" width="14" height="17" rx="2" />
        <path d="M9 4.5V3h6v1.5M9 10h6M9 14h6M9 18h4" />
      </>
    ),
    rocket: (
      <>
        <path d="M14 4c3.5-2 6-1 6-1s1 2.5-1 6c-1.2 2.2-3 4.1-5.5 5.5L9.5 10C10.9 7.5 12.8 5.7 14 4z" />
        <path d="m9.5 10-4 1-2.5 2.5 5 1" />
        <path d="m14.5 14-1 4-2.5 2.5-1-5" />
        <circle cx="16.5" cy="7.5" r="1.2" />
      </>
    ),
    check: (
      <>
        <circle cx="12" cy="12" r="9" />
        <path d="m8 12 2.5 2.5L16 9" />
      </>
    ),
    plus: (
      <>
        <circle cx="12" cy="12" r="9" />
        <path d="M12 8v8M8 12h8" />
      </>
    ),
    settings: (
      <>
        <circle cx="12" cy="12" r="3" />
        <path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-1.7 1.7-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.5v.2h-2.4v-.2a1.7 1.7 0 0 0-1-1.5 1.7 1.7 0 0 0-1.9.3l-.1.1L8 17l.1-.1a1.7 1.7 0 0 0 .3-1.9 1.7 1.7 0 0 0-1.5-1H6.7v-2.4h.2a1.7 1.7 0 0 0 1.5-1 1.7 1.7 0 0 0-.3-1.9L8 8.6l1.7-1.7.1.1a1.7 1.7 0 0 0 1.9.3 1.7 1.7 0 0 0 1-1.5v-.2h2.4v.2a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.9-.3l.1-.1 1.7 1.7-.1.1a1.7 1.7 0 0 0-.3 1.9 1.7 1.7 0 0 0 1.5 1h.2v2.4h-.2a1.7 1.7 0 0 0-1.5 1z" />
      </>
    ),
  }

  return (
    <svg
      className="dashboard-icon"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {paths[name] || paths.document}
    </svg>
  )
}

const emptyDashboard = {
  employer_name: 'Employer',
  organization_name: null,
  stats: {
    active_jobs: 0,
    new_applications: 0,
    candidates_pipeline: 0,
    interviews_upcoming: 0,
  },
  pipeline: {
    new: 0,
    screening: 0,
    shortlisted: 0,
    interview: 0,
    offer: 0,
    hired: 0,
  },
}

export default function EmployerDashboard({ onNavigate }) {
  const [dashboard, setDashboard] = useState(emptyDashboard)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false

    async function loadDashboard() {
      try {
        setLoading(true)
        setError('')

        const response = await authenticatedFetch('/api/employer/dashboard')

        if (!response.ok) {
          if (response.status === 401) {
            throw new Error('Authentication required')
          }

          if (response.status === 403) {
            throw new Error('You are not authorized to access the Employer Portal')
          }

          throw new Error('Unable to load employer dashboard')
        }

        const data = await response.json()

        if (!cancelled) {
          setDashboard(data)
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message || 'Unable to load employer dashboard')
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    loadDashboard()

    return () => {
      cancelled = true
    }
  }, [])

  const { stats, pipeline } = dashboard

  const organizationLabel =
    dashboard.organization_name || 'Authorized Organization'

  return (
    <>
      <div className="employer-dashboard-banner">
        <img
          src={employerPortalBanner}
          alt="Talent Bridge BD Employer Portal"
        />
        <div className="employer-dashboard-banner-content">
          <span className="employer-dashboard-banner-brand">TALENT BRIDGE BD</span>
          <h1>EMPLOYER PORTAL</h1>
          <p>Connect with talent. Build your workforce.</p>
          <span className="employer-dashboard-banner-org">{organizationLabel}</span>
        </div>
      </div>

      {error && (
        <div className="empty-state">
          <strong>Unable to load dashboard</strong>
          <span>{error}</span>
        </div>
      )}

      <div className="stats-grid">
        <StatCard
          icon={<DashboardIcon name="briefcase" />}
          label="Active jobs"
          value={loading ? '—' : stats.active_jobs}
          detail="Currently open"
        />

        <StatCard
          icon={<DashboardIcon name="document" />}
          label="New applications"
          value={loading ? '—' : stats.new_applications}
          detail="Awaiting review"
        />

        <StatCard
          icon={<DashboardIcon name="users" />}
          label="Candidates pipeline"
          value={loading ? '—' : stats.candidates_pipeline}
          detail="Active applications"
        />

        <StatCard
          icon={<DashboardIcon name="calendar" />}
          label="Upcoming interviews"
          value={loading ? '—' : stats.interviews_upcoming}
          detail="Scheduled interviews"
        />
      </div>

      <section className="dashboard-grid">
        <DashboardCard title="Recruitment Pipeline">
          <div className="overview-grid">
            <div className="overview-item">
              <span className="overview-icon"><DashboardIcon name="inbox" /></span>
              <div>
                <strong>Applied</strong>
                <span>{loading ? '—' : pipeline.applied} applications</span>
              </div>
            </div>
            <div className="overview-item">
              <span className="overview-icon"><DashboardIcon name="search" /></span>
              <div>
                <strong>Screening</strong>
                <span>{loading ? '—' : pipeline.screening} candidates</span>
              </div>
            </div>
            <div className="overview-item">
              <span className="overview-icon"><DashboardIcon name="interview" /></span>
              <div>
                <strong>Interview</strong>
                <span>{loading ? '—' : pipeline.interview} candidates</span>
              </div>
            </div>
            <div className="overview-item">
              <span className="overview-icon"><DashboardIcon name="tools" /></span>
              <div>
                <strong>Trade Test</strong>
                <span>{loading ? '—' : pipeline.trade_test} candidates</span>
              </div>
            </div>
            <div className="overview-item">
              <span className="overview-icon"><DashboardIcon name="medical" /></span>
              <div>
                <strong>Medical</strong>
                <span>{loading ? '—' : pipeline.medical} candidates</span>
              </div>
            </div>
            <div className="overview-item">
              <span className="overview-icon"><DashboardIcon name="passport" /></span>
              <div>
                <strong>Visa Processing</strong>
                <span>{loading ? '—' : pipeline.visa_processing} candidates</span>
              </div>
            </div>
            <div className="overview-item">
              <span className="overview-icon"><DashboardIcon name="plane" /></span>
              <div>
                <strong>Ticketing</strong>
                <span>{loading ? '—' : pipeline.ticketing} candidates</span>
              </div>
            </div>
            <div className="overview-item">
              <span className="overview-icon"><DashboardIcon name="clipboard" /></span>
              <div>
                <strong>Onboarding</strong>
                <span>{loading ? '—' : pipeline.onboarding} candidates</span>
              </div>
            </div>
            <div className="overview-item">
              <span className="overview-icon"><DashboardIcon name="rocket" /></span>
              <div>
                <strong>Deployment</strong>
                <span>{loading ? '—' : pipeline.deployment} candidates</span>
              </div>
            </div>
            <div className="overview-item">
              <span className="overview-icon"><DashboardIcon name="check" /></span>
              <div>
                <strong>Completed</strong>
                <span>{loading ? '—' : pipeline.completed} candidates</span>
              </div>
            </div>
          </div>
        </DashboardCard>

      </section>

      <section className="dashboard-card">
        <div className="card-heading">
          <h2>Quick Actions</h2>
        </div>

        <div className="quick-actions">
          <QuickAction
            icon={<DashboardIcon name="plus" />}
            label="Create Job"
            onClick={() => onNavigate('Recruitment Jobs')}
          />

          <QuickAction
            icon={<DashboardIcon name="users" />}
            label="Review Candidates"
            onClick={() => onNavigate('Recruitment Candidates')}
          />

          <QuickAction
            icon={<DashboardIcon name="calendar" />}
            label="Schedule Interview"
            onClick={() => onNavigate('Recruitment Interviews')}
          />

          <QuickAction
            icon={<DashboardIcon name="document" />}
            label="Create Offer"
            onClick={() => onNavigate('Recruitment Onboarding')}
          />

          <QuickAction
            icon={<DashboardIcon name="settings" />}
            label="Manage Organization"
            onClick={() => onNavigate('Employer Organization')}
          />
        </div>
      </section>
    </>
  )
}
