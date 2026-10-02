import { useEffect, useState } from 'react'

import PageHeader from '../components/PageHeader'
import DashboardCard from '../components/DashboardCard'
import { authenticatedFetch } from '../utils/auth'

export default function CandidateAvailableJobs() {
  const [jobs, setJobs] = useState([])
  const [applications, setApplications] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [applyingJobId, setApplyingJobId] = useState('')
  const [applicationError, setApplicationError] = useState('')
  const [applicationSuccess, setApplicationSuccess] = useState('')
  const [selectedJobId, setSelectedJobId] = useState('')
  const [coverLetter, setCoverLetter] = useState('')

  useEffect(() => {
    let active = true

    async function loadJobs() {
      try {
        setLoading(true)
        setError('')

        const response = await authenticatedFetch('/api/candidate/jobs')

        if (!response.ok) {
          const body = await response.text()
          throw new Error(body || `Unable to load jobs (${response.status})`)
        }

        const data = await response.json()

        if (!active) return

        setJobs(Array.isArray(data.jobs) ? data.jobs : [])

        const applicationsResponse = await authenticatedFetch(
          '/api/candidate/applications',
        )

        if (applicationsResponse.ok) {
          const applicationsData = await applicationsResponse.json()
          if (active) {
            setApplications(
              Array.isArray(applicationsData.applications)
                ? applicationsData.applications
                : [],
            )
          }
        }
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

  function getClosingState(value) {
    if (!value) {
      return {
        label: 'Closing date: Not specified',
        closed: false,
        emphasis: false,
      }
    }

    const closingDate = new Date(value)

    if (Number.isNaN(closingDate.getTime())) {
      return {
        label: `Closing date: ${formatDate(value)}`,
        closed: false,
        emphasis: false,
      }
    }

    const now = new Date()
    const closingDay = new Date(
      closingDate.getFullYear(),
      closingDate.getMonth(),
      closingDate.getDate(),
    )
    const today = new Date(
      now.getFullYear(),
      now.getMonth(),
      now.getDate(),
    )

    const daysUntilClosing = Math.ceil(
      (closingDay.getTime() - today.getTime()) / 86400000,
    )

    if (daysUntilClosing < 0) {
      return {
        label: `Applications closed · ${formatDate(value)}`,
        closed: true,
        emphasis: true,
      }
    }

    if (daysUntilClosing === 0) {
      return {
        label: `Closing today · ${formatDate(value)}`,
        closed: false,
        emphasis: true,
      }
    }

    if (daysUntilClosing <= 7) {
      return {
        label: `Closing soon · ${formatDate(value)}`,
        closed: false,
        emphasis: true,
      }
    }

    return {
      label: `Closing date: ${formatDate(value)}`,
      closed: false,
      emphasis: false,
    }
  }

  function openApplicationForm(jobId) {
    setSelectedJobId(jobId)
    setCoverLetter('')
    setApplicationError('')
    setApplicationSuccess('')
  }

  function closeApplicationForm() {
    if (applyingJobId) return
    setSelectedJobId('')
    setCoverLetter('')
  }

  async function handleApply() {
    if (!selectedJobId) return

    try {
      setApplyingJobId(selectedJobId)
      setApplicationError('')
      setApplicationSuccess('')

      const trimmedCoverLetter = coverLetter.trim()

      const response = await authenticatedFetch('/api/candidate/applications', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          job_id: selectedJobId,
          cover_letter: trimmedCoverLetter || null,
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

      setApplications((current) => [
        ...current,
        {
          id: data.application?.id || `submitted-${selectedJobId}`,
          job_id: selectedJobId,
          cover_letter: trimmedCoverLetter || null,
        },
      ])

      setApplicationSuccess(
        trimmedCoverLetter
          ? 'Application submitted successfully. Cover letter submitted ✓'
          : 'Application submitted successfully. No cover letter provided.',
      )

      setSelectedJobId('')
      setCoverLetter('')
    } catch (err) {
      setApplicationError(
        err.message || 'Unable to submit your application.',
      )
    } finally {
      setApplyingJobId('')
    }
  }

  return (
    <div className="candidate-portal-page">
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
          <div className="candidate-jobs-grid">
            {jobs.map((job) => (
              <article className="candidate-job-card" key={job.id}>
                <div className="candidate-job-icon" aria-hidden="true">▤</div>

                <div className="candidate-job-content">
                  <div className="candidate-job-heading">
                    <strong>{job.title}</strong>
                  </div>
                  <div className="candidate-job-meta">

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

                  </div>

                  {job.description && (
                    <span className="candidate-job-description">
                      {job.description}
                    </span>
                  )}

                  {(() => {
                    const closingState = getClosingState(job.closing_at)

                    return (
                      <>
                        <span
                          className={
                            closingState.emphasis
                              ? 'job-closing-date job-closing-date-emphasis'
                              : 'job-closing-date'
                          }
                        >
                          {closingState.label}
                        </span>

                        {!closingState.closed && (
                          applications.some(
                            (application) => application.job_id === job.id,
                          ) ? (
                            <button type="button" disabled>
                              Already Applied
                            </button>
                          ) : (
                            <button
                              type="button"
                              onClick={() => openApplicationForm(job.id)}
                              disabled={applyingJobId === job.id}
                            >
                              Apply
                            </button>
                          )
                        )}
                      </>
                    )
                  })()}
                </div>
              </article>
            ))}
          </div>
        )}
      </DashboardCard>

      {selectedJobId && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="application-dialog-title"
          style={{
            position: 'fixed',
            inset: 0,
            zIndex: 1000,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '24px',
            background: 'rgba(15, 23, 42, 0.45)',
          }}
        >
          <div
            style={{
              width: '100%',
              maxWidth: '680px',
              background: '#FFFFFF',
              borderRadius: '14px',
              padding: '24px',
              boxShadow: '0 20px 50px rgba(15, 23, 42, 0.2)',
            }}
          >
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'flex-start',
                gap: '16px',
                marginBottom: '20px',
              }}
            >
              <div>
                <h2
                  id="application-dialog-title"
                  style={{
                    margin: 0,
                    color: '#0F172A',
                    fontSize: '20px',
                  }}
                >
                  Submit Application
                </h2>
                <p
                  style={{
                    margin: '6px 0 0',
                    color: '#64748B',
                    fontSize: '14px',
                  }}
                >
                  Add an optional cover letter before submitting your
                  application.
                </p>
              </div>

              <button
                type="button"
                onClick={closeApplicationForm}
                disabled={Boolean(applyingJobId)}
                aria-label="Close application form"
              >
                ×
              </button>
            </div>

            <label
              htmlFor="candidate-cover-letter"
              style={{
                display: 'block',
                color: '#0F172A',
                fontWeight: 600,
                marginBottom: '8px',
              }}
            >
              Cover Letter{' '}
              <span style={{ color: '#64748B', fontWeight: 400 }}>
                (Optional)
              </span>
            </label>

            <textarea
              id="candidate-cover-letter"
              value={coverLetter}
              onChange={(event) => setCoverLetter(event.target.value)}
              placeholder="Briefly explain why you are interested in this position and why your experience is relevant."
              rows={8}
              maxLength={5000}
              disabled={Boolean(applyingJobId)}
              style={{
                width: '100%',
                boxSizing: 'border-box',
                resize: 'vertical',
                minHeight: '180px',
                padding: '12px',
                border: '1px solid #E2E8F0',
                borderRadius: '8px',
                color: '#0F172A',
                fontSize: '14px',
                lineHeight: 1.5,
              }}
            />

            <div
              style={{
                marginTop: '6px',
                color: '#64748B',
                fontSize: '12px',
              }}
            >
              {coverLetter.length}/5000 characters
            </div>

            {applicationError && (
              <div
                style={{
                  marginTop: '14px',
                  padding: '12px',
                  borderRadius: '8px',
                  background: '#FEF2F2',
                  color: '#991B1B',
                  fontSize: '14px',
                }}
              >
                {applicationError}
              </div>
            )}

            <div
              style={{
                display: 'flex',
                justifyContent: 'flex-end',
                gap: '10px',
                marginTop: '20px',
              }}
            >
              <button
                type="button"
                className="secondary-action"
                onClick={closeApplicationForm}
                disabled={Boolean(applyingJobId)}
              >
                Cancel
              </button>

              <button
                type="button"
                className="primary-action"
                onClick={handleApply}
                disabled={Boolean(applyingJobId)}
              >
                {applyingJobId ? 'Submitting...' : 'Submit Application'}
              </button>
            </div>
          </div>
        </div>
      )}


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
    </div>
  )
}
