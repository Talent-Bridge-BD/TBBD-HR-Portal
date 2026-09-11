import { useEffect, useState } from 'react'

import PageHeader from '../components/PageHeader'
import DashboardCard from '../components/DashboardCard'

export default function CandidateMyApplications() {
  const [applications, setApplications] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true

    async function loadApplications() {
      try {
        setLoading(true)
        setError('')

        const response = await fetch('/api/candidate/applications')

        if (!response.ok) {
          const body = await response.text()
          throw new Error(
            body || `Unable to load applications (${response.status})`,
          )
        }

        const data = await response.json()

        if (!active) return

        setApplications(
          Array.isArray(data.applications) ? data.applications : [],
        )
      } catch (err) {
        if (active) {
          setError(
            err.message || 'Unable to load your applications.',
          )
        }
      } finally {
        if (active) {
          setLoading(false)
        }
      }
    }

    loadApplications()

    return () => {
      active = false
    }
  }, [])

  function formatDate(value) {
    if (!value) return 'Not specified'

    const date = new Date(value)

    if (Number.isNaN(date.getTime())) {
      return value
    }

    return date.toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  function formatStatus(status) {
    if (!status) return 'Submitted'

    return status
      .replace(/_/g, ' ')
      .replace(/\b\w/g, (character) => character.toUpperCase())
  }

  return (
    <>
      <PageHeader
        title="My Applications"
        subtitle="Track your job applications and recruitment progress."
      />

      <DashboardCard title="Application Activity">
        {loading && (
          <div className="empty-state">
            <strong>Loading applications...</strong>
            <span>
              Please wait while your application history is retrieved.
            </span>
          </div>
        )}

        {!loading && error && (
          <div className="empty-state">
            <strong>Unable to load applications</strong>
            <span>{error}</span>
          </div>
        )}

        {!loading && !error && applications.length === 0 && (
          <div className="empty-state">
            <strong>No applications yet</strong>
            <span>
              Your submitted job applications and recruitment status will
              appear here.
            </span>
          </div>
        )}

        {!loading && !error && applications.length > 0 && (
          <div className="overview-grid">
            {applications.map((application) => (
              <div className="overview-item" key={application.id}>
                <span className="overview-icon">▤</span>

                <div>
                  <strong>
                    {application.job_title || 'Job application'}
                  </strong>

                  <span>
                    Status: {formatStatus(application.status)}
                  </span>

                  <span>
                    Applied: {formatDate(application.applied_at)}
                  </span>

                  {application.cover_letter && (
                    <span>
                      Cover letter submitted
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </DashboardCard>

      <section className="dashboard-card">
        <div className="card-heading">
          <h2>Application Status</h2>
        </div>

        <div className="overview-grid">
          <div className="overview-item">
            <span className="overview-icon">▤</span>
            <div>
              <strong>Submitted</strong>
              <span>Applications you have submitted.</span>
            </div>
          </div>

          <div className="overview-item">
            <span className="overview-icon">◌</span>
            <div>
              <strong>Under Review</strong>
              <span>Applications currently being reviewed.</span>
            </div>
          </div>

          <div className="overview-item">
            <span className="overview-icon">◷</span>
            <div>
              <strong>Interview</strong>
              <span>
                Applications that have reached the interview stage.
              </span>
            </div>
          </div>

          <div className="overview-item">
            <span className="overview-icon">✓</span>
            <div>
              <strong>Shortlisted</strong>
              <span>
                Applications where you have been shortlisted.
              </span>
            </div>
          </div>
        </div>
      </section>
    </>
  )
}
