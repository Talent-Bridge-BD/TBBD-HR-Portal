import { useEffect, useState } from 'react'
import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import DashboardCard from '../components/DashboardCard'
import QuickAction from '../components/QuickAction'

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

        const response = await fetch('/api/employer/dashboard')

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
      <PageHeader
        title={`Welcome, ${dashboard.employer_name}`}
        subtitle={`${organizationLabel} · Employer Portal`}
      />

      {error && (
        <div className="empty-state">
          <strong>Unable to load dashboard</strong>
          <span>{error}</span>
        </div>
      )}

      <div className="stats-grid">
        <StatCard
          icon="•"
          label="Active jobs"
          value={loading ? '—' : stats.active_jobs}
          detail="Currently open"
        />

        <StatCard
          icon="•"
          label="New applications"
          value={loading ? '—' : stats.new_applications}
          detail="Awaiting review"
        />

        <StatCard
          icon="+"
          label="Candidates pipeline"
          value={loading ? '—' : stats.candidates_pipeline}
          detail="Active applications"
        />

        <StatCard
          icon="•"
          label="Upcoming interviews"
          value={loading ? '—' : stats.interviews_upcoming}
          detail="Scheduled interviews"
        />
      </div>

      <section className="dashboard-grid">
        <DashboardCard title="Recruitment Pipeline">
          <div className="overview-grid">
            <div className="overview-item">
              <span className="overview-icon">+</span>
              <div>
                <strong>New</strong>
                <span>{loading ? '—' : pipeline.new} applications</span>
              </div>
            </div>

            <div className="overview-item">
              <span className="overview-icon">•</span>
              <div>
                <strong>Screening</strong>
                <span>{loading ? '—' : pipeline.screening} candidates</span>
              </div>
            </div>

            <div className="overview-item">
              <span className="overview-icon">•</span>
              <div>
                <strong>Shortlisted</strong>
                <span>{loading ? '—' : pipeline.shortlisted} candidates</span>
              </div>
            </div>

            <div className="overview-item">
              <span className="overview-icon">•</span>
              <div>
                <strong>Interview</strong>
                <span>{loading ? '—' : pipeline.interview} candidates</span>
              </div>
            </div>

            <div className="overview-item">
              <span className="overview-icon">•</span>
              <div>
                <strong>Offer</strong>
                <span>{loading ? '—' : pipeline.offer} candidates</span>
              </div>
            </div>

            <div className="overview-item">
              <span className="overview-icon">•</span>
              <div>
                <strong>Hired</strong>
                <span>{loading ? '—' : pipeline.hired} candidates</span>
              </div>
            </div>
          </div>
        </DashboardCard>

        <DashboardCard title="Upcoming Interviews">
          <div className="empty-state">
            <strong>Interview schedule</strong>
            <span>
              Upcoming interview details will appear here when interviews are scheduled.
            </span>
          </div>
        </DashboardCard>
      </section>

      <section className="dashboard-card">
        <div className="card-heading">
          <h2>Quick Actions</h2>
        </div>

        <div className="quick-actions">
          <QuickAction
            icon="+"
            label="Create Job"
            onClick={() => onNavigate('Recruitment Jobs')}
          />

          <QuickAction
            icon="•"
            label="Review Candidates"
            onClick={() => onNavigate('Recruitment Candidates')}
          />

          <QuickAction
            icon="•"
            label="Schedule Interview"
            onClick={() => onNavigate('Recruitment Interviews')}
          />

          <QuickAction
            icon="•"
            label="Create Offer"
            onClick={() => onNavigate('Recruitment Offers')}
          />

          <QuickAction
            icon="•"
            label="Manage Organization"
            onClick={() => onNavigate('Employer Organization')}
          />
        </div>
      </section>
    </>
  )
}
