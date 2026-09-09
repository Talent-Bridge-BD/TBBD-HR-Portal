import { useEffect, useState } from 'react'
import PageHeader from '../components/PageHeader'

export default function EmployerJobOpenings({ auth }) {
  const [jobs, setJobs] = useState([])
  const [organizationId, setOrganizationId] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

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
        ) : jobs.length === 0 ? (
          <div className="empty-state">
            <strong>No job openings yet</strong>
            <span>
              Approved recruitment requests will become job openings here.
            </span>
          </div>
        ) : (
          <div className="notification-list">
            {jobs.map((job) => (
              <div className="notification-item" key={job.id}>
                <span className="notification-dot" />
                <span className="notification-content">
                  <strong>{job.title}</strong>
                  <small>
                    {job.status}
                    {job.location ? ` · ${job.location}` : ''}
                    {job.country ? ` · ${job.country}` : ''}
                    {job.number_of_positions
                      ? ` · ${job.number_of_positions} position(s)`
                      : ''}
                  </small>
                </span>
              </div>
            ))}
          </div>
        )}
      </section>
    </>
  )
}
