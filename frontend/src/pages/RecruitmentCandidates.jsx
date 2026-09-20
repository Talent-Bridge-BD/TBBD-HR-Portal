import { useEffect, useMemo, useState } from 'react'

import PageHeader from '../components/PageHeader'

export default function RecruitmentCandidates({ auth }) {
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
            data.detail || 'Unable to load candidates.'
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

  const candidates = useMemo(
    () =>
      Array.from(
        new Map(
          applications.map((application) => [
            application.candidate_id,
            application,
          ])
        ).values()
      ),
    [applications]
  )

  const filteredCandidates = useMemo(() => {
    const query = search.trim().toLowerCase()

    if (!query) {
      return candidates
    }

    return candidates.filter((candidate) =>
      [
        candidate.candidate_first_name,
        candidate.candidate_last_name,
        candidate.candidate_email,
        candidate.job_title,
        candidate.status,
      ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase()
        .includes(query)
    )
  }, [candidates, search])

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
          data.detail || 'Unable to load application details.'
        )
      }

      setSelectedApplication(data.application)
    } catch (err) {
      setDetailError(err.message)
    } finally {
      setDetailLoading(false)
    }
  }


  const updateApplicationStatus = async (
    applicationId,
    status
  ) => {
    try {
      const response = await fetch(
        `/api/applications/${encodeURIComponent(
          applicationId
        )}/status?organization_id=${encodeURIComponent(
          organizationId
        )}&status=${encodeURIComponent(status)}`,
        {
          method: 'PUT',
          credentials: 'include',
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || 'Unable to update status.'
        )
      }

      setSelectedApplication(data.application)

      setApplications((current) =>
        current.map((item) =>
          item.id === applicationId
            ? data.application
            : item
        )
      )
    } catch (err) {
      alert(err.message)
    }
  }

  const formatDate = (value) => {

    if (!value) {
      return '—'
    }

    return new Date(value).toLocaleDateString()
  }

  const getInitials = (candidate) => {
    const first = candidate.candidate_first_name?.[0] || ''
    const last = candidate.candidate_last_name?.[0] || ''

    return `${first}${last}`.toUpperCase() || 'C'
  }

  return (
    <>
      <PageHeader
        title="Candidates"
        subtitle="Manage and review candidates across the recruitment pipeline."
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
          <p>Loading candidates...</p>
        </section>
      ) : error ? (
        <section className="placeholder-card">
          <h2>Unable to load candidates</h2>
          <p>{error}</p>
        </section>
      ) : (
        <>
          <section className="dashboard-card recruitment-candidates-toolbar">
            <div>
              <strong>{candidates.length}</strong>
              <span>
                {candidates.length === 1
                  ? ' candidate'
                  : ' candidates'}
              </span>
            </div>

            <label>
              <span className="sr-only">Search candidates</span>
              <input
                type="search"
                placeholder="Search candidates, email or job..."
                value={search}
                onChange={(event) => setSearch(event.target.value)}
              />
            </label>
          </section>

          {filteredCandidates.length === 0 ? (
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
                      <th>Applied Job</th>
                      <th>Status</th>
                      <th>Applied Date</th>
                      <th>Actions</th>
                    </tr>
                  </thead>

                  <tbody>
                    {filteredCandidates.map((candidate) => (
                      <tr key={candidate.candidate_id}>
                        <td>
                          <div className="candidate-identity">
                            <span className="candidate-avatar">
                              {getInitials(candidate)}
                            </span>

                            <div>
                              <strong>
                                {candidate.candidate_first_name}{' '}
                                {candidate.candidate_last_name}
                              </strong>

                              <small>
                                Candidate ID: {candidate.candidate_id}
                              </small>
                            </div>
                          </div>
                        </td>

                        <td>
                          <span className="candidate-email">
                            {candidate.candidate_email}
                          </span>
                        </td>

                        <td>
                          <strong className="candidate-job">
                            {candidate.job_title || '—'}
                          </strong>
                        </td>

                        <td>
                          <span className="recruitment-status-badge">
                            {candidate.status || 'Applied'}
                          </span>
                        </td>

                        <td>
                          <span className="candidate-date">
                            {formatDate(candidate.applied_at)}
                          </span>
                        </td>

                        <td>
                          <button
                            type="button"
                            className="recruitment-view-button"
                            onClick={() =>
                              openApplication(candidate.id)
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
                aria-label="Candidate application details"
                onClick={(event) => event.stopPropagation()}
              >
                <div className="recruitment-detail-header">
                  <div>
                    <span className="recruitment-detail-eyebrow">
                      APPLICATION DETAILS
                    </span>

                    <h2>
                      {selectedApplication
                        ? `${selectedApplication.candidate_first_name} ${selectedApplication.candidate_last_name}`
                        : 'Candidate Details'}
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
                    Loading application details...
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
                        <span>Application Status</span>
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
