import { useEffect, useMemo, useState } from 'react'

import PageHeader from '../components/PageHeader'
import { authenticatedFetch } from '../utils/auth'
import { useOrganization } from '../context/OrganizationContext'

const STATUS_STYLES = {
  Applied: {
    color: '#0067B8',
    background: '#EAF4FB',
  },
  Screening: {
    color: '#D97706',
    background: '#FFF7E6',
  },
  Interview: {
    color: '#7C3AED',
    background: '#F3E8FF',
  },
  Completed: {
    color: '#16A34A',
    background: '#ECFDF3',
  },
}

function getDisplayStatus(status) {
  const normalized = String(status || '').toLowerCase()

  if (normalized === 'submitted') {
    return 'Applied'
  }

  if (normalized === 'screening' || normalized === 'under_review') {
    return 'Screening'
  }

  if (normalized === 'interview') {
    return 'Interview'
  }

  if (
    normalized === 'completed' ||
    normalized === 'hired' ||
    normalized === 'approved'
  ) {
    return 'Completed'
  }

  return status || 'Applied'
}

function formatDate(value) {
  if (!value) {
    return '—'
  }

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return '—'
  }

  return date.toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

function getCandidateName(application) {
  const name = [
    application.candidate_first_name,
    application.candidate_last_name,
  ]
    .filter(Boolean)
    .join(' ')

  return name || 'Unnamed Candidate'
}

function getInitials(application) {
  const name = getCandidateName(application)

  const parts = name.split(/\s+/).filter(Boolean)

  if (parts.length === 1) {
    return parts[0].slice(0, 2).toUpperCase()
  }

  return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase()
}

export default function EmployerApplications({ auth }) {
  const {
    selectedOrganizationId,
    organizationLoading,
  } = useOrganization()

  const organizationId = selectedOrganizationId || ''

  const [applications, setApplications] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [actionApplicationId, setActionApplicationId] = useState('')
  const [selectedApplication, setSelectedApplication] = useState(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [applicationDocuments, setApplicationDocuments] = useState([])
  const [documentsLoading, setDocumentsLoading] = useState(false)

  useEffect(() => {
    if (organizationLoading || !organizationId) {
      setLoading(false)
      return
    }

    authenticatedFetch(
      `/api/applications?organization_id=${encodeURIComponent(
        organizationId
      )}`,
    )
      .then(async (response) => {
        const data = await response.json()

        if (!response.ok) {
          throw new Error(
            data.detail || 'Unable to load applications.'
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
  }, [organizationId, organizationLoading])

  async function startScreening(application) {
    if (!application?.id || !organizationId) return

    setActionApplicationId(application.id)
    setError('')

    try {
      const response = await authenticatedFetch(
        `/api/applications/${application.id}/status?organization_id=${encodeURIComponent(
          organizationId
        )}&status=under_review`,
        {
          method: 'PUT',
        },
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || 'Unable to start screening.',
        )
      }

      setApplications((current) =>
        current.map((item) =>
          item.id === application.id
            ? { ...item, ...data.application }
            : item,
        ),
      )
    } catch (err) {
      console.error(err)
      setError(err.message || 'Unable to start screening.')
    } finally {
      setActionApplicationId('')
    }
  }

  async function updateApplicationStatus(application, status) {
    if (!application?.id || !organizationId) return

    setActionApplicationId(application.id)
    setError('')

    try {
      const response = await authenticatedFetch(
        `/api/applications/${application.id}/status?organization_id=${encodeURIComponent(
          organizationId
        )}&status=${encodeURIComponent(status)}`,
        {
          method: 'PUT',
        },
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || 'Unable to update application status.',
        )
      }

      setApplications((current) =>
        current.map((item) =>
          item.id === application.id
            ? { ...item, ...data.application }
            : item,
        ),
      )

      setSelectedApplication((current) =>
        current?.id === application.id
          ? { ...current, ...data.application }
          : current,
      )
    } catch (err) {
      console.error(err)
      setError(err.message || 'Unable to update application status.')
    } finally {
      setActionApplicationId('')
    }
  }

  async function viewApplicationDocument(document) {
    if (!document?.id || !selectedApplication?.id || !organizationId) return

    try {
      const response = await authenticatedFetch(
        `/api/applications/${selectedApplication.id}/documents/${document.id}?organization_id=${encodeURIComponent(
          organizationId
        )}`,
      )

      if (!response.ok) {
        let message = 'Unable to view candidate document.'
        try {
          const data = await response.json()
          message = data.detail || message
        } catch {
          // Keep the default message when the response is not JSON.
        }
        throw new Error(message)
      }

      const blob = await response.blob()
      const url = URL.createObjectURL(blob)
      window.open(url, '_blank', 'noopener,noreferrer')

      window.setTimeout(() => {
        URL.revokeObjectURL(url)
      }, 60000)
    } catch (err) {
      console.error(err)
      setError(err.message || 'Unable to view candidate document.')
    }
  }

  async function viewApplication(application) {
    if (!application?.id || !organizationId) return

    setDetailLoading(true)
    setDocumentsLoading(true)
    setApplicationDocuments([])
    setError('')

    try {
      const response = await authenticatedFetch(
        `/api/applications/${application.id}?organization_id=${encodeURIComponent(
          organizationId
        )}`,
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || 'Unable to load application details.',
        )
      }

      setSelectedApplication(data.application || null)

      const documentsResponse = await authenticatedFetch(
        `/api/applications/${application.id}/documents?organization_id=${encodeURIComponent(
          organizationId
        )}`,
      )

      const documentsData = await documentsResponse.json()

      if (!documentsResponse.ok) {
        throw new Error(
          documentsData.detail || 'Unable to load candidate documents.',
        )
      }

      setApplicationDocuments(documentsData.documents || [])
    } catch (err) {
      console.error(err)
      setError(
        err.message || 'Unable to load application details.',
      )
    } finally {
      setDetailLoading(false)
      setDocumentsLoading(false)
    }
  }

  const summary = useMemo(() => {
    const counts = {
      total: applications.length,
      applied: 0,
      screening: 0,
      interview: 0,
    }

    applications.forEach((application) => {
      const status = getDisplayStatus(application.status)

      if (status === 'Applied') {
        counts.applied += 1
      }

      if (status === 'Screening') {
        counts.screening += 1
      }

      if (status === 'Interview') {
        counts.interview += 1
      }
    })

    return counts
  }, [applications])

  return (
    <>
      <PageHeader
        title="Applications"
        subtitle="Review candidate applications for your organization."
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
          <p>Loading applications...</p>
        </section>
      ) : error ? (
        <section className="placeholder-card">
          <h2>Unable to load applications</h2>
          <p>{error}</p>
        </section>
      ) : (
        <>
          <section
            style={{
              display: 'grid',
              gridTemplateColumns:
                'repeat(auto-fit, minmax(190px, 1fr))',
              gap: '14px',
              marginBottom: '20px',
            }}
          >
            {[
              {
                label: 'Total Applications',
                value: summary.total,
                color: '#0067B8',
                background: '#EAF4FB',
              },
              {
                label: 'Applied',
                value: summary.applied,
                color: '#0067B8',
                background: '#EAF4FB',
              },
              {
                label: 'Screening',
                value: summary.screening,
                color: '#D97706',
                background: '#FFF7E6',
              },
              {
                label: 'Interview',
                value: summary.interview,
                color: '#7C3AED',
                background: '#F3E8FF',
              },
            ].map((item) => (
              <section
                key={item.label}
                className="dashboard-card"
                style={{
                  padding: '18px',
                  borderRadius: '14px',
                  border: '1px solid #E5E7EB',
                  boxShadow:
                    '0 2px 6px rgba(15, 23, 42, 0.06)',
                }}
              >
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    gap: '12px',
                  }}
                >
                  <div>
                    <div
                      className="employer-app-summary-label"
                      style={{
                        color: '#64748B',
                        marginBottom: '6px',
                      }}
                    >
                      {item.label}
                    </div>

                    <div
                      className="employer-app-summary-value"
                      style={{
                        color: '#0F172A',
                        lineHeight: 1,
                      }}
                    >
                      {item.value}
                    </div>
                  </div>

                  <div
                    style={{
                      width: '10px',
                      height: '10px',
                      borderRadius: '50%',
                      background: item.color,
                      flexShrink: 0,
                    }}
                  />
                </div>
              </section>
            ))}
          </section>

          <section
            className="dashboard-card"
            style={{
              padding: '20px',
              borderRadius: '16px',
              border: '1px solid #E5E7EB',
              boxShadow:
                '0 2px 8px rgba(15, 23, 42, 0.05)',
            }}
          >
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: '12px',
                marginBottom: '18px',
              }}
            >
              <div>
                <h2 className="employer-app-section-title">
                  Candidate Applications
                </h2>

                <p
                  className="employer-app-section-description"
                  style={{
                    margin: '5px 0 0',
                    color: '#64748B',
                  }}
                >
                  Review candidates progressing through recruitment.
                </p>
              </div>

              <div
                className="employer-app-count-pill"
                style={{
                  padding: '6px 10px',
                  borderRadius: '999px',
                  background: '#F8FAFC',
                  color: '#475569',
                }}
              >
                {summary.total}{' '}
                {summary.total === 1 ? 'application' : 'applications'}
              </div>
            </div>

            {applications.length === 0 ? (
              <div
                style={{
                  padding: '42px 20px',
                  textAlign: 'center',
                  border: '1px dashed #CBD5E1',
                  borderRadius: '12px',
                  color: '#64748B',
                }}
              >
                <div
                  className="employer-app-empty-title"
                  style={{
                    color: '#334155',
                    marginBottom: '6px',
                  }}
                >
                  No applications yet
                </div>

                <div className="employer-app-empty-text">
                  Candidate applications for your organization will
                  appear here.
                </div>
              </div>
            ) : (
              <div
                style={{
                  display: 'grid',
                  gap: '12px',
                }}
              >
                {applications.map((application) => {
                  const status = getDisplayStatus(application.status)
                  const statusStyle =
                    STATUS_STYLES[status] || STATUS_STYLES.Applied

                  return (
                    <article
                      key={application.id}
                      style={{
                        display: 'grid',
                        gridTemplateColumns:
                          'auto minmax(180px, 1.4fr) minmax(180px, 1fr) auto',
                        alignItems: 'center',
                        gap: '18px',
                        padding: '16px',
                        border: '1px solid #E5E7EB',
                        borderRadius: '14px',
                        background: '#FFFFFF',
                        boxShadow:
                          '0 1px 3px rgba(15, 23, 42, 0.04)',
                      }}
                    >
                      <div
                        style={{
                          width: '48px',
                          height: '48px',
                          borderRadius: '14px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          background: '#EAF4FB',
                          color: '#0067B8',
                          fontWeight: 700,
                        }}
                      >
                        {getInitials(application)}
                      </div>

                      <div style={{ minWidth: 0 }}>
                        <div
                          className="employer-app-candidate-name"
                          style={{
                            color: '#0F172A',
                            marginBottom: '4px',
                          }}
                        >
                          {getCandidateName(application)}
                        </div>

                        <div
                          className="employer-app-candidate-email"
                          style={{
                            color: '#64748B',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                          }}
                        >
                          {application.candidate_email || 'No email'}
                        </div>
                      </div>

                      <div style={{ minWidth: 0 }}>
                        <div
                          className="employer-app-position-label"
                          style={{
                            color: '#64748B',
                            marginBottom: '4px',
                          }}
                        >
                          Position
                        </div>

                        <div
                          className="employer-app-position"
                          style={{
                            color: '#334155',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                          }}
                        >
                          {application.job_title || '—'}
                        </div>

                        <div
                          className="employer-app-applied-date"
                          style={{
                            marginTop: '5px',
                            color: '#94A3B8',
                          }}
                        >
                          Applied {formatDate(application.applied_at)}
                        </div>
                      </div>

                      <div
                        style={{
                          display: 'flex',
                          flexDirection: 'column',
                          alignItems: 'flex-end',
                          gap: '8px',
                        }}
                      >
                        <span
                          className="employer-app-status-badge"
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            padding: '6px 10px',
                            borderRadius: '999px',
                            background: statusStyle.background,
                            color: statusStyle.color,
                          }}
                        >
                          {status}
                        </span>

                        <div
                          style={{
                            display: 'flex',
                            flexWrap: 'wrap',
                            justifyContent: 'flex-end',
                            gap: '8px',
                          }}
                        >
                          <button
                            className="secondary-action"
                            type="button"
                            onClick={() => viewApplication(application)}
                            disabled={detailLoading}
                          >
                            {detailLoading &&
                            selectedApplication?.id === application.id
                              ? 'Loading...'
                              : 'View Application'}
                          </button>

                          {status === 'Applied' && (
                            <button
                              className="primary-action"
                              type="button"
                              onClick={() => startScreening(application)}
                              disabled={
                                actionApplicationId === application.id
                              }
                            >
                              {actionApplicationId === application.id
                                ? 'Starting...'
                                : 'Start Screening'}
                            </button>
                          )}
                        </div>
                      </div>
                    </article>
                  )
                })}
              </div>
            )}
          </section>

          {selectedApplication && (
            <section
              style={{
                marginTop: '20px',
                padding: '22px',
                border: '1px solid #E2E8F0',
                borderRadius: '14px',
                background: '#FFFFFF',
                boxShadow: '0 1px 3px rgba(15, 23, 42, 0.04)',
              }}
            >
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: '16px',
                  marginBottom: '20px',
                }}
              >
                <div>
                  <div
                    style={{
                      fontSize: '18px',
                      fontWeight: 700,
                      color: '#0F172A',
                    }}
                  >
                    Application Details
                  </div>
                  <div
                    style={{
                      marginTop: '4px',
                      color: '#64748B',
                      fontSize: '14px',
                    }}
                  >
                    {getCandidateName(selectedApplication)}
                  </div>
                </div>

                <button
                  className="secondary-action"
                  type="button"
                  onClick={() => setSelectedApplication(null)}
                >
                  Close
                </button>
              </div>

              {detailLoading ? (
                <div style={{ color: '#64748B' }}>
                  Loading application details...
                </div>
              ) : (
                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns:
                      'repeat(auto-fit, minmax(220px, 1fr))',
                    gap: '16px',
                  }}
                >
                  <div>
                    <div
                      style={{
                        color: '#64748B',
                        fontSize: '13px',
                        marginBottom: '5px',
                      }}
                    >
                      Candidate
                    </div>
                    <div style={{ color: '#0F172A', fontWeight: 600 }}>
                      {getCandidateName(selectedApplication)}
                    </div>
                  </div>

                  <div>
                    <div
                      style={{
                        color: '#64748B',
                        fontSize: '13px',
                        marginBottom: '5px',
                      }}
                    >
                      Email
                    </div>
                    <div style={{ color: '#334155' }}>
                      {selectedApplication.candidate_email || '—'}
                    </div>
                  </div>

                  <div>
                    <div
                      style={{
                        color: '#64748B',
                        fontSize: '13px',
                        marginBottom: '5px',
                      }}
                    >
                      Phone
                    </div>
                    <div style={{ color: '#334155' }}>
                      {selectedApplication.candidate_phone || '—'}
                    </div>
                  </div>

                  <div>
                    <div
                      style={{
                        color: '#64748B',
                        fontSize: '13px',
                        marginBottom: '5px',
                      }}
                    >
                      Position
                    </div>
                    <div style={{ color: '#334155' }}>
                      {selectedApplication.job_title || '—'}
                    </div>
                  </div>

                  <div>
                    <div
                      style={{
                        color: '#64748B',
                        fontSize: '13px',
                        marginBottom: '5px',
                      }}
                    >
                      Status
                    </div>
                    <div style={{ color: '#334155', fontWeight: 600 }}>
                      {getDisplayStatus(selectedApplication.status)}
                    </div>
                  </div>

                  <div>
                    <div
                      style={{
                        color: '#64748B',
                        fontSize: '13px',
                        marginBottom: '5px',
                      }}
                    >
                      Applied
                    </div>
                    <div style={{ color: '#334155' }}>
                      {formatDate(selectedApplication.applied_at)}
                    </div>
                  </div>

                  <div style={{ gridColumn: '1 / -1' }}>
                    <div
                      style={{
                        color: '#64748B',
                        fontSize: '13px',
                        marginBottom: '5px',
                      }}
                    >
                      Cover Letter
                    </div>
                    <div
                      style={{
                        color: '#334155',
                        whiteSpace: 'pre-wrap',
                        lineHeight: 1.6,
                      }}
                    >
                      {selectedApplication.cover_letter ||
                        'No cover letter was provided with this application.'}
                    </div>
                  </div>

                  {getDisplayStatus(selectedApplication.status) ===
                    'Screening' && (
                    <div
                      style={{
                        gridColumn: '1 / -1',
                        marginTop: '8px',
                        paddingTop: '18px',
                        borderTop: '1px solid #E2E8F0',
                      }}
                    >
                      <div
                        style={{
                          color: '#64748B',
                          fontSize: '13px',
                          marginBottom: '10px',
                        }}
                      >
                        Recruitment Actions
                      </div>

                      <div
                        style={{
                          display: 'flex',
                          flexWrap: 'wrap',
                          gap: '10px',
                        }}
                      >
                        <button
                          type="button"
                          className="primary-action"
                          onClick={() =>
                            updateApplicationStatus(
                              selectedApplication,
                              'shortlisted',
                            )
                          }
                          disabled={
                            actionApplicationId === selectedApplication.id
                          }
                        >
                          {actionApplicationId === selectedApplication.id
                            ? 'Updating...'
                            : 'Shortlist'}
                        </button>

                        <button
                          type="button"
                          className="secondary-action"
                          onClick={() =>
                            updateApplicationStatus(
                              selectedApplication,
                              'rejected',
                            )
                          }
                          disabled={
                            actionApplicationId === selectedApplication.id
                          }
                        >
                          Reject
                        </button>
                      </div>
                    </div>
                  )}

                  <div
                    style={{
                      gridColumn: '1 / -1',
                      marginTop: '8px',
                      paddingTop: '18px',
                      borderTop: '1px solid #E2E8F0',
                    }}
                  >
                    <div
                      style={{
                        color: '#64748B',
                        fontSize: '13px',
                        marginBottom: '10px',
                      }}
                    >
                      Candidate Documents
                    </div>

                    {documentsLoading ? (
                      <div style={{ color: '#64748B' }}>
                        Loading candidate documents...
                      </div>
                    ) : applicationDocuments.length === 0 ? (
                      <div
                        style={{
                          padding: '14px',
                          border: '1px dashed #CBD5E1',
                          borderRadius: '10px',
                          color: '#64748B',
                          background: '#F8FAFC',
                        }}
                      >
                        No candidate documents are available.
                      </div>
                    ) : (
                      <div
                        style={{
                          display: 'grid',
                          gap: '8px',
                        }}
                      >
                        {applicationDocuments.map((document) => (
                          <div
                            key={document.id}
                            style={{
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'space-between',
                              gap: '12px',
                              padding: '12px 14px',
                              border: '1px solid #E2E8F0',
                              borderRadius: '10px',
                              background: '#FFFFFF',
                            }}
                          >
                            <div style={{ minWidth: 0 }}>
                              <div
                                style={{
                                  color: '#0F172A',
                                  fontWeight: 600,
                                }}
                              >
                                {document.file_name || 'Unnamed document'}
                              </div>
                              <div
                                style={{
                                  marginTop: '3px',
                                  color: '#64748B',
                                  fontSize: '13px',
                                }}
                              >
                                {document.document_type || 'Document'}
                              </div>
                            </div>

                            <button
                              type="button"
                              onClick={() => viewApplicationDocument(document)}
                              style={{
                                flexShrink: 0,
                                padding: '7px 12px',
                                border: '1px solid #0067B8',
                                borderRadius: '7px',
                                background: '#FFFFFF',
                                color: '#0067B8',
                                fontWeight: 600,
                                cursor: 'pointer',
                              }}
                            >
                              View
                            </button>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </section>
          )}
        </>
      )}
    </>
  )
}
