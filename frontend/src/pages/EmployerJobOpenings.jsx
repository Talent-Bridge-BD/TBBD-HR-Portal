import { useEffect, useState } from 'react'
import PageHeader from '../components/PageHeader'
import { authenticatedFetch } from '../utils/auth'

export default function EmployerJobOpenings({ auth }) {
  const [jobs, setJobs] = useState([])
  const [organizationId, setOrganizationId] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [statusFilter, setStatusFilter] = useState('All')
  const [actionJobId, setActionJobId] = useState('')

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

  async function loadJobs(showLoading = true) {
    if (!organizationId) {
      setJobs([])
      setLoading(false)
      return
    }

    if (showLoading) {
      setLoading(true)
    }

    setError('')

    try {
      const response = await authenticatedFetch(
        `/api/jobs?organization_id=${encodeURIComponent(organizationId)}`,
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
      if (showLoading) {
        setLoading(false)
      }
    }
  }

  useEffect(() => {
    loadJobs()
  }, [organizationId])

  async function updateJobStatus(job, status) {
    if (!organizationId || !job?.id) return

    setActionJobId(job.id)
    setError('')

    try {
      const response = await authenticatedFetch(`/api/jobs/${job.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          organization_id: organizationId,
          title: job.title,
          description: job.description,
          employment_type: job.employment_type,
          location: job.location,
          country: job.country,
          status,
          number_of_positions: job.number_of_positions,
          published_at:
            status === 'open'
              ? job.published_at || new Date().toISOString()
              : job.published_at,
          closing_at: job.closing_at,
          requisition_number: job.requisition_number || '',
          employer_name: job.employer_name || '',
          employer_country: job.employer_country || '',
          employer_city: job.employer_city || '',
          trade_skill_category: job.trade_skill_category || '',
          industry_sector: job.industry_sector || '',
          gender_requirement: job.gender_requirement || '',
          minimum_age: job.minimum_age,
          maximum_age: job.maximum_age,
          contract_duration: job.contract_duration || '',
          work_location: job.work_location || '',
          project_name: job.project_name || '',
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Unable to change job status.')
      }

      await loadJobs(false)
    } catch (err) {
      console.error(err)
      setError(err.message || 'Unable to change job status.')
    } finally {
      setActionJobId('')
    }
  }

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

                      <div className="job-opening-actions">
                        {String(job.status || '').toLowerCase() === 'draft' && (
                          <button
                            className="primary-action"
                            type="button"
                            onClick={() => updateJobStatus(job, 'open')}
                            disabled={actionJobId === job.id}
                          >
                            {actionJobId === job.id
                              ? 'Publishing...'
                              : 'Publish Job'}
                          </button>
                        )}

                        {String(job.status || '').toLowerCase() === 'open' && (
                          <>
                            <button
                              className="secondary-action"
                              type="button"
                              onClick={() => updateJobStatus(job, 'paused')}
                              disabled={actionJobId === job.id}
                            >
                              {actionJobId === job.id ? 'Updating...' : 'Pause'}
                            </button>

                            <button
                              className="secondary-action"
                              type="button"
                              onClick={() => updateJobStatus(job, 'closed')}
                              disabled={actionJobId === job.id}
                            >
                              {actionJobId === job.id ? 'Updating...' : 'Close'}
                            </button>
                          </>
                        )}

                        {String(job.status || '').toLowerCase() === 'paused' && (
                          <>
                            <button
                              className="primary-action"
                              type="button"
                              onClick={() => updateJobStatus(job, 'open')}
                              disabled={actionJobId === job.id}
                            >
                              {actionJobId === job.id ? 'Updating...' : 'Open'}
                            </button>

                            <button
                              className="secondary-action"
                              type="button"
                              onClick={() => updateJobStatus(job, 'closed')}
                              disabled={actionJobId === job.id}
                            >
                              {actionJobId === job.id ? 'Updating...' : 'Close'}
                            </button>
                          </>
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
