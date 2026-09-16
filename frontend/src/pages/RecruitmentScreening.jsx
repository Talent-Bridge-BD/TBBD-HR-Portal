import { useEffect, useMemo, useState } from 'react'

import PageHeader from '../components/PageHeader'

export default function RecruitmentScreening({ auth }) {
  const organizationId = auth?.organization_ids?.[0] || ''

  const [applications, setApplications] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [selectedApplication, setSelectedApplication] = useState(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [detailError, setDetailError] = useState('')

  useEffect(() => {
    if (!organizationId) {
      setLoading(false)
      return
    }

    fetch(
      `/api/applications?organization_id=${encodeURIComponent(
        organizationId
      )}`,
      {
        credentials: 'include',
      }
    )
      .then(async (response) => {
        const data = await response.json()

        if (!response.ok) {
          throw new Error(
            data.detail || 'Unable to load screening candidates.'
          )
        }

        return data
      })
      .then((data) => {
        setApplications(data.applications || [])
      })
      .catch((err) => {
        setError(err.message)
      })
      .finally(() => {
        setLoading(false)
      })
  }, [organizationId])

  const filteredApplications = useMemo(() => {
    const query = search.trim().toLowerCase()

    if (!query) {
      return applications
    }

    return applications.filter((application) =>
      [
        application.candidate_first_name,
        application.candidate_last_name,
        application.candidate_email,
        application.job_title,
        application.status,
        application.cover_letter,
      ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase()
        .includes(query)
    )
  }, [applications, search])

  const openApplication = async (applicationId) => {
    setSelectedApplication(null)
    setDetailError('')
    setDetailLoading(true)

    try {
      const response = await fetch(
        `/api/applications/${encodeURIComponent(
          applicationId
        )}?organization_id=${encodeURIComponent(
          organizationId
        )}`,
        {
          credentials: 'include',
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || 'Unable to load screening details.'
        )
      }

      setSelectedApplication(data.application)
    } catch (err) {
      setDetailError(err.message)
    } finally {
      setDetailLoading(false)
    }
  }

  const formatDate = (value) => {
    if (!value) {
      return '—'
    }

    return new Date(value).toLocaleDateString()
  }

  const getInitials = (application) => {
    const first = application.candidate_first_name?.[0] || ''
    const last = application.candidate_last_name?.[0] || ''

    return `${first}${last}`.toUpperCase() || 'C'
  }

  return (
    <>
      <PageHeader
        title="Screening"
        subtitle="Review and evaluate candidates before moving them to the next recruitment stage."
      />

      {!organizationId ? (
        <section className="placeholder-card">
          <h2>Organization access required</h2>
          <p>
            Your account is not currently assigned to an organization.
          </p>
        </section>
      ) : loading ? (
        <section className="placeholder-card">
          <p>Loading screening candidates...</p>
        </section>
      ) : error ? (
        <section className="placeholder-card">
          <h2>Unable to load screening candidates</h2>
          <p>{error}</p>
        </section>
      ) : (
        <>
          <section className="dashboard-card recruitment-candidates-toolbar">
            <div>
              <strong>{applications.length}</strong>
              <span>
                {applications.length === 1
                  ? ' candidate'
                  : ' candidates'}
              </span>
            </div>

            <label>
              <span className="sr-only">Search screening candidates</span>
              <input
                type="search"
                placeholder="Search candidate, email or job..."
                value={search}
                onChange={(event) => setSearch(event.target.value)}
              />
            </label>
          </section>

          {filteredApplications.length === 0 ? (
            <section className="placeholder-card">
              <h2>No matching candidates</h2>
              <p>
                Try a different candidate name, email address, or job title.
              </p>
            </section>
          ) : (
            <section className="dashboard-card recruitment-candidates-card">
              <div className="table-wrap recruitment-candidates-table-wrap">
                <table className="recruitment-candidates-table">
                  <thead>
                    <tr>
                      <th>Candidate</th>
                      <th>Email</th>
                      <th>Job</th>
                      <th>Workflow Status</th>
                      <th>Cover Letter</th>
                      <th>Applied Date</th>
                      <th>Actions</th>
                    </tr>
                  </thead>

                  <tbody>
                    {filteredApplications.map((application) => (
                      <tr key={application.id}>
                        <td>
                          <div className="candidate-identity">
                            <span className="candidate-avatar">
                              {getInitials(application)}
                            </span>

                            <div>
                              <strong>
                                {application.candidate_first_name}{' '}
                                {application.candidate_last_name}
                              </strong>

                              <small>
                                Application ID: {application.id}
                              </small>
                            </div>
                          </div>
                        </td>

                        <td>
                          <span className="candidate-email">
                            {application.candidate_email}
                          </span>
                        </td>

                        <td>
                          <strong className="candidate-job">
                            {application.job_title || '—'}
                          </strong>
                        </td>

                        <td>
                          <span className="recruitment-status-badge">
                            {application.status || 'Applied'}
                          </span>
                        </td>

                        <td>
                          <span className="candidate-email">
                            {application.cover_letter
                              ? 'Provided'
                              : '—'}
                          </span>
                        </td>

                        <td>
                          <span className="candidate-date">
                            {formatDate(application.applied_at)}
                          </span>
                        </td>

                        <td>
                          <button
                            type="button"
                            className="recruitment-view-button"
                            onClick={() =>
                              openApplication(application.id)
                            }
                          >
                            View
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}

          {(detailLoading || detailError || selectedApplication) && (
            <div
              className="recruitment-detail-overlay"
              role="presentation"
              onClick={() => {
                if (!detailLoading) {
                  setSelectedApplication(null)
                  setDetailError('')
                }
              }}
            >
              <aside
                className="recruitment-detail-panel"
                role="dialog"
                aria-modal="true"
                aria-label="Screening details"
                onClick={(event) => event.stopPropagation()}
              >
                <div className="recruitment-detail-header">
                  <div>
                    <span className="recruitment-detail-eyebrow">
                      SCREENING DETAILS
                    </span>

                    <h2>
                      {selectedApplication
                        ? `${selectedApplication.candidate_first_name} ${selectedApplication.candidate_last_name}`
                        : 'Screening Details'}
                    </h2>
                  </div>

                  <button
                    type="button"
                    className="recruitment-detail-close"
                    onClick={() => {
                      setSelectedApplication(null)
                      setDetailError('')
                    }}
                    aria-label="Close details"
                  >
                    ×
                  </button>
                </div>

                {detailLoading ? (
                  <div className="recruitment-detail-loading">
                    Loading screening details...
                  </div>
                ) : detailError ? (
                  <div className="recruitment-detail-error">
                    <strong>Unable to load details</strong>
                    <p>{detailError}</p>
                  </div>
                ) : selectedApplication ? (
                  <div className="recruitment-detail-content">
                    <div className="recruitment-detail-profile">
                      <span className="candidate-avatar candidate-avatar-large">
                        {getInitials(selectedApplication)}
                      </span>

                      <div>
                        <h3>
                          {selectedApplication.candidate_first_name}{' '}
                          {selectedApplication.candidate_last_name}
                        </h3>

                        <p>
                          {selectedApplication.candidate_email}
                        </p>
                      </div>
                    </div>

                    <div className="recruitment-detail-grid">
                      <div>
                        <span>Phone</span>
                        <strong>
                          {selectedApplication.candidate_phone || '—'}
                        </strong>
                      </div>

                      <div>
                        <span>Applied Job</span>
                        <strong>
                          {selectedApplication.job_title || '—'}
                        </strong>
                      </div>

                      <div>
                        <span>Workflow Status</span>
                        <strong>
                          {selectedApplication.status || 'Applied'}
                        </strong>
                      </div>

                      <div>
                        <span>Applied Date</span>
                        <strong>
                          {formatDate(
                            selectedApplication.applied_at
                          )}
                        </strong>
                      </div>
                    </div>

                    <section className="recruitment-cover-letter">
                      <h3>Cover Letter</h3>

                      <p>
                        {selectedApplication.cover_letter ||
                          'No cover letter was provided with this application.'}
                      </p>
                    </section>
                  </div>
                ) : null}
              </aside>
            </div>
          )}
        </>
      )}
    </>
  )
}
