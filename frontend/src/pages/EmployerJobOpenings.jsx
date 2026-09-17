import { useEffect, useState } from 'react'
import PageHeader from '../components/PageHeader'

export default function EmployerJobOpenings({ auth }) {
  const [jobs, setJobs] = useState([])
  const [organizationId, setOrganizationId] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [statusFilter, setStatusFilter] = useState('All')

  const statusOptions = ['All', 'Open', 'Paused', 'Closed', 'Draft']

  const filteredJobs =
    statusFilter === 'All'
      ? jobs
      : jobs.filter(
          (job) =>
            String(job.status || '').toLowerCase() ===
            statusFilter.toLowerCase(),
        )

  useEffect(() => {
    const id = auth?.organization_ids?.[0] || ''
    setOrganizationId(id)
  }, [auth])

  useEffect(() => {
    async function loadJobs() {
      if (!organizationId) {
        setJobs([])
        setLoading(false)
        return
      }

      setLoading(true)
      setError('')

      try {
        const response = await fetch(
          `/api/jobs?organization_id=${encodeURIComponent(organizationId)}`,
          { credentials: 'include' },
        )

        if (!response.ok) {
          throw new Error(`Failed to load job openings: ${response.status}`)
        }

        const data = await response.json()
        setJobs(data.jobs || [])
      } catch (err) {
        console.error(err)
        setError('Unable to load job openings.')
      } finally {
        setLoading(false)
      }
    }

    loadJobs()
  }, [organizationId])

  return (
    <>
      <PageHeader
        title="Job Openings"
        subtitle="View your organization's recruitment job openings."
      />

      <section className="dashboard-card">
        <div className="card-heading">
          <div>
            <h2>Employer Job Openings</h2>
            <p>
              Review open, paused, closed, and draft positions for your
              organization.
            </p>
          </div>
        </div>

        {error && (
          <div className="empty-state">
            <strong>{error}</strong>
          </div>
        )}

        {!organizationId && !loading ? (
          <div className="empty-state">
            <strong>Organization access required</strong>
            <span>
              Your account must be connected to an employer organization.
            </span>
          </div>
        ) : loading ? (
          <div className="empty-state">
            <strong>Loading job openings...</strong>
          </div>
        ) : (
          <>
            <div className="job-opening-filters" aria-label="Job opening status filter">
              {statusOptions.map((status) => {
                const count =
                  status === 'All'
                    ? jobs.length
                    : jobs.filter(
                        (job) =>
                          String(job.status || '').toLowerCase() ===
                          status.toLowerCase(),
                      ).length

                return (
                  <button
                    key={status}
                    type="button"
                    className={`job-opening-filter ${
                      statusFilter === status ? 'active' : ''
                    }`}
                    onClick={() => setStatusFilter(status)}
                  >
                    {status} <span>{count}</span>
                  </button>
                )
              })}
            </div>

            {filteredJobs.length === 0 ? (
              <div className="empty-state">
                <strong>No {statusFilter.toLowerCase()} job openings</strong>
                <span>
                  There are no job openings with this status for your
                  organization.
                </span>
              </div>
            ) : (
              <div className="job-opening-list">
                {filteredJobs.map((job) => (
                  <article className="job-opening-card" key={job.id}>
                    <div className="job-opening-main">
                      <div className="job-opening-title-row">
                        <h3>{job.title}</h3>
                        <span className={`job-opening-status status-${String(job.status || '').toLowerCase()}`}>
                          {job.status}
                        </span>
                      </div>

                      <div className="job-opening-meta">
                        {job.location && (
                          <span>📍 {job.location}</span>
                        )}
                        {job.country && (
                          <span>🌐 {job.country}</span>
                        )}
                        {job.employment_type && (
                          <span>💼 {job.employment_type}</span>
                        )}
                        {job.number_of_positions && (
                          <span>👥 {job.number_of_positions} position(s)</span>
                        )}
                        {job.closing_at && (
                          <span>
                            📅 Closing {new Date(job.closing_at).toLocaleDateString()}
                          </span>
                        )}
                      </div>
                    </div>
                  </article>
                ))}
              </div>
            )}
          </>
        )}

      </section>
    </>
  )
}
