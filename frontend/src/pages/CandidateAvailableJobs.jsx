import { useEffect, useState } from 'react'

import PageHeader from '../components/PageHeader'
import DashboardCard from '../components/DashboardCard'

export default function CandidateAvailableJobs() {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [applyingJobId, setApplyingJobId] = useState('')
  const [applicationError, setApplicationError] = useState('')
  const [applicationSuccess, setApplicationSuccess] = useState('')

  useEffect(() => {
    let active = true

    async function loadJobs() {
      try {
        setLoading(true)
        setError('')

        const response = await fetch('/api/candidate/jobs')

        if (!response.ok) {
          const body = await response.text()
          throw new Error(body || `Unable to load jobs (${response.status})`)
        }

        const data = await response.json()

        if (!active) return

        setJobs(Array.isArray(data.jobs) ? data.jobs : [])
      } catch (err) {
        if (active) {
          setError(err.message || 'Unable to load available jobs.')
        }
      } finally {
        if (active) {
          setLoading(false)
        }
      }
    }

    loadJobs()

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

  async function handleApply(jobId) {
    try {
      setApplyingJobId(jobId)
      setApplicationError('')
      setApplicationSuccess('')

      const response = await fetch('/api/candidate/applications', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          job_id: jobId,
        }),
      })

      const data = await response.json().catch(() => ({}))

      if (!response.ok) {
        throw new Error(
          data.detail ||
            data.message ||
            `Unable to submit application (${response.status})`,
        )
      }

      setApplicationSuccess(
        data.message || 'Application submitted successfully.',
      )
    } catch (err) {
      setApplicationError(
        err.message || 'Unable to submit your application.',
      )
    } finally {
      setApplyingJobId('')
    }
  }

  return (
    <>
      <PageHeader
        title="Available Jobs"
        subtitle="Explore recruitment opportunities that may match your profile."
      />

      <DashboardCard title="Job Opportunities">
        {applicationError && (
          <div className="empty-state">
            <strong>Application could not be submitted</strong>
            <span>{applicationError}</span>
          </div>
        )}

        {applicationSuccess && (
          <div className="empty-state">
            <strong>Application submitted</strong>
            <span>{applicationSuccess}</span>
          </div>
        )}

        {loading && (
          <div className="empty-state">
            <strong>Loading available jobs...</strong>
            <span>
              Please wait while current opportunities are retrieved.
            </span>
          </div>
        )}

        {!loading && error && (
          <div className="empty-state">
            <strong>Unable to load jobs</strong>
            <span>{error}</span>
          </div>
        )}

        {!loading && !error && jobs.length === 0 && (
          <div className="empty-state">
            <strong>No jobs available yet</strong>
            <span>
              New recruitment opportunities will appear here when they become
              available.
            </span>
          </div>
        )}

        {!loading && !error && jobs.length > 0 && (
          <div className="overview-grid">
            {jobs.map((job) => (
              <div className="overview-item" key={job.id}>
                <span className="overview-icon">▤</span>

                <div>
                  <strong>{job.title}</strong>

                  <span>
                    {job.location || 'Location not specified'}
                    {job.country ? ` · ${job.country}` : ''}
                  </span>

                  {job.employment_type && (
                    <span>{job.employment_type}</span>
                  )}

                  <span>
                    {job.number_of_positions || 1}{' '}
                    {job.number_of_positions === 1
                      ? 'position'
                      : 'positions'}
                  </span>

                  {job.description && <span>{job.description}</span>}

                  <span>
                    Closing date: {formatDate(job.closing_at)}
                  </span>

                  <button
                    type="button"
                    onClick={() => handleApply(job.id)}
                    disabled={applyingJobId === job.id}
                  >
                    {applyingJobId === job.id ? 'Applying...' : 'Apply'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </DashboardCard>

      <section className="dashboard-card">
        <div className="card-heading">
          <h2>How Job Matching Works</h2>
        </div>

        <div className="overview-grid">
          <div className="overview-item">
            <span className="overview-icon">◉</span>

            <div>
              <strong>Complete Your Profile</strong>
              <span>
                Keep your professional information, skills, and experience
                up to date.
              </span>
            </div>
          </div>

          <div className="overview-item">
            <span className="overview-icon">▤</span>

            <div>
              <strong>Explore Jobs</strong>
              <span>
                Review available opportunities and recruitment requirements.
              </span>
            </div>
          </div>

          <div className="overview-item">
            <span className="overview-icon">✓</span>

            <div>
              <strong>Apply</strong>
              <span>
                Submit your application for suitable opportunities.
              </span>
            </div>
          </div>

          <div className="overview-item">
            <span className="overview-icon">◷</span>

            <div>
              <strong>Track Progress</strong>
              <span>
                Follow your application, interview, and hiring progress.
              </span>
            </div>
          </div>
        </div>
      </section>
    </>
  )
}
